#!/usr/bin/env python3
"""Lossless byte compressor; CLI: f.py enc|dec, using stdin/stdout."""
import bz2
import lzma
import re
import sys
import zlib

_MAGIC = b'FC1'
_HEX = re.compile(rb'[0-9a-f]{32,}\Z')
_WORD = re.compile(rb'[a-z0-9]{32,}\Z')
_MARK = 0


def _putvar(out, n):
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)


def _getvar(data, pos):
    n = shift = 0
    while True:
        if pos >= len(data) or shift > 63:
            raise ValueError('invalid encoded stream')
        b = data[pos]
        pos += 1
        n |= (b & 127) << shift
        if b < 128:
            return n, pos
        shift += 7


def _pack6(line):
    out = bytearray()
    acc = bits = 0
    for c in line:
        v = c - 48 if c <= 57 else c - 87
        acc = (acc << 6) | v
        bits += 6
        if bits >= 8:
            bits -= 8
            out.append((acc >> bits) & 255)
    if bits:
        out.append((acc << (8 - bits)) & 255)
    return bytes(out)


def _unpack6(data, n):
    out = bytearray()
    acc = bits = pos = 0
    for _ in range(n):
        while bits < 6:
            acc = (acc << 8) | data[pos]
            pos += 1
            bits += 8
        bits -= 6
        v = (acc >> bits) & 63
        out.append(48 + v if v < 10 else 87 + v)
    return bytes(out)


def _transform(raw):
    out = bytearray()
    for line in raw.splitlines(keepends=True):
        nl = line.endswith(b'\n')
        body = line[:-1] if nl else line
        kind = 0
        if len(body) >= 32 and len(body) % 2 == 0 and _HEX.fullmatch(body):
            kind, packed = 1, bytes.fromhex(body.decode('ascii'))
        elif len(body) >= 32 and _WORD.fullmatch(body) and any(c >= 97 for c in body) and not all(c in b'0123456789abcdef' for c in body):
            kind, packed = 2, _pack6(body)
        else:
            # Escape the reserved marker so this transform is unambiguous for all bytes.
            out.extend(line.replace(b'\0', b'\0\0'))
            continue
        out.extend((0, kind))
        _putvar(out, len(body))
        out.extend(packed)
        if nl:
            out.append(10)
    return bytes(out)


def _untransform(data):
    out = bytearray()
    pos = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        if b != 0:
            out.append(b)
            continue
        if pos >= len(data):
            raise ValueError('truncated escape')
        kind = data[pos]
        pos += 1
        if kind == 0:
            out.append(0)
        elif kind in (1, 2):
            n, pos = _getvar(data, pos)
            size = n // 2 if kind == 1 else (n * 6 + 7) // 8
            if kind == 1 and n % 2 or pos + size > len(data):
                raise ValueError('invalid transformed stream')
            if kind == 1:
                out.extend(data[pos:pos + size].hex().encode('ascii'))
            else:
                out.extend(_unpack6(data[pos:pos + size], n))
            pos += size
        else:
            raise ValueError('invalid transformed marker')
    return bytes(out)


def enc(data):
    data = bytes(data)
    candidates = [(b'R', data)]
    transformed = _transform(data)
    candidates.append((b'T', transformed))
    for mode, comp in ((b'B', bz2.compress), (b'Z', zlib.compress), (b'L', lzma.compress)):
        candidates.append((mode, comp(data)))
        candidates.append((mode.lower(), comp(transformed)))
    mode, payload = min(candidates, key=lambda item: len(item[1]) + 4)
    return _MAGIC + mode + payload


def dec(blob):
    blob = bytes(blob)
    if len(blob) < 4 or blob[:3] != _MAGIC:
        raise ValueError('bad f.py stream')
    mode, payload = blob[3:4], blob[4:]
    if mode == b'R':
        return payload
    if mode in (b'B', b'b'):
        payload = bz2.decompress(payload)
    elif mode in (b'Z', b'z'):
        payload = zlib.decompress(payload)
    elif mode in (b'L', b'l'):
        payload = lzma.decompress(payload)
    elif mode != b'T':
        raise ValueError('bad f.py mode')
    return _untransform(payload) if mode in (b'T', b'b', b'z', b'l') else payload

encode = enc
decode = dec

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('enc', 'dec', 'encode', 'decode', 'c', 'd'):
        raise SystemExit('usage: f.py enc|dec')
    fn = enc if sys.argv[1] in ('enc', 'encode', 'c') else dec
    sys.stdout.buffer.write(fn(sys.stdin.buffer.read()))
