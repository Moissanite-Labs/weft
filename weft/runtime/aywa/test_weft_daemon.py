#!/usr/bin/env python3
"""Tests for the Aywa one-shot telemetry daemon (issue #78)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weft_daemon import MAX_RELATIVE_CLOCK_SECONDS, build_unified_64b_frame  # noqa: E402


class TestWeftDaemonElapsedSeconds(unittest.TestCase):
    def test_elapsed_seconds_is_written_to_slot_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = build_unified_64b_frame(tmp, elapsed_seconds=12.5)
        self.assertEqual(res["shm_frame_64b_head"][2], 12.5)

    def test_out_of_range_elapsed_seconds_raises(self) -> None:
        for bad in (-1.0, MAX_RELATIVE_CLOCK_SECONDS + 10.0, float("nan"), float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    build_unified_64b_frame(elapsed_seconds=bad)

    def test_zero_elapsed_seconds_static_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = build_unified_64b_frame(tmp, elapsed_seconds=0.0)
        self.assertEqual(res["shm_frame_64b_head"][2], 0.0)


if __name__ == "__main__":
    unittest.main()
