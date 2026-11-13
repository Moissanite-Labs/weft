#!/usr/bin/env python3
"""Self-contained lossless compressor; standard library only."""
import bz2
import sys
from pathlib import Path
from structure import prepare, restore


def compress(data):
    transformed = prepare(data, 0)
    if transformed is not None and restore(transformed) == data:
        return b'S' + bz2.compress(transformed, 9)
    return b'B' + bz2.compress(data, 9)


def decompress(data):
    raw = bz2.decompress(data[1:])
    if data[:1] == b'S':
        return restore(raw)
    if data[:1] == b'B':
        return raw
    raise ValueError('invalid archive')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
