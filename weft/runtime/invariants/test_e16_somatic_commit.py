#!/usr/bin/env python3
"""Discover the E16 somatic C2 commit tests from the experiment tree."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_TEST_FILE = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "program"
    / "experiments"
    / "endogenous-cells-e16-2026-11"
    / "test_run_e16.py"
)


def load_tests(loader, tests, pattern):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("test_run_e16", _TEST_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load E16 somatic tests from {_TEST_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return loader.loadTestsFromModule(module)


if __name__ == "__main__":
    unittest.main()
