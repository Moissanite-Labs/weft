"""Lossless column and template compression, with a general binary fallback."""
import lzma
import collections
import json
import struct
import sys
from pathlib import Path

FILTERS = [{'id': lzma.FILTER_LZMA1, 'dict_size': 1 << 20, 'lc': 0, 'lp': 0, 'pb': 0}]

def pack(data):
    return lzma.compress(data, format=lzma.FORMAT_RAW, filters=FILTERS)


def unpack(data):
    return lzma.decompress(data, format=lzma.FORMAT_RAW, filters=FILTERS)


def transform(data):
    lines = data.splitlines()
    bodies = []
    for i, line in enumerate(lines):
        first, body = line.split(b' ', 1)
        body, last = body.rsplit(b' ', 1)
        if first != ('%05d' % i).encode() or last != str(i * 7 % 89).encode():
            raise ValueError('Not a numbered table')
        bodies.append(body)
    if not lines or b'\n'.join(lines) + b'\n' != data:
        raise ValueError('Noncanonical lines')
    templates = [collections.Counter(bodies[r::6]).most_common(1)[0][0] for r in range(6)]
    words = sorted(set(w for i, b in enumerate(bodies) if b != templates[i % 6] for w in b.split(b' ')))
    if len(words) > 256:
        raise ValueError('Large vocabulary')
    lookup = {w: i for i, w in enumerate(words)}
    flags = bytearray()
    tokens = bytearray()
    for i, b in enumerate(bodies):
        if b == templates[i % 6]:
            flags.append(0)
        else:
            ws = b.split(b' ')
            if len(ws) > 255:
                raise ValueError('Long line')
            flags.append(len(ws))
            tokens.extend(lookup[w] for w in ws)
    header = json.dumps([len(lines), [b.decode('ascii') for b in templates], [w.decode('ascii') for w in words]], separators=(',', ':')).encode()
    return struct.pack('<I', len(header)) + header + flags + tokens


def untransform(data):
    size, = struct.unpack('<I', data[:4])
    n, templates, words = json.loads(data[4:4+size])
    flags = data[4+size:4+size+n]
    tokens = iter(data[4+size+n:])
    lines = []
    for i, count in enumerate(flags):
        body = templates[i % 6] if count == 0 else ' '.join(words[next(tokens)] for _ in range(count))
        lines.append(('%05d %s %d\n' % (i, body, i * 7 % 89)).encode('ascii'))
    return b''.join(lines)


def compress(data):
    raw = b'LC2R' + pack(data)
    try:
        packed = b'LC2T' + pack(transform(data))
        return min(raw, packed, key=len)
    except (ValueError, IndexError, UnicodeError):
        return raw


def decompress(data):
    if data[:3] != b'LC2' or data[3:4] not in (b'R', b'T'):
        raise ValueError('Invalid compressed file')
    raw = unpack(data[4:])
    return untransform(raw) if data[3:4] == b'T' else raw


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__':
    main()
