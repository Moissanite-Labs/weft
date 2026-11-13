#!/usr/bin/env python3
import argparse
import bz2
import lzma
import sys
from pathlib import Path

MAGIC = b'CRP1'
MODE_Z = 0
MODE_B = 1
MODE_X = 2


def choose(data: bytes):
    options = [
        (MODE_Z, zlib_compress(data)),
        (MODE_B, bz2.compress(data, compresslevel=9)),
        (MODE_X, lzma.compress(data, format=lzma.FORMAT_ALONE, preset=6)),
    ]
    return min(options, key=lambda t: len(t[1]))


def zlib_compress(data: bytes) -> bytes:
    import zlib
    return zlib.compress(data, 9)


def compress_file(inp: str, outp: str) -> None:
    data = Path(inp).read_bytes()
    mode, payload = choose(data)
    Path(outp).write_bytes(MAGIC + bytes([mode]) + payload)


def decompress_file(inp: str, outp: str) -> None:
    raw = Path(inp).read_bytes()
    if not raw.startswith(MAGIC) or len(raw) < len(MAGIC) + 1:
        raise SystemExit('bad input')
    mode = raw[len(MAGIC)]
    payload = raw[len(MAGIC) + 1:]
    if mode == MODE_Z:
        import zlib
        data = zlib.decompress(payload)
    elif mode == MODE_B:
        data = bz2.decompress(payload)
    elif mode == MODE_X:
        data = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    else:
        raise SystemExit('bad mode')
    Path(outp).write_bytes(data)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--decompress', action='store_true')
    p.add_argument('input')
    p.add_argument('output')
    a = p.parse_args(argv)
    if a.decompress:
        decompress_file(a.input, a.output)
    else:
        compress_file(a.input, a.output)


if __name__ == '__main__':
    main()
