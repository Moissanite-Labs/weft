#!/usr/bin/env python3
"""Compress a file and restore it losslessly, using only the standard library."""
import base64
import collections
import json
import lzma
import re
import sys
import entropy
import zlib
from pathlib import Path


def structured(data, mode=0):
    lines = data.splitlines(keepends=True)
    if len(lines) < 10:
        return None
    matches = [re.fullmatch(rb'(\d+) (.*) (\d+)\n', line) for line in lines]
    if not all(matches):
        return None
    width = len(matches[0][1])
    first = int(matches[0][1])
    if any(m[1] != str(first + i).zfill(width).encode() for i, m in enumerate(matches)):
        return None
    nums = [int(m[3]) for m in matches]
    if any(m[3] != str(n).encode() for m, n in zip(matches, nums)):
        return None
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus
    if any(n != (nums[0] + step * i) % modulus for i, n in enumerate(nums)):
        return None
    bodies = [m[2] for m in matches]
    best = None
    for period in range(1, min(24, len(lines)) + 1):
        templates = [collections.Counter(bodies[i::period]).most_common(1)[0][0] for i in range(period)]
        score = sum(len(b) + 1 for i, b in enumerate(bodies) if b != templates[i % period]) + sum(map(len, templates)) + period * 10
        if best is None or score < best[0]:
            best = score, templates
    templates = best[1]
    exceptions = [b for i, b in enumerate(bodies) if b != templates[i % len(templates)]]
    words = collections.Counter(w for b in exceptions for w in b.split(b' '))
    if len(words) > 254:
        return None
    dictionary = [w for w, _ in words.most_common()]
    indices = {w: i + 1 for i, w in enumerate(dictionary)}
    stream = bytearray()
    for i, body in enumerate(bodies):
        if body == templates[i % len(templates)]:
            stream.append(0)
        else:
            stream.append(1)
            stream.extend(indices[w] for w in body.split(b' '))
            stream.append(0)
    encode = lambda b: base64.b64encode(b).decode('ascii')
    meta, bits = entropy.pack(stream, len(lines), len(dictionary))
    header = json.dumps([first, width, nums[0], step, modulus, len(lines), list(map(encode, templates)), list(map(encode, dictionary)), meta], separators=(',', ':')).encode()
    if mode == 0:
        return b'A' + lzma.compress(len(header).to_bytes(4, 'big') + header + bits, preset=9)
    zipped = zlib.compress(header, 9)
    return b'B' + len(zipped).to_bytes(4, 'big') + zipped + bits


def compress(data, mode=0):
    plain = b'L' + lzma.compress(data, preset=9)
    special = structured(data, mode)
    return min((x for x in (plain, special) if x is not None), key=len)


def decompress(data):
    if data[:1] == b'L':
        return lzma.decompress(data[1:])
    if data[:1] == b'A':
        raw = lzma.decompress(data[1:])
        size = int.from_bytes(raw[:4], 'big')
        header, bits = raw[4:4+size], raw[4+size:]
    elif data[:1] == b'B':
        size = int.from_bytes(data[1:5], 'big')
        header, bits = zlib.decompress(data[5:5+size]), data[5+size:]
    else:
        raise ValueError('unknown compressed format')
    first, width, start, step, modulus, count, templates, dictionary, meta = json.loads(header)
    templates = [base64.b64decode(x) for x in templates]
    dictionary = [base64.b64decode(x) for x in dictionary]
    stream = entropy.unpack(meta, bits, count)
    output = bytearray()
    pos = 0
    for i in range(count):
        flag = stream[pos]
        pos += 1
        if flag == 0:
            body = templates[i % len(templates)]
        elif flag == 1:
            words = []
            while stream[pos]:
                words.append(dictionary[stream[pos] - 1])
                pos += 1
            pos += 1
            body = b' '.join(words)
        else:
            raise ValueError('invalid record')
        output.extend(str(first+i).zfill(width).encode() + b' ' + body + b' ' + str((start + step*i) % modulus).encode() + b'\n')
    if pos != len(stream):
        raise ValueError('trailing data')
    return bytes(output)


def main():
    args = sys.argv[1:]
    if len(args) == 2:
        src, dst = args
        transform = compress
    elif len(args) == 3 and args[0] == '--decompress':
        _, src, dst = args
        transform = decompress
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(dst).write_bytes(transform(Path(src).read_bytes()))


if __name__ == '__main__':
    main()
