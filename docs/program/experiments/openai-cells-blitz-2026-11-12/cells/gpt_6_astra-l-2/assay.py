"""Verify actual CLI roundtrip and time-sized in-process repeat checks."""
from pathlib import Path
import subprocess
import sys
import time
import compress


def main():
    original = Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    encoded = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != original:
        print(0)
        return
    deadline = time.monotonic() + 0.35
    while time.monotonic() < deadline:
        candidate = compress.compress(original)
        if candidate != encoded or compress.decompress(candidate) != original:
            print(0)
            return
    print(max(0, 100 * (1 - len(encoded) / len(original))))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
