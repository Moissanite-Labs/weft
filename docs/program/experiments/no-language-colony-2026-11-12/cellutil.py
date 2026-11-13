#!/usr/bin/env python3
"""Shared machinery for the no-language colony: sandbox, scoring, paths.

Extracted from the 2026-11-12 blitz harness, unchanged in behavior.
Leak counting is done by measurement, never by rewriting model code.
"""
import ast
import io
import re
import statistics
import tokenize
import subprocess
import sys
import time
from pathlib import Path

OUT_CAP = 4000
ASSAY_RUNS = 3
SPREAD_MAX = 0.15
WIN_MARGIN = 1.03

CORPUS = Path(__file__).resolve().parent / "corpus_hard.txt"
CORPUS_SHA256 = "00abb98851008a506a270c84646431194f943e80f16d17da3d1b2e5242a9ef76"

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


def inside(cell: Path, rel: str):
    p = (cell / rel).resolve()
    if p.is_relative_to(cell.resolve()) and p.name not in ("NEED", "log.jsonl", "ASSAY.json", "RESULT", "x.bin"):
        return p
    return None


def sandbox_run(cell: Path, cmd: str, timeout: int = 30):
    real = str(cell.resolve())
    tmp = cell / "tmp"
    tmp.mkdir(exist_ok=True)
    prof = (
        '(version 1)(deny default)'
        '(allow file-read*)'
        f'(deny file-read* (subpath "{Path.home()}"))'
        f'(allow file-read* (subpath "{real}"))'
        f'(allow file-write* (subpath "{real}"))'
        '(allow process-exec (subpath "/"))'
        '(allow process-fork)'
        '(deny network*)'
    )
    env = {"PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin", "HOME": real, "TMPDIR": str(tmp), "LANG": "C.UTF-8"}
    t = time.perf_counter()
    try:
        p = subprocess.run(["sandbox-exec", "-p", prof, "/bin/sh", "-c", cmd], cwd=real, env=env,
                           capture_output=True, text=True, timeout=timeout)
        out = f"exit {p.returncode}\n{p.stdout}{p.stderr}"
    except subprocess.TimeoutExpired:
        out = "timeout"
    dt = time.perf_counter() - t
    if len(out) > OUT_CAP:
        out = out[: OUT_CAP // 2] + "\n...\n" + out[-OUT_CAP // 2:]
    return out, dt


def parse_score(out: str):
    nums = NUM_RE.findall(out.split("exit", 1)[-1])
    return float(nums[-1]) if nums else None


def run_assay(cell: Path):
    cmd = (cell / "ASSAY").read_text().strip() if (cell / "ASSAY").exists() else None
    if not cmd:
        return None
    scores = []
    for _ in range(ASSAY_RUNS):
        out, _ = sandbox_run(cell, cmd, timeout=30)
        s = parse_score(out)
        if s is None or out.startswith("exit 0") is False:
            scores.append(None)
        else:
            scores.append(s)
    ok = all(s is not None for s in scores) and scores and all(s > 0 for s in scores)
    med = statistics.median([s for s in scores if s is not None]) if any(s is not None for s in scores) else None
    spread = ((max(scores) - min(scores)) / med) if ok and med else None
    return {"scores": scores, "median": med, "spread": spread, "ok": bool(ok and spread is not None and spread <= SPREAD_MAX)}


def python_leaks(src: str) -> dict:
    """Count blocklist words inside comments and docstrings (measurement only)."""
    from lint import english_hits
    comments, docstrings = [], []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comments.append(tok.string)
    except Exception:
        pass
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                docstrings.append(node.value.value)
    except Exception:
        pass
    cc = [w for c in comments for w in english_hits(c)]
    dd = [w for d in docstrings for w in english_hits(d)]
    return {"comment_hits": len(cc), "docstring_hits": len(dd),
            "comment_words": sorted(set(cc)), "docstring_words": sorted(set(dd))}
