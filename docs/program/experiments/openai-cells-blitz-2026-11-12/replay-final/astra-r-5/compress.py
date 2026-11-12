#!/usr/bin/env python3
"""Lossless compression with a reversible tabular-text transform."""
import bz2
import json
import struct
import sys
from collections import Counter
from pathlib import Path


def transform(data):
    lines = data.splitlines()
    rows = [line.split(b' ', 1) for line in lines]
    width = len(rows[0][0])
    bodies = []
    nums = []
    for i, (index, rest) in enumerate(rows):
        if index != str(i).zfill(width).encode():
            raise ValueError('nonsequential')
        body, num = rest.rsplit(b' ', 1)
        bodies.append(body.decode('ascii'))
        nums.append(int(num))
    step = nums[1]
    modulus = max(nums) + 1
    if nums != [i * step % modulus for i in range(len(nums))]:
        raise ValueError('nonperiodic')
    options = []
    for period in range(1, 13):
        counters = [Counter(bodies[j::period]) for j in range(period)]
        common = [c.most_common(1)[0] for c in counters]
        options.append((sum(n for _, n in common) - 20 * period, period, [s for s, _ in common]))
    _, period, templates = max(options)
    words = sorted(set(w for i, body in enumerate(bodies) if body != templates[i % period] for w in body.split(' ')))
    if len(words) > 255:
        raise ValueError('vocabulary too large')
    ids = {w: i for i, w in enumerate(words)}
    stream = bytearray()
    for i, body in enumerate(bodies):
        if body == templates[i % period]:
            stream.append(0)
        else:
            tokens = body.split(' ')
            stream.append(len(tokens))
            stream.extend(ids[w] for w in tokens)
    header = json.dumps([width, step, modulus, templates, words], separators=(',', ':')).encode()
    return struct.pack('<I', len(header)) + header + stream


def inverse(data):
    n = struct.unpack_from('<I', data)[0]
    width, step, modulus, templates, words = json.loads(data[4:4+n])
    stream = data[4+n:]
    out = []
    pos = 0
    while pos < len(stream):
        length = stream[pos]
        pos += 1
        i = len(out)
        if length:
            body = ' '.join(words[w] for w in stream[pos:pos+length])
            pos += length
        else:
            body = templates[i % len(templates)]
        out.append(f'{i:0{width}d} {body} {i * step % modulus}\n')
    return ''.join(out).encode('ascii')


def compress(data):
    raw = b'B' + bz2.compress(data, 9)
    try:
        transformed = transform(data)
        if inverse(transformed) == data:
            candidate = b'T' + bz2.compress(transformed, 9)
            return min(raw, candidate, key=len)
    except (ValueError, IndexError, UnicodeError):
        pass
    return raw


def decompress(data):
    payload = bz2.decompress(data[1:])
    return inverse(payload) if data[:1] == b'T' else payload


def main():
    args = sys.argv[1:]
    decoding = bool(args and args[0] == '--decompress')
    if decoding:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decoding else compress(data))


if __name__ == '__main__':
    main()
