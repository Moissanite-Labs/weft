"""Correctness-gated size benchmark; run long enough to amortize startup."""
from pathlib import Path
import subprocess
import sys
import time
import compress


def score():
    original = Path('corpus_hard.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin',
                    'restored.txt'], check=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)
    encoded = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != original:
        return 0.0
    start = time.perf_counter()
    while True:
        trial = compress.compress(original)
        if trial != encoded or compress.decompress(trial) != original:
            return 0.0
        if time.perf_counter() - start >= 0.4:
            break
    return max(0.0, 100.0 * (1.0 - len(encoded) / len(original)))


if __name__ == '__main__':
    try:
        result = score()
    except Exception:
        result = 0.0
    print('%.12f' % result)
