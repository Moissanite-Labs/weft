#!/usr/bin/env python3
"""Regression tests for the E16 somatic C2 commit path."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_RUNNER = Path(__file__).resolve().parent / "run_e16.py"
_SPEC = importlib.util.spec_from_file_location("weft_e16_run_e16", _RUNNER)
assert _SPEC is not None and _SPEC.loader is not None
run_e16 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_e16)


class TestE16SomaticGate(unittest.TestCase):
    def setUp(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        self.torch = torch

    def _tensors(self):
        torch = self.torch
        dim = run_e16.DIM
        core = run_e16.CORE_ROWS
        baseline = torch.zeros(dim, dim, dtype=torch.float32)
        current = baseline.clone()
        current[core:, :] = 0.01
        watermark = torch.zeros(dim, dim, dtype=torch.float32)
        watermark[:core, 0] = 0.5
        baseline[:core, :] = watermark[:core, :]
        current[:core, :] = watermark[:core, :]
        return baseline, current, watermark

    def test_rejecting_distance_gate_leaves_w_and_budget_unchanged(self) -> None:
        torch = self.torch
        baseline, current, watermark = self._tensors()
        before = current.clone()
        # Far outside the R=12 ball.
        candidate = current.clone()
        candidate[run_e16.CORE_ROWS :, :] = 1.0
        budget = 50.0
        committed, rem, ok, dist, reason = run_e16.commit_weight_update(
            baseline, current, candidate, budget, run_e16.SOMATIC_STEP_COST, watermark
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "baseline_distance_exceeded")
        self.assertGreater(dist, run_e16.R_BALL)
        self.assertEqual(rem, budget)
        self.assertTrue(torch.equal(committed, before))
        self.assertTrue(torch.equal(current, before))

    def test_rejecting_budget_gate_leaves_w_unchanged(self) -> None:
        torch = self.torch
        baseline, current, watermark = self._tensors()
        before = current.clone()
        candidate = current.clone()
        candidate[run_e16.CORE_ROWS, 0] = current[run_e16.CORE_ROWS, 0] + 0.01
        committed, rem, ok, dist, reason = run_e16.commit_weight_update(
            baseline, current, candidate, 0.0, run_e16.SOMATIC_STEP_COST, watermark
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "non_positive_budget_or_cost")
        self.assertEqual(rem, 0.0)
        self.assertTrue(torch.equal(committed, before))

    def test_accepting_gate_commits_candidate_and_consumes_budget(self) -> None:
        torch = self.torch
        baseline, current, watermark = self._tensors()
        candidate = current.clone()
        candidate[run_e16.CORE_ROWS, 0] = current[run_e16.CORE_ROWS, 0] + 0.05
        budget = 8.0
        committed, rem, ok, dist, reason = run_e16.commit_weight_update(
            baseline, current, candidate, budget, run_e16.SOMATIC_STEP_COST, watermark
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")
        self.assertLessEqual(dist, run_e16.R_BALL)
        self.assertAlmostEqual(rem, budget - run_e16.SOMATIC_STEP_COST, places=6)
        self.assertTrue(torch.equal(committed[: run_e16.CORE_ROWS], watermark[: run_e16.CORE_ROWS]))
        self.assertTrue(torch.equal(committed[run_e16.CORE_ROWS :], candidate[run_e16.CORE_ROWS :]))
        self.assertFalse(torch.equal(committed, current))


if __name__ == "__main__":
    unittest.main()
