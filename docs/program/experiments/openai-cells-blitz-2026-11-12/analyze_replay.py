#!/usr/bin/env python3
"""Aggregate the replay of the 2026-11-12 archive against the historical logs.

Pairs replayed variants calls with the historical ones (same order per cell)
and reports: reproduction, fixed-semantics outcomes, anchor status, and a
round-trip check of the replayed final bodies in a sandbox.
"""
import glob
import json
import os
import random
import shutil
import statistics
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "offline-analysis-dummy")
sys.argv = ["harness.py", "offline-model", "offline-cell", "compress"]
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402


def model_of(cell):
    base = cell.split("-retry")[0]
    table = {"astra": "gpt-6-astra", "sol": "gpt-6-sol", "luna": "gpt-6-luna",
             "gpt_6_astra": "gpt-6-astra", "gpt_6_sol": "gpt-6-sol",
             "gpt_61_terra": "gpt-6.1-terra", "gpt_55": "gpt-5.5",
             "gpt_54_mini": "gpt-5.4-mini", "gpt_54": "gpt-5.4"}
    for k, v in sorted(table.items(), key=lambda kv: -len(kv[0])):
        if cell == k or cell.startswith(k + "-"):
            return v
    return cell.split("-")[0]


def recs_from_logs(cell):
    out = []
    for line in open(ROOT / "logs" / f"{cell}.jsonl"):
        e = json.loads(line)
        if e["kind"] == "variant":
            out.append(("variant", e))
        elif e["kind"] == "variants_result":
            out.append(("result", e))
    return out


def analyze_cell(r):
    cell = r["cell"]
    hist = recs_from_logs(cell)
    h_variants = [e for k, e in hist if k == "variant"]
    h_results = [e for k, e in hist if k == "result"]
    rep = r.get("variants_calls", [])
    n = min(len(h_results), len(rep))
    paired = []
    for i in range(n):
        h = h_results[i]
        rp = rep[i]
        paired.append({
            "cell": cell, "step": h.get("step"),
            "hist_adopted": h.get("adopted"),
            "rep_outcome": rp.get("replayed_outcome", rp.get("outcome")),
            "rep_winner": rp.get("replayed_winner"),
            "inc_rep": rp.get("inc_median"),
            "n_candidates_rep": len(rp.get("candidates", [])),
            "rep_scores": [c.get("scores") for c in rp.get("candidates", [])],
        })
    # reproduction of candidate scores
    # historical variant events are in the same order the harness logged them:
    # per variants call, candidates were logged in index order. Reconstruct the same
    # grouping from the flat list by matching counts per call.
    repro = {"total": 0, "exact": 0, "drift": 0, "missing": 0}
    idx = 0
    for rp in rep:
        m = len(rp.get("candidates", []))
        for j in range(m):
            if idx < len(h_variants):
                hs, rs = h_variants[idx].get("scores"), rp["candidates"][j]["scores"]
                if hs is None or rs is None:
                    repro["missing"] += 1
                elif len(hs) == len(rs) and all(
                        (a is None) == (b is None) or a is None
                        for a, b in zip(hs, rs)):
                    ok = all(a == b or (a is not None and b is not None and abs(a - b) <= max(1e-6, 1e-4 * abs(a)))
                             for a, b in zip(hs, rs))
                    repro["exact" if ok else "drift"] += 1
                else:
                    repro["drift"] += 1
                repro["total"] += 1
                idx += 1
    return {"cell": cell, "paired": paired, "repro": repro,
            "anchor": r.get("anchor_exact"), "error": r.get("error"),
            "sh_count": r.get("sh_count"), "elapsed_s": r.get("elapsed_s")}


def roundtrip_final(cell):
    d = ROOT / "replay-final" / cell
    src = ROOT / "cells" / cell
    if not (d / "compress.py").exists():
        return "missing"
    corpus = "corpus_hard.txt" if (src / "corpus_hard.txt").exists() else ("corpus.txt" if (src / "corpus.txt").exists() else None)
    if corpus is None:
        return "no-corpus"
    tmp = Path(tempfile.mkdtemp(prefix="rt-"))
    try:
        shutil.copytree(d, tmp, dirs_exist_ok=True)
        shutil.copy(src / corpus, tmp / corpus)
        cmd = ("python3 -B compress.py {c} out.bin && python3 -B compress.py --decompress out.bin r.bin && "
               "cmp {c} r.bin && echo RT-OK").format(c=corpus)
        out, _ = harness.sandbox_run(tmp, cmd, timeout=90)
        return "ok" if out.startswith("exit 0") else "ROUNDTRIP-FAIL"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    results = [json.loads(l) for l in open(ROOT / "replay-results.jsonl")]
    analyses = [analyze_cell(r) for r in results]
    paired = [p for a in analyses for p in a["paired"]]
    adopted = [p for p in paired if p["hist_adopted"] is not None]
    same = [p for p in adopted if p["rep_outcome"] == "adopt" and p["rep_winner"] == p["hist_adopted"]]
    diff_winner = [p for p in adopted if p["rep_outcome"] == "adopt" and p["rep_winner"] != p["hist_adopted"]]
    no_adopt = [p for p in adopted if p["rep_outcome"] != "adopt"]
    replay_adopts = [p for p in paired if p["rep_outcome"] == "adopt"]
    rt = {a["cell"]: roundtrip_final(a["cell"]) for a in analyses if not a.get("error")}
    rt_ok = sum(1 for v in rt.values() if v not in ("ROUNDTRIP-FAIL", "missing", "no-corpus"))
    anchors = {"True": 0, "False": 0, "None": 0}
    for a in analyses:
        anchors[str(a["anchor"] if a["anchor"] is not None else "None")] += 1
    repro_tot = sum(a["repro"]["total"] for a in analyses)
    repro_ex = sum(a["repro"]["exact"] for a in analyses)
    repro_dr = sum(a["repro"]["drift"] for a in analyses)
    repro_mi = sum(a["repro"]["missing"] for a in analyses)
    out = {
        "cells": len(analyses),
        "paired_variants_calls": len(paired),
        "historical_adoptions": len(adopted),
        "replay_same_winner": len(same),
        "replay_different_winner": len(diff_winner),
        "replay_would_not_adopt": len(no_adopt),
        "replay_total_adoptions_fixed_semantics": len(replay_adopts),
        "anchor_true": anchors["True"], "anchor_false": anchors["False"], "anchor_none": anchors["None"],
        "candidate_evals_reproduced_exact": repro_ex,
        "candidate_evals_drifted": repro_dr,
        "candidate_evals_missing": repro_mi,
        "candidate_evals_total": repro_tot,
        "roundtrip_ok": rt_ok, "roundtrip_total": len(rt),
        "errors": [a["cell"] for a in analyses if a.get("error")],
    }
    print(json.dumps(out, indent=2))
    with open(ROOT / "replay-analysis.json", "w") as f:
        json.dump({"summary": out,
                   "per_cell": analyses,
                   "roundtrip": rt}, f, indent=1)


if __name__ == "__main__":
    main()
