#!/usr/bin/env python3
"""Lossless stdlib-only compressor with reversible record packing."""
import bz2
import sys
from pathlib import Path
import math
import re
import struct
import zlib
import bz2

PATTERN = re.compile(rb'([^\n ]+) line (0|[1-9][0-9]*) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]*)')
ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


def to_radix(values, base):
    number = 0
    for value in values:
        number = number * base + value
    length = ((base ** len(values) - 1).bit_length() + 7) // 8
    return number.to_bytes(length, 'big')


def from_radix(data, count, base):
    number = int.from_bytes(data, 'big')
    result = [0] * count
    for i in range(count - 1, -1, -1):
        number, result[i] = divmod(number, base)
    if number:
        raise ValueError('Invalid packed integer')
    return result


def base36(number):
    chars = ['0'] * 64
    for i in range(63, -1, -1):
        number, digit = divmod(number, 36)
        chars[i] = ALPHABET[digit]
    return ''.join(chars).encode('ascii')


def pack(data, mode=0):
    if not data.endswith(b'\n'):
        raise ValueError('not newline terminated')
    types = bytearray()
    hexes = bytearray()
    words = []
    numbers = []
    prefix = None
    for line in data[:-1].split(b'\n'):
        match = PATTERN.fullmatch(line)
        if match:
            p, a, b, c = match.groups()
            if prefix is None:
                prefix = p
            if p != prefix:
                raise ValueError('different prefixes')
            a, b, c = int(a), int(b), int(c)
            if a >= 10**6 or c >= 10**9:
                raise ValueError('number out of range')
            types.append(0)
            numbers.append((a * 10**6 + b) * 10**9 + c)
        elif re.fullmatch(rb'[0-9a-f]{96}', line):
            types.append(1)
            hexes.extend(bytes.fromhex(line.decode('ascii')))
        elif re.fullmatch(rb'[0-9a-z]{64}', line):
            types.append(2)
            words.append(int(line, 36))
        else:
            raise ValueError('unrecognized record')
    prefix = prefix or b''
    if mode == 0:
        tags = zlib.compress(types, 9)
    elif mode == 1:
        tags = bz2.compress(types, 9)
    else:
        tags = to_radix(types, 3)
    return (struct.pack('>BHIH', mode, len(prefix), len(types), len(tags))
            + prefix + tags + hexes + to_radix(words, 36**64)
            + to_radix(numbers, 10**21))


def unpack(data):
    mode, plen, count, tlen = struct.unpack('>BHIH', data[:9])
    pos = 9
    prefix = data[pos:pos + plen]
    pos += plen
    tags = data[pos:pos + tlen]
    pos += tlen
    if mode == 0:
        types = zlib.decompress(tags)
    elif mode == 1:
        types = bz2.decompress(tags)
    else:
        types = from_radix(tags, count, 3)
    if len(types) != count:
        raise ValueError('bad record count')
    hexlen = types.count(1) * 48
    hextext = data[pos:pos + hexlen].hex().encode('ascii')
    hexes = iter(hextext[i:i+96] for i in range(0, hexlen * 2, 96))
    pos += hexlen
    wordcount = types.count(2)
    wordlen = (((36**64)**wordcount - 1).bit_length() + 7) // 8
    words = iter(from_radix(data[pos:pos+wordlen], wordcount, 36**64))
    pos += wordlen
    numbers = iter(from_radix(data[pos:], types.count(0), 10**21))
    lines = []
    for tag in types:
        if tag == 0:
            value, c = divmod(next(numbers), 10**9)
            a, b = divmod(value, 10**6)
            lines.append(prefix + (' line %d ratio 0.%06d select pick win seed %d' % (a, b, c)).encode('ascii'))
        elif tag == 1:
            lines.append(next(hexes))
        elif tag == 2:
            lines.append(base36(next(words)))
        else:
            raise ValueError('bad record type')
    return b'\n'.join(lines) + b'\n'



def compress(data):
    fallback = b'B' + bz2.compress(data, 9)
    try:
        packed = b'P' + pack(data, 0)
        return min((fallback, packed), key=len)
    except (ValueError, OverflowError):
        return fallback


def decompress(data):
    if data[:1] == b'P':
        return unpack(data[1:])
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    raise ValueError('Unknown compression format')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes((decompress if decode else compress)(data))


if __name__ == '__main__':
    main()
