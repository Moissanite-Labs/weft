#!/usr/bin/env python3
"""Self-contained lossless compressor using learned record structure.

B: bzip2 fallback; S: compressed metadata and three compressed symbol streams.
No source file or external dictionary is needed to decompress.
"""
import bz2
import collections
import json
import math
import struct
import sys
import zlib
from pathlib import Path


def pack(data):
    options = [b'z' + zlib.compress(data, 9), b'b' + bz2.compress(data, 9)]
    alphabet = bytes(sorted(set(data)))
    base = len(alphabet)
    if 0 < base < 256:
        lookup = {v: i for i, v in enumerate(alphabet)}
        rank = 0
        for value in data:
            rank = rank * base + lookup[value]
        options.append(b'r' + struct.pack('<IB', len(data), base) + alphabet + rank.to_bytes((rank.bit_length() + 7) // 8, 'big'))
    if alphabet == b'\x00\x01':
        n, k = len(data), sum(data)
        total = math.comb(n, k)
        rank = 0
        for value in data:
            zero = total * (n - k) // n
            if value:
                rank += zero
                total -= zero
                k -= 1
            else:
                total = zero
            n -= 1
        options.append(b'f' + struct.pack('<II', len(data), sum(data)) + rank.to_bytes((rank.bit_length() + 7) // 8, 'big'))
    return min(options, key=len)


def unpack(data):
    tag = data[:1]
    if tag == b'z':
        return zlib.decompress(data[1:])
    if tag == b'b':
        return bz2.decompress(data[1:])
    if tag == b'r':
        n, base = struct.unpack_from('<IB', data, 1)
        alphabet = data[6:6 + base]
        rank = int.from_bytes(data[6 + base:], 'big')
        output = bytearray(n)
        for i in range(n - 1, -1, -1):
            rank, digit = divmod(rank, base)
            output[i] = alphabet[digit]
        return bytes(output)
    if tag == b'f':
        n, k = struct.unpack_from('<II', data, 1)
        rank = int.from_bytes(data[9:], 'big')
        total = math.comb(n, k)
        output = bytearray()
        while n:
            zero = total * (n - k) // n
            if rank >= zero:
                output.append(1)
                rank -= zero
                total -= zero
                k -= 1
            else:
                output.append(0)
                total = zero
            n -= 1
        return bytes(output)
    raise ValueError('unknown stream codec')


def frame(parts):
    return b''.join(struct.pack('<I', len(p)) + p for p in parts)


def unframe(data):
    parts = []
    pos = 0
    while pos < len(data):
        size, = struct.unpack_from('<I', data, pos)
        pos += 4
        parts.append(data[pos:pos + size])
        pos += size
    return parts


def structured(data):
    lines = data.decode('ascii').splitlines()
    if len(lines) < 20 or not data.endswith(b'\n'):
        raise ValueError('not records')
    records = [line.split(' ', 1) for line in lines]
    width = len(records[0][0])
    start = int(records[0][0])
    if any(r[0] != str(start + i).zfill(width) for i, r in enumerate(records)):
        raise ValueError('not sequential')
    records = [r[1].rsplit(' ', 1) for r in records]
    nums = [int(r[1]) for r in records]
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus
    if any(r[1] != str((nums[0] + i * step) % modulus) for i, r in enumerate(records)):
        raise ValueError('not modular')
    bodies = [r[0] for r in records]
    # Infer the shortest strongly predictive periodic template.
    choices = []
    for period in range(1, min(33, len(lines))):
        templates = [collections.Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        misses = sum(s != templates[i % period] for i, s in enumerate(bodies))
        choices.append((misses * 10 + sum(map(len, templates)), period, templates))
    _, period, templates = min(choices)
    exceptions = [s for i, s in enumerate(bodies) if s != templates[i % period]]
    if any(' '.join(s.split(' ')) != s for s in exceptions):
        raise ValueError('bad spacing')
    vocab = sorted(set(w for s in exceptions for w in s.split(' ')))
    if len(vocab) > 255:
        raise ValueError('large vocabulary')
    index = {w: i for i, w in enumerate(vocab)}
    flags = bytes(s != templates[i % period] for i, s in enumerate(bodies))
    lengths = bytes(len(s.split(' ')) for s in exceptions)
    words = bytes(index[w] for s in exceptions for w in s.split(' '))
    metadata = [len(lines), width, start, nums[0], step, modulus, templates, vocab]
    result = b'S' + frame([pack(json.dumps(metadata, separators=(',', ':')).encode()), pack(flags), pack(lengths), pack(words)])
    if decompress(result) != data:
        raise ValueError('noncanonical records')
    return result


def compress(data):
    baseline = b'B' + bz2.compress(data, 9)
    try:
        candidate = structured(data)
        return min(baseline, candidate, key=len)
    except (ValueError, UnicodeError, IndexError, OverflowError):
        return baseline


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] != b'S':
        raise ValueError('unknown format')
    meta, flags, lengths, words = [unpack(p) for p in unframe(data[1:])]
    n, width, start, offset, step, modulus, templates, vocab = json.loads(meta)
    lengths, words = iter(lengths), iter(words)
    output = []
    for i in range(n):
        body = templates[i % len(templates)]
        if flags[i]:
            body = ' '.join(vocab[next(words)] for _ in range(next(lengths)))
        output.append(str(start + i).zfill(width) + ' ' + body + ' ' + str((offset + i * step) % modulus) + '\n')
    return ''.join(output).encode('ascii')


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args.pop(0)
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
