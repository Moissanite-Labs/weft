#!/usr/bin/env python3
"""Local dry-run of the no-language instrument against ollama's
OpenAI-compatible endpoint. Free: no API keys, no credits.

Same cells, same sandbox, same assay logic as harness_nl.py. Tool-call
tolerance is deliberate: schema errors are counted, not fatal. Leak words
(blocklist) in any non-tool content are counted per message.

Usage: PROFILE=E2 NOL_MODEL=qwen3:32b python3 ollama_nl.py CELL
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
PROFILE = os.environ.get("PROFILE", "E2")
if PROFILE in ("E4a", "E4b", "E4c"):
    sys.exit("E4 has its own runner")
CELL_TAG = sys.argv[1] if len(sys.argv) > 1 else "ollama-1"
MODEL = os.environ.get("NOL_MODEL", "qwen3:32b")
STEPS = int(os.environ.get("NOL_STEPS", "10"))
HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ROOT = Path(__file__).resolve().parent

os.environ["PROFILE"] = PROFILE
os.environ.setdefault("OPENAI_API_KEY", "ollama-local-dummy")
os.environ.setdefault("NOL_MAX_STEPS", str(STEPS))
sys.argv = ["harness_nl.py", "ollama", sys.argv[1] if len(sys.argv) > 1 else "ollama-cell"]

import harness_nl  # noqa: E402  (sets up tools, assertions, dispatch)
from cellutil import python_leaks  # noqa: E402
from lint import english_hits  # noqa: E402
import profiles  # noqa: E402

cell = harness_nl.CELLS / CELL_TAG
if cell.exists():
    sys.exit(f"cell {cell} exists; refusing to overwrite")
cell.mkdir(parents=True)
(cell / "NEED").write_text(harness_nl.SYSTEM)
(cell / "x.bin").write_bytes((ROOT.parent / "openai-blitz-2026-11-12" / "corpus_hard.txt").read_bytes())
for name, content in harness_nl.CHANNEL["files"].items():
    if content:
        (cell / name).write_text(content)

logf = open(harness_nl.LOGS / f"{CELL_TAG}.jsonl", "a")


def log(kind, obj):
    logf.write(json.dumps({"t": time.time(), "kind": kind, "profile": PROFILE, "local_model": MODEL, **obj}) + "\n")
    logf.flush()


harness_nl.CURRENT_CELL, harness_nl.LOG = cell, log

tools = profiles.tools_common()
messages = [{"role": "system", "content": harness_nl.SYSTEM},
            {"role": "user", "content": "x.bin"}]
wins = 0
schema_errors = 0
english_msgs = 0
for step in range(STEPS):
    body = {"model": MODEL, "messages": messages, "tools": tools,
            "max_tokens": int(os.environ.get("NOL_MAX_TOKENS", "1200")), "temperature": 0}
    req = urllib.request.Request(f"{HOST}/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read())
    except Exception as e:
        log("abort", {"reason": str(e)[:300]})
        break
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or ""
    tcs = msg.get("tool_calls") or []
    leaks = english_hits(content)
    if leaks:
        english_msgs += 1
    log("model_turn", {"step": step, "leak_words": leaks, "n_tool_calls": len(tcs),
                       "content_head": content[:200]})
    if not tcs:
        if content:
            english_msgs += 0
        messages.append({"role": "user", "content": "tool=1"})
        continue
    call = tcs[0]
    name = (call.get("function") or {}).get("name") or ""
    try:
        args = json.loads((call.get("function") or {}).get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}
        schema_errors += 1
        log("schema_error", {"step": step, "raw": (call.get("function") or {}).get("arguments", "")[:200]})
    if name not in ("s", "w", "v", "a", "d"):
        schema_errors += 1
        log("schema_error", {"step": step, "name": name})
    log("tool_call", {"step": step, "name": name, "args": args})
    result = harness_nl.tool_dispatch(cell, log, name, args)
    log("tool_result", {"step": step, "name": name, "result": str(result)[:4000]})
    messages.append({"role": "assistant", "content": content, "tool_calls": tcs})
    messages.append({"role": "tool", "tool_call_id": call.get("id", "x"), "content": str(result)})
    if name == "d":
        log("finished", {"step": step, "wins": wins, "schema_errors": schema_errors, "english_msgs": english_msgs})
        break
    if name == "v" and str(result).startswith("✓"):
        wins += 1
else:
    log("finished", {"step": "max", "wins": wins, "schema_errors": schema_errors, "english_msgs": english_msgs})
print(json.dumps({"cell": CELL_TAG, "wins": wins, "schema_errors": schema_errors, "english_msgs": english_msgs}))
