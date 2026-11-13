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
    payload = bytearray()
    for line in lines:
        m = RECORD.fullmatch(line)
        if HEX.fullmatch(line):
            t = 0
            payload.extend(bytes.fromhex(line.decode()))
        elif BASE.fullmatch(line):
            t = 1
            payload.extend(int(line, 36).to_bytes(42, 'big'))
        elif m and int(m[1]) < 10**6 and int(m[3]) < 10**9:
            t = 2
            r = (int(m[1]) * 10**6 + int(m[2])) * 10**9 + int(m[3])
            payload.extend(r.to_bytes(9, 'big'))
        else:
            return fallback
        types = types * 3 + t
    packed = b'S' + len(lines).to_bytes(4, 'big') + types.to_bytes(width(3, len(lines)), 'big') + payload
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
    out = []
    for t in reversed(types):
        w = (48, 42, 9)[t]
        chunk = data[end:end+w]
        end += w
        if t == 0:
            out.append(chunk.hex().encode() + b'\n')
        elif t == 1:
            out.append(base36(int.from_bytes(chunk, 'big')))
        else:
            r, seed = divmod(int.from_bytes(chunk, 'big'), 10**9)
            line, ratio = divmod(r, 10**6)
            out.append(('e18a line %d ratio 0.%06d select pick win seed %d\n' % (line, ratio, seed)).encode())
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
