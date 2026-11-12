"""Time-amortized round-trip check; fitness is solely size reduction."""
import time
import sys
from pathlib import Path
import compress


def main():
    source = Path('corpus.txt').read_bytes()
    end = time.perf_counter() + 0.5
    while True:
        packed = compress.compress(source)
        if compress.decompress(packed) != source:
            print(0)
            return
        if time.perf_counter() >= end:
            break
    Path('out.bin').write_bytes(packed)
    print(100 * (1 - len(packed) / len(source)))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        print(0)
