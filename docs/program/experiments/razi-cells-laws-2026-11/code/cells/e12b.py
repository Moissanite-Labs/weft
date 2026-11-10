#!/usr/bin/env python3
"""E12 second analysis (NOT preregistered). Finds cells whose benchmark inputs changed after the assay was
registered, and reruns the E12 comparisons without them. Usage: e12b.py [prefix, default e12]"""
import json, os, sys, glob, random, statistics as st
E = os.path.expanduser("~/Work/razi-cells/exp")
P = sys.argv[1] if len(sys.argv) > 1 else "e12"
ARMS = {"c": P + "c", "n": P + "n", "ch": P + "ch", "nh": P + "nh"} if P == "e12" else {"c": P + "c", "n": P + "n"}
TASKS = ["compress", "fibmod", "csvsum", "maze"]
SKIP = {"log.jsonl", "ASSAY.json", "RESULT", "variants.jsonl", "NEED", ".tokens", ".calls"}
BODY = {"compress": "squeeze.py", "fibmod": "fibmod.py", "csvsum": "csvsum.py", "maze": "maze.py"}

def cell(d, task):
    assay_t = None; fg = None; base = fin = None; done_t = None
    for l in open(d + "/log.jsonl"):
        try: r = json.loads(l)
        except Exception: continue
        if r.get("event") == "assay": assay_t = r["t"]           # latest accepted or attempted assay
        if "act" in r: done_t = r["t"]                           # last act of the cell, before the final measurement
        if r.get("event") == "final": fg, base, fin = r.get("final_gain"), r.get("baseline"), r.get("final")
    changed = []
    if assay_t is not None:
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x != "__pycache__" and not x.startswith(".")]
            if root != d: continue                               # top level only: daughters live in subfolders
            for f in files:
                if f in SKIP or f == BODY[task] or f.endswith(".pyc"): continue
                m = os.path.getmtime(os.path.join(root, f))
                # changed by the cell between the assay and its last act. Files the assay command itself
                # rewrites get a later mtime from the final measurement, so they are not counted.
                if assay_t + 1 < m < (done_t or 0) - 0.5: changed.append(f)
    return {"fg": fg, "base": base, "fin": fin, "changed": sorted(changed)}

data = {}
for a, p in ARMS.items():
    for i in range(1, 5):
        for t in TASKS:
            d = f"{E}/{p}{i}/{t}"
            if os.path.exists(d + "/log.jsonl"): data[(a, i, t)] = cell(d, t)

print("cells with benchmark files changed after the assay:")
bad = set()
for k, v in sorted(data.items()):
    if v["changed"] and v["fg"] is not None:
        bad.add(k); print("  ", ARMS[k[0]] + str(k[1]), k[2], "final_gain", v["fg"], "base", round(v["base"], 3), "final", round(v["fin"], 3), v["changed"])
print("count", len(bad), "of", sum(1 for v in data.values() if v["fg"] is not None), "assayed cells")
for a in ARMS: print("  arm", a, "flagged", sum(1 for k in bad if k[0] == a))

def vals(a, drop):
    return [v["fg"] for k, v in data.items() if k[0] == a and v["fg"] is not None and not (drop and k in bad)]
def taskmean(a, t, drop):
    x = [v["fg"] for k, v in data.items() if k[0] == a and k[2] == t and v["fg"] is not None and not (drop and k in bad)]
    return st.mean(x) if x else None
def perm(x, y, n=5000, seed=0):
    rng = random.Random(seed); obs = st.median(x) - st.median(y); pool = x + y; hit = 0
    for _ in range(n):
        rng.shuffle(pool)
        if abs(st.median(pool[:len(x)]) - st.median(pool[len(x):])) >= abs(obs) - 1e-12: hit += 1
    return round(obs, 4), round((hit + 1) / (n + 1), 4)
NOMAZE = False
for drop in (False, True, "nomaze"):
    if drop == "nomaze":
        data = {k: v for k, v in data.items() if k[2] != "maze"}; TASKS = [t for t in TASKS if t != "maze"]; drop = False
        print("\n== maze task removed entirely (3 tasks)")
    else:
        print("\n== " + ("flagged cells dropped" if drop else "all assayed cells (matches e12.py)"))
    for a in ARMS:
        x = vals(a, drop); print("  ", a, "n", len(x), "median", round(st.median(x), 4) if x else None, "worse(<-0.03)", sum(1 for q in x if q < -0.03))
    pairs = [("nh", "n"), ("nh", "ch"), ("ch", "c"), ("n", "c")] if P == "e12" else [("n", "c")]
    for a, b in pairs:
        td = {}
        for t in TASKS:
            ma, mb = taskmean(a, t, drop), taskmean(b, t, drop)
            if ma is not None and mb is not None: td[t] = round(ma - mb, 4)
        o, p = perm(vals(a, drop), vals(b, drop))
        print("  ", a, "minus", b, "task diffs", td, "| median", round(st.median(td.values()), 4), "| positive", sum(1 for q in td.values() if q > 0), "of", len(td), "| cell median diff", o, "| p", p)

# Third view, NOT preregistered: mean instead of median, and attempt outcomes. Maze excluded (data already filtered above).
print("\n== means, maze removed (not preregistered)")
for a in ARMS:
    tm = {t: [data[(a, r, t)]["fg"] for r in range(1, 5) if (a, r, t) in data and data[(a, r, t)]["fg"] is not None] for t in TASKS}
    means = {t: round(sum(v) / len(v), 4) for t, v in tm.items() if v}
    allv = [x for v in tm.values() for x in v]
    print("  ", a, "task means", means, "| mean of task means", round(sum(means.values()) / len(means), 4),
          "| cell mean", round(sum(allv) / len(allv), 4), "| cells with gain > 0.03:", sum(1 for x in allv if x > 0.03), "of", len(allv),
          "| max", round(max(allv), 4))
