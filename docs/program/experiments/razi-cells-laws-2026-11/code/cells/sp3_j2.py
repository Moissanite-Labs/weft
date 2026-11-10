#!/usr/bin/env python3
"""SP3 readout J2. Written 2026-11-10 before any SP3 arm data. Run unchanged.

  python sp3_j2.py ARM=run,run,... [ARM=...]

Per arm: cells that, after their first assay, thought a step on a dearer model than their previous step,
(a) any act, the S3-j count, and (b) leaving out steps whose act is rest.
"""
import json, sys
from pathlib import Path
RANK = {"light": 0, "mid": 1, "heavy": 2}
PARTS = ("compress", "fibmod", "csvsum", "maze")


def cell(d):
    es = [json.loads(l) for l in open(Path(d) / "log.jsonl")]
    ia = next((i for i, e in enumerate(es) if e.get("event") == "assay"), None)
    if ia is None:
        return 0, 0
    act = {e["step"]: (e.get("act") or {}).get("do") for e in es if "act" in e and "step" in e}
    use = [(i, e) for i, e in enumerate(es) if isinstance(e.get("usage"), dict)]
    prev = ([e.get("model") for i, e in use if i <= ia] or [None])[-1]
    a = b = 0
    for i, e in use:
        if i <= ia:
            continue
        m = e.get("model")
        if prev is not None and RANK.get(m, 0) > RANK.get(prev, 0):
            a += 1
            b += act.get(e.get("step")) != "rest"
        prev = m
    return a, b


for s in sys.argv[1:]:
    k, v = s.split("=")
    r = [cell(Path(run) / p) for run in v.split(",") for p in PARTS if (Path(run) / p / "log.jsonl").exists()]
    print(f"arm {k}: cells {len(r)} | climbed after first assay (S3-j count) {sum(x[0] > 0 for x in r)}"
          f" | climbed, rest steps left out (J2) {sum(x[1] > 0 for x in r)}")
