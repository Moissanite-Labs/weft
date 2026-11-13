#!/usr/bin/env python3
"""Stdlib lossless compressor. Usage: compress.py [--decompress] INPUT OUTPUT."""
import bz2
import json
import sys
from pathlib import Path

MAGIC = b'CL2'


def render(meta, bodies):
    n, width, first, step, start, delta, modulus = meta
    return b''.join((f'{first + i * step:0{width}d} '.encode() + body +
                     f' {(start + i * delta) % modulus}\n'.encode())
                    for i, body in enumerate(bodies))


def split_records(data):
    if not data.endswith(b'\n'):
        raise ValueError('not newline-terminated records')
    lines = data[:-1].split(b'\n')
    if len(lines) < 2:
        raise ValueError('too few records')
    left, bodies, right = [], [], []
    for line in lines:
        a, rest = line.split(b' ', 1)
        body, b = rest.rsplit(b' ', 1)
        left.append(a)
        bodies.append(body)
        right.append(int(b))
    first = int(left[0])
    step = int(left[1]) - first
    modulus = max(right) + 1
    if modulus <= 0:
        raise ValueError('no modular counter')
    meta = [len(lines), len(left[0]), first, step, right[0],
            (right[1] - right[0]) % modulus, modulus]
    if render(meta, bodies) != data:
        raise ValueError('counters are not predictable')
    return meta, bodies


def compress(data):
    best = MAGIC + b'B' + bz2.compress(data, 9)
    try:
        meta, bodies = split_records(data)
        payload = json.dumps(meta, separators=(',', ':')).encode() + b'\n' + b'\n'.join(bodies)
        candidate = MAGIC + b'S' + bz2.compress(payload, 9)
        if len(candidate) < len(best):
            best = candidate
    except (ValueError, IndexError, OverflowError):
        pass
    return best


def decompress(data):
    if not data.startswith(MAGIC):
        raise ValueError('not a CL2 file')
    payload = bz2.decompress(data[4:])
    if data[3:4] == b'B':
        return payload
    if data[3:4] != b'S':
        raise ValueError('unknown codec')
    header, bodies = payload.split(b'\n', 1)
    meta = json.loads(header)
    bodies = bodies.split(b'\n')
    if len(bodies) != meta[0]:
        raise ValueError('wrong record count')
    return render(meta, bodies)


def main():
    args = sys.argv[1:]
    decoding = bool(args and args[0] == '--decompress')
    if decoding:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit(__doc__)
    source, target = map(Path, args)
    target.write_bytes((decompress if decoding else compress)(source.read_bytes()))


if __name__ == '__main__':
    main()
