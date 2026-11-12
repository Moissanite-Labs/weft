#!/usr/bin/env python3
"""Replay the 2026-11-12 archive under the fixed do_variants semantics.

Zero API calls. Each cell's events are re-executed in a scratch copy of the
cell under the same sandbox the harness used, so file state is ground truth,
not a reconstruction: write/assay events are applied, sh events actually run,
and variants events are scored under the fixed selection logic. The replayed
final body is then compared byte-for-byte against the committed cell.

Checkpoints to replay-results.jsonl after every cell.
"""
import hashlib
import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "offline-replay-dummy")
sys.argv = ["harness.py", "offline-model", "offline-cell", "compress"]

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import harness  # noqa: E402

SCRATCH = Path(tempfile.mkdtemp(prefix="replay-2026-11-12-"))
RESULTS = ROOT / "replay-results.jsonl"
TARGET_RE = re.compile(r"^[^/]+\.py$")


def target_name(cell):
    for target in ("compress.py",):
        return target


def run_assay(tmpdir, assay_cmd):
    scores = []
    for _ in range(harness.ASSAY_RUNS):
        out, _ = harness.sandbox_run(Path(tmpdir), assay_cmd, timeout=30)
        s = harness.parse_score(out)
        scores.append(None if (s is None or not out.startswith("exit 0")) else s)
    med = statistics.median([x for x in scores if x is not None]) if any(x is not None for x in scores) else None
    ok = all(x is not None for x in scores) and bool(scores) and all(x > 0 for x in scores)
    if ok and med:
        spread = (max(scores) - min(scores)) / med
        ok = spread <= harness.SPREAD_MAX
    return {"scores": scores, "median": med, "ok": bool(ok)}





def replay_cell(cell: str) -> dict:
    src = ROOT / "cells" / cell
    tmp = SCRATCH / cell
    tmp.mkdir(parents=True, exist_ok=True)
    for name in ("corpus.txt", "corpus_hard.txt"):
        if (src / name).exists():
            shutil.copy(src / name, tmp / name)
    files: dict[str, bytes] = {}
    unknown_paths: set[str] = set()
    sh_writes = 0
    sh_count = 0
    slow_sh = 0
    variants_calls = []
    sum_ok = 0
    hist_pairs = []
    seq = 0
    for line in open(ROOT / "logs" / f"{cell}.jsonl"):
        e = json.loads(line)
        if e["kind"] != "tool_call":
            continue
        name, args = e.get("name"), e.get("args") or {}
        step = e.get("step")
        if name == "write":
            p = str(args.get("path", ""))
            files[p] = str(args.get("content", "")).encode(errors="ignore")
            (tmp / p).parent.mkdir(parents=True, exist_ok=True)
            (tmp / p).write_bytes(files[p])
            unknown_paths.discard(p)
        elif name == "assay":
            cmd = str(args.get("command", ""))
            files["ASSAY"] = cmd.encode()
            (tmp / "ASSAY").write_text(cmd)
        elif name == "sh":
            cmd = str(args.get("command", ""))
            out, _dt = harness.sandbox_run(tmp, cmd, timeout=30)
            sh_count += 1
            if _dt > 25:
                slow_sh += 1
            # re-sync everything we may know about from disk
            for p in list(files):
                q = tmp / p
                if q.exists():
                    try:
                        files[p] = q.read_bytes()[:5_000_000]
                    except OSError:
                        files.pop(p, None)
                else:
                    files.pop(p, None)
                    unknown_paths.add(p)
            before = set(files)
            for q in tmp.rglob("*.py"):
                if q.is_file() and q.stat().st_size < 5_000_000:
                    rel = str(q.relative_to(tmp))
                    files[rel] = q.read_bytes()
            if set(files) - before:
                sh_writes += 1
        elif name == "variants":
            path = str(args.get("path", ""))
            versions = [str(v) for v in (args.get("versions") or [])]
            assay_cmd = files.get("ASSAY")
            rec = {"step": step, "n_versions": len(versions), "sh_writes_so_far": sh_writes}
            if assay_cmd is None:
                rec["outcome"] = "no-assay-registered"
                variants_calls.append(rec)
                continue
            if path in unknown_paths:
                rec["outcome"] = "incumbent-unknown"
                variants_calls.append(rec)
                continue
            inc = files.get(path)
            rec["inc_existed"] = inc is not None
            if inc is not None:
                (tmp / path).write_bytes(inc)
            inc_res = run_assay(tmp, assay_cmd.decode())
            inc_med = inc_res["median"] if inc_res["ok"] else None
            rec["inc_median"] = inc_med
            if inc_med is None:
                rec["outcome"] = "incumbent-not-ok"
                variants_calls.append(rec)
                # historical behavior: no candidates written by harness; files unchanged
                continue
            best_i, best_med, best_min = None, inc_med, None
            survivors = []
            for i, v in enumerate(versions):
                (tmp / path).write_text(v)
                r = run_assay(tmp, assay_cmd.decode())
                s = r["scores"]
                ok = r["ok"]
                med = statistics.median([x for x in s if x is not None]) if any(x is not None for x in s) else None
                mn = min([x for x in s if x is not None]) if any(x is not None for x in s) else None
                rec.setdefault("candidates", []).append(
                    {"i": i, "scores": s, "median": med, "min": mn, "ok": ok,
                     "sha256": hashlib.sha256(v.encode()).hexdigest()})
                if not ok:
                    survivors.append(None)
                    continue
                if med > best_med * harness.WIN_MARGIN and mn >= inc_med * 0.97:
                    best_i, best_med, best_min = i, med, mn
                survivors.append(i if i == best_i else None)
            if best_i is None:
                if inc is not None:
                    (tmp / path).write_bytes(inc)
                    files[path] = inc
                elif (tmp / path).exists():
                    (tmp / path).unlink()
                    files.pop(path, None)
                rec["replayed_outcome"] = "no-win"
            else:
                winner = versions[best_i]
                (tmp / path).write_text(winner)
                files[path] = winner.encode()
                after = run_assay(tmp, assay_cmd.decode())
                rec["replayed_outcome"] = "adopt"
                rec["replayed_winner"] = best_i
                rec["replayed_winner_median"] = best_med
                rec["replayed_after_median"] = after["median"]
                rec["replayed_winner_sha256"] = hashlib.sha256(winner.encode()).hexdigest()
            variants_calls.append(rec)
    # save the replayed final body for post-hoc checks (round-trip, compile)
    outdir = ROOT / "replay-final" / cell
    outdir.mkdir(parents=True, exist_ok=True)
    for q in tmp.rglob("*"):
        if q.is_file() and q.stat().st_size < 5_000_000:
            rel = q.relative_to(tmp)
            if str(rel).startswith(("tmp/", "__pycache__/")):
                continue
            if rel.name in ("out.bin", "restored.txt", "out.json", "r.bin"):
                continue
            (outdir / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(q, outdir / rel)
    # anchor: replayed final bytes vs committed final bytes; None means unknown
    anchor = None
    tgt = target_name(cell)
    if tgt in unknown_paths:
        anchor = None
    elif tgt in files and (src / tgt).exists():
        anchor = files[tgt] == (src / tgt).read_bytes()
    elif (src / tgt).exists():
        anchor = None
    return {"cell": cell, "variants_calls": variants_calls,
            "anchor_exact": anchor,
            "sh_writes": sh_writes,
            "sh_count": sh_count,
            "slow_sh": slow_sh,
            "unknown_paths_final": sorted(unknown_paths)}


def main():
    import glob as _glob
    cells = sorted(os.path.basename(os.path.dirname(f)) for f in _glob.glob("cells/*/ASSAY"))
    already = set()
    if RESULTS.exists():
        for line in open(RESULTS):
            already.add(json.loads(line)["cell"])
    for cell in cells:
        if cell in already:
            continue
        t0 = time.time()
        try:
            res = replay_cell(cell)
        except Exception as ex:
            res = {"cell": cell, "error": f"{type(ex).__name__}: {ex}"}
        res["elapsed_s"] = round(time.time() - t0, 1)
        with open(RESULTS, "a") as f:
            f.write(json.dumps(res) + "\n")
        o = res.get("replayed_outcome")
        print(f"{cell:22} {res.get('elapsed_s')}s calls={len(res.get('variants_calls', []))} "
              f"anchor={res.get('anchor_exact')} shw={res.get('sh_writes_suspected')} "
              f"err={res.get('error', '')}", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
