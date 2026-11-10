#!/usr/bin/env python3
"""SP3 report (T-K3 plus the price question). Written 2026-11-10 before any SP3 data. Run unchanged.

  python sp3.py REF.json CEIL.json ARM=run,run,... [ARM=run,...]     (run dirs are looked up in the current folder)

Part 1 is sp2.py unchanged (O1, O2, cost, law record) on the fixed-reference metric.
Part 2 is behaviour, read from log.jsonl only: which model thought each step, the choice made at step 0,
moves up the menu, work done after the first assay, the sense readings, and how many steps logged their reasoning.
"""
import statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sp2  # noqa: E402
from stem_report import ev, PARTS  # noqa: E402

RANK = {"light": 0, "mid": 1, "heavy": 2}


def cell(run, part):
    es = ev(Path(run) / part)
    laws = next((e for e in es if e.get("event") == "laws"), {})
    use = [e for e in es if isinstance(e.get("usage"), dict)]
    acts = [e for e in es if "act" in e and "step" in e]
    models = [e.get("model") for e in use]
    born = (laws.get("start") or [models[0] if models else None])[0]
    first_next = next((e.get("next") for e in acts if e.get("next")), None)
    # first step thought on light, counted in steps (None if never)
    first_light = next((i for i, m in enumerate(models) if m == "light"), None)
    up = any(RANK.get(m, 0) > RANK.get(born, 0) for m in models)
    ia = next((i for i, e in enumerate(es) if e.get("event") == "assay"), None)
    after = es[ia + 1:] if ia is not None else []
    am = [e.get("model") for e in after if isinstance(e.get("usage"), dict)]
    prev = ([e.get("model") for e in es[:ia + 1] if isinstance(e.get("usage"), dict)] or [born])[-1] if ia is not None else born
    climb = sum(RANK.get(b, 0) > RANK.get(a, 0) for a, b in zip([prev] + am, am))  # steps dearer than the step before
    sense = [e for e in es if e.get("event") == "sense"]
    ratios = [e["ratio"] for e in sense if "ratio" in e]
    rest = next((e for e in es if e.get("event") == "rest"), None)
    return {
        "laws": laws, "born": born, "steps": len(use), "models": models,
        "step0_to_light": bool(first_next) and first_next[0] == "light" and born != "light",
        "first_light": first_light, "up": up,
        "assayed": ia is not None,
        "steps_after": sum(isinstance(e.get("usage"), dict) for e in after),
        "rounds_after": sum(e.get("event") in ("variants", "try") for e in after),
        "divides_after": sum(e.get("act", {}).get("do") == "divide" for e in after if "act" in e),
        "up_after": any(RANK.get(e.get("model"), 0) > RANK.get(born, 0) for e in after if isinstance(e.get("usage"), dict)),
        "climb_after": climb,
        "improve": sum(e.get("event") == "improve" for e in es),
        "death": any(e.get("event") == "death" for e in es), "rested": rest is not None,
        "gave": (rest or {}).get("gave", 0.0),
        "sense_first": ratios[0] if ratios else None, "sense_last": ratios[-1] if ratios else None,
        "sense_err": sum("error" in e for e in sense),
        "why": sum(bool(e.get("why")) for e in use), "say": sum(bool(e.get("say")) for e in use),
    }


def med(v):
    v = [x for x in v if x is not None]
    return round(statistics.median(v), 3) if v else None


def behaviour(arms):
    print("\n==== Part 2: behaviour (log.jsonl only)")
    for a, runs in arms.items():
        cs = {(r, p): cell(r, p) for r in runs for p in PARTS}
        v = list(cs.values())
        laws = sorted({(c["laws"].get("price_show"), c["laws"].get("sense_show"), c["laws"].get("sense_dir"), c["born"]) for c in v},
                      key=str)
        n = len(v)
        mods = [m for c in v for m in c["models"]]
        tot = max(len(mods), 1)
        print(f"\n== arm {a}: {n} cells | laws (price_show, sense_show, sense_dir, born): {laws}")
        print(f"  steps {len(mods)} | share light {mods.count('light') / tot:.3f} mid {mods.count('mid') / tot:.3f}"
              f" heavy {mods.count('heavy') / tot:.3f}")
        print(f"  B1 cells choosing light at step 0 (born above light): {sum(c['step0_to_light'] for c in v)} of"
              f" {sum(c['born'] != 'light' for c in v)}")
        print(f"  B2 cells that thought on light by their 4th step: {sum(c['first_light'] is not None and c['first_light'] <= 3 for c in v)}"
              f" | ever: {sum(c['first_light'] is not None for c in v)} | first light step, median {med([c['first_light'] for c in v])}")
        print(f"  B3 cells that ever thought above their birth model: {sum(c['up'] for c in v)}"
              f" | after first assay: {sum(c['up_after'] for c in v)}"
              f" | cells that moved to a dearer model than their previous step after first assay: {sum(c['climb_after'] > 0 for c in v)}")
        ass = [c for c in v if c["assayed"]]
        print(f"  B4 assayed cells {len(ass)} | steps after first assay, median {med([c['steps_after'] for c in ass])}"
              f" mean {statistics.mean([c['steps_after'] for c in ass]) if ass else 0:.2f}"
              f" | variant rounds after first assay, total {sum(c['rounds_after'] for c in ass)}"
              f" | cells with 2 or more rounds {sum(c['rounds_after'] >= 2 for c in ass)}"
              f" | divides {sum(c['divides_after'] for c in ass)}")
        print(f"  B5 improvements {sum(c['improve'] for c in v)} | deaths {sum(c['death'] for c in v)} | rested {sum(c['rested'] for c in v)}"
              f" | energy given away at rest, median {med([c['gave'] for c in v if c['rested']])}")
        print(f"  B6 sense first, median {med([c['sense_first'] for c in v])} | sense last, median {med([c['sense_last'] for c in v])}"
              f" | sense errors {sum(c['sense_err'] for c in v)} | cells with a reading {sum(c['sense_last'] is not None for c in v)}")
        for p in PARTS:
            print(f"     {p:9}" + " ".join(
                f"{r}: {cs[(r, p)]['sense_first']}->{cs[(r, p)]['sense_last']} st {cs[(r, p)]['steps']}"
                f" aft {cs[(r, p)]['steps_after']} rd {cs[(r, p)]['rounds_after']}"
                f" {''.join((m or '?')[0] for m in cs[(r, p)]['models'])} |" for r in runs))
        print(f"  B7 steps with reasoning text logged {sum(c['why'] for c in v)} of {len(mods)} | with reply text {sum(c['say'] for c in v)}")


if __name__ == "__main__":
    A = {}
    for s in sys.argv[3:]:
        k, v = s.split("=")
        A[k] = v.split(",")
    print("==== Part 1: sp2.py unchanged")
    sp2.main(sys.argv[1], sys.argv[2], A)
    behaviour(A)
