#!/usr/bin/env python3
"""Unit tests verifying the Apple Silicon MPS baseline and device selection (#76)."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[3]
PAPER1_DIR = ROOT / "papers" / "01-models-as-cells"
MPS_RESULTS_PATH = PAPER1_DIR / "results-mps-m1.json"
EXPERIMENTS_PY = PAPER1_DIR / "experiments.py"


class TestMPSBaselineFile(unittest.TestCase):
    """Verify integrity, schema, and sanitization of the committed MPS baseline."""

    def test_mps_baseline_file_exists_and_schema(self) -> None:
        self.assertTrue(MPS_RESULTS_PATH.is_file(), f"Missing MPS baseline: {MPS_RESULTS_PATH}")
        data = json.loads(MPS_RESULTS_PATH.read_text(encoding="utf-8"))

        self.assertEqual(data.get("schema"), "weft-paper-1-results/1")
        for key in ("environment", "e1_compared_sizes", "e2_plasm_cycles", "e3_watermark", "e4_conformance", "e5_radius_sweep"):
            self.assertIn(key, data)

        env = data["environment"]
        self.assertEqual(env.get("device"), "mps")
        self.assertEqual(env.get("machine"), "arm64")
        self.assertEqual(env.get("system"), "Darwin")
        self.assertTrue(env.get("mps_available"))
        self.assertIn("chip", env)
        self.assertIn("Apple", env["chip"])

        # Sanitization: Ensure no hardware UUIDs, serial numbers, or local user paths exist in JSON
        raw_text = MPS_RESULTS_PATH.read_text(encoding="utf-8")
        self.assertNotIn("/Users/", raw_text)
        self.assertNotIn("/home/", raw_text)
        self.assertNotIn("IOPlatformSerialNumber", raw_text)
        self.assertNotIn("hardware_uuid", raw_text)

    def test_mps_experiment_metrics(self) -> None:
        data = json.loads(MPS_RESULTS_PATH.read_text(encoding="utf-8"))

        # E1: baseline-distance gate rejects large norm-preserving moves
        e1 = data["e1_compared_sizes"]
        self.assertEqual(e1["cases"], 37)
        self.assertEqual(e1["weak_accepts"], 37)
        self.assertEqual(e1["gate_accepts"], 3)
        self.assertEqual(e1["first_rejected_theta_deg"], 15.0)

        # E2: Plasm mitotic cycle passes on MPS
        e2 = data["e2_plasm_cycles"]
        self.assertTrue(e2["all_pass"])
        self.assertEqual(e2["commits_total"], 120)
        self.assertEqual(e2["proposals_total"], 120)
        self.assertEqual(e2["max_core_row_drift"], 0.0)
        self.assertEqual(e2["min_watermark_alignment"], 1.0)

        # E3: provenance watermark retained under periphery plasticity
        e3 = data["e3_watermark"]
        self.assertTrue(e3["masked_all_retained"])
        self.assertEqual(e3["masked_max_response_drift"], 0.0)
        self.assertTrue(e3["rank1_overwrite"]["detected"])

        # E4: conformance vector agreement
        e4 = data["e4_conformance"]
        self.assertEqual(e4["python_agrees"], e4["weight_update_vectors"])


class TestExperimentsCLIDevice(unittest.TestCase):
    """Verify CLI argument parsing and execution modes for experiments.py."""

    def test_cli_help_displays_device_and_check_mps(self) -> None:
        cmd = [sys.executable, str(EXPERIMENTS_PY), "--help"]
        out = subprocess.check_output(cmd, text=True)
        self.assertIn("--device {cpu,mps}", out)
        self.assertIn("--check-mps", out)
        self.assertIn("--out", out)

    @unittest.skipUnless(
        hasattr(torch.backends, "mps") and torch.backends.mps.is_available(),
        "Apple MPS backend required for live execution check",
    )
    def test_live_check_mps(self) -> None:
        cmd = [sys.executable, str(EXPERIMENTS_PY), "--check-mps"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"experiments.py --check-mps failed: {res.stderr}")
        self.assertIn('"status": "PASS"', res.stdout)
        self.assertIn('"differences": 0', res.stdout)


if __name__ == "__main__":
    unittest.main()
