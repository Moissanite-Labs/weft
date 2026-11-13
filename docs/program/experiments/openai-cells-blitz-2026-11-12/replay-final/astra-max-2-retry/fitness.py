"""Score the actual archive, after a byte-for-byte round trip."""
from pathlib import Path
import time
import runpy

# Compile the current source, never a timestamp-cached version from another trial.
codec = runpy.run_path('compress.py')


def main():
    original = Path('corpus.txt').read_bytes()
    started = time.perf_counter()
    try:
        while True:
            archive = codec['compress'](original)
            restored = codec['decompress'](archive)
            if restored != original:
                print(0)
                return
            if time.perf_counter() - started >= 0.45:
                break
        Path('out.bin').write_bytes(archive)
        Path('restored.txt').write_bytes(restored)
        print(100 * (1 - len(archive) / len(original)))
    except Exception:
        print(0)


if __name__ == '__main__':
    main()
