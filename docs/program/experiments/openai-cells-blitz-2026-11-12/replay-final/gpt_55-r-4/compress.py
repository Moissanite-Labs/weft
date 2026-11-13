#!/usr/bin/env python3
import sys, struct, bz2

TEMPLATES = [
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
]
VOCAB = [b'assay', b'bound', b'core', b'error', b'kin', b'measure', b'spore']
VMAP = {w:i for i,w in enumerate(VOCAB)}
MAGIC = b'CSTM1\0'
FALL = b'BZ2__\0'

class BitWriter:
    def __init__(self):
        self.buf = bytearray(); self.acc = 0; self.n = 0
    def write(self, val, bits):
        self.acc |= val << self.n; self.n += bits
        while self.n >= 8:
            self.buf.append(self.acc & 255); self.acc >>= 8; self.n -= 8
    def finish(self):
        if self.n: self.buf.append(self.acc & 255)
        return bytes(self.buf)

class BitReader:
    def __init__(self, data):
        self.data = data; self.p = 0; self.acc = 0; self.n = 0
    def read(self, bits):
        while self.n < bits:
            if self.p >= len(self.data): raise EOFError
            self.acc |= self.data[self.p] << self.n; self.p += 1; self.n += 8
        v = self.acc & ((1 << bits) - 1)
        self.acc >>= bits; self.n -= bits
        return v

def try_custom(data):
    if not data.endswith(b'\n'):
        return None
    lines = data[:-1].split(b'\n') if data else []
    n = len(lines)
    mids = []
    for i, line in enumerate(lines):
        pref = (b'%05d ' % i)
        suf = (b' %d' % ((i * 7) % 89))
        if not (line.startswith(pref) and line.endswith(suf)):
            return None
        mid = line[len(pref):len(line)-len(suf)]
        if mid == TEMPLATES[i % 6]:
            mids.append(None)
        else:
            words = mid.split(b' ')
            if not (3 <= len(words) <= 9):
                return None
            codes = []
            for w in words:
                c = VMAP.get(w)
                if c is None: return None
                codes.append(c)
            mids.append(codes)
    bw = BitWriter()
    for codes in mids:
        if codes is None:
            bw.write(0, 1)
        else:
            bw.write(1, 1)
            bw.write(len(codes) - 3, 3)
            for c in codes: bw.write(c, 3)
    payload = bw.finish()
    return MAGIC + struct.pack('<I', n) + payload

def compress(inp, outp):
    data = open(inp, 'rb').read()
    enc = try_custom(data)
    if enc is None:
        enc = FALL + bz2.compress(data, compresslevel=9)
    open(outp, 'wb').write(enc)

def decompress(inp, outp):
    data = open(inp, 'rb').read()
    if data.startswith(FALL):
        raw = bz2.decompress(data[len(FALL):])
    elif data.startswith(MAGIC):
        if len(data) < len(MAGIC) + 4: raise SystemExit('truncated')
        n = struct.unpack('<I', data[len(MAGIC):len(MAGIC)+4])[0]
        br = BitReader(data[len(MAGIC)+4:])
        out = bytearray()
        for i in range(n):
            out += b'%05d ' % i
            if br.read(1) == 0:
                out += TEMPLATES[i % 6]
            else:
                ln = br.read(3) + 3
                words = [VOCAB[br.read(3)] for _ in range(ln)]
                out += b' '.join(words)
            out += b' %d\n' % ((i * 7) % 89)
        raw = bytes(out)
    else:
        raise SystemExit('bad format')
    open(outp, 'wb').write(raw)

def main(argv):
    if len(argv) == 3:
        compress(argv[1], argv[2])
    elif len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    else:
        raise SystemExit('usage: compress.py [--decompress] in out')
if __name__ == '__main__': main(sys.argv)
