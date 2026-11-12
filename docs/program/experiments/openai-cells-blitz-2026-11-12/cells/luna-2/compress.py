#!/usr/bin/env python3
"""Compress the supplied record corpus; all coding uses the Python stdlib."""
import argparse
import struct
import zlib

MAGIC = b'CPZ2'

def encode(data):
    # Records have a deterministic five-digit row id and a mod-89 check field.
    # Factoring those predictable fields out exposes the much smaller body stream.
    lines = data.splitlines()
    bodies = []
    eligible = bool(lines)
    for i, line in enumerate(lines):
        fields = line.split(b' ')
        if (len(line) < 8 or len(fields[0]) != 5 or not fields[0].isdigit()
                or int(fields[0]) != i or not fields[-1].isdigit()
                or int(fields[-1]) != (7 * i) % 89):
            eligible = False
            break
        bodies.append(b' '.join(fields[1:-1]))
    if eligible:
        payload = zlib.compress(b'\n'.join(bodies), 9)
        return MAGIC + b'R' + struct.pack('>I', len(lines)) + payload
    return MAGIC + b'Z' + zlib.compress(data, 9)

def decode(blob):
    if not blob.startswith(MAGIC) or len(blob) < 5:
        raise ValueError('invalid compressed file')
    mode = blob[4:5]
    if mode == b'Z':
        return zlib.decompress(blob[5:])
    if mode == b'R' and len(blob) >= 9:
        count = struct.unpack('>I', blob[5:9])[0]
        bodies = zlib.decompress(blob[9:]).split(b'\n')
        if len(bodies) != count:
            raise ValueError('corrupt record stream')
        return b''.join(('%05d ' % i).encode('ascii') + body + (' %d\n' % ((7*i) % 89)).encode('ascii')
                        for i, body in enumerate(bodies))
    raise ValueError('invalid compressed file')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--decompress', action='store_true')
    p.add_argument('source')
    p.add_argument('destination')
    a = p.parse_args()
    with open(a.source, 'rb') as f:
        data = f.read()
    result = decode(data) if a.decompress else encode(data)
    with open(a.destination, 'wb') as f:
        f.write(result)

if __name__ == '__main__':
    main()
