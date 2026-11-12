#!/usr/bin/env python3
"""Lossless compressor with validated structured-text preprocessing."""
import bz2
import collections
import json
import sys


def pack(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out


def unpack(data, pos):
    n = shift = 0
    while True:
        b = data[pos]
        pos += 1
        n |= (b & 127) << shift
        if b < 128:
            return n, pos
        shift += 7


def transform(data):
    lines = data.splitlines(keepends=True)
    bodies = []
    for i, line in enumerate(lines):
        prefix = ('%05d ' % i).encode()
        suffix = (' %d\n' % (i * 7 % 89)).encode()
        if not line.startswith(prefix) or not line.endswith(suffix):
            raise ValueError('not structured')
        bodies.append(line[len(prefix):-len(suffix)].decode('ascii'))
    if not bodies:
        raise ValueError('empty')
    templates = [collections.Counter(bodies[r::6]).most_common(1)[0][0] for r in range(6)]
    exceptions = [(i, b) for i, b in enumerate(bodies) if b != templates[i % 6]]
    vocab = sorted(set(w for _, b in exceptions for w in b.split(' ')))
    codes = {w: i for i, w in enumerate(vocab)}
    header = json.dumps([len(lines), 5, 7, 89, templates, vocab], separators=(',', ':')).encode()
    out = bytearray(pack(len(header))) + header
    previous = -1
    for i, body in exceptions:
        words = body.split(' ')
        out.extend(pack(i - previous))
        out.extend(pack(len(words)))
        for w in words:
            out.extend(pack(codes[w]))
        previous = i
    return bytes(out)


def inverse(data):
    size, pos = unpack(data, 0)
    count, width, step, modulus, templates, vocab = json.loads(data[pos:pos + size])
    pos += size
    bodies = [templates[i % len(templates)] for i in range(count)]
    previous = -1
    while pos < len(data):
        delta, pos = unpack(data, pos)
        previous += delta
        length, pos = unpack(data, pos)
        words = []
        for _ in range(length):
            code, pos = unpack(data, pos)
            words.append(vocab[code])
        bodies[previous] = ' '.join(words)
    return ''.join(str(i).zfill(width) + ' ' + body + ' ' + str(i * step % modulus) + '\n' for i, body in enumerate(bodies)).encode('ascii')


def compress(data):
    best = b'B' + bz2.compress(data)
    try:
        payload = transform(data)
        if inverse(payload) == data:
            candidate = b'S' + bz2.compress(payload)
            if len(candidate) < len(best):
                best = candidate
    except (ValueError, IndexError, UnicodeError):
        pass
    return best


def decompress(data):
    payload = bz2.decompress(data[1:])
    if data[:1] == b'B':
        return payload
    if data[:1] == b'S':
        return inverse(payload)
    raise ValueError('unknown format')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as source:
        data = source.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as destination:
        destination.write(result)


if __name__ == '__main__':
    main()
