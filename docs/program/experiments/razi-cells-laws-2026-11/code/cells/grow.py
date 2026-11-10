#!/usr/bin/env python3
"""GR1 growth pilot: two engines in a tiny network. Preregistered in exp/TESTS.md ("GR1 growth pilot").

Engine 1 (signal-led): gradient training with Adam.
Engine 2 (blind): growth by neuron splitting, kept only if a gate says the grown lineage is better.
Compute law: one training step costs one unit per parameter. Every arm gets the same budget.

Details fixed before any run, beyond the preregistration text:
- Train and gate labels carry noise 0.1. Test loss is measured against the clean teacher, so its floor is 0.
- Reading the gradient signal (one pass over the training rows) and each gate reading are charged
  rows/64 steps at the network's size. `nogate` reads the signal but pays for no gate and no second lineage.
- A trial starts only if the budget left covers it. Otherwise the network trains alone to the end.
- A split copies the parent's Adam state to the child. Outgoing weight is halved for both.
- All arms of one seed share the data, and the first neurons of every birth come from the same draws.

Usage: grow.py run OUT.json [--seeds 10] [--par 8]   |   grow.py report OUT.json   |   grow.py selftest
"""
from __future__ import annotations

import json
import os
import statistics
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
import numpy as np  # noqa: E402

D_IN, BATCH, LR = 8, 64, 0.005
N_TRAIN, N_GATE, N_TEST, NOISE = 2000, 1000, 5000, 0.1
TRIAL, MARGIN, BIRTH = 300, 0.02, 2
TEACHERS = (4, 16, 64)
ARMS = ("gate-signal", "gate-random", "nogate", "fixed2", "fixed128", "fixed-same")


def n_params(w: int) -> int:
    return w * (D_IN + 1) + w + 1


BUDGET = n_params(64) * 8000  # 5,128,000


def make_data(teacher: int, seed: int) -> dict:
    r = np.random.default_rng(1000 * teacher + seed)
    W, b, v = r.normal(0, 1, (teacher, D_IN)), r.normal(0, 0.5, teacher), r.normal(0, 1, teacher) / np.sqrt(teacher)
    out = {}
    for name, n, noise in (("train", N_TRAIN, NOISE), ("gate", N_GATE, NOISE), ("test", N_TEST, 0.0)):
        X = r.normal(0, 1, (n, D_IN))
        out[name] = (X, np.tanh(X @ W.T + b) @ v + noise * r.normal(0, 1, n))
    return out


def birth(width: int, seed: int) -> dict:
    r = np.random.default_rng(77 + seed)
    W = r.normal(0, 1 / np.sqrt(D_IN), (1024, D_IN))[:width]  # same draws for the first neurons at any width
    v = r.normal(0, 1, 1024)[:width] / np.sqrt(width)
    p = {"W": W.copy(), "b": np.zeros(width), "v": v.copy(), "c": np.zeros(1)}
    return {"p": p, "m": {k: np.zeros_like(x) for k, x in p.items()},
            "s": {k: np.zeros_like(x) for k, x in p.items()}, "t": 0}


def clone(net: dict) -> dict:
    return {"p": {k: x.copy() for k, x in net["p"].items()}, "m": {k: x.copy() for k, x in net["m"].items()},
            "s": {k: x.copy() for k, x in net["s"].items()}, "t": net["t"]}


def width(net: dict) -> int:
    return len(net["p"]["b"])


def grads(net: dict, X: np.ndarray, y: np.ndarray) -> tuple[dict, float]:
    p = net["p"]
    h = np.tanh(X @ p["W"].T + p["b"])
    err = h @ p["v"] + p["c"][0] - y
    dy = 2 * err / len(y)
    dz = (dy[:, None] * p["v"][None, :]) * (1 - h * h)
    return {"W": dz.T @ X, "b": dz.sum(0), "v": h.T @ dy, "c": np.array([dy.sum()])}, float((err * err).mean())


def loss(net: dict, data: tuple) -> float:
    p = net["p"]
    X, y = data
    e = np.tanh(X @ p["W"].T + p["b"]) @ p["v"] + p["c"][0] - y
    return float((e * e).mean())


def step(net: dict, X: np.ndarray, y: np.ndarray) -> None:
    g, _ = grads(net, X, y)
    net["t"] += 1
    t = net["t"]
    for k in net["p"]:
        net["m"][k] = 0.9 * net["m"][k] + 0.1 * g[k]
        net["s"][k] = 0.999 * net["s"][k] + 0.001 * g[k] * g[k]
        net["p"][k] -= LR * (net["m"][k] / (1 - 0.9 ** t)) / (np.sqrt(net["s"][k] / (1 - 0.999 ** t)) + 1e-8)


def train(net: dict, data: tuple, batches: np.ndarray) -> None:
    X, y = data
    for idx in batches:
        step(net, X[idx], y[idx])


def split(net: dict, who: np.ndarray, r: np.random.Generator) -> dict:
    """Each chosen neuron divides. The child copies the parent with small noise. Both keep half the outgoing weight."""
    new = clone(net)
    for d, scale in ((new["p"], 0.5), (new["m"], 0.5), (new["s"], 0.25)):
        d["v"][who] *= scale
    for d in (new["p"], new["m"], new["s"]):
        for k in ("W", "b", "v"):
            d[k] = np.concatenate([d[k], d[k][who]], axis=0)
    n = len(who)
    new["p"]["W"][-n:] += r.normal(0, 0.01, (n, D_IN))
    new["p"]["b"][-n:] += r.normal(0, 0.01, n)
    return new


def run_arm(arm: str, teacher: int, seed: int, data: dict, same_width: int = 0) -> dict:
    r = np.random.default_rng(5000 + seed)   # batches: the same stream for every arm of a seed
    rs = np.random.default_rng(9000 + seed)  # split noise and random choice
    spent, trace, trials, wins = 0.0, [], 0, 0

    def draw(n: int) -> np.ndarray:
        return r.integers(0, N_TRAIN, (n, BATCH))

    def alone(net: dict, steps: int) -> float:
        steps = min(steps, int((BUDGET - spent) // n_params(width(net))))
        if steps > 0:
            train(net, data["train"], draw(steps))
        return steps * n_params(width(net))

    if arm.startswith("fixed"):
        w = {"fixed2": 2, "fixed128": 128, "fixed-same": same_width}[arm]
        net = birth(w, seed)
        spent += alone(net, 10 ** 9)
    else:
        net, rejects = birth(BIRTH, seed), 0
        while True:
            w = width(net)
            k = max(1, w // 2)
            pa, pb = n_params(w), n_params(w + k)
            gated = arm != "nogate"
            need = N_TRAIN / BATCH * pa * (arm != "gate-random") + TRIAL * (pb + pa * gated) + N_GATE / BATCH * (pa + pb) * gated
            if spent + need > BUDGET:
                spent += alone(net, 10 ** 9)
                break
            if arm == "gate-random":
                who = rs.choice(w, k, replace=False)
            else:
                g, _ = grads(net, *data["train"])
                who = np.argsort(-(np.square(g["W"]).sum(1) + np.square(g["b"])))[:k]
            grown = split(net, np.sort(who), rs)
            batches = draw(TRIAL)
            train(grown, data["train"], batches)
            trials += 1
            if gated:
                train(net, data["train"], batches)
                keep = loss(grown, data["gate"]) < (1 - MARGIN) * loss(net, data["gate"])
            else:
                keep = True
            spent += need
            if keep:
                net, rejects, wins = grown, 0, wins + 1
            else:
                rejects += 1
                spent += alone(net, TRIAL * 2 ** (rejects - 1))
            trace.append([round(spent), width(net), int(keep)])
    return {"arm": arm, "teacher": teacher, "seed": seed, "width": width(net), "test": loss(net, data["test"]),
            "gate": loss(net, data["gate"]), "spent": round(spent), "trials": trials, "wins": wins, "trace": trace}


def job(ts: tuple[int, int]) -> list[dict]:
    teacher, seed = ts
    data = make_data(teacher, seed)
    rows = [run_arm(a, teacher, seed, data) for a in ARMS[:-1]]
    rows.append(run_arm("fixed-same", teacher, seed, data, same_width=rows[0]["width"]))
    return rows


def report(rows: list[dict]) -> None:
    med = statistics.median
    by = {}
    for x in rows:
        by.setdefault((x["teacher"], x["arm"]), {})[x["seed"]] = x

    def ratio(t: int, a: str, b: str) -> float:
        return med(by[t, a][s]["test"] / by[t, b][s]["test"] for s in by[t, a])
    print(f"budget {BUDGET} units per arm, seeds {len(by[TEACHERS[0], ARMS[0]])}")
    print("teacher | arm          | median test loss | median width | width min-max | trials | wins")
    for t in TEACHERS:
        for a in ARMS:
            c = list(by[t, a].values())
            ws = [x["width"] for x in c]
            print(f"{t:7d} | {a:12s} | {med(x['test'] for x in c):16.5f} | {med(ws):12g} | {min(ws):5d}-{max(ws):<5d} | "
                  f"{med(x['trials'] for x in c):6g} | {med(x['wins'] for x in c):4g}")
    print("\npaired median ratios of test loss (below 1 means the first arm is better)")
    pairs = (("gate-signal", "fixed-same"), ("gate-signal", "gate-random"), ("gate-signal", "nogate"), ("gate-signal", "fixed128"),
             ("gate-signal", "fixed2"))
    for t in TEACHERS:
        print(f"teacher {t}: " + ", ".join(f"{a}/{b} {ratio(t, a, b):.3f}" for a, b in pairs))
    m = {(t, a): med(x["test"] for x in by[t, a].values()) for t in TEACHERS for a in ARMS}
    w = [med(x["width"] for x in by[t, "gate-signal"].values()) for t in TEACHERS]
    print("\nguesses, judged as written")
    print(f"GR-a width rises with need {w}: {w[0] < w[1] < w[2]}")
    n = sum(m[t, "nogate"] > m[t, "gate-signal"] for t in TEACHERS)
    print(f"GR-b nogate worse than gate-signal on {n} of 3 needs: {n >= 2}")
    rc = [ratio(t, "gate-signal", "fixed-same") for t in TEACHERS]
    print(f"GR-c gate-signal never beats fixed-same by more than 10% {[round(x, 3) for x in rc]}: {all(x >= 0.9 for x in rc)}")
    rd = [ratio(t, "gate-signal", "gate-random") for t in TEACHERS]
    print(f"GR-d signal and random within 10% on at least 2 needs {[round(x, 3) for x in rd]}: {sum(0.9 <= x <= 1.1 for x in rd) >= 2}")
    print(f"GR-e fixed128 beats gate-signal on teacher 64 ({m[64, 'fixed128']:.5f} vs {m[64, 'gate-signal']:.5f}): "
          f"{m[64, 'fixed128'] < m[64, 'gate-signal']}")


def selftest() -> None:
    global BUDGET
    data = make_data(4, 0)
    net = birth(5, 0)
    train(net, data["train"], np.random.default_rng(0).integers(0, N_TRAIN, (50, BATCH)))
    # 1. the hand-written gradient matches a numeric one
    g, _ = grads(net, *data["gate"])
    for k, i in (("W", (1, 2)), ("b", (3,)), ("v", (0,)), ("c", (0,))):
        a, b = clone(net), clone(net)
        a["p"][k][i] += 1e-6
        b["p"][k][i] -= 1e-6
        num = (loss(a, data["gate"]) - loss(b, data["gate"])) / 2e-6
        assert abs(num - g[k][i]) < 1e-6, (k, num, g[k][i])
    # 2. a split without noise leaves the function unchanged
    class Z:
        def normal(self, a, b, n):
            return np.zeros(n)
    s = split(net, np.array([0, 3]), Z())
    assert width(s) == 7 and abs(loss(s, data["gate"]) - loss(net, data["gate"])) < 1e-12
    assert n_params(64) == 641 and BUDGET == 5_128_000
    # 3. every arm stays inside the budget and is repeatable
    full, BUDGET = BUDGET, 200_000
    try:
        for a in ARMS[:-1]:
            x, y = run_arm(a, 4, 0, data), run_arm(a, 4, 0, data)
            assert x["spent"] <= BUDGET and x["test"] == y["test"] and x["width"] == y["width"], a
            assert x["spent"] > 0.98 * BUDGET or a == "fixed128", (a, x["spent"])
    finally:
        BUDGET = full
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
            rows = [x for part in pool.map(job, [(t, s) for t in TEACHERS for s in range(seeds)]) for x in part]
        with open(sys.argv[2], "w") as f:
            json.dump(rows, f)
        report(rows)
    elif cmd == "report":
        report(json.load(open(sys.argv[2])))
    else:
        raise SystemExit(__doc__)
