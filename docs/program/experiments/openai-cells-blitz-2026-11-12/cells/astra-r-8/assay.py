"""Benchmark score with byte-for-byte round-trip validation."""
import pathlib
import subprocess
import sys
import time
import compress

try:
    original = pathlib.Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != original:
        raise ValueError('round trip mismatch')
    deadline = time.monotonic() + 0.4
    while time.monotonic() < deadline:
        trial = compress.compress(original)
        if trial != packed or compress.decompress(trial) != original:
            raise ValueError('round trip mismatch')
    print(100 * (1 - len(packed) / len(original)))
except Exception:
    print(0)
