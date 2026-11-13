#!/usr/bin/env python3
"""Self-contained lossless compressor for structured logs, with an LZMA fallback."""
import argparse
import bz2
from collections import Counter
import lzma
import math
from pathlib import Path
import re
import zlib

METHOD = b'Z'


def put(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out


def structure(data):
    rows = [re.fullmatch(rb'([0-9]+) (.*) ([0-9]+)\n', line)
            for line in data.splitlines(keepends=True)]
    if len(rows) < 3 or not all(rows):
        return None
    n = len(rows)
    ids = [int(r[1]) for r in rows]
    values = [int(r[3]) for r in rows]
    messages = [r[2] for r in rows]
    width, start, step = len(rows[0][1]), ids[0], ids[1] - ids[0]
    if step < 0 or any(r[1] != str(start + i * step).zfill(width).encode()
                       for i, r in enumerate(rows)):
        return None
    modulus = math.gcd(*(values[i] - 2 * values[i-1] + values[i-2]
                         for i in range(2, n)))
    offset = values[0]
    stride = values[1] - offset
    if modulus:
        stride %= modulus
    if stride < 0 or any(r[3] != str((offset + i * stride) % modulus if modulus
                                    else offset + i * stride).encode()
                         for i, r in enumerate(rows)):
        return None
    best = None
    for period in range(1, min(n, 32) + 1):
        table = [Counter(messages[j::period]).most_common(1)[0][0]
                 for j in range(period)]
        errors = sum(m != table[i % period] for i, m in enumerate(messages))
        cost = sum(len(t) + 1 for t in table) + 6 * errors
        if best is None or cost < best[0]:
            best = cost, table
    table = best[1]
    period = len(table)
    exceptions = [(i, m.split(b' ')) for i, m in enumerate(messages)
                  if m != table[i % period]]
    vocabulary = sorted({w for _, words in exceptions for w in words})
    indexes = {w: i for i, w in enumerate(vocabulary)}
    out = bytearray()
    for x in (n, width, start, step, modulus, offset, stride, period):
        out.extend(put(x))
    for t in table:
        out.extend(put(len(t))); out.extend(t)
    out.extend(put(len(vocabulary)))
    for w in vocabulary:
        out.extend(put(len(w))); out.extend(w)
    out.extend(put(len(exceptions)))
    previous = -1
    for i, words in exceptions:
        out.extend(put(i - previous - 1)); previous = i
        out.extend(put(len(words)))
        for w in words:
            out.extend(put(indexes[w]))
    return bytes(out)


def unstructure(data):
    pos = 0
    def get():
        nonlocal pos
        value = shift = 0
        while True:
            b = data[pos]; pos += 1
            value |= (b & 127) << shift
            if b < 128:
                return value
            shift += 7
    def text():
        nonlocal pos
        size = get()
        result = data[pos:pos+size]; pos += size
        return result
    n, width, start, step, modulus, offset, stride, period = [get() for _ in range(8)]
    table = [text() for _ in range(period)]
    vocabulary = [text() for _ in range(get())]
    exceptions = {}
    previous = -1
    for _ in range(get()):
        i = previous + get() + 1; previous = i
        exceptions[i] = b' '.join(vocabulary[get()] for _ in range(get()))
    if pos != len(data):
        raise ValueError('trailing structured data')
    return b''.join(str(start + i * step).zfill(width).encode() + b' ' +
                    exceptions.get(i, table[i % period]) + b' ' +
                    str((offset + i * stride) % modulus if modulus
                        else offset + i * stride).encode() + b'\n' for i in range(n))


def pack(data, method):
    if method == b'L':
        return lzma.compress(data, format=lzma.FORMAT_ALONE, preset=9)
    if method == b'B':
        return bz2.compress(data, compresslevel=9)
    return zlib.compress(data, 9)


def compress(data):
    candidates = [b'CP2L\0' + pack(data, b'L')]
    prepared = structure(data)
    if prepared is not None:
        candidates.append(b'CP2' + METHOD + b'\1' + pack(prepared, METHOD))
    return min(candidates, key=len)


def decompress(data):
    if data[:3] != b'CP2':
        raise ValueError('not a CP2 compressed file')
    method, kind = data[3:4], data[4]
    if method == b'L':
        decoded = lzma.decompress(data[5:], format=lzma.FORMAT_ALONE)
    elif method == b'B':
        decoded = bz2.decompress(data[5:])
    elif method == b'Z':
        decoded = zlib.decompress(data[5:])
    else:
        raise ValueError('unknown codec')
    if kind not in (0, 1):
        raise ValueError('unknown representation')
    return unstructure(decoded) if kind else decoded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source'); parser.add_argument('destination')
    args = parser.parse_args()
    raw = Path(args.source).read_bytes()
    result = decompress(raw) if args.decompress else compress(raw)
    Path(args.destination).write_bytes(result)


if __name__ == '__main__':
    main()
