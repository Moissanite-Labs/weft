#!/usr/bin/env python3
"""Lossless compression using bulk mixed-radix packing and a bzip2 fallback."""
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


def pack(values, radix):
    value = 0
    for item in values:
        value = value * radix + item
    return value.to_bytes(width(radix, len(values)), 'big')


def unpack(data, count, radix):
    value = int.from_bytes(data, 'big')
    values = [0] * count
    for i in range(count-1, -1, -1):
        value, values[i] = divmod(value, radix)
    if value:
        raise ValueError('Value out of range')
    return values


def parse(data):
    types, records, hexes, base36s = [], [], [], []
    for line in data.splitlines(keepends=True):
        match = RECORD.fullmatch(line)
        if match:
            a, b, c = map(int, match.groups())
            types.append(0)
            records.append((a * 10**6 + b) * 10**9 + c)
        elif HEX.fullmatch(line):
            types.append(1)
            hexes.append(bytes.fromhex(line[:-1].decode('ascii')))
        elif BASE36.fullmatch(line):
            types.append(2)
            base36s.append(int(line[:-1], 36))
        else:
            return None
    if len(types) >= 2 ** 32:
        return None
    return types, records, hexes, base36s


def compress(data):
    fallback = MAGIC + b'B' + bz2.compress(data, compresslevel=9)
    parsed = parse(data)
    if parsed is None:
        return fallback
    types, records, hexes, base36s = parsed
    packed = (MAGIC + b'M' + len(types).to_bytes(4, 'big') + pack(types, 3) +
              pack(records, R) + b''.join(hexes) + pack(base36s, B))
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
    if data[4:5] != b'M' or len(data) < 9:
        raise ValueError('Invalid encoding')
    n = int.from_bytes(data[5:9], 'big')
    size = width(3, n)
    pos = 9 + size
    if pos > len(data):
        raise ValueError('Truncated type stream')
    types = unpack(data[9:pos], n, 3)
    nr, nh, nb = (types.count(i) for i in range(3))
    rs, hs, bs = width(R, nr), nh * 48, width(B, nb)
    if pos + rs + hs + bs != len(data):
        raise ValueError('Invalid payload length')
    records = iter(unpack(data[pos:pos+rs], nr, R))
    pos += rs
    hexes = iter(data[i:i+48] for i in range(pos, pos+hs, 48))
    pos += hs
    base36s = iter(unpack(data[pos:], nb, B))
    lines = []
    for kind in types:
        if kind == 0:
            lines.append(record(next(records)))
        elif kind == 1:
            lines.append(next(hexes).hex().encode('ascii') + b'\n')
        else:
            lines.append(base36(next(base36s)))
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
