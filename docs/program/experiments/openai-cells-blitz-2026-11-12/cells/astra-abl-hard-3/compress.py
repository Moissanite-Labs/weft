#!/usr/bin/env python3
"""Lossless text compression: typed mixed-radix streams, with XZ fallback.

Structured records are represented by their numeric information, not ASCII.
The file carries record order and count; decoding needs no external corpus.
"""
import lzma
import re
import sys
from pathlib import Path

MAGIC = b'MRX1'
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
RECORD = re.compile(rb'e18a line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
RADIX36 = 36 ** 64
RADIXREC = 10 ** 21

def width(radix, count):
    return ((radix ** count - 1).bit_length() + 7) // 8

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
        raise ValueError('Invalid mixed-radix stream')
    return result

def structured(data):
    if not data.endswith(b'\n'):
        return None
    kinds, hexes, words, records = [], [], [], []
    for line in data[:-1].split(b'\n'):
        if HEX.fullmatch(line):
            kinds.append(0)
            hexes.append(bytes.fromhex(line.decode('ascii')))
        elif BASE36.fullmatch(line):
            kinds.append(1)
            words.append(int(line, 36))
        else:
            m = RECORD.fullmatch(line)
            if not m:
                return None
            a, b, c = map(int, m.groups())
            kinds.append(2)
            records.append((a * 10**6 + b) * 10**9 + c)
    return (MAGIC + len(kinds).to_bytes(4, 'big') + pack(kinds, 3)
            + b''.join(hexes) + pack(words, RADIX36) + pack(records, RADIXREC))

def compress(data):
    candidate = structured(data)
    # The numeric stream is almost entirely entropy; XZ is for other inputs.
    if candidate is not None:
        return candidate
    return lzma.compress(data, preset=9)

def base36(value):
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    chars = ['0'] * 64
    for i in range(63, -1, -1):
        value, digit = divmod(value, 36)
        chars[i] = alphabet[digit]
    return ''.join(chars).encode('ascii')

def decompress(data):
    if not data.startswith(MAGIC):
        return lzma.decompress(data)
    count = int.from_bytes(data[4:8], 'big')
    offset = 8
    def take(size):
        nonlocal offset
        result = data[offset:offset+size]
        offset += size
        if len(result) != size:
            raise ValueError('Truncated file')
        return result
    kinds = unpack(take(width(3, count)), 3, count)
    hexes = iter([take(48).hex().encode('ascii') for _ in range(kinds.count(0))])
    n = kinds.count(1)
    words = iter(map(base36, unpack(take(width(RADIX36, n)), RADIX36, n)))
    n = kinds.count(2)
    records = []
    for value in unpack(take(width(RADIXREC, n)), RADIXREC, n):
        value, c = divmod(value, 10**9)
        a, b = divmod(value, 10**6)
        records.append(f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}'.encode('ascii'))
    streams = [hexes, words, iter(records)]
    if offset != len(data):
        raise ValueError('Trailing data')
    return b''.join(next(streams[k]) + b'\n' for k in kinds)

def main():
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(args[1]).write_bytes((decompress if decode else compress)(Path(args[0]).read_bytes()))

if __name__ == '__main__':
    main()
