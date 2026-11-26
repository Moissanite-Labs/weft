#!/usr/bin/env python3
"""Tests for the fixed evaluation harness for the weight-update gate (#223)."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.invariants import load_conformance_vectors  # noqa: E402
from weft.runtime.invariants.eval_harness import (  # noqa: E402
    RESULTS_PATH,
    compare,
    decode,
    encode,
    run_eval,
    run_grid,
    run_sequence,
)


def _run_harness(*args):
    return subprocess.run(
        [sys.executable, "-B", str(HERE / "eval_harness.py"), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


class TestEvalHarness(unittest.TestCase):
    def test_grid_covers_every_vector_factor_and_budget(self) -> None:
        vectors = load_conformance_vectors()
        grid = run_grid(vectors)
        names = [v["name"] for v in vectors["weight_update_vectors"]]
        self.assertEqual(len(grid), 9 * len(names))
        for name in names:
            self.assertEqual(sum(1 for r in grid if r["vector"] == name), 9)
        self.assertEqual(
            {(r["radius_factor"], r["budget"]) for r in grid},
            {(0.5, 5.0), (0.5, 10.0), (0.5, 25.0),
             (1.0, 5.0), (1.0, 10.0), (1.0, 25.0),
             (2.0, 5.0), (2.0, 10.0), (2.0, 25.0)},
        )

    def test_sequence_spends_budget_only_on_accepts(self) -> None:
        rows = run_sequence()
        self.assertEqual(len(rows), 13)
        budget = 10.0
        for row in rows:
            if row["accepted"]:
                self.assertAlmostEqual(row["remaining_budget"], budget - 1.0)
                budget = row["remaining_budget"]
                self.assertGreaterEqual(row["remaining_budget"], 0.0)
            else:
                # Reject paths leave the caller's budget unchanged (#210 / #235).
                self.assertAlmostEqual(row["remaining_budget"], budget)
                self.assertGreaterEqual(row["remaining_budget"], 0.0)
        self.assertAlmostEqual(budget, 0.0)
        self.assertFalse(rows[-1]["accepted"])
        self.assertEqual(rows[-1]["reason"], "non_positive_budget_or_cost")
        self.assertAlmostEqual(rows[-1]["remaining_budget"], 0.0)

    def test_eval_is_deterministic(self) -> None:
        first = run_eval()
        second = run_eval()
        first.pop("environment")
        second.pop("environment")
        self.assertEqual(first, second)

    def test_encode_preserves_signed_infinities_and_nan(self) -> None:
        self.assertEqual(encode(float("nan")), "NaN")
        self.assertEqual(encode(float("inf")), "Inf")
        self.assertEqual(encode(float("-inf")), "-Inf")
        self.assertEqual(encode(1.5), 1.5)
        self.assertEqual(encode(3), 3)
        self.assertTrue(math.isinf(decode("-Inf")) and decode("-Inf") < 0)

    def test_compare_exact_integers_and_rejects_bool_as_int(self) -> None:
        self.assertEqual(compare(100000, 100000, "/count"), [])
        self.assertEqual(len(compare(100000, 100001, "/count")), 1)
        self.assertEqual(len(compare(True, 1, "/flag")), 1)
        self.assertEqual(len(compare(1, True, "/flag")), 1)
        self.assertEqual(len(compare(False, 0, "/flag")), 1)
        self.assertEqual(len(compare(0, False, "/flag")), 1)
        self.assertEqual(len(compare(True, 1.0, "/flag")), 1)
        self.assertEqual(compare(True, True, "/flag"), [])
        self.assertEqual(len(compare("-Inf", "Inf", "/val")), 1)
        self.assertEqual(compare(1.0, 1.0 + 1e-6, "/dist"), [])

    def test_summary_matches_committed_table(self) -> None:
        committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        result = run_eval()
        self.assertEqual(result["summary"], committed["summary"])
        self.assertEqual(result["summary"]["grid"]["runs"], 216)
        self.assertEqual(result["summary"]["sequence"]["runs"], 13)
        self.assertEqual(
            result["summary"]["sequence"]["reasons"],
            {"baseline_distance_exceeded": 2, "non_positive_budget_or_cost": 1, "ok": 10},
        )

    def test_check_passes_on_committed_table(self) -> None:
        proc = _run_harness("--check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('"status": "PASS"', proc.stdout)

    def test_check_fails_on_perturbed_table(self) -> None:
        committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        committed["grid"][0]["accepted"] = not committed["grid"][0]["accepted"]
        with tempfile.TemporaryDirectory() as tmpdir:
            perturbed = Path(tmpdir) / "perturbed.json"
            perturbed.write_text(json.dumps(committed), encoding="utf-8")
            proc = _run_harness("--check", "--table", str(perturbed))
            self.assertEqual(proc.returncode, 1)
            self.assertIn('"status": "FAIL"', proc.stdout)
            self.assertIn("DIFF /grid[0]/accepted", proc.stderr)
        self.assertFalse(perturbed.exists())


if __name__ == "__main__":
    unittest.main()
