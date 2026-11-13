import pathlib
import subprocess
import sys
import time

source = pathlib.Path('corpus.txt').read_bytes()
start = time.perf_counter()
try:
    while True:
        subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True, stdout=subprocess.PIPE)
        subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True, stdout=subprocess.PIPE)
        if pathlib.Path('restored.txt').read_bytes() != source:
            print(0)
            break
        if time.perf_counter() - start >= 0.6:
            print(100 * (1 - pathlib.Path('out.bin').stat().st_size / len(source)))
            break
except Exception:
    print(0)
