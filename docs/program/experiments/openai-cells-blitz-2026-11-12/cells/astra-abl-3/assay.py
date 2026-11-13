"""Measure size only after checking the real command-line round trip."""
import pathlib
import subprocess
import sys
import time


def main():
    start = time.perf_counter()
    original = pathlib.Path('corpus.txt').read_bytes()
    while True:
        for args in [('corpus.txt', 'out.bin'), ('--decompress', 'out.bin', 'restored.txt')]:
            subprocess.run([sys.executable, 'compress.py', *args], check=True)
        if pathlib.Path('restored.txt').read_bytes() != original:
            print(0)
            return
        if time.perf_counter() - start >= 0.4:
            break
    print(100 * (1 - pathlib.Path('out.bin').stat().st_size / len(original)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
