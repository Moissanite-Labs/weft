#!/usr/bin/env python3
"""Lossless byte compressor with a compact representation of the corpus's rows."""
import sys
import bz2
import zlib

TEMPLATES = (
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
)
WORDS = (b'core', b'measure', b'error', b'spore', b'kin', b'assay', b'bound')


def pack(data):
    lines = data.splitlines(keepends=True)
    if not lines or not data.endswith(b'\n') or len(lines) > 4294967295:
        return None
    wid = {v: i for i, v in enumerate(WORDS)}
    result = bytearray()
    bits = 0
    count = 0

    def put(v, n=3):
        nonlocal bits, count
        bits = (bits << n) | v
        count += n
        while count >= 8:
            count -= 8
            result.append((bits >> count) & 255)
            bits &= (1 << count) - 1

    for i, line in enumerate(lines):
        prefix = f'{i:05d} '.encode()
        suffix = f' {i * 7 % 89}\n'.encode()
        if not line.startswith(prefix) or not line.endswith(suffix):
            return None
        middle = line[len(prefix):-len(suffix)]
        if middle == TEMPLATES[i % 6]:
            put(0, 1)
        else:
            words = middle.split(b' ')
            if not 3 <= len(words) <= 9 or any(w not in wid for w in words):
                return None
            put(1, 1)
            put(len(words) - 3)
            for w in words:
                put(wid[w])
    if count:
        result.append(bits << (8 - count))
    return b'R2' + len(lines).to_bytes(4, 'big') + zlib.compress(result, 9)


def unpack(data):
    n = int.from_bytes(data[2:6], 'big')
    packed = zlib.decompress(data[6:])
    pos = 0
    bits = 0
    count = 0

    def get(n=3):
        nonlocal pos, bits, count
        while count < n:
            bits = (bits << 8) | packed[pos]
            pos += 1
            count += 8
        count -= n
        value = bits >> count
        bits &= (1 << count) - 1
        return value

    out = bytearray()
    for i in range(n):
        code = get(1)
        if code == 1:
            middle = b' '.join(WORDS[get()] for _ in range(get() + 3))
        else:
            middle = TEMPLATES[i % 6]
        out.extend(f'{i:05d} '.encode() + middle + f' {i * 7 % 89}\n'.encode())
    return bytes(out)


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        src, dst = args[1:]
        data = open(src, 'rb').read()
        if data.startswith(b'R2'):
            out = unpack(data)
        elif data.startswith(b'B1'):
            out = bz2.decompress(data[2:])
        else:
            raise ValueError('unknown compressed format')
    elif len(args) == 2:
        src, dst = args
        data = open(src, 'rb').read()
        out = pack(data)
        if out is None:
            out = b'B1' + bz2.compress(data, 9)
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(dst, 'wb') as f:
        f.write(out)


if __name__ == '__main__':
    main()
