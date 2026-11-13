#!/usr/bin/env python3
"""Lossless compact encoding of the three record formats in corpus_hard.txt."""
import sys
import re
import zlib
import bz2
import lzma
from pathlib import Path

META = re.compile(rb'e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)')
ALPH = b'0123456789abcdefghijklmnopqrstuvwxyz'

def pack(data):
    lines = data.split(b'\n')
    if lines[-1] != b'':
        raise ValueError('expected final newline')
    lines.pop()
    if len(lines) > 65535:
        raise ValueError('too many records')
    types = bytearray((len(lines) + 3)//4)
    payload = bytearray()
    for i, line in enumerate(lines):
        match = META.fullmatch(line)
        if match:
            kind = 0
            a, b, c = (int(v) for v in match.groups())
            payload.extend(((a<<50)|(b<<30)|c).to_bytes(9,'big'))
        elif len(line) == 96 and re.fullmatch(rb'[0-9a-f]{96}', line):
            kind = 1
            payload.extend(bytes.fromhex(line.decode('ascii')))
        elif len(line) == 64 and re.fullmatch(rb'[0-9a-z]{64}', line):
            kind = 2
            value = 0
            for digit in line:
                value = value * 36 + ALPH.index(digit)
            payload.extend(value.to_bytes(42, 'big'))
        else:
            raise ValueError('unknown record: ' + repr(line[:100]))
        types[i//4] |= kind << (2*(i%4))
    raw = len(lines).to_bytes(2,'big') + types + payload
    options = [zlib.compress(raw,9), bz2.compress(raw,9), lzma.compress(raw,preset=9)]
    idx = min(range(3),key=lambda k:len(options[k]))
    return b'CH1' + bytes([idx]) + options[idx]

def unpack(blob):
    if blob[:3] != b'CH1':
        raise ValueError('invalid header')
    decompressors = (zlib.decompress, bz2.decompress, lzma.decompress)
    raw = decompressors[blob[3]](blob[4:])
    count = int.from_bytes(raw[:2],'big')
    types = raw[2:2+(count+3)//4]
    pos = 2+len(types)
    lines = []
    for i in range(count):
        kind = (types[i//4] >> (2*(i%4))) & 3
        if kind == 0:
            a = int.from_bytes(raw[pos:pos+9],'big') >> 50
            b = (int.from_bytes(raw[pos:pos+9],'big') >> 30) & ((1<<20)-1)
            c = int.from_bytes(raw[pos:pos+9],'big') & ((1<<30)-1)
            pos += 9
            line = b'e18a line %d ratio 0.%06d select pick win seed %d' % (a,b,c)
        elif kind == 1:
            line = raw[pos:pos+48].hex().encode('ascii')
            pos += 48
        elif kind == 2:
            value = int.from_bytes(raw[pos:pos+42], 'big')
            pos += 42
            digits = bytearray(64)
            for j in range(63,-1,-1):
                value, digit = divmod(value,36)
                digits[j] = ALPH[digit]
            line = bytes(digits)
        else:
            raise ValueError('bad record type')
        lines.append(line)
    if pos != len(raw):
        raise ValueError('unexpected trailing bytes')
    return b'\n'.join(lines) + b'\n'

def main():
    args = sys.argv[1:]
    if len(args) == 2:
        src, dst = args
        data = pack(Path(src).read_bytes())
    elif len(args) == 3 and args[0] == '--decompress':
        _, src, dst = args
        data = unpack(Path(src).read_bytes())
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(dst).write_bytes(data)

if __name__ == '__main__':
    main()
