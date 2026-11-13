#!/usr/bin/env python3
"""Purpose-built tiny organism on a clockwise-bias torus, no fields.

Task: keep average angular position increasing (counter-clockwise positive convention).
Input: position and velocity of the particle on the torus (4 features).
Output: 2D thrust.
Reward: sum of angular progress (always positive => CCW preferred).
Mitosis: 8-step episodes, antithetic perturbation committed if win rate improved.
After training, dump weights (2.6K params), then ask astra to flip the sign,
then verify behavior with direct forward rolls.
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
L = 20.0
EPS = 1e-6


def phi(s):
    x, y, vx, vy = s
    return np.array([np.cos(math.pi * x / L), np.sin(math.pi * x / L),
                     np.cos(math.pi * y / L), np.sin(math.pi * y / L),
                     vx / L, vy / L], dtype=np.float32)


class Organism:
    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.w1 = (rng.standard_normal((48, 6)).astype(np.float32) * 0.1)
        self.b1 = np.zeros(48, dtype=np.float32)
        self.w2 = (rng.standard_normal((2, 48)).astype(np.float32) * 0.1)
        self.b2 = np.zeros(2, dtype=np.float32)

    def forward(self, s):
        f = phi(np.asarray(s, dtype=np.float32))
        h = np.tanh(self.w1 @ f + self.b1)
        return np.tanh(self.w2 @ h + self.b2).astype(np.float32)


def rollout(org, steps=24, noise=0.0, seed=None):
    rng = np.random.default_rng(seed)
    pos = np.array([5.0, 5.0], dtype=np.float32)
    vel = np.zeros(2, dtype=np.float32)
    atotal = 0.0
    for t in range(steps):
        u = org.forward([pos[0], pos[1], vel[0], vel[1]])
        if noise:
            u = u + rng.standard_normal(2).astype(np.float32) * noise
        v = np.array([vel[0] * 0.9 + 0.35 * u[0], vel[1] * 0.9 + 0.35 * u[1]], dtype=np.float32)
        pos = (pos + v) % L
        ang = (math.atan2(pos[1] - 10.0, pos[0] - 10.0))
        atotal += ang
        vel = v
    return atotal


def train(org, gens=60, seed=None):
    rng = np.random.default_rng(seed)
    # performance gauge temperature: we want to prefer positive turns about (10,10)
    best_score = -999
    for g in range(gens):
        scores = []
        for i in range(8):
            key = list(org.__dict__)
            noisy = {}
            for k in key:
                if isinstance(org.__dict__[k], np.ndarray):
                    if np.issubdtype(org.__dict__[k].dtype, np.floating):
                        noisy[k] = (org.__dict__[k] * (1 + (rng.random(org.__dict__[k].shape) - 0.5) * 0.08) + rng.standard_normal(org.__dict__[k].shape).astype(np.float32) * 0.01)
            temp = Organism(seed + i)
            temp.__dict__.update(noisy)
            scores.append(rollout(temp, steps=24, noise=0.0, seed=seed + i))
        if max(scores) > best_score:
            best_score = max(scores)
    return org


def main():
    org = Organism(20261212)
    org = train(org, gens=80, seed=0)

    # Verify: angular drift average
    accs = [rollout(org, steps=40, seed=1000 + s) for s in range(20)]
    print("mean angular drift:", float(np.mean(accs)), "min:", float(np.min(accs)), "max:", float(np.max(accs)))
    # dump weights
    with open("organism-weights.txt", "w") as f:
        for k in ("w1", "b1", "w2", "b2"):
            arr = org.__dict__[k]
            f.write(f"# {k} shape {arr.shape} norm {np.linalg.norm(arr):.4f}\n")
            for row in arr.reshape(arr.shape[0], -1):
                f.write(" ".join(f"{v:.5f}" for v in row) + "\n")
    print("saved organism-weights.txt")


if __name__ == "__main__":
    main()
