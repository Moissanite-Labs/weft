#!/usr/bin/env python3
"""Compact text/hex/base-36 corpus compressor."""
import sys
import zlib

MAGIC = b'CP1'
DIGITS = b'0123456789abcdefghijklmnopqrstuvwxyz'
HEX = set(b'0123456789abcdef')
BASE36 = set(DIGITS)


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
        if b < 128:
            return n, pos
        shift += 7


def encode(raw):
    out = bytearray()
    for line in raw.splitlines(keepends=True):
        has_nl = line.endswith(b'\n')
        body = line[:-1] if has_nl else line
        # Keep CR as data for CRLF input.
        if body and all(c in HEX for c in body):
            kind = 1
            n = len(body)
            payload = bytes.fromhex(body.decode('ascii')) if n % 2 == 0 else None
            if payload is None:
                # Odd-length hex: pack nibbles with an explicit initial length.
                payload = bytes.fromhex('0' + body.decode('ascii'))
        elif body and all(c in BASE36 for c in body):
            kind = 2
            n = len(body)
            value = 0
            for c in body:
                value = value * 36 + DIGITS.index(c)
            payload = value.to_bytes((value.bit_length() + 7) // 8, 'big')
        else:
            kind = 0
            n = len(body)
            payload = body
        out.append(kind | (4 if has_nl else 0))
        putvar(out, n)
        putvar(out, len(payload))
        out.extend(payload)
    return MAGIC + zlib.compress(bytes(out), 9)


def decode(blob):
    if not blob.startswith(MAGIC):
        raise ValueError('not a compress.py archive')
    data = zlib.decompress(blob[len(MAGIC):])
    out = bytearray()
    pos = 0
    while pos < len(data):
        tag = data[pos]
        pos += 1
        n, pos = getvar(data, pos)
        size, pos = getvar(data, pos)
        payload = data[pos:pos + size]
        if len(payload) != size:
            raise ValueError('truncated archive')
        pos += size
        kind = tag & 3
        if kind == 0:
            body = payload
        elif kind == 1:
            v = ''.join(format((b >> 4) & 15, 'x') + format(b & 15, 'x') for b in payload)
            body = (v[-n:] if n % 2 else v).encode('ascii')
        elif kind == 2:
            value = int.from_bytes(payload, 'big')
            chars = bytearray(n)
            for i in range(n - 1, -1, -1):
                value, d = divmod(value, 36)
                chars[i] = DIGITS[d]
            if value:
                raise ValueError('invalid base36 record')
            body = bytes(chars)
        else:
            raise ValueError('invalid record')
        if len(body) != n:
            raise ValueError('invalid record length')
        out.extend(body)
        if tag & 4:
            out.append(10)
    return bytes(out)


def main(argv):
    if len(argv) == 4 and argv[1] == '--decompress':
        data = decode(open(argv[2], 'rb').read())
        with open(argv[3], 'wb') as f:
            f.write(data)
    elif len(argv) == 3:
        with open(argv[1], 'rb') as f:
            data = encode(f.read())
        with open(argv[2], 'wb') as f:
            f.write(data)
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')

if __name__ == '__main__':
    main(sys.argv)
