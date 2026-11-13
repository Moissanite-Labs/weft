#!/usr/bin/env python3
"""Lossless structured text packing with a general bzip2 fallback."""
import bz2
import re
import sys
from pathlib import Path

RECORD = re.compile(rb'e18a line (0|[1-9][0-9]*) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]*)\n')
HEX = re.compile(rb'[0-9a-f]{96}\n')
BASE = re.compile(rb'[0-9a-z]{64}\n')
B36 = 36 ** 64
NUM = 10 ** 21


def width(radix, n):
    return ((radix ** n - 1).bit_length() + 7) // 8


def compress(data):
    fallback = b'B' + bz2.compress(data)
    lines = data.splitlines(keepends=True)
    types = 0
    h = bytearray()
    b = r = 0
    nb = nr = 0
    for line in lines:
        m = RECORD.fullmatch(line)
        if HEX.fullmatch(line):
            t = 0
            h.extend(bytes.fromhex(line.decode()))
        elif BASE.fullmatch(line):
            t = 1
            b = b * B36 + int(line, 36)
            nb += 1
        elif m and int(m[1]) < 10**6 and int(m[3]) < 10**9:
            t = 2
            r = r * NUM + (int(m[1]) * 10**6 + int(m[2])) * 10**9 + int(m[3])
            nr += 1
        else:
            return fallback
        types = types * 3 + t
    packed = (b'S' + len(lines).to_bytes(4, 'big') + types.to_bytes(width(3, len(lines)), 'big')
              + h + b.to_bytes(width(B36, nb), 'big') + r.to_bytes(width(NUM, nr), 'big'))
    return min((fallback, packed), key=len)


def base36(v):
    out = bytearray(64)
    alphabet = b'0123456789abcdefghijklmnopqrstuvwxyz'
    for i in range(63, -1, -1):
        v, rem = divmod(v, 36)
        out[i] = alphabet[rem]
    return bytes(out) + b'\n'


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] != b'S':
        raise ValueError('unknown format')
    n = int.from_bytes(data[1:5], 'big')
    end = 5 + width(3, n)
    t = int.from_bytes(data[5:end], 'big')
    types = []
    for _ in range(n):
        t, rem = divmod(t, 3)
        types.append(rem)
    types.reverse()
    nh, nb, nr = (types.count(i) for i in range(3))
    hexdata = data[end:end + nh*48]
    end += nh * 48
    bw = width(B36, nb)
    b = int.from_bytes(data[end:end+bw], 'big')
    r = int.from_bytes(data[end+bw:], 'big')
    bases = []
    for _ in range(nb):
        b, rem = divmod(b, B36)
        bases.append(base36(rem))
    records = []
    for _ in range(nr):
        r, rem = divmod(r, NUM)
        rem, seed = divmod(rem, 10**9)
        line, ratio = divmod(rem, 10**6)
        records.append(('e18a line %d ratio 0.%06d select pick win seed %d\n' % (line, ratio, seed)).encode())
    out = []
    hi = 0
    for t in types:
        if t == 0:
            out.append(hexdata[hi:hi+48].hex().encode() + b'\n')
            hi += 48
        elif t == 1:
            out.append(bases.pop())
        else:
            out.append(records.pop())
    return b''.join(out)


def main():
    args = sys.argv[1:]
    decode = args[:1] == ['--decompress']
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(args[1]).write_bytes((decompress if decode else compress)(Path(args[0]).read_bytes()))


if __name__ == '__main__':
    main()
