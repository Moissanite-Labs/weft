#!/usr/bin/env python3
"""Lossless compression of text, with packed numeric/hex/base36 records."""
import bz2
import re
import sys
from pathlib import Path

MAGIC = b'CHC2'
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'
RECORD = re.compile(rb'e18a line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})\n')
HEX = re.compile(rb'[0-9a-f]{96}\n')
BASE36 = re.compile(rb'[0-9a-z]{64}\n')
R = 10 ** 21
B = 36 ** 64


def width(radix, count):
    return ((radix ** count - 1).bit_length() + 7) // 8


def parse(data):
    types, values = [], []
    for line in data.splitlines(keepends=True):
        match = RECORD.fullmatch(line)
        if match:
            a, b, c = map(int, match.groups())
            types.append(0)
            values.append(((a * 10**6 + b) * 10**9 + c).to_bytes(9, 'big'))
        elif HEX.fullmatch(line):
            types.append(1)
            values.append(bytes.fromhex(line[:-1].decode('ascii')))
        elif BASE36.fullmatch(line):
            types.append(2)
            values.append(int(line[:-1], 36).to_bytes(42, 'big'))
        else:
            return None
    if len(types) >= 2 ** 32:
        return None
    return types, values


def compress(data):
    fallback = MAGIC + b'B' + bz2.compress(data, compresslevel=9)
    parsed = parse(data)
    if parsed is None:
        return fallback
    types, values = parsed
    order = 0
    for kind in types:
        order = order * 3 + kind
    packed = (MAGIC + b'S' + len(types).to_bytes(4, 'big') +
              order.to_bytes(width(3, len(types)), 'big') + b''.join(values))
    return min((fallback, packed), key=len)


def record(value):
    ab, c = divmod(value, 10**9)
    a, b = divmod(ab, 10**6)
    return b'e18a line %d ratio 0.%06d select pick win seed %d\n' % (a, b, c)


def base36(value):
    text = bytearray(65)
    text[64] = 10
    for i in range(63, -1, -1):
        value, digit = divmod(value, 36)
        text[i] = ALPHABET[digit]
    if value:
        raise ValueError('Base36 value out of range')
    return bytes(text)


def decompress(data):
    if data[:4] == b'CHC1':
        return bz2.decompress(data[4:])
    if data[:4] != MAGIC:
        raise ValueError('Invalid file signature')
    if data[4:5] == b'B':
        return bz2.decompress(data[5:])
    if data[4:5] != b'S' or len(data) < 9:
        raise ValueError('Invalid encoding')
    n = int.from_bytes(data[5:9], 'big')
    size = width(3, n)
    pos = 9 + size
    if pos > len(data):
        raise ValueError('Truncated type stream')
    order = int.from_bytes(data[9:pos], 'big')
    types = [0] * n
    for i in range(n-1, -1, -1):
        order, types[i] = divmod(order, 3)
    if order:
        raise ValueError('Invalid type stream')
    lines = []
    for kind in types:
        size = (9, 48, 42)[kind]
        chunk = data[pos:pos+size]
        if len(chunk) != size:
            raise ValueError('Truncated payload')
        pos += size
        if kind == 0:
            value = int.from_bytes(chunk, 'big')
            if value >= R:
                raise ValueError('Record out of range')
            lines.append(record(value))
        elif kind == 1:
            lines.append(chunk.hex().encode('ascii') + b'\n')
        else:
            lines.append(base36(int.from_bytes(chunk, 'big')))
    if pos != len(data):
        raise ValueError('Trailing payload')
    return b''.join(lines)


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
