"""E11 analysis, written 2026-11-10 while the run was in progress and before any E11 arm data was read.
Definitions follow the E11 preregistration in TESTS.md. Pilot (e11p) is excluded.
Reading of 'permutation test on cell medians': statistic is median(novar cells) - median(ctrl cells) over
final_gain of cells with an assay, cell labels shuffled, 5000 shuffles, seed 0, two sided."""
import json, random, statistics as st, sys
from pathlib import Path
E = Path.home() / "Work/razi-cells/exp"
ARMS = {"ctrl": [f"e11c{i}" for i in (1, 2, 3, 4)], "novar": [f"e11n{i}" for i in (1, 2, 3, 4)]}
if len(sys.argv) > 1 and sys.argv[1] == "selftest": ARMS = {"ctrl": ["e11p"], "novar": ["e11p"]}
def cells(arm):
    for r in ARMS[arm]:
        f = E / r / "summary.json"
        if not f.exists(): print("MISSING", r); continue
        for name, c in json.loads(f.read_text())["cells"].items(): yield r, name, c
def arm_table(arm):
    cs = list(cells(arm)); assayed = [c for _, _, c in cs if c.get("assays", 0) > 0 and c.get("final_gain") is not None]
    g = [c["final_gain"] for c in assayed]
    calls = sum(c["calls"] for _, _, c in cs); imps = sum(c["improvements"] for _, _, c in cs); tok = sum(c.get("tokens", 0) for _, _, c in cs)
    return dict(cells=len(cs), assayed=len(assayed), O4_share=round(len(assayed) / max(len(cs), 1), 3),
                O1_median=round(st.median(g), 4) if g else None, calls=calls, imps=imps,
                O2_per100=round(100 * imps / max(calls, 1), 2), tokens=tok, O3_tok_per_imp=round(tok / imps) if imps else None,
                usd=round(sum(c.get("usd") or 0 for _, _, c in cs), 3), budget_hits=sum(bool(c.get("token_budget_hit")) for _, _, c in cs),
                deaths=sum(bool(c.get("apoptosis")) for _, _, c in cs),
                routes=sorted({r for _, _, c in cs for r in (c.get("routes") or {})})), g
def per_task(arm):
    d = {}
    for _, name, c in cells(arm):
        if c.get("assays", 0) > 0 and c.get("final_gain") is not None: d.setdefault(name, []).append(c["final_gain"])
    return {k: st.mean(v) for k, v in d.items()}, {k: len(v) for k, v in d.items()}
T = {}; G = {}
for a in ARMS: T[a], G[a] = arm_table(a); print(a, T[a])
A, nA = per_task("novar"); B, nB = per_task("ctrl")
diffs = {k: round(A[k] - B[k], 4) for k in A if k in B}
print("per task novar mean", {k: round(v, 4) for k, v in A.items()}, "n", nA)
print("per task ctrl  mean", {k: round(v, 4) for k, v in B.items()}, "n", nB)
med = round(st.median(diffs.values()), 4) if diffs else None
print("task diffs novar-ctrl", diffs, "| median", med, "| positive", sum(v > 0 for v in diffs.values()), "of", len(diffs))
obs = st.median(G["novar"]) - st.median(G["ctrl"]); pool = G["novar"] + G["ctrl"]; k = len(G["novar"]); rng = random.Random(0); ge = 0
for _ in range(5000):
    rng.shuffle(pool); ge += abs(st.median(pool[:k]) - st.median(pool[k:])) >= abs(obs) - 1e-12
print("permutation: obs median diff", round(obs, 4), "two sided p", round((ge + 1) / 5001, 4), "n", k, len(pool) - k)
c, n = T["ctrl"], T["novar"]
print("H12 ctrl beats novar (median task diff < 0):", med, "->", med is not None and med < 0)
print("H13 >=75% assayed in both arms:", c["O4_share"], n["O4_share"], "->", c["O4_share"] >= 0.75 and n["O4_share"] >= 0.75)
print("H14 ctrl >=5 imp/100 and novar fewer:", c["O2_per100"], n["O2_per100"], "->", c["O2_per100"] >= 5 and n["O2_per100"] < c["O2_per100"])
print("H15 novar more tokens per improvement:", n["O3_tok_per_imp"], "vs", c["O3_tok_per_imp"], "->",
      (n["O3_tok_per_imp"] is None and c["O3_tok_per_imp"] is not None) or (None not in (n["O3_tok_per_imp"], c["O3_tok_per_imp"]) and n["O3_tok_per_imp"] > c["O3_tok_per_imp"]))
