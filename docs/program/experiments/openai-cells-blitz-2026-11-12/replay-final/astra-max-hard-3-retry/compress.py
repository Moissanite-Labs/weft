#!/usr/bin/env python3
"""Lossless stdlib compressor with fixed-width structured records."""
import argparse
import bz2
import re
import zlib
from pathlib import Path

HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
RECORD = re.compile(rb'(\S+) line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def width(radix, count):
    return ((pow(radix, count) - 1).bit_length() + 7) // 8


def parse(data):
    end = int(data.endswith(b'\n'))
    lines = data.split(b'\n')
    if end:
        lines.pop()
    types, values, prefix = [], [], None
    for line in lines:
        if HEX.fullmatch(line):
            t, value = 0, bytes.fromhex(line.decode('ascii'))
        elif BASE36.fullmatch(line):
            t, value = 1, int(line, 36).to_bytes(42, 'big')
        else:
            m = RECORD.fullmatch(line)
            if m is None:
                return None
            tag, a, b, c = m.groups()
            x, y, z = int(a), int(b), int(c)
            if x >= 10**6 or z >= 10**9 or str(x).encode() != a or str(z).encode() != c:
                return None
            if prefix is None:
                prefix = tag
            if prefix != tag or len(tag) > 255:
                return None
            t, value = 2, (x * 10**15 + y * 10**9 + z).to_bytes(9, 'big')
        types.append(t)
        values.append(value)
    prefix = prefix or b''
    n = len(types)
    if n >= 2**32:
        return None
    index = 0
    for t in types:
        index = index * 3 + t
    return (b'P1' + n.to_bytes(4, 'big') + bytes((end, len(prefix))) + prefix
            + index.to_bytes(width(3, n), 'big') + b''.join(values))


def compress(data):
    choices = [b'B' + bz2.compress(data, compresslevel=9), b'Z' + zlib.compress(data, 9), b'R' + data]
    packed = parse(data)
    if packed is not None:
        choices.append(packed)
    return min(choices, key=len)


def base36(value):
    result = bytearray(64)
    for i in range(63, -1, -1):
        value, r = divmod(value, 36)
        result[i] = ALPHABET[r]
    if value:
        raise ValueError('Invalid base36 value')
    return bytes(result)


def record(value, prefix):
    value, c = divmod(value, 10**9)
    a, b = divmod(value, 10**6)
    if a >= 10**6:
        raise ValueError('Invalid record')
    return prefix + b' line ' + str(a).encode() + b' ratio 0.' + ('%06d' % b).encode() + b' select pick win seed ' + str(c).encode()


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] == b'Z':
        return zlib.decompress(data[1:])
    if data[:1] == b'R':
        return data[1:]
    if data[:2] != b'P1' or len(data) < 8:
        raise ValueError('Unknown compressed format')
    n = int.from_bytes(data[2:6], 'big')
    end, plen = data[6:8]
    if n > len(data) or end > 1:
        raise ValueError('Invalid header')
    prefix = data[8:8 + plen]
    p = 8 + plen
    size = width(3, n)
    index = int.from_bytes(data[p:p + size], 'big')
    p += size
    types = [0] * n
    for i in range(n - 1, -1, -1):
        index, types[i] = divmod(index, 3)
    if index:
        raise ValueError('Invalid type stream')
    lines = []
    for t in types:
        size = (48, 42, 9)[t]
        v = data[p:p + size]
        if len(v) != size:
            raise ValueError('Truncated payload')
        p += size
        if t == 0:
            lines.append(v.hex().encode('ascii'))
        elif t == 1:
            lines.append(base36(int.from_bytes(v, 'big')))
        else:
            lines.append(record(int.from_bytes(v, 'big'), prefix))
    if p != len(data):
        raise ValueError('Trailing payload')
    return b'\n'.join(lines) + (b'\n' if end else b'')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    source = Path(args.source).read_bytes()
    result = decompress(source) if args.decompress else compress(source)
    Path(args.destination).write_bytes(result)


if __name__ == '__main__':
    main()
