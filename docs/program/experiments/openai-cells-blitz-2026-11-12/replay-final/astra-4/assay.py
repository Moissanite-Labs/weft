"""Size-only fitness; all repeated compression results must round-trip exactly."""
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
    while True:
        candidate = compress.compress(original)
        if candidate != packed or compress.decompress(candidate) != original:
            return 0
        if time.monotonic() - start >= 0.4:
            break
    return max(0, 100 * (1 - len(packed) / len(original)))


if __name__ == '__main__':
    try:
        print(main())
    except Exception:
        print(0)
