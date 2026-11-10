#!/usr/bin/env python3
"""Unit tests for Codebase C1 (`weft/runtime/plasm`) covering Issues #4, #5, #6, #14, #17, #22, #28, #40, #74."""

import ctypes
import json
import math
import os
import struct
import sys
import unittest
import uuid
import warnings
from multiprocessing import shared_memory
from pathlib import Path

import torch

from weft.runtime.plasm import (
    ARENA_BYTE_SIZE,
    DEFAULT_SEED_PHRASE,
    MAX_SHM_NAME_BYTES,
    StratifiedAppleSiliconPlasm,
    StratifiedMemoryArena,
    adjust_homeostatic_mutation_scale,
    check_shm_name,
    compute_plasticity_mask,
    embed_weight_watermark,
    run_weft_plasm_cycle,
    verify_watermark_retention,
)


class TestI4SharedMemoryContract(unittest.TestCase):
    """Check the static I4 profile against both the producer and a raw consumer."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.vectors = json.loads(
            Path(__file__).with_name("i4-vectors.json").read_text(encoding="utf-8")
        )
        cls.fields = {field["name"]: field for field in cls.vectors["fields"]}

    def arena(self) -> StratifiedAppleSiliconPlasm:
        return StratifiedAppleSiliconPlasm(name=f"weft_i4_{uuid.uuid4().hex[:16]}")

    def test_native_layout_and_mapped_views_match_profile(self) -> None:
        self.assertEqual(sys.byteorder, self.vectors["byte_order"])
        self.assertEqual(ctypes.alignment(StratifiedMemoryArena), self.vectors["alignment_bytes"])
        self.assertEqual(ARENA_BYTE_SIZE, self.vectors["arena_bytes"])
        ctypes_fields = dict(StratifiedMemoryArena._fields_)
        scalar_types = {"Q": ctypes.c_uint64, "d": ctypes.c_double, "f": ctypes.c_float, "B": ctypes.c_uint8}
        self.assertEqual(list(ctypes_fields), list(self.fields))
        end = 0
        with self.arena() as plasm:
            for field in self.fields.values():
                with self.subTest(field=field["name"]):
                    # Contiguous regions cover the full mapping, without overlap or padding.
                    self.assertEqual(field["offset"], end)
                    self.assertEqual(
                        field["size_bytes"], math.prod(field["shape"]) * field["scalar_bytes"]
                    )
                    self.assertEqual(struct.calcsize("<" + field["format"]), field["scalar_bytes"])
                    end += field["size_bytes"]
                    self.assertEqual(getattr(StratifiedMemoryArena, field["name"]).offset, field["offset"])
                    self.assertEqual(ctypes.sizeof(ctypes_fields[field["name"]]), field["size_bytes"])
                    actual_type = ctypes_fields[field["name"]]
                    if field["shape"]:
                        actual_type = actual_type._type_
                    self.assertIs(actual_type, scalar_types[field["format"]])
                    if "view" in field:
                        view = getattr(plasm, field["view"])
                        try:
                            self.assertEqual(list(view.shape), field["shape"])
                            self.assertEqual(view.dtype.kind, "f")
                            self.assertEqual(view.itemsize, field["scalar_bytes"])
                            self.assertTrue(view.dtype.isnative)
                            self.assertTrue(view.flags.c_contiguous)
                            self.assertEqual(
                                view.strides,
                                tuple(math.prod(field["shape"][i + 1:]) * field["scalar_bytes"]
                                      for i in range(len(field["shape"]))),
                            )
                            self.assertEqual(
                                view.ctypes.data - ctypes.addressof(plasm.c_view), field["offset"]
                            )
                        finally:
                            del view  # Do not retain an exported buffer across close().
            self.assertEqual(end, self.vectors["arena_bytes"])

    def test_golden_bytes_exchange_with_independent_raw_consumer(self) -> None:
        samples = self.vectors["samples"]
        expected = bytearray(self.vectors["arena_bytes"])
        occupied = set()
        for sample in samples:
            field = self.fields[sample["field"]]
            self.assertEqual(len(sample["index"]), len(field["shape"]))
            flat_index = 0
            for index, dimension in zip(sample["index"], field["shape"]):
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, dimension)
                flat_index = flat_index * dimension + index
            self.assertEqual(sample["byte_offset"], field["offset"] + flat_index * field["scalar_bytes"])
            golden = bytes.fromhex(sample["hex"])
            self.assertEqual(golden, struct.pack("<" + field["format"], sample["value"]))
            start, end = sample["byte_offset"], sample["byte_offset"] + len(golden)
            self.assertLessEqual(end, field["offset"] + field["size_bytes"])
            self.assertTrue(occupied.isdisjoint(range(start, end)))
            occupied.update(range(start, end))
            expected[start:end] = golden

        with self.arena() as plasm:
            raw = shared_memory.SharedMemory(name=plasm.name, create=False)
            # macOS rounds an attached mapping up to whole pages (16 KiB on arm64),
            # so the raw buffer can be longer than the profile. Only the profile's
            # bytes are the contract; the tail is OS padding (#68).
            size = int(self.vectors["arena_bytes"])
            self.assertGreaterEqual(len(raw.buf), size)
            region = raw.buf[:size]
            try:
                region[:] = bytes(self.vectors["arena_bytes"])
                # Producer views write values; an independent reader uses only fixture offsets.
                for sample in samples:
                    field = self.fields[sample["field"]]
                    if "view" in field:
                        getattr(plasm, field["view"])[tuple(sample["index"])] = sample["value"]
                    elif field["shape"]:
                        getattr(plasm.c_view, field["name"])[sample["index"][0]] = sample["value"]
                    else:
                        setattr(plasm.c_view, field["name"], sample["value"])
                self.assertEqual(bytes(region), bytes(expected))
                for sample in samples:
                    field = self.fields[sample["field"]]
                    self.assertEqual(
                        struct.unpack_from("<" + field["format"], raw.buf, sample["byte_offset"])[0],
                        sample["value"],
                    )

                # Independent writer packs bytes; producer reads its typed views.
                region[:] = bytes(self.vectors["arena_bytes"])
                for sample in samples:
                    field = self.fields[sample["field"]]
                    struct.pack_into("<" + field["format"], raw.buf, sample["byte_offset"], sample["value"])
                for sample in samples:
                    field = self.fields[sample["field"]]
                    if "view" in field:
                        value = getattr(plasm, field["view"])[tuple(sample["index"])]
                    elif field["shape"]:
                        value = getattr(plasm.c_view, field["name"])[sample["index"][0]]
                    else:
                        value = getattr(plasm.c_view, field["name"])
                    self.assertEqual(value, sample["value"])
            finally:
                region.release()
                raw.close()

    def test_detached_tensor_lifetime_and_unlink(self) -> None:
        with self.arena() as plasm:
            name = plasm.name
            plasm.focal_matrix.fill(1.0)
            focal, symp, hippo = plasm.read_tensors_to_device(torch.device("cpu"))
            plasm.focal_matrix[0, 0] = 2.0
            self.assertEqual(focal[0, 0].item(), 1.0)
            focal[0, 0] = 3.0
            self.assertEqual(plasm.focal_matrix[0, 0], 2.0)
        self.assertTrue(plasm._closed)
        self.assertIsNone(plasm.c_view)
        self.assertIsNone(plasm.focal_matrix)
        self.assertIsNone(plasm.symp_matrix)
        self.assertIsNone(plasm.hippo_matrix)
        self.assertIsNone(plasm._raw_np)
        self.assertEqual(focal[0, 0].item(), 3.0)
        plasm.close()  # Closing an already closed owner is harmless.
        with self.assertRaises(FileNotFoundError):
            shared_memory.SharedMemory(name=name, create=False)


class TestWeftPlasm(unittest.TestCase):
    def test_no_passphrase_literal_in_code(self) -> None:
        """Issue #14: runtime code must not hard-code passphrase-like literals."""
        plasm_src = (Path(__file__).resolve().parent / "plasm.py").read_text(encoding="utf-8")
        self.assertEqual(DEFAULT_SEED_PHRASE, "WEFT_DETERMINISTIC_SEED_V1")
        for forbidden in ("Sacred_Weaver", "Sovereign_Identity_Key", "House_Of_Light_777"):
            self.assertNotIn(forbidden, plasm_src)

    def test_shared_memory_lifecycle_releases_views_cleanly(self) -> None:
        """Issue #17: closing StratifiedAppleSiliconPlasm must release all views without BufferError."""
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            arena_name = f"weft_test_shm_{os.getpid()}"
            with StratifiedAppleSiliconPlasm(name=arena_name, create=True) as plasm:
                self.assertEqual(plasm.size, ARENA_BYTE_SIZE)
                plasm.seed_arena()
                focal, symp, hippo = plasm.read_tensors_to_device(torch.device("cpu"))
                self.assertEqual(tuple(focal.shape), (256, 256))
                self.assertEqual(tuple(symp.shape), (1024,))
                self.assertEqual(tuple(hippo.shape), (64, 1024))
                plasm.write_focal_from_tensor(focal * 1.01, epoch=2, tension=24.5)
            # After context exit, views are None and _closed is True
            self.assertTrue(plasm._closed)
            self.assertIsNone(plasm.focal_matrix)
            self.assertIsNone(plasm._raw_np)

    def test_core_freezing_plasticity_mask(self) -> None:
        """Issues #6 & #22: core rows must be strictly 0.0 in the plasticity mask while periphery rows are > 0."""
        w = torch.randn(64, 64)
        mask = compute_plasticity_mask(w, core_rows=16)
        self.assertEqual(float(mask[:16, :].abs().max().item()), 0.0)
        self.assertGreater(float(mask[16:, :].min().item()), 0.0)

    def test_watermark_retention_and_adversarial_overwrite_detection(self) -> None:
        """Issue #4: watermark stays intact under periphery updates but fails when core trigger response is overwritten."""
        w = torch.randn(64, 64) * 0.05
        w_wm, trigger, target, align = embed_weight_watermark(w, core_rows=16)
        self.assertGreater(align, 0.90)

        # 1. Legitimate periphery update preserves the core watermark
        mask = compute_plasticity_mask(w_wm, core_rows=16)
        w_periphery_updated = w_wm + mask * (torch.randn_like(w_wm) * 0.05)
        res_ok = verify_watermark_retention(w_wm, w_periphery_updated, trigger, target)
        self.assertTrue(res_ok["retained"])
        self.assertEqual(res_ok["response_l2_drift"], 0.0)

        # 2. Adversarial rank-1 overwrite of the trigger response is caught
        adv_target = -target
        curr_resp = torch.mv(w_wm.t(), trigger)
        w_overwritten = w_wm + torch.outer(trigger, adv_target - curr_resp)
        res_adv = verify_watermark_retention(w_wm, w_overwritten, trigger, target)
        self.assertFalse(res_adv["retained"])
        self.assertEqual(res_adv["reason"], "cosine_alignment_below_threshold")

    def test_ab_convergence_and_cellular_contract(self) -> None:
        """Issues #5, #6, #22: A/B mitotic cycle reduces target error monotonically while keeping core rows frozen."""
        report = run_weft_plasm_cycle(generations=5)
        gens = report["generations"]
        self.assertEqual(len(gens), 5)
        self.assertLess(report["final_target_error"], report["initial_target_error"])
        for g in gens:
            self.assertTrue(g["invariant_safe"])
            self.assertTrue(g["watermark_retained"])
            self.assertEqual(g["core_row_drift"], 0.0)
            self.assertLessEqual(g["winner_target_error"], g["parent_target_error"])
            self.assertTrue(g["homeostatic"])

    def test_rejected_candidates_never_count_as_progress(self) -> None:
        """Issue #63: with a radius so small the gate rejects everything, the held error is the initial error."""
        import weft.runtime.plasm.plasm as plasm_module

        original = plasm_module.R_INVARIANT
        plasm_module.R_INVARIANT = 0.05
        try:
            torch.manual_seed(0)
            report = run_weft_plasm_cycle(generations=6)
        finally:
            plasm_module.R_INVARIANT = original
        gens = report["generations"]
        self.assertEqual(report["committed_generations"], 0)
        self.assertFalse(any(g["committed"] for g in gens))
        self.assertEqual(report["final_target_error"], report["initial_target_error"])
        for g in gens:
            self.assertEqual(g["held_target_error"], g["parent_target_error"])
        # The candidates themselves did improve; that must not be reported as progress.
        self.assertLess(gens[-1]["winner_target_error"], report["initial_target_error"])
        self.assertEqual(report["status"], "FAIL")

    def test_watermark_failure_blocks_commit(self) -> None:
        """Issue #74 finding 5: a candidate that fails the watermark check is never committed, even when it improves target error and passes the distance gate."""
        import weft.runtime.plasm.plasm as plasm_module

        original = plasm_module.verify_watermark_retention

        def failing_check(*args, **kwargs):
            return {
                "retained": False,
                "cosine_alignment": -0.04,
                "response_l2_drift": 1.0,
                "reason": "cosine_alignment_below_threshold",
            }

        plasm_module.verify_watermark_retention = failing_check
        try:
            torch.manual_seed(0)
            report = run_weft_plasm_cycle(generations=6)
        finally:
            plasm_module.verify_watermark_retention = original
        gens = report["generations"]
        self.assertEqual(report["committed_generations"], 0)
        self.assertFalse(any(g["committed"] for g in gens))
        self.assertEqual(report["final_target_error"], report["initial_target_error"])
        for g in gens:
            self.assertFalse(g["watermark_retained"])
            self.assertEqual(g["held_target_error"], g["parent_target_error"])
        # The candidates themselves did improve; that must not be reported as progress.
        self.assertLess(gens[-1]["winner_target_error"], report["initial_target_error"])
        self.assertEqual(report["status"], "FAIL")

    def test_committed_generations_report_the_held_error(self) -> None:
        report = run_weft_plasm_cycle(generations=4)
        for g in report["generations"]:
            expected = g["winner_target_error"] if g["committed"] else g["parent_target_error"]
            self.assertEqual(g["held_target_error"], expected)
        self.assertEqual(report["final_target_error"], report["generations"][-1]["held_target_error"])
        self.assertEqual(report["committed_generations"], sum(g["committed"] for g in report["generations"]))

    def test_shared_memory_names_fit_the_macos_limit(self) -> None:
        """Issue #68: names over 30 bytes fail on macOS only, so they are refused everywhere."""
        self.assertEqual(check_shm_name("weft_stratified_plasm_v1"), "weft_stratified_plasm_v1")
        self.assertEqual(check_shm_name("x" * MAX_SHM_NAME_BYTES), "x" * MAX_SHM_NAME_BYTES)
        for bad in ("x" * (MAX_SHM_NAME_BYTES + 1), f"weft_i4_{uuid.uuid4().hex}", "", "a/b"):
            with self.subTest(name=bad), self.assertRaises(ValueError):
                StratifiedAppleSiliconPlasm(name=bad)
        # The per-process default used by the cycle fits even with a 7-digit PID.
        self.assertLessEqual(len(f"weft_plasm_{4194304}"), MAX_SHM_NAME_BYTES)

    def test_homeostatic_feedback_controller(self) -> None:
        """Issue #6: sigma contracts when tension exceeds upper band and expands when below lower band."""
        self.assertLess(adjust_homeostatic_mutation_scale(0.02, 40.0), 0.02)
        self.assertGreater(adjust_homeostatic_mutation_scale(0.02, 10.0), 0.02)
        self.assertEqual(adjust_homeostatic_mutation_scale(0.02, 25.0), 0.02)


if __name__ == "__main__":
    unittest.main()
