"""Measure actual file size, rejecting any byte mismatch."""
import time
from pathlib import Path
import compress

source = Path('corpus_hard.txt').read_bytes()
start = time.monotonic()
while True:
    encoded = compress.compress(source)
    if compress.decompress(encoded) != source:
        print(0)
        raise SystemExit(0)
    if time.monotonic() - start >= 0.4:
        break
Path('out.bin').write_bytes(encoded)
Path('restored.txt').write_bytes(compress.decompress(Path('out.bin').read_bytes()))
print(100 * (1 - len(encoded) / len(source)) if Path('restored.txt').read_bytes() == source else 0)
