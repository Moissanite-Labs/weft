#!/usr/bin/env python3
"""Tests for scripts/check_lanes.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_lanes", ROOT / "scripts" / "check_lanes.py")
assert spec and spec.loader
lanes = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lanes
spec.loader.exec_module(lanes)


class MisplacedTest(unittest.TestCase):
    def test_build_paths_pass(self) -> None:
        paths = [
            "weft/runtime/plasm/plasm.py",
            "site/index.html",
            "papers/01-models-as-cells/paper.md",
            "docs/program/build-program.md",
            "docs/interfaces/I4-shared-memory.md",
            "scripts/check_lanes.py",
        ]
        self.assertEqual(lanes.misplaced(paths), [])

    def test_research_dirs_fail(self) -> None:
        paths = [
            "docs/program/experiments/E07/README.md",
            "docs/program/audit/README.md",
            "experiments/e14_suite/protocol.json",
            "audit/ledger.json",
            "incidents/2026-11-13/README.md",
            "notes/idea.md",
        ]
        self.assertEqual(lanes.misplaced(paths), sorted(paths))

    def test_kept_design_notes_pass_and_new_ones_fail(self) -> None:
        kept = sorted(lanes.KEPT_DESIGN_NOTES)
        new = "docs/design-notes/horizon-ii-ideas-backlog.md"
        self.assertEqual(lanes.misplaced(kept + [new]), [new])

    def test_prefix_is_a_directory_not_a_word(self) -> None:
        # "experiments.py" at the root or a paper's experiments.py is code, not a record.
        paths = ["experiments.py", "papers/02-checkable-computation/experiments.py", "auditor.py"]
        self.assertEqual(lanes.misplaced(paths), [])

    def test_current_tree_is_clean(self) -> None:
        self.assertEqual(lanes.misplaced(lanes.tracked_files()), [])


if __name__ == "__main__":
    unittest.main()
