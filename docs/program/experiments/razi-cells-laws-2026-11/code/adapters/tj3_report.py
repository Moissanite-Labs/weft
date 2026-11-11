"""tj3_report.py: judge the T-J3 guesses as written. Written 2026-11-10 before any T-J3 training result exists.
Usage: python tj3_report.py OUT_seed0.json OUT_seed1.json OUT_seed2.json
Every number comes from the OUT files written by tj3.py. Lower loss is better (nats per row on test rows).
Each arm is judged on the median of its final test loss over the seeds given.
TJ-e uses counts summed over all seeds, since a median of a choice is not defined."""
import json, sys, statistics as st
from pathlib import Path
runs = [json.load(open(p)) for p in sys.argv[1:]]
bad = [p for p, r in zip(sys.argv[1:], runs) if not r.get("ok")]
if bad: print("INCOMPLETE runs, not judged:", bad); sys.exit(1)
ARMS = ("gc", "gn", "gb", "s")
prior = st.median(r["prior"]["test"] for r in runs)
start = st.median(r["start"]["test"] for r in runs)
med = {a: st.median(r["arms"][a]["test"] for r in runs) for a in ARMS}
print("seeds", [r["args"]["seed"] for r in runs], "| rows", runs[0]["rows"])
print("prior test %.5f | untrained start test %.5f" % (prior, start))
for a in ARMS:
    v = [r["arms"][a]["test"] for r in runs]
    print("%-3s test per seed %s | median %.5f | vs prior %+.1f%% | gate median %.5f" % (
        a, v, med[a], 100 * (med[a] / prior - 1), st.median(r["arms"][a]["gate"] for r in runs)))
nat = bal = ref = gens = 0
for r in runs:
    for g in r["arms"]["s"]["log"]:
        gens += 1
        if g["took"] == "nat": nat += 1
        elif g["took"] == "bal": bal += 1
        else: ref += 1
print("arm s gate over %d generations: took natural %d, took balanced %d, refused %d" % (gens, nat, bal, ref))
print("depth of the s lineage per seed:", [max([g["depth"] for g in r["arms"]["s"]["log"]] or [0]) for r in runs])
J = {
 "TJ-a gc below prior": med["gc"] < prior,
 "TJ-b gn worse than gc, by less than 15%": med["gn"] > med["gc"] and (med["gn"] / med["gc"] - 1) < 0.15,
 "TJ-c gb worse than gn": med["gb"] > med["gn"],
 "TJ-d s worse than gn": med["s"] > med["gn"],
 "TJ-e gate takes natural more than balanced, refuses at least once": nat > bal and ref >= 1,
 "TJ-f no arm more than 40% below prior": min(med.values()) >= 0.6 * prior,
}
for k, v in J.items(): print(("HELD   " if v else "MISSED ") + k)
print("held %d of %d" % (sum(J.values()), len(J)))
tok = {}
for r in runs:
    for k, v in r.get("tokens", {}).items(): tok[k] = tok.get(k, 0) + v
print("tokens", tok, "| wall s", [r.get("wall_s") for r in runs])

# Per-generation eval_nll trajectory from each OUT file's companion jsonl (one file per OUT).
trajectories: dict[tuple, list[tuple[int, float]]] = {}
for p in sys.argv[1:]:
    jf = Path(p).with_suffix(".jsonl")
    if not jf.is_file():
        continue
    for line in open(jf):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("event") != "eval" or "eval_nll" not in e:
            continue
        key = (e.get("tag", "?"), e.get("seed", 0), e.get("arm", "unknown"))
        trajectories.setdefault(key, []).append((e.get("gen", 0), e["eval_nll"]))

if trajectories:
    print("\neval_nll trajectory (from OUT jsonl, eval events):")
    for (tag, s, a), pts in sorted(trajectories.items()):
        seen: dict[int, float] = {}
        for g, nll in pts:
            seen[g] = nll
        pts_str = ", ".join(f"g{g}: {nll:.5f}" for g, nll in sorted(seen.items()))
        print(f"  tag {tag} seed {s} arm {a:<5}: {pts_str}")
else:
    print("\n(no eval_nll jsonl trajectories found)")
