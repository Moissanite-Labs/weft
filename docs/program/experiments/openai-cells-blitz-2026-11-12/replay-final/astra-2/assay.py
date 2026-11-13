"""Correctness-gated size assay; repeat work for at least 0.35 seconds."""
import pathlib
import subprocess
import sys
import time
import compress


def main():
    original = pathlib.Path('corpus.txt').read_bytes()
    start = time.monotonic()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != original:
        return 0
    while time.monotonic() - start < 0.35:
        test = compress.compress(original)
        if test != packed or compress.decompress(test) != original:
            return 0
    return max(0, 100 * (1 - len(packed) / len(original)))


try:
    print(main())
except Exception:
    print(0)
