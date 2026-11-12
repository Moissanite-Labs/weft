#!/usr/bin/env python3
"""Compress and restore files using standard-library codecs."""
import bz2
import collections
import lzma
import re
import struct
import sys
import zlib

MAGIC = b"CPZ1"
_LINE = re.compile(rb"([0-9]{5}) (.*) ([0-9]+)\n\Z")


def _varint(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out


def _readvar(data, pos):
    value = shift = 0
    while pos < len(data):
        byte = data[pos]
        pos += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, pos
        shift += 7
        if shift > 63:
            raise ValueError("invalid integer")
    raise ValueError("truncated integer")


def _text_transform(data):
    lines = data.splitlines(keepends=True)
    rows = []
    frequencies = collections.Counter()
    for line in lines:
        match = _LINE.fullmatch(line)
        if match is None:
            return None
        prefix, body, suffix = match.groups()
        # Restrict the reversible integer representation to canonical numbers.
        if str(int(suffix)).encode() != suffix:
            return None
        rows.append((int(prefix), body, int(suffix)))
        frequencies[body] += 1
    if not rows:
        return None

    ordered = [body for body, _ in frequencies.most_common()]
    ids = {body: i for i, body in enumerate(ordered)}
    out = bytearray(b"LT1")
    out.extend(_varint(len(ordered)))
    for body in ordered:
        out.extend(_varint(len(body)))
        out.extend(body)
    out.extend(_varint(len(rows)))
    previous = 0
    for prefix, body, suffix in rows:
        delta = prefix - previous
        previous = prefix
        # Signed zig-zag delta keeps sequential and nearby prefixes tiny.
        out.extend(_varint(delta * 2 if delta >= 0 else -delta * 2 - 1))
        out.extend(_varint(ids[body]))
        out.extend(_varint(suffix))
    return bytes(out)


def _text_restore(data):
    if not data.startswith(b"LT1"):
        raise ValueError("invalid transformed stream")
    pos = 3
    count, pos = _readvar(data, pos)
    dictionary = []
    for _ in range(count):
        size, pos = _readvar(data, pos)
        end = pos + size
        if end > len(data):
            raise ValueError("truncated dictionary")
        dictionary.append(data[pos:end])
        pos = end
    rows, pos = _readvar(data, pos)
    result = bytearray()
    previous = 0
    for _ in range(rows):
        delta, pos = _readvar(data, pos)
        delta = delta // 2 if delta % 2 == 0 else -(delta // 2) - 1
        previous += delta
        ident, pos = _readvar(data, pos)
        suffix, pos = _readvar(data, pos)
        if ident >= len(dictionary) or previous < 0 or previous > 99999:
            raise ValueError("invalid row")
        result.extend(f"{previous:05d} ".encode())
        result.extend(dictionary[ident])
        result.extend(b" " + str(suffix).encode() + b"\n")
    if pos != len(data):
        raise ValueError("trailing transformed data")
    return bytes(result)


def _codecs(data):
    return ((0, zlib.compress(data)),
            (1, bz2.compress(data, compresslevel=9)),
            (2, lzma.compress(data, preset=6)))


def compress(data):
    choices = [(len(payload), codec, payload) for codec, payload in _codecs(data)]
    transformed = _text_transform(data)
    if transformed is not None:
        for subcodec, payload in _codecs(transformed):
            wrapped = bytes((subcodec,)) + payload
            choices.append((len(wrapped), 3, wrapped))
    _, codec, payload = min(choices, key=lambda item: item[0])
    return MAGIC + bytes((codec,)) + struct.pack(">Q", len(data)) + payload


def decompress(blob):
    if len(blob) < 13 or blob[:4] != MAGIC:
        raise ValueError("invalid compressed file")
    codec = blob[4]
    size = struct.unpack(">Q", blob[5:13])[0]
    payload = blob[13:]
    if codec == 0:
        result = zlib.decompress(payload)
    elif codec == 1:
        result = bz2.decompress(payload)
    elif codec == 2:
        result = lzma.decompress(payload)
    elif codec == 3:
        if not payload:
            raise ValueError("truncated transformed stream")
        subcodec, payload = payload[0], payload[1:]
        if subcodec == 0:
            transformed = zlib.decompress(payload)
        elif subcodec == 1:
            transformed = bz2.decompress(payload)
        elif subcodec == 2:
            transformed = lzma.decompress(payload)
        else:
            raise ValueError("unknown transformed codec")
        result = _text_restore(transformed)
    else:
        raise ValueError("unknown codec")
    if len(result) != size:
        raise ValueError("decompressed length mismatch")
    return result


def main(argv):
    if len(argv) == 3 and argv[1] != "--decompress":
        with open(argv[1], "rb") as f:
            data = f.read()
        with open(argv[2], "wb") as f:
            f.write(compress(data))
    elif len(argv) == 4 and argv[1] == "--decompress":
        with open(argv[2], "rb") as f:
            data = f.read()
        with open(argv[3], "wb") as f:
            f.write(decompress(data))
    else:
        raise SystemExit("usage: compress.py input output | compress.py --decompress input output")


if __name__ == "__main__":
    main(sys.argv)
