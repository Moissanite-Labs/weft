#!/usr/bin/env python3
"""Run the lineage exit checks, writing output to a temporary directory."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "run_lineage.py"
TRACKED = HERE / "results.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("native_lineage_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestLineageRecord(unittest.TestCase):
    def test_exit_checks_write_to_temporary_out(self):
        tracked_mtime = TRACKED.stat().st_mtime if TRACKED.exists() else None
        runner = load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "results.json"
            runner.main(["--out", str(out)])
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size, 0)
        if tracked_mtime is not None:
            self.assertEqual(TRACKED.stat().st_mtime, tracked_mtime)


if __name__ == "__main__":
    unittest.main()
