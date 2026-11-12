#!/usr/bin/env python3
import argparse
import bz2
import lzma
import struct
import sys
import zlib
from pathlib import Path

MAGIC = b'CMP1'


def compress_data(data: bytes) -> bytes:
    candidates = []
    candidates.append((b'z', zlib.compress(data, 9)))
    candidates.append((b'b', bz2.compress(data, compresslevel=9)))
    presets = [6, 7, 8, 9]
    for preset in presets:
        candidates.append((bytes([preset]), lzma.compress(data, format=lzma.FORMAT_XZ, preset=preset)))
    tag, body = min(candidates, key=lambda x: len(x[1]))
    return MAGIC + tag + struct.pack('>Q', len(data)) + body


def decompress_data(blob: bytes) -> bytes:
    if len(blob) < 13 or blob[:4] != MAGIC:
        raise ValueError('bad header')
    tag = blob[4:5]
    size = struct.unpack('>Q', blob[5:13])[0]
    body = blob[13:]
    if tag == b'z':
        data = zlib.decompress(body)
    elif tag == b'b':
        data = bz2.decompress(body)
    else:
        data = lzma.decompress(body, format=lzma.FORMAT_XZ)
    if len(data) != size:
        raise ValueError('size mismatch')
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('src')
    parser.add_argument('dst')
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    data = src.read_bytes()
    out = decompress_data(data) if args.decompress else compress_data(data)
    dst.write_bytes(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
