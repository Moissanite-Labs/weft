"""Reversible column transform for numeric records and printable random data.

Unknown inputs use the outer compressor's ordinary byte-oriented fallback.
No source file is needed by the inverse transform.
"""
import re
import struct
import zlib

RECORD = re.compile(rb'([a-z0-9]+) line (0|[1-9][0-9]*) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]*)\n')
HEX = re.compile(rb'[0-9a-f]{96}\n')
BASE = re.compile(rb'[0-9a-z]{64}\n')
RADIX = 10**21
BASE_RADIX = 36**64
ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


def pack_numbers(values, radix, aggregate):
    if not aggregate:
        width = ((radix - 1).bit_length() + 7) // 8
        return b''.join(v.to_bytes(width, 'big') for v in values)
    value = 0
    for v in values:
        value = value * radix + v
    return value.to_bytes((value.bit_length() + 7) // 8, 'big')


def unpack_numbers(data, count, radix, aggregate):
    if not aggregate:
        width = ((radix - 1).bit_length() + 7) // 8
        return [int.from_bytes(data[i:i+width], 'big') for i in range(0, len(data), width)]
    value = int.from_bytes(data, 'big')
    out = [0] * count
    for i in range(count - 1, -1, -1):
        value, out[i] = divmod(value, radix)
    return out


def encode(data, aggregate):
    tags = bytearray()
    hexes = bytearray()
    bases = []
    numbers = []
    prefix = None
    for line in data.splitlines(keepends=True):
        match = RECORD.fullmatch(line)
        if match:
            p, a, b, c = match.groups()
            if prefix is None:
                prefix = p
            a, b, c = int(a), int(b), int(c)
            if p != prefix or a >= 10**6 or c >= 10**9:
                return None
            tags.append(2)
            numbers.append((a * 10**6 + b) * 10**9 + c)
        elif HEX.fullmatch(line):
            tags.append(0)
            hexes.extend(bytes.fromhex(line.decode('ascii')))
        elif BASE.fullmatch(line):
            tags.append(1)
            bases.append(int(line, 36))
        else:
            return None
    parts = [prefix or b'', zlib.compress(bytes(tags), 9), bytes(hexes),
             pack_numbers(bases, BASE_RADIX, aggregate),
             pack_numbers(numbers, RADIX, aggregate)]
    return bytes([aggregate]) + struct.pack('>5I', *map(len, parts)) + b''.join(parts)


def decode(data):
    aggregate = data[0]
    lengths = struct.unpack('>5I', data[1:21])
    parts = []
    offset = 21
    for length in lengths:
        parts.append(data[offset:offset + length])
        offset += length
    prefix, tags, hexes, bases, numbers = parts
    tags = zlib.decompress(tags)
    base_values = iter(unpack_numbers(bases, tags.count(1), BASE_RADIX, aggregate))
    numeric_values = iter(unpack_numbers(numbers, tags.count(2), RADIX, aggregate))
    out = []
    h = 0
    for tag in tags:
        if tag == 0:
            out.append(hexes[h:h+48].hex().encode() + b'\n')
            h += 48
        elif tag == 1:
            value = next(base_values)
            digits = []
            for _ in range(64):
                value, digit = divmod(value, 36)
                digits.append(ALPHABET[digit])
            out.append(''.join(reversed(digits)).encode() + b'\n')
        elif tag == 2:
            ab, c = divmod(next(numeric_values), 10**9)
            a, b = divmod(ab, 10**6)
            out.append(prefix + (' line %d ratio 0.%06d select pick win seed %d\n' % (a, b, c)).encode())
        else:
            raise ValueError('invalid record tag')
    return b''.join(out)


"""Lossless standard-library compressor with reversible record transforms."""
import bz2
import sys
from pathlib import Path


def compress(data):
    candidates = [b'B' + bz2.compress(data, 9)]
    packed = encode(data, True)
    if packed is not None:
        candidates.extend([b'T' + packed, b'Z' + bz2.compress(packed, 9)])
    return min(candidates, key=len)


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] == b'T':
        return decode(data[1:])
    if data[:1] == b'Z':
        return decode(bz2.decompress(data[1:]))
    raise ValueError('invalid compressed file')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        Path(args[2]).write_bytes(decompress(Path(args[1]).read_bytes()))
    elif len(args) == 2:
        Path(args[1]).write_bytes(compress(Path(args[0]).read_bytes()))
    else:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
