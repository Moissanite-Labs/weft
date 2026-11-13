"""Measure size reduction only after byte-exact CLI round trips."""
import subprocess
import sys
import time
from pathlib import Path


def score():
    source = Path('corpus_hard.txt').read_bytes()
    start = time.perf_counter()
    size = None
    while True:
        subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if Path('restored.txt').read_bytes() != source:
            return 0.0
        current_size = Path('out.bin').stat().st_size
        if size is not None and size != current_size:
            return 0.0
        size = current_size
        if time.perf_counter() - start >= 0.4:
            break
    return 100 * (1 - size / len(source))


if __name__ == '__main__':
    try:
        print(score())
    except Exception:
        print(0)
