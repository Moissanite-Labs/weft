"""Static arithmetic coder for the structured record stream."""
from bisect import bisect_right
from collections import Counter

HALF = 1 << 31
QUARTER = 1 << 30
MASK = (1 << 32) - 1

class Encoder:
    def __init__(self):
        self.low, self.high, self.pending = 0, MASK, 0
        self.out, self.byte, self.nbits = bytearray(), 0, 0
    def bit(self, bit):
        self.byte = (self.byte << 1) | bit
        self.nbits += 1
        if self.nbits == 8:
            self.out.append(self.byte)
            self.byte = self.nbits = 0
    def emit(self, b):
        self.bit(b)
        for _ in range(self.pending):
            self.bit(1-b)
        self.pending = 0
    def put(self, sym, cum):
        low, high = self.low, self.high
        span = high - low + 1
        high = low + span * cum[sym + 1] // cum[-1] - 1
        low = low + span * cum[sym] // cum[-1]
        while True:
            if high < HALF:
                self.emit(0)
            elif low >= HALF:
                self.emit(1)
                low -= HALF; high -= HALF
            elif low >= QUARTER and high < 3*QUARTER:
                self.pending += 1
                low -= QUARTER; high -= QUARTER
            else:
                break
            low *= 2; high = high * 2 + 1
        self.low, self.high = low, high
    def finish(self):
        self.pending += 1
        self.emit(int(self.low >= QUARTER))
        if self.nbits:
            self.out.append(self.byte << (8-self.nbits))
        return bytes(self.out)

class Decoder:
    def __init__(self, data):
        self.data, self.pos = data, 0
        self.low, self.high, self.value = 0, MASK, 0
        for _ in range(32):
            self.value = (self.value << 1) | self.bit()
    def bit(self):
        p = self.pos
        self.pos += 1
        return (self.data[p//8] >> (7-p%8)) & 1 if p//8 < len(self.data) else 0
    def get(self, cum):
        low, high = self.low, self.high
        span = high - low + 1
        target = ((self.value-low+1)*cum[-1]-1)//span
        sym = bisect_right(cum, target)-1
        high = low + span*cum[sym+1]//cum[-1]-1
        low += span*cum[sym]//cum[-1]
        while True:
            if high < HALF:
                pass
            elif low >= HALF:
                low -= HALF; high -= HALF; self.value -= HALF
            elif low >= QUARTER and high < 3*QUARTER:
                low -= QUARTER; high -= QUARTER; self.value -= QUARTER
            else:
                break
            low *= 2; high = high*2+1
            self.value = self.value*2 + self.bit()
        self.low, self.high = low, high
        return sym

def cumulative(counts):
    c = [0]
    for n in counts:
        c.append(c[-1] + n)
    return c

def pack(stream, count, ndict):
    records = []
    p = 0
    for i in range(count):
        flag = stream[p]; p += 1
        if flag:
            e = stream.index(0, p)
            records.append(stream[p:e])
            p = e+1
        else:
            records.append(None)
    lengths = sorted({len(r) for r in records if r is not None})
    length_ids = {v:i for i,v in enumerate(lengths)}
    flag_counts = [sum(r is None for r in records), sum(r is not None for r in records)]
    length_counts = [sum(r is not None and len(r) == n for r in records) for n in lengths]
    word_counts = [0]*ndict
    for r in records:
        if r is not None:
            for w in r: word_counts[w-1] += 1
    # Dictionary entries are derived from the records, so all word counts are positive.
    models = list(map(cumulative, [flag_counts, length_counts, word_counts]))
    enc = Encoder()
    for r in records:
        enc.put(int(r is not None), models[0])
        if r is not None:
            enc.put(length_ids[len(r)], models[1])
            for w in r: enc.put(w-1, models[2])
    return [lengths, flag_counts, length_counts, word_counts], enc.finish()

def unpack(meta, data, count):
    lengths, fc, lc, wc = meta
    models = list(map(cumulative, [fc, lc, wc]))
    dec = Decoder(data)
    out = bytearray()
    for _ in range(count):
        flag = dec.get(models[0])
        out.append(flag)
        if flag:
            length = lengths[dec.get(models[1])]
            for _ in range(length): out.append(dec.get(models[2])+1)
            out.append(0)
    return out
