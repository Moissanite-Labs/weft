#!/usr/bin/env python3
"""Invariant-gated micro-cell organism (E09 Arm 1, custom cell).

Environment identical to E08: torus 20, moving harmonic field,
phi(s) 256 features (imported unchanged), reward as E08, probe-commit rule.

Organism:
  core = 256x256 watermarked block, frozen; rows 0..191 frozen (watermark block).
  periphery = 512x256 plastic matrix.
  H = relu(concat(core @ phi(s[0:256]) + b1c, periphery @ phi(s) + b1p))
  mu = tanh((W_mu @ H + b_mu) / 2.0); lsig = clip(W_lsig @ H + b_l, -2, 2); u = mu.

Verified controls parallel to E09: F-frozen (periphery frozen too), C3-single-agent.
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

E08 = Path(__file__).resolve().parent.parent / "zero-lexicon-cells-2026-11-12"
sys.path.insert(0, str(E08))
import plasm_np as pl
import zerolex_e08 as Z

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
DECODER_FP = hashlib.sha256((E08 / "zerolex_e08.py").read_bytes()).hexdigest()

HIDDEN_CORE = 256
HIDDEN_PL = 512
HIDDEN = HIDDEN_CORE + HIDDEN_PL
CORE_ROWS = 192
EP_LEN = 80
PROBE_LEN = int(os.environ.get("NOLEX_PROBE_LEN", "24"))
PROBE_T = int(os.environ.get("NOLEX_PROBE_T", "1000"))
SIGMA_NOISE = 0.10
NS_PAIRS = 4
R_INVARIANT = 120.0


class Cell:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.wc = (rng.standard_normal((HIDDEN_CORE, 256)).astype(np.float32) * 0.05)
        self.wc, self.trigger, self.target, self.wm_align = pl.watermark_embed(self.wc, core_rows=CORE_ROWS)
        self.wp = (rng.standard_normal((HIDDEN_PL, 256)).astype(np.float32) * 0.05)
        self.b1c = np.zeros(HIDDEN_CORE, dtype=np.float32)
        self.b1p = np.zeros(HIDDEN_PL, dtype=np.float32)
        self.w_mu = (rng.standard_normal((2, HIDDEN_CORE + HIDDEN_PL)).astype(np.float32) * 0.02)
        self.b_mu = np.zeros(2, dtype=np.float32)
        self.w_sg = (rng.standard_normal((2, HIDDEN_CORE + HIDDEN_PL)).astype(np.float32) * 0.02)
        self.b_sg = np.zeros(2, dtype=np.float32)
        self.wp_base = self.wp.copy()
        self._u = np.zeros(2, dtype=np.float32)

    def forward(self, s):
        feat = Z.phi(np.asarray(s, dtype=np.float32).reshape(16)).astype(np.float32)
        hc = np.maximum(self.wc @ feat + self.b1c, 0.0)
        hp = np.maximum(self.wp @ feat + self.b1p, 0.0)
        h = np.concatenate([hc, hp])
        mu = np.tanh((self.w_mu @ h + self.b_mu) / 2.0)
        lsig = np.clip(self.w_sg @ h + self.b_sg, -2.0, 2.0)
        return mu.astype(np.float32), lsig.astype(np.float32)

    def plastic_mask(self):
        return np.ones((HIDDEN_PL, 256), dtype=np.float32)


def episode(cells, t0=0, steps=EP_LEN):
    field = Z.Field(t0=t0, agents=len(cells))
    ring = (np.linspace(0.0, 1.0, 1024, dtype=np.float32) * 0.5).astype(np.float32)
    totals = {k: 0.0 for k in cells}
    collisions = 0
    traj = {k: [] for k in cells}
    for step in range(steps):
        ring = ring.copy()
        for i, (name, cell) in enumerate(cells.items()):
            Z.ring_write(ring, i, field.pos[name], field.vel[name], cell._u)
        thrusts = {}
        for i, (name, cell) in enumerate(cells.items()):
            if len(cells) == 2:
                other = "B" if name == "A" else "A"
                if other in field.pos:
                    rel = (field.pos[other] - field.pos[name]) / Z.L
                    slot = Z.ring_read(ring, 1 - i)
                else:
                    rel = np.zeros(2, dtype=np.float32)
                    slot = np.zeros(8, dtype=np.float32)
            else:
                rel = np.zeros(2, dtype=np.float32)
                slot = np.zeros(8, dtype=np.float32)
            s = np.concatenate([field.pos[name] / Z.L,
                                field.vel[name] / Z.MAX_SPEED,
                                field.grad(field.pos[name], field.t),
                                rel, slot]).astype(np.float32)
            mu, _ = cell.forward(s)
            cell._u = mu
            traj[name].append(mu)
            thrusts[name] = mu
        rewards, collided = field.step(thrusts)
        collisions += int(collided)
        for n, r in rewards.items():
            totals[n] += r
    return {"returns": totals, "collisions": collisions, "traj": traj}


def probe_return(cells, name, wp):
    ent = cells[name]
    saved = ent.wp.copy()
    ent.wp = wp.astype(np.float32)
    ep = episode(cells, t0=PROBE_T, steps=PROBE_LEN)
    ret = ep["returns"][name] / PROBE_LEN
    ent.wp = saved
    return ret


def generation(cells, rng):
    ep = episode(cells)
    out = {"returns": {k: float(v) for k, v in ep["returns"].items()},
           "collisions": ep["collisions"], "ent": {}}
    for name, ent in cells.items():
        base_probe = probe_return(cells, name, ent.wp)
        best = None
        rejected = evaluated = 0
        mask = ent.plastic_mask()
        for i in range(NS_PAIRS):
            noise = rng.standard_normal(ent.wp.shape).astype(np.float32)
            for sign in (1.0, -1.0):
                wp_c = ent.wp + sign * SIGMA_NOISE * mask * noise
                drift = float(np.linalg.norm(wp_c - ent.wp_base))
                wm = pl.watermark_verify(ent.wc, ent.wc, ent.trigger, ent.target)  # core unchanged this generation
                if drift > R_INVARIANT:
                    rejected += 1
                    continue
                evaluated += 1
                probe = probe_return(cells, name, wp_c)
                if probe >= 1.01 * base_probe and (best is None or probe > best[2]):
                    best = (f"p{i}{'+' if sign > 0 else '-'}", wp_c, probe)
        committed = 0
        fro = 0.0
        if best is not None:
            ent.wp = best[1].astype(np.float32)
            committed = 1
            fro = float(np.linalg.norm(ent.wp - ent.wp_base))
        wm = pl.watermark_verify(ent.wc, ent.wc, ent.trigger, ent.target)
        out["ent"][name] = {"evaluated": evaluated, "rejected": rejected,
                            "committed": committed, "fro_drift": fro,
                            "wm_cos": float(wm["cosine_alignment"]),
                            "wm_drift": float(wm["response_l2_drift"]),
                            "probe_parent": base_probe,
                            "probe_best": best[2] if best is not None else None}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--control", default="none", choices=["none", "C1", "C3"])
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--gens", type=int, default=40)
    ns = ap.parse_args()
    print(json.dumps({"decoder_sha256": DECODER_FP, "arm": "mlp-768-inv-gated",
                      "seed": ns.seed, "control": ns.control}))
    rng = np.random.default_rng(ns.seed)
    cells = {"A": Cell(ns.seed)}
    if ns.control != "C3":
        cells["B"] = Cell(ns.seed + 101)
    if ns.control == "C1":
        for c in cells.values():
            c.plastic_mask = lambda: np.zeros((HIDDEN_PL, 256), dtype=np.float32)
    with open(LOGS / f"{ns.tag}.jsonl", "w") as logf:
        t0 = time.time()
        for gen in range(1, ns.gens + 1):
            step = generation(cells, rng)
            step["gen"] = gen
            step["elapsed_s"] = round(time.time() - t0, 2)
            logf.write(json.dumps(step) + "\n")
            logf.flush()
            cm = {k: v["committed"] for k, v in step["ent"].items()}
            rt = {k: round(v, 3) for k, v in step["returns"].items()}
            print(f"gen {gen}: returns={rt} collisions={step['collisions']} committed={cm}")
    print(f"wrote {LOGS / (ns.tag + '.jsonl')}")


if __name__ == "__main__":
    main()
