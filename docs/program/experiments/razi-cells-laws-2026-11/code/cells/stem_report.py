#!/usr/bin/env python3
"""stem_report.py RUN_DIR [RUN_DIR ...]: one table per run, flat (colony.py + metab.py) or stem (stem.py).
Written 2026-11-10 before any stem pilot data. Numbers come from log.jsonl and .ledger.json only."""
import json, statistics, sys
from pathlib import Path

PARTS = ["compress", "fibmod", "csvsum", "maze"]


def ev(d):
    f = d / "log.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []


def tok(es):
    us = [e["usage"] for e in es if isinstance(e.get("usage"), dict)]
    return (len(us), sum((u.get("inp") or 0) + (u.get("out") or 0) + (u.get("cw") or 0) for u in us),
            round(sum(u.get("usd") or 0 for u in us), 4))


def report(run):
    run = Path(run)
    stem = (run / "stem" / "log.jsonl").exists()
    led = json.loads(next(run.glob("**/.ledger.json")).read_text()) if list(run.glob("**/.ledger.json")) else {}
    print(f"== {run.name} ({'stem' if stem else 'flat'})")
    gains, calls, toks, usd, imps = [], 0, 0, 0.0, 0
    for p in PARTS:
        es = ev(run / p)
        if not es:
            print(f"  {p:9s} no cell"); gains.append(0.0); continue
        fin = [e for e in es if e.get("event") == "final" and "final_gain" in e]
        fg = fin[-1]["final_gain"] if fin else None
        gains.append(fg if fg is not None else 0.0)
        c, t, u = tok(es); calls += c; toks += t; usd += u
        im = [e for e in es if e.get("event") == "improve"]; imps += len(im)
        acts = [e["act"].get("do") for e in es if "act" in e]
        rests = sum(a == "rest" for a in acts)
        models = sorted({e["model"] for e in es if "usage" in e})
        l = led.get(p, {})
        print(f"  {p:9s} final_gain {fg}  imps {len(im)}  calls {c}  tokens {t}  usd {u}  rests {rests}  "
              f"divides {acts.count('divide')}  variants {acts.count('variants')}  models {models}  "
              f"state {l.get('state')}  spent {round(l.get('spent', 0), 1)}  earned {round(l.get('earned', 0), 1)}")
    out = {"run": run.name, "arm": "stem" if stem else "flat", "median_final_gain": round(statistics.median(gains), 4),
           "mean_final_gain": round(statistics.mean(gains), 4), "gains": gains, "improvements": imps}
    if stem:
        es = ev(run / "stem")
        c, t, u = tok(es); calls += c; toks += t; usd += u
        feeds = [e for e in es if e.get("event") == "feed"]
        births = [e for e in feeds if e["kind"] == "birth"]
        wakes = [e for e in feeds if e["kind"] == "wake"]
        acts = [e["act"].get("do") for e in es if "act" in e]
        first_wait = next((i for i, e in enumerate(es) if e.get("act", {}).get("do") == "wait"), len(es))
        born_before_wait = len({e["part"] for e in es[:first_wait] if e.get("event") == "feed" and e["kind"] == "birth"})
        after = 0
        for w in wakes:  # adopted improvements in the woken part after this wake
            after += sum(1 for e in ev(run / w["part"]) if e.get("event") == "improve" and e["t"] > w["t"])
        s = led.get("stem", {})
        out.update(stem_steps=c, stem_spent=round(s.get("spent", 0), 1), stem_unspent=round(s.get("e", 0), 1),
                   stem_state=s.get("state"), births=[(e["part"], e["gave"], e.get("model"), e.get("effort")) for e in births],
                   wakes=[(e["part"], e["gave"], e.get("model"), e.get("effort")) for e in wakes],
                   topups=sum(e["kind"] == "top-up" for e in feeds), parts_born_before_first_wait=born_before_wait,
                   improvements_after_wake=after, stem_acts={a: acts.count(a) for a in sorted(set(acts))},
                   notes=[e.get("note", "")[:140] for e in feeds],
                   stem_models=sorted({(e["model"], e["effort"]) for e in es if "usage" in e}))
    born = led.get("stem", {}).get("born") if stem else sum(v.get("born", 0) for k, v in led.items() if "/" not in k)
    spent = sum(v.get("spent", 0) for k, v in led.items() if "/" not in k)
    out.update(calls=calls, tokens=toks, usd=round(usd, 4), energy_born=born, energy_spent=round(spent, 1),
               energy_earned=round(sum(v.get("earned", 0) for v in led.values()), 1),
               bad_replies=sum(1 for p in PARTS + ["stem"] for e in ev(run / p) if "bad_reply" in e),
               errors=sum(1 for p in PARTS + ["stem"] for e in ev(run / p) if "error" in e))
    for k, v in out.items():
        print(f"  {k}: {v}")
    return out


if __name__ == "__main__":
    for r in sys.argv[1:]:
        report(r)
