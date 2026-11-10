#!/usr/bin/env python3
"""NOT preregistered. Diagnostic for GR1: replays the gate-signal trial loop of grow.py and prints what the gate saw."""
import numpy as np
import grow as G


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


ratios, cosines = [], []
for teacher in (16, 64):
    for seed in range(4):
        data = G.make_data(teacher, seed)
        r, rs = np.random.default_rng(5000 + seed), np.random.default_rng(9000 + seed)
        net, rejects = G.birth(G.BIRTH, seed), 0
        for trial in range(6):
            w = G.width(net)
            k = max(1, w // 2)
            g, _ = G.grads(net, *data["train"])
            who = np.sort(np.argsort(-(np.square(g["W"]).sum(1) + np.square(g["b"])))[:k])
            grown = G.split(net, who, rs)
            b = r.integers(0, G.N_TRAIN, (G.TRIAL, G.BATCH))
            G.train(grown, data["train"], b)
            G.train(net, data["train"], b)
            lg, ln = G.loss(grown, data["gate"]), G.loss(net, data["gate"])
            ratios.append(lg / ln)
            cosines.append(cos(grown["p"]["W"][who[0]], grown["p"]["W"][-k]))
            if lg < (1 - G.MARGIN) * ln:
                net, rejects = grown, 0
            else:
                rejects += 1
                G.train(net, data["train"], r.integers(0, G.N_TRAIN, (G.TRIAL * 2 ** (rejects - 1), G.BATCH)))
print(f"trials {len(ratios)} (teachers 16 and 64, seeds 0-3, first 6 trials each)")
print(f"gate loss grown/ungrown: min {min(ratios):.4f}, median {np.median(ratios):.4f}, max {max(ratios):.4f}; needed below {1 - G.MARGIN}")
print(f"parent-child input-weight cosine after the trial: min {min(cosines):.4f}, median {np.median(cosines):.4f}")
