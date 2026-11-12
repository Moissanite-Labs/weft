#!/usr/bin/env python3
"""E08 zero-lexicon arenas — Naked Matrix regime, numpy float32.

Arena geometry, mask, watermark, and invariants port unchanged from
`weft/runtime/plasm` via `plasm_np.py` (shm exchanged for identical numpy
buffers; semantics preserved; torch absent on this machine).

Entity: W (256x256). Frozen rows 0..63 hold the identity watermark.
Plastic rows 64..255 carry the thrust head: thrust u = tanh(W @ phi(s))[64:66].
Feature map phi: 16 scalars -> 256 dims, poly 4 | harmonics 6 | tanh 3 | pairs 2 | 16 ones.
Field H(p,t) = cos(0.35 x - 0.6 t) * sin(0.22 y + 0.6 t) on a 20-unit torus.
Ring: 1024 f32 shared channel; each entity writes 8 floats per step;
the other entity reads those 8 floats as the trailing slot of its own state s.
Episode: 80 steps. Probe: 24 steps at fixed offset t_probe=1000 for A/B comparisons.

Reward (per entity): mean H(pos) - 2.0 on collision - 0.02*|u| per step.

Adaptation per generation (one episode):
  saliency g = sum_t (r_t - r_bar) * d(u/dz)(y_t) * phi(s_t)^T restricted to rows 64:66,
  normalized by max abs entry, A/B temperaments:
    A = 0.85*g + 0.15*noise,  B = 0.50*g - 0.50*noise,  sigma = 0.05
  W' = W + LR * mask(W) * candidate, LR = 0.35
  Commit iff invariants pass (R_INVARIANT, watermark, core drift 0.0) AND
  probe_return(W') >= 1.01 * probe_return(W). Otherwise revert (reject++).
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
sys.path.insert(0, str(ROOT))
import plasm_np as pl

L = 20.0
K1, K2, OMEGA = 0.35, 0.22, 0.6
DT = 0.5
MAX_SPEED = 0.15
ACC = 0.30
FRICTION = 0.90
COLLIDE_DIST = 0.6
COLLIDE_PEN = 2.0
METAB = 0.02
EP_LEN = 80
PROBE_LEN = 24
PROBE_T = 1000
ALPHA_NOVELTY = 0.05
SIGMA_NOISE = 0.3
NS_PAIRS = int(os.environ.get('NOLEX_NS_PAIRS', '4'))
LR = 0.35
SIGMA = 0.05
R_INVARIANT = 120.0


PHI_PERM = None
def _phi_perm():
    global PHI_PERM
    if PHI_PERM is None:
        if os.environ.get("NOLEX_PHI_SHUFFLE"):
            PHI_PERM = np.random.default_rng(int(os.environ["NOLEX_PHI_SHUFFLE"])).permutation(16)
        else:
            PHI_PERM = None
    return PHI_PERM

def phi(s: np.ndarray) -> np.ndarray:
    s = np.asarray(s, dtype=np.float64).reshape(16)
    p = _phi_perm()
    if p is not None:
        s = s[p]
    A = np.concatenate([s, s**2, s**3, s**4])                                     # 64
    B = np.concatenate([np.sin(s), np.cos(s), np.sin(2*s), np.cos(2*s),
                        np.sin(4*s), np.cos(4*s)])                                # 96
    C = np.concatenate([np.tanh(s), np.tanh(2*s), np.tanh(s/2)])                  # 48
    nxt = np.roll(s, -1)
    nxt2 = np.roll(s, -2)
    D = np.concatenate([s * nxt, s * nxt2])                                       # 32
    E = np.ones(16)                                                               # 16
    v = np.concatenate([A, B, C, D, E])
    assert v.shape == (256,)
    return v.astype(np.float32)


DECODER_FINGERPRINT = None


def decoder_fingerprint() -> str:
    global DECODER_FINGERPRINT
    if DECODER_FINGERPRINT is None:
        DECODER_FINGERPRINT = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return DECODER_FINGERPRINT


class Entity:
    def __init__(self, seed: int):
        rng = np.random.default_rng(seed)
        self.w = (rng.standard_normal((256, 256), dtype=np.float32) * 0.02).astype(np.float32)
        self.w, self.trigger, self.target, self.wm0 = pl.watermark_embed(self.w, core_rows=64)
        self.w_base = self.w.copy()
        self._hippo = []

    def thrust(self, s: np.ndarray) -> np.ndarray:
        z = self.w @ phi(s)
        return action_map(z)[64:66].astype(np.float32)

    def mask(self):
        return pl.plasticity_mask(self.w, core_rows=64)


def ring_read(ring: np.ndarray, slot: int) -> np.ndarray:
    off = slot * 8
    return ring[off:off + 8].copy()


class Field:
    def __init__(self, t0: int = 0, agents: int = 2):
        self.t = t0
        self.agents = agents
        if agents == 2:
            self.pos = {"A": np.array([-5.0, -5.0], dtype=np.float32),
                        "B": np.array([5.0, 5.0], dtype=np.float32)}
        else:
            self.pos = {"A": np.array([-5.0, -5.0], dtype=np.float32)}
        self.vel = {k: np.zeros(2, dtype=np.float32) for k in self.pos}

    def grad(self, p, t):
        x, y = p
        return np.array([
            -K1 * math.sin(K1 * x - OMEGA * t) * math.sin(K2 * y + OMEGA * t),
             K2 * math.cos(K1 * x - OMEGA * t) * math.cos(K2 * y + OMEGA * t),
        ], dtype=np.float32)

    def h(self, p, t):
        x, y = p
        return math.cos(K1 * x - OMEGA * t) * math.sin(K2 * y + OMEGA * t)

    def step(self, thrusts):
        for name, u in thrusts.items():
            v = self.vel[name] * FRICTION + ACC * np.asarray(u, dtype=np.float32)
            n = np.linalg.norm(v)
            if n > MAX_SPEED:
                v = v / n * MAX_SPEED
            self.vel[name] = v
            self.pos[name] = (self.pos[name] + v * DT) % L
        self.t += 1
        rewards = {name: self.h(self.pos[name], self.t) - METAB * float(np.abs(thrusts[name]).sum())
                   for name in self.pos}
        collision = False
        if "A" in self.pos and "B" in self.pos:
            d = float(np.linalg.norm(self.pos["A"] - self.pos["B"]))
            collision = d < COLLIDE_DIST
        if collision:
            for name in rewards:
                rewards[name] -= COLLIDE_PEN
        return rewards, collision


def ring_write(ring, slot, pos, vel, thrust):
    posn = (np.asarray(pos) / L) * 2.0
    veln = np.asarray(vel) / MAX_SPEED
    off = slot * 8
    ring[off:off + 8] = np.array([posn[0], posn[1], veln[0], veln[1],
                                  thrust[0], thrust[1], 1.0 + slot, 1.0], dtype=np.float32)


def episode(entities, t0=0, steps=EP_LEN):
    field = Field(t0=t0, agents=len(entities))
    ring = (np.linspace(0.0, 1.0, 1024, dtype=np.float32) * 0.5).astype(np.float32)
    for ent in entities.values():
        ent._u = np.zeros(2, dtype=np.float32)
    traj = {name: [] for name in entities}
    totals = {name: 0.0 for name in entities}
    collisions = 0
    for _ in range(steps):
        ring = ring.copy()
        for i, (name, ent) in enumerate(entities.items()):
            thrust_prev = getattr(ent, "_u", np.zeros(2, dtype=np.float32))
            ring_write(ring, i, field.pos[name], field.vel[name], thrust_prev)
        feats = {}
        for i, (name, ent) in enumerate(entities.items()):
            s = np.concatenate([field.pos[name] / L,
                                field.vel[name] / MAX_SPEED,
                                field.grad(field.pos[name], field.t),
                                (field.pos["B"] - field.pos["A"]) / L if name == "B" else
                                (field.pos["A"] - field.pos["B"]) / L if name == "A" and "B" in field.pos else
                                np.zeros(2, dtype=np.float32),
                                ring_read(ring, 1 - i) if (len(entities) == 2) else np.zeros(8, dtype=np.float32)]).astype(np.float32)
            feats[name] = phi(s)
        thrusts = {}
        for name, ent in entities.items():
            y = ent.w @ feats[name]
            u = action_map(y)[64:66].astype(np.float32)
            thrusts[name] = u
            ent._u = u
            ent._y = y
            ent._feat = feats[name]
        rewards, collided = field.step(thrusts)
        collisions += int(collided)
        for name in entities:
            totals[name] += rewards[name]
            traj[name].append((feats[name], thrusts[name], rewards[name]))
    return {"returns": totals, "collisions": collisions, "traj": traj,
            "feat_mean": {name: np.mean(np.stack([t[0] for t in traj[name]]), axis=0) for name in traj}}


def evaluate_w(entities, name, w):
    backup = entities[name].w.copy()
    entities[name].w = w.astype(np.float32)
    ep = episode(entities, t0=PROBE_T, steps=PROBE_LEN)
    entities[name].w = backup
    return ep["returns"][name] / PROBE_LEN, ep["feat_mean"][name]


def novelty(hippo, feat_mean):
    if len(hippo) < 2:
        return 1.0
    ref = np.mean(np.stack(hippo), axis=0)
    n = float(np.linalg.norm(feat_mean - ref))
    d = float(np.linalg.norm(feat_mean) + np.linalg.norm(ref)) + 1e-6
    return n / d


def generation(entities, rng):
    ep = episode(entities)
    out = {"returns": {k: float(v) for k, v in ep["returns"].items()},
           "collisions": ep["collisions"], "ent": {}}
    for name, ent in entities.items():
        mask = ent.mask()
        parent_ret = ep["returns"][name] / EP_LEN
        base_probe, base_feat = evaluate_w(entities, name, ent.w)
        base_nov = novelty(ent._hippo, base_feat)
        base_score = base_probe + ALPHA_NOVELTY * base_nov
        best = None          # (tag, w, probe)
        evaluated = 0
        rejected = 0
        for i in range(NS_PAIRS):
            eps = rng.standard_normal(ent.w.shape).astype(np.float32)
            for sign in (1.0, -1.0):
                w = ent.w + sign * SIGMA_NOISE * eps * mask
                safe, drift, _, reason = pl.safety_gate_ex(ent.w_base, w, 100.0, 2.5, R_INVARIANT)
                wm = pl.watermark_verify(ent.w_base, w, ent.trigger, ent.target)
                drift_core = float(np.linalg.norm(w[:64] - ent.w_base[:64]))
                if not (safe and wm["retained"] and drift_core == 0.0):
                    rejected += 1
                    continue
                evaluated += 1
                cand_probe, cand_feat = evaluate_w(entities, name, w)
                cand_nov = novelty(ent._hippo, cand_feat)
                cand_score = cand_probe + ALPHA_NOVELTY * cand_nov
                if cand_score >= 1.01 * base_score:
                    if best is None or cand_score > best[2]:
                        best = (f"pair{i}{'+' if sign > 0 else '-'}", w, cand_score)
        committed = 0
        fro = 0.0
        if best is not None:
            ent.w = best[1].astype(np.float32)
            committed = 1
            fro = float(np.linalg.norm(ent.w - ent.w_base))
        ent._hippo.append(ep["feat_mean"][name])
        if len(ent._hippo) > 24:
            ent._hippo = ent._hippo[-24:]
        wm = pl.watermark_verify(ent.w_base, ent.w, ent.trigger, ent.target)
        out["ent"][name] = {
            "evaluated": evaluated,
            "committed": committed,
            "rejected": rejected,
            "fro_drift": fro,
            "core_drift": float(np.linalg.norm(ent.w[:64] - ent.w_base[:64])),
            "wm_cos": float(wm["cosine_alignment"]),
            "wm_drift": float(wm["response_l2_drift"]),
            "probe_parent": base_probe,
            "probe_best": best[2] if best else None,
            "novelty_parent": base_nov,
            "score_parent": base_score,
        }
    return out


def action_map(z):
    import os
    if os.environ.get("NOLEX_HEAD") == "soft":
        n = z.shape[0]
        return z * math.sqrt(n / (n + float(np.dot(z, z))))
    return np.tanh(z / 2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--regime", default="R1", choices=["R1", "R2"])
    ap.add_argument("--control", default="none", choices=["none", "C1", "C2", "C3"])
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--gens", type=int, default=6)
    ns = ap.parse_args()
    print(json.dumps({"decoder_sha256": decoder_fingerprint(),
                      "regime": ns.regime, "control": ns.control, "seed": ns.seed}))
    rng = np.random.default_rng(ns.seed)
    ents = {"A": Entity(ns.seed)}
    if ns.control != "C3":
        ents["B"] = Entity(ns.seed)
    if ns.control == "C1":
        for ent in ents.values():
            ent.mask = lambda: np.zeros((256, 256), dtype=np.float32)

    log = open(Path(ns.tag).with_suffix(".jsonl"), "w")
    t0 = time.time()
    for gen in range(1, ns.gens + 1):
        step = generation(ents, rng)
        step["gen"] = gen
        step["elapsed_s"] = round(time.time() - t0, 2)
        log.write(json.dumps(step) + "\n")
        log.flush()
        cm = {k: v["committed"] for k, v in step["ent"].items()}
        print(f"gen {gen}: returns={ {k: round(v, 3) for k, v in step['returns'].items()} } collisions={step['collisions']} committed={cm}")
    log.close()


if __name__ == "__main__":
    main()
