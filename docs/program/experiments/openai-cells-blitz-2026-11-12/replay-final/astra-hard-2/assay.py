"""Check CLI and repeat round trips for a substantial correctness workload."""
import pathlib
import subprocess
import sys
import time
import compress


def main():
    original = pathlib.Path('corpus_hard.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    encoded = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != original:
        print(0)
        return
    deadline = time.monotonic() + 0.4
    while True:
        packed = compress.compress(original)
        if packed != encoded or compress.decompress(packed) != original:
            print(0)
            return
        if time.monotonic() >= deadline:
            break
    print(100 * (1 - len(encoded) / len(original)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
