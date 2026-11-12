#!/usr/bin/env python3
"""Lossless file compression: structured records with a bzip2 fallback."""
import argparse
import bz2
import re
from pathlib import Path

RECORD = re.compile(rb'([A-Za-z0-9_-]+) line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
WIDTHS = (9, 48, 42)
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def records(data):
    lines = data.split(b'\n')
    newline = lines[-1] == b''
    if newline:
        lines.pop()
    if not lines or len(lines) >= 2**32:
        return None
    prefix = None
    rows = []
    for line in lines:
        m = RECORD.fullmatch(line)
        if m:
            p, a, r, s = m.groups()
            if prefix is None:
                prefix = p
            if p != prefix:
                return None
            rows.append((0, int(a) * 10**15 + int(r) * 10**9 + int(s)))
        elif HEX.fullmatch(line):
            rows.append((1, int(line, 16)))
        elif BASE36.fullmatch(line):
            rows.append((2, int(line, 36)))
        else:
            return None
    return newline, prefix or b'', rows


def render(kind, value, prefix):
    if kind == 0:
        value, seed = divmod(value, 10**9)
        line, ratio = divmod(value, 10**6)
        return prefix + (b' line %d ratio 0.%06d select pick win seed %d' % (line, ratio, seed))
    if kind == 1:
        return ('%096x' % value).encode('ascii')
    text = bytearray()
    while value:
        value, digit = divmod(value, 36)
        text.append(ALPHABET[digit])
    return bytes(reversed(text)).rjust(64, b'0')


def compress(data):
    fallback = b'B' + bz2.compress(data, compresslevel=9)
    parsed = records(data)
    if parsed is None:
        return fallback
    newline, prefix, rows = parsed
    tags = 0
    body = bytearray()
    for kind, value in rows:
        tags = tags * 3 + kind
        body.extend(value.to_bytes(WIDTHS[kind], 'big'))
    n = len(rows)
    tag_bytes = ((3**n - 1).bit_length() + 7) // 8
    packed = (b'P' + bytes([newline]) + n.to_bytes(4, 'big') + prefix + b'\n'
              + tags.to_bytes(tag_bytes, 'big') + body)
    return min((fallback, packed), key=len)


def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    if data[:1] != b'P' or len(data) < 7 or data[1] > 1:
        raise ValueError('Unrecognized compressed format')
    newline = data[1]
    n = int.from_bytes(data[2:6], 'big')
    prefix, body = data[6:].split(b'\n', 1)
    tag_bytes = ((3**n - 1).bit_length() + 7) // 8
    tags = int.from_bytes(body[:tag_bytes], 'big')
    kinds = []
    for _ in range(n):
        tags, kind = divmod(tags, 3)
        kinds.append(kind)
    pos = tag_bytes
    lines = []
    for kind in reversed(kinds):
        end = pos + WIDTHS[kind]
        if end > len(body):
            raise ValueError('Truncated record')
        lines.append(render(kind, int.from_bytes(body[pos:end], 'big'), prefix))
        pos = end
    if pos != len(body) or tags:
        raise ValueError('Invalid packed records')
    return b'\n'.join(lines) + b'\n' * newline


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
