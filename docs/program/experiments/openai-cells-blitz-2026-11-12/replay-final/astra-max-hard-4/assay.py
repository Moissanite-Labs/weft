"""CLI round-trip check, followed by at least half a second of verified work."""
import subprocess
import sys
import time
from pathlib import Path
import compress


def score():
    source = Path('corpus_hard.txt').read_bytes()
    start = time.perf_counter()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    encoded = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != source:
        return 0.0
    while True:
        trial = compress.compress(source)
        if compress.decompress(trial) != source or trial != encoded:
            return 0.0
        if time.perf_counter() - start >= 0.5:
            break
    return max(0.0, 100 * (1 - len(encoded) / len(source)))


if __name__ == '__main__':
    try:
        print(score())
    except Exception:
        print(0.0)
