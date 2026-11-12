#!/usr/bin/env python3
"""Lossless compressor for a corpus of tagged hexadecimal, base36 and record lines."""
import bz2
import re
import sys

META = re.compile(rb'e18a line ([0-9]+) ratio (0\.[0-9]{6}) select pick win seed ([0-9]+)')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE = re.compile(rb'[0-9a-z]{64}')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def pack(data):
    lines = data.splitlines()
    tags = bytearray((len(lines) + 3) // 4)
    body = bytearray()
    for i, line in enumerate(lines):
        m = META.fullmatch(line)
        if m:
            tag = 0
            a, r, s = m.groups()
            body.extend(int(a).to_bytes(3, 'big'))
            body.extend(int(r[2:]).to_bytes(3, 'big'))
            body.extend(int(s).to_bytes(4, 'big'))
        elif HEX.fullmatch(line):
            tag = 1
            body.extend(bytes.fromhex(line.decode('ascii')))
        elif BASE.fullmatch(line):
            tag = 2
            body.extend(int(line, 36).to_bytes(42, 'big'))
        else:
            tag = 3
            body.extend(len(line).to_bytes(4, 'big'))
            body.extend(line)
        tags[i // 4] |= tag << (2 * (i % 4))
    payload = len(lines).to_bytes(4, 'big') + bytes([data.endswith(b'\n')]) + tags + body
    return b'HC01' + bz2.compress(payload, compresslevel=9)


def unpack(data):
    if not data.startswith(b'HC01'):
        raise ValueError('Invalid compressed file')
    src = bz2.decompress(data[4:])
    count = int.from_bytes(src[:4], 'big')
    newline = src[4]
    tags = src[5:5 + (count + 3) // 4]
    body = memoryview(src)[5 + (count + 3) // 4:]
    pos = 0
    lines = []
    for i in range(count):
        tag = (tags[i // 4] >> (2 * (i % 4))) & 3
        if tag == 0:
            a = int.from_bytes(body[pos:pos+3], 'big')
            r = int.from_bytes(body[pos+3:pos+6], 'big')
            s = int.from_bytes(body[pos+6:pos+10], 'big')
            pos += 10
            line = f'e18a line {a} ratio 0.{r:06d} select pick win seed {s}'.encode()
        elif tag == 1:
            line = bytes(body[pos:pos+48]).hex().encode()
            pos += 48
        elif tag == 2:
            n = int.from_bytes(body[pos:pos+42], 'big')
            pos += 42
            digits = bytearray(64)
            for j in range(63, -1, -1):
                n, rem = divmod(n, 36)
                digits[j] = ALPHABET[rem]
            line = bytes(digits)
        else:
            length = int.from_bytes(body[pos:pos+4], 'big')
            pos += 4
            line = bytes(body[pos:pos+length])
            pos += length
        lines.append(line)
    if pos != len(body):
        raise ValueError('Trailing data')
    return b'\n'.join(lines) + (b'\n' if newline else b'')


def main():
    if len(sys.argv) == 3:
        mode, source, dest = 'pack', sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        mode, source, dest = 'unpack', sys.argv[2], sys.argv[3]
    else:
        raise SystemExit('Usage: compress.py [--decompress] source destination')
    with open(source, 'rb') as f:
        data = f.read()
    result = pack(data) if mode == 'pack' else unpack(data)
    with open(dest, 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
