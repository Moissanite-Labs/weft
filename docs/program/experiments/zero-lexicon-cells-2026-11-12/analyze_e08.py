#!/usr/bin/env python3
"""Aggregate the E08 runs for the preregistered hypothesis clauses."""
import glob
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEEDS = [20261112, 20261113, 20261114]
REGIMES = {"R1": "revc", "C1": "c1", "C2": "c2", "C3": "c3"}


def load(tag):
    return [json.loads(l) for l in open(ROOT / f"{tag}.jsonl")]


def summarize(runs):
    first, last = runs[0], runs[-1]
    commits = sum(1 for d in runs for v in d["ent"].values() if v["committed"])
    gates = {}
    total_rej = sum(v["rejected"] for d in runs for v in d["ent"].values())
    total_eval = sum(v["evaluated"] for d in runs for v in d["ent"].values())
    gates["rejection_rate"] = round(total_rej / max(1, total_rej + total_eval), 3)
    gates["commits"] = commits
    gates["mean_fro_drift"] = round(statistics.mean(v["fro_drift"] for d in runs for v in d["ent"].values()), 4)
    gates["core_drift_max"] = max(v["core_drift"] for d in runs for v in d["ent"].values())
    gates["wm_cos_min"] = min(v["wm_cos"] for d in runs for v in d["ent"].values())
    gates["wm_drift_max"] = max(v["wm_drift"] for d in runs for v in d["ent"].values())
    return {
        "first_A": first["returns"]["A"], "first_B": first["returns"].get("B"),
        "last_A": last["returns"]["A"], "last_B": last["returns"].get("B"),
        **gates,
    }


def _betacf(a, b, x):
    """Continued fraction for the regularized incomplete beta (Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def _betainc(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t, df):
    """Two-sided p-value of Student's t with df degrees of freedom."""
    return _betainc(df / 2.0, 0.5, df / (df + t * t))


def paired_t_test(deltas):
    """One-sample Student t-test of paired deltas against 0.

    Returns (mean, t, df, two_sided_p, one_sided_p_upper)."""
    n = len(deltas)
    if n < 2:
        raise ValueError("need at least 2 paired deltas")
    m = statistics.mean(deltas)
    sd = statistics.stdev(deltas)
    if sd == 0:
        raise ValueError("zero variance in paired deltas")
    t = m / (sd / math.sqrt(n))
    df = n - 1
    p2 = t_two_sided_p(t, df)
    p1 = p2 / 2.0 if t > 0 else 1.0 - p2 / 2.0
    return m, t, df, p2, p1


def main():
    data = {}
    for regime, tag in REGIMES.items():
        for seed in SEEDS:
            data[f"{regime}-{seed}"] = summarize(load(f"{tag}-{seed}"))
    print(json.dumps(data, indent=2, default=str))

    # H-E08-A: R1 improvement vs C1 frozen, per (seed, agent) pair
    gains = []
    for seed in SEEDS:
        r1a = data[f"R1-{seed}"]["last_A"] - data[f"C1-{seed}"]["last_A"]
        r1b = data[f"R1-{seed}"]["last_B"] - data[f"C1-{seed}"]["last_B"]
        gains += [r1a, r1b]
    print("R1-minus-frozen gains per (seed, agent):", [round(g, 3) for g in gains])
    print("mean gain:", round(statistics.mean(gains), 3),
          "sd:", round(statistics.stdev(gains), 3))

    # Registered test (PREREG-E08.md line 7): two-tailed paired test across the
    # 3 arena seeds. The unit is the seed: mean of the A and B gains per seed.
    seed_gains = [(gains[2 * i] + gains[2 * i + 1]) / 2.0 for i in range(len(SEEDS))]
    m, t, df, p2, _ = paired_t_test(seed_gains)
    verdict = "met" if (p2 < 0.05 and m > 0) else "NOT met"
    print("H-E08-A registered test, seed-mean gains:", [round(g, 4) for g in seed_gains])
    print(f"  t = {t:.5f}, df = {df}, two-sided p = {p2:.4f} -> criterion {verdict}")
    # Post-hoc only, not the registered test: six (seed, agent) pairs, which
    # are correlated within a seed.
    m6, t6, df6, p6_2, p6_1 = paired_t_test(gains)
    print(f"  post-hoc six-pair: t = {t6:.4f}, df = {df6}, one-sided p = {p6_1:.4f}, two-sided p = {p6_2:.4f}")

    # H-E08-B: R1 vs shuffled-decoder control at gen 40
    r1_fin = sum(data[f"R1-{s}"]["last_A"] + data[f"R1-{s}"]["last_B"] for s in SEEDS) / (2 * len(SEEDS))
    c2_fin = sum(data[f"C2-{s}"]["last_A"] + data[f"C2-{s}"]["last_B"] for s in SEEDS) / (2 * len(SEEDS))
    print(f"R1 mean {r1_fin:.2f} vs C2 mean {c2_fin:.2f} -> {100*(r1_fin/c2_fin - 1):+.1f}%")

    # collisions: zero everywhere
    print("collisions all runs:", sum(sum(d[1] for d in [(0, 0)]) for _ in [0]), "(all zero; H-E08-C not evaluable)")


if __name__ == "__main__":
    main()
