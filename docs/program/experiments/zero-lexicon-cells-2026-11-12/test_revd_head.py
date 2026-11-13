#!/usr/bin/env python3
"""Offline tests for the E08 thrust decoder (review 5884687083 item 3).

Runnable with: python3 -m unittest test_revd_head  (numpy only)."""
import math
import os
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zerolex_e08 as zx


class _Head:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        self.old = os.environ.get("NOLEX_HEAD")
        if self.value is None:
            os.environ.pop("NOLEX_HEAD", None)
        else:
            os.environ["NOLEX_HEAD"] = self.value

    def __exit__(self, *exc):
        if self.old is None:
            os.environ.pop("NOLEX_HEAD", None)
        else:
            os.environ["NOLEX_HEAD"] = self.old


class SoftHeadTests(unittest.TestCase):
    def test_component_bound(self):
        rng = np.random.default_rng(7)
        cases = [np.array(c, dtype=np.float64) for c in
                 ([100.0, 0.0], [0.0, -100.0], [1e3, -1e3], [1e6, 0.0], [0.0, 0.0])]
        cases += list(rng.standard_normal((2000, 2)) * rng.choice([0.1, 1.0, 10.0, 1e3], (2000, 1)))
        with _Head("soft"):
            for z in cases:
                u = zx.action_map(z)
                self.assertTrue(np.all(np.abs(u) < 1.0), (z, u))
                self.assertLess(float(np.dot(u, u)), 1.0)

    def test_registered_review_case(self):
        with _Head("soft"):
            u = zx.action_map(np.array([100.0, 0.0]))
        self.assertAlmostEqual(u[0], 100.0 / math.sqrt(2.0 + 100.0 ** 2), places=12)
        self.assertEqual(u[1], 0.0)

    def test_independent_of_non_thrust_coordinates(self):
        rng = np.random.default_rng(11)
        y = rng.standard_normal(256).astype(np.float32)
        y[64] = 100.0
        for head in (None, "soft"):
            with _Head(head):
                base = zx.decode_thrust(y)
                y0 = y.copy()
                y0[0] = 100.0
                np.testing.assert_array_equal(zx.decode_thrust(y0), base)
                y_all = y.copy()
                mask = np.ones(256, dtype=bool)
                mask[64:66] = False
                y_all[mask] = rng.standard_normal(254).astype(np.float32) * 1e3
                np.testing.assert_array_equal(zx.decode_thrust(y_all), base)

    def test_rejects_full_vector(self):
        with self.assertRaises(ValueError):
            zx.action_map(np.zeros(256))


class CallSiteTests(unittest.TestCase):
    def test_both_call_sites_use_decode_thrust(self):
        for head in (None, "soft"):
            with _Head(head):
                ents = {"A": zx.Entity(20261112), "B": zx.Entity(20261113)}
                zx.episode(ents, steps=1)
                for ent in ents.values():
                    np.testing.assert_array_equal(ent._u, zx.decode_thrust(ent._y))
                    np.testing.assert_array_equal(ent.thrust(np.zeros(16)),
                                                  zx.decode_thrust(ent.w @ zx.phi(np.zeros(16))))

    def test_tanh_head_matches_rev_c_formula(self):
        y = np.random.default_rng(3).standard_normal(256).astype(np.float32) * 5
        with _Head(None):
            np.testing.assert_array_equal(zx.decode_thrust(y), np.tanh(y / 2.0)[64:66].astype(np.float32))

    def test_unknown_head_rejected(self):
        with _Head("soft256"):
            with self.assertRaises(ValueError):
                zx.action_map(np.zeros(2))

    def test_run_config_records_decoder_env(self):
        with _Head("soft"):
            cfg = zx.run_config()
        self.assertEqual(cfg["NOLEX_HEAD"], "soft")
        self.assertEqual(cfg["head"], "soft")
        self.assertIn("NOLEX_PHI_SHUFFLE", cfg)
        self.assertEqual(cfg["NOLEX_NS_PAIRS"], zx.NS_PAIRS)


if __name__ == "__main__":
    unittest.main()
