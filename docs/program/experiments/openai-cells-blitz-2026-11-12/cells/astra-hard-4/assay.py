"""Repeat real compression and byte verification to amortize startup cost."""
import time
from pathlib import Path
import compress


def main():
    try:
        original = Path('corpus_hard.txt').read_bytes()
        deadline = time.monotonic() + 0.5
        while True:
            packed = compress.compress(original)
            if compress.decompress(packed) != original:
                print(0)
                return
            if time.monotonic() >= deadline:
                break
        Path('out.bin').write_bytes(packed)
        print(100 * (1 - len(packed) / len(original)))
    except Exception:
        print(0)


if __name__ == '__main__':
    main()
