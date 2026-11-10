"""SP2 DIAGNOSTIC, not preregistered. Written after sp2.py output was seen. Reads logs only, no model calls.
usage: python sp2_diag.py   (run in exp/)"""
import json, glob, os, statistics as st, hashlib
RUNS = [f"s2{a}{i}" for i in range(1, 5) for a in "fsm"]
PARTS = ["compress", "fibmod", "csvsum", "maze"]
def ev(p):
    out = []
    if not os.path.exists(p): return out
    for l in open(p):
        try: out.append(json.loads(l))
        except Exception: pass
    return out
ref = {(r["run"], r["kit"]): r["rel"] for r in json.load(open("results/sp2-ref.json")) if r.get("run")}

print("== 1. input-side estimate against the real input cost (cost - basal - output), by model")
PR = {"light": (1, 5), "mid": (20, 100), "heavy": (40, 200)}
by = {}
for p in glob.glob("s2*/*/log.jsonl"):
    for e in ev(p):
        if "usage" in e and e.get("est") is not None and e.get("model") in PR:
            real = e["cost"] - 8 - (e["usage"].get("out") or 0) / 1000 * PR[e["model"]][1]
            by.setdefault(e["model"], []).append((real, e["est"]))
for m, v in sorted(by.items()):
    d = [r - s for r, s in v]
    print(f"  {m:6} n {len(v):3} median real {st.median(r for r,_ in v):6.1f} median est {st.median(s for _,s in v):6.1f} "
          f"median real-est {st.median(d):+.1f} max real-est {max(d):+.1f} share est too low {sum(x>0 for x in d)/len(d):.2f}")

print("== 2. model used at each step (m mid, l light), per part cell")
for run in RUNS:
    row = []
    for part in PARTS:
        L = ev(f"{run}/{part}/log.jsonl")
        us = [e for e in L if "usage" in e]
        mods = "".join((e.get("model") or "?")[0] for e in us)
        row.append(f"{part[:4]} {mods or '-'}")
    print(f"  {run}: " + " | ".join(row))

print("== 3. wakes: what the woken part did, and whether its body changed")
for run in [r for r in RUNS if r[2] == "s"]:
    S = ev(f"{run}/stem/log.jsonl")
    for e in S:
        if e.get("event") == "feed" and e.get("wake"):
            print("  ", run, {k: e[k] for k in e if k not in ("t", "event")})
    for part in PARTS:
        L = ev(f"{run}/{part}/log.jsonl")
        rests = [i for i, e in enumerate(L) if e.get("event") in ("rest", "death")]
        if len(rests) < 2 and not any(e.get("event") == "downshift" for e in L): continue
        cut = rests[0] if rests else 0
        after = L[cut + 1:]
        us = [e for e in after if "usage" in e]
        acts = [ (e["act"].get("do")) for e in after if "act" in e]
        imps = [round(e.get("gain", 0), 4) for e in after if e.get("event") == "improve"]
        ds = [(e.get("frm"), e.get("to"), e.get("e")) for e in after if e.get("event") == "downshift"]
        print(f"   {run}/{part}: after first stop: steps {len(us)} models {''.join((e.get('model') or '?')[0] for e in us)} "
              f"cost {sum(e['cost'] for e in us):.1f} acts {acts} improves {imps} downshifts {ds} rel {ref.get((run, part))}")

print("== 4. fibmod bodies: size, hash, markers")
for run in RUNS:
    d = f"{run}/fibmod"
    b = [f for f in os.listdir(d) if f.endswith(".py")] if os.path.isdir(d) else []
    for f in b:
        s = open(f"{d}/{f}").read()
        mk = {k: (k in s) for k in ("sys.stdin.buffer", "pisano", "Pisano", "lru_cache", "numpy", "divmod", "bit_length", "matrix", "join", "ctypes", "gmpy")}
        print(f"  {run} {f} {len(s)}B {hashlib.sha256(s.encode()).hexdigest()[:8]} rel {ref.get((run,'fibmod'))} " + " ".join(k for k, v in mk.items() if v))
for run in ("kp_ch", "msmoke1", "e13ch1"):
    d = f"{run}/fibmod"
    for f in [f for f in os.listdir(d) if f.endswith(".py")]:
        s = open(f"{d}/{f}").read()
        mk = [k for k in ("sys.stdin.buffer", "pisano", "Pisano", "lru_cache", "numpy", "divmod", "bit_length", "matrix", "join", "ctypes", "gmpy") if k in s]
        print(f"  CEIL {run} {f} {len(s)}B " + " ".join(mk))

print("== 5. O1 with the s2f1 compress zero dropped (median over the 3 parts that have a body)")
for a in "fsm":
    meds = []
    for i in range(1, 5):
        v = [ref[(f"s2{a}{i}", p)] for p in PARTS if ref.get((f"s2{a}{i}", p), 0) > 0]
        meds.append(st.median(v))
    print(f"  {a}: run medians {[round(x,3) for x in meds]} mean {st.mean(meds):.4f}")
print("== 6. O1 per arm with fibmod left out (median of 3 parts)")
for a in "fsm":
    meds = [st.median([ref[(f"s2{a}{i}", p)] for p in PARTS if p != "fibmod"]) for i in range(1, 5)]
    print(f"  {a}: {[round(x,3) for x in meds]} mean {st.mean(meds):.4f}")

print("== 7. variants rounds: model that thought the step, versions tried, adopted gain")
for run in RUNS:
    for part in PARTS:
        L = ev(f"{run}/{part}/log.jsonl"); last = None; out = []
        for e in L:
            if "usage" in e: last = (e.get("model") or "?")[0]
            if e.get("event") == "variants": out.append(f"{last}:{e.get('n', e.get('tried', '?'))}")
            if e.get("event") == "improve": out.append(f"WIN{e.get('gain', 0):+.3f}")
        if out: print(f"  {run}/{part}: " + " ".join(out))
print("== 8. per arm: variants rounds, rounds that won, cells that rested with no variants round")
for a in "fsm":
    vr = w = nov = cells = 0
    for i in range(1, 5):
        for part in PARTS:
            L = ev(f"s2{a}{i}/{part}/log.jsonl"); cells += 1
            v = sum(e.get("event") == "variants" for e in L); vr += v
            w += sum(e.get("event") == "improve" for e in L); nov += (v == 0)
    print(f"  {a}: cells {cells} variants rounds {vr} wins {w} win share {w/max(vr,1):.2f} cells with no round {nov}")

print("== 9. model that thought the first write of the body, and steps on mid, per arm")
for a in "fsm":
    fw = {"m": 0, "l": 0, "h": 0, "none": 0}; midsteps = []; 
    for i in range(1, 5):
        for part in PARTS:
            L = ev(f"s2{a}{i}/{part}/log.jsonl"); last = None; got = None; nm = 0
            for e in L:
                if "usage" in e:
                    last = (e.get("model") or "?")[0]; nm += (last == "m")
                if got is None and "act" in e and e["act"].get("do") in ("write", "variants") and not str(e.get("res", "")).startswith("refused"):
                    got = last
            fw[got or "none"] += 1; midsteps.append(nm)
    print(f"  {a}: first body thought on {fw} | mid steps per cell: median {st.median(midsteps)} max {max(midsteps)} total {sum(midsteps)}")

print("== 10. cross-experiment rel per kit (ceiling-ref.json session for old runs, sp2-ref.json for SP2). Different")
print("       sessions, runtimes and step caps: a lead only.")
old = {(r["run"], r["kit"]): r["rel"] for r in json.load(open("results/ceiling-ref.json")) if r.get("run")}
groups = {"e13 c (sonnet, cell.py)": [f"e13c{i}" for i in range(1, 5)], "e13 ch (sonnet, hold)": [f"e13ch{i}" for i in range(1, 5)],
          "e13 n (sonnet, no variants)": [f"e13n{i}" for i in range(1, 5)]}
for g, runs in groups.items():
    print(f"  {g:30} " + " ".join(f"{p[:4]} {st.median([old[(r,p)] for r in runs if (r,p) in old]):.3f}" for p in PARTS))
for a in "fsm":
    print(f"  {'SP2 ' + a + ' (energy laws)':30} " + " ".join(f"{p[:4]} {st.median([ref[(f's2{a}{i}',p)] for i in range(1,5)]):.3f}" for p in PARTS))
