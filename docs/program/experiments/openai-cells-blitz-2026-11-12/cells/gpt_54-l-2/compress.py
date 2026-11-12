#!/usr/bin/env python3
import argparse
import bz2
import lzma
import struct
import sys
import zlib

MAGIC = b"CP01"
METHODS = {
    b"z": lambda data: zlib.compress(data, 9),
    b"b": lambda data: bz2.compress(data, compresslevel=9),
    b"x": lambda data: lzma.compress(data, format=lzma.FORMAT_XZ, preset=9 | lzma.PRESET_EXTREME),
}
DECOMPRESS = {
    b"z": zlib.decompress,
    b"b": bz2.decompress,
    b"x": lzma.decompress,
}


def compress_file(src_path, dst_path):
    data = open(src_path, 'rb').read()
    best_method = None
    best_payload = None
    for method, fn in METHODS.items():
        payload = fn(data)
        if best_payload is None or len(payload) < len(best_payload):
            best_method = method
            best_payload = payload
    with open(dst_path, 'wb') as f:
        f.write(MAGIC)
        f.write(best_method)
        f.write(struct.pack('>Q', len(data)))
        f.write(best_payload)


def decompress_file(src_path, dst_path):
    blob = open(src_path, 'rb').read()
    if len(blob) < 13 or blob[:4] != MAGIC:
        raise SystemExit('invalid file format')
    method = blob[4:5]
    size = struct.unpack('>Q', blob[5:13])[0]
    if method not in DECOMPRESS:
        raise SystemExit('unknown compression method')
    data = DECOMPRESS[method](blob[13:])
    if len(data) != size:
        raise SystemExit('size mismatch after decompression')
    with open(dst_path, 'wb') as f:
        f.write(data)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--decompress', action='store_true')
    p.add_argument('input')
    p.add_argument('output')
    args = p.parse_args(argv)
    if args.decompress:
        decompress_file(args.input, args.output)
    else:
        compress_file(args.input, args.output)


if __name__ == '__main__':
    main()
