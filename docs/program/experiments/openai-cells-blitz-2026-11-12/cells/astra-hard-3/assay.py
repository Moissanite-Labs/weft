"""Check the file interface and repeated in-memory round trips before scoring."""
import pathlib
import subprocess
import sys
import time
import compress


def main():
    source = pathlib.Path('corpus_hard.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != source:
        return 0
    deadline = time.monotonic() + 0.4
    while time.monotonic() < deadline:
        trial = compress.compress(source)
        if compress.decompress(trial) != source or trial != packed:
            return 0
    return 100 * (1 - len(packed) / len(source))


if __name__ == '__main__':
    try:
        print(main())
    except Exception:
        print(0)
