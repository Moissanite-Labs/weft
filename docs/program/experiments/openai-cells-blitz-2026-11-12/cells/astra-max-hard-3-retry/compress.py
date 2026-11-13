#!/usr/bin/env python3
"""Lossless stdlib compressor using grouped mixed-radix packing."""
import argparse
import bz2
import re
import zlib
from pathlib import Path

HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
RECORD = re.compile(rb'(\S+) line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'
RADICES = (256**48, 36**64, 10**21)


def width(radix, count):
    return ((pow(radix, count) - 1).bit_length() + 7) // 8


def pack(values, radix):
    value = 0
    for v in values:
        value = value * radix + v
    return value.to_bytes(width(radix, len(values)), 'big')


def unpack(data, radix, count):
    value = int.from_bytes(data, 'big')
    result = [0] * count
    for i in range(count - 1, -1, -1):
        value, result[i] = divmod(value, radix)
    if value:
        raise ValueError('Invalid mixed-radix value')
    return result


def parse(data):
    end = int(data.endswith(b'\n'))
    lines = data.split(b'\n')
    if end:
        lines.pop()
    types, groups, prefix = [], [[], [], []], None
    for line in lines:
        if HEX.fullmatch(line):
            t, value = 0, int(line, 16)
        elif BASE36.fullmatch(line):
            t, value = 1, int(line, 36)
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
            t, value = 2, x * 10**15 + y * 10**9 + z
        types.append(t)
        groups[t].append(value)
    prefix = prefix or b''
    n = len(types)
    if n >= 2**32:
        return None
    header = b'P2' + n.to_bytes(4, 'big') + bytes((end, len(prefix))) + prefix
    return header + pack(types, 3) + b''.join(pack(g, r) for g, r in zip(groups, RADICES))


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
    return bytes(result)


def record(value, prefix):
    value, c = divmod(value, 10**9)
    a, b = divmod(value, 10**6)
    return prefix + b' line ' + str(a).encode() + b' ratio 0.' + ('%06d' % b).encode() + b' select pick win seed ' + str(c).encode()


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] == b'Z':
        return zlib.decompress(data[1:])
    if data[:1] == b'R':
        return data[1:]
    if data[:2] != b'P2' or len(data) < 8:
        raise ValueError('Unknown compressed format')
    n = int.from_bytes(data[2:6], 'big')
    end, plen = data[6:8]
    if n > len(data) or end > 1:
        raise ValueError('Invalid header')
    prefix = data[8:8 + plen]
    p = 8 + plen
    size = width(3, n)
    if p + size > len(data):
        raise ValueError('Truncated types')
    types = unpack(data[p:p + size], 3, n)
    p += size
    groups = []
    for t, radix in enumerate(RADICES):
        count = types.count(t)
        size = width(radix, count)
        if p + size > len(data):
            raise ValueError('Truncated payload')
        groups.append(iter(unpack(data[p:p + size], radix, count)))
        p += size
    if p != len(data):
        raise ValueError('Trailing payload')
    lines = []
    for t in types:
        value = next(groups[t])
        if t == 0:
            lines.append(('%096x' % value).encode('ascii'))
        elif t == 1:
            lines.append(base36(value))
        else:
            lines.append(record(value, prefix))
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
