#!/usr/bin/env python3
"""Byte-identical compression of structured corpus lines."""
import bz2
import sys
import core


def pack(data):
    return b'HC01' + core.pack(data)[4:]


def unpack(data):
    return core.unpack(data)


def main():
    if len(sys.argv) == 3:
        mode, source, dest = 'pack', sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        mode, source, dest = 'unpack', sys.argv[2], sys.argv[3]
    else:
        raise SystemExit('Usage: compress.py [--decompress] source destination')
    with open(source, 'rb') as f:
        data = f.read()
    result = pack(data) if mode == 'pack' else unpack(data)
    with open(dest, 'wb') as f:
        f.write(result)

if __name__ == '__main__':
    main()
