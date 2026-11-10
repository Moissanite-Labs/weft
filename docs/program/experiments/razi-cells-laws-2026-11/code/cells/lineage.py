"""lineage.py: many generations of metab.py cells with heredity (2026-11-11).

Every colony before this one started from nothing and ended with its cells. Nothing a cell built outlived it
except one line in a library. Here each need has a lineage:

  germline   RUN/.germ/<kit>/body   the best body the lineage has built (code and the memory file).
  store      ledger entry store-<kit>   the lineage's energy. It pays for each birth. A resting cell's unspent
             energy returns to it. A dead cell's energy is lost. Wins mint energy (metab.py law 2).

One generation: each lineage with enough energy gives birth to WIDTH cells. A newborn has the germline body,
already assayed by the harness. Cells live under metab.py's laws with CELL_PAY_ANY=1 (any measured gain over the
last scored body pays). When all cells of the generation have rested or died, the harness measures each lineage's
bodies against its germline body, interleaved. The best one replaces the germline only if it wins beyond noise.

The harness decides nothing about what a cell does. It owns birth, the bench and the germline gate.

  python lineage.py RUN_DIR needs.json --gens G [--width W] [--e0 400] [--store S] [--par 4] [--sense DIR]

Writes RUN/lineage.jsonl (one row per lineage per generation) and RUN/summary.json.
"""
from __future__ import annotations

import argparse, fcntl, json, os, shutil, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("CELL_KIT", "maze")  # metab.py needs one at import; each cell gets its own below
sys.path.insert(0, str(HERE))
import cell as C, metab as M  # noqa: E402

PY = str(Path.home() / "Work/exo-live/.venv/bin/python")
REPEATS = 5
SKIP = ("variants.jsonl",)  # a cell's archive of its own drafts is not part of what it passes on
MIN_BIRTH = 100.0  # below this a newborn could not pay for a first thought on the starting model


def store(kit: str) -> str:
    return "store-" + kit


def jlog(run: Path, **rec) -> None:
    rec["t"] = round(time.time(), 2)
    with open(run / "lineage.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def lib(run: Path, kit: str, line: str) -> None:
    with open(run / "LIBRARY.md", "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(f"- [lineage {kit}] {' '.join(line.split())[:400]}\n")


def take(run: Path, kit: str, want: float) -> float:
    """Birth energy leaves the store. Returns what the newborn gets (0.0: the lineage cannot afford a birth)."""
    def fn(d):
        s = d[store(kit)]
        give = want if s["e"] >= want else (s["e"] if s["e"] >= MIN_BIRTH else 0.0)
        s["e"] -= give
        s["gave"] += give
        return give
    return M.ledger(run / store(kit), fn)


def launch(run: Path, name: str, need: dict, energy: float, a) -> tuple[str, int, float]:
    kit = need["kit"]
    env = {**os.environ, "CELL_KIT": kit, "CELL_GERM": "" if a.blank else str(run / ".germ" / kit), "CELL_PAY_ANY": "1",
           "CELL_LINEAGE": "1", "CELL_HEIR": store(kit), "CELL_E0": str(energy), "CELL_REWARD": str(a.reward),
           "CELL_FUSE": "1e12", "CELL_MAX_CALLS": str(a.calls), "CELL_PRICE_SHOW": "1"}
    if a.sense:
        env.update(CELL_SENSE_DIR=str(Path(a.sense).resolve()), CELL_SENSE_SHOW="1")
    t = time.time()
    with open(run / f"{name}.out", "w") as fh:
        rc = subprocess.run([PY, str(HERE / "metab.py"), "seed", str(run / name), need["need"]],
                            stdout=fh, stderr=subprocess.STDOUT, env=env).returncode
    return name, rc, round(time.time() - t, 1)


def gate(run: Path, kit: str, gen: int, names: list[str]) -> dict:
    """The germline gate: measured by the harness, cells take no part. Same rule as every other win (C.beats)."""
    germ = run / ".germ" / kit / "body"
    dirs = {n: run / n for n in names if any(p.name not in SKIP + ("genome.md",) for p in C.body_files(run / n))}
    has_germ = germ.is_dir() and any(germ.iterdir())
    if has_germ:
        dirs = {"germ": germ, **dirs}
    row = {"gen": gen, "kit": kit, "cells": names, "had_germ": has_germ, "took": None, "gain": None}
    if not [k for k in dirs if k != "germ"]:
        return row
    m = C.measure(dirs, "kit:" + kit, REPEATS)
    med = {k: statistics.median(v) for k, v in m.items()}
    row.update(medians={k: round(v, 6) for k, v in med.items()}, zero=dict(C.LAST_WHY))
    best = max((k for k in med if k != "germ"), key=med.get)
    if has_germ:
        ok, gain = C.beats(m[best], m["germ"], C.spread(m["germ"]))
    else:
        ok, gain = med[best] > 0 and min(m[best]) > 0, 0.0
    row["gain"] = round(gain, 4)
    if ok:
        old = run / ".germ" / kit / f"gen{gen}-replaced"
        if has_germ:
            shutil.move(str(germ), str(old))
        germ.mkdir(parents=True, exist_ok=True)
        for p in C.body_files(run / best):
            if p.name in SKIP:
                continue
            q = germ / p.relative_to(run / best)
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
        row["took"] = best
        lib(run, kit, f"GEN {gen}: the germline body is now the body of {best}" +
            (f", measured {gain:+.0%} over the one before." if has_germ else ", the lineage's first."))
    elif has_germ:
        lib(run, kit, f"GEN {gen}: no body beat the germline beyond noise (best {gain:+.0%}). The germline is unchanged.")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("needs")
    ap.add_argument("--gens", type=int, default=4); ap.add_argument("--width", type=int, default=2)
    ap.add_argument("--e0", type=float, default=400.0, help="energy a newborn takes from the store")
    ap.add_argument("--store", type=float, default=0.0, help="energy each lineage's store starts with (0: gens*width*e0/2)")
    ap.add_argument("--reward", type=float, default=400.0)
    ap.add_argument("--par", type=int, default=4); ap.add_argument("--calls", type=int, default=80)
    ap.add_argument("--blank", action="store_true", help="control: newborns do not inherit the germline body")
    ap.add_argument("--sense", default="", help="folder of record bodies per kit (the SENSE number), optional")
    a = ap.parse_args()
    run = Path(a.run).expanduser().resolve()
    run.mkdir(parents=True, exist_ok=True)
    needs = json.loads(Path(a.needs).read_text())
    s0 = a.store or a.gens * a.width * a.e0 / 2
    for n in needs:
        C.kit.ensure(n["kit"])
        (run / ".germ" / n["kit"]).mkdir(parents=True, exist_ok=True)
        if store(n["kit"]) not in M.ledger(run / store(n["kit"])):
            M.born(run / store(n["kit"]), s0)
    jlog(run, event="start", gens=a.gens, width=a.width, e0=a.e0, store=s0, reward=a.reward, sense=bool(a.sense), blank=a.blank,
         kits=[n["kit"] for n in needs], menu=M.MENU)
    t0 = time.time()
    for g in range(a.gens):
        births = []
        for n in needs:
            for i in range(a.width):
                e = take(run, n["kit"], a.e0)
                if e > 0:
                    births.append((f"g{g}-{n['kit']}-{i}", n, e))
        if not births:
            jlog(run, event="extinct", gen=g)
            break
        with ThreadPoolExecutor(a.par) as ex:
            res = list(ex.map(lambda b: launch(run, b[0], b[1], b[2], a), births))
        led = M.ledger(run / store(needs[0]["kit"]))
        for n in needs:
            names = [b[0] for b in births if b[1]["kit"] == n["kit"]]
            row = gate(run, n["kit"], g, names) if names else {"gen": g, "kit": n["kit"], "cells": []}
            row.update(event="gen", store=round(led[store(n["kit"])]["e"], 1),
                       born=round(sum(b[2] for b in births if b[1]["kit"] == n["kit"]), 1),
                       spent=round(sum(led[c]["spent"] for c in names), 1),
                       earned=round(sum(led[c]["earned"] for c in names), 1),
                       returned=round(sum(led[c]["gave"] for c in names), 1),
                       states={c: led[c]["state"] for c in names}, ages={c: led[c]["age"] for c in names},
                       rc={r[0]: r[1] for r in res if r[0] in names})
            jlog(run, **row)
            print(json.dumps({k: row.get(k) for k in ("gen", "kit", "took", "gain", "store", "spent", "earned", "states")}),
                  flush=True)
    rows = [json.loads(l) for l in (run / "lineage.jsonl").read_text().splitlines()]
    (run / "summary.json").write_text(json.dumps({"wall_s": round(time.time() - t0, 1),
                                                  "ledger": M.ledger(run / store(needs[0]["kit"])),
                                                  "gens": [r for r in rows if r.get("event") == "gen"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
