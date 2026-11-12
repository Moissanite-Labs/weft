import os
import subprocess
import sys

try:
    for _ in range(2):
        subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'tmp/out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'tmp/out.bin', 'tmp/restored.txt'], check=True)
    original = open('corpus.txt', 'rb').read()
    restored = open('tmp/restored.txt', 'rb').read()
    print(100 * (1 - os.path.getsize('tmp/out.bin') / len(original)) if original == restored else 0)
except Exception:
    print(0)
