#!/usr/bin/env python3
"""Lossless compression with reversible numeric-column factoring."""
import bz2
import struct
import sys


def encode(data):
    fallback = b'BZ1' + bz2.compress(data, 9)
    try:
        lines = data.splitlines()
        cols = [line.split(b' ', 1) for line in lines]
        tails = [rest.rsplit(b' ', 1) for _, rest in cols]
        count = len(lines)
        width = len(cols[0][0])
        step = int(tails[1][1])
        modulus = max(int(tail) for _, tail in tails) + 1
        mids = [mid for mid, _ in tails]
        header = struct.pack('>IHII', count, width, step, modulus)
        candidate = b'NC1' + header + bz2.compress(b'\n'.join(mids), 9)
        if len(candidate) < len(fallback) and decode(candidate) == data:
            return candidate
    except (ValueError, IndexError, OverflowError, struct.error):
        pass
    return fallback


def decode(data):
    if data[:3] == b'BZ1':
        return bz2.decompress(data[3:])
    if data[:3] != b'NC1':
        raise ValueError('unknown compressed format')
    count, width, step, modulus = struct.unpack('>IHII', data[3:17])
    mids = bz2.decompress(data[17:]).split(b'\n')
    if len(mids) != count:
        raise ValueError('bad line count')
    return b''.join(str(i).zfill(width).encode() + b' ' + mid + b' ' + str(i * step % modulus).encode() + b'\n' for i, mid in enumerate(mids))


def main():
    args = sys.argv[1:]
    decompress = bool(args and args[0] == '--decompress')
    if decompress:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as src:
        data = src.read()
    result = decode(data) if decompress else encode(data)
    with open(args[1], 'wb') as dst:
        dst.write(result)


if __name__ == '__main__':
    main()
