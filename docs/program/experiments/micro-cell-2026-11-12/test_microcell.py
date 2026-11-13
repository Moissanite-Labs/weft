#!/usr/bin/env python3
"""Offline regression checks for microcell.py. No network, no API calls.

Run: python3 -m unittest discover -s docs/program/experiments/micro-cell-2026-11-12 -p 'test_*.py'
"""
import json
import unittest
from pathlib import Path

import numpy as np

import microcell as M

SEED = 20261112
LOGS = Path(__file__).resolve().parent / "logs"


def candidates(cell, n, seed=7):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        noise = rng.standard_normal(cell.wp.shape).astype(np.float32)
        for sign in (1.0, -1.0):
            out.append(cell.wp + sign * M.SIGMA_NOISE * noise)
    return out


class EpisodeStateTests(unittest.TestCase):
    def test_identical_weights_reset_u_same_return(self):
        cells = M.build_cells(SEED)
        first = M.episode(cells)["returns"]
        # Leave arbitrary previous-action state behind; the reset must erase it.
        for c in cells.values():
            c._u = np.array([0.7, -0.4], dtype=np.float32)
        second = M.episode(cells)["returns"]
        self.assertEqual(first, second)

    def test_legacy_mode_shows_the_leak(self):
        cells = M.build_cells(SEED)
        first = M.episode(cells, legacy_u_leak=True)["returns"]
        second = M.episode(cells, legacy_u_leak=True)["returns"]
        self.assertNotEqual(first, second)

    def test_reversing_candidate_order_keeps_each_score(self):
        for probe_len, probe_t in (M.PROTOCOLS["e09"].values(), M.PROTOCOLS["e10"].values()):
            cells = M.build_cells(SEED)
            cands = candidates(cells["A"], 2)
            fwd = [M.probe_return(cells, "A", c, probe_t, probe_len) for c in cands]
            rev = [M.probe_return(cells, "A", c, probe_t, probe_len) for c in reversed(cands)]
            self.assertEqual(fwd, list(reversed(rev)))

    def test_probe_leaves_state_unchanged(self):
        cells = M.build_cells(SEED)
        M.episode(cells)  # leaves non-zero _u, as in a real generation
        before = {k: (c.wp.copy(), c._u.copy(), c.wc.copy()) for k, c in cells.items()}
        self.assertTrue(any(np.any(b[1] != 0) for b in before.values()))
        for cand in candidates(cells["A"], 1):
            M.probe_return(cells, "A", cand, 1000, 24)
        for k, c in cells.items():
            np.testing.assert_array_equal(c.wp, before[k][0])
            np.testing.assert_array_equal(c._u, before[k][1])
            np.testing.assert_array_equal(c.wc, before[k][2])

    def test_failed_probe_restores_state(self):
        cells = M.build_cells(SEED)
        M.episode(cells)
        before = {k: (c.wp.copy(), c._u.copy()) for k, c in cells.items()}
        real = M.episode

        def boom(*a, **kw):
            for c in cells.values():
                c._u = np.array([9.0, 9.0], dtype=np.float32)
            raise RuntimeError("trial failed")

        M.episode = boom
        try:
            with self.assertRaises(RuntimeError):
                M.probe_return(cells, "A", candidates(cells["A"], 1)[0], 1000, 24)
        finally:
            M.episode = real
        for k, c in cells.items():
            np.testing.assert_array_equal(c.wp, before[k][0])
            np.testing.assert_array_equal(c._u, before[k][1])

    def test_frozen_control_is_flat_after_fix(self):
        cells = M.build_cells(SEED, control="C1")
        rng = np.random.default_rng(SEED)
        rows = [M.generation(cells, rng, 1000, 24) for _ in range(3)]
        self.assertEqual(rows[0]["returns"], rows[1]["returns"])
        self.assertEqual(rows[1]["returns"], rows[2]["returns"])


class CoreGateTests(unittest.TestCase):
    def test_core_drift_measured_against_base(self):
        cells = M.build_cells(SEED)
        ok, drift, wm = M.core_check(cells["A"])
        self.assertTrue(ok)
        self.assertEqual(drift, 0.0)
        cells["A"].wc = cells["A"].wc + 1e-3
        ok, drift, wm = M.core_check(cells["A"])
        self.assertFalse(ok)
        self.assertGreater(drift, 0.0)
        self.assertGreater(wm["response_l2_drift"], 0.0)

    def test_core_change_rejects_every_candidate(self):
        cells = M.build_cells(SEED)
        cells["A"].wc = cells["A"].wc + 1e-3
        row = M.generation(cells, np.random.default_rng(SEED), 1000, 24)
        a = row["ent"]["A"]
        self.assertEqual(a["committed"], 0)
        self.assertEqual(a["evaluated"], 0)
        self.assertEqual(a["rejected_core"], 2 * M.NS_PAIRS)
        self.assertGreater(a["core_drift"], 0.0)


class ProtocolTests(unittest.TestCase):
    def test_protocol_defaults(self):
        self.assertEqual(M.resolve_probe("e09", env={}), (24, 1000))
        self.assertEqual(M.resolve_probe("e10", env={}), (80, 0))
        self.assertEqual(M.resolve_probe("e10", env={"NOLEX_PROBE_LEN": "30"}), (30, 0))
        self.assertEqual(M.resolve_probe("e09", 12, 5, env={"NOLEX_PROBE_LEN": "30"}), (12, 5))

    def test_vendored_decoder_hash_matches_logs(self):
        self.assertEqual(M.DECODER_FP, M.DECODER_SHA256_PINNED)
        header = json.loads((LOGS / "main-12.out").read_text().splitlines()[0])
        self.assertEqual(header["decoder_sha256"], M.DECODER_SHA256_PINNED)

    def test_legacy_mode_reproduces_committed_log_start(self):
        committed = [json.loads(l) for l in (LOGS / "seed-a.jsonl").read_text().splitlines()[:3]]
        cells = M.build_cells(SEED)
        rng = np.random.default_rng(SEED)
        for row in committed:
            new = M.generation(cells, rng, 1000, 24, legacy_u_leak=True)
            for k in ("A", "B"):
                self.assertAlmostEqual(new["returns"][k], row["returns"][k], delta=1e-3)
                self.assertEqual(new["ent"][k]["committed"], row["ent"][k]["committed"])

    def test_no_absolute_home_paths_in_logs(self):
        for f in LOGS.iterdir():
            self.assertNotIn("/Users/", f.read_text(), f.name)


if __name__ == "__main__":
    unittest.main()
