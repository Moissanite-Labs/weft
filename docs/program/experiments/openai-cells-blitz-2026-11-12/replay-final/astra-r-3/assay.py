"""Measure only size; repeat verified round trips for a stable workload."""
import time
import zlib
from pathlib import Path
import compress


def main():
    original = Path('corpus.txt').read_bytes()
    start = time.monotonic()
    packed = compress.compress(original)
    while True:
        if compress.decompress(packed) != original:
            print(0)
            return
        if time.monotonic() - start >= 0.4:
            break
        packed = compress.compress(original)
    Path('out.bin').write_bytes(packed)
    Path('restored.txt').write_bytes(compress.decompress(packed))
    print(100 * (1 - len(packed) / len(original)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)
