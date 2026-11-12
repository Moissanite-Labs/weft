#!/usr/bin/env python3
import sys, zlib, struct

FIXED = [
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
]
WORDS = [b'assay', b'bound', b'core', b'error', b'kin', b'measure', b'spore']
WID = {w:i for i,w in enumerate(WORDS)}
MAGIC = b'C6a1'
FALL = b'Z6a1'

class BW:
    def __init__(self):
        self.a = bytearray(); self.buf = 0; self.n = 0
    def bits(self, v, k):
        self.buf = (self.buf << k) | v; self.n += k
        while self.n >= 8:
            self.n -= 8; self.a.append((self.buf >> self.n) & 255)
            self.buf &= (1 << self.n) - 1
    def finish(self):
        if self.n:
            self.a.append((self.buf << (8-self.n)) & 255)
        return bytes(self.a)

class BR:
    def __init__(self, data):
        self.d=data; self.p=0; self.buf=0; self.n=0
    def bits(self,k):
        while self.n < k:
            if self.p >= len(self.d): raise EOFError
            self.buf = (self.buf << 8) | self.d[self.p]; self.p += 1; self.n += 8
        self.n -= k
        v = (self.buf >> self.n) & ((1<<k)-1)
        self.buf &= (1 << self.n) - 1
        return v

def try_custom(data):
    lines = data.splitlines()
    # splitlines() loses a final blank line detail; this corpus has exactly one newline per line.
    if not data.endswith(b'\n') or len(lines) > 65535:
        return None
    bw = BW()
    try:
        for i, line in enumerate(lines):
            first, rest = line.split(b' ', 1)
            if first != (b'%05d' % i): return None
            text, tail = rest.rsplit(b' ', 1)
            if tail != str((7*i) % 89).encode(): return None
            if text == FIXED[i % 6]:
                bw.bits(0, 1)
            else:
                ws = text.split(b' ')
                if not (3 <= len(ws) <= 9): return None
                bw.bits(1, 1); bw.bits(len(ws)-3, 3)
                for w in ws:
                    j = WID.get(w)
                    if j is None: return None
                    bw.bits(j, 3)
    except ValueError:
        return None
    return MAGIC + struct.pack('>H', len(lines)) + bw.finish()

def compress(inp, outp):
    data = open(inp,'rb').read()
    enc = try_custom(data)
    if enc is None:
        enc = FALL + zlib.compress(data, 9)
    open(outp,'wb').write(enc)

def decompress(inp, outp):
    data = open(inp,'rb').read()
    if data.startswith(FALL):
        raw = zlib.decompress(data[4:])
    elif data.startswith(MAGIC):
        n = struct.unpack('>H', data[4:6])[0]
        br = BR(data[6:])
        out = bytearray()
        for i in range(n):
            if br.bits(1) == 0:
                text = FIXED[i % 6]
            else:
                L = br.bits(3) + 3
                text = b' '.join(WORDS[br.bits(3)] for _ in range(L))
            out += b'%05d ' % i
            out += text
            out += b' '
            out += str((7*i) % 89).encode()
            out += b'\n'
        raw = bytes(out)
    else:
        raise SystemExit('bad format')
    open(outp,'wb').write(raw)

def main(argv):
    if len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    elif len(argv) == 3:
        compress(argv[1], argv[2])
    else:
        raise SystemExit('usage: compress.py [--decompress] in out')
if __name__ == '__main__': main(sys.argv)
