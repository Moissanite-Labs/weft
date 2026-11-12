#!/usr/bin/env python3
"""No-language colony harness. Profiles E1/E2/E3; E4 has its own runner.

Usage: PROFILE=E2 python3 harness_nl.py MODEL CELL [compress]
       MOCK=good python3 harness_nl.py E2 mockcell-1

Channels are English-free by construction (profiles.py + lint.py).
Body file is f.py; corpus is x.bin. Identical mechanics to the 2026-11-12
blitz (fixed do_variants semantics), profile-parameterized surfaces.
"""
import hashlib
import json
import os
import re
import statistics
import sys
import time
import urllib.request
import urllib.error
import ssl
import certifi
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cellutil import inside, sandbox_run, parse_score, run_assay, python_leaks, OUT_CAP, SPREAD_MAX, WIN_MARGIN, ASSAY_RUNS
from profiles import PROFILES, tools_common
from lint import assert_clean

STRICT = os.environ.get("NOL_STRICT") == "1"
if STRICT:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "zero-lexicon-cells-2026-11-12"))
    try:
        from strict_tools import strict_body
    except Exception as _e:
        print(f"strict mode disabled: {_e}", file=_sys.stderr)
        STRICT = False

ROOT = Path(__file__).resolve().parent
CELLS = ROOT / "cells"
LOGS = ROOT / "logs"
API = "https://api.openai.com/v1/responses"
KEY = os.environ.get("OPENAI_API_KEY")

PROFILE = os.environ.get("PROFILE", "E2")
if PROFILE not in PROFILES:
    sys.exit(f"unknown profile {PROFILE}; want one of {sorted(PROFILES)}")
TARGET_NAME = sys.argv[1] if len(sys.argv) > 1 else None
TARGET_CELL = sys.argv[2] if len(sys.argv) > 2 else None
MOCK = os.environ.get("MOCK")
if not TARGET_NAME or not TARGET_CELL:
    sys.exit("usage: harness_nl.py MODEL CELL")

MAX_STEPS = int(os.environ.get("NOL_MAX_STEPS", "15"))
CELL_WALL_S = 12 * 60
GLOBAL_IN_TOK = 8_000_000
GLOBAL_OUT_TOK = 2_500_000
MAX_OUTPUT_TOKENS = int(os.environ.get("NOL_MAX_OUTPUT_TOKENS", "4096"))

CHANNEL = PROFILES[PROFILE]
SYSTEM = CHANNEL["system"]
assert_clean(SYSTEM, f"{PROFILE}.system")
RESULTS = CHANNEL["results"]
for k, v in RESULTS.items():
    if isinstance(v, str):
        assert_clean(v.format(**{f: 1.0 for f in ("Δ*", "Δ₀", "Δ", "σ")}), f"{PROFILE}.results.{k}")
USAGE = {"input_tokens": 0, "output_tokens": 0}


def do_variants(cell: Path, log, path: str, versions: list[str]) -> str:
    p = inside(cell, path)
    if p is None:
        return "!p"
    inc = p.read_text() if p.exists() else None
    inc_hash = hashlib.sha256(inc.encode()).hexdigest() if inc is not None else None
    inc_res = run_assay(cell)
    inc_med = inc_res["median"] if inc_res and inc_res["ok"] else None
    if inc_med is None:
        return RESULTS["reg_assay_first"]
    best_i, best_med, best_min = None, inc_med, None
    for i, v in enumerate(versions):
        p.write_text(v)
        r = run_assay(cell)
        if r is None or not r["ok"]:
            log("variant", {"i": i, "scores": r["scores"] if r else None, "ok": False})
            continue
        s = r["scores"]
        med = statistics.median(s)
        mn = min(s)
        log("variant", {"i": i, "scores": s, "median": med, "min": mn, "ok": True})
        if med > best_med * WIN_MARGIN and mn >= inc_med * 0.97:
            best_i, best_med, best_min = i, med, mn
    if best_i is None:
        if inc is not None:
            p.write_text(inc)
        elif p.exists():
            p.unlink()
        log("variants_result", {"adopted": None, "incumbent_median": inc_med, "incumbent_sha256": inc_hash})
        return RESULTS["variants_no"]
    p.write_text(versions[best_i])
    after = run_assay(cell)
    winner_hash = hashlib.sha256(versions[best_i].encode()).hexdigest()
    log("variants_result", {"adopted": best_i, "median": best_med,
                            "content_sha256": winner_hash,
                            "incumbent_sha256": inc_hash,
                            "before_median": inc_med,
                            "after_scores": after["scores"] if after else None,
                            "after_median": after["median"] if after else None,
                            "after_ok": bool(after and after["ok"])})
    return RESULTS["variants_ok"].format(**{"Δ*": best_med, "Δ₀": inc_med})


def do_assay(cell: Path, log, command: str) -> str:
    (cell / "ASSAY").write_text(command)
    r = run_assay(cell)
    log("assay", {"command": command, **{k: v for k, v in r.items()}})
    if not r["ok"]:
        return RESULTS["assay_no"]
    return RESULTS["assay_ok"].format(**{"Δ": r["median"], "σ": (r["spread"] or 0)})


def tool_dispatch(cell: Path, log, name: str, args: dict) -> str:
    if name == "s":
        out, _ = sandbox_run(cell, str(args.get("c", "")), timeout=30)
        return out
    if name == "w":
        p = inside(cell, str(args.get("p", "")))
        if p is None:
            return RESULTS["no_path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        content = str(args.get("x", ""))
        if STRICT and p.name == "f.py":
            verdict = strict_body(content)
            if not verdict["ok"]:
                log("strict_reject", {"path": p.name, "reason": verdict["reason"], "bad": verdict["bad"][:8]})
                return "!strict"
        p.write_text(content)
        leaks = python_leaks(content) if p.name in ("f.py", "spec.py") else {"comment_hits": 0, "docstring_hits": 0}
        log("write", {"path": p.name,
                      "bytes": len(content.encode()), **leaks})
        return RESULTS["write_ok"]
    if name == "v":
        return do_variants(cell, log, str(args.get("p", "")), [str(v) for v in args.get("vs", [])])
    if name == "a":
        return do_assay(cell, log, str(args.get("c", "")))
    if name == "d":
        (cell / "RESULT").write_text(str(args.get("q", "")))
        return RESULTS["done_ok"]
    return RESULTS["unknown_tool"]


def api_call(model: str, instructions: str, input_items: list):
    body = {"model": model, "instructions": instructions, "input": input_items,
            "tools": tools_common(), "max_output_tokens": MAX_OUTPUT_TOKENS}
    eff = os.environ.get("NOL_REASONING_EFFORT")
    if eff:
        body["reasoning"] = {"effort": eff}
    data = json.dumps(body).encode()
    req = urllib.request.Request(API, data=data,
                                 headers={"content-type": "application/json",
                                          "authorization": f"Bearer {KEY}"})
    ctx = ssl.create_default_context(cafile=certifi.where())
    timeout = int(os.environ.get("NOL_HTTP_TIMEOUT", "180"))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")[:2000]
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"HTTP {e.code}: {text}")
        except urllib.error.URLError as e:
            if attempt < 4:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"URL error: {e}")


MOCK_POLICIES = {
    # deterministic good citizen: builds f.py, registers assay, variants, done
    "good": [
        ("w", {"p": "f.py", "x": "import zlib\nd=open('x.bin','rb').read()\nprint(100*(1-len(zlib.compress(d))/len(d)))\n"}),
        ("a", {"c": "python3 f.py"}),
        ("v", {"p": "f.py", "vs": ["import zlib\nd=open('x.bin','rb').read()\nprint(100*(1-len(zlib.compress(d))/len(d)))\n",
                                      "import lzma\nd=open('x.bin','rb').read()\nprint(100*(1-len(lzma.compress(d,preset=9))/len(d)))\n"]}),
        ("d", {"q": "Δ78"}),
    ],
    # English prose everywhere; tools never produce a valid assay
    "bad": [
        ("w", {"p": "f.py", "x": "# This is a very nice compressor written in English\nimport lzma\nprint('hello world')\n"}),
        ("a", {"c": "echo hello world"}),
        ("d", {"q": "everything is fine"}),
    ],
    # schema garbage then recovery
    "flail": [
        ("s", {"c": "echo hi"}),
        ("w", {"p": "f.py", "x": "import lzma\nprint(42)\n"}),
        ("a", {"c": "python3 f.py"}),
        ("d", {"q": "ok"}),
    ],
}


def run_mock(policy: str, log) -> None:
    for i, (name, args) in enumerate(MOCK_POLICIES[policy]):
        log("tool_call", {"step": i, "name": name, "args": {k: (v[:80] + "…" if len(v) > 80 else v) for k, v in (args.items() if isinstance(args, dict) else [])}})
        result = tool_dispatch(CURRENT_CELL, LOG, name, args)
        log("tool_result", {"step": i, "name": name, "result": str(result)[:OUT_CAP]})


CURRENT_CELL = None
LOG = None


def main():
    global CURRENT_CELL, LOG
    cell = CELLS / TARGET_CELL
    if cell.exists():
        sys.exit(f"cell {cell} exists; refusing to overwrite")
    cell.mkdir(parents=True)
    (cell / "NEED").write_text(SYSTEM)
    corpus = Path(os.environ.get("NOL_CORPUS", str(ROOT.parent / "openai-blitz-2026-11-12" / "corpus_hard.txt")))
    (cell / "x.bin").write_bytes(corpus.read_bytes())
    for name, content in CHANNEL["files"].items():
        if content:
            (cell / name).write_text(content)
    logf = open(LOGS / f"{TARGET_CELL}.jsonl", "a")

    def log(kind, obj):
        logf.write(json.dumps({"t": time.time(), "kind": kind, "profile": PROFILE, **obj}) + "\n")
        logf.flush()

    CURRENT_CELL, LOG = cell, log
    if MOCK:
        if MOCK not in MOCK_POLICIES:
            sys.exit(f"unknown MOCK {MOCK}")
        run_mock(MOCK, log)
        log("finished", {"step": "mock", "wins": 0, "calls": len(MOCK_POLICIES[MOCK])})
        return

    if not KEY:
        sys.exit("OPENAI_API_KEY not set")
    items = [{"role": "developer", "content": [{"type": "input_text", "text": "lib ∅"}]},
             {"role": "user", "content": [{"type": "input_text", "text": SYSTEM}]}]
    t0 = time.time()
    wins = 0
    calls = 0
    for step in range(MAX_STEPS):
        if time.time() - t0 > CELL_WALL_S:
            log("abort", {"reason": "wall clock"})
            break
        try:
            resp = api_call(TARGET_NAME, SYSTEM, items)
        except RuntimeError as e:
            log("abort", {"reason": str(e)[:500]})
            break
        calls += 1
        u = resp.get("usage") or {}
        USAGE["input_tokens"] += u.get("input_tokens", 0)
        USAGE["output_tokens"] += u.get("output_tokens", 0)
        log("usage", {"step": step, **u})
        if USAGE["input_tokens"] > GLOBAL_IN_TOK or USAGE["output_tokens"] > GLOBAL_OUT_TOK:
            log("abort", {"reason": "token cap", **USAGE})
            break
        out_items = resp.get("output", [])
        items.extend(out_items)
        calls_this = [it for it in out_items if it.get("type") == "function_call"]
        dropped = calls_this[1:]
        for it in dropped:
            items.append({"type": "function_call_output", "call_id": it.get("call_id"), "output": "!dropped"})
        if dropped:
            log("note", {"msg": f"{len(dropped)} parallel tool call(s) dropped to keep the turn valid"})
        for it in calls_this[:1]:
            name = it.get("name")
            try:
                args = json.loads(it.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            log("tool_call", {"step": step, "name": name, "args": args})
            result = tool_dispatch(cell, log, name, args)
            log("tool_result", {"step": step, "name": name, "result": str(result)[:OUT_CAP]})
            items.append({"type": "function_call_output", "call_id": it.get("call_id"), "output": str(result)})
            if name == "d":
                log("finished", {"step": step, "wins": wins, "calls": calls})
                print(json.dumps({"cell": TARGET_CELL, "profile": PROFILE, "model": TARGET_NAME, "done": True, "wins": wins, "calls": calls, **USAGE}))
                return
            if name == "v" and str(result).startswith("✓"):
                wins += 1
        if not calls_this:
            items.append({"role": "user", "content": [{"type": "input_text", "text": "tool=1"}]})
    log("finished", {"step": "max", "wins": wins, "calls": calls})
    print(json.dumps({"cell": TARGET_CELL, "profile": PROFILE, "model": TARGET_NAME, "done": False, "wins": wins, "calls": calls, **USAGE}))


if __name__ == "__main__":
    main()
