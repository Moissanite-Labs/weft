import os
import subprocess
import sys

for _ in range(4):
    if subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'tmp/out.bin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode:
        print(0); raise SystemExit
    if subprocess.run([sys.executable, 'compress.py', '--decompress', 'tmp/out.bin', 'tmp/restored.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode:
        print(0); raise SystemExit
    if open('corpus.txt', 'rb').read() != open('tmp/restored.txt', 'rb').read():
        print(0); raise SystemExit
print(100 * (1 - os.path.getsize('tmp/out.bin') / os.path.getsize('corpus.txt')))
