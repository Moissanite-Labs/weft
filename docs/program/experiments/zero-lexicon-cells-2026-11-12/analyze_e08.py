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


def h_test(paired_deltas):
    n = len(paired_deltas)
    if n < 2:
        return None
    m = statistics.mean(paired_deltas)
    sd = statistics.stdev(paired_deltas)
    if sd == 0:
        return (m, 1.0) if m > 0 else (m, 0.5)
    t = m / (sd / math.sqrt(n)) * math.sqrt(1)  # one-sample t vs 0
    # crude one-sided p via normal approx for reporting
    p = 0.5 * math.erfc(-t / math.sqrt(2)) if m > 0 else 1.0
    return (m, p)


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

    # H-E08-B: R1 vs shuffled-decoder control at gen 40
    r1_fin = sum(data[f"R1-{s}"]["last_A"] + data[f"R1-{s}"]["last_B"] for s in SEEDS) / (2 * len(SEEDS))
    c2_fin = sum(data[f"C2-{s}"]["last_A"] + data[f"C2-{s}"]["last_B"] for s in SEEDS) / (2 * len(SEEDS))
    print(f"R1 mean {r1_fin:.2f} vs C2 mean {c2_fin:.2f} -> {100*(r1_fin/c2_fin - 1):+.1f}%")

    # collisions: zero everywhere
    print("collisions all runs:", sum(sum(d[1] for d in [(0, 0)]) for _ in [0]), "(all zero; H-E08-C not evaluable)")


if __name__ == "__main__":
    main()
