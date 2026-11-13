#!/usr/bin/env python3
"""Compact the structured text corpus, with exact byte-for-byte restoration."""
import re
import struct
import sys
import zlib

MAGIC = b'CPZ1'
HEADER = re.compile(rb'e18a line (\d+) ratio (\d+)\.(\d{6}) select pick win seed (\d+)\Z')
HEX = re.compile(rb'[0-9a-f]{96}\Z')
BASE36 = re.compile(rb'[0-9a-z]{64}\Z')
ALPH = b'0123456789abcdefghijklmnopqrstuvwxyz'


def putvar(out, n):
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)


def getvar(data, pos):
    n = shift = 0
    while True:
        b = data[pos]
        pos += 1
        n |= (b & 127) << shift
        if not b & 128:
            return n, pos
        shift += 7


def encode(raw):
    packed = bytearray()
    for full in raw.splitlines(keepends=True):
        if full.endswith(b'\r\n'):
            line, nl = full[:-2], 2
        elif full.endswith(b'\n'):
            line, nl = full[:-1], 1
        else:
            line, nl = full, 0
        m = HEADER.fullmatch(line)
        if m:
            a, whole, frac, seed = (int(x) for x in m.groups())
            packed.append(0)
            for n in (a, whole * 1000000 + frac, seed):
                putvar(packed, n)
        elif HEX.fullmatch(line):
            packed.append(1)
            packed.extend(bytes.fromhex(line.decode('ascii')))
        elif BASE36.fullmatch(line):
            packed.append(2)
            n = 0
            for c in line:
                n = n * 36 + ALPH.index(c)
            packed.extend(n.to_bytes(42, 'big'))
        else:
            packed.append(3)
            putvar(packed, len(line))
            packed.extend(line)
        packed.append(nl)
    return MAGIC + zlib.compress(bytes(packed), 9)


def decode(blob):
    if not blob.startswith(MAGIC):
        raise ValueError('not a compress.py archive')
    data = zlib.decompress(blob[len(MAGIC):])
    out = bytearray()
    p = 0
    while p < len(data):
        typ = data[p]
        p += 1
        if typ == 0:
            a, p = getvar(data, p)
            ratio, p = getvar(data, p)
            seed, p = getvar(data, p)
            line = (f'e18a line {a} ratio {ratio // 1000000}.{ratio % 1000000:06d} '
                    f'select pick win seed {seed}').encode()
        elif typ == 1:
            line = data[p:p+48].hex().encode()
            p += 48
        elif typ == 2:
            n = int.from_bytes(data[p:p+42], 'big')
            p += 42
            chars = bytearray()
            while n:
                n, r = divmod(n, 36)
                chars.append(ALPH[r])
            line = bytes(reversed(chars)).rjust(64, b'0')
        elif typ == 3:
            size, p = getvar(data, p)
            line = data[p:p+size]
            p += size
        else:
            raise ValueError('invalid record type')
        nl = data[p]
        p += 1
        out.extend(line)
        out.extend(b'\n' if nl == 1 else b'\r\n' if nl == 2 else b'')
    return bytes(out)


def main(argv):
    if len(argv) == 4 and argv[1] == '--decompress':
        with open(argv[2], 'rb') as f:
            raw = decode(f.read())
        with open(argv[3], 'wb') as f:
            f.write(raw)
    elif len(argv) == 3:
        with open(argv[1], 'rb') as f:
            blob = encode(f.read())
        with open(argv[2], 'wb') as f:
            f.write(blob)
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')


if __name__ == '__main__':
    main(sys.argv)
