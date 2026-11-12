#!/usr/bin/env python3
"""Lossless compression with numeric columns and periodic text templates."""
import bz2
from collections import Counter
import struct
import sys


def encode(data):
    fallback = b'BZ2' + bz2.compress(data, 9)
    try:
        lines = data.splitlines()
        cols = [line.split(b' ', 1) for line in lines]
        tails = [rest.rsplit(b' ', 1) for _, rest in cols]
        count = len(lines)
        width = len(cols[0][0])
        step = int(tails[1][1])
        modulus = max(int(tail) for _, tail in tails) + 1
        mids = [mid for mid, _ in tails]
        best = None
        for period in range(1, min(17, count + 1)):
            templates = [Counter(mids[j::period]).most_common(1)[0][0] for j in range(period)]
            residuals = [b'' if mid == templates[i % period] else mid for i, mid in enumerate(mids)]
            payload = b'\n'.join(templates + residuals)
            if best is None or len(payload) < best[0]:
                best = len(payload), period, payload
        _, period, payload = best
        header = struct.pack('>IHHII', count, width, period, step, modulus)
        candidate = b'PT1' + header + bz2.compress(payload, 9)
        if len(candidate) < len(fallback) and decode(candidate) == data:
            return candidate
    except (ValueError, IndexError, OverflowError, struct.error):
        pass
    return fallback


def decode(data):
    if data[:3] == b'BZ2':
        return bz2.decompress(data[3:])
    if data[:3] != b'PT1':
        raise ValueError('unknown compressed format')
    count, width, period, step, modulus = struct.unpack('>IHHII', data[3:19])
    parts = bz2.decompress(data[19:]).split(b'\n')
    templates, residuals = parts[:period], parts[period:]
    if len(residuals) != count:
        raise ValueError('bad line count')
    mids = [mid or templates[i % period] for i, mid in enumerate(residuals)]
    return b''.join(str(i).zfill(width).encode() + b' ' + mid + b' ' + str(i * step % modulus).encode() + b'\n' for i, mid in enumerate(mids))


def main():
    args = sys.argv[1:]
    decompress = bool(args and args[0] == '--decompress')
    if decompress:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as src:
        data = src.read()
    result = decode(data) if decompress else encode(data)
    with open(args[1], 'wb') as dst:
        dst.write(result)


if __name__ == '__main__':
    main()
