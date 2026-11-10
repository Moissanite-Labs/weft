"""lineage_report.py: L1 report. Written 2026-11-11 before any L1 data. Run unchanged.

  python lineage_report.py REF.json h=run,run,run b=run,run,run

REF.json is refscore.py output over results/l1-final/<run>/<kit> (the final germline body of each lineage).
Reads each run's lineage.jsonl, summary.json and the cells' log.jsonl. Prints HELD or MISSED for L1-a to L1-h.
"""
import json, statistics, sys
from pathlib import Path

E = Path.home() / "Work/razi-cells/exp"
ref = json.loads(Path(sys.argv[1]).read_text())
REL = {(r["run"], r["kit"]): r["rel"] for r in ref}
arms = {a.split("=")[0]: a.split("=")[1].split(",") for a in sys.argv[2:]}
med = statistics.median


def rows(run):
    return [json.loads(l) for l in (E / run / "lineage.jsonl").read_text().splitlines()]


def cell_events(run, cell):
    f = E / run / cell / "log.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []


out = {}
for arm, runs in arms.items():
    A = out[arm] = {"o1": [], "lineages": [], "inherit_ok": 0, "inherit_n": 0, "late_takes": 0, "late_cells": 0,
                    "late_idle": 0, "spent0": [], "spent_late": [], "store_up": 0, "extinct": 0, "errors": 0,
                    "deaths": 0, "cells": 0, "improve": 0, "income": 0.0, "total_spent": 0.0}
    for run in runs:
        R = rows(run)
        start = [r for r in R if r.get("event") == "start"][0]
        gens = [r for r in R if r.get("event") == "gen"]
        kits = start["kits"]
        A["o1"].append(med([REL.get((run, k)) or 0.0 for k in kits]))
        for k in kits:
            G = [g for g in gens if g["kit"] == k]
            late = [g for g in G if g["gen"] >= 1]
            took_late = sum(1 for g in late if g.get("took"))
            A["late_takes"] += took_late
            A["store_up"] += 1 if G and G[-1]["store"] > start["store"] else 0
            A["extinct"] += 1 if len(G) < start["gens"] or any(not g["cells"] for g in G) else 0
            A["lineages"].append({"run": run, "kit": k, "rel": REL.get((run, k)), "took_late": took_late,
                                  "store_end": G[-1]["store"] if G else None, "gains": [g.get("gain") for g in G]})
            for g in G:
                per = g["spent"] / max(len(g["cells"]), 1)
                (A["spent0"] if g["gen"] == 0 else A["spent_late"]).append(per)
                A["total_spent"] += g["spent"]
                A["income"] += g["earned"]
                for c in g["cells"]:
                    ev = cell_events(run, c)
                    A["cells"] += 1
                    A["errors"] += sum(1 for e in ev if e.get("event") in ("error", "overdraft"))
                    A["deaths"] += 1 if g["states"].get(c) == "dead" else 0
                    A["improve"] += sum(1 for e in ev if e.get("event") == "improve")
                    inh = [e for e in ev if e.get("event") == "inherit"]
                    if g["gen"] >= 1:
                        A["late_cells"] += 1
                        A["inherit_n"] += 1 if arm == "h" else 0
                        A["inherit_ok"] += 1 if inh and inh[0].get("ok") else 0
                        acts = [(e.get("act") or {}).get("do") for e in ev if e.get("act")]
                        tried = any(x in ("write", "variants", "divide") for x in acts)
                        A["late_idle"] += 0 if tried else 1

for arm, A in out.items():
    print(f"\nARM {arm}: runs {arms[arm]}")
    print(f"  O1 run medians of final germline rel: {[round(x, 3) for x in A['o1']]}  mean {statistics.mean(A['o1']):.4f}")
    for L in A["lineages"]:
        print(f"   {L['run']:8} {L['kit']:9} rel {L['rel']}  late takes {L['took_late']}  store end {L['store_end']}  gate gains {L['gains']}")
    print(f"  cells {A['cells']}  deaths {A['deaths']}  errors {A['errors']}  improve events {A['improve']}  income {A['income']:.1f}  spent {A['total_spent']:.1f}")
    print(f"  late cells {A['late_cells']}  inherit ok {A['inherit_ok']}  late cells with no write/variants/divide {A['late_idle']}")
    print(f"  spent per cell: gen 0 median {med(A['spent0']) if A['spent0'] else None}, later median {med(A['spent_late']) if A['spent_late'] else None}")
    print(f"  lineages whose store ended above its start: {A['store_up']} of {len(A['lineages'])}; extinct {A['extinct']}")

h, b = out.get("h"), out.get("b")
def verdict(name, ok, info):
    print(f"{name}: {'HELD' if ok else 'MISSED'}  ({info})")
print()
if h and b:
    verdict("L1-a", h["inherit_n"] > 0 and h["inherit_ok"] == h["inherit_n"] and b["inherit_ok"] == 0 and h["errors"] + b["errors"] == 0,
            f"h inherit {h['inherit_ok']}/{h['inherit_n']}, b inherit {b['inherit_ok']}, errors {h['errors']}+{b['errors']}")
    d = statistics.mean(h["o1"]) - statistics.mean(b["o1"])
    verdict("L1-b", d >= 0.10, f"O1 h minus b {d:+.4f}, needs +0.10 or more")
    nl = len(h["lineages"]); wl = sum(1 for L in h["lineages"] if L["took_late"] >= 1)
    verdict("L1-c", wl * 2 >= nl, f"{wl} of {nl} heredity lineages replaced the germline after generation 0")
    s0, sl = med(h["spent0"]), med(h["spent_late"])
    verdict("L1-d", sl < 0.6 * s0, f"h spent per cell: later {sl:.1f} against gen 0 {s0:.1f}, needs under 0.6")
    verdict("L1-e", h["store_up"] * 2 < nl, f"{h['store_up']} of {nl} heredity stores ended above their start")
    verdict("L1-f", h["late_idle"] * 2 > h["late_cells"], f"{h['late_idle']} of {h['late_cells']} later heredity cells did no write, variants or divide")
    kits = sorted({L["kit"] for L in h["lineages"]})
    dk = {k: statistics.mean([L["rel"] or 0 for L in h["lineages"] if L["kit"] == k]) -
             statistics.mean([L["rel"] or 0 for L in b["lineages"] if L["kit"] == k]) for k in kits}
    top = max(dk, key=lambda k: abs(dk[k]))
    verdict("L1-g", top == "fibmod", "per kit h minus b: " + ", ".join(f"{k} {v:+.3f}" for k, v in dk.items()))
    eff_h = (statistics.mean(h["o1"]) - 1) / max(h["total_spent"], 1) * 1000
    eff_b = (statistics.mean(b["o1"]) - 1) / max(b["total_spent"], 1) * 1000
    verdict("L1-h", eff_h > eff_b, f"(O1 minus 1) per 1000 energy spent: h {eff_h:.4f}, b {eff_b:.4f}")
