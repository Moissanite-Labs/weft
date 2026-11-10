#!/usr/bin/env python3
"""GR3: robustness of GR2. Preregistered in exp/TESTS.md ("GR3 robustness of GR2").

Moves one hand-picked knob at a time (gate margin, trial length, learning rate) and adds a second task (sine teacher).
grow.py and grow2.py are imported unchanged. Knobs are set on the grow module inside each worker.

Details fixed before any run, beyond the preregistration text:
- `sin` task: y = sum_j v_j * sin(W_j.x + b_j), same draws, noise and row counts as the tanh task.
- `nogate-asym` here uses blind candidates too (the first k), so the only difference from `asym-random` is the gate.

Usage: grow3.py run OUT.json [--seeds 10] [--par 8]   |   grow3.py report OUT.json   |   grow3.py selftest
"""
from __future__ import annotations

import json
import statistics
import sys

import grow as G
import grow2 as G2
import numpy as np

SETTINGS = {
    "margin0.005": {"MARGIN": 0.005}, "margin0.08": {"MARGIN": 0.08},
    "trial100": {"TRIAL": 100}, "trial1000": {"TRIAL": 1000},
    "lr0.002": {"LR": 0.002}, "lr0.02": {"LR": 0.02},
    "sin": {},
}
BASE = {"MARGIN": 0.02, "TRIAL": 300, "LR": 0.005}
ARMS = ("asym-random", "nogate-asym", "fixed-same")


def sin_data(teacher: int, seed: int) -> dict:
    r = np.random.default_rng(1000 * teacher + seed)
    W, b, v = r.normal(0, 1, (teacher, G.D_IN)), r.normal(0, 0.5, teacher), r.normal(0, 1, teacher) / np.sqrt(teacher)
    out = {}
    for name, n, noise in (("train", G.N_TRAIN, G.NOISE), ("gate", G.N_GATE, G.NOISE), ("test", G.N_TEST, 0.0)):
        X = r.normal(0, 1, (n, G.D_IN))
        out[name] = (X, np.sin(X @ W.T + b) @ v + noise * r.normal(0, 1, n))
    return out


def nogate_blind(teacher: int, seed: int, data: dict) -> dict:
    """Ungated growth with blind candidates: grow2's asym-random loop with the gate always saying yes."""
    r, rs = np.random.default_rng(5000 + seed), np.random.default_rng(9000 + seed)
    net, spent, trials = G.birth(G.BIRTH, seed), 0.0, 0
    while True:
        w = G.width(net)
        k = max(1, w // 2)
        need = G.TRIAL * G.n_params(w + k)
        if spent + need > G.BUDGET:
            steps = int((G.BUDGET - spent) // G.n_params(w))
            if steps > 0:
                G.train(net, data["train"], r.integers(0, G.N_TRAIN, (steps, G.BATCH)))
            spent += steps * G.n_params(w)
            break
        net = G2.add(net, rs.normal(0, 1 / np.sqrt(G.D_IN), (G2.POOL * k, G.D_IN))[:k])
        G.train(net, data["train"], r.integers(0, G.N_TRAIN, (G.TRIAL, G.BATCH)))
        spent += need
        trials += 1
    return {"arm": "nogate-asym", "teacher": teacher, "seed": seed, "width": G.width(net),
            "test": G.loss(net, data["test"]), "spent": round(spent), "trials": trials, "wins": trials}


def job(args: tuple[str, int, int]) -> list[dict]:
    name, teacher, seed = args
    for k, x in {**BASE, **SETTINGS[name]}.items():
        setattr(G, k, x)
    data = sin_data(teacher, seed) if name == "sin" else G.make_data(teacher, seed)
    a = G2.run_arm("asym-random", teacher, seed, data)
    rows = [a, nogate_blind(teacher, seed, data), G.run_arm("fixed-same", teacher, seed, data, same_width=a["width"])]
    for x in rows:
        x.pop("trace", None)
        x["setting"] = name
    return rows


def report(rows: list[dict]) -> None:
    med, T = statistics.median, G.TEACHERS
    by = {}
    for x in rows:
        by.setdefault((x["setting"], x["teacher"], x["arm"]), {})[x["seed"]] = x

    def m(s, t, a, key="test"):
        return med(x[key] for x in by[s, t, a].values())

    def ratio(s, t, a, b):
        return med(by[s, t, a][i]["test"] / by[s, t, b][i]["test"] for i in by[s, t, a])
    print(f"budget {G.BUDGET} units per arm, seeds {len(by['sin', T[0], ARMS[0]])}")
    print("setting     | gated width at need 4/16/64 | gated/ungated loss 4/16/64 | grown/born-same loss 4/16/64 | ungated width")
    res = {}
    for s in SETTINGS:
        w = [m(s, t, "asym-random", "width") for t in T]
        ru = [ratio(s, t, "asym-random", "nogate-asym") for t in T]
        rf = [ratio(s, t, "asym-random", "fixed-same") for t in T]
        res[s] = (w, ru, rf, m(s, 4, "nogate-asym") > m(s, 4, "asym-random"))
        print(f"{s:11s} | {w[0]:7g} {w[1]:7g} {w[2]:7g}     | {ru[0]:7.3f} {ru[1]:7.3f} {ru[2]:7.3f}    | "
              f"{rf[0]:7.3f} {rf[1]:7.3f} {rf[2]:7.3f}      | {m(s, 4, 'nogate-asym', 'width'):g}")
    six = [s for s in SETTINGS if s != "sin"]
    print("\nguesses, judged as written")
    n = sum(res[s][0][0] < res[s][0][1] < res[s][0][2] for s in six)
    print(f"GR3-a width rises with need in {n} of 6 settings: {n >= 5}")
    n = sum(res[s][0][0] <= 8 for s in six)
    print(f"GR3-b teacher 4 width 8 or less in {n} of 6 settings {[s for s in six if res[s][0][0] > 8]} broke it: {n >= 4}")
    n = sum(res[s][3] for s in six)
    print(f"GR3-c ungated worse than gated on teacher 4 in {n} of 6 settings: {n == 6}")
    w = res["sin"][0]
    print(f"GR3-d sin task: width rises {w}: {w[0] < w[1] < w[2]}; ungated worse on need 4: {res['sin'][3]}; "
          f"both: {w[0] < w[1] < w[2] and res['sin'][3]}")
    n = sum(res[s][2][1] < 0.9 for s in six)
    print(f"GR3-e grown beats born-same by more than 10% on teacher 16 in {n} of 6 settings: {n >= 3}")


def selftest() -> None:
    full, G.BUDGET = G.BUDGET, 150_000
    try:
        for name in ("margin0.08", "sin"):
            x, y = job((name, 4, 0)), job((name, 4, 0))
            assert [r["test"] for r in x] == [r["test"] for r in y], name
            assert all(r["spent"] <= G.BUDGET and r["spent"] > 0.97 * G.BUDGET for r in x), [(r["arm"], r["spent"]) for r in x]
        assert G.MARGIN == 0.02 and G.TRIAL == 300 and G.LR == 0.005  # sin leaves the knobs at GR2 values
        job(("lr0.02", 4, 0))
        assert G.LR == 0.02 and G.MARGIN == 0.02
    finally:
        G.BUDGET = full
        for k, x in BASE.items():
            setattr(G, k, x)
    print("selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        selftest()
    elif cmd == "run":
        from multiprocessing import Pool
        seeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 10
        par = int(sys.argv[sys.argv.index("--par") + 1]) if "--par" in sys.argv else 8
        with Pool(par, maxtasksperchild=1) as pool:
            jobs = [(s, t, i) for s in SETTINGS for t in G.TEACHERS for i in range(seeds)]
            rows = [x for part in pool.map(job, jobs, chunksize=1) for x in part]
        with open(sys.argv[2], "w") as f:
            json.dump(rows, f)
        report(rows)
    elif cmd == "report":
        report(json.load(open(sys.argv[2])))
    else:
        raise SystemExit(__doc__)
