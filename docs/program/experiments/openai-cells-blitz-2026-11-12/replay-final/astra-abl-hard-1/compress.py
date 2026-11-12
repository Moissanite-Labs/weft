"""Lossless structured-text compressor, using only the Python standard library.

Structured blocks separate hex strings, base36 strings, and numeric records.
Mixed-radix packing avoids wasting bits on textual representations. Other
inputs use bzip2. No original input is needed to decompress either format.
"""
import bz2
import math
import re
import sys
from pathlib import Path

RECORD = re.compile(rb'([^\r\n]+) line (0|[1-9][0-9]*) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]*)')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'
RADIX = 10**21
B36 = 36**64


def varint(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)


def width(radix, n):
    return ((radix**n - 1).bit_length() + 7) // 8


def multinomial(counts):
    a, b, c = counts
    return math.comb(a + b + c, a) * math.comb(b + c, b)


def rank_types(types, counts):
    counts = counts[:]
    ways = multinomial(counts)
    rank = 0
    left = sum(counts)
    for t in types:
        rank += ways * sum(counts[:t]) // left
        ways = ways * counts[t] // left
        counts[t] -= 1
        left -= 1
    return rank


def unrank_types(rank, counts):
    counts = counts[:]
    ways = multinomial(counts)
    left = sum(counts)
    result = []
    while left:
        for t in range(3):
            block = ways * counts[t] // left
            if rank < block:
                result.append(t)
                ways = block
                counts[t] -= 1
                break
            rank -= block
        else:
            raise ValueError('invalid sequence rank')
        left -= 1
    return result


def structured(data):
    final = data.endswith(b'\n')
    lines = data.split(b'\n')
    if final:
        lines.pop()
    prefix = None
    types = []
    counts = [0, 0, 0]
    numeric = 0
    base36 = 0
    hexdata = bytearray()
    for line in lines:
        m = RECORD.fullmatch(line)
        if m:
            p, a, b, c = m.groups()
            if prefix is None:
                prefix = p
            if p != prefix:
                return None
            a, b, c = int(a), int(b), int(c)
            if a >= 10**6 or c >= 10**9:
                return None
            numeric = numeric * RADIX + (a * 10**6 + b) * 10**9 + c
            t = 0
        elif HEX.fullmatch(line):
            hexdata.extend(bytes.fromhex(line.decode('ascii')))
            t = 1
        elif BASE36.fullmatch(line):
            base36 = base36 * B36 + int(line, 36)
            t = 2
        else:
            return None
        types.append(t)
        counts[t] += 1
    prefix = prefix or b''
    header = b'ST1' + bytes([final]) + b''.join(varint(n) for n in counts) + varint(len(prefix)) + prefix
    typewidth = ((multinomial(counts) - 1).bit_length() + 7) // 8
    return (header + rank_types(types, counts).to_bytes(typewidth, 'big')
            + numeric.to_bytes(width(RADIX, counts[0]), 'big')
            + hexdata + base36.to_bytes(width(B36, counts[2]), 'big'))


def compress(data):
    fallback = b'BZ1' + bz2.compress(data, compresslevel=9)
    packed = structured(data)
    return packed if packed is not None and len(packed) < len(fallback) else fallback


def decompress(data):
    if data[:3] == b'BZ1':
        return bz2.decompress(data[3:])
    if data[:3] != b'ST1':
        raise ValueError('unknown format')
    pos = 3
    def take(n):
        nonlocal pos
        if n < 0 or pos + n > len(data):
            raise ValueError('truncated input')
        result = data[pos:pos+n]
        pos += n
        return result
    def getvar():
        n = shift = 0
        while True:
            b = take(1)[0]
            n |= (b & 127) << shift
            if b < 128:
                return n
            shift += 7
    final = take(1)[0]
    counts = [getvar() for _ in range(3)]
    prefix = take(getvar())
    tw = ((multinomial(counts)-1).bit_length()+7)//8
    types = unrank_types(int.from_bytes(take(tw), 'big'), counts)
    numeric = int.from_bytes(take(width(RADIX, counts[0])), 'big')
    numbers = []
    for _ in range(counts[0]):
        numeric, v = divmod(numeric, RADIX)
        v, c = divmod(v, 10**9)
        a, b = divmod(v, 10**6)
        numbers.append(prefix + b' line %d ratio 0.%06d select pick win seed %d' % (a, b, c))
    hexdata = take(48 * counts[1])
    hexlines = [hexdata[i:i+48].hex().encode('ascii') for i in range(0, len(hexdata), 48)]
    base36 = int.from_bytes(take(width(B36, counts[2])), 'big')
    strings = []
    for _ in range(counts[2]):
        base36, v = divmod(base36, B36)
        chars = bytearray(64)
        for i in range(63, -1, -1):
            v, digit = divmod(v, 36)
            chars[i] = ALPHABET[digit]
        strings.append(bytes(chars))
    if pos != len(data):
        raise ValueError('trailing data')
    streams = [iter(reversed(numbers)), iter(hexlines), iter(reversed(strings))]
    return b'\n'.join(next(streams[t]) for t in types) + (b'\n' if final else b'')


if __name__ == '__main__':
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(args[1]).write_bytes((decompress if decode else compress)(Path(args[0]).read_bytes()))
