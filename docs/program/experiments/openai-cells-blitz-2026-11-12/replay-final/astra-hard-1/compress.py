#!/usr/bin/env python3
"""Lossless typed-text compression with a general-purpose fallback."""
import bz2
import re
import struct
import sys
import zlib
from pathlib import Path

PAT = re.compile(rb'e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)')
RADIX = 10**21

def pack(values, radix):
    n = 0
    for v in values:
        n = n * radix + v
    return n.to_bytes((n.bit_length()+7)//8, 'big')

def unpack(data, radix, count):
    n = int.from_bytes(data, 'big')
    result = [0]*count
    for i in range(count-1, -1, -1):
        n, result[i] = divmod(n, radix)
    if n:
        raise ValueError('Invalid packed integer')
    return result

def compress(data):
    fallback = b'CH1' + bz2.compress(data)
    tags = bytearray()
    groups = [[], [], []]
    for line in data.splitlines():
        m = PAT.fullmatch(line)
        if m:
            a,b,c = map(int, m.groups())
            if a >= 10**6 or c >= 10**9:
                return fallback
            t,v = 0, (a*10**6+b)*10**9+c
        elif re.fullmatch(rb'[0-9a-f]{96}', line):
            t,v = 1,int(line,16)
        elif re.fullmatch(rb'[0-9a-z]{64}', line):
            t,v = 2,int(line,36)
        else:
            return fallback
        tags.append(t)
        groups[t].append(v)
    parts = [zlib.compress(tags,9), pack(groups[0], RADIX), pack(groups[1], 16**96), pack(groups[2], 36**64)]
    out = b'CH2' + struct.pack('>5I',len(tags),*(len(p) for p in parts)) + b''.join(parts)
    if len(out) < len(fallback) and decompress(out) == data:
        return out
    return fallback

def decompress(data):
    if data[:3] == b'CH1':
        return bz2.decompress(data[3:])
    if data[:3] != b'CH2':
        raise ValueError('Unknown format')
    count,*sizes = struct.unpack('>5I',data[3:23])
    parts=[]
    pos=23
    for size in sizes:
        parts.append(data[pos:pos+size]);pos+=size
    tags=zlib.decompress(parts[0])
    if len(tags)!=count:
        raise ValueError('Invalid tags')
    groups=[iter(unpack(parts[i+1],radix,tags.count(i))) for i,radix in enumerate((RADIX,16**96,36**64))]
    lines=[]
    for t in tags:
        v=next(groups[t])
        if t==0:
            v,c=divmod(v,10**9);a,b=divmod(v,10**6)
            line=f'e18a line {a} ratio 0.{b:06d} select pick win seed {c}'
        elif t==1:
            line=f'{v:096x}'
        else:
            chars=[]
            for _ in range(64):
                v,r=divmod(v,36);chars.append('0123456789abcdefghijklmnopqrstuvwxyz'[r])
            line=''.join(reversed(chars))
        lines.append(line.encode()+b'\n')
    return b''.join(lines)

def main():
    args=sys.argv[1:]
    decode=bool(args and args[0]=='--decompress')
    if decode:args.pop(0)
    if len(args)!=2:raise SystemExit('Usage: compress.py [--decompress] INPUT OUTPUT')
    data=Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))

if __name__=='__main__':main()
