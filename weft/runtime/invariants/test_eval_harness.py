#!/usr/bin/env python3
"""Tests for the fixed evaluation harness for the weight-update gate (#223)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from weft.runtime.invariants import load_conformance_vectors
from weft.runtime.invariants.eval_harness import (
    RESULTS_PATH,
    run_eval,
    run_grid,
    run_sequence,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _run_harness(*args):
    return subprocess.run(
        [sys.executable, str(HERE / "eval_harness.py"), *args],
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
        self.assertEqual(len(rows), 12)
        budget = 10.0
        for row in rows:
            if row["accepted"]:
                self.assertAlmostEqual(row["remaining_budget"], budget - 1.0)
                budget = row["remaining_budget"]
            else:
                self.assertAlmostEqual(row["remaining_budget"], budget)
            self.assertGreaterEqual(row["remaining_budget"], 0.0)
        self.assertAlmostEqual(budget, 0.0)

    def test_eval_is_deterministic(self) -> None:
        first = run_eval()
        second = run_eval()
        first.pop("environment")
        second.pop("environment")
        self.assertEqual(first, second)

    def test_summary_matches_committed_table(self) -> None:
        committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        result = run_eval()
        self.assertEqual(result["summary"], committed["summary"])
        self.assertEqual(result["summary"]["grid"]["runs"], 207)
        self.assertEqual(result["summary"]["sequence"]["runs"], 12)

    def test_check_passes_on_committed_table(self) -> None:
        proc = _run_harness("--check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('"status": "PASS"', proc.stdout)

    def test_check_fails_on_perturbed_table(self) -> None:
        committed = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        committed["grid"][0]["accepted"] = not committed["grid"][0]["accepted"]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(committed, fh)
            perturbed = fh.name
        proc = _run_harness("--check", "--table", perturbed)
        self.assertEqual(proc.returncode, 1)
        self.assertIn('"status": "FAIL"', proc.stdout)
        self.assertIn("DIFF /grid[0]/accepted", proc.stderr)


if __name__ == "__main__":
    unittest.main()
