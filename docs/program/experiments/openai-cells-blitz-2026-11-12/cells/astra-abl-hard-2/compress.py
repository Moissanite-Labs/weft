#!/usr/bin/env python3
"""Lossless structural compression with a bzip2 fallback; standard library only.

CH2 models hexadecimal, base-36 and numeric log records. Record order is
encoded as a multinomial rank; values use exact mixed-radix packing. All
parameters needed for decoding are in the file, never in the source corpus.
CH1 handles arbitrary bytes with bzip2.
"""
import bz2
import math
import re
import sys

LOG = re.compile(rb'([^\n]+?) line (0|[1-9][0-9]*) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]*)')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def varint(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)


def readint(data, pos):
    n = shift = 0
    while True:
        b = data[pos]
        pos += 1
        n |= (b & 127) << shift
        if b < 128:
            return n, pos
        shift += 7


def ways(counts):
    a, b, c = counts
    return math.comb(a+b+c, a) * math.comb(b+c, b)


def rank_order(order, counts):
    counts = counts[:]
    total = sum(counts)
    w = ways(counts)
    rank = 0
    for t in order:
        rank += w * sum(counts[:t]) // total
        w = w * counts[t] // total
        counts[t] -= 1
        total -= 1
    return rank


def unrank_order(rank, counts):
    counts = counts[:]
    total = sum(counts)
    w = ways(counts)
    order = []
    while total:
        for t in range(3):
            block = w * counts[t] // total
            if rank < block:
                order.append(t)
                w = block
                counts[t] -= 1
                break
            rank -= block
        else:
            raise ValueError('invalid record order')
        total -= 1
    return order


def structured(data):
    if not data.endswith(b'\n'):
        return None
    records = []
    prefix = None
    ndigits = sdigits = 1
    for line in data[:-1].split(b'\n'):
        if HEX.fullmatch(line):
            records.append((0, int(line, 16)))
        elif BASE36.fullmatch(line):
            records.append((1, int(line, 36)))
        else:
            m = LOG.fullmatch(line)
            if m is None:
                return None
            p, n, r, s = m.groups()
            if prefix is None:
                prefix = p
            if p != prefix or len(n) > 18 or len(s) > 18:
                return None
            ndigits = max(ndigits, len(n))
            sdigits = max(sdigits, len(s))
            records.append((2, (int(n), int(r), int(s))))
    prefix = prefix or b''
    order = [t for t, v in records]
    counts = [order.count(t) for t in range(3)]
    sr = 10**sdigits
    radices = [1 << 384, 36**64, 10**ndigits * 1000000 * sr]
    value = 0
    product = 1
    for t, v in records:
        if t == 2:
            n, r, s = v
            v = (n * 1000000 + r) * sr + s
        value = value * radices[t] + v
        product *= radices[t]
    # Combine record ordering and values into one compact integer.
    value += rank_order(order, counts) * product
    size = ((ways(counts) * product - 1).bit_length() + 7) // 8
    header = (b'CH2' + b''.join(varint(c) for c in counts)
              + varint(len(prefix)) + prefix + bytes([ndigits, sdigits]))
    return header + value.to_bytes(size, 'big')


def compress(data):
    fallback = b'CH1' + bz2.compress(data, compresslevel=9)
    packed = structured(data)
    return packed if packed is not None and len(packed) < len(fallback) else fallback


def base36(value):
    result = bytearray(64)
    for i in range(63, -1, -1):
        value, digit = divmod(value, 36)
        result[i] = ALPHABET[digit]
    return bytes(result)


def decompress(data):
    if data[:3] == b'CH1':
        return bz2.decompress(data[3:])
    if data[:3] != b'CH2':
        raise ValueError('invalid compressed file')
    pos = 3
    counts = []
    for _ in range(3):
        c, pos = readint(data, pos)
        counts.append(c)
    length, pos = readint(data, pos)
    prefix = data[pos:pos+length]
    pos += length
    ndigits, sdigits = data[pos:pos+2]
    pos += 2
    sr = 10**sdigits
    radices = [1 << 384, 36**64, 10**ndigits * 1000000 * sr]
    product = math.prod(r**c for r, c in zip(radices, counts))
    rank, value = divmod(int.from_bytes(data[pos:], 'big'), product)
    order = unrank_order(rank, counts)
    lines = []
    for t in reversed(order):
        value, v = divmod(value, radices[t])
        if t == 0:
            line = format(v, '096x').encode('ascii')
        elif t == 1:
            line = base36(v)
        else:
            v, s = divmod(v, sr)
            n, r = divmod(v, 1000000)
            line = prefix + (' line %d ratio 0.%06d select pick win seed %d' % (n, r, s)).encode('ascii')
        lines.append(line)
    return b'\n'.join(reversed(lines)) + b'\n'


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as f:
        source = f.read()
    result = decompress(source) if decode else compress(source)
    with open(args[1], 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
