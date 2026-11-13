#!/usr/bin/env python3
"""Measure percentage reduction only after checking complete CLI round trips."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def score():
    root = Path(__file__).resolve().parent
    original = (root / 'corpus.txt').read_bytes()
    if not original:
        return 0.0
    deadline = time.perf_counter() + 0.45
    with tempfile.TemporaryDirectory(prefix='compression-assay-', dir=root) as tmp:
        packed = Path(tmp) / 'out.bin'
        restored = Path(tmp) / 'restored.txt'
        size = None
        while True:
            for args in (
                [str(root / 'corpus.txt'), str(packed)],
                ['--decompress', str(packed), str(restored)],
            ):
                subprocess.run(
                    [sys.executable, str(root / 'compress.py'), *args],
                    check=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=10,
                )
            if restored.read_bytes() != original:
                return 0.0
            current = packed.stat().st_size
            if size is not None and current != size:
                return 0.0
            size = current
            if time.perf_counter() >= deadline:
                break
    return 100.0 * (1.0 - size / len(original))


if __name__ == '__main__':
    try:
        print(f'{score():.12f}')
    except Exception:
        print(0)
