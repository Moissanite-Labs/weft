#!/usr/bin/env python3
"""Self-contained lossless compression using learned record structure.

The stream carries all dictionaries and numeric-field parameters. Arbitrary
non-record inputs use a standard-library general-purpose codec instead.
"""
import bz2
import collections
import json
import lzma
import sys
import zlib

class Encoder:
    def __init__(self):
        self.lo = 0
        self.hi = (1 << 32) - 1
        self.pending = 0
        self.bits = []
    def emit(self, bit):
        self.bits.append(bit)
        self.bits.extend([1 - bit] * self.pending)
        self.pending = 0
    def put(self, symbol, counts):
        total = sum(counts)
        lower = sum(counts[:symbol])
        width = self.hi - self.lo + 1
        self.hi = self.lo + width * (lower + counts[symbol]) // total - 1
        self.lo += width * lower // total
        while True:
            if self.hi < 0x80000000:
                self.emit(0)
            elif self.lo >= 0x80000000:
                self.emit(1)
                self.lo -= 0x80000000
                self.hi -= 0x80000000
            elif self.lo >= 0x40000000 and self.hi < 0xc0000000:
                self.pending += 1
                self.lo -= 0x40000000
                self.hi -= 0x40000000
            else:
                break
            self.lo *= 2
            self.hi = self.hi * 2 + 1
        counts[symbol] += 1
    def finish(self):
        self.pending += 1
        self.emit(int(self.lo >= 0x40000000))
        self.bits.extend([0] * (-len(self.bits) % 8))
        return bytes(sum(self.bits[i+j] << (7-j) for j in range(8)) for i in range(0,len(self.bits),8))

class Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.lo = 0
        self.hi = (1 << 32) - 1
        self.value = 0
        for _ in range(32):
            self.value = self.value * 2 + self.bit()
    def bit(self):
        i = self.pos
        self.pos += 1
        return (self.data[i//8] >> (7-i%8)) & 1 if i//8 < len(self.data) else 0
    def get(self, counts):
        total = sum(counts)
        width = self.hi - self.lo + 1
        target = ((self.value-self.lo+1)*total-1)//width
        lower = 0
        for symbol, count in enumerate(counts):
            if target < lower + count:
                break
            lower += count
        self.hi = self.lo + width * (lower+count)//total - 1
        self.lo += width*lower//total
        while True:
            if self.hi < 0x80000000:
                pass
            elif self.lo >= 0x80000000:
                self.lo -= 0x80000000
                self.hi -= 0x80000000
                self.value -= 0x80000000
            elif self.lo >= 0x40000000 and self.hi < 0xc0000000:
                self.lo -= 0x40000000
                self.hi -= 0x40000000
                self.value -= 0x40000000
            else:
                break
            self.lo *= 2
            self.hi = self.hi*2+1
            self.value = self.value*2+self.bit()
        counts[symbol] += 1
        return symbol

def structured(data):
    text = data.decode('utf8')
    lines = text.splitlines()
    if len(lines) < 32 or not text.endswith('\n'):
        raise ValueError('not records')
    parts = [line.split(' ',1) for line in lines]
    tails = [part[1].rsplit(' ',1) for part in parts]
    n = len(lines)
    start = int(parts[0][0])
    width = len(parts[0][0])
    nums = [int(t[1]) for t in tails]
    modulus = max(nums)+1
    step = (nums[1]-nums[0]) % modulus
    for i in range(n):
        if parts[i][0] != str(start+i).zfill(width) or tails[i][1] != str((nums[0]+i*step)%modulus):
            raise ValueError('irregular numeric fields')
    bodies = [t[0] for t in tails]
    # Learn the shortest high-coverage repeating template schedule.
    best = None
    for period in range(1,33):
        templates = [collections.Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        misses = sum(body != templates[i%period] for i,body in enumerate(bodies))
        cost = misses*20 + sum(len(t) for t in templates)
        if best is None or cost < best[0]:
            best = cost, templates
    templates = best[1]
    period = len(templates)
    flags = [int(body != templates[i%period]) for i,body in enumerate(bodies)]
    exceptions = [body.split(' ') for body,flag in zip(bodies,flags) if flag]
    words = sorted(set(word for row in exceptions for word in row))
    lengths = sorted(set(map(len,exceptions)))
    wordmap = {w:i for i,w in enumerate(words)}
    lenmap = {v:i for i,v in enumerate(lengths)}
    meta = [n,start,width,nums[0],step,modulus,templates,words,lengths]
    header = zlib.compress(json.dumps(meta,separators=(',',':'),ensure_ascii=False).encode(),9)
    coder = Encoder()
    counts = [1,1]
    for flag in flags:
        coder.put(flag,counts)
    counts = [1]*len(lengths)
    for row in exceptions:
        coder.put(lenmap[len(row)],counts)
    counts = [1]*len(words)
    for row in exceptions:
        for word in row:
            coder.put(wordmap[word],counts)
    return b'S' + len(header).to_bytes(4,'big') + header + coder.finish()

def compress(data):
    candidates = [b'B'+bz2.compress(data,9),b'L'+lzma.compress(data,preset=9),b'Z'+zlib.compress(data,9)]
    try:
        special = structured(data)
        if decompress(special) == data:
            candidates.append(special)
    except (ValueError,IndexError,UnicodeError,ZeroDivisionError):
        pass
    return min(candidates,key=len)

def decompress(data):
    kind = data[:1]
    if kind == b'B':
        return bz2.decompress(data[1:])
    if kind == b'L':
        return lzma.decompress(data[1:])
    if kind == b'Z':
        return zlib.decompress(data[1:])
    if kind != b'S':
        raise ValueError('unknown compression format')
    size = int.from_bytes(data[1:5],'big')
    n,start,width,initial,step,modulus,templates,words,lengths = json.loads(zlib.decompress(data[5:5+size]))
    coder = Decoder(data[5+size:])
    counts = [1,1]
    flags = [coder.get(counts) for _ in range(n)]
    counts = [1]*len(lengths)
    lens = [lengths[coder.get(counts)] for _ in range(sum(flags))]
    counts = [1]*len(words)
    exceptions = iter(' '.join(words[coder.get(counts)] for _ in range(length)) for length in lens)
    result = []
    for i,flag in enumerate(flags):
        body = next(exceptions) if flag else templates[i%len(templates)]
        result.append(f'{str(start+i).zfill(width)} {body} {(initial+i*step)%modulus}\n')
    return ''.join(result).encode('utf8')

def main():
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)

if __name__ == '__main__':
    main()
