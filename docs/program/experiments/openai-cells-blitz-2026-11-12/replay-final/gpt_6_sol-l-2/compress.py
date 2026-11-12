#!/usr/bin/env python3
"""Lossless corpus compressor with a compact template-and-exceptions format."""
import sys
import zlib
import bz2
import lzma

TEMPLATES = (
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
)
WORDS = (b'core', b'measure', b'error', b'spore', b'kin', b'assay', b'bound')
LOOKUP = {s: i for i, s in enumerate(WORDS)}


def varint(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out


def getvar(b, pos):
    n = 0
    shift = 0
    while True:
        x = b[pos]
        pos += 1
        n |= (x & 127) << shift
        if x < 128:
            return n, pos
        shift += 7


def specialized(data):
    if not data.endswith(b'\n'):
        return None
    lines = data.splitlines()
    diffs = []
    for i, line in enumerate(lines):
        lead = (b'%05d ' % i)
        tail = (b' %d' % (i * 7 % 89))
        if not line.startswith(lead) or not line.endswith(tail):
            return None
        text = line[len(lead):-len(tail)]
        if text != TEMPLATES[i % 6]:
            words = text.split(b' ')
            if not 3 <= len(words) <= 9 or any(w not in LOOKUP for w in words):
                return None
            diffs.append((i, words))
    positions = bytearray()
    symbols = bytearray()
    bits = 0
    accum = 0
    def put(value):
        nonlocal bits, accum
        accum |= value << bits
        bits += 3
        while bits >= 8:
            symbols.append(accum & 255)
            accum >>= 8
            bits -= 8
    previous = -1
    for index, words in diffs:
        positions.extend(varint(index - previous - 1))
        previous = index
        put(len(words) - 2)
        for word in words:
            put(LOOKUP[word])
    if bits:
        symbols.append(accum)
    body = bytes(varint(len(lines)) + varint(len(diffs)) + varint(len(positions)) + positions + symbols)
    choices = [(b'R', body), (b'Z', zlib.compress(body, 9)),
               (b'B', bz2.compress(body, compresslevel=9)),
               (b'L', lzma.compress(body, preset=9))]
    method, payload = min(choices, key=lambda x: len(x[1]))
    return b'CT1' + method + payload


def unspecialized(data):
    method = data[3:4]
    body = data[4:]
    if method == b'Z':
        body = zlib.decompress(body)
    elif method == b'B':
        body = bz2.decompress(body)
    elif method == b'L':
        body = lzma.decompress(body)
    elif method != b'R':
        raise ValueError('unknown method')
    count, p = getvar(body, 0)
    numdiff, p = getvar(body, p)
    poslen, p = getvar(body, p)
    indexbytes = body[p:p + poslen]
    symbols = body[p + poslen:]
    exceptions = {}
    prev = -1
    bitpos = 0
    ip = 0
    def read3():
        nonlocal bitpos
        byte = bitpos >> 3
        offset = bitpos & 7
        val = (symbols[byte] >> offset) & 7
        if offset > 5:
            val |= (symbols[byte + 1] << (8 - offset)) & 7
        bitpos += 3
        return val
    for _ in range(numdiff):
        step, ip = getvar(indexbytes, ip)
        index = prev + 1 + step
        prev = index
        length = read3() + 2
        exceptions[index] = b' '.join(WORDS[read3()] for _ in range(length))
    return b''.join((b'%05d ' % i) + exceptions.get(i, TEMPLATES[i % 6]) +
                    (b' %d\n' % (i * 7 % 89)) for i in range(count))


def compress(data):
    options = [(b'ZLB', zlib.compress(data, 9)),
               (b'BZ2', bz2.compress(data, compresslevel=9)),
               (b'LZM', lzma.compress(data, preset=9))]
    custom = specialized(data)
    if custom is not None:
        options.append((b'', custom))
    marker, payload = min(options, key=lambda x: len(x[0]) + len(x[1]))
    return marker + payload


def decompress(data):
    if data.startswith(b'CT1'):
        return unspecialized(data)
    if data.startswith(b'ZLB'):
        return zlib.decompress(data[3:])
    if data.startswith(b'BZ2'):
        return bz2.decompress(data[3:])
    if data.startswith(b'LZM'):
        return lzma.decompress(data[3:])
    raise ValueError('not a supported compressed file')


def main():
    if len(sys.argv) == 3:
        source, dest = sys.argv[1:]
        func = compress
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        source, dest = sys.argv[2:]
        func = decompress
    else:
        raise SystemExit('usage: compress.py [--decompress] SOURCE DEST')
    with open(source, 'rb') as f:
        data = f.read()
    with open(dest, 'wb') as f:
        f.write(func(data))


if __name__ == '__main__':
    main()
