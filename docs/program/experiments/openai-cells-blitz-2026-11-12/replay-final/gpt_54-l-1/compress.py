#!/usr/bin/env python3
import argparse
import bz2
import lzma
import os
import struct
import sys
import zlib

MAGIC = b'CMP1'
ALG_ZLIB = 1
ALG_BZ2 = 2
ALG_LZMA = 3


def compress_file(src, dst):
    data = open(src, 'rb').read()
    candidates = []
    for level in range(1, 10):
        candidates.append((ALG_ZLIB, level, zlib.compress(data, level)))
    for level in range(1, 10):
        candidates.append((ALG_BZ2, level, bz2.compress(data, compresslevel=level)))
    presets = [0, 1, 3, 6, 9]
    for preset in presets:
        candidates.append((ALG_LZMA, preset, lzma.compress(data, preset=preset, format=lzma.FORMAT_XZ)))
    alg, param, comp = min(candidates, key=lambda t: len(t[2]))
    header = MAGIC + bytes([alg, param]) + struct.pack('>Q', len(data))
    with open(dst, 'wb') as f:
        f.write(header)
        f.write(comp)


def decompress_file(src, dst):
    blob = open(src, 'rb').read()
    if len(blob) < 14 or blob[:4] != MAGIC:
        raise SystemExit('invalid input')
    alg = blob[4]
    param = blob[5]
    size = struct.unpack('>Q', blob[6:14])[0]
    comp = blob[14:]
    if alg == ALG_ZLIB:
        data = zlib.decompress(comp)
    elif alg == ALG_BZ2:
        data = bz2.decompress(comp)
    elif alg == ALG_LZMA:
        data = lzma.decompress(comp, format=lzma.FORMAT_XZ)
    else:
        raise SystemExit('unknown algorithm')
    if len(data) != size:
        raise SystemExit('size mismatch')
    with open(dst, 'wb') as f:
        f.write(data)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args(argv)
    if args.decompress:
        decompress_file(args.input, args.output)
    else:
        compress_file(args.input, args.output)


if __name__ == '__main__':
    main()
