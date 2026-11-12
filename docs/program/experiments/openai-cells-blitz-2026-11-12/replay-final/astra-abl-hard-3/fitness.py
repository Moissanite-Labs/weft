"""Repeated, verified round trips; output only the size-reduction score."""
import time
from pathlib import Path
import compress

def main():
    source = Path('corpus_hard.txt').read_bytes()
    start = time.monotonic()
    while True:
        packed = compress.compress(source)
        if compress.decompress(packed) != source:
            print(0)
            return
        if time.monotonic() - start >= 0.4:
            break
    Path('out.bin').write_bytes(packed)
    Path('restored.txt').write_bytes(compress.decompress(packed))
    print(100 * (1 - len(packed) / len(source)))

if __name__ == '__main__':
    main()
