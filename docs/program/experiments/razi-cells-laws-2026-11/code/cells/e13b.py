"""E13 second look, NOT preregistered: does the colony LIBRARY state at decision time predict quit vs attempt?
For each root cell: decision = first act after the accepted assay. Library state = entries written by OTHER
cells of the same colony before the decision prompt was built (time of the assay act log line).
Usage: e13b.py  (run from exp/)"""
import json, collections, sys
from pathlib import Path

RUNS = {"E11": ["e11c", "e11n"], "E12": ["e12c", "e12n", "e12ch", "e12nh"], "E13": ["e13c", "e13n", "e13ch", "e13nh"]}
ATT = {"try", "variants", "write"}


def load(d):
    cells = {}
    for c in sorted(Path(d).iterdir()):
        f = c / "log.jsonl"
        if f.exists():
            cells[c.name] = [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    return cells


def lib_events(ev):
    """(time, kind) of each LIBRARY line this cell wrote."""
    out = []
    for e in ev:
        if isinstance(e.get("act"), dict) and e["act"].get("do") == "done" and "res" not in e:  # a refused (held) done has res and writes no line
            out.append((e["t"], "DONE"))
        elif e.get("event") == "improve":
            out.append((e["t"], "WIN"))
        elif e.get("event") == "try" and not e.get("won"):
            out.append((e["t"], "LOSS"))
    return out


rows = []
for exp, pres in RUNS.items():
    for pre in pres:
        for r in range(1, 5):
            d = f"{pre}{r}"
            if not Path(d).exists():
                continue
            cells = load(d)
            libs = {n: lib_events(ev) for n, ev in cells.items()}
            for n, ev in cells.items():
                ta, dec = None, None
                for e in ev:
                    a = e.get("act")
                    if not isinstance(a, dict):
                        continue
                    if ta is None:
                        if a.get("do") == "assay" and str(e.get("res", "")).startswith("assay accepted"):
                            ta = e["t"]
                    elif a.get("do") != "assay":
                        dec = a.get("do")
                        break
                if ta is None or dec is None:
                    continue
                seen = collections.Counter(k for m, l in libs.items() if m != n for t, k in l if t < ta)
                # a DONE seen before any WIN by that same cell = "finished without improving"
                quit_seen = 0
                for m, l in libs.items():
                    if m == n:
                        continue
                    ds = [t for t, k in l if k == "DONE" and t < ta]
                    ws = [t for t, k in l if k == "WIN" and t < ta]
                    if ds and not ws:
                        quit_seen += 1
                rows.append(dict(exp=exp, arm=pre[3:], run=d, task=n, dec=("attempt" if dec in ATT else dec),
                                 done=seen["DONE"], win=seen["WIN"], loss=seen["LOSS"], quit=quit_seen))

json.dump(rows, open("results/e13b-rows.json", "w"))


def tab(rs, label):
    c = collections.Counter()
    for r in rs:
        state = "quit_seen" if r["quit"] else ("win_only" if r["win"] else ("loss_only" if r["loss"] else "empty"))
        c[(state, r["dec"])] += 1
    print(label, "n", len(rs))
    for state in ("empty", "quit_seen", "win_only", "loss_only"):
        a, dn, sh = c[(state, "attempt")], c[(state, "done")], c[(state, "sh")] + c[(state, "remember")]
        if a + dn + sh:
            print(f"   {state:10s} attempt {a:3d}  done {dn:3d}  other {sh:3d}  attempt share {a / (a + dn + sh):.3f}")


tab(rows, "ALL root cells, E11-E13")
for exp in RUNS:
    tab([r for r in rows if r["exp"] == exp], exp)
for arm in ("c", "n", "ch", "nh"):
    tab([r for r in rows if r["arm"] == arm], f"arm {arm}")
tab([r for r in rows if r["arm"] in ("n", "nh")], "novar arms (n, nh) only")
tab([r for r in rows if r["arm"] in ("c", "ch")], "ctrl arms (c, ch) only")
for task in ("compress", "fibmod", "csvsum", "maze"):
    tab([r for r in rows if r["task"] == task], f"task {task}")
    tab([r for r in rows if r["task"] == task and r["arm"] in ("n", "nh")], f"task {task}, novar arms")
