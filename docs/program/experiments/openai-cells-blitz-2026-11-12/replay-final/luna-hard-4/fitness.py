import os
import subprocess
import sys

src = "corpus_hard.txt"
n = os.path.getsize(src)
for _ in range(12):
    a = subprocess.run([sys.executable, "compress.py", src, "fitness.bin"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    b = subprocess.run([sys.executable, "compress.py", "--decompress", "fitness.bin", "fitness.txt"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if a.returncode or b.returncode:
        print(0)
        raise SystemExit
    with open(src, "rb") as f:
        original = f.read()
    with open("fitness.txt", "rb") as f:
        restored = f.read()
    if original != restored:
        print(0)
        raise SystemExit
size = os.path.getsize("fitness.bin")
print(100 * (1 - size / n))
