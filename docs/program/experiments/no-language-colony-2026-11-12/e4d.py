#!/usr/bin/env python3
"""E4d embedding decoder (prereg PREREG-5, registered 2026-11-12).

Channel: no tool schema at all. The cell sees one line of formula plus two
filename hints. Anything it says is decoded by cosine-argmax against a fixed,
disclosed codebook (text-embedding-3-small). Actions have no signed arguments
from outside the cell; whatever code or command appears in the reply is what
runs.

This is an instrument for measuring whether current frontier text models can
act as statistical organisms at all: arbitrary prose in, deterministic actions
out, tensor-grade determinism at the boundary.

codebook (labels kept bare, zero English content other than the descriptions
themselves, which is the point of the experiment):
  look       :: "I want to inspect my current body and the corpus state"
  write      :: "here is the new body (source code) for f.py"
  run        :: "run this shell command in my cell"
  assay      :: "register this shell command as my fitness assay"
  variants   :: "score several bodies at once, keep the best"
  done       :: "finish; the f.py on disk is final"
  corpus     :: "show me the corpus samples"
  help       :: "describe what Ω means and how scoring works"
"""
import json
import math
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

import certifi
import numpy as np

ROOT = Path(__file__).resolve().parent
CELLS = ROOT / "cells"
LOGS = ROOT / "logs"
API = "https://api.openai.com/v1/responses"
EMB = "https://api.openai.com/v1/embeddings"
KEY = os.environ.get("OPENAI_API_KEY")
if not KEY:
    sys.exit("OPENAI_API_KEY not set")
CELL_TAG = sys.argv[1]
MODEL = sys.argv[2] if len(sys.argv) > 2 else "gpt-6-astra"
STEPS = int(os.environ.get("E4D_STEPS", "15"))
EMB_MODEL = "text-embedding-3-small"

CODEBOOK = [
    ("look", "I want to inspect my current body and the corpus state, print file listing and sizes"),
    ("write", "here is the new body, source code for the file f.py"),
    ("run", "run this shell command in my cell"),
    ("assay", "register this shell command as my fitness assay which prints one number"),
    ("variants", "score several different bodies at once and keep the best"),
    ("done", "finish, the f.py on disk is final"),
    ("corpus", "show me samples of the corpus"),
    ("help", "what does Ω mean, describe the rules of the task and the scoring"),
]
NAME_VECS = None
NAME_LUT = None


def emb(texts):
    body = json.dumps({"model": EMB_MODEL, "input": texts}).encode()
    req = urllib.request.Request(EMB, data=body,
                                 headers={"content-type": "application/json",
                                          "authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context(cafile=certifi.where())) as r:
        d = json.loads(r.read())
    v = np.array([x["embedding"] for x in d["data"]], dtype=np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v


def codebook_vecs():
    global NAME_VECS, NAME_LUT
    if NAME_VECS is None:
        NAME_VECS = emb([t for _, t in CODEBOOK])
        NAME_LUT = [n for n, _ in CODEBOOK]
    return NAME_VECS, NAME_LUT


def api_chat(model, input_items):
    body = {"model": model, "input": input_items, "max_output_tokens": 4000}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json",
                                          "authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=120, context=ssl.create_default_context(cafile=certifi.where())) as r:
        return json.loads(r.read())


def run_cell():
    cell = CELLS / CELL_TAG
    if cell.exists():
        sys.exit(f"cell {cell} exists")
    cell.mkdir(parents=True)
    corpus = ROOT.parent / "openai-blitz-2026-11-12" / "corpus_hard.txt"
    (cell / "x.bin").write_bytes(corpus.read_bytes())
    logf = open(LOGS / f"{CELL_TAG}.jsonl", "a")

    def log(kind, obj):
        logf.write(json.dumps({"t": time.time(), "kind": kind, "profile": "E4d", **obj}) + "\n")
        logf.flush()

    v0, lut = codebook_vecs()
    incumbent_score = 0.0
    inc_src = None
    inc_body = None
    steps = 0
    assay_cmd = None
    wins = 0
    messages = [{"role": "user", "content": [{"type": "input_text", "text":
        "Ω ≝ ∀x∈B⁺: dec(enc x) = x  ∧  |enc x| ≤ θ·|x|\nf.py ≡ Ω-out · x.bin ≡ Ω-in"}]}]

    def sandbox(cmd, timeout=30):
        import tempfile
        tmpdir = Path(tempfile.mkdtemp(prefix="e4d-score-"))
        import shutil
        for f in ("corpus_hard.txt", "x.bin"):
            srcf = corpus if f == "corpus_hard.txt" else (cell / "x.bin")
            if srcf.exists():
                shutil.copy(srcf, tmpdir / "x.bin")
        prof = '(version 1)(deny default)(allow file-read*)(deny file-read* (subpath "/Users/kethuda"))(allow file-read* (subpath "%s"))(allow file-write* (subpath "%s"))(allow process-exec (subpath "/"))(allow process-fork)(deny network*)' % (tmpdir, tmpdir)
        import subprocess as sp
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(tmpdir), "TMPDIR": str(tmpdir / "tmp"), "LANG": "C.UTF-8"}
        tmpdir.joinpath("tmp").mkdir(exist_ok=True)
        try:
            p = sp.run(["sandbox-exec", "-p", prof, "/bin/sh", "-c", cmd], cwd=tmpdir,
                       capture_output=True, text=True, env=env, timeout=timeout)
        except sp.TimeoutExpired:
            return "timeout"
        out = f"exit {p.returncode}\n{p.stdout}{p.stderr}"
        return out[:2000]

    def score_body(src):
        if "enc" not in src:
            return 0.0
        for _ in range(3):
            out = sandbox("python3 cand.py", timeout=60,
                          files={"cand.py": src, "x.bin": (cell / "x.bin").read_bytes()})
            m = re.findall(r"-?\d+(?:\.\d+)?", out.split("exit", 1)[-1])
            if not m or not out.startswith("exit 0"):
                return 0.0
        try:
            return float(m[-1])
        except ValueError:
            return 0.0

    def commit_if_better(src, tag):
        nonlocal incumbent_score, inc_src, inc_body, wins
        s = score_body(src)
        if s > incumbent_score * 1.03:
            inc_src, inc_body = src, f"{tag}.py"
            incumbent_score = s
            wins += 1
            (cell / "keep.py").write_text(src)
            return True, s
        return False, s

    def parse_code_blocks(text):
        blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.S)
        if not blocks:
            # fenced-looking but unmatched: take lines with def/function tokens
            lines = [l for l in text.splitlines() if l.strip().startswith(("def ", "import ", "class "))]
            if len(lines) > 2:
                blocks = ["\n".join(lines)]
        return blocks

    for step in range(STEPS):
        resp = api_chat(MODEL, messages)
        usage = resp.get("usage") or {}
        text = "".join(c.get("text", "") for out in resp.get("output", [])
                       if out.get("type") == "message"
                       for c in out.get("content", []))
        q = emb([text])[0]
        sims = v0 @ q
        best_i = int(np.argmax(sims))
        best_label = lut[best_i]
        best_sim = float(sims[best_i])
        log("turn", {"step": step, "usage": usage, "decoded": best_label,
                     "sim": round(best_sim, 4), "text_head": text[:200]})
        action = best_label if best_sim >= 0.10 else "uninterpretable"
        result = "uninterpretable"
        if action == "look":
            body_state = cell.joinpath("f.py").read_text()[:200] if cell.joinpath("f.py").exists() else "∅"
            result = json.dumps([int(cell.joinpath("f.py").exists()), len(cell.joinpath("f.py").read_bytes()) if cell.joinpath("f.py").exists() else 0,
                                 round(incumbent_score, 3), STEPS - step - 1])
        elif action == "corpus":
            raw = corpus.read_bytes()[:600].decode("utf-8", errors="ignore")
            result = raw[:200]
        elif action == "help":
            result = "Ω ≝ ∀x: dec(enc x) = x ∧ |enc x| ≤ θ·|x|"
        elif action == "write":
            blocks = parse_code_blocks(text)
            if blocks:
                src = blocks[0]
                (cell / "f.py").write_text(src)
                committed, s = commit_if_better(src, "cand")
                result = json.dumps([round(s, 3), int(committed)])
            else:
                result = "!no-code"
        elif action == "run":
            m = re.search(r"(?:^|\n)(?:\$|>)\s*(.+)", text)
            cmd = m.group(1).strip() if m else None
            if cmd:
                result = sandbox(cmd, timeout=30)[:500]
            else:
                result = "!no-cmd"
        elif action == "assay":
            m = re.search(r"(?:^|\n)(?:\$|assay:?)\s*(.+)", text)
            cmd = m.group(1).strip() if m else None
            if cmd:
                assay_cmd = cmd
                out = sandbox(cmd, timeout=60)
                mnum = re.findall(r"-?\d+(?:\.\d+)?", out.split("exit", 1)[-1])
                ok = bool(mnum) and out.startswith("exit 0") and float(mnum[-1]) > 0
                result = json.dumps([int(ok), float(mnum[-1]) if mnum else 0.0])
                log("assay", {"command": cmd, "ok": ok})
            else:
                result = "!no-assay"
        elif action == "variants":
            blocks = parse_code_blocks(text)
            if len(blocks) >= 2:
                scores = []
                for i, src in enumerate(blocks[:4]):
                    _, s = commit_if_better(src, f"v{i}")
                    scores.append(round(s, 3))
                result = json.dumps(scores)
            else:
                result = "!<2-bodies"
        elif action == "done":
            (cell / "RESULT").write_text(f"e4d Ω final score {incumbent_score:.4f}")
            log("finished", {"step": step, "wins": wins, "score": incumbent_score})
            print(json.dumps({"cell": CELL_TAG, "done": True, "wins": wins, "score": incumbent_score}))
            return
        log("result", {"step": step, "action": action, "result": str(result)[:400]})
        messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": str(result)})
    log("finished", {"step": "max", "wins": wins, "score": incumbent_score})
    print(json.dumps({"cell": CELL_TAG, "done": False, "wins": wins, "score": incumbent_score}))


def main():
    run_cell()


if __name__ == "__main__":
    main()
