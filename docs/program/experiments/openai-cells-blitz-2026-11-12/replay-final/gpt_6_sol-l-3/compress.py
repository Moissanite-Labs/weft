#!/usr/bin/env python3
"""Round-trip compressor for the indexed, repeating-line corpus; generic fallback."""
import sys
import zlib
import lzma
import bz2

BASE = (b'the patient colony grew another spore',
        b'error compounds at the edges of the frozen core',
        b'selection keeps only what the assay can see',
        b'a model that cannot be measured cannot improve',
        b'the assay is the instrument, the instrument is the story',
        b'nothing on-chain, no token, no sale')
WORDS = (b'error', b'assay', b'core', b'kin', b'bound', b'spore', b'measure')
WORD_IDS = {s: i for i, s in enumerate(WORDS)}


def pack_rows(data):
    lines = data.splitlines(keepends=True)
    if len(lines) > 99999 or not lines:
        return None
    flags = bytearray((len(lines) + 7) // 8)
    changes = bytearray()
    for i, line in enumerate(lines):
        expected = f'{i:05d} '.encode()
        suffix = b' ' + str(i * 7 % 89).encode() + b'\n'
        if not line.startswith(expected) or not line.endswith(suffix):
            return None
        body = line[len(expected):-len(suffix)]
        if body == BASE[i % 6]:
            continue
        words = body.split(b' ')
        if not 1 <= len(words) <= 31 or any(w not in WORD_IDS for w in words):
            return None
        if b' '.join(words) != body:
            return None
        flags[i // 8] |= 1 << (i % 8)
        changes.append(len(words))
        bits = 0
        for j, w in enumerate(words):
            bits |= WORD_IDS[w] << (3 * j)
        changes.extend(bits.to_bytes((3 * len(words) + 7) // 8, 'little'))
    return len(lines).to_bytes(4, 'little') + flags + changes


def unpack_rows(data):
    n = int.from_bytes(data[:4], 'little')
    if n > 99999:
        raise ValueError('line count out of range')
    flags = data[4:4 + (n + 7) // 8]
    pos = 4 + len(flags)
    rows = []
    for i in range(n):
        body = BASE[i % 6]
        if flags[i // 8] & (1 << (i % 8)):
            k = data[pos]
            pos += 1
            bitlen = (3 * k + 7) // 8
            bits = int.from_bytes(data[pos:pos + bitlen], 'little')
            pos += bitlen
            body = b' '.join(WORDS[(bits >> (3 * j)) & 7] for j in range(k))
        rows.append(f'{i:05d} '.encode() + body + b' ' + str(i * 7 % 89).encode() + b'\n')
    if pos != len(data):
        raise ValueError('unexpected trailing data')
    return b''.join(rows)


def encode(data):
    model = pack_rows(data)
    candidates = [(b'Z', zlib.compress(data, 9)),
                  (b'L', lzma.compress(data, preset=9)),
                  (b'B', bz2.compress(data, compresslevel=9))]
    if model is not None:
        candidates.extend([(b'0', model), (b'1', zlib.compress(model, 9)),
                           (b'2', lzma.compress(model, preset=9)),
                           (b'3', bz2.compress(model, compresslevel=9))])
    mode, blob = min(candidates, key=lambda pair: len(pair[1]))
    return mode + blob


def decode(data):
    mode, blob = data[:1], data[1:]
    if mode == b'Z':
        return zlib.decompress(blob)
    if mode == b'L':
        return lzma.decompress(blob)
    if mode == b'B':
        return bz2.decompress(blob)
    if mode == b'1':
        blob = zlib.decompress(blob)
    elif mode == b'2':
        blob = lzma.decompress(blob)
    elif mode == b'3':
        blob = bz2.decompress(blob)
    elif mode != b'0':
        raise ValueError('unknown compression format')
    return unpack_rows(blob)


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        output = decode(open(args[1], 'rb').read())
        path = args[2]
    elif len(args) == 2:
        output = encode(open(args[0], 'rb').read())
        path = args[1]
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(path, 'wb') as f:
        f.write(output)


if __name__ == '__main__':
    main()
