"""Score the actual CLI, repeatedly so the workload is at least 0.5 seconds."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def main():
    root = Path.cwd()
    original = (root / 'corpus.txt').read_bytes()
    deadline = time.perf_counter() + 0.5
    sizes = []
    try:
        with tempfile.TemporaryDirectory(dir=root / 'tmp') as directory:
            packed = Path(directory) / 'packed.bin'
            restored = Path(directory) / 'restored.txt'
            while not sizes or time.perf_counter() < deadline:
                subprocess.run([sys.executable, str(root / 'compress.py'),
                                str(root / 'corpus.txt'), str(packed)],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run([sys.executable, str(root / 'compress.py'), '--decompress',
                                str(packed), str(restored)],
                               check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if restored.read_bytes() != original:
                    print(0)
                    return
                sizes.append(packed.stat().st_size)
        if len(set(sizes)) != 1 or not original:
            print(0)
        else:
            print(100 * (1 - sizes[0] / len(original)))
    except Exception:
        print(0)


if __name__ == '__main__':
    main()
