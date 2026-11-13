#!/usr/bin/env python3
"""Invariant-gated micro-cell organism (E09 Arm 1, custom cell; E10 reuses it).

Environment identical to E08: torus 20, moving harmonic field,
phi(s) 256 features (imported unchanged), reward as E08, probe-commit rule.

Organism as it actually runs (correction 2026-11-12, see 00-DESIGN.md):
  core      wc = 256x256 watermarked block, frozen in full (never written).
  periphery wp = 512x256 matrix, the only plastic parameters.
  H  = relu(concat(wc @ phi(s) + b1c, wp @ phi(s) + b1p))     (768 units)
  mu = tanh((W_mu @ H + b_mu) / 2.0); u = mu (deterministic thrust).
  lsig = clip(W_sg @ H + b_sg, -2, 2) is computed but unused.
  W_mu, W_sg and all biases stay at their initial values.

Gate per candidate: ||wp_c - wp_base||_F <= R_INVARIANT, ||wc - wc_base||_F == 0.0
and watermark_verify(wc_base, wc).cosine >= 0.85 (registered cut), then the
probe rule: commit iff probe >= 1.01 * parent probe.

Episode-local state: every cell's previous action `_u` is zeroed at the start
of every episode, and `probe_return` snapshots and restores `wp` and every
cell's `_u`, also when a trial fails. `--legacy-u-leak` restores the pre-fix
behaviour that produced the committed logs (no reset at episode entry, only
`wp` restored after a probe).

Protocols: `--protocol e09` probes 24 steps at t=1000 (E08/E09 setting);
`--protocol e10` probes 80 steps at t=0 (the settings of logs/e10-*.jsonl).
`--probe-len/--probe-t` or NOLEX_PROBE_LEN/NOLEX_PROBE_T override the protocol;
the values used are printed in the run header and written in every jsonl row.

Dependencies: numpy, plus `plasm_np.py` and `zerolex_e08.py` vendored
byte-for-byte in `vendor_e08/` from PR #141 head c62d2653 (sha256 pinned below).
Controls: C1 frozen (periphery frozen too), C3 single agent.
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

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
VENDOR = ROOT / "vendor_e08"
# Pinned to PR #141 head c62d2653; this is the decoder hash in every committed stdout header.
DECODER_SHA256_PINNED = "3e18e18e2c26ab2efea284ef8ba32b3ba83a80918054374b10a825b16432a12b"
PLASM_NP_SHA256_PINNED = "2343f4c876b4cc2129c01213161dd283a2f7ca7d7ca4e13c000bb5de82bcd170"


def _check_vendor():
    pins = {"zerolex_e08.py": DECODER_SHA256_PINNED, "plasm_np.py": PLASM_NP_SHA256_PINNED}
    for fname, want in pins.items():
        path = VENDOR / fname
        if not path.is_file():
            sys.exit(f"microcell.py: missing {path}. This record needs the vendored E08 modules "
                     f"in vendor_e08/ (copied from PR #141 head c62d2653).")
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != want:
            sys.exit(f"microcell.py: {path} has sha256 {got}, expected {want}. "
                     f"Restore the pinned copy from PR #141 head c62d2653.")


_check_vendor()
sys.path.insert(0, str(VENDOR))
import plasm_np as pl  # noqa: E402
import zerolex_e08 as Z  # noqa: E402

DECODER_FP = hashlib.sha256((VENDOR / "zerolex_e08.py").read_bytes()).hexdigest()

HIDDEN_CORE = 256
HIDDEN_PL = 512
HIDDEN = HIDDEN_CORE + HIDDEN_PL
CORE_ROWS = 192
EP_LEN = 80
PROTOCOLS = {"e09": {"probe_len": 24, "probe_t": 1000},
             "e10": {"probe_len": 80, "probe_t": 0}}
SIGMA_NOISE = 0.10
NS_PAIRS = 4
R_INVARIANT = 120.0
WM_MIN_COS = 0.85


def resolve_probe(protocol, probe_len=None, probe_t=None, env=None):
    """Probe settings: explicit argument > NOLEX_PROBE_* env var > protocol default."""
    env = os.environ if env is None else env
    base = PROTOCOLS[protocol]
    if probe_len is None:
        probe_len = int(env["NOLEX_PROBE_LEN"]) if "NOLEX_PROBE_LEN" in env else base["probe_len"]
    if probe_t is None:
        probe_t = int(env["NOLEX_PROBE_T"]) if "NOLEX_PROBE_T" in env else base["probe_t"]
    return int(probe_len), int(probe_t)


class Cell:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.wc = (rng.standard_normal((HIDDEN_CORE, 256)).astype(np.float32) * 0.05)
        self.wc, self.trigger, self.target, self.wm_align = pl.watermark_embed(self.wc, core_rows=CORE_ROWS)
        self.wc_base = self.wc.copy()
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


def reset_episode_state(cells):
    for cell in cells.values():
        cell._u = np.zeros(2, dtype=np.float32)


def episode(cells, t0=0, steps=EP_LEN, legacy_u_leak=False):
    if not legacy_u_leak:
        reset_episode_state(cells)
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


def probe_return(cells, name, wp, probe_t, probe_len, legacy_u_leak=False):
    ent = cells[name]
    saved_wp = ent.wp.copy()
    saved_u = {k: c._u.copy() for k, c in cells.items()}
    try:
        ent.wp = wp.astype(np.float32)
        ep = episode(cells, t0=probe_t, steps=probe_len, legacy_u_leak=legacy_u_leak)
        return ep["returns"][name] / probe_len
    finally:
        ent.wp = saved_wp
        if not legacy_u_leak:
            for k, c in cells.items():
                c._u = saved_u[k]


def core_check(ent):
    core_drift = float(np.linalg.norm(ent.wc - ent.wc_base))
    wm = pl.watermark_verify(ent.wc_base, ent.wc, ent.trigger, ent.target)
    ok = core_drift == 0.0 and wm["cosine_alignment"] >= WM_MIN_COS
    return ok, core_drift, wm


def generation(cells, rng, probe_t, probe_len, legacy_u_leak=False):
    ep = episode(cells, legacy_u_leak=legacy_u_leak)
    out = {"returns": {k: float(v) for k, v in ep["returns"].items()},
           "collisions": ep["collisions"], "ent": {}}
    for name, ent in cells.items():
        base_probe = probe_return(cells, name, ent.wp, probe_t, probe_len, legacy_u_leak)
        best = None
        rejected = rejected_core = evaluated = 0
        mask = ent.plastic_mask()
        for i in range(NS_PAIRS):
            noise = rng.standard_normal(ent.wp.shape).astype(np.float32)
            for sign in (1.0, -1.0):
                wp_c = ent.wp + sign * SIGMA_NOISE * mask * noise
                drift = float(np.linalg.norm(wp_c - ent.wp_base))
                core_ok, _, _ = core_check(ent)
                if not core_ok:
                    rejected += 1
                    rejected_core += 1
                    continue
                if drift > R_INVARIANT:
                    rejected += 1
                    continue
                evaluated += 1
                probe = probe_return(cells, name, wp_c, probe_t, probe_len, legacy_u_leak)
                if probe >= 1.01 * base_probe and (best is None or probe > best[2]):
                    best = (f"p{i}{'+' if sign > 0 else '-'}", wp_c, probe)
        committed = 0
        fro = 0.0
        if best is not None:
            ent.wp = best[1].astype(np.float32)
            committed = 1
            fro = float(np.linalg.norm(ent.wp - ent.wp_base))
        _, core_drift, wm = core_check(ent)
        out["ent"][name] = {"evaluated": evaluated, "rejected": rejected,
                            "rejected_core": rejected_core,
                            "committed": committed, "fro_drift": fro,
                            "core_drift": core_drift,
                            "wm_cos": float(wm["cosine_alignment"]),
                            "wm_drift": float(wm["response_l2_drift"]),
                            "probe_parent": base_probe,
                            "probe_best": best[2] if best is not None else None,
                            "best_id": best[0] if best is not None else None}
    return out


def build_cells(seed, control="none"):
    cells = {"A": Cell(seed)}
    if control != "C3":
        cells["B"] = Cell(seed + 101)
    if control == "C1":
        for c in cells.values():
            c.plastic_mask = lambda: np.zeros((HIDDEN_PL, 256), dtype=np.float32)
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--control", default="none", choices=["none", "C1", "C3"])
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--gens", type=int, default=40)
    ap.add_argument("--protocol", default="e09", choices=sorted(PROTOCOLS))
    ap.add_argument("--probe-len", type=int, default=None)
    ap.add_argument("--probe-t", type=int, default=None)
    ap.add_argument("--legacy-u-leak", action="store_true",
                    help="reproduce the pre-fix instrument of the committed logs")
    ns = ap.parse_args()
    probe_len, probe_t = resolve_probe(ns.protocol, ns.probe_len, ns.probe_t)
    LOGS.mkdir(exist_ok=True)
    print(json.dumps({"decoder_sha256": DECODER_FP, "arm": "mlp-768-inv-gated",
                      "seed": ns.seed, "control": ns.control, "protocol": ns.protocol,
                      "PROBE_LEN": probe_len, "PROBE_T": probe_t, "EP_LEN": EP_LEN,
                      "u_reset": not ns.legacy_u_leak}))
    rng = np.random.default_rng(ns.seed)
    cells = build_cells(ns.seed, ns.control)
    with open(LOGS / f"{ns.tag}.jsonl", "w") as logf:
        t0 = time.time()
        for gen in range(1, ns.gens + 1):
            step = generation(cells, rng, probe_t, probe_len, ns.legacy_u_leak)
            step["gen"] = gen
            step["probe_len"] = probe_len
            step["probe_t"] = probe_t
            step["u_reset"] = not ns.legacy_u_leak
            step["elapsed_s"] = round(time.time() - t0, 2)
            logf.write(json.dumps(step) + "\n")
            logf.flush()
            cm = {k: v["committed"] for k, v in step["ent"].items()}
            rt = {k: round(v, 3) for k, v in step["returns"].items()}
            print(f"gen {gen}: returns={rt} collisions={step['collisions']} committed={cm}")
    print(f"wrote {(LOGS / (ns.tag + '.jsonl')).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
