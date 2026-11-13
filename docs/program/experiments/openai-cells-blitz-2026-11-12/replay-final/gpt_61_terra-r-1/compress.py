#!/usr/bin/env python3
"""Lossless compressor with a model for regularly numbered text records.

Unmodelled input uses XZ. The structured format stores its learned model in the
file; decompression does not depend on the original corpus.
"""
import collections
import json
import lzma
import re
import struct
import sys
import zlib

TOP = (1 << 32) - 1
HALF = 1 << 31
QUARTER = 1 << 30
THREE_QUARTERS = 3 << 30


class Encoder:
    def __init__(self):
        self.low = 0
        self.high = TOP
        self.pending = 0
        self.bits = []

    def bit(self, b):
        self.bits.append(b)
        self.bits.extend([1 - b] * self.pending)
        self.pending = 0

    def put(self, start, end, total):
        span = self.high - self.low + 1
        self.high = self.low + span * end // total - 1
        self.low += span * start // total
        while True:
            if self.high < HALF:
                self.bit(0)
            elif self.low >= HALF:
                self.bit(1)
                self.low -= HALF
                self.high -= HALF
            elif self.low >= QUARTER and self.high < THREE_QUARTERS:
                self.pending += 1
                self.low -= QUARTER
                self.high -= QUARTER
            else:
                break
            self.low = (self.low << 1) & TOP
            self.high = ((self.high << 1) | 1) & TOP

    def finish(self):
        self.pending += 1
        self.bit(0 if self.low < QUARTER else 1)
        result = bytearray((len(self.bits) + 7) // 8)
        for i, b in enumerate(self.bits):
            result[i // 8] |= b << (7 - i % 8)
        return bytes(result)


class Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.low = 0
        self.high = TOP
        self.code = 0
        for _ in range(32):
            self.code = (self.code << 1) | self.bit()

    def bit(self):
        p = self.pos
        self.pos += 1
        return (self.data[p // 8] >> (7 - p % 8)) & 1 if p // 8 < len(self.data) else 0

    def get(self, total):
        return ((self.code - self.low + 1) * total - 1) // (self.high - self.low + 1)

    def take(self, start, end, total):
        span = self.high - self.low + 1
        self.high = self.low + span * end // total - 1
        self.low += span * start // total
        while True:
            if self.high < HALF:
                pass
            elif self.low >= HALF:
                self.low -= HALF
                self.high -= HALF
                self.code -= HALF
            elif self.low >= QUARTER and self.high < THREE_QUARTERS:
                self.low -= QUARTER
                self.high -= QUARTER
                self.code -= QUARTER
            else:
                break
            self.low = (self.low << 1) & TOP
            self.high = ((self.high << 1) | 1) & TOP
            self.code = ((self.code << 1) & TOP) | self.bit()


def model(data):
    # Restrict the model to a simple, self-describing record grammar.
    if not data.endswith(b'\n') or len(data) > 10000000:
        return None
    lines = data.splitlines(keepends=True)
    if len(lines) < 20 or len(lines) > 1000000:
        return None
    records = []
    for i, line in enumerate(lines):
        m = re.fullmatch(rb'(\d+) (.*) (\d+)\n', line)
        if not m or int(m[1]) != i or str(int(m[3])).encode() != m[3]:
            return None
        if i == 0:
            width = len(m[1])
        if m[1] != str(i).zfill(width).encode():
            return None
        records.append((m[2], int(m[3])))
    vals = [x[1] for x in records]
    step = vals[1] - vals[0]
    if step <= 0:
        return None
    modulus = next((vals[i-1] + step - vals[i] for i in range(2, len(vals)) if vals[i] != vals[i-1] + step), 0)
    if modulus <= max(vals) or any(v != (vals[0] + step * i) % modulus for i, v in enumerate(vals)):
        return None
    texts = [x[0] for x in records]
    best = None
    for period in range(1, 17):
        bases = [collections.Counter(texts[i::period]).most_common(1)[0][0] for i in range(period)]
        exceptions = [t for i, t in enumerate(texts) if t != bases[i % period]]
        cost = len(exceptions) * 10 + sum(map(len, bases))
        if best is None or cost < best[0]:
            best = (cost, bases, exceptions)
    _, bases, exceptions = best
    words = sorted(set(w for t in exceptions for w in t.split(b' ')))
    if not words or len(words) > 256 or any(not w for w in words):
        return None
    lengths = [len(t.split(b' ')) for t in exceptions]
    lo, hi = min(lengths), max(lengths)
    if hi > 255:
        return None
    try:
        meta = [len(lines), width, vals[0], step, modulus,
                [x.decode('latin1') for x in bases], [x.decode('latin1') for x in words],
                len(exceptions), lo, hi]
        header = zlib.compress(json.dumps(meta, separators=(',', ':'), ensure_ascii=True).encode(), 9)
        indexes = {w: i for i, w in enumerate(words)}
        enc = Encoder()
        remaining = len(exceptions)
        for i, text in enumerate(texts):
            total = len(texts) - i
            exc = text != bases[i % len(bases)]
            if exc:
                enc.put(total - remaining, total, total)
                remaining -= 1
                ws = text.split(b' ')
                enc.put(len(ws) - lo, len(ws) - lo + 1, hi - lo + 1)
                for w in ws:
                    k = indexes[w]
                    enc.put(k, k + 1, len(words))
            else:
                enc.put(0, total - remaining, total)
        return b'STR1' + struct.pack('>I', len(header)) + header + enc.finish()
    except (ValueError, OverflowError):
        return None


def compress(data):
    plain = b'XZ00' + lzma.compress(data, preset=9)
    structured = model(data)
    return structured if structured is not None and len(structured) < len(plain) else plain


def decompress(data):
    if data[:4] == b'XZ00':
        return lzma.decompress(data[4:])
    if data[:4] != b'STR1':
        raise ValueError('unrecognized format')
    size = struct.unpack('>I', data[4:8])[0]
    n, width, initial, step, modulus, bases, words, remaining, lo, hi = json.loads(zlib.decompress(data[8:8+size]))
    bases = [x.encode('latin1') for x in bases]
    words = [x.encode('latin1') for x in words]
    dec = Decoder(data[8+size:])
    output = bytearray()
    for i in range(n):
        total = n - i
        split = total - remaining
        if dec.get(total) >= split:
            dec.take(split, total, total)
            remaining -= 1
            k = dec.get(hi - lo + 1)
            dec.take(k, k + 1, hi - lo + 1)
            ws = []
            for _ in range(k + lo):
                w = dec.get(len(words))
                dec.take(w, w + 1, len(words))
                ws.append(words[w])
            text = b' '.join(ws)
        else:
            dec.take(0, split, total)
            text = bases[i % len(bases)]
        output.extend(str(i).zfill(width).encode() + b' ' + text + b' ' + str((initial + step * i) % modulus).encode() + b'\n')
    return bytes(output)


def main():
    if len(sys.argv) == 3:
        source, dest = sys.argv[1:]
        transform = compress
    elif len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        source, dest = sys.argv[2:]
        transform = decompress
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(source, 'rb') as f:
        data = f.read()
    result = transform(data)
    with open(dest, 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
