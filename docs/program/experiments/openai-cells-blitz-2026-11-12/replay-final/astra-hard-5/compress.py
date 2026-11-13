#!/usr/bin/env python3
"""Lossless text codec with a generic bzip2 fallback."""
import bz2
import re
import sys
import zlib
from pathlib import Path

PAT = re.compile(rb'e18a line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})\n')

def compress(data):
    types = bytearray()
    payload = bytearray()
    for line in data.splitlines(keepends=True):
        match = PAT.fullmatch(line)
        if match:
            a, b, c = map(int, match.groups())
            types.append(0)
            payload.extend(((a * 1000000 + b) * 1000000000 + c).to_bytes(9, 'big'))
        elif re.fullmatch(rb'[0-9a-f]{96}\n', line):
            types.append(1)
            payload.extend(bytes.fromhex(line.decode()))
        elif re.fullmatch(rb'[0-9a-z]{64}\n', line):
            types.append(2)
            payload.extend(int(line, 36).to_bytes(42, 'big'))
        else:
            return b'B' + bz2.compress(data)
    table = zlib.compress(types, 9)
    encoded = b'T' + len(table).to_bytes(4, 'big') + table + payload
    return min(encoded, b'B' + bz2.compress(data), key=len)

def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] != b'T':
        raise ValueError('unknown format')
    n = int.from_bytes(data[1:5], 'big')
    types = zlib.decompress(data[5:5+n])
    pos = 5+n
    out = bytearray()
    for t in types:
        size = (9, 48, 42)[t]
        item = data[pos:pos+size]
        if len(item) != size:
            raise ValueError('truncated file')
        pos += size
        if t == 0:
            v, c = divmod(int.from_bytes(item, 'big'), 1000000000)
            a, b = divmod(v, 1000000)
            out.extend(f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}\n'.encode())
        elif t == 1:
            out.extend(item.hex().encode() + b'\n')
        else:
            v = int.from_bytes(item, 'big')
            chars = bytearray(64)
            for i in range(63, -1, -1):
                v, r = divmod(v, 36)
                chars[i] = b'0123456789abcdefghijklmnopqrstuvwxyz'[r]
            out.extend(chars + b'\n')
    if pos != len(data):
        raise ValueError('trailing data')
    return bytes(out)

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
