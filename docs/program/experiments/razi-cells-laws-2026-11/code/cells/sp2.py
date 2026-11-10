#!/usr/bin/env python3
"""SP2 report (T-K2). Written 2026-11-10 before any SP2 data. Run unchanged.

  python sp2.py REF.json CEIL.json ARM=run,run,... [ARM=run,...]     (run dirs are looked up in the current folder)

REF.json  : refscore.py output for the SP2 runs (rel = final body / reference body, one session, interleaved).
CEIL.json : refscore.py output made before SP2, the best body any earlier run produced per kit (IDEAS K15).
Primary outcome O1: per run, the median rel over the 4 parts. Arm value = mean of its run medians.
O2: share of the gap from reference to ceiling, (rel - 1) / (ceiling - 1), per part, arm mean.
Numbers come from REF.json, log.jsonl and .ledger.json only.
"""
import json, random, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stem_report import ev, PARTS  # noqa: E402

SHUFFLES, SEED = 5000, 0


def perm(a, b):
    """Two sided, difference of medians, cells shuffled between arms. Overstates n (cells in a run are not independent)."""
    rng = random.Random(SEED)
    obs = statistics.median(a) - statistics.median(b)
    pool, n, hit = a + b, len(a), 0
    for _ in range(SHUFFLES):
        rng.shuffle(pool)
        if abs(statistics.median(pool[:n]) - statistics.median(pool[n:])) >= abs(obs) - 1e-12:
            hit += 1
    return round(obs, 4), round((hit + 1) / (SHUFFLES + 1), 4)


def usage(run):
    c = t = cr = 0; usd = 0.0
    for d in PARTS + ["stem"]:
        for e in ev(Path(run) / d):
            u = e.get("usage")
            if isinstance(u, dict):
                c += 1; t += (u.get("inp") or 0) + (u.get("out") or 0) + (u.get("cw") or 0)
                cr += u.get("cr") or 0; usd += u.get("usd") or 0
    return c, t, t + cr, usd


def law(run):
    led = json.loads((Path(run) / ".ledger.json").read_text())
    evs = [e for d in PARTS + ["stem"] for e in ev(Path(run) / d)]
    n = lambda k: sum(e.get("event") == k for e in evs)  # noqa: E731
    acts = [e["act"].get("do") for e in evs if "act" in e]
    return {"min_e": round(min(v["e"] for v in led.values()), 1), "overdraft": n("overdraft"), "downshift": n("downshift"),
            "death": n("death"), "divide": acts.count("divide"), "improve": n("improve"),
            "spent": sum(v.get("spent", 0) for k, v in led.items() if "/" not in k),
            "earned": sum(v.get("earned", 0) for v in led.values()),
            "stem_e": led.get("stem", {}).get("e"), "stem_born": led.get("stem", {}).get("born")}


def own_gain(run):
    out = []
    for p in PARTS:
        fin = [e for e in ev(Path(run) / p) if e.get("event") == "final" and "final_gain" in e]
        out.append(fin[-1]["final_gain"] if fin else 0.0)
    return out


def wakes(run):
    """Each wake with the part's own gain when it last stopped before the wake, and whether it then held the best gain."""
    es = ev(Path(run) / "stem")
    last, out = {}, []
    for e in es:
        if e.get("event") == "stopped":
            last[e["part"]] = e.get("fit") or 0.0
        if e.get("event") == "feed" and e["kind"] == "wake":
            f = last.get(e["part"], 0.0)
            best = max(last.values()) if last else 0.0
            out.append({"part": e["part"], "gave": e["gave"], "model": e.get("model"), "fit_then": round(f, 4),
                        "was_best": bool(last) and f >= best and f > 0.03, "flat_zero": f <= 0.03})
    births = [(e["part"], e["gave"], e.get("model")) for e in es if e.get("event") == "feed" and e["kind"] == "birth"]
    return births, out


def main(ref, ceil, arms):
    rows = json.loads(Path(ref).read_text())
    rel = {(r["kit"], r["run"]): r["rel"] for r in rows}
    zero = [(r["kit"], r["run"], r["why"]) for r in rows if r.get("why")]
    crow = [r for r in json.loads(Path(ceil).read_text()) if not r.get("why") and r["run"] != "ref"]
    ceiling = {k: max(r["rel"] for r in crow if r["kit"] == k) for k in PARTS}
    print("ceiling so far (rel, fixed before SP2):", {k: round(v, 3) for k, v in ceiling.items()})
    share = lambda k, v: (v - 1) / (ceiling[k] - 1) if ceiling[k] > 1 else float("nan")  # noqa: E731
    names = list(arms)
    O1, cells, part_mean, part_share, cost = {}, {}, {}, {}, {}
    for a, runs in arms.items():
        meds = []
        print(f"\n== arm {a}: {runs}")
        for r in runs:
            v = [rel.get((k, r), 0.0) or 0.0 for k in PARTS]
            meds.append(statistics.median(v))
            c, t, tc, usd = usage(r); L = law(r)
            cost.setdefault(a, []).append((c, t, tc, usd, L["spent"], L["earned"], L["improve"]))
            print(f"  {r:6} rel " + " ".join(f"{k} {x:.3f}" for k, x in zip(PARTS, v)) + f" | median {meds[-1]:.3f}"
                  f" | own gain {own_gain(r)} | calls {c} tok {t} usd {usd:.4f} spent {L['spent']:.1f} earned {L['earned']:.1f}"
                  f" | min_e {L['min_e']} overdraft {L['overdraft']} downshift {L['downshift']} death {L['death']}"
                  f" divide {L['divide']} imps {L['improve']}"
                  + (f" | stem unspent {L['stem_e'] / L['stem_born']:.2f}" if L["stem_born"] else ""))
            if (Path(r) / "stem").is_dir():
                b, w = wakes(r)
                print(f"         births {b}\n         wakes {w}")
        O1[a] = statistics.mean(meds)
        cells[a] = [rel.get((k, r), 0.0) or 0.0 for r in runs for k in PARTS]
        part_mean[a] = {k: statistics.mean(rel.get((k, r), 0.0) or 0.0 for r in runs) for k in PARTS}
        part_share[a] = {k: statistics.mean(share(k, rel.get((k, r), 0.0) or 0.0) for r in runs) for k in PARTS}
        print(f"  O1 mean of run medians {O1[a]:.4f} | run medians {[round(m, 3) for m in meds]}")
        print(f"  part mean rel {({k: round(v, 3) for k, v in part_mean[a].items()})}")
        print(f"  O2 share of gap {({k: round(v, 3) for k, v in part_share[a].items()})} | mean {statistics.mean(part_share[a].values()):.3f}")
        print(f"  own-baseline gain, median over cells {statistics.median([g for r in runs for g in own_gain(r)]):.4f}")
    print("\n== contrasts (first minus second)")
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = {k: part_mean[a][k] - part_mean[b][k] for k in PARTS}
            obs, p = perm(list(cells[a]), list(cells[b]))
            print(f"  {a} - {b}: O1 {O1[a] - O1[b]:+.4f} | per part {({k: round(v, 3) for k, v in d.items()})}"
                  f" | parts positive {sum(v > 0 for v in d.values())}/4 | median of part diffs {statistics.median(d.values()):+.4f}"
                  f" | cell medians diff {obs:+.4f} p {p}")
    print("\n== cost, arm totals")
    base = names[0]
    tot = {a: [sum(x[i] for x in cost[a]) for i in range(7)] for a in names}
    for a in names:
        c, t, tc, usd, sp, ea, im = tot[a]
        print(f"  {a}: calls {c} tokens {t} (with cache reads {tc}) usd {usd:.4f} energy spent {sp:.1f} earned {ea:.1f} imps {im}"
              f" | tokens vs {base} {t / max(tot[base][1], 1):.2f} | energy vs {base} {sp / max(tot[base][4], 1e-9):.2f}"
              f" | O1 above reference per 1000 energy {(O1[a] - 1) / max(sp, 1e-9) * 1000 * len(arms[a]):.4f}")
    for z in zero:
        print("ZERO SCORE", z)


if __name__ == "__main__":
    A = {}
    for s in sys.argv[3:]:
        k, v = s.split("=")
        A[k] = v.split(",")
    main(sys.argv[1], sys.argv[2], A)
