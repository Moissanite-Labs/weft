#!/usr/bin/env python3
"""Self-contained lossless compressor using a validated periodic text model.

The structured format stores its numeric sequence parameters, phrase dictionary,
word dictionary and arithmetic-coded exceptions. Other inputs use bzip2.
Only Python's standard library is required.
"""
import bz2
from collections import Counter
import json
import struct
import sys
import zlib

TOP = (1 << 32) - 1
HALF = 1 << 31
QUARTER = 1 << 30

class Encoder:
    def __init__(self):
        self.lo = 0
        self.hi = TOP
        self.pending = 0
        self.out = bytearray()
        self.byte = self.nbits = 0

    def bit(self, value):
        self.byte = (self.byte << 1) | value
        self.nbits += 1
        if self.nbits == 8:
            self.out.append(self.byte)
            self.byte = self.nbits = 0

    def emit(self, value):
        self.bit(value)
        for _ in range(self.pending):
            self.bit(1 - value)
        self.pending = 0

    def symbol(self, low, high, total):
        width = self.hi - self.lo + 1
        self.hi = self.lo + width * high // total - 1
        self.lo += width * low // total
        while True:
            if self.hi < HALF:
                self.emit(0)
            elif self.lo >= HALF:
                self.emit(1)
                self.lo -= HALF
                self.hi -= HALF
            elif self.lo >= QUARTER and self.hi < 3 * QUARTER:
                self.pending += 1
                self.lo -= QUARTER
                self.hi -= QUARTER
            else:
                break
            self.lo <<= 1
            self.hi = (self.hi << 1) | 1

    def finish(self):
        self.pending += 1
        self.emit(0 if self.lo < QUARTER else 1)
        if self.nbits:
            self.out.append(self.byte << (8 - self.nbits))
        return bytes(self.out)

class Decoder:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.lo = 0
        self.hi = TOP
        self.code = 0
        for _ in range(32):
            self.code = (self.code << 1) | self.bit()

    def bit(self):
        p = self.pos
        self.pos += 1
        return (self.data[p // 8] >> (7 - p % 8)) & 1 if p // 8 < len(self.data) else 0

    def target(self, total):
        return ((self.code - self.lo + 1) * total - 1) // (self.hi - self.lo + 1)

    def consume(self, low, high, total):
        width = self.hi - self.lo + 1
        self.hi = self.lo + width * high // total - 1
        self.lo += width * low // total
        while True:
            if self.hi < HALF:
                pass
            elif self.lo >= HALF:
                self.code -= HALF
                self.lo -= HALF
                self.hi -= HALF
            elif self.lo >= QUARTER and self.hi < 3 * QUARTER:
                self.code -= QUARTER
                self.lo -= QUARTER
                self.hi -= QUARTER
            else:
                break
            self.lo <<= 1
            self.hi = (self.hi << 1) | 1
            self.code = (self.code << 1) | self.bit()

    def uniform(self, total):
        value = self.target(total)
        self.consume(value, value + 1, total)
        return value


def structured(data):
    text = data.decode('ascii')
    newline = text.endswith('\n')
    rows = text[:-1].split('\n') if newline else text.split('\n')
    if len(rows) < 32:
        raise ValueError('too short')
    prefixes, bodies, suffixes = [], [], []
    for row in rows:
        prefix, rest = row.split(' ', 1)
        body, suffix = rest.rsplit(' ', 1)
        prefixes.append(prefix)
        bodies.append(body)
        suffixes.append(suffix)
    n = len(rows)
    width = len(prefixes[0])
    start = int(prefixes[0])
    step = int(prefixes[1]) - start
    if any(p != str(start + i * step).zfill(width) for i, p in enumerate(prefixes)):
        raise ValueError('nonlinear prefix')
    numbers = list(map(int, suffixes))
    modulus = max(numbers) + 1
    if modulus <= 0:
        raise ValueError('bad suffix')
    initial = numbers[0]
    delta = (numbers[1] - initial) % modulus
    if any(s != str((initial + i * delta) % modulus) for i, s in enumerate(suffixes)):
        raise ValueError('nonmodular suffix')
    best = None
    for period in range(1, 17):
        phrases = [Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        errors = sum(body != phrases[i % period] for i, body in enumerate(bodies))
        cost = errors * 20 + sum(map(len, phrases))
        if best is None or cost < best[0]:
            best = cost, phrases
    phrases = best[1]
    period = len(phrases)
    exceptions = [body for i, body in enumerate(bodies) if body != phrases[i % period]]
    if not exceptions:
        words, minlen, maxlen = [], 0, 0
    else:
        split = [body.split(' ') for body in exceptions]
        words = sorted({w for row in split for w in row})
        minlen = min(map(len, split))
        maxlen = max(map(len, split))
    if len(words) > 10000 or maxlen > 10000:
        raise ValueError('model too large')
    mapping = {word: i for i, word in enumerate(words)}
    good = n - len(exceptions)
    encoder = Encoder()
    for i, body in enumerate(bodies):
        if body == phrases[i % period]:
            encoder.symbol(0, good, n)
        else:
            encoder.symbol(good, n, n)
            tokens = body.split(' ')
            length = len(tokens) - minlen
            encoder.symbol(length, length + 1, maxlen - minlen + 1)
            for word in tokens:
                index = mapping[word]
                encoder.symbol(index, index + 1, len(words))
    header = [n, width, start, step, initial, delta, modulus, phrases, words, minlen, maxlen, good, newline]
    packed = zlib.compress(json.dumps(header, separators=(',', ':')).encode('ascii'), 9)
    return b'PC1' + struct.pack('>I', len(packed)) + packed + encoder.finish()


def compress(data):
    fallback = b'BZ1' + bz2.compress(data, compresslevel=9)
    try:
        candidate = structured(data)
        if len(candidate) < len(fallback) and decompress(candidate) == data:
            return candidate
    except (ValueError, UnicodeError, IndexError, OverflowError):
        pass
    return fallback


def decompress(data):
    if data[:3] == b'BZ1':
        return bz2.decompress(data[3:])
    if data[:3] != b'PC1':
        raise ValueError('unknown compressed format')
    size, = struct.unpack('>I', data[3:7])
    header = json.loads(zlib.decompress(data[7:7 + size]))
    n, width, start, step, initial, delta, modulus, phrases, words, minlen, maxlen, good, newline = header
    decoder = Decoder(data[7 + size:])
    rows = []
    for i in range(n):
        if decoder.target(n) < good:
            decoder.consume(0, good, n)
            body = phrases[i % len(phrases)]
        else:
            decoder.consume(good, n, n)
            length = minlen + decoder.uniform(maxlen - minlen + 1)
            body = ' '.join(words[decoder.uniform(len(words))] for _ in range(length))
        rows.append(str(start + i * step).zfill(width) + ' ' + body + ' ' + str((initial + i * delta) % modulus))
    return ('\n'.join(rows) + ('\n' if newline else '')).encode('ascii')


if __name__ == '__main__':
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)
