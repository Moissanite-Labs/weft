#!/usr/bin/env python3
"""E4a: matrix-as-message statistical entities. No words anywhere on this channel.

Input: one message whose text is a pure 8x8 float matrix (a list of lists).
The model's reply: one 8x8 float matrix, same serialization. A fixed,
disclosed decoder D maps the reply onto a compressor template family and
parameter set. The materialized program runs on the corpus; the harness
returns the fitness as a 1x4 float matrix. No text flows or is parsed.

Decoder (part of the preregistration):

  r[i] = mean(abs(row i)) of the 8x8 output matrix.
  row 0 -> family f = clamp(int(r0 * 4) % 4, 0, 3)
          0 = zlib        1 = bz2          2 = lzma          3 = lzma(delta+lzma2)
  row 1 -> primary knob pk = clamp(int(r1 * 10), 1, 9)
          zlib: level=pk      bz2: compresslevel=pk   lzma: preset=pk   f=3: preset=pk
  row 2 -> toggle t = (r2 > 0.5)
          zlib: wbits=15 if t else 9
          bz2: rsyncable if t
          lzma: check=CRC32 if t else CRC64
          f=3: delta dist 8 if t else 16
  row 3 -> secondary sk = clamp(int(r3 * 4), 0, 3)
          zlib: memLevel = sk + 1       bz2: blocksize = sk + 1
          lzma: dict_size = [1,4,16,64] MB[sk]    f=3: dict_size = [1,4,16,64] MB[sk]
  rows 4-7 -> row 4 doubles as the termination signal: r4 > 0.9 ends the run.

Assay: byte round-trip on the corpus; score is the percentage size reduction,
0 if the round-trip fails. Retention: incumbent replaced iff round-trip ok
and score > incumbent * 1.03.

Usage: NOL_MODEL=gpt-6-astra python3 e4a.py CELL [steps]
       MOCK=good python3 e4a.py CELL [steps]
"""
import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import time
import urllib.request
import urllib.error
import ssl
import certifi
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CELLS = ROOT / "cells"
LOGS = ROOT / "logs"
API = "https://api.openai.com/v1/responses"
KEY = os.environ.get("OPENAI_API_KEY")
CELL_TAG = sys.argv[1] if len(sys.argv) > 1 else "e4a-1"
STEPS = int(os.environ.get("E4A_STEPS", sys.argv[2] if len(sys.argv) > 2 else "15"))
MOCK = os.environ.get("MOCK")
MODEL = os.environ.get("NOL_MODEL", "gpt-6-astra")
sys.path.insert(0, str(ROOT))
from cellutil import sandbox_run  # noqa: E402


def fmt_matrix(m):
    return json.dumps([[round(v, 4) for v in row] for row in m], separators=(",", ":"))


def parse_matrix(text: str):
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", text)]
    if len(nums) < 64:
        return None
    nums = nums[:64]
    return [nums[i * 8:(i + 1) * 8] for i in range(8)]


def decode(m):
    r = [abs(sum(row) / len(row)) for row in m]
    fam = max(0, min(3, int(r[0] * 4) % 4))
    pk = max(1, min(9, int(r[1] * 10)))
    t = r[2] > 0.5
    sk = max(0, min(3, int(r[3] * 4)))
    fin = r[4] > 0.9
    return fam, pk, t, sk, fin


def template(fam, p, t, s):
    dicts = [1 << 20, 4 << 20, 16 << 20, 64 << 20][s]
    if fam == 0:
        return (
            "import zlib\n"
            "class C:\n"
            "    @staticmethod\n"
            "    def compress_all(data):\n"
            f"        return zlib.compress(data, {p}, wbits={15 if t else 9}, memLevel={s + 1})\n"
            "    @staticmethod\n"
            "    def decompress_all(packed):\n"
            "        return zlib.decompress(packed)\n")
    if fam == 1:
        return (
            "import bz2\n"
            "class C:\n"
            "    @staticmethod\n"
            "    def compress_all(data):\n"
            f"        return bz2.compress(data, {p})\n"
            "    @staticmethod\n"
            "    def decompress_all(packed):\n"
            "        return bz2.decompress(packed)\n")
    if fam == 2:
        return (
            "import lzma\n"
            "class C:\n"
            "    @staticmethod\n"
            "    def compress_all(data):\n"
            f"        return lzma.compress(data, preset={p}, check=lzma.CHECK_{'CRC32' if t else 'CRC64'})\n"
            "    @staticmethod\n"
            "    def decompress_all(packed):\n"
            "        return lzma.decompress(packed)\n")
    return (
        "import lzma\n"
        "class C:\n"
        "    @staticmethod\n"
        "    def compress_all(data):\n"
        f"        return lzma.compress(data, filters=[{{'id': lzma.FILTER_DELTA, 'dist': {8 if t else 16}}}, {{'id': lzma.FILTER_LZMA2, 'preset': {p}}}])\n"
        "    @staticmethod\n"
        "    def decompress_all(packed):\n"
        "        return lzma.decompress(packed)\n")


RUNNER = """
import sys
from pathlib import Path
data = Path('x.bin').read_bytes()
try:
    z = C.compress_all(data)
    assert C.decompress_all(z) == data
    print(100 * (1 - len(z) / len(data)))
except Exception:
    print(0)
"""


def main():
    cell = CELLS / CELL_TAG
    if cell.exists():
        sys.exit(f"cell {cell} exists; refusing to overwrite")
    cell.mkdir(parents=True)
    (cell / "NEED").write_text("[0,0,0,0,0,0,0,0]")
    (cell / "x.bin").write_bytes((ROOT.parent / "openai-blitz-2026-11-12" / "corpus_hard.txt").read_bytes())
    logf = open(LOGS / f"{CELL_TAG}.jsonl", "a")

    def log(kind, obj):
        logf.write(json.dumps({"t": time.time(), "kind": kind, "profile": "E4a", **obj}) + "\n")
        logf.flush()

    rng = random.Random(20261112)
    state = [[rng.uniform(-0.3, 0.3) for _ in range(8)] for _ in range(8)]
    inc_score = 0.0
    wins = 0

    def matrix_out():
        return fmt_matrix(state)

    corpus = (ROOT.parent / "openai-blitz-2026-11-12" / "corpus_hard.txt").read_bytes()

    def materialize_score(fam, p, t, s):
        src = template(fam, p, t, s)
        with tempfile.TemporaryDirectory(prefix="e4a-score-") as d:
            tmp = Path(d)
            (tmp / "x.bin").write_bytes(corpus)
            (tmp / "cand.py").write_text(src + RUNNER)
            out, _ = sandbox_run(tmp, "python3 cand.py", timeout=60)
        nums = re.findall(r"-?\d+(?:\.\d+)?", out.split("exit", 1)[-1])
        try:
            return (float(nums[-1]) if nums else 0.0), src
        except ValueError:
            return 0.0, src

    messages = [{"role": "user", "content": matrix_out()}]
    ctx = ssl.create_default_context(cafile=certifi.where())
    inc_src = None
    for step in range(STEPS):
        if MOCK == "good":
            state = [[0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6],
                     [0.0] * 8, [0.8] * 8, [0.2] * 8, [0.0] * 8, [0.0] * 8, [0.0] * 8, [0.0] * 8]
            state[1] = [0.1 + step * 0.09] * 8
            if step == STEPS - 1:
                state[4] = [0.95] * 8
            text = matrix_out()
            usage = {"mock": True}
        elif MOCK == "rand":
            state = [[rng.uniform(-1, 1) for _ in range(8)] for _ in range(8)]
            text = matrix_out()
            usage = {"mock": True}
        else:
            if not KEY:
                sys.exit("OPENAI_API_KEY not set")
            body = {"model": MODEL, "input": messages, "max_output_tokens": 600}
            req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                         headers={"content-type": "application/json", "authorization": f"Bearer {KEY}"})
            try:
                with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
                    resp_d = json.loads(resp.read())
            except urllib.error.HTTPError as e:
                log("abort", {"reason": f"HTTP {e.code}: {e.read()[:300]}"})
                break
            usage = resp_d.get("usage") or {}
            text = "".join(c.get("text", "") for it in resp_d.get("output", []) if it.get("type") == "message"
                           for c in it.get("content", []) if c.get("type") == "output_text")
        m = parse_matrix(text)
        log("turn", {"step": step, "usage": usage, "parsed": m is not None,
                     "rows": ([round(abs(sum(r) / 8), 4) for r in m] if m else None),
                     "text_head": text[:120]})
        messages.append({"role": "assistant", "content": text})
        def fb_matrix(score, valid, kept):
            rows = [[round(score / 100.0, 4), valid, kept, round((STEPS - step - 1) / STEPS, 3), 0.0, 0.0, 0.0, 0.0]]
            rows += [[0.0] * 8 for _ in range(7)]
            return rows
        if m is None:
            feedback = fb_matrix(0.0, 0.0, 0.0)
            messages.append({"role": "user", "content": fmt_matrix(feedback)})
            log("feedback", {"step": step, "matrix": feedback[0]})
            continue
        fam, p, t, s, fin = decode(m)
        score, src = materialize_score(fam, p, t, s)
        kept = 0.0
        if score > inc_score * 1.03:
            inc_score, inc_src, kept = score, src, 1.0
            wins += 1
            (cell / "keep.py").write_text(src)
        feedback = fb_matrix(score, 1.0 if score > 0 else 0.0, kept)
        log("score", {"step": step, "family": fam, "p": p, "tog": bool(t), "s": s,
                      "score": score, "kept": kept, "inc_score": inc_score})
        messages.append({"role": "user", "content": fmt_matrix(feedback)})
        log("feedback", {"step": step, "matrix": feedback})
        if fin:
            log("finished", {"step": step, "wins": wins, "reason": "fin", "inc_score": inc_score})
            print(json.dumps({"cell": CELL_TAG, "done": True, "wins": wins, "inc_score": inc_score}))
            return
    log("finished", {"step": "max", "wins": wins, "inc_score": inc_score})
    print(json.dumps({"cell": CELL_TAG, "done": False, "wins": wins, "inc_score": inc_score}))


if __name__ == "__main__":
    main()
