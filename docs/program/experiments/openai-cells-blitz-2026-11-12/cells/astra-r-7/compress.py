"""Self-contained lossless structured-text compressor, standard library only."""
import sys
import json
import lzma
import bz2
from pathlib import Path
from collections import Counter


def transform(data):
    lines = data.splitlines()
    rows = [line.split(b' ', 1)[1].rsplit(b' ', 1)[0] for line in lines]
    nums = [int(line.rsplit(b' ', 1)[1]) for line in lines]
    n = len(lines)
    width = len(lines[0].split(b' ', 1)[0])
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus
    phrases = [Counter(rows[j::6]).most_common(1)[0][0] for j in range(6)]
    words = sorted({w for i, row in enumerate(rows) if row != phrases[i % 6] for w in row.split(b' ')})
    if len(words) > 256:
        raise ValueError('too many words')
    lookup = {w: i for i, w in enumerate(words)}
    header = [n, width, nums[0], step, modulus, [s.decode('ascii') for s in phrases], [s.decode('ascii') for s in words]]
    payload = bytearray(json.dumps(header, separators=(',', ':')).encode() + b'\n')
    for i, row in enumerate(rows):
        if row == phrases[i % 6]:
            payload.append(0)
        else:
            tokens = row.split(b' ')
            payload.append(len(tokens))
            payload.extend(lookup[w] for w in tokens)
    return bytes(payload)


def untransform(data):
    header, payload = data.split(b'\n', 1)
    n, width, base, step, modulus, phrases, words = json.loads(header)
    phrases = [s.encode('ascii') for s in phrases]
    words = [s.encode('ascii') for s in words]
    rows = []
    pos = 0
    for i in range(n):
        length = payload[pos]
        pos += 1
        if length:
            row = b' '.join(words[v] for v in payload[pos:pos + length])
            pos += length
        else:
            row = phrases[i % 6]
        rows.append(str(i).zfill(width).encode() + b' ' + row + b' ' + str((base + i * step) % modulus).encode() + b'\n')
    if pos != len(payload):
        raise ValueError('trailing data')
    return b''.join(rows)


def compress(data):
    raw = b'R' + lzma.compress(data, preset=9)
    try:
        transformed = transform(data)
        if untransform(transformed) == data:
            packed = b'S' + bz2.compress(transformed, compresslevel=9)
            return min(raw, packed, key=len)
    except (ValueError, IndexError, UnicodeError):
        pass
    return raw


def decompress(data):
    if data[:1] == b'R':
        return lzma.decompress(data[1:])
    if data[:1] == b'S':
        return untransform(bz2.decompress(data[1:]))
    raise ValueError('unknown format')


def main():
    args = sys.argv[1:]
    decode = args[:1] == ['--decompress']
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
