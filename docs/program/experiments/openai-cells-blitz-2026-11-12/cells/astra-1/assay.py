"""Size-only fitness, checking both real CLI modes for at least 0.4 seconds."""
from pathlib import Path
import subprocess
import sys
import time


def main():
    try:
        original = Path('corpus.txt').read_bytes()
        start = time.perf_counter()
        size = None
        while size is None or time.perf_counter() - start < 0.4:
            subprocess.run([sys.executable, '-B', 'compress.py', 'corpus.txt', 'out.bin'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run([sys.executable, '-B', 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if Path('restored.txt').read_bytes() != original:
                return 0
            current = Path('out.bin').stat().st_size
            if size is not None and size != current:
                return 0
            size = current
        return max(0, 100 * (1 - size / len(original)))
    except Exception:
        return 0


if __name__ == '__main__':
    print(main())
