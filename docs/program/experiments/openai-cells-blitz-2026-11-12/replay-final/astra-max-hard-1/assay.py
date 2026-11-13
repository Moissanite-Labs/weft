#!/usr/bin/env python3
"""Validate the actual command-line round trip, then repeat real work for 0.5s."""
import importlib
from pathlib import Path
import subprocess
import sys
import time


def measure():
    original = Path('corpus_hard.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'],
                   check=True, capture_output=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'],
                   check=True, capture_output=True)
    packed = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != original:
        return 0.0
    codec = importlib.import_module('compress')
    deadline = time.perf_counter() + 0.5
    count = 0
    while count < 2 or time.perf_counter() < deadline:
        result = codec.compress_bytes(original)
        if result != packed or codec.decompress_bytes(result) != original:
            return 0.0
        count += 1
    for sample in (b'', b'hello\n', bytes(range(256)) * 2, original[:-1]):
        if codec.decompress_bytes(codec.compress_bytes(sample)) != sample:
            return 0.0
    return 100.0 * (1.0 - len(packed) / len(original))


if __name__ == '__main__':
    try:
        print('%.12f' % measure())
    except Exception as exc:
        print('assay failed: %s' % exc, file=sys.stderr)
        print(0)
