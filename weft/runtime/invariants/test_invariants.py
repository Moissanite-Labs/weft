#!/usr/bin/env python3
"""Unit and cross-language C conformance tests for Codebase C2 (`weft/runtime/invariants`)."""

import math
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from weft.runtime.invariants import (
    HOMEOSTATIC_TENSION_MAX,
    HOMEOSTATIC_TENSION_MIN,
    ROYALTY_UPSTREAM_BPS,
    ROYALTY_WEAVER_BPS,
    R_INVARIANT,
    TENSION_MAX,
    compute_royalty_split,
    load_conformance_vectors,
    verify_tension_bound,
    verify_weight_update_safety,
    verify_weight_update_safety_ex,
)


class TestWeftInvariants(unittest.TestCase):
    def setUp(self) -> None:
        self.vectors = load_conformance_vectors()

    def test_weight_update_vectors(self) -> None:
        for vec in self.vectors["weight_update_vectors"]:
            with self.subTest(vec=vec["name"]):
                ok, dist, rem, reason = verify_weight_update_safety_ex(
                    vec["baseline"],
                    vec["candidate"],
                    vec["r_invariant"],
                    vec["budget"],
                    vec["cost"],
                )
                self.assertEqual(ok, vec["expected_accepted"])
                self.assertEqual(reason, vec["expected_reason"])
                if vec["expected_distance"] == "Inf":
                    self.assertTrue(math.isinf(dist))
                else:
                    self.assertAlmostEqual(dist, float(vec["expected_distance"]), places=6)
                self.assertAlmostEqual(rem, float(vec["expected_remaining_budget"]), places=6)

    def test_tension_vectors(self) -> None:
        for vec in self.vectors["tension_vectors"]:
            with self.subTest(vec=vec["name"]):
                res = verify_tension_bound(vec["tension"], vec["max_tension"])
                self.assertEqual(res["accepted"], vec["expected_accepted"])
                self.assertEqual(res["homeostatic"], vec["expected_homeostatic"])
                self.assertEqual(res["excision_triggered"], vec["expected_excision"])

    def test_royalty_vectors(self) -> None:
        for vec in self.vectors["royalty_vectors"]:
            with self.subTest(vec=vec["name"]):
                split = compute_royalty_split(vec["gross_wei"], vec["upstream_bps"])
                self.assertEqual(split["upstream_wei"], vec["expected_upstream_wei"])
                self.assertEqual(split["weaver_wei"], vec["expected_weaver_wei"])
                self.assertEqual(split["upstream_wei"] + split["weaver_wei"], vec["gross_wei"])

    def test_constants_block_matches_module(self) -> None:
        constants = self.vectors["constants"]
        self.assertEqual(constants["R_INVARIANT"], R_INVARIANT)
        self.assertEqual(constants["TENSION_MAX"], TENSION_MAX)
        self.assertEqual(constants["HOMEOSTATIC_TENSION_MIN"], HOMEOSTATIC_TENSION_MIN)
        self.assertEqual(constants["HOMEOSTATIC_TENSION_MAX"], HOMEOSTATIC_TENSION_MAX)
        self.assertEqual(constants["ROYALTY_UPSTREAM_BPS"], ROYALTY_UPSTREAM_BPS)
        self.assertEqual(constants["ROYALTY_WEAVER_BPS"], ROYALTY_WEAVER_BPS)

    def test_budget_underflow_reports_ex_distance_not_candidate_norm(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        baseline = torch.tensor([1.0, 0.0, 0.0, 1.0])
        current = baseline.clone()
        candidate = torch.tensor([3.0, 0.0, 0.0, 3.0])
        cand_norm = float(torch.linalg.norm(candidate).item())
        self.assertTrue(math.isfinite(cand_norm))
        res = verify_weight_update_safety(
            baseline,
            current,
            candidate,
            remaining_budget=0.5,
            update_cost=1.0,
            max_baseline_distance=R_INVARIANT,
        )
        self.assertFalse(res["accepted"])
        self.assertEqual(res["reason"], "remaining_budget_underflow")
        self.assertTrue(math.isinf(res["baseline_distance"]))
        self.assertNotAlmostEqual(res["baseline_distance"], cand_norm)

    def test_c_header_conformance(self) -> None:
        cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
        self.assertIsNotNone(cc, "C compiler (cc/clang/gcc) is required to verify weft_invariants.h")
        here = Path(__file__).resolve().parent
        c_src = here / "test_invariants_c.c"
        with tempfile.TemporaryDirectory() as tmp:
            bin_path = Path(tmp) / "test_invariants_c"
            r_compile = subprocess.run(
                [cc, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(c_src), "-lm", "-o", str(bin_path)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r_compile.returncode, 0, f"C compile failed: {r_compile.stderr}")
            r_run = subprocess.run([str(bin_path)], capture_output=True, text=True)
            self.assertEqual(r_run.returncode, 0, f"C vector test failed: {r_run.stderr}")
            self.assertIn("C_INVARIANTS_VECTORS_PASS", r_run.stdout)


if __name__ == "__main__":
    unittest.main()
