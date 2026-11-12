"""Correctness-gated size score; repeats work for at least 0.4 seconds."""
import time
import zlib
import runpy
from pathlib import Path


def score():
    # Execute source directly so rapid candidate replacement cannot use stale bytecode.
    codec = runpy.run_path('compress.py')
    original = Path('corpus.txt').read_bytes()
    deadline = time.perf_counter() + 0.4
    first = None
    while True:
        packed = codec['compress'](original)
        if codec['decompress'](packed) != original:
            return 0.0
        if first is None:
            first = packed
        elif packed != first:
            return 0.0
        if time.perf_counter() >= deadline:
            break
    Path('out.bin').write_bytes(first)
    if len(first) >= len(zlib.compress(original)):
        return 0.0
    return 100.0 * (1.0 - len(first) / len(original))


try:
    print(score())
except Exception:
    print(0.0)
