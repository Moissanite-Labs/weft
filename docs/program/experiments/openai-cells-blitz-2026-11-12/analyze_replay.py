#!/usr/bin/env python3
"""Aggregate the fixed-action offline replay of the 2026-11-12 archive.

Joins each replayed variants call to its historical counterpart on the
(cell, step) of the `variants` tool_call. Each historical record holds that
call's terminal tool_result plus the nested `variant` and `variants_result`
events logged between the call and its result. A historical call that ended in
a rejection (no assay registered, or the current body scored 0) has a
tool_result and no `variants_result`; it is kept and labelled `rejected`, not
dropped. Unmatched calls on either side are counted, not discarded.

Reports: the join, outcome transitions, candidate-score reproduction (only for
calls the historical run actually scored; candidates of historically rejected
calls are counted as newly evaluated), anchor status, and a round-trip check of
the replayed final bodies.

The replay re-executes the historical model commands in order. It does not
re-ask any model, so after a call whose feedback would have differed, later
commands are still the historical ones. Read the outcomes as a fixed-action
offline replay, not as what a live model would have done.
"""
import collections
import glob
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "offline-analysis-dummy")
sys.argv = ["harness.py", "offline-model", "offline-cell", "compress"]
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402

REJECTION = "variants: register a valid assay first"


def _local_run(cell, cmd, timeout=30):
    """Round-trip runner where macOS sandbox-exec is absent: a local shell in
    the scratch folder, network removed with `unshare -rn` when available."""
    argv = ["/bin/sh", "-c", cmd]
    if shutil.which("unshare"):
        argv = ["unshare", "-rn"] + argv
    try:
        p = subprocess.run(argv, cwd=str(cell), capture_output=True, text=True, timeout=timeout)
        return f"exit {p.returncode}\n{p.stdout}{p.stderr}", 0.0
    except subprocess.TimeoutExpired:
        return "timeout", 0.0


if shutil.which("sandbox-exec"):
    RUN, RUNNER = harness.sandbox_run, "sandbox-exec"
else:
    RUN, RUNNER = _local_run, "local-subprocess" + (" (unshare -rn)" if shutil.which("unshare") else "")


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


def wave_of(cell):
    if cell.startswith("astra-abl"):
        return "E19b"
    if cell.startswith("astra-max"):
        return "E19a"
    if "-l-" in cell:
        return "E18b"
    if cell.startswith("astra-r-"):
        return "E18c"
    if cell.startswith("gpt_61_terra-r-"):
        return "E18e"
    if cell.startswith("gpt_55-r-"):
        return "E18f"
    if "-hard-" in cell:
        return "E18a"
    return "blitz"


def historical_calls(cell, events):
    """One record per historical `variants` tool_call, keyed by (cell, step).

    `events` is the cell's log as a list of dicts, in log order. Returns
    (records, problems): records maps (cell, step) to a dict holding the
    call's candidates, its variants_result (or None) and its tool_result
    (or None); problems counts events that could not be attached.
    """
    records = {}
    problems = collections.Counter()
    cur = None
    for e in events:
        kind = e.get("kind")
        if kind == "tool_call":
            if cur is not None:
                problems["call_without_result"] += 1
                cur = None
            if e.get("name") == "variants":
                key = (cell, e.get("step"))
                if key in records:
                    problems["duplicate_key"] += 1
                    continue
                cur = {"cell": cell, "step": e.get("step"), "candidates": [],
                       "variants_result": None, "tool_result": None}
                records[key] = cur
        elif kind == "variant":
            if cur is None:
                problems["orphan_variant"] += 1
            else:
                cur["candidates"].append(e)
        elif kind == "variants_result":
            if cur is None:
                problems["orphan_variants_result"] += 1
            elif cur["variants_result"] is not None:
                problems["second_variants_result"] += 1
            else:
                cur["variants_result"] = e
        elif kind == "tool_result" and cur is not None:
            if e.get("name") == "variants" and e.get("step") == cur["step"]:
                cur["tool_result"] = e.get("result")
            else:
                problems["mismatched_tool_result"] += 1
            cur = None
    if cur is not None:
        problems["call_without_result"] += 1
    return records, problems


def hist_outcome(rec):
    vr = rec["variants_result"]
    if vr is not None:
        return "adopt" if vr.get("adopted") is not None else "no-win"
    tr = rec["tool_result"]
    if tr is None:
        return "no-result"
    return "rejected" if tr.startswith(REJECTION) else "other-result"


def rep_outcome(rp):
    return rp.get("replayed_outcome", rp.get("outcome"))


def _close(a, b):
    return a == b or (a is not None and b is not None
                      and abs(a - b) <= max(1e-6, 1e-4 * abs(a)))


def compare_candidates(h_cands, r_cands):
    """Per-index comparison of one call's candidate scores."""
    out = collections.Counter()
    by_i = {int(c.get("index")): c for c in h_cands}
    for rc in r_cands:
        hc = by_i.get(int(rc["i"]))
        if hc is None:
            out["missing"] += 1
            continue
        hs, rs = hc.get("scores"), rc.get("scores")
        if hs is None or rs is None:
            out["missing"] += 1
        elif len(hs) == len(rs) and all(_close(a, b) for a, b in zip(hs, rs)):
            out["exact"] += 1
        else:
            out["drift"] += 1
    return out


def join_cell(cell, events, replay_calls):
    """Join historical and replayed variants calls of one cell on (cell, step)."""
    hist, problems = historical_calls(cell, events)
    rep = {}
    for rp in replay_calls:
        key = (cell, rp.get("step"))
        if key in rep:
            problems["duplicate_replay_key"] += 1
            continue
        rep[key] = rp
    pairs = []
    repro = collections.Counter()
    for key in sorted(set(hist) | set(rep), key=lambda k: (k[1] is None, k[1])):
        h, rp = hist.get(key), rep.get(key)
        rec = {"cell": cell, "step": key[1],
               "hist_outcome": hist_outcome(h) if h else None,
               "rep_outcome": rep_outcome(rp) if rp else None}
        if h is None or rp is None:
            rec["match"] = "replay-only" if h is None else "historical-only"
            pairs.append(rec)
            continue
        rec["match"] = "matched"
        vr = h["variants_result"] or {}
        rec["hist_adopted"] = vr.get("adopted")
        rec["hist_median"] = vr.get("median")
        rec["hist_result"] = (h["tool_result"] or "")[:120]
        rec["rep_winner"] = rp.get("replayed_winner")
        rec["rep_winner_median"] = rp.get("replayed_winner_median")
        rec["rep_after_median"] = rp.get("replayed_after_median")
        rec["inc_rep"] = rp.get("inc_median")
        r_cands = rp.get("candidates", [])
        rec["rep_scores"] = [c.get("scores") for c in r_cands]
        if h["candidates"]:
            c = compare_candidates(h["candidates"], r_cands)
            repro.update(c)
            rec["candidates"] = "reproduced"
        else:
            repro["newly_evaluated"] += len(r_cands)
            rec["candidates"] = "newly-evaluated" if r_cands else "none"
        pairs.append(rec)
    # does a replayed adoption still hold the incumbent at the next variants call?
    matched = [p for p in pairs if p["rep_outcome"] is not None]
    for i, p in enumerate(matched):
        if p["rep_outcome"] != "adopt":
            continue
        nxt = matched[i + 1] if i + 1 < len(matched) else None
        if nxt is None or nxt.get("inc_rep") is None:
            p["next_call_incumbent"] = "no-later-call"
        elif _close(nxt["inc_rep"], p["rep_after_median"]):
            p["next_call_incumbent"] = "same-median"
        else:
            p["next_call_incumbent"] = "different-median"
    return {"cell": cell, "pairs": pairs, "repro": dict(repro),
            "problems": dict(problems)}


def load_events(cell):
    with open(ROOT / "logs" / f"{cell}.jsonl") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def summarize(joined):
    pairs = [p for j in joined for p in j["pairs"]]
    matched = [p for p in pairs if p["match"] == "matched"]
    hist_adopts = [p for p in matched if p["hist_outcome"] == "adopt"]
    rep_adopts = [p for p in matched if p["rep_outcome"] == "adopt"]
    trans = collections.Counter(f"{p['hist_outcome']}->{p['rep_outcome']}" for p in matched)
    repro = collections.Counter()
    problems = collections.Counter()
    for j in joined:
        repro.update(j["repro"])
        problems.update(j["problems"])
    by_wave_hist = collections.Counter(wave_of(p["cell"]) for p in hist_adopts)
    by_wave_rep = collections.Counter(wave_of(p["cell"]) for p in rep_adopts)
    return {
        "cells": len(joined),
        "join_key": "(cell, step) of the variants tool_call",
        "historical_variants_calls": sum(1 for p in pairs if p["hist_outcome"] is not None),
        "replay_variants_calls": sum(1 for p in pairs if p["rep_outcome"] is not None),
        "matched_calls": len(matched),
        "unmatched_historical_calls": sum(1 for p in pairs if p["match"] == "historical-only"),
        "unmatched_replay_calls": sum(1 for p in pairs if p["match"] == "replay-only"),
        "historical_outcomes": dict(collections.Counter(p["hist_outcome"] for p in matched)),
        "historical_rejections": sum(1 for p in matched if p["hist_outcome"] == "rejected"),
        "historical_scored_calls": sum(1 for p in matched if p["hist_outcome"] in ("adopt", "no-win")),
        "replay_outcomes": dict(collections.Counter(p["rep_outcome"] for p in matched)),
        "outcome_transitions": dict(sorted(trans.items())),
        "historical_adoptions": len(hist_adopts),
        "replay_same_winner": sum(1 for p in hist_adopts if p["rep_outcome"] == "adopt"
                                  and p["rep_winner"] == p["hist_adopted"]),
        "replay_different_winner": sum(1 for p in hist_adopts if p["rep_outcome"] == "adopt"
                                       and p["rep_winner"] != p["hist_adopted"]),
        "replay_would_not_adopt": sum(1 for p in hist_adopts if p["rep_outcome"] != "adopt"),
        "replay_adoptions": len(rep_adopts),
        "replay_adoptions_from_historical_rejection": [
            f"{p['cell']} step {p['step']}" for p in rep_adopts if p["hist_outcome"] == "rejected"],
        "replay_adoptions_after_median_equals_winner_median": sum(
            1 for p in rep_adopts if _close(p["rep_after_median"], p["rep_winner_median"])),
        "replay_adoption_vs_next_call_incumbent": dict(collections.Counter(
            p.get("next_call_incumbent") for p in rep_adopts)),
        "replay_adoptions_not_incumbent_at_next_call": [
            f"{p['cell']} step {p['step']}" for p in rep_adopts
            if p.get("next_call_incumbent") == "different-median"],
        "historical_adoptions_by_wave": dict(sorted(by_wave_hist.items())),
        "replay_adoptions_by_wave": dict(sorted(by_wave_rep.items())),
        "candidate_evals_reproduced_exact": repro["exact"],
        "candidate_evals_drifted": repro["drift"],
        "candidate_evals_missing": repro["missing"],
        "candidate_evals_reproduced_total": repro["exact"] + repro["drift"] + repro["missing"],
        "candidate_evals_newly_evaluated": repro["newly_evaluated"],
        "log_attachment_problems": dict(problems),
    }


def roundtrip_final(cell):
    d = ROOT / "replay-final" / cell
    src = ROOT / "cells" / cell
    if not (d / "compress.py").exists():
        return "missing"
    # Corpora are not duplicated into the committed cell folders; the task's
    # corpus name comes from the cell's NEED, the bytes from the registered root
    # copy when the cell folder has none.
    need = (src / "NEED").read_text() if (src / "NEED").exists() else ""
    corpus = "corpus_hard.txt" if "corpus_hard.txt" in need else "corpus.txt"
    corpus_src = src / corpus if (src / corpus).exists() else ROOT / corpus
    if not corpus_src.exists():
        return "no-corpus"
    tmp = Path(tempfile.mkdtemp(prefix="rt-"))
    try:
        shutil.copytree(d, tmp, dirs_exist_ok=True)
        shutil.copy(corpus_src, tmp / corpus)
        cmd = ("python3 -B compress.py {c} out.bin && python3 -B compress.py --decompress out.bin r.bin && "
               "cmp {c} r.bin && echo RT-OK").format(c=corpus)
        out, _ = RUN(tmp, cmd, timeout=90)
        return "ok" if out.startswith("exit 0") else "ROUNDTRIP-FAIL"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    results = [json.loads(l) for l in open(ROOT / "replay-results.jsonl")]
    joined = [join_cell(r["cell"], load_events(r["cell"]), r.get("variants_calls", []))
              for r in results]
    summary = summarize(joined)
    by_cell = {r["cell"]: r for r in results}
    rt = {r["cell"]: roundtrip_final(r["cell"]) for r in results if not r.get("error")}
    rt_ok = sum(1 for v in rt.values() if v == "ok")
    anchors = collections.Counter(str(r.get("anchor_exact")) for r in results)
    summary.update({
        "anchor_true": anchors["True"], "anchor_false": anchors["False"],
        "anchor_none": anchors["None"],
        "roundtrip_ok": rt_ok, "roundtrip_total": len(rt),
        "roundtrip_runner": RUNNER,
        "errors": [r["cell"] for r in results if r.get("error")],
    })
    print(json.dumps(summary, indent=2))
    per_cell = []
    for j in joined:
        r = by_cell[j["cell"]]
        per_cell.append({**j, "anchor": r.get("anchor_exact"), "error": r.get("error"),
                         "sh_count": r.get("sh_count"), "elapsed_s": r.get("elapsed_s")})
    with open(ROOT / "replay-analysis.json", "w") as f:
        json.dump({"summary": summary, "per_cell": per_cell, "roundtrip": rt}, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
