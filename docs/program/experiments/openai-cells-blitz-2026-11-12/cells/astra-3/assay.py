"""Measure losslessness and actual output size; repeat to amortize startup."""
import pathlib
import time


def main():
    namespace = {'__name__': 'compression_under_test'}
    exec(compile(pathlib.Path('compress.py').read_bytes(), 'compress.py', 'exec'), namespace)
    source = pathlib.Path('corpus.txt').read_bytes()
    start = time.perf_counter()
    try:
        while True:
            packed = namespace['compress'](source)
            pathlib.Path('out.bin').write_bytes(packed)
            restored = namespace['decompress'](pathlib.Path('out.bin').read_bytes())
            pathlib.Path('restored.txt').write_bytes(restored)
            if pathlib.Path('restored.txt').read_bytes() != source:
                print(0)
                return
            if time.perf_counter() - start >= 0.4:
                break
        print(100 * (1 - pathlib.Path('out.bin').stat().st_size / len(source)))
    except Exception:
        print(0)


if __name__ == '__main__':
    main()
