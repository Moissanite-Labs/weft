#!/usr/bin/env python3
"""OpenAI blitz 2026-11-12: direct /v1/responses colony-style cells.

Exploratory harness. Reads OPENAI_API_KEY from the environment. Writes logs
to this directory only. See PREREGISTRATION.md.
"""
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.request
import urllib.error
import ssl
import certifi
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CELLS = ROOT / "cells"
LOGS = ROOT / "logs"
API = "https://api.openai.com/v1/responses"
KEY = os.environ.get("OPENAI_API_KEY")
if not KEY:
    sys.exit("OPENAI_API_KEY not set")

TARGET_NAME = sys.argv[1] if len(sys.argv) > 1 else None           # model
TARGET_CELL = sys.argv[2] if len(sys.argv) > 2 else None           # cell tag
TARGET_TASK = sys.argv[3] if len(sys.argv) > 3 else "compress"
if not TARGET_NAME or not TARGET_CELL:
    sys.exit("usage: harness.py MODEL CELLTAG [TASK]")

CORPUSES = {"compress": "corpus.txt", "compress-hard": "corpus_hard.txt"}
if TARGET_TASK not in CORPUSES:
    sys.exit(f"unknown task {TARGET_TASK}")
CORPUS_FILE = CORPUSES[TARGET_TASK]
MAX_STEPS = int(os.environ.get("BLITZ_MAX_STEPS", "18"))
CELL_WALL_S = 12 * 60
GLOBAL_IN_TOK = 8_000_000
GLOBAL_OUT_TOK = 2_500_000
MAX_OUTPUT_TOKENS = int(os.environ.get("BLITZ_MAX_OUTPUT_TOKENS", "8192"))
OUT_CAP = 4000
ASSAY_RUNS = 3
SPREAD_MAX = 0.15
WIN_MARGIN = 1.03

# global token ledger shared across this process; the blitz runner enforces the cap
USAGE = {"input_tokens": 0, "output_tokens": 0}

SYSTEM = (
    "You are a cell: a tiny agent that starts with nothing but a NEED and an empty folder (your body).\n"
    "Grow only the tools your need demands, one step at a time. Call exactly one tool per reply.\n"
    "Path to fitness: 1) build a correct version and check it. 2) register an `assay`: a shell command that\n"
    "prints one number, higher is better, 0 if the output is wrong. Make its workload heavy enough (about\n"
    "0.3 to 3 s) that process startup does not dominate. 3) improve with `variants` (cheap: several versions\n"
    "of one file in one reply, all scored). Only scored wins are kept. Read LIBRARY if present."
)
if os.environ.get("BLITZ_ABLATE") == "novariants":
    SYSTEM = SYSTEM.replace("3) improve with `variants` (cheap: several versions\n"
                            "of one file in one reply, all scored). Only scored wins are kept.",
                            "3) improve however you can. No scoring tool is available to you.")

NEED = (
    f"NEED: write a stdlib-only Python program `compress.py` in your folder that round-trips `{CORPUS_FILE}`\n"
    f"(also in your folder): `python3 compress.py {CORPUS_FILE} out.bin` writes the compressed form, and\n"
    "`python3 compress.py --decompress out.bin restored.txt` restores it byte-identically.\n"
    f"Your assay prints one number: the percentage size reduction, 100 * (1 - bytes(out.bin)/bytes({CORPUS_FILE})).\n"
    "Fitness is 0 when the round trip is wrong in any byte. Higher is better.\n"
    "Rules: stdlib only. No imports outside the Python standard library. The corpus is fixed. Beat the\n"
    "trivial baseline (zlib with default settings) before anything else."
)

TOOLS = [
    {"type": "function", "name": "sh",
     "description": "Run a shell command in your folder. No network, 30 s limit, python3 available.",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"type": "function", "name": "write",
     "description": "Create or overwrite a text file in your folder.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"type": "function", "name": "remember",
     "description": "Replace genome.md, your memory across steps (max 4000 chars).",
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"type": "function", "name": "assay",
     "description": "Register your fitness command. The harness runs it 3 times and accepts it only if it exits 0, prints a number > 0, and is stable (spread under 15%).",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"type": "function", "name": "variants",
     "description": "Propose 2 to 6 full alternative versions of ONE file. Each is scored by your assay against the current body; the best is adopted only if it wins beyond noise.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "versions": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 6}}, "required": ["path", "versions"]}},
    {"type": "function", "name": "done",
     "description": "Finish. One paragraph: what you built and the evidence it works.",
     "parameters": {"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]}},
]


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


def inside(cell: Path, rel: str) -> Path | None:
    p = (cell / rel).resolve()
    if p.is_relative_to(cell.resolve()) and p.name not in ("NEED", "log.jsonl", "ASSAY.json", "RESULT"):
        return p
    return None


NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")


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


def do_assay(cell: Path, log, command: str) -> str:
    (cell / "ASSAY").write_text(command)
    r = run_assay(cell)
    log("assay", {"command": command, **{k: v for k, v in r.items()}})
    if not r["ok"]:
        return (f"assay rejected: scores={r['scores']} spread={r['spread']}. "
                f"Need exit 0, a number > 0, spread <= {SPREAD_MAX}.")
    return f"assay accepted. median={r['median']:.4f} spread={(r['spread'] or 0):.3f}"


def do_variants(cell: Path, log, path: str, versions: list[str]) -> str:
    p = inside(cell, path)
    if p is None:
        return "variants: path escapes the cell folder or is hidden."
    inc = p.read_text() if p.exists() else None
    inc_res = run_assay(cell)
    inc_med = inc_res["median"] if inc_res and inc_res["ok"] else None
    if inc_med is None:
        return "variants: register a valid assay first (assay tool), or current body scores 0."
    best_i, best_med, best_min = None, inc_med, None
    for i, v in enumerate(versions):
        p.write_text(v)
        r = run_assay(cell)
        s = [x for x in r["scores"] if x is not None]
        med = statistics.median(s) if s else 0.0
        mn = min(s) if s else 0.0
        log("variant", {"index": i, "scores": r["scores"], "median": med, "min": mn})
        if med > best_med * WIN_MARGIN and mn >= inc_med * 0.97:
            best_i, best_med, best_min = i, med, mn
    if best_i is None:
        if inc is not None:
            p.write_text(inc)
        log("variants_result", {"adopted": None, "incumbent_median": inc_med})
        return f"no variant beat the incumbent (median {inc_med:.4f}). Body unchanged."
    log("variants_result", {"adopted": best_i, "median": best_med})
    return f"variant {best_i} adopted. median {best_med:.4f} vs incumbent {inc_med:.4f}."


def tool_dispatch(cell: Path, log, name: str, args: dict) -> str:
    if name == "sh":
        out, dt = sandbox_run(cell, str(args.get("command", "")), timeout=30)
        return out
    if name == "write":
        p = inside(cell, str(args.get("path", "")))
        if p is None:
            return "write: path escapes the cell folder or is hidden."
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(args.get("content", "")))
        return f"wrote {p.relative_to(cell)}"
    if name == "remember":
        t = str(args.get("text", ""))[:4000]
        (cell / "genome.md").write_text(t)
        return "remembered"
    if name == "assay":
        return do_assay(cell, log, str(args.get("command", "")))
    if name == "variants":
        return do_variants(cell, log, str(args.get("path", "")), [str(v) for v in args.get("versions", [])])
    if name == "done":
        (cell / "RESULT").write_text(str(args.get("summary", "")))
        return "done"
    return f"unknown tool {name}"


def api_call(model: str, instructions: str, input_items: list):
    body = {"model": model, "instructions": instructions, "input": input_items,
            "tools": TOOLS, "max_output_tokens": MAX_OUTPUT_TOKENS}
    eff = os.environ.get("BLITZ_REASONING_EFFORT")
    if eff:
        body["reasoning"] = {"effort": eff}
    if os.environ.get("BLITZ_ABLATE") == "novariants":
        body["tools"] = [t for t in TOOLS if t["name"] != "variants"]
    data = json.dumps(body).encode()
    req = urllib.request.Request(API, data=data, headers={
        "content-type": "application/json", "authorization": f"Bearer {KEY}"})
    ctx = ssl.create_default_context(cafile=certifi.where())
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=int(os.environ.get('BLITZ_HTTP_TIMEOUT', '180')), context=ctx) as resp:
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


def main():
    cell = CELLS / TARGET_CELL
    if cell.exists():
        sys.exit(f"cell dir {cell} exists; refusing to overwrite")
    cell.mkdir(parents=True)
    (cell / CORPUS_FILE).write_bytes((ROOT / CORPUS_FILE).read_bytes())
    (cell / "NEED").write_text(NEED)
    logf = open(LOGS / f"{TARGET_CELL}.jsonl", "a")

    def log(kind, obj):
        logf.write(json.dumps({"t": time.time(), "kind": kind, **obj}) + "\n")
        logf.flush()

    items = [{"role": "developer", "content": [{"type": "input_text", "text": "LIBRARY: (empty)"}]},
             {"role": "user", "content": [{"type": "input_text", "text": NEED}]}]
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
        text_bits = [it for it in out_items if it.get("type") == "message" for c in it.get("content", []) if c.get("type") == "output_text"]
        if len(calls_this) > 1:
            log("note", {"msg": f"{len(calls_this)} parallel tool calls; dispatching first only"})
        for it in calls_this[:1]:
            name = it.get("name")
            try:
                args = json.loads(it.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            log("tool_call", {"step": step, "name": name, "args": args})
            result = tool_dispatch(cell, log, name, args)
            log("tool_result", {"step": step, "name": name, "result": result[:OUT_CAP]})
            items.append({"type": "function_call_output", "call_id": it.get("call_id"), "output": result})
            if name == "done":
                log("finished", {"step": step, "wins": wins, "calls": calls})
                print(json.dumps({"cell": TARGET_CELL, "model": TARGET_NAME, "done": True, "wins": wins, "calls": calls, **USAGE}))
                return
            if name == "variants" and result.startswith(("variant",)) and "adopted" in result:
                wins += 1
        if not calls_this and not text_bits:
            log("note", {"msg": "no actionable output this step"})
        elif not calls_this:
            items.append({"role": "user", "content": [{"type": "input_text", "text": "Call exactly one tool."}]})
    log("finished", {"step": "max", "wins": wins, "calls": calls})
    print(json.dumps({"cell": TARGET_CELL, "model": TARGET_NAME, "done": False, "wins": wins, "calls": calls, **USAGE}))


if __name__ == "__main__":
    main()
