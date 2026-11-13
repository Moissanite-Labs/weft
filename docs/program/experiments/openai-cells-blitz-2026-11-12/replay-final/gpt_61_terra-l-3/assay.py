import subprocess
from pathlib import Path

source = Path('corpus.txt').read_bytes()
for _ in range(2):
    subprocess.run(['python3', 'compress.py', 'corpus.txt', 'tmp/assay.bin'], check=True)
    subprocess.run(['python3', 'compress.py', '--decompress', 'tmp/assay.bin', 'tmp/assay.txt'], check=True)
    if Path('tmp/assay.txt').read_bytes() != source:
        print(0)
        break
else:
    print(100 * (1 - Path('tmp/assay.bin').stat().st_size / len(source)))
