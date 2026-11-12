"""Size fitness, with repeated byte-for-byte correctness checks."""
import types
from pathlib import Path
import subprocess
import sys
import time


def main():
    source = Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    if Path('restored.txt').read_bytes() != source:
        return 0
    packed = Path('out.bin').read_bytes()
    module = types.ModuleType('candidate')
    exec(compile(Path('compress.py').read_bytes(), 'compress.py', 'exec'), module.__dict__)
    deadline = time.monotonic() + 0.4
    while True:
        result = module.compress(source)
        if result != packed or module.decompress(result) != source:
            return 0
        if time.monotonic() >= deadline:
            break
    return max(0, 100 * (1 - len(packed) / len(source)))


try:
    print(main())
except Exception:
    print(0)
