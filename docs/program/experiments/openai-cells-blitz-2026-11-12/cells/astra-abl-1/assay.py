"""Verify the CLI, then exercise the codec for at least 0.5 seconds."""
import pathlib
import subprocess
import sys
import time
import compress


def main():
    source = pathlib.Path('corpus.txt').read_bytes()
    start = time.perf_counter()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != source:
        print(0)
        return
    while time.perf_counter() - start < 0.5:
        test = compress.compress(source)
        if test != packed or compress.decompress(test) != source:
            print(0)
            return
    print(100 * (1 - len(packed) / len(source)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
