#!/usr/bin/env python3
"""Lossless compression with validated numeric-column and periodic-text models."""
import bz2
import lzma
import collections
import json
import struct
import sys


def transform(data):
    lines = data.splitlines()
    if not lines or not data.endswith(b'\n'):
        raise ValueError('not newline-delimited')
    rows = [line.split(b' ', 1) for line in lines]
    width = len(rows[0][0])
    if any(a != str(i).zfill(width).encode() for i, (a, b) in enumerate(rows)):
        raise ValueError('not sequential')
    bodies, values = zip(*(b.rsplit(b' ', 1) for a, b in rows))
    nums = list(map(int, values))
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus if len(nums) > 1 else 0
    if any(v != str((nums[0] + i * step) % modulus).encode() for i, v in enumerate(values)):
        raise ValueError('not modular')
    choices = []
    for period in range(1, min(24, len(lines)) + 1):
        templates = [collections.Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        cost = sum(len(t) for t in templates) + sum(len(b) + 2 for i, b in enumerate(bodies) if b != templates[i % period])
        choices.append((cost, period, templates))
    _, period, templates = min(choices)
    exceptions = [b.split(b' ') for i, b in enumerate(bodies) if b != templates[i % period]]
    vocab = sorted(set(w for row in exceptions for w in row))
    if len(vocab) > 256 or any(len(row) > 255 for row in exceptions):
        raise ValueError('too many words')
    ids = {w: i for i, w in enumerate(vocab)}
    lengths = bytearray()
    tokens = bytearray()
    for i, body in enumerate(bodies):
        if body == templates[i % period]:
            lengths.append(0)
        else:
            words = body.split(b' ')
            lengths.append(len(words))
            tokens.extend(ids[w] for w in words)
    meta = [len(lines), width, nums[0], step, modulus, [t.decode('latin1') for t in templates], [w.decode('latin1') for w in vocab]]
    header = json.dumps(meta, separators=(',', ':')).encode()
    return struct.pack('>I', len(header)) + header + lengths + tokens


def restore(data):
    size = struct.unpack('>I', data[:4])[0]
    n, width, first, step, modulus, templates, vocab = json.loads(data[4:4 + size])
    templates = [t.encode('latin1') for t in templates]
    vocab = [w.encode('latin1') for w in vocab]
    lengths = data[4 + size:4 + size + n]
    tokens = data[4 + size + n:]
    pos = 0
    lines = []
    for i, length in enumerate(lengths):
        body = templates[i % len(templates)]
        if length:
            body = b' '.join(vocab[t] for t in tokens[pos:pos + length])
            pos += length
        lines.append(str(i).zfill(width).encode() + b' ' + body + b' ' + str((first + i * step) % modulus).encode() + b'\n')
    return b''.join(lines)


def compress(data):
    candidates = [b'B' + bz2.compress(data)]
    try:
        model = transform(data)
        if restore(model) == data:
            candidates.append(b'T' + lzma.compress(model, format=lzma.FORMAT_ALONE, preset=9))
    except (ValueError, IndexError, OverflowError):
        pass
    return min(candidates, key=len)


def decompress(data):
    if data[:1] == b'T':
        return restore(lzma.decompress(data[1:], format=lzma.FORMAT_ALONE))
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    raise ValueError('Unknown format')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('Usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as source:
        result = (decompress if decode else compress)(source.read())
    with open(args[1], 'wb') as target:
        target.write(result)


if __name__ == '__main__':
    main()
