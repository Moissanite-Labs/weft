#!/usr/bin/env python3
"""Unit and cross-language C conformance tests for Codebase C2 (`weft/runtime/invariants`)."""

import math
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from weft.runtime.invariants import (
    compute_royalty_split,
    load_conformance_vectors,
    verify_tension_bound,
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
