"""Validate the CLI and measure percentage size reduction (not speed)."""
import runpy
import subprocess
import sys
import time
from pathlib import Path


def main():
    source = Path('corpus_hard.txt').read_bytes()
    try:
        # Execute source afresh: variants can have equal size and mtime, which
        # would otherwise permit a stale Python bytecode cache.
        codec = runpy.run_path('compress.py')
        encode, decode = codec['encode'], codec['decode']
        subprocess.run([sys.executable, 'compress.py', 'corpus_hard.txt', 'out.bin'],
                       check=True, capture_output=True)
        subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'],
                       check=True, capture_output=True)
        packed = Path('out.bin').read_bytes()
        if Path('restored.txt').read_bytes() != source:
            print(0)
            return
        # Repeat real compression/decompression work to amortize process startup.
        start = time.perf_counter()
        while time.perf_counter() - start < 0.5:
            trial = encode(source)
            if trial != packed or decode(trial) != source:
                print(0)
                return
        print(100 * (1 - len(packed) / len(source)))
    except Exception:
        print(0)


if __name__ == '__main__':
    main()
