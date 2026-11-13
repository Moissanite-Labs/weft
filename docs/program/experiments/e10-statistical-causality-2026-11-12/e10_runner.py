"""Experiment E10 Runnable Benchmark Suite (Track A Micro-Cell Scaling + Track B Causal/KL Entities)."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

DIM = 64
CORE_ROWS = 16
SEEDS_TRACK_A = [20261112 + i for i in range(12)]
# Reserved for a Track B runner that emits per-seed output. Unused by this file.
SEEDS_TRACK_B = [20261120 + i for i in range(12)]
ARMS_TRACK_A = [
    "Frozen_Control",
    "Mismatch_24_t1000",
    "Matched_80_Unscaled",
    "Matched_80_RMS_Antithetic",
]
TRACK_A_OUTPUT = Path(__file__).with_name("track_a_per_seed.json")
# Published Track A mean last-returns (four decimals), from this runner.
PUBLISHED_MEAN_LAST = {
    "Frozen_Control": 32.5814,
    "Mismatch_24_t1000": 32.6315,
    "Matched_80_Unscaled": 33.2787,
    "Matched_80_RMS_Antithetic": 40.7979,
}
PUBLISHED_MEAN_SEEDWISE_PCT_RMS = 0.2692
PUBLISHED_RATIO_OF_MEANS_RMS = 0.2522


def action_map_revd_fixed(z_full: np.ndarray, start: int, k: int) -> np.ndarray:
    z_s = z_full[start : start + k]
    return z_s / math.sqrt(float(k) + float(np.dot(z_s, z_s)))


def make_torus_obs_mlp(pos_self: np.ndarray, pos_other: np.ndarray, wave_c: np.ndarray, t_abs: int) -> np.ndarray:
    obs = np.zeros(16, dtype=np.float64)
    d_wave = np.sin(wave_c - pos_self)
    d_other = np.sin(pos_other - pos_self)
    obs[0:2], obs[2:4], obs[4:6] = d_wave, np.cos(wave_c - pos_self), d_other
    obs[6] = math.exp(-2.5 * float(np.linalg.norm(d_other)))
    obs[7], obs[8] = math.sin(0.08 * t_abs), math.cos(0.08 * t_abs)
    obs[9], obs[10], obs[11] = math.sin(0.16 * t_abs), math.cos(0.16 * t_abs), 1.0
    obs[12:16] = np.sin(np.arange(1, 5) * float(pos_self[0] - pos_self[1])) * 0.5
    return obs


def forward_microcell(w1: np.ndarray, w2: np.ndarray, obs: np.ndarray) -> np.ndarray:
    out = w2 @ np.maximum(0.0, w1 @ obs)
    mu, log_s2 = out[0:2], np.clip(out[2:4], -4.0, 0.5)
    return mu * (math.sqrt(2.0) / math.sqrt(2.0 + float(np.sum(mu ** 2) + np.sum(np.exp(log_s2)))))


def run_mlp_episode(ca, cb, ep_seed: int, t0: int, steps: int) -> Tuple[float, float]:
    rng = np.random.default_rng(ep_seed)
    pos_a = rng.uniform(-math.pi, math.pi, size=2)
    pos_b = pos_a + rng.uniform(-0.5, 0.5, size=2)
    base_c = rng.uniform(-math.pi, math.pi, size=2)
    ret_a, ret_b = 0.0, 0.0
    for s in range(steps):
        t_abs = t0 + s
        drift = np.array([0.06 * s + 1.15 * math.sin(0.05 * t_abs), -0.05 * s + 1.15 * math.cos(0.05 * t_abs)])
        wave_c = (base_c + drift + math.pi) % (2.0 * math.pi) - math.pi
        ua = forward_microcell(ca[0], ca[1], make_torus_obs_mlp(pos_a, pos_b, wave_c, t_abs))
        ub = forward_microcell(cb[0], cb[1], make_torus_obs_mlp(pos_b, pos_a, wave_c, t_abs))
        pos_a = (pos_a + 0.34 * ua + math.pi) % (2.0 * math.pi) - math.pi
        pos_b = (pos_b + 0.34 * ub + math.pi) % (2.0 * math.pi) - math.pi
        pen = 0.25 if float(np.linalg.norm(np.sin(0.5 * (pos_a - pos_b)))) * 2.0 < 0.35 else 0.0
        ret_a += 0.25 * float(np.sum(np.cos(pos_a - wave_c)) + 1.6) - pen
        ret_b += 0.25 * float(np.sum(np.cos(pos_b - wave_c)) + 1.6) - pen
    return ret_a, ret_b


def run_microcell_arm(seed: int, mode: str) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    h_core, h_pl, in_dim = 32, 64, 16
    p_plastic = h_pl * in_dim + 4 * h_pl
    def init_c(tag: bytes):
        crng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag + str(seed).encode()).digest()[:8], "little"))
        w1 = rng.standard_normal((h_core + h_pl, in_dim)) * 0.10
        w1[:h_core, :] = crng.standard_normal((h_core, in_dim)) * 0.15
        w2 = rng.standard_normal((4, h_core + h_pl)) * 0.08
        trig = crng.standard_normal(in_dim)
        trig /= np.linalg.norm(trig) + 1e-12
        return w1, w2, trig, w1[:h_core, :] @ trig
    w1_a0, w2_a0, trig_a, targ_a = init_c(b"MICRO_A_")
    w1_b0, w2_b0, trig_b, targ_b = init_c(b"MICRO_B_")
    w1_a, w2_a, w1_b, w2_b = w1_a0.copy(), w2_a0.copy(), w1_b0.copy(), w2_b0.copy()
    eval_test = lambda ca, cb: tuple(sum(x[i] for x in [run_mlp_episode(ca, cb, seed * 1000 + k, 0, 80) for k in range(3)]) / 3.0 for i in (0, 1))
    first_a, first_b = eval_test((w1_a, w2_a), (w1_b, w2_b))
    def probe(ca, cb):
        if mode == "Mismatch_24_t1000":
            return run_mlp_episode(ca, cb, seed * 500 + 7, 1000, 24)
        r1, r2 = run_mlp_episode(ca, cb, seed * 500 + 11, 0, 80), run_mlp_episode(ca, cb, seed * 500 + 29, 0, 80)
        return 0.5 * (r1[0] + r2[0]), 0.5 * (r1[1] + r2[1])
    commits, rejects, proposals = 0, 0, 0
    r_bound = 0.22 * math.sqrt(p_plastic) if mode == "Matched_80_RMS_Antithetic" else 3.80
    if mode != "Frozen_Control":
        bpa, bpb = probe((w1_a, w2_a), (w1_b, w2_b))
        m1a, m2a, m1b, m2b = np.zeros_like(w1_a), np.zeros_like(w2_a), np.zeros_like(w1_b), np.zeros_like(w2_b)
        for _ in range(40):
            if mode == "Matched_80_RMS_Antithetic":
                dw1a, dw1b, dw2a, dw2b = np.zeros_like(w1_a), np.zeros_like(w1_b), np.zeros_like(w2_a), np.zeros_like(w2_b)
                dw1a[h_core:] = 0.045 * rng.standard_normal((h_pl, in_dim)) + 0.35 * m1a[h_core:]
                dw1b[h_core:] = 0.045 * rng.standard_normal((h_pl, in_dim)) + 0.35 * m1b[h_core:]
                dw2a[:, h_core:] = 0.11 * rng.standard_normal((4, h_pl)) + 0.35 * m2a[:, h_core:]
                dw2b[:, h_core:] = 0.11 * rng.standard_normal((4, h_pl)) + 0.35 * m2b[:, h_core:]
                for sgn in (+1.0, -1.0):
                    proposals += 1
                    ca1, ca2, cb1, cb2 = w1_a + sgn * dw1a, w2_a + sgn * dw2a, w1_b + sgn * dw1b, w2_b + sgn * dw2b
                    if math.sqrt(float(np.sum((ca1 - w1_a0) ** 2) + np.sum((ca2 - w2_a0) ** 2))) > r_bound or math.sqrt(float(np.sum((cb1 - w1_b0) ** 2) + np.sum((cb2 - w2_b0) ** 2))) > r_bound:
                        rejects += 1
                        continue
                    cpa, cpb = probe((ca1, ca2), (cb1, cb2))
                    if (cpa + cpb) >= (bpa + bpb) * 1.008:
                        m1a, m2a, m1b, m2b = sgn * dw1a, sgn * dw2a, sgn * dw1b, sgn * dw2b
                        w1_a, w2_a, w1_b, w2_b, bpa, bpb = ca1, ca2, cb1, cb2, cpa, cpb
                        commits += 1
                        break
            else:
                for sc in (0.045, 0.095):
                    proposals += 1
                    dw1a, dw1b, dw2a, dw2b = np.zeros_like(w1_a), np.zeros_like(w1_b), np.zeros_like(w2_a), np.zeros_like(w2_b)
                    dw1a[h_core:], dw1b[h_core:] = rng.standard_normal((h_pl, in_dim)) * sc, rng.standard_normal((h_pl, in_dim)) * sc
                    dw2a[:, h_core:], dw2b[:, h_core:] = rng.standard_normal((4, h_pl)) * sc, rng.standard_normal((4, h_pl)) * sc
                    ca1, ca2, cb1, cb2 = w1_a + dw1a, w2_a + dw2a, w1_b + dw1b, w2_b + dw2b
                    if math.sqrt(float(np.sum((ca1 - w1_a0) ** 2) + np.sum((ca2 - w2_a0) ** 2))) > r_bound or math.sqrt(float(np.sum((cb1 - w1_b0) ** 2) + np.sum((cb2 - w2_b0) ** 2))) > r_bound:
                        rejects += 1
                        continue
                    cpa, cpb = probe((ca1, ca2), (cb1, cb2))
                    upd = False
                    if cpa >= bpa * 1.01:
                        w1_a, w2_a, upd = ca1, ca2, True
                    if cpb >= bpb * 1.01:
                        w1_b, w2_b, upd = cb1, cb2, True
                    if upd:
                        bpa, bpb = probe((w1_a, w2_a), (w1_b, w2_b))
                        commits += 1
    last_a, last_b = eval_test((w1_a, w2_a), (w1_b, w2_b))
    cd = float(np.linalg.norm(w1_a[:h_core] - w1_a0[:h_core]) + np.linalg.norm(w1_b[:h_core] - w1_b0[:h_core]))

    def _watermark_cos(w1: np.ndarray, trig: np.ndarray, targ: np.ndarray) -> float:
        resp = w1[:h_core, :] @ trig
        denom = float(np.linalg.norm(resp) * np.linalg.norm(targ)) + 1e-12
        return float(np.dot(resp, targ) / denom)

    wm = 0.5 * (_watermark_cos(w1_a, trig_a, targ_a) + _watermark_cos(w1_b, trig_b, targ_b))
    return {
        "first": 0.5 * (first_a + first_b),
        "last": 0.5 * (last_a + last_b),
        "commits": commits,
        "reject_rate": rejects / max(proposals, 1),
        "core_drift": cd,
        "watermark_cos": wm,
    }


def collect_track_a(seeds: List[int] | None = None) -> Dict[str, object]:
    seeds = list(SEEDS_TRACK_A if seeds is None else seeds)
    arms: Dict[str, object] = {}
    for mode in ARMS_TRACK_A:
        rows = []
        for seed in seeds:
            result = run_microcell_arm(seed, mode)
            first = float(result["first"])
            last = float(result["last"])
            pct = 0.0 if first == 0.0 else (last - first) / first
            rows.append({
                "seed": seed,
                "first": first,
                "last": last,
                "pct_change": pct,
                "commits": int(result["commits"]),
                "reject_rate": float(result["reject_rate"]),
                "core_drift": float(result["core_drift"]),
                "watermark_cos": float(result["watermark_cos"]),
            })
        mean_last = float(np.mean([row["last"] for row in rows]))
        arms[mode] = {
            "seeds": rows,
            "mean_last": mean_last,
            "mean_pct_change": float(np.mean([row["pct_change"] for row in rows])),
            "seeds_improved": int(sum(1 for row in rows if row["last"] > row["first"])),
            "mean_reject_rate": float(np.mean([row["reject_rate"] for row in rows])),
            "n": len(rows),
        }
    frozen_mean = arms["Frozen_Control"]["mean_last"]
    rms_mean = arms["Matched_80_RMS_Antithetic"]["mean_last"]
    return {
        "arms": arms,
        "mean_of_seedwise_pct_rms": arms["Matched_80_RMS_Antithetic"]["mean_pct_change"],
        "ratio_of_means_rms_vs_frozen": (rms_mean / frozen_mean - 1.0) if frozen_mean else 0.0,
    }


def write_track_a_output(payload: Dict[str, object], path: Path = TRACK_A_OUTPUT) -> Path:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


class TestE10Invariants(unittest.TestCase):
    def test_slice_local_revd_bounds(self):
        z1 = np.zeros(256)
        z1[64] = 100.0
        u1 = action_map_revd_fixed(z1, 64, 2)
        self.assertLess(abs(float(u1[0])), 1.0)
        z2 = z1.copy()
        z2[:64] = 999.0
        np.testing.assert_allclose(u1, action_map_revd_fixed(z2, 64, 2), rtol=0, atol=1e-15)

    def test_rms_antithetic_core_invariance(self):
        r = run_microcell_arm(20261112, "Matched_80_RMS_Antithetic")
        self.assertEqual(r["core_drift"], 0.0)
        self.assertAlmostEqual(r["watermark_cos"], 1.0, places=11)
        self.assertGreater(r["last"], r["first"])

    def test_published_track_a_means(self):
        payload = collect_track_a()
        arms = payload["arms"]
        for mode, expected in PUBLISHED_MEAN_LAST.items():
            self.assertAlmostEqual(arms[mode]["mean_last"], expected, places=4, msg=mode)
        self.assertEqual(arms["Matched_80_RMS_Antithetic"]["seeds_improved"], 12)
        self.assertAlmostEqual(payload["mean_of_seedwise_pct_rms"], PUBLISHED_MEAN_SEEDWISE_PCT_RMS, places=4)
        self.assertAlmostEqual(payload["ratio_of_means_rms_vs_frozen"], PUBLISHED_RATIO_OF_MEANS_RMS, places=4)
        for mode in ARMS_TRACK_A:
            for row in arms[mode]["seeds"]:
                self.assertEqual(row["core_drift"], 0.0)
                self.assertAlmostEqual(row["watermark_cos"], 1.0, places=11)


if __name__ == "__main__":
    if "--full" not in sys.argv:
        unittest.main(verbosity=2)
    else:
        payload = collect_track_a()
        path = write_track_a_output(payload)
        means = {mode: payload["arms"][mode]["mean_last"] for mode in ARMS_TRACK_A}
        print(json.dumps({
            "means": means,
            "mean_of_seedwise_pct_rms": payload["mean_of_seedwise_pct_rms"],
            "ratio_of_means_rms_vs_frozen": payload["ratio_of_means_rms_vs_frozen"],
            "path": str(path),
        }, indent=2))
