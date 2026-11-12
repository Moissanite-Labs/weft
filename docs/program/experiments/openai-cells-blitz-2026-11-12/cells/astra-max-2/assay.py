#!/usr/bin/env python3
"""Check the real CLI and repeatedly verify lossless compression before scoring."""
import subprocess
import sys
import time
from pathlib import Path


def score():
    root = Path(__file__).resolve().parent
    source = root / 'corpus.txt'
    packed = root / 'out.bin'
    restored = root / 'restored.txt'
    data = source.read_bytes()
    if not data:
        return 0.0
    for arguments in ([str(source), str(packed)],
                      ['--decompress', str(packed), str(restored)]):
        subprocess.run([sys.executable, str(root / 'compress.py'), *arguments],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if restored.read_bytes() != data:
        return 0.0
    encoded = packed.read_bytes()
    import compress
    start = time.perf_counter()
    while True:
        candidate = compress.compress(data)
        if candidate != encoded or compress.decompress(candidate) != data:
            return 0.0
        if time.perf_counter() - start >= 0.6:
            break
    return 100.0 * (1.0 - len(encoded) / len(data))


if __name__ == '__main__':
    try:
        value = score()
    except Exception:
        value = 0.0
    print(f'{value:.12f}')
