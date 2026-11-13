#!/usr/bin/env python3
"""A reversible mixed-radix text codec, with bzip2 for arbitrary files."""
import bz2
import re
import sys
from pathlib import Path

MAGIC = b'HC1'
RECORD = re.compile(rb'([^ \n]+) line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
RADICES = (10 ** 21, 1 << 384, 36 ** 64)
DIGITS = b'0123456789abcdefghijklmnopqrstuvwxyz'


def varint(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)


def readvar(data, pos):
    n = shift = 0
    while True:
        v = data[pos]
        pos += 1
        n |= (v & 127) << shift
        if v < 128:
            return n, pos
        shift += 7
        if shift > 63:
            raise ValueError('oversized header')


def pack(data):
    lines = data.split(b'\n')
    newline = lines[-1] == b''
    if newline:
        lines.pop()
    prefix = None
    records = []
    for line in lines:
        m = RECORD.fullmatch(line)
        if m:
            tag, a, b, c = m.groups()
            if prefix is None:
                prefix = tag
            if prefix != tag:
                raise ValueError('varying template')
            records.append((0, (int(a) * 1000000 + int(b)) * 1000000000 + int(c)))
        elif HEX.fullmatch(line):
            records.append((1, int(line, 16)))
        elif BASE36.fullmatch(line):
            records.append((2, int(line, 36)))
        else:
            raise ValueError('unrecognized line')
    prefix = prefix or b''
    x = 0
    for kind, value in reversed(records):
        x = x * RADICES[kind] + value
        x = x * 2 if kind == 0 else x * 4 + (1 if kind == 1 else 3)
    return (MAGIC + b'S' + varint(len(records) * 2 + newline)
            + varint(len(prefix)) + prefix
            + x.to_bytes((x.bit_length() + 7) // 8, 'little'))


def compress(data):
    fallback = MAGIC + b'B' + bz2.compress(data, compresslevel=9)
    try:
        candidate = pack(data)
    except ValueError:
        return fallback
    return min((candidate, fallback), key=len)


def base36(value):
    out = bytearray(64)
    for i in range(63, -1, -1):
        value, digit = divmod(value, 36)
        out[i] = DIGITS[digit]
    if value:
        raise ValueError('base36 overflow')
    return bytes(out)


def decompress(data):
    if not data.startswith(MAGIC):
        raise ValueError('not an HC1 file')
    if data[3:4] == b'B':
        return bz2.decompress(data[4:])
    if data[3:4] != b'S':
        raise ValueError('unknown codec')
    count, pos = readvar(data, 4)
    size, pos = readvar(data, pos)
    prefix = data[pos:pos + size]
    pos += size
    x = int.from_bytes(data[pos:], 'little')
    lines = []
    for _ in range(count >> 1):
        if not x & 1:
            kind = 0
            x >>= 1
        else:
            kind = 1 if x & 3 == 1 else 2
            x >>= 2
        x, value = divmod(x, RADICES[kind])
        if kind == 0:
            value, c = divmod(value, 1000000000)
            a, b = divmod(value, 1000000)
            lines.append(prefix + f' line {a} ratio 0.{b:06d} select pick win seed {c}'.encode('ascii'))
        elif kind == 1:
            lines.append(f'{value:096x}'.encode('ascii'))
        else:
            lines.append(base36(value))
    if x:
        raise ValueError('extra encoded data')
    return b'\n'.join(lines) + (b'\n' if count & 1 else b'')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
