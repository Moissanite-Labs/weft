"""E13 second look (NOT preregistered): voluntary vs forced improvement attempts, by task, with and without compress.
An attempt is a `variants` or `try` event in a root cell's log. It is forced if a `hold` event came before it
in the same cell, else voluntary. Won = adopted (variants) or won (try). Also: what each daughter did first."""
import json, sys, collections
from pathlib import Path
E = Path(__file__).resolve().parents[2] / "razi-cells" / "exp" if len(sys.argv) < 2 else Path(sys.argv[1])
TASKS = ["compress", "fibmod", "csvsum", "maze"]
def ev(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
for exp in ("e13", "e12"):
    tab = collections.Counter(); dau = collections.Counter()
    for arm in ("c", "n", "ch", "nh"):
        for r in range(1, 5):
            for t in TASKS:
                cell = E / f"{exp}{arm}{r}" / t
                held = False
                for e in ev(cell / "log.jsonl"):
                    if e.get("event") == "hold":
                        held = True
                    elif e.get("event") in ("variants", "try"):
                        won = bool(e.get("adopted") if e["event"] == "variants" else e.get("won"))
                        tab[(arm, t, "forced" if held else "voluntary", "won" if won else "lost")] += 1
                for d in sorted((cell / ".lineage").glob("*")) if (cell / ".lineage").exists() else []:
                    acts = [(e["act"].get("do"), str(e.get("res", ""))) for e in ev(d / "log.jsonl") if isinstance(e.get("act"), dict)]
                    first = acts[0] if acts else ("none", "")
                    refused = first[0] == "try" and first[1].startswith("refused")
                    wrote = any(a in ("write", "variants") for a, _ in acts)
                    dau[(arm, t, "first act try, refused" if refused else "first act " + str(first[0]), "wrote code" if wrote else "wrote nothing", d.name.split("-")[1])] += 1
    print(f"== {exp} attempts (arm, kind): won/lost, all tasks | without compress")
    for arm in ("c", "n", "ch", "nh"):
        for kind in ("voluntary", "forced"):
            w = sum(v for (a, t, k, o), v in tab.items() if a == arm and k == kind and o == "won")
            l = sum(v for (a, t, k, o), v in tab.items() if a == arm and k == kind and o == "lost")
            w2 = sum(v for (a, t, k, o), v in tab.items() if a == arm and k == kind and o == "won" and t != "compress")
            l2 = sum(v for (a, t, k, o), v in tab.items() if a == arm and k == kind and o == "lost" and t != "compress")
            if w + l:
                print(f"{arm:3} {kind:9} {w}/{l} | {w2}/{l2}")
    for kind in ("voluntary", "forced"):
        for nocomp in (False, True):
            w = sum(v for (a, t, k, o), v in tab.items() if k == kind and o == "won" and not (nocomp and t == "compress"))
            l = sum(v for (a, t, k, o), v in tab.items() if k == kind and o == "lost" and not (nocomp and t == "compress"))
            print(f"ALL {kind:9} {'no compress' if nocomp else 'all tasks  '} won {w} lost {l} share {w / max(w + l, 1):.3f}")
    print(f"== {exp} by task (kind, outcome)")
    for t in TASKS:
        print(t, {f"{a}/{k}/{o}": v for (a, tt, k, o), v in sorted(tab.items()) if tt == t})
    print(f"== {exp} daughters")
    for k, v in sorted(dau.items()):
        print(v, k)
