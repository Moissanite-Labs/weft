"""Verify the CLI and exercise repeated independent round trips before scoring."""
import pathlib
import subprocess
import sys
import time
import types
compress = types.ModuleType("codec_under_test")
exec(compile(pathlib.Path("compress.py").read_text(), "compress.py", "exec"), compress.__dict__)


def main():
    source = pathlib.Path('corpus.txt').read_bytes()
    subprocess.run([sys.executable, 'compress.py', 'corpus.txt', 'out.bin'], check=True)
    subprocess.run([sys.executable, 'compress.py', '--decompress', 'out.bin', 'restored.txt'], check=True)
    packed = pathlib.Path('out.bin').read_bytes()
    if pathlib.Path('restored.txt').read_bytes() != source:
        return 0
    deadline = time.monotonic() + 0.35
    while time.monotonic() < deadline:
        test = compress.compress(source)
        if test != packed or compress.decompress(test) != source:
            return 0
    return 100 * (1 - len(packed) / len(source))


if __name__ == '__main__':
    try:
        print(main())
    except Exception:
        print(0)
