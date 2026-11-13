"""Measure actual output size; reject any incorrect round trip."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import compress


def measure():
    source = Path('corpus_hard.txt').read_bytes()
    with tempfile.TemporaryDirectory(dir='tmp') as directory:
        packed = Path(directory) / 'out.bin'
        restored = Path(directory) / 'restored.txt'
        for args in [('corpus_hard.txt', str(packed)), ('--decompress', str(packed), str(restored))]:
            subprocess.run([sys.executable, 'compress.py', *args], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if restored.read_bytes() != source:
            return 0
        blob = packed.read_bytes()
        start = time.perf_counter()
        # Real codec work, not process-launch overhead, dominates this assay.
        while time.perf_counter() - start < 0.45:
            candidate = compress.compress(source)
            if candidate != blob or compress.decompress(candidate) != source:
                return 0
        return 100 * (1 - len(blob) / len(source))


if __name__ == '__main__':
    try:
        print(measure())
    except Exception:
        print(0)
