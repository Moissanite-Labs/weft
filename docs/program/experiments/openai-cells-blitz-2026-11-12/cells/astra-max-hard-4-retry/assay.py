"""Score actual CLI output, check exact recovery, and repeat for >=0.4 seconds."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def evaluate():
    start = time.monotonic()
    root = Path(__file__).resolve().parent
    original = (root / 'corpus_hard.txt').read_bytes()
    with tempfile.TemporaryDirectory(dir=root / 'tmp') as folder:
        packed = Path(folder) / 'out.bin'
        restored = Path(folder) / 'restored.txt'
        for args in [(str(root / 'corpus_hard.txt'), str(packed)),
                     ('--decompress', str(packed), str(restored))]:
            subprocess.run([sys.executable, str(root / 'compress.py'), *args],
                           check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=15)
        if restored.read_bytes() != original:
            return 0
        encoded = packed.read_bytes()
    spec = importlib.util.spec_from_file_location('candidate', root / 'compress.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    while time.monotonic() - start < 0.4:
        trial = module.compress(original)
        if trial != encoded or module.decompress(trial) != original:
            return 0
    return 100 * (1 - len(encoded) / len(original))


if __name__ == '__main__':
    try:
        print(evaluate())
    except Exception:
        print(0)
