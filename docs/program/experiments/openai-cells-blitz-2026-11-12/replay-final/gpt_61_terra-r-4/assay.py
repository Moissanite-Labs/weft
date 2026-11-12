import pathlib, subprocess, sys
p = pathlib.Path('corpus.txt')
original = p.read_bytes()
try:
    for _ in range(6):
        subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'tmp/assay.bin'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run([sys.executable, 'compress.py', '--decompress', 'tmp/assay.bin', 'tmp/assay.txt'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pathlib.Path('tmp/assay.txt').read_bytes() != original:
            raise ValueError('round trip mismatch')
    n = pathlib.Path('tmp/assay.bin').stat().st_size
    print(max(0, 100 * (1 - n / len(original))))
except Exception:
    print(0)
