"""Lossless LZMA with verified numeric-column prediction."""
import lzma
import json
import sys
from pathlib import Path


def restore(raw):
    header, body = raw.split(b'\n', 1)
    width, step, modulus = json.loads(header)
    return b''.join(str(i).zfill(width).encode() + b' ' + line + b' ' + str(i * step % modulus).encode() + b'\n' for i, line in enumerate(body.splitlines()))


def compress(data):
    candidate = data
    mode = b'B'
    try:
        rows = [line.split(b' ', 1) for line in data.splitlines()]
        fields = [row[1].rsplit(b' ', 1) for row in rows]
        width = len(rows[0][0])
        nums = [int(f[1]) for f in fields]
        header = json.dumps([width, nums[1], max(nums) + 1], separators=(',', ':')).encode()
        raw = header + b'\n' + b'\n'.join(f[0] for f in fields) + b'\n'
        if restore(raw) == data:
            candidate, mode = raw, b'N'
    except (ValueError, IndexError, ZeroDivisionError):
        pass
    return mode + lzma.compress(candidate, preset=6)


def decompress(data):
    raw = lzma.decompress(data[1:])
    return restore(raw) if data[:1] == b'N' else raw


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args.pop(0)
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    source, destination = map(Path, args)
    destination.write_bytes((decompress if decode else compress)(source.read_bytes()))


if __name__ == '__main__':
    main()
