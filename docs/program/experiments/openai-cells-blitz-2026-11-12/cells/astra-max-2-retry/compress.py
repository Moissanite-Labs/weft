#!/usr/bin/env python3
"""Self-contained, lossless compression of patterned text; stdlib only."""
import argparse
import bz2
from collections import Counter
import json
import math
from pathlib import Path
import zlib

MAGIC = b'CP1'
HEADER_CODEC = b'J'


def structure(data):
    if not data.endswith(b'\n'):
        return None
    lines = data[:-1].split(b'\n')
    if len(lines) < 2:
        return None
    prefixes, bodies, tails = [], [], []
    for line in lines:
        first, rest = line.split(b' ', 1)
        body, last = rest.rsplit(b' ', 1)
        if not first.isdigit() or not last.isdigit():
            return None
        prefixes.append(first)
        bodies.append(body)
        tails.append(int(last))
        if last != str(tails[-1]).encode():
            return None
    n, width, start = len(lines), len(prefixes[0]), int(prefixes[0])
    modulus = max(tails) + 1
    step = (tails[1] - tails[0]) % modulus
    for i in range(n):
        if prefixes[i] != f'{start+i:0{width}d}'.encode():
            return None
        if tails[i] != (tails[0] + step*i) % modulus:
            return None
    best_score, templates = -1, None
    for period in range(1, min(n, 32) + 1):
        popular = [Counter(bodies[r::period]).most_common(1)[0] for r in range(period)]
        score = sum(count for body, count in popular)
        if score > best_score:
            best_score = score
            templates = [body for body, count in popular]
    positions = [i for i, body in enumerate(bodies) if body != templates[i % len(templates)]]
    tokens = [bodies[i].split(b' ') for i in positions]
    vocab = sorted({word for row in tokens for word in row})
    lo = min(map(len, tokens), default=0)
    hi = max(map(len, tokens), default=0)
    meta = [n, width, start, tails[0], step, modulus, len(positions), lo, hi,
            [s.decode('latin1') for s in templates], [s.decode('latin1') for s in vocab]]
    return meta, positions, tokens, vocab


def encode_mask(n, positions):
    k = len(positions)
    ways = math.comb(n, k)
    size = ((ways - 1).bit_length() + 7) // 8
    rank, remaining = 0, k
    chosen = set(positions)
    for i in range(n):
        if not remaining:
            break
        zero = ways * (n - i - remaining) // (n - i)
        if i in chosen:
            rank += zero
            ways -= zero
            remaining -= 1
        else:
            ways = zero
    return rank.to_bytes(size, 'big')


def decode_mask(n, k, data):
    ways = math.comb(n, k)
    size = ((ways - 1).bit_length() + 7) // 8
    if len(data) < size:
        raise ValueError('Truncated mask')
    rank = int.from_bytes(data[:size], 'big')
    if rank >= ways:
        raise ValueError('Invalid mask')
    remaining, positions = k, []
    for i in range(n):
        if not remaining:
            break
        zero = ways * (n - i - remaining) // (n - i)
        if rank >= zero:
            positions.append(i)
            rank -= zero
            ways -= zero
            remaining -= 1
        else:
            ways = zero
    return positions, data[size:]


def compress(data):
    raw = MAGIC + b'B' + bz2.compress(data, compresslevel=9)
    try:
        parsed = structure(data)
    except (ValueError, IndexError):
        parsed = None
    if parsed is None:
        return raw
    meta, positions, rows, vocab = parsed
    index = {word: i for i, word in enumerate(vocab)}
    base, length_base = max(1, len(vocab)), meta[8] - meta[7] + 1
    value = 0
    for row in reversed(rows):
        for word in reversed(row):
            value = value * base + index[word]
        value = value * length_base + len(row) - meta[7]
    symbols = value.to_bytes((value.bit_length() + 7) // 8, 'big')
    header = json.dumps(meta, separators=(',', ':')).encode()
    header = zlib.compress(header, 9) if HEADER_CODEC == b'Z' else bz2.compress(header)
    archive = (MAGIC + HEADER_CODEC + zlib.crc32(data).to_bytes(4, 'big') + header
               + encode_mask(meta[0], positions) + symbols)
    return min((raw, archive), key=len)


def decompress(data):
    if data[:3] != MAGIC:
        raise ValueError('Not a CP1 archive')
    mode = data[3:4]
    if mode == b'B':
        return bz2.decompress(data[4:])
    if mode not in (b'Z', b'J'):
        raise ValueError('Unknown archive mode')
    checksum = int.from_bytes(data[4:8], 'big')
    decoder = zlib.decompressobj() if mode == b'Z' else bz2.BZ2Decompressor()
    header = decoder.decompress(data[8:])
    if not decoder.eof:
        raise ValueError('Truncated header')
    n, width, start, tail, step, modulus, k, lo, hi, templates, vocab = json.loads(header)
    templates = [s.encode('latin1') for s in templates]
    vocab = [s.encode('latin1') for s in vocab]
    positions, symbols = decode_mask(n, k, decoder.unused_data)
    value = int.from_bytes(symbols, 'big')
    exceptions = {}
    for i in positions:
        value, length = divmod(value, hi - lo + 1)
        row = []
        for _ in range(length + lo):
            value, word = divmod(value, len(vocab))
            row.append(vocab[word])
        exceptions[i] = b' '.join(row)
    if value:
        raise ValueError('Excess symbol data')
    result = b''.join(f'{start+i:0{width}d}'.encode() + b' '
                      + exceptions.get(i, templates[i % len(templates)]) + b' '
                      + str((tail + step*i) % modulus).encode() + b'\n' for i in range(n))
    if zlib.crc32(result) != checksum:
        raise ValueError('Checksum mismatch')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    data = Path(args.source).read_bytes()
    result = decompress(data) if args.decompress else compress(data)
    Path(args.destination).write_bytes(result)


if __name__ == '__main__':
    main()
