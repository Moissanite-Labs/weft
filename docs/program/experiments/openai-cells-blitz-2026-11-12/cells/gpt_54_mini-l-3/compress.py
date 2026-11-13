#!/usr/bin/env python3
import sys, zlib, struct

MAGIC = b'C0MP'


def compress(data: bytes) -> bytes:
    comp = zlib.compress(data, 9)
    return MAGIC + struct.pack('<I', len(data)) + comp


def decompress(blob: bytes) -> bytes:
    if blob[:4] != MAGIC:
        raise SystemExit('bad magic')
    raw_len = struct.unpack('<I', blob[4:8])[0]
    data = zlib.decompress(blob[8:])
    if len(data) != raw_len:
        raise SystemExit('length mismatch')
    return data


def main(argv):
    if len(argv) == 3 and argv[0] == '--decompress':
        inp, out = argv[1], argv[2]
        blob = open(inp, 'rb').read()
        data = decompress(blob)
        open(out, 'wb').write(data)
    elif len(argv) == 2:
        inp, out = argv
        data = open(inp, 'rb').read()
        blob = compress(data)
        open(out, 'wb').write(blob)
    else:
        raise SystemExit('usage: compress.py [--decompress] infile outfile')


if __name__ == '__main__':
    main(sys.argv[1:])
