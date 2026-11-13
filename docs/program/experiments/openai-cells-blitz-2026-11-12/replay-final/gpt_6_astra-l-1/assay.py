"""Measure actual file-size savings, accepting only byte-identical round trips."""
import pathlib
import subprocess
import sys
import time
import compress


def main():
    source = pathlib.Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True, stdout=subprocess.PIPE)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True, stdout=subprocess.PIPE)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != source:
        return 0
    end = time.monotonic() + 0.45
    while time.monotonic() < end:
        trial = compress.encode(source)
        if trial != packed or compress.decode(trial) != source:
            return 0
    return max(0, 100 * (1 - len(packed) / len(source)))


if __name__ == '__main__':
    try:
        print(main())
    except Exception:
        print(0)
