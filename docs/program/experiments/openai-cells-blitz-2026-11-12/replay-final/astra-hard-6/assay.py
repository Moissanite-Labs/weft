"""Correctness-gated size fitness; repeated work amortizes interpreter startup."""
from pathlib import Path
import time
import compress

source = Path('corpus_hard.txt').read_bytes()
start = time.perf_counter()
try:
    encoded = compress.compress(source)
    if compress.decompress(encoded) != source:
        print(0)
    else:
        correct = True
        count = 0
        while time.perf_counter() - start < 0.45 or count < 3:
            candidate = compress.compress(source)
            if candidate != encoded or compress.decompress(candidate) != source:
                correct = False
                break
            count += 1
        Path('out.bin').write_bytes(encoded)
        print(100 * (1 - len(encoded) / len(source)) if correct else 0)
except Exception:
    print(0)
