#!/usr/bin/env python3
"""Self-contained lossless compression with reversible numeric-column modeling."""
import bz2
import struct
import sys
from pathlib import Path


def transform(data):
    try:
        lines = data.splitlines()
        fields = [line.split(b' ', 1) for line in lines]
        width = len(fields[0][0])
        parts = [rest.rsplit(b' ', 1) for _, rest in fields]
        numbers = [int(x[1]) for x in parts]
        modulus = max(numbers) + 1
        step = numbers[1]
        bodies = [x[0] for x in parts]
        rebuilt = b''.join(str(i).zfill(width).encode() + b' ' + body + b' ' + str(i * step % modulus).encode() + b'\n' for i, body in enumerate(bodies))
        if rebuilt == data:
            return b'T' + struct.pack('<III', width, step, modulus) + b'\n'.join(bodies)
    except (ValueError, IndexError, OverflowError):
        pass
    return b'R' + data


def compress(data):
    return bz2.compress(transform(data), 9)


def decompress(data):
    raw = bz2.decompress(data)
    if raw[:1] == b'R':
        return raw[1:]
    if raw[:1] != b'T':
        raise ValueError('Unknown format')
    width, step, modulus = struct.unpack('<III', raw[1:13])
    return b''.join(str(i).zfill(width).encode() + b' ' + body + b' ' + str(i * step % modulus).encode() + b'\n' for i, body in enumerate(raw[13:].split(b'\n')))


def main():
    args = sys.argv[1:]
    decoding = bool(args and args[0] == '--decompress')
    if decoding:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decoding else compress(data))


if __name__ == '__main__':
    main()
