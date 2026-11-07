#!/usr/bin/env python3
"""Unit tests for Codebase C1 (`weft/runtime/plasm`) covering Issues #4, #5, #6, #14, #17, #22, #28."""

import os
import unittest
import warnings
from pathlib import Path

import torch

from weft.runtime.plasm import (
    ARENA_BYTE_SIZE,
    DEFAULT_SEED_PHRASE,
    StratifiedAppleSiliconPlasm,
    adjust_homeostatic_mutation_scale,
    compute_plasticity_mask,
    embed_weight_watermark,
    run_weft_plasm_cycle,
    verify_watermark_retention,
)


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

    def test_homeostatic_feedback_controller(self) -> None:
        """Issue #6: sigma contracts when tension exceeds upper band and expands when below lower band."""
        self.assertLess(adjust_homeostatic_mutation_scale(0.02, 40.0), 0.02)
        self.assertGreater(adjust_homeostatic_mutation_scale(0.02, 10.0), 0.02)
        self.assertEqual(adjust_homeostatic_mutation_scale(0.02, 25.0), 0.02)


if __name__ == "__main__":
    unittest.main()
