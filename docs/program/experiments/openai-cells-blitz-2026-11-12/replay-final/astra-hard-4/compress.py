#!/usr/bin/env python3
"""Lossless mixed-radix text packing, with a bzip2 fallback."""
import bz2
import re
import struct
import sys
from pathlib import Path

NUMBER = re.compile(rb'([^\s]+) line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
RADIX = (10**21, 2**384, 36**64)


def pack(data):
    if not data.endswith(b'\n'):
        raise ValueError('not newline terminated')
    lines = data[:-1].split(b'\n')
    prefix = None
    types = 0
    value = 1
    for line in lines:
        match = NUMBER.fullmatch(line)
        if match:
            p, a, b, c = match.groups()
            if prefix is None:
                prefix = p
            if p != prefix:
                raise ValueError('multiple templates')
            kind = 0
            v = int(a)*10**15 + int(b)*10**9 + int(c)
        elif re.fullmatch(rb'[0-9a-f]{96}', line):
            kind, v = 1, int(line, 16)
        elif re.fullmatch(rb'[0-9a-z]{64}', line):
            kind, v = 2, int(line, 36)
        else:
            raise ValueError('unrecognized line')
        types = types*3 + kind
        value = value*RADIX[kind] + v
    prefix = prefix or b''
    n = len(lines)
    width = ((3**n - 1).bit_length()+7)//8
    return struct.pack('>IH', n, len(prefix)) + prefix + types.to_bytes(width, 'big') + value.to_bytes((value.bit_length()+7)//8, 'big')


def unpack(data):
    n, plen = struct.unpack('>IH', data[:6])
    prefix = data[6:6+plen]
    pos = 6+plen
    width = ((3**n - 1).bit_length()+7)//8
    types = int.from_bytes(data[pos:pos+width], 'big')
    value = int.from_bytes(data[pos+width:], 'big')
    lines = []
    for _ in range(n):
        types, kind = divmod(types, 3)
        value, v = divmod(value, RADIX[kind])
        if kind == 0:
            a, v = divmod(v, 10**15)
            b, c = divmod(v, 10**9)
            line = prefix + (' line %d ratio 0.%06d select pick win seed %d' % (a,b,c)).encode('ascii')
        elif kind == 1:
            line = ('%096x' % v).encode('ascii')
        else:
            chars = bytearray(64)
            for i in range(63,-1,-1):
                v, digit = divmod(v,36)
                chars[i] = b'0123456789abcdefghijklmnopqrstuvwxyz'[digit]
            line = bytes(chars)
        lines.append(line)
    if value != 1 or types:
        raise ValueError('corrupt packed stream')
    return b'\n'.join(reversed(lines)) + b'\n'


def compress(data):
    fallback = b'B' + bz2.compress(data)
    try:
        packed = b'P' + pack(data)
        return min((fallback, packed), key=len)
    except (ValueError, OverflowError):
        return fallback


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] == b'P':
        return unpack(data[1:])
    raise ValueError('unknown compression format')


def main():
    args = sys.argv[1:]
    decode = args[:1] == ['--decompress']
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    source, target = map(Path, args)
    target.write_bytes((decompress if decode else compress)(source.read_bytes()))


if __name__ == '__main__':
    main()
