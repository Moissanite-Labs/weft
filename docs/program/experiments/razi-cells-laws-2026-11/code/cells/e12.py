"""E12 analysis, written 2026-11-10 before any E12 arm data existed (only the pilot e12p was running).
Definitions follow the E12 preregistration in TESTS.md. Pilot (e12p) is excluded.
Arms: c = ctrl, n = novar, ch = ctrl+hold, nh = novar+hold. Usage: e12.py [selftest]"""
import json, random, statistics as st, sys
from pathlib import Path
E = Path.home() / "Work/razi-cells/exp"
ARMS = {a: [f"e12{a}{i}" for i in (1, 2, 3, 4)] for a in ("c", "n", "ch", "nh")}
if len(sys.argv) > 1 and sys.argv[1] == "selftest": ARMS = {a: ["e12p"] for a in ARMS}
SEARCH = ("write", "variants", "try")
def cells(arm):
    for r in ARMS[arm]:
        f = E / r / "summary.json"
        if not f.exists(): print("MISSING", r); continue
        for name, c in json.loads(f.read_text())["cells"].items(): yield r, name, c
def acts(run, name):
    out, holds = [], 0
    f = E / run / name / "log.jsonl"
    for line in (f.read_text().splitlines() if f.exists() else []):
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("event") == "hold": holds += 1
        a = e.get("act")
        if isinstance(a, dict) and a.get("do"):
            out.append((a["do"], str(e.get("res", ""))))
    return out, holds
def ok(c): return c.get("assays", 0) > 0 and c.get("final_gain") is not None
def arm_table(arm):
    cs = list(cells(arm)); assayed = [(r, n, c) for r, n, c in cs if ok(c)]
    g = [c["final_gain"] for _, _, c in assayed]
    calls = sum(c["calls"] for _, _, c in cs); imps = sum(c["improvements"] for _, _, c in cs); tok = sum(c.get("tokens", 0) for _, _, c in cs)
    attempted = tries = holds = 0
    for r, n, c in cs:
        a, h = acts(r, n); holds += h; tries += sum(d == "try" for d, _ in a)
        if ok(c):
            first = next((i for i, (d, res) in enumerate(a) if d == "assay" and res.startswith("assay accepted")), None)
            attempted += first is not None and any(d in SEARCH for d, _ in a[first + 1:])
    return dict(cells=len(cs), assayed=len(assayed), O4_share=round(len(assayed) / max(len(cs), 1), 3),
                O1_median=round(st.median(g), 4) if g else None, calls=calls, imps=imps,
                O2_per100=round(100 * imps / max(calls, 1), 2), O5_attempt_share=round(attempted / max(len(assayed), 1), 3),
                O6_try_calls=tries, O7_worse=sum(x < -0.03 for x in g), holds=holds, tokens=tok,
                usd=round(sum(c.get("usd") or 0 for _, _, c in cs), 3), budget_hits=sum(bool(c.get("token_budget_hit")) for _, _, c in cs),
                deaths=sum(bool(c.get("apoptosis")) for _, _, c in cs),
                routes=sorted({r for _, _, c in cs for r in (c.get("routes") or {})})), g
def per_task(arm):
    d = {}
    for _, name, c in cells(arm):
        if ok(c): d.setdefault(name, []).append(c["final_gain"])
    return {k: st.mean(v) for k, v in d.items()}
def compare(x, y):
    """x minus y: median of per-task mean differences, count positive, permutation p on cell final_gain."""
    A, B = per_task(x), per_task(y); diffs = {k: round(A[k] - B[k], 4) for k in A if k in B}
    med = round(st.median(diffs.values()), 4) if diffs else None
    gx, gy = G[x], G[y]; p = obs = None
    if gx and gy:
        obs = st.median(gx) - st.median(gy); pool = gx + gy; k = len(gx); rng = random.Random(0); ge = 0
        for _ in range(5000):
            rng.shuffle(pool); ge += abs(st.median(pool[:k]) - st.median(pool[k:])) >= abs(obs) - 1e-12
        p = round((ge + 1) / 5001, 4); obs = round(obs, 4)
    print(f"{x} minus {y}: task diffs {diffs} | median {med} | positive {sum(v > 0 for v in diffs.values())} of {len(diffs)}"
          f" | cell median diff {obs} | two sided p {p} | n {len(gx)} {len(gy)}")
    return med
T, G = {}, {}
for a in ARMS: T[a], G[a] = arm_table(a); print(a, T[a])
m17, m18, m19, m21 = compare("nh", "n"), compare("nh", "ch"), compare("ch", "c"), compare("n", "c")
def show(label, val, verdict): print(label, val, "->", verdict)
show("H16 O5 in novar+hold >= 0.75:", T["nh"]["O5_attempt_share"], T["nh"]["O5_attempt_share"] >= 0.75)
show("H17 novar+hold beats novar (median task diff > 0):", m17, m17 is not None and m17 > 0)
show("H18 ctrl+hold beats novar+hold (nh minus ch < 0):", m18, m18 is not None and m18 < 0)
show("H19 hold neutral for ctrl (|ch minus c| < 0.03):", m19, m19 is not None and abs(m19) < 0.03)
show("H20 at least one try call in novar+hold:", T["nh"]["O6_try_calls"], T["nh"]["O6_try_calls"] >= 1)
show("H21 ctrl beats novar again (n minus c < 0):", m21, m21 is not None and m21 < 0)
