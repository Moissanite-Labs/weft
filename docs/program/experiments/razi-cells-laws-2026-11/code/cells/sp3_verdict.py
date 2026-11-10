#!/usr/bin/env python3
"""SP3 verdicts. Written 2026-11-10 AFTER the SP3 report was read. It adds no new measure: it applies the guesses
S3-a to S3-l exactly as worded in TESTS.md to the logs, the ledgers and results/sp3-ref.json, so no verdict is read by eye.
  python sp3_verdict.py REF.json"""
import json, sys, statistics as st
from pathlib import Path
PARTS = ("compress", "fibmod", "csvsum", "maze"); RANK = {"light": 0, "mid": 1, "heavy": 2}
ARMS = {a: [f"s3{a}{i}" for i in (1, 2, 3, 4)] for a in "abcd"}
WANT = {"a": (True, False), "b": (False, False), "c": (True, True), "d": (False, True)}
ref = json.load(open(sys.argv[1]))
def rows(p): return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
REL = {(r["run"], r["kit"]): r["rel"] for r in ref}
def rel(run, part): return REL[(run, part)]
S = {a: dict(laws_ok=0, sense=0, sense_err=0, over=0, light0=0, steps=0, light=0, above=0, light4=0, after=[], rounds2=0,
             climb=0, divide=0, spent=0.0) for a in ARMS}
for a, runs in ARMS.items():
    s = S[a]
    for run in runs:
        led = json.load(open(f"{run}/.ledger.json"))
        s["spent"] += sum(v.get("spent", 0) for v in led.values() if isinstance(v, dict))
        for part in PARTS:
            R = rows(f"{run}/{part}/log.jsonl"); models = []; seen = False; after = 0; rounds = 0; prev = None; climbed = False
            for r in R:
                ev = r.get("event")
                if ev == "laws": s["laws_ok"] += (r["price_show"], r["sense_show"]) == WANT[a] and r["start"][0] == "mid"
                elif ev == "sense": pass
                elif ev == "sense_error": s["sense_err"] += 1
                elif ev == "overdraft": s["over"] += 1
                elif ev == "divide": s["divide"] += 1
                elif ev == "assay": seen = True
                if "usage" in r:
                    m = r["model"]; models.append(m)
                    if seen:
                        after += 1
                        if prev is not None and RANK[m] > RANK[prev]: climbed = True
                    prev = m
                if "act" in r and isinstance(r["act"], dict) and seen and r["act"].get("do") == "variants": rounds += 1
            s["sense"] += any(r.get("event") == "sense" for r in R)
            fn = next((r.get("next") for r in R if "act" in r and r.get("next")), None)  # same definition as B1 in sp3.py
            s["light0"] += bool(fn) and fn[0] == "light"
            s["steps"] += len(models); s["light"] += models.count("light")
            s["above"] += any(RANK[m] > RANK["mid"] for m in models)
            s["light4"] += "light" in models[:4]
            if seen: s["after"].append(after)
            s["rounds2"] += rounds >= 2; s["climb"] += climbed
O1 = {a: st.mean(st.median(rel(run, p) for p in PARTS) for run in runs) for a, runs in ARMS.items()}
fib = {a: sum(rel(run, "fibmod") >= 2.0 for run in runs) for a, runs in ARMS.items()}
ma = {a: st.mean(S[a]["after"]) for a in ARMS}
print("counts", json.dumps({a: {k: (round(v, 1) if isinstance(v, float) else v) for k, v in s.items() if k != "after"} for a, s in S.items()}))
print("O1", {a: round(v, 4) for a, v in O1.items()}, "| fibmod runs at 2.0 or above", fib, "| mean steps after first assay", {a: round(v, 2) for a, v in ma.items()})
tot = lambda k: sum(S[a][k] for a in ARMS)
J = [
 ("S3-a laws match, 56+ of 64 sensed, 2 or fewer sense errors, 2 or fewer overdrafts", tot("laws_ok") == 64 and tot("sense") >= 56 and tot("sense_err") <= 2 and tot("over") <= 2,
  f"laws {tot('laws_ok')}/64 sensed {tot('sense')}/64 errors {tot('sense_err')} overdrafts {tot('over')}"),
 ("S3-b arm a: 12+ of 16 light at step 0, light share 0.70+, 0 above birth", S["a"]["light0"] >= 12 and S["a"]["light"] / S["a"]["steps"] >= 0.70 and S["a"]["above"] == 0,
  f"{S['a']['light0']}/16, share {S['a']['light'] / S['a']['steps']:.3f}, above {S['a']['above']}"),
 ("S3-c arm b: at most 8 of 16 light at step 0", S["b"]["light0"] <= 8, f"{S['b']['light0']}/16"),
 ("S3-d arm b: 10+ of 16 on light by 4th step", S["b"]["light4"] >= 10, f"{S['b']['light4']}/16"),
 ("S3-e b spends 1.3x a or more, and b level with a on O1", S["b"]["spent"] >= 1.3 * S["a"]["spent"] and abs(O1["b"] - O1["a"]) < 0.10,
  f"energy ratio {S['b']['spent'] / S['a']['spent']:.2f}, O1 b minus a {O1['b'] - O1['a']:+.4f}"),
 ("S3-f steps after first assay, b within 1.0 of a", abs(ma["b"] - ma["a"]) <= 1.0, f"b {ma['b']:.2f} a {ma['a']:.2f}"),
 ("S3-g c at least 1.0 above a on steps after assay, 4+ of 16 in c with 2+ rounds, at most 2 in a", ma["c"] - ma["a"] >= 1.0 and S["c"]["rounds2"] >= 4 and S["a"]["rounds2"] <= 2,
  f"c minus a {ma['c'] - ma['a']:+.2f}, 2+ rounds c {S['c']['rounds2']} a {S['a']['rounds2']}"),
 ("S3-h fibmod 2.0 in 4+ of 8 sensor runs and at most 2 of 8 without", fib["c"] + fib["d"] >= 4 and fib["a"] + fib["b"] <= 2,
  f"sensor {fib['c'] + fib['d']}/8 (c {fib['c']} d {fib['d']}), without {fib['a'] + fib['b']}/8 (a {fib['a']} b {fib['b']})"),
 ("S3-i c above a by 0.10 or more on O1", O1["c"] - O1["a"] >= 0.10, f"{O1['c'] - O1['a']:+.4f}"),
 ("S3-j climbs after first assay: at most 1 of 16 in a, 4+ of 32 in c and d", S["a"]["climb"] <= 1 and S["c"]["climb"] + S["d"]["climb"] >= 4,
  f"a {S['a']['climb']}, c+d {S['c']['climb'] + S['d']['climb']}, b {S['b']['climb']}"),
 ("S3-k 0 divides", tot("divide") == 0, f"{tot('divide')}"),
 ("S3-l d level with c or above on O1", O1["d"] - O1["c"] > -0.10, f"d minus c {O1['d'] - O1['c']:+.4f}"),
]
for k, v, why in J: print(("HELD   " if v else "MISSED ") + k + " | " + why)
print("held %d of %d" % (sum(v for _, v, _ in J), len(J)))
