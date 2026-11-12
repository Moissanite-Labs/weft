#!/usr/bin/env python3
"""Compact lossless codec for line-oriented hex, base36, and telemetry text."""
import sys
import re
import packing

MAGIC = b'CH1'
TEMPLATE = re.compile(rb'e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)\Z')
BASE36 = b'0123456789abcdefghijklmnopqrstuvwxyz'

def encode(data):
    lines = data.splitlines(keepends=True)
    if any(not line.endswith(b'\n') for line in lines):
        raise ValueError('input must end with a newline')
    count = len(lines)
    if count > 65535:
        raise ValueError('too many lines')
    types = bytearray((count + 3) // 4)
    payload = bytearray()
    for i, line in enumerate(lines):
        line = line[:-1]
        match = TEMPLATE.fullmatch(line)
        if match and len(match[1]) == len(str(int(match[1]))) and len(match[3]) == len(str(int(match[3]))) and int(match[1]) < 1 << 24 and int(match[3]) < 1 << 32:
            typ = 0
            payload.extend(packing.pack(*(int(x) for x in match.groups())))
        elif len(line) == 96 and all(c in b'0123456789abcdef' for c in line):
            typ = 1
            payload.extend(bytes.fromhex(line.decode('ascii')))
        elif len(line) == 64 and all(c in BASE36 for c in line):
            typ = 2
            payload.extend(int(line.decode('ascii'), 36).to_bytes(42, 'big'))
        else:
            typ = 3
            if len(line) > 65535:
                raise ValueError('line too long')
            payload.extend(len(line).to_bytes(2, 'big'))
            payload.extend(line)
        types[i // 4] |= typ << (2 * (i % 4))
    return MAGIC + count.to_bytes(2, 'big') + types + payload

def decode(data):
    if not data.startswith(MAGIC):
        raise ValueError('invalid format')
    count = int.from_bytes(data[3:5], 'big')
    types = data[5:5 + (count + 3)//4]
    p = 5 + len(types)
    result = bytearray()
    for i in range(count):
        typ = (types[i//4] >> (2*(i%4))) & 3
        if typ == 0:
            a, b, c, p = packing.unpack(data, p)
            line = f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}'.encode()
        elif typ == 1:
            line = data[p:p+48].hex().encode()
            p += 48
        elif typ == 2:
            n = int.from_bytes(data[p:p+42], 'big')
            p += 42
            chars = bytearray(64)
            for k in range(63, -1, -1):
                n, r = divmod(n, 36)
                chars[k] = BASE36[r]
            line = chars
        else:
            n = int.from_bytes(data[p:p+2], 'big')
            p += 2
            line = data[p:p+n]
            p += n
        result.extend(line)
        result.append(10)
    if p != len(data):
        raise ValueError('invalid trailing data')
    return bytes(result)

def main():
    if len(sys.argv) == 3:
        src, dst = sys.argv[1:]
        fn = encode
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        src, dst = sys.argv[2:]
        fn = decode
    else:
        raise SystemExit('usage: compress.py [--decompress] source destination')
    with open(src, 'rb') as f:
        data = f.read()
    with open(dst, 'wb') as f:
        f.write(fn(data))

if __name__ == '__main__':
    main()
