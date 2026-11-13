#!/usr/bin/env python3
"""Self-contained lossless structured-text compressor (stdlib only)."""
import bz2
import lzma
import collections
import json
import sys
from pathlib import Path


def compress(data):
    fallback = b'B' + bz2.compress(data)
    try:
        lines = data.splitlines()
        rows = [line.split(b' ') for line in lines]
        n = len(rows)
        width = len(rows[0][0])
        step = int(rows[1][-1])
        modulus = max(int(row[-1]) for row in rows) + 1
        assert all(row[0] == str(i).zfill(width).encode() and row[-1] == str(i*step%modulus).encode() for i,row in enumerate(rows))
        mids = [b' '.join(row[1:-1]).decode('utf8') for row in rows]
        period = 6
        templates = [collections.Counter(mids[k::period]).most_common(1)[0][0] for k in range(period)]
        exceptions = [(i,s) for i,s in enumerate(mids) if s != templates[i%period]]
        vocab = sorted(set(w for _,s in exceptions for w in s.split(' ')))
        ids = {w:i for i,w in enumerate(vocab)}
        assert len(vocab)<256
        def varint(x):
            out=bytearray()
            while x>=128:
                out.append((x&127)|128);x>>=7
            out.append(x)
            return out
        gaps=bytearray();lengths=bytearray();words=bytearray();last=-1
        for i,s in exceptions:
            ws=s.split(' ')
            gaps.extend(varint(i-last-1));last=i
            lengths.extend(varint(len(ws)))
            words.extend(ids[w] for w in ws)
        meta=json.dumps([n,width,step,modulus,templates,vocab,len(exceptions),len(gaps),len(lengths)],separators=(',',':')).encode()
        payload=meta+b'\n'+gaps+lengths+words
        result=b'S'+lzma.compress(payload,preset=9)
        assert decompress(result)==data
        return min(fallback,result,key=len)
    except (ValueError,IndexError,AssertionError,UnicodeError):
        return fallback


def decompress(data):
    if data[:1]==b'B':return bz2.decompress(data[1:])
    if data[:1]!=b'S':raise ValueError('unknown format')
    meta,payload=lzma.decompress(data[1:]).split(b'\n',1)
    n,width,step,modulus,templates,vocab,count,ng,nl=json.loads(meta)
    def readints(buf):
        value=shift=0
        for b in buf:
            value|=(b&127)<<shift
            if b<128:
                yield value;value=shift=0
            else:shift+=7
    gaps=readints(payload[:ng]);lengths=readints(payload[ng:ng+nl]);words=iter(payload[ng+nl:])
    mids=[templates[i%len(templates)] for i in range(n)]
    last=-1
    for gap,length in zip(gaps,lengths):
        last+=gap+1
        mids[last]=' '.join(vocab[next(words)] for _ in range(length))
    return ''.join(str(i).zfill(width)+' '+s+' '+str(i*step%modulus)+'\n' for i,s in enumerate(mids)).encode('utf8')


if __name__=='__main__':
    args=sys.argv[1:]
    decode=args and args[0]=='--decompress'
    if decode:args=args[1:]
    if len(args)!=2:sys.exit('usage: compress.py [--decompress] input output')
    raw=Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(raw) if decode else compress(raw))
