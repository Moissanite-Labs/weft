#!/usr/bin/env python3
"""Small, self-contained lossless compressor using only the standard library."""
import bz2
import lzma
from pathlib import Path
import sys
import zlib

MAGIC = b'CH1'


def compress(data):
    choices = [b'R' + data,
               b'Z' + zlib.compress(data, 9),
               b'B' + bz2.compress(data, 9),
               b'L' + lzma.compress(data, preset=9)]
    return MAGIC + min(choices, key=len)


def decompress(data):
    if not data.startswith(MAGIC) or len(data) < 4:
        raise ValueError('Not a CH1 compressed file')
    tag, payload = data[3:4], data[4:]
    if tag == b'R':
        return payload
    codecs = {b'Z': zlib.decompress, b'B': bz2.decompress,
              b'L': lzma.decompress}
    if tag not in codecs:
        raise ValueError('Unknown compression method')
    return codecs[tag](payload)


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('Usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
