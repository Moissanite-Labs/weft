#!/usr/bin/env python3
"""GR2 growth pilot: asymmetric division. Preregistered in exp/TESTS.md ("GR2 growth pilot").

One change from GR1 (grow.py, imported unchanged): a new neuron is born different from its parent.
It gets fresh input weights and outgoing weight 0, so the output is unchanged at division.

Details fixed before any run, beyond the preregistration text:
- Candidates: input weights normal(0, 1/sqrt(D_IN)), bias 0. `asym-signal` draws 4*k and keeps the k with the
  largest |sum over training rows of activity * error|. `asym-random` draws the same 4*k and keeps the first k.
- New neurons start with zero Adam state.
- Trial cost, gate cost and the doubling wait are as in GR1.

Usage: grow2.py run OUT.json [--seeds 10] [--par 8]   |   grow2.py report OUT.json   |   grow2.py selftest
"""
from __future__ import annotations

import json
import statistics
import sys

import grow as G
import numpy as np

ARMS = ("asym-signal", "asym-random", "nogate-asym", "gate-signal", "fixed128", "fixed-same")
POOL = 4


def add(net: dict, Wn: np.ndarray) -> dict:
    new, n = G.clone(net), len(Wn)
    fresh = {"W": Wn, "b": np.zeros(n), "v": np.zeros(n)}
    for k in ("W", "b", "v"):
        new["p"][k] = np.concatenate([new["p"][k], fresh[k]], axis=0)
        for d in (new["m"], new["s"]):
            d[k] = np.concatenate([d[k], np.zeros_like(fresh[k])], axis=0)
    return new


def run_arm(arm: str, teacher: int, seed: int, data: dict) -> dict:
    r = np.random.default_rng(5000 + seed)   # batches: the same stream as GR1
    rs = np.random.default_rng(9000 + seed)  # candidates
    spent, trace, trials, wins = 0.0, [], 0, 0
    X, y = data["train"]

    def alone(net: dict, steps: int) -> float:
        steps = min(steps, int((G.BUDGET - spent) // G.n_params(G.width(net))))
        if steps > 0:
            G.train(net, data["train"], r.integers(0, G.N_TRAIN, (steps, G.BATCH)))
        return steps * G.n_params(G.width(net))

    net, rejects = G.birth(G.BIRTH, seed), 0
    gated, look = arm != "nogate-asym", arm != "asym-random"
    while True:
        w = G.width(net)
        k = max(1, w // 2)
        pa, pb = G.n_params(w), G.n_params(w + k)
        need = (G.N_TRAIN / G.BATCH * G.n_params(w + POOL * k) * look + G.TRIAL * (pb + pa * gated)
                + G.N_GATE / G.BATCH * (pa + pb) * gated)
        if spent + need > G.BUDGET:
            spent += alone(net, 10 ** 9)
            break
        cand = rs.normal(0, 1 / np.sqrt(G.D_IN), (POOL * k, G.D_IN))
        if look:
            p = net["p"]
            err = np.tanh(X @ p["W"].T + p["b"]) @ p["v"] + p["c"][0] - y
            cand = cand[np.sort(np.argsort(-np.abs(np.tanh(X @ cand.T).T @ err))[:k])]
        else:
            cand = cand[:k]
        grown = add(net, cand)
        batches = r.integers(0, G.N_TRAIN, (G.TRIAL, G.BATCH))
        G.train(grown, data["train"], batches)
        trials += 1
        if gated:
            G.train(net, data["train"], batches)
            keep = G.loss(grown, data["gate"]) < (1 - G.MARGIN) * G.loss(net, data["gate"])
        else:
            keep = True
        spent += need
        if keep:
            net, rejects, wins = grown, 0, wins + 1
        else:
            rejects += 1
            spent += alone(net, G.TRIAL * 2 ** (rejects - 1))
        trace.append([round(spent), G.width(net), int(keep)])
    return {"arm": arm, "teacher": teacher, "seed": seed, "width": G.width(net), "test": G.loss(net, data["test"]),
            "gate": G.loss(net, data["gate"]), "spent": round(spent), "trials": trials, "wins": wins, "trace": trace}


def job(ts: tuple[int, int]) -> list[dict]:
    teacher, seed = ts
    data = G.make_data(teacher, seed)
    rows = [run_arm(a, teacher, seed, data) for a in ARMS[:3]]
    rows += [G.run_arm(a, teacher, seed, data) for a in ("gate-signal", "fixed128")]
    rows.append(G.run_arm("fixed-same", teacher, seed, data, same_width=rows[0]["width"]))
    return rows


def report(rows: list[dict]) -> None:
    med, T = statistics.median, G.TEACHERS
    by = {}
    for x in rows:
        by.setdefault((x["teacher"], x["arm"]), {})[x["seed"]] = x

    def ratio(t: int, a: str, b: str) -> float:
        return med(by[t, a][s]["test"] / by[t, b][s]["test"] for s in by[t, a])
    print(f"budget {G.BUDGET} units per arm, seeds {len(by[T[0], ARMS[0]])}")
    print("teacher | arm          | median test loss | median width | width min-max | trials | wins")
    for t in T:
        for a in ARMS:
            c = list(by[t, a].values())
            ws = [x["width"] for x in c]
            print(f"{t:7d} | {a:12s} | {med(x['test'] for x in c):16.5f} | {med(ws):12g} | {min(ws):5d}-{max(ws):<5d} | "
                  f"{med(x['trials'] for x in c):6g} | {med(x['wins'] for x in c):4g}")
    print("\npaired median ratios of test loss (below 1 means the first arm is better)")
    others = ("gate-signal", "asym-random", "nogate-asym", "fixed-same", "fixed128")
    for t in T:
        print(f"teacher {t}: " + ", ".join(f"asym-signal/{b} {ratio(t, 'asym-signal', b):.3f}" for b in others))
    m = {(t, a): med(x["test"] for x in by[t, a].values()) for t in T for a in ARMS}
    w = [med(x["width"] for x in by[t, "asym-signal"].values()) for t in T]
    print("\nguesses, judged as written")
    print(f"GR2-a width rises with need {w}: {w[0] < w[1] < w[2]}")
    rb = [ratio(t, "asym-signal", "gate-signal") for t in (16, 64)]
    print(f"GR2-b beats copy division on teachers 16 and 64, ratio below 0.5 {[round(x, 3) for x in rb]}: {all(x < 0.5 for x in rb)}")
    print(f"GR2-c teacher 4 median width {w[0]} is 8 or less: {w[0] <= 8}")
    rd = [ratio(t, "asym-signal", "asym-random") for t in T]
    print(f"GR2-d signal and random within 10% on at least 2 needs {[round(x, 3) for x in rd]}: {sum(0.9 <= x <= 1.1 for x in rd) >= 2}")
    rc = [ratio(t, "asym-signal", "fixed-same") for t in T]
    e1, e2 = all(x >= 0.9 for x in rc), m[64, "fixed128"] < m[64, "asym-signal"]
    print(f"GR2-e never beats fixed-same by more than 10% {[round(x, 3) for x in rc]}: {e1}; fixed128 better on teacher 64 "
          f"({m[64, 'fixed128']:.5f} vs {m[64, 'asym-signal']:.5f}): {e2}; both: {e1 and e2}")
    print(f"GR2-f nogate-asym worse than asym-signal on teacher 4 ({m[4, 'nogate-asym']:.5f} vs {m[4, 'asym-signal']:.5f}): "
          f"{m[4, 'nogate-asym'] > m[4, 'asym-signal']}")


def selftest() -> None:
    data = G.make_data(4, 0)
    net = G.birth(5, 0)
    G.train(net, data["train"], np.random.default_rng(0).integers(0, G.N_TRAIN, (50, G.BATCH)))
    s = add(net, np.random.default_rng(1).normal(0, 1, (3, G.D_IN)))
    assert G.width(s) == 8 and abs(G.loss(s, data["gate"]) - G.loss(net, data["gate"])) < 1e-12  # output unchanged at birth
    G.train(s, data["train"], np.random.default_rng(0).integers(0, G.N_TRAIN, (5, G.BATCH)))
    assert np.all(np.abs(s["p"]["v"][-3:]) > 0)  # the new neurons do learn
    full, G.BUDGET = G.BUDGET, 200_000
    try:
        for a in ARMS[:3]:
            x, z = run_arm(a, 4, 0, data), run_arm(a, 4, 0, data)
            assert x["spent"] <= G.BUDGET and x["test"] == z["test"] and x["width"] == z["width"], a
            assert x["spent"] > 0.98 * G.BUDGET, (a, x["spent"])
    finally:
        G.BUDGET = full
    print("selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        selftest()
    elif cmd == "run":
        from multiprocessing import Pool
        seeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 10
        par = int(sys.argv[sys.argv.index("--par") + 1]) if "--par" in sys.argv else 8
        with Pool(par) as pool:
            rows = [x for part in pool.map(job, [(t, s) for t in G.TEACHERS for s in range(seeds)]) for x in part]
        with open(sys.argv[2], "w") as f:
            json.dump(rows, f)
        report(rows)
    elif cmd == "report":
        report(json.load(open(sys.argv[2])))
    else:
        raise SystemExit(__doc__)
