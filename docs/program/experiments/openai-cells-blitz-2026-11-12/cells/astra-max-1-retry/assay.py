"""Check the public CLI and time a substantial repeated round-trip workload."""
import subprocess
import sys
import time
from pathlib import Path


def score():
    import compress

    original = Path("corpus.txt").read_bytes()
    for args in (("corpus.txt", "out.bin"),
                 ("--decompress", "out.bin", "restored.txt")):
        subprocess.run([sys.executable, "compress.py", *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    packed = Path("out.bin").read_bytes()
    if Path("restored.txt").read_bytes() != original:
        return 0.0
    deadline = time.perf_counter() + 0.4
    while True:
        trial = compress.compress(original)
        if trial != packed or compress.decompress(trial) != original:
            return 0.0
        if time.perf_counter() >= deadline:
            break
    return 100.0 * (1.0 - len(packed) / len(original))


if __name__ == "__main__":
    try:
        result = score()
    except Exception:
        result = 0.0
    print(result)
