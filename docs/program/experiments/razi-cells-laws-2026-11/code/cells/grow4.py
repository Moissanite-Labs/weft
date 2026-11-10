#!/usr/bin/env python3
"""GR4: two ways to tell "satisfied" from "stuck". Preregistered in exp/TESTS.md ("GR4 two ways ...").

grow.py, grow2.py and grow3.py are imported unchanged. All arms use blind candidates (GR2 `asym-random` rules).
- `base`:  the GR2 fixed gate. The loop here must reproduce grow2's `asym-random` exactly (checked in selftest).
- `level`: the margin is MARGIN * (1 - u / U0), u = gate loss of the ungrown lineage / variance of the gate targets.
- `escal`: fixed gate, but after each refused step the next step is twice as big (at most 16 times the base step).
- `nogate`: grow3's ungated blind growth.

Details fixed before any run, beyond the preregistration text:
- u is read from the gate reading the trial already pays for, so `level` costs nothing extra.
- `escal` keeps the GR1 doubling wait after a refusal. A step that the budget cannot cover ends growth, as in GR1.
- Noisy conditions set the label noise of the train and gate rows to 0.5. Test rows are always clean.
- Regret: an arm's test loss divided by the lowest test loss among the four arms, same condition and seed.

Usage: grow4.py run OUT.json [--seeds 10] [--par 8]   |   grow4.py report OUT.json   |   grow4.py selftest
"""
from __future__ import annotations

import json
import statistics
import sys

import grow as G
import grow2 as G2
import grow3 as G3
import numpy as np

U0, ESC_MAX = 0.25, 16
ARMS = ("base", "level", "escal", "nogate")
CONDS = {  # name: (task, teacher, label noise)
    "tanh4": ("tanh", 4, 0.1), "tanh16": ("tanh", 16, 0.1), "tanh64": ("tanh", 64, 0.1),
    "sin4": ("sin", 4, 0.1), "sin16": ("sin", 16, 0.1), "sin64": ("sin", 64, 0.1),
    "noisy4": ("tanh", 4, 0.5), "noisy16": ("tanh", 16, 0.5),
}


def run_arm(arm: str, teacher: int, seed: int, data: dict) -> dict:
    r = np.random.default_rng(5000 + seed)   # batches: the same stream as GR1 and GR2
    rs = np.random.default_rng(9000 + seed)  # candidates
    spent, trials, wins, us = 0.0, 0, 0, []
    var = float(np.var(data["gate"][1]))

    def alone(net: dict, steps: int) -> float:
        steps = min(steps, int((G.BUDGET - spent) // G.n_params(G.width(net))))
        if steps > 0:
            G.train(net, data["train"], r.integers(0, G.N_TRAIN, (steps, G.BATCH)))
        return steps * G.n_params(G.width(net))

    net, rejects = G.birth(G.BIRTH, seed), 0
    while True:
        w = G.width(net)
        k = max(1, w // 2)
        if arm == "escal":
            k *= min(2 ** rejects, ESC_MAX)
        pa, pb = G.n_params(w), G.n_params(w + k)
        need = G.TRIAL * (pb + pa) + G.N_GATE / G.BATCH * (pa + pb)
        if spent + need > G.BUDGET:
            spent += alone(net, 10 ** 9)
            break
        cand = rs.normal(0, 1 / np.sqrt(G.D_IN), (G2.POOL * k, G.D_IN))[:k]
        grown = G2.add(net, cand)
        batches = r.integers(0, G.N_TRAIN, (G.TRIAL, G.BATCH))
        G.train(grown, data["train"], batches)
        trials += 1
        G.train(net, data["train"], batches)
        old = G.loss(net, data["gate"])
        u = old / var
        us.append(u)
        margin = G.MARGIN * (1 - u / U0) if arm == "level" else G.MARGIN
        keep = G.loss(grown, data["gate"]) < (1 - margin) * old
        spent += need
        if keep:
            net, rejects, wins = grown, 0, wins + 1
        else:
            rejects += 1
            spent += alone(net, G.TRIAL * 2 ** (rejects - 1))
    return {"arm": arm, "teacher": teacher, "seed": seed, "width": G.width(net), "test": G.loss(net, data["test"]),
            "spent": round(spent), "trials": trials, "wins": wins, "u_last": round(us[-1], 4) if us else None}


def job(args: tuple[str, int]) -> list[dict]:
    name, seed = args
    task, teacher, noise = CONDS[name]
    for k, x in G3.BASE.items():
        setattr(G, k, x)
    G.NOISE = noise
    data = G3.sin_data(teacher, seed) if task == "sin" else G.make_data(teacher, seed)
    rows = [run_arm(a, teacher, seed, data) for a in ARMS[:3]]
    ng = G3.nogate_blind(teacher, seed, data)
    ng["arm"] = "nogate"
    rows.append(ng)
    best = min(x["test"] for x in rows)
    for x in rows:
        x["cond"], x["regret"] = name, x["test"] / best
    return rows


def report(rows: list[dict]) -> None:
    med = statistics.median
    by = {}
    for x in rows:
        by.setdefault((x["cond"], x["arm"]), {})[x["seed"]] = x

    def m(c, a, key):
        return med(x[key] for x in by[c, a].values())

    def ratio(c, a, b):
        return med(by[c, a][i]["test"] / by[c, b][i]["test"] for i in by[c, a])
    print(f"budget {G.BUDGET} units per arm, seeds {len(by['tanh4', 'base'])}, U0 {U0}, escal max {ESC_MAX}")
    print("cond    | median width base/level/escal/nogate | median test loss base/level/escal/nogate     | "
          "level/base escal/base | median regret base/level/escal/nogate")
    for c in CONDS:
        print(f"{c:7s} | " + " ".join(f"{m(c, a, 'width'):7g}" for a in ARMS) + "      | "
              + " ".join(f"{m(c, a, 'test'):9.5f}" for a in ARMS) + "     | "
              + f"{ratio(c, 'level', 'base'):9.3f} {ratio(c, 'escal', 'base'):9.3f}  | "
              + " ".join(f"{m(c, a, 'regret'):6.2f}" for a in ARMS))
    worst = {a: max(m(c, a, "regret") for c in CONDS) for a in ARMS}
    print("worst-case median regret: " + ", ".join(f"{a} {worst[a]:.2f}" for a in ARMS))
    print("\nguesses, judged as written")
    ra = [ratio("sin64", a, "base") for a in ("level", "escal")]
    print(f"GR4-a on sin64 level and escal beat base, ratio below 0.9 {[round(x, 3) for x in ra]}: {all(x < 0.9 for x in ra)}")
    T = ("tanh4", "tanh16", "tanh64")
    rl, re = [ratio(c, "level", "base") for c in T], [ratio(c, "escal", "base") for c in T]
    nl, ne = sum(0.8 <= x <= 1.25 for x in rl), sum(0.8 <= x <= 1.25 for x in re)
    print(f"GR4-b on tanh, ratio to base inside 0.8 to 1.25: level {[round(x, 3) for x in rl]} {nl} of 3, "
          f"escal {[round(x, 3) for x in re]} {ne} of 3: {nl == 3 and ne >= 2}")
    wb, wl, we = (m("noisy4", a, "width") for a in ("base", "level", "escal"))
    print(f"GR4-c noisy4 median width base {wb:g}, level {wl:g}, escal {we:g}; level more than twice base and escal not: "
          f"{wl > 2 * wb and not we > 2 * wb}")
    print(f"GR4-d escal has the lowest worst-case regret: {all(worst['escal'] < worst[a] for a in ARMS if a != 'escal')}")
    w = [m(c, "escal", "width") for c in T]
    print(f"GR4-e escal width rises with need on tanh {w}: {w[0] < w[1] < w[2]}")


def selftest() -> None:
    data = G.make_data(4, 0)
    full, G.BUDGET = G.BUDGET, 200_000
    try:
        ref = G2.run_arm("asym-random", 4, 0, data)
        for a in ARMS[:3]:
            x, z = run_arm(a, 4, 0, data), run_arm(a, 4, 0, data)
            assert x["spent"] <= G.BUDGET and x["test"] == z["test"] and x["width"] == z["width"], a
            assert x["spent"] > 0.98 * G.BUDGET, (a, x["spent"])
            if a == "base":  # the loop here is grow2's asym-random, bit for bit
                assert x["test"] == ref["test"] and x["width"] == ref["width"] and x["trials"] == ref["trials"], (x, ref)
    finally:
        G.BUDGET = full
    assert G.NOISE == 0.1 and G.MARGIN == 0.02 and G.TRIAL == 300 and G.LR == 0.005
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
            rows = [x for part in pool.map(job, [(c, s) for c in CONDS for s in range(seeds)]) for x in part]
        with open(sys.argv[2], "w") as f:
            json.dump(rows, f)
        report(rows)
    elif cmd == "report":
        report(json.load(open(sys.argv[2])))
    else:
        raise SystemExit(__doc__)
