"""Verify the CLI and repeated round trips, then report actual byte savings."""
from pathlib import Path
import subprocess
import sys
import time


def score():
    original = Path('corpus.txt').read_bytes()
    if not original:
        return 0.0
    for args in (['corpus.txt', 'out.bin'],
                 ['--decompress', 'out.bin', 'restored.txt']):
        subprocess.run([sys.executable, 'compress.py', *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=10)
    packed = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != original:
        return 0.0
    import compress
    start = time.perf_counter()
    while True:
        trial = compress.compress(original)
        if trial != packed or compress.decompress(trial) != original:
            return 0.0
        if time.perf_counter() - start >= 0.4:
            break
    return 100.0 * (1.0 - len(packed) / len(original))


if __name__ == '__main__':
    try:
        result = score()
    except Exception:
        result = 0.0
    print(result)
