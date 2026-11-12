"""Score the on-disk CLI and repeat its codec for a stable >=0.4s workload."""
import types
from pathlib import Path
import subprocess
import sys
import time


def score():
    start = time.perf_counter()
    original = Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True, stdout=subprocess.PIPE)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True, stdout=subprocess.PIPE)
    if Path('restored.txt').read_bytes() != original:
        return 0
    encoded = Path('out.bin').read_bytes()
    codec = types.ModuleType('codec')
    exec(compile(Path('compress.py').read_bytes(), 'compress.py', 'exec'), codec.__dict__)
    while time.perf_counter() - start < 0.4:
        trial = codec.compress(original)
        if trial != encoded or codec.decompress(trial) != original:
            return 0
    return 100 * (1 - len(encoded) / len(original))


try:
    print(score())
except Exception:
    print(0)
