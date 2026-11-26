"""
Report contract and ownership lifecycle for the Plasm substrate (issue #51).

Covers:
  - effective-config echo from the Mac loom path (forwarded, never fabricated);
  - deterministic replay for identical seed/config/backend;
  - the explicit zero-iteration result;
  - candidate vs committed-state final error separation;
  - arena ownership: attachers never unlink the owner's segment, create over
    an existing segment fails closed, and `force_unlink` is the only
    administrative removal path.
"""

from __future__ import annotations

import os
import unittest
import uuid

import torch

import weft.runtime.plasm.plasm as plasm_module
from weft.runtime.mac.metal_loom import run_metal_mitotic_loom
from weft.runtime.plasm import StratifiedAppleSiliconPlasm, run_weft_plasm_cycle


def _force_cpu() -> None:
    plasm_module.select_compute_device = lambda: torch.device("cpu")


def _restore_device(original) -> None:
    plasm_module.select_compute_device = original


class TestLoomEffectiveConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._original = plasm_module.select_compute_device
        _force_cpu()

    def tearDown(self) -> None:
        _restore_device(self._original)

    def test_loom_forwards_budget_and_invariant_into_cycle(self) -> None:
        report = run_metal_mitotic_loom(dim=256, generations=1, r_invariant=77.0, initial_budget=12.5)
        cfg = report["effective_config"]
        self.assertEqual(cfg["r_invariant"], 77.0)
        self.assertEqual(cfg["initial_metabolic_budget"], 12.5)
        self.assertEqual(cfg["dim"], 256)
        self.assertEqual(cfg["core_rows"], 64)
        self.assertEqual(cfg["generations"], 1)
        self.assertEqual(report["iterations_executed"], 1)
        self.assertEqual(report["iterations_requested"], 1)

    def test_loom_rejects_non_executable_dim(self) -> None:
        with self.assertRaises(ValueError):
            run_metal_mitotic_loom(dim=512, generations=1)

    def test_default_budget_matches_cycle_default_100(self) -> None:
        report = run_metal_mitotic_loom(dim=256, generations=1)
        self.assertEqual(report["effective_config"]["initial_metabolic_budget"], 100.0)


class TestReproducibleReplay(unittest.TestCase):
    def setUp(self) -> None:
        self._original = plasm_module.select_compute_device
        _force_cpu()

    def tearDown(self) -> None:
        _restore_device(self._original)

    def test_same_seed_config_backend_replays_identically(self) -> None:
        r1 = run_weft_plasm_cycle(generations=2, seed_phrase="WEFT-51-SEED", shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        r2 = run_weft_plasm_cycle(generations=2, seed_phrase="WEFT-51-SEED", shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        self.assertEqual(r1["final_weights_sha256"], r2["final_weights_sha256"])
        self.assertEqual([g["winner"] for g in r1["generations"]], [g["winner"] for g in r2["generations"]])
        self.assertEqual(r1["effective_config"]["noise_seed"], r2["effective_config"]["noise_seed"])

    def test_different_seed_phrase_diverges(self) -> None:
        r1 = run_weft_plasm_cycle(generations=2, seed_phrase="WEFT-51-SEED-A", shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        r2 = run_weft_plasm_cycle(generations=2, seed_phrase="WEFT-51-SEED-B", shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        self.assertNotEqual(r1["final_weights_sha256"], r2["final_weights_sha256"])


class TestZeroIterationContract(unittest.TestCase):
    def setUp(self) -> None:
        self._original = plasm_module.select_compute_device
        _force_cpu()

    def tearDown(self) -> None:
        _restore_device(self._original)

    def test_zero_iterations_is_explicit_and_never_crashes(self) -> None:
        report = run_weft_plasm_cycle(generations=0, shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        self.assertEqual(report["status"], "NOOP")
        self.assertTrue(report["zero_iteration_noop"])
        self.assertEqual(report["iterations_executed"], 0)
        self.assertEqual(report["generations"], [])
        self.assertIsNone(report["final_target_error"])
        self.assertIsNone(report["proposed_candidate_final_error"])
        self.assertIsNone(report["committed_state_final_error"])

    def test_negative_iterations_is_the_same_explicit_result(self) -> None:
        report = run_weft_plasm_cycle(generations=-3)
        self.assertEqual(report["status"], "NOOP")
        self.assertEqual(report["iterations_requested"], -3)


class TestCandidateVsCommittedSeparation(unittest.TestCase):
    def setUp(self) -> None:
        self._original = plasm_module.select_compute_device
        _force_cpu()

    def tearDown(self) -> None:
        _restore_device(self._original)

    def test_committed_state_error_is_held_not_candidate(self) -> None:
        report = run_weft_plasm_cycle(generations=2, seed_phrase="WEFT-51-SPLIT", shm_name=f"weft_51_{uuid.uuid4().hex[:12]}")
        history = report["generations"]
        self.assertEqual(report["final_target_error"], history[-1]["held_target_error"])
        self.assertEqual(report["committed_state_final_error"], history[-1]["held_target_error"])
        self.assertEqual(report["proposed_candidate_final_error"], history[-1]["winner_target_error"])


class TestArenaOwnershipLifecycle(unittest.TestCase):
    def _name(self) -> str:
        return f"weft_51_{uuid.uuid4().hex[:12]}"

    def test_create_refuses_to_touch_existing_segment(self) -> None:
        name = self._name()
        owner = StratifiedAppleSiliconPlasm(name=name, create=True)
        try:
            with self.assertRaises(FileExistsError) as ctx:
                StratifiedAppleSiliconPlasm(name=name, create=True)
            self.assertIn("refusing", str(ctx.exception))
        finally:
            owner.close(unlink=True)

    def test_attacher_cannot_unlink_owner_segment(self) -> None:
        name = self._name()
        owner = StratifiedAppleSiliconPlasm(name=name, create=True)
        owner.seed_arena()
        attacher = StratifiedAppleSiliconPlasm(name=name, create=False)
        self.assertFalse(attacher.owner)
        self.assertTrue(owner.owner)
        with self.assertRaises(PermissionError):
            attacher.close(unlink=True)
        # Segment must still exist and hold the owner's bytes after the refusal.
        probe = StratifiedAppleSiliconPlasm(name=name, create=False)
        self.assertAlmostEqual(float(probe.symp_matrix[0]), 0.0, places=6)
        probe.close()
        attacher.close()  # default close: never unlinks, must not raise
        owner.close(unlink=True)
        with self.assertRaises(FileNotFoundError):
            StratifiedAppleSiliconPlasm(name=name, create=False)

    def test_owner_can_leave_segment_then_admin_force_unlink(self) -> None:
        name = self._name()
        owner = StratifiedAppleSiliconPlasm(name=name, create=True)
        owner.close(unlink=False)  # persisted on purpose
        with self.assertRaises(FileExistsError):
            StratifiedAppleSiliconPlasm(name=name, create=True)
        StratifiedAppleSiliconPlasm.force_unlink(name)
        with self.assertRaises(FileNotFoundError):
            StratifiedAppleSiliconPlasm(name=name, create=False)

    def test_attach_then_owner_unlink_invalidates_future_attach(self) -> None:
        name = self._name()
        owner = StratifiedAppleSiliconPlasm(name=name, create=True)
        attacher = StratifiedAppleSiliconPlasm(name=name, create=False)
        attacher.close()
        owner.close(unlink=True)
        with self.assertRaises(FileNotFoundError):
            StratifiedAppleSiliconPlasm(name=name, create=False)


if __name__ == "__main__":
    unittest.main()
