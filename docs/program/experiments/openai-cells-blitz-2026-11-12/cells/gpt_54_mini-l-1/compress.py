#!/usr/bin/env python3
import argparse
import hashlib
import lzma
import struct

MAGIC = b'CX1\0'


def _load(path):
    with open(path, 'rb') as f:
        return f.read()


def _save(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def compress(inp, outp):
    data = _load(inp)
    payload = lzma.compress(
        data,
        format=lzma.FORMAT_XZ,
        preset=9 | lzma.PRESET_EXTREME,
    )
    h = hashlib.blake2s(data, digest_size=16).digest()
    blob = MAGIC + struct.pack('<Q', len(data)) + h + payload
    _save(outp, blob)


def decompress(inp, outp):
    blob = _load(inp)
    if blob[:4] != MAGIC:
        raise SystemExit('bad magic')
    n = struct.unpack('<Q', blob[4:12])[0]
    h = blob[12:28]
    data = lzma.decompress(blob[28:])
    if len(data) != n or hashlib.blake2s(data, digest_size=16).digest() != h:
        raise SystemExit('corrupt archive')
    _save(outp, data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--decompress', action='store_true')
    ap.add_argument('input')
    ap.add_argument('output')
    args = ap.parse_args()
    if args.decompress:
        decompress(args.input, args.output)
    else:
        compress(args.input, args.output)


if __name__ == '__main__':
    main()
