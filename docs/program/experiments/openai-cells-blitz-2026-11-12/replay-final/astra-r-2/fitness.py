import pathlib
import subprocess
import sys
import time
import compress


def main():
    try:
        original = pathlib.Path('corpus.txt').read_bytes()
        subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
        subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
        packed = pathlib.Path('out.bin').read_bytes()
        if pathlib.Path('restored.txt').read_bytes() != original:
            return 0
        start = time.perf_counter()
        while time.perf_counter() - start < 0.35:
            trial = compress.compress(original)
            if trial != packed or compress.decompress(trial) != original:
                return 0
        return 100 * (1 - len(packed) / len(original))
    except Exception:
        return 0


print(main())
