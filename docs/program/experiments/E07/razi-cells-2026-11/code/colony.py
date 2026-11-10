"""Run many cells at once and watch the machine.

  python colony.py RUN_DIR needs.json [--par N] [--calls C] [--steps S]

needs.json: [{"name": "...", "need": "..."}]. Each cell is its own process (own router, own shared loop).
Every 2 s we sample RSS and CPU of all cell processes. Writes RUN_DIR/summary.json.
"""
from __future__ import annotations

import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = str(Path.home() / "Work/exo-live/.venv/bin/python")


def sample(pids: set[int]) -> tuple[float, float, int]:
    if not pids:
        return 0.0, 0.0, 0
    out = subprocess.run(["ps", "-o", "pid=,ppid=,rss=,%cpu=", "-A"], capture_output=True, text=True).stdout
    rows = [r.split() for r in out.splitlines() if len(r.split()) == 4]
    kids = {int(r[0]): r for r in rows}
    tree, grew = set(pids), True
    while grew:  # include sandboxed shells and their pythons
        new = {p for p, r in kids.items() if int(r[1]) in tree} - tree
        grew, tree = bool(new), tree | new
    rss = sum(int(kids[p][2]) for p in tree if p in kids) / 1024
    cpu = sum(float(kids[p][3]) for p in tree if p in kids)
    return rss, cpu, len(tree & kids.keys())


def cell_stats(d: Path) -> dict:
    ev = [json.loads(l) for l in (d / "log.jsonl").read_text().splitlines()] if (d / "log.jsonl").exists() else []
    acts = [e.get("act", {}).get("do") for e in ev if "act" in e]
    mit = [e for e in ev if e.get("event") == "try"]  # a split is one `try` (asymmetric mitosis); cell.py never logs "mitosis"
    return {"steps": len(ev), "errors": sum("error" in e for e in ev), "acts": {a: acts.count(a) for a in set(acts)},
            "splits": len(mit), "ties": sum(not m.get("won") for m in mit),
            "bad_replies": sum("bad_reply" in e for e in ev), "assays": sum(e.get("event") == "assay" for e in ev),
            "variants": sum(e.get("event") == "variants" for e in ev),
            "tries": sum(e.get("event") == "try" for e in ev),
            "improvements": sum(e.get("event") == "improve" for e in ev),
            "gain": round(__import__("math").prod(1 + e["gain"] for e in ev if e.get("event") == "improve") - 1, 3),
            "apoptosis": any(e.get("event") == "apoptosis" for e in ev),
            "calls": int((d / ".calls").read_text()) if (d / ".calls").exists() else 0,
            "routes": {r: sum(e.get("route") == r for e in ev) for r in {e.get("route") for e in ev if e.get("route")}},
            "done": (d / "RESULT").exists()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("needs")
    ap.add_argument("--par", type=int, default=8); ap.add_argument("--calls", type=int, default=40)
    ap.add_argument("--steps", type=int, default=14)
    ap.add_argument("--model", default="", help="pin every cell to this model ref unless the need names one")
    a = ap.parse_args()
    run = Path(a.run).expanduser().resolve(); run.mkdir(parents=True, exist_ok=True)
    needs = json.loads(Path(a.needs).read_text())
    live: dict[str, subprocess.Popen] = {}
    samples, t0 = [], time.time()
    env = {**os.environ, "CELL_MAX_CALLS": str(a.calls)}

    def one(n: dict) -> tuple[str, int, float]:
        s = time.time()
        with open(run / f"{n['name']}.out", "w") as fh:
            cenv = {**env, **({"CELL_MODEL": n.get("model") or a.model} if (n.get("model") or a.model) else {})}
            p = subprocess.Popen([PY, str(HERE / "cell.py"), "seed", str(run / n["name"]), n["need"],
                                  "--steps", str(a.steps)], stdout=fh, stderr=subprocess.STDOUT, env=cenv)
            live[n["name"]] = p
            rc = p.wait()
        live.pop(n["name"], None)
        return n["name"], rc, round(time.time() - s, 1)

    with ThreadPoolExecutor(a.par) as ex:
        futs = [ex.submit(one, n) for n in needs]
        while not all(f.done() for f in futs):
            rss, cpu, procs = sample({p.pid for p in list(live.values())})
            samples.append({"t": round(time.time() - t0, 1), "cells": len(live), "procs": procs,
                            "rss_mb": round(rss, 1), "cpu_pct": round(cpu, 1)})
            time.sleep(2)
        results = [f.result() for f in futs]
    cells = {name: {"rc": rc, "secs": secs, **cell_stats(run / name)} for name, rc, secs in results}
    calls = sum(c["calls"] for c in cells.values())
    imps = sum(c["improvements"] for c in cells.values())
    summ = {"calls": calls, "improvements": imps, "imp_per_100_calls": round(100 * imps / max(calls, 1), 2),
            "done": sum(c["done"] for c in cells.values()), "bad_replies": sum(c["bad_replies"] for c in cells.values()),
            "wall_s": round(time.time() - t0, 1), "par": a.par,
            "peak_rss_mb": max((s["rss_mb"] for s in samples), default=0),
            "peak_cpu_pct": max((s["cpu_pct"] for s in samples), default=0),
            "mean_cpu_pct": round(sum(s["cpu_pct"] for s in samples) / max(len(samples), 1), 1),
            "cells": cells}
    (run / "samples.json").write_text(json.dumps(samples))
    (run / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "cells"}))
    for name, c in summ["cells"].items():
        print(name, json.dumps(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
