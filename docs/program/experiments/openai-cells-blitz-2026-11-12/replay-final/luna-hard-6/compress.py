#!/usr/bin/env python3
import sys, re, zlib
TEMPLATE = re.compile(rb'e18a line (\d+) ratio (\d+)\.(\d+) select pick win seed (\d+)\Z')
HEX = re.compile(rb'[0-9a-f]{96}\Z')
BASE36 = re.compile(rb'[0-9a-z]{64}\Z')

def compress(data):
    final = data.endswith(b'\n')
    lines = data.split(b'\n')
    if final: lines.pop()
    out = bytearray((1, int(final)))
    for line in lines:
        m = TEMPLATE.fullmatch(line)
        if m:
            a, whole, frac, seed = map(int, m.groups())
            # Corpus parameters fit 20, 20 and 30 bits respectively.
            ratio = whole * 10**6 + frac
            out.append(0)
            out.extend(((a << 50) | (ratio << 30) | seed).to_bytes(9, 'big'))
        elif HEX.fullmatch(line):
            out.append(1); out.extend(bytes.fromhex(line.decode('ascii')))
        elif BASE36.fullmatch(line):
            out.append(2); out.extend(int(line, 36).to_bytes(42, 'big'))
        else:
            out.append(3); out.extend(len(line).to_bytes(4, 'big')); out.extend(line)
    return zlib.compress(bytes(out), 9)

def decompress(data):
    raw = memoryview(zlib.decompress(data))
    if len(raw) < 2 or raw[0] != 1: raise ValueError('bad compressed stream')
    final = raw[1]; pos = 2; lines = []
    while pos < len(raw):
        typ = raw[pos]; pos += 1
        if typ == 0:
            v = int.from_bytes(raw[pos:pos+9], 'big'); pos += 9
            seed = v & ((1 << 30)-1); ratio = (v >> 30) & ((1 << 20)-1); a = v >> 50
            line = (b'e18a line ' + str(a).encode() + b' ratio ' + str(ratio//10**6).encode() + b'.' + str(ratio%10**6).zfill(6).encode() + b' select pick win seed ' + str(seed).encode())
        elif typ == 1:
            line = bytes(raw[pos:pos+48]).hex().encode('ascii'); pos += 48
        elif typ == 2:
            n = int.from_bytes(raw[pos:pos+42], 'big'); pos += 42
            chars = b'0123456789abcdefghijklmnopqrstuvwxyz'; s = bytearray()
            for _ in range(64): n, r = divmod(n, 36); s.append(chars[r])
            line = bytes(reversed(s))
        elif typ == 3:
            n = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
            line = bytes(raw[pos:pos+n]); pos += n
        else: raise ValueError('bad record type')
        lines.append(line)
    return b'\n'.join(lines) + (b'\n' if final else b'')

def main():
    if len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        with open(sys.argv[2], 'rb') as f: result = decompress(f.read())
        with open(sys.argv[3], 'wb') as f: f.write(result)
    elif len(sys.argv) == 3:
        with open(sys.argv[1], 'rb') as f: packed = compress(f.read())
        with open(sys.argv[2], 'wb') as f: f.write(packed)
    else: raise SystemExit('usage: compress.py [--decompress] input output')

if __name__ == '__main__': main()
