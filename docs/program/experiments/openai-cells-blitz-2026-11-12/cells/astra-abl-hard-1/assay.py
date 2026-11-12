"""Repeat round trips to make the correctness assay substantial."""
from pathlib import Path
import time
import compress


def main():
    original = Path('corpus_hard.txt').read_bytes()
    deadline = time.perf_counter() + 0.5
    while True:
        packed = compress.compress(original)
        if compress.decompress(packed) != original:
            print(0)
            return
        if time.perf_counter() >= deadline:
            break
    Path('out.bin').write_bytes(packed)
    Path('restored.txt').write_bytes(compress.decompress(packed))
    print(100 * (1 - len(packed) / len(original)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
