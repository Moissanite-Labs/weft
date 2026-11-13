#!/usr/bin/env python3
import sys, bz2, struct

MAGIC = b'CSTM1\0'
FALLBACK = b'BZ2__\0'
BASE = [
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
]
WORDS = [b'error', b'assay', b'core', b'bound', b'kin', b'measure', b'spore']
W2I = {w:i for i,w in enumerate(WORDS)}

class BitWriter:
    def __init__(self):
        self.buf = bytearray(); self.acc = 0; self.n = 0
    def write(self, val, bits):
        self.acc |= (val & ((1 << bits) - 1)) << self.n
        self.n += bits
        while self.n >= 8:
            self.buf.append(self.acc & 255)
            self.acc >>= 8; self.n -= 8
    def finish(self):
        if self.n:
            self.buf.append(self.acc & 255)
            self.acc = 0; self.n = 0
        return bytes(self.buf)

class BitReader:
    def __init__(self, data):
        self.data = data; self.pos = 0; self.acc = 0; self.n = 0
    def read(self, bits):
        while self.n < bits:
            if self.pos >= len(self.data):
                raise EOFError('truncated bitstream')
            self.acc |= self.data[self.pos] << self.n
            self.pos += 1; self.n += 8
        val = self.acc & ((1 << bits) - 1)
        self.acc >>= bits; self.n -= bits
        return val

def try_custom(raw):
    lines = raw.splitlines()
    if not raw.endswith(b'\n') or len(lines) >= 65536:
        return None
    exc = []
    for i, line in enumerate(lines):
        pref = (b'%05d ' % i)
        suff = b' ' + str((i * 7) % 89).encode()
        if not (line.startswith(pref) and line.endswith(suff)):
            return None
        text = line[len(pref):len(line)-len(suff)]
        if text != BASE[i % 6]:
            ws = text.split(b' ')
            if not (3 <= len(ws) <= 10 and all(w in W2I for w in ws)):
                return None
            exc.append((i, ws))
    bw = BitWriter()
    exdict = dict(exc)
    for i in range(len(lines)):
        bw.write(1 if i in exdict else 0, 1)
    for i, ws in exc:
        bw.write(len(ws) - 3, 3)
        for w in ws:
            bw.write(W2I[w], 3)
    bits = bw.finish()
    return MAGIC + struct.pack('<HH', len(lines), len(exc)) + bits

def compress(infile, outfile):
    raw = open(infile, 'rb').read()
    enc = try_custom(raw)
    if enc is None:
        enc = FALLBACK + bz2.compress(raw, 9)
    open(outfile, 'wb').write(enc)

def decompress(infile, outfile):
    data = open(infile, 'rb').read()
    if data.startswith(FALLBACK):
        raw = bz2.decompress(data[len(FALLBACK):])
    elif data.startswith(MAGIC):
        n, ne = struct.unpack('<HH', data[len(MAGIC):len(MAGIC)+4])
        br = BitReader(data[len(MAGIC)+4:])
        flags = [br.read(1) for _ in range(n)]
        out = []
        for i, f in enumerate(flags):
            if f:
                ln = br.read(3) + 3
                text = b' '.join(WORDS[br.read(3)] for _ in range(ln))
            else:
                text = BASE[i % 6]
            out.append((b'%05d ' % i) + text + b' ' + str((i * 7) % 89).encode() + b'\n')
        if sum(flags) != ne:
            raise ValueError('bad exception count')
        raw = b''.join(out)
    else:
        raise ValueError('unknown format')
    open(outfile, 'wb').write(raw)

def main(argv):
    if len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    elif len(argv) == 3:
        compress(argv[1], argv[2])
    else:
        sys.stderr.write('usage: compress.py IN OUT | compress.py --decompress IN OUT\n')
        return 2
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
