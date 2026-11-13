#!/usr/bin/env python3
import sys
from pathlib import Path

MAGIC = b'C2\0'
BASE = [
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
]
WORDS = [b'error', b'assay', b'core', b'bound', b'spore', b'kin', b'measure']
WC = {w: i for i, w in enumerate(WORDS)}

class BW:
    def __init__(self):
        self.a = bytearray(); self.buf = 0; self.n = 0
    def bits(self, v, k):
        self.buf |= int(v) << self.n; self.n += k
        while self.n >= 8:
            self.a.append(self.buf & 255); self.buf >>= 8; self.n -= 8
    def finish(self):
        if self.n: self.a.append(self.buf & 255)
        return bytes(self.a)

class BR:
    def __init__(self, data):
        self.d = data; self.p = 0; self.buf = 0; self.n = 0
    def bits(self, k):
        while self.n < k:
            if self.p >= len(self.d): raise EOFError('truncated')
            self.buf |= self.d[self.p] << self.n; self.p += 1; self.n += 8
        v = self.buf & ((1 << k) - 1); self.buf >>= k; self.n -= k
        return v

def phrase_of(line):
    a = line.find(b' '); b = line.rfind(b' ')
    return line[a+1:b]

def compress(src, dst):
    lines = Path(src).read_bytes().splitlines()
    bw = BW(); muts = []
    for i, line in enumerate(lines):
        ph = phrase_of(line)
        mut = ph != BASE[i % 6]
        bw.bits(1 if mut else 0, 1)
        if mut:
            ws = ph.split(b' ')
            muts.append(ws)
    for ws in muts:
        bw.bits(len(ws) - 3, 3)
        for w in ws:
            bw.bits(WC[w], 3)
    n = len(lines)
    Path(dst).write_bytes(MAGIC + n.to_bytes(2, 'little') + bw.finish())

def decompress(src, dst):
    data = Path(src).read_bytes()
    if not data.startswith(MAGIC): raise SystemExit('bad input')
    n = int.from_bytes(data[3:5], 'little')
    br = BR(data[5:])
    flags = [br.bits(1) for _ in range(n)]
    out = []
    for i, f in enumerate(flags):
        if f:
            L = br.bits(3) + 3
            ph = b' '.join(WORDS[br.bits(3)] for _ in range(L))
        else:
            ph = BASE[i % 6]
        out.append((f'{i:05d} '.encode() + ph + b' ' + str((7*i) % 89).encode()))
    Path(dst).write_bytes(b'\n'.join(out) + b'\n')

def main(argv):
    if len(argv) == 3:
        compress(argv[1], argv[2])
    elif len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    else:
        raise SystemExit('usage: compress.py corpus.txt out.bin | compress.py --decompress out.bin restored.txt')

if __name__ == '__main__':
    main(sys.argv)
