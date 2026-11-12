#!/usr/bin/env python3
"""Lossless, stdlib-only compressor with a compact encoding for the corpus format."""
import bz2
import lzma
import re
import sys
import bitpacking
import zlib

HEADER = re.compile(rb'e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)\Z')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def encode(data):
    lines = data.splitlines(keepends=True)
    values = []
    try:
        if not lines or len(lines) > 65535 or any(not line.endswith(b'\n') for line in lines):
            raise ValueError('nonstandard line ending')
        for line in lines:
            line = line[:-1]
            match = HEADER.fullmatch(line)
            if match:
                first, fraction, seed = map(int, match.groups())
                if first >= 1 << 20 or seed >= 1 << 30 or fraction >= 1000000:
                    raise ValueError('oversized header')
                values.append((0, ((first << 20) | fraction) << 30 | seed))
            elif len(line) == 96 and all(ch in b'0123456789abcdef' for ch in line):
                values.append((1, int(line, 16)))
            elif len(line) == 64 and all(ch in ALPHABET for ch in line):
                values.append((2, int(line, 36)))
            else:
                raise ValueError('unrecognized line')
        raw = b'S' + len(values).to_bytes(2, 'big') + bitpacking.pack(values)
    except (ValueError, OverflowError):
        raw = b'R' + data
    choices = [(b'n', raw), (b'z', zlib.compress(raw, 9)),
               (b'b', bz2.compress(raw, 9)), (b'l', lzma.compress(raw, preset=9))]
    kind, output = min(choices, key=lambda choice: len(choice[1]))
    return b'CP1' + kind + output


def decode(data):
    if data[:3] != b'CP1':
        raise ValueError('not a compressed file')
    mode = data[3:4]
    if mode == b'n':
        raw = data[4:]
    elif mode == b'z':
        raw = zlib.decompress(data[4:])
    elif mode == b'b':
        raw = bz2.decompress(data[4:])
    elif mode == b'l':
        raw = lzma.decompress(data[4:])
    else:
        raise ValueError('unknown compression method')
    if raw[:1] == b'R':
        return raw[1:]
    if raw[:1] != b'S':
        raise ValueError('unknown encoding')
    count = int.from_bytes(raw[1:3], 'big')
    result = bytearray()
    for tag, value in bitpacking.unpack(raw[3:], count):
        if tag == 0:
            seed = value & ((1 << 30) - 1)
            fraction = (value >> 30) & ((1 << 20) - 1)
            first = value >> 50
            result += f'e18a line {first} ratio 0.{fraction:06d} select pick win seed {seed}\n'.encode()
        elif tag == 1:
            result += f'{value:096x}\n'.encode()
        else:
            digits = bytearray(64)
            for i in range(63, -1, -1):
                value, d = divmod(value, 36)
                digits[i] = ALPHABET[d]
            if value:
                raise ValueError('base36 overflow')
            result += digits + b'\n'
    return bytes(result)


def main():
    if len(sys.argv) == 3:
        source, dest = sys.argv[1:]
        transform = encode
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        source, dest = sys.argv[2:]
        transform = decode
    else:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(source, 'rb') as f:
        data = f.read()
    result = transform(data)
    with open(dest, 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
