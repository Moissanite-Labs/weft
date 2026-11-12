#!/usr/bin/env python3
"""Lossless mixed-radix text codec; all unsupported input uses bzip2."""
import bz2
import re
import sys
import zlib
from pathlib import Path

PAT = re.compile(rb'e18a line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})\n')
RADIX = (10**21, 16**96, 36**64)

def compress(data):
    types = bytearray()
    value = 0
    bound = 1
    for line in data.splitlines(keepends=True):
        match = PAT.fullmatch(line)
        if match:
            a, b, c = map(int, match.groups())
            t, v = 0, (a * 1000000 + b) * 1000000000 + c
        elif re.fullmatch(rb'[0-9a-f]{96}\n', line):
            t, v = 1, int(line, 16)
        elif re.fullmatch(rb'[0-9a-z]{64}\n', line):
            t, v = 2, int(line, 36)
        else:
            return b'B' + bz2.compress(data)
        types.append(t)
        value = value * RADIX[t] + v
        bound *= RADIX[t]
    table = zlib.compress(types, 9)
    encoded = b'M' + len(table).to_bytes(4, 'big') + table + value.to_bytes(((bound-1).bit_length()+7)//8, 'big')
    return min(encoded, b'B' + bz2.compress(data), key=len)

def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] != b'M':
        raise ValueError('unknown format')
    n = int.from_bytes(data[1:5], 'big')
    types = zlib.decompress(data[5:5+n])
    value = int.from_bytes(data[5+n:], 'big')
    out = []
    for t in reversed(types):
        value, v = divmod(value, RADIX[t])
        if t == 0:
            v, c = divmod(v, 1000000000)
            a, b = divmod(v, 1000000)
            out.append(f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}\n'.encode())
        elif t == 1:
            out.append(f'{v:096x}\n'.encode())
        else:
            chars = bytearray(64)
            for i in range(63, -1, -1):
                v, r = divmod(v, 36)
                chars[i] = b'0123456789abcdefghijklmnopqrstuvwxyz'[r]
            out.append(bytes(chars) + b'\n')
    if value:
        raise ValueError('invalid payload')
    return b''.join(reversed(out))

def main():
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    Path(args[1]).write_bytes((decompress if decode else compress)(Path(args[0]).read_bytes()))

if __name__ == '__main__':
    main()
