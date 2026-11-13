"""Validate CLI and repeated codec round trips, then report size reduction."""
import sys
import subprocess
from pathlib import Path
import compress


def main():
    original = Path('corpus_hard.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    encoded = Path('out.bin').read_bytes()
    if Path('restored.txt').read_bytes() != original:
        return 0
    for _ in range(10):
        packed = compress.compress(original)
        if packed != encoded or compress.decompress(packed) != original:
            return 0
    return 100 * (1 - len(encoded) / len(original))


if __name__ == '__main__':
    try:
        print(main())
    except Exception:
        print(0)
