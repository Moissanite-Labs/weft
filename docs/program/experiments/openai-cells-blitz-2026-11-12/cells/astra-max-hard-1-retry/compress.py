#!/usr/bin/env python3
"""Lossless stdlib compression with compact encodings for structured text."""
import argparse
import bz2
import re
from pathlib import Path

SCHEME = 2
TEMPLATE = re.compile(rb'e18a line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'
RADICES = (10**21, 1 << 384, 36**64)
BINARY_RADICES = (1 << 70, 1 << 384, 1 << 331)


def encode(data):
    fallback = b'HC0' + bz2.compress(data, compresslevel=9)
    newline = data.endswith(b'\n')
    lines = data.split(b'\n')
    if newline:
        lines.pop()
    state = 1
    radices = RADICES if SCHEME == 2 else BINARY_RADICES
    for line in lines:
        m = TEMPLATE.fullmatch(line)
        if m:
            a, b, c = map(int, m.groups())
            kind, value = 0, (a * 10**6 + b) * 10**9 + c
        elif HEX.fullmatch(line):
            kind, value = 1, int(line, 16)
        elif BASE36.fullmatch(line):
            kind, value = 2, int(line, 36)
        else:
            return fallback
        state = state * radices[kind] + value
        if SCHEME == 0:
            state = (state << 2) | kind
        elif kind == 0:
            state <<= 1
        else:
            state = (state << 2) | (1 if kind == 1 else 3)
    packed = b'HC1' + bytes([SCHEME * 2 + newline]) + state.to_bytes((state.bit_length() + 7) // 8, 'big')
    return min((fallback, packed), key=len)


def base36(value):
    out = bytearray(64)
    for i in range(63, -1, -1):
        value, digit = divmod(value, 36)
        out[i] = ALPHABET[digit]
    if value:
        raise ValueError('base36 field overflow')
    return bytes(out)


def decode(data):
    if data[:3] == b'HC0':
        return bz2.decompress(data[3:])
    if data[:3] != b'HC1' or len(data) < 5:
        raise ValueError('not a supported compressed file')
    scheme, newline = divmod(data[3], 2)
    if scheme > 2:
        raise ValueError('unsupported encoding')
    radices = RADICES if scheme == 2 else BINARY_RADICES
    state = int.from_bytes(data[4:], 'big')
    lines = []
    while state > 1:
        if scheme == 0:
            kind, state = state & 3, state >> 2
        elif state & 1:
            kind, state = 1 + ((state >> 1) & 1), state >> 2
        else:
            kind, state = 0, state >> 1
        if kind > 2:
            raise ValueError('bad record type')
        state, value = divmod(state, radices[kind])
        if kind == 0:
            a, c = divmod(value, 10**9)
            a, b = divmod(a, 10**6)
            line = f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}'.encode('ascii')
        elif kind == 1:
            line = f'{value:096x}'.encode('ascii')
        else:
            line = base36(value)
        lines.append(line)
    if state != 1:
        raise ValueError('truncated or invalid payload')
    lines.reverse()
    return b'\n'.join(lines) + (b'\n' if newline else b'')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    data = Path(args.source).read_bytes()
    Path(args.destination).write_bytes(decode(data) if args.decompress else encode(data))


if __name__ == '__main__':
    main()
