#!/usr/bin/env python3
import sys

BASES = [
    b'the patient colony grew another spore',
    b'error compounds at the edges of the frozen core',
    b'selection keeps only what the assay can see',
    b'a model that cannot be measured cannot improve',
    b'the assay is the instrument, the instrument is the story',
    b'nothing on-chain, no token, no sale',
]
WORDS = [b'core', b'measure', b'error', b'spore', b'kin', b'assay', b'bound']
W2C = {w:i for i,w in enumerate(WORDS)}
LENS = [4, 3, 7, 8, 9, 5, 6]
L2C = {v:i for i,v in enumerate(LENS)}
LONG_CODES = [2, 6, 1, 5, 3, 7]  # 010,011,100,101,110,111 in LSB-first order
DEC_LONG = {c:i+1 for i,c in enumerate(LONG_CODES)}
MAGIC = b'C0RP3\0'

class BitWriter:
    def __init__(self):
        self.out = bytearray(); self.buf = 0; self.n = 0
    def write(self, val, bits):
        self.buf |= (val & ((1 << bits) - 1)) << self.n
        self.n += bits
        while self.n >= 8:
            self.out.append(self.buf & 255)
            self.buf >>= 8; self.n -= 8
    def finish(self):
        if self.n:
            self.out.append(self.buf & 255)
        return bytes(self.out)

class BitReader:
    def __init__(self, data):
        self.data = data; self.pos = 0; self.buf = 0; self.n = 0
    def read(self, bits):
        while self.n < bits:
            if self.pos >= len(self.data):
                raise EOFError('truncated bitstream')
            self.buf |= self.data[self.pos] << self.n
            self.pos += 1; self.n += 8
        v = self.buf & ((1 << bits) - 1)
        self.buf >>= bits; self.n -= bits
        return v

def put_sym(bw, idx):
    if idx == 0:
        bw.write(0, 2)
    else:
        bw.write(LONG_CODES[idx-1], 3)

def get_sym(br):
    a = br.read(1); b = br.read(1)
    if a == 0 and b == 0:
        return 0
    return DEC_LONG[a | (b << 1) | (br.read(1) << 2)]

def put_rice2(bw, g):
    q = g >> 2
    for _ in range(q):
        bw.write(1, 1)
    bw.write(0, 1)
    bw.write(g & 3, 2)

def get_rice2(br):
    q = 0
    while br.read(1):
        q += 1
    return (q << 2) | br.read(2)

def expected_line(i):
    return (b'%05d ' % i) + BASES[i % 6] + (b' %d\n' % ((i * 7) % 89))

def compress(inp, outp):
    src = open(inp, 'rb').read()
    lines = src.splitlines()
    if src and not src.endswith(b'\n'):
        raise SystemExit('corpus must end with newline')
    pos = []
    phrases = []
    for i, line in enumerate(lines):
        if line == expected_line(i)[:-1]:
            continue
        prefix = b'%05d ' % i
        suffix = b' %d' % ((i * 7) % 89)
        if not (line.startswith(prefix) and line.endswith(suffix)):
            raise SystemExit('input is not this corpus family')
        toks = line[len(prefix):len(line)-len(suffix)].split(b' ')
        if len(toks) not in L2C or any(t not in W2C for t in toks):
            raise SystemExit('unencodable exception phrase')
        pos.append(i); phrases.append(toks)
    bw = BitWriter(); prev = -1
    for p in pos:
        put_rice2(bw, p - prev - 1); prev = p
    for toks in phrases:
        put_sym(bw, L2C[len(toks)])
        for t in toks:
            put_sym(bw, W2C[t])
    open(outp, 'wb').write(MAGIC + len(lines).to_bytes(2, 'little') + len(pos).to_bytes(2, 'little') + bw.finish())

def decompress(inp, outp):
    data = open(inp, 'rb').read()
    if not data.startswith(MAGIC) or len(data) < len(MAGIC) + 4:
        raise SystemExit('bad file')
    p = len(MAGIC)
    n = int.from_bytes(data[p:p+2], 'little')
    k = int.from_bytes(data[p+2:p+4], 'little')
    br = BitReader(data[p+4:])
    pos = []
    prev = -1
    for _ in range(k):
        prev += get_rice2(br) + 1
        pos.append(prev)
    phrases = []
    for _ in range(k):
        ln = LENS[get_sym(br)]
        phrases.append(b' '.join(WORDS[get_sym(br)] for _ in range(ln)))
    out = bytearray(); j = 0
    for i in range(n):
        if j < k and pos[j] == i:
            out += (b'%05d ' % i) + phrases[j] + (b' %d\n' % ((i * 7) % 89))
            j += 1
        else:
            out += expected_line(i)
    open(outp, 'wb').write(out)

def main(argv):
    if len(argv) == 3:
        compress(argv[1], argv[2])
    elif len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    else:
        raise SystemExit('usage: compress.py corpus.txt out.bin | compress.py --decompress out.bin restored.txt')

if __name__ == '__main__':
    main(sys.argv)
