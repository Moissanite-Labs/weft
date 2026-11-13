#!/usr/bin/env python3
"""Compact lossless encoding for the structured corpus, with a generic fallback."""
import sys
import zlib
import lzma

BASE = (
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
)
WORDS = (b'assay', b'bound', b'core', b'error', b'kin', b'measure', b'spore')
INDEX = {word: i for i, word in enumerate(WORDS)}


class Bits:
    def __init__(self, data=b''):
        self.data = bytearray(data)
        self.bit = 0

    def put(self, x, n):
        for k in range(n-1, -1, -1):
            if not self.bit % 8:
                self.data.append(0)
            self.data[-1] |= ((x >> k) & 1) << (7 - self.bit % 8)
            self.bit += 1

    def get(self, n):
        value = 0
        for _ in range(n):
            value = (value << 1) | ((self.data[self.bit // 8] >> (7 - self.bit % 8)) & 1)
            self.bit += 1
        return value


def structured(data):
    lines = data.splitlines(keepends=True)
    bits = Bits()
    for i, line in enumerate(lines):
        prefix = f'{i:05d} '.encode()
        suffix = f' {i * 7 % 89}\n'.encode()
        if not line.startswith(prefix) or not line.endswith(suffix):
            return None
        text = line[len(prefix):-len(suffix)]
        if text == BASE[i % 6]:
            bits.put(0, 1)
        else:
            words = text.split(b' ')
            if not 3 <= len(words) <= 10 or any(w not in INDEX for w in words):
                return None
            bits.put(1, 1)
            bits.put(len(words)-3, 3)
            for word in words:
                bits.put(INDEX[word], 3)
    return b'C' + len(lines).to_bytes(4, 'big') + zlib.compress(bits.data, 9)


def decompress(data):
    if data[:1] == b'Z':
        return lzma.decompress(data[1:])
    if data[:1] != b'C':
        raise ValueError('unknown file format')
    count = int.from_bytes(data[1:5], 'big')
    bits = Bits(zlib.decompress(data[5:]))
    result = bytearray()
    for i in range(count):
        if bits.get(1):
            n = bits.get(3) + 3
            text = b' '.join(WORDS[bits.get(3)] for _ in range(n))
        else:
            text = BASE[i % 6]
        result.extend(f'{i:05d} '.encode())
        result.extend(text)
        result.extend(f' {i * 7 % 89}\n'.encode())
    return bytes(result)


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        content = decompress(open(args[1], 'rb').read())
        dest = args[2]
    elif len(args) == 2:
        source = open(args[0], 'rb').read()
        encoded = structured(source)
        content = encoded if encoded is not None else b'Z' + lzma.compress(source)
        dest = args[1]
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(dest, 'wb') as stream:
        stream.write(content)


if __name__ == '__main__':
    main()
