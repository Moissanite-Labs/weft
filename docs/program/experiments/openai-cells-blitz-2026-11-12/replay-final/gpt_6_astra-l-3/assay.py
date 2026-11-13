import os
import subprocess
import sys
import time
import compress

original = open('corpus.txt', 'rb').read()
start = time.monotonic()
valid = True
while True:
    packed = compress.compress(original)
    if compress.decompress(packed) != original:
        valid = False
        break
    if time.monotonic() - start >= 0.4:
        break
subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
valid = valid and open('restored.txt', 'rb').read() == original
print(100 * (1 - os.path.getsize('out.bin') / len(original)) if valid else 0)
