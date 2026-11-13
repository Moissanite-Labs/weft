#!/usr/bin/env python3
"""Lossless compression with reversible numeric-column prediction."""
import bz2
import json
import re
import sys


def compress(data):
    raw = b'B' + bz2.compress(data, 9)
    rows = [re.fullmatch(rb'(\d+) (.*) (\d+)\n', line) for line in data.splitlines(keepends=True)]
    if not rows or not all(rows):
        return raw
    n = len(rows)
    width = len(rows[0][1])
    modulus = max(int(r[3]) for r in rows) + 1
    step = int(rows[1][3]) if n > 1 else 0
    if not all(r[1] == str(i).zfill(width).encode() and r[3] == str(i * step % modulus).encode() for i, r in enumerate(rows)):
        return raw
    header = json.dumps([n, width, step, modulus], separators=(',', ':')).encode()
    payload = header + b'\n' + b'\n'.join(r[2] for r in rows)
    packed = b'N' + bz2.compress(payload, 9)
    return min((raw, packed), key=len)


def decompress(data):
    payload = bz2.decompress(data[1:])
    if data[:1] == b'B':
        return payload
    if data[:1] != b'N':
        raise ValueError('Invalid compressed file')
    header, body = payload.split(b'\n', 1)
    n, width, step, modulus = json.loads(header)
    rows = body.split(b'\n')
    if len(rows) != n:
        raise ValueError('Invalid row count')
    return b''.join(str(i).zfill(width).encode() + b' ' + text + b' ' + str(i * step % modulus).encode() + b'\n' for i, text in enumerate(rows))


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
