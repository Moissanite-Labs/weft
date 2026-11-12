#!/usr/bin/env python3
"""Lossless stdlib compressor with a self-describing periodic-record model.

All learned templates and vocabulary are in the compressed file. Unstructured
inputs fall back to ordinary compression. No external files aid decompression.
"""
import bz2
from collections import Counter
import json
import lzma
import struct
import sys
import zlib

TOP = (1 << 32) - 1
HALF = 1 << 31
QUARTER = 1 << 30


class Arithmetic:
    def __init__(self, data=None):
        self.lo, self.hi = 0, TOP
        self.pending = 0
        self.bits = []
        self.data = data
        self.pos = 0
        self.value = 0
        if data is not None:
            for _ in range(32):
                self.value = (self.value << 1) | self.read()

    def read(self):
        p = self.pos
        self.pos += 1
        return (self.data[p // 8] >> (7 - p % 8)) & 1 if p < len(self.data)*8 else 0

    def emit(self, bit):
        self.bits.append(bit)
        self.bits.extend([1-bit] * self.pending)
        self.pending = 0

    def symbol(self, counts, symbol=None):
        total = sum(counts)
        width = self.hi - self.lo + 1
        cumulative = 0
        if self.data is not None:
            target = ((self.value - self.lo + 1)*total - 1) // width
            symbol = 0
            while cumulative + counts[symbol] <= target:
                cumulative += counts[symbol]
                symbol += 1
        else:
            cumulative = sum(counts[:symbol])
        self.hi = self.lo + width*(cumulative + counts[symbol])//total - 1
        self.lo += width*cumulative//total
        while True:
            if self.hi < HALF:
                if self.data is None:
                    self.emit(0)
            elif self.lo >= HALF:
                if self.data is None:
                    self.emit(1)
                self.lo -= HALF
                self.hi -= HALF
                self.value -= HALF
            elif self.lo >= QUARTER and self.hi < 3*QUARTER:
                self.pending += 1
                self.lo -= QUARTER
                self.hi -= QUARTER
                self.value -= QUARTER
            else:
                break
            self.lo *= 2
            self.hi = self.hi*2 + 1
            if self.data is not None:
                self.value = self.value*2 + self.read()
        counts[symbol] += 1
        if total >= 16384:
            counts[:] = [(x+1)//2 for x in counts]
        return symbol

    def finish(self):
        self.pending += 1
        self.emit(int(self.lo >= QUARTER))
        self.bits.extend([0] * (-len(self.bits) % 8))
        return bytes(sum(self.bits[i+j] << (7-j) for j in range(8))
                     for i in range(0, len(self.bits), 8))


def structured(data):
    if not data.endswith(b'\n'):
        return None
    lines = data[:-1].split(b'\n')
    if len(lines) < 32:
        return None
    try:
        pieces = [line.split(b' ', 1) for line in lines]
        width = len(pieces[0][0])
        if any(p[0] != str(i).zfill(width).encode() for i,p in enumerate(pieces)):
            return None
        pieces = [p[1].rsplit(b' ', 1) for p in pieces]
        numbers = [int(p[1]) for p in pieces]
        modulus = max(numbers) + 1
        start = numbers[0]
        step = (numbers[1] - start) % modulus
        if any(p[1] != str((start+i*step) % modulus).encode() for i,p in enumerate(pieces)):
            return None
        bodies = [p[0] for p in pieces]
        best = None
        for period in range(1, 17):
            templates = [Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
            errors = sum(body != templates[i % period] for i,body in enumerate(bodies))
            score = errors + 5*period
            if best is None or score < best[0]:
                best = score, templates
        templates = best[1]
        period = len(templates)
        exceptions = [body.split(b' ') for i,body in enumerate(bodies) if body != templates[i % period]]
        vocab = sorted({word for words in exceptions for word in words})
        if not vocab or len(vocab) > 255:
            return None
        lengths = [len(words) for words in exceptions]
        minimum, maximum = min(lengths), max(lengths)
        if maximum - minimum > 255:
            return None
        index = {word:i for i,word in enumerate(vocab)}
        header = [len(lines), width, start, step, modulus,
                  [t.decode('latin1') for t in templates],
                  [w.decode('latin1') for w in vocab], minimum, maximum]
        header = zlib.compress(json.dumps(header, separators=(',', ':')).encode(), 9)
        coder = Arithmetic()
        flags, lens, words = [1,1], [1]*(maximum-minimum+1), [1]*len(vocab)
        for i,body in enumerate(bodies):
            exceptional = body != templates[i % period]
            coder.symbol(flags, int(exceptional))
            if exceptional:
                tokens = body.split(b' ')
                coder.symbol(lens, len(tokens)-minimum)
                for word in tokens:
                    coder.symbol(words, index[word])
        return b'CEL2A' + struct.pack('>I', len(header)) + header + coder.finish()
    except (ValueError, IndexError, ZeroDivisionError):
        return None


def compress(data):
    candidates = [b'CEL2B' + bz2.compress(data, compresslevel=9)]
    special = structured(data)
    if special is not None and decompress(special) == data:
        candidates.append(special)
    else:
        candidates.extend([b'CEL2Z'+zlib.compress(data,9), b'CEL2L'+lzma.compress(data)])
    return min(candidates, key=len)


def decompress(data):
    if data[:4] != b'CEL2':
        raise ValueError('Invalid compressed stream')
    mode = data[4:5]
    if mode == b'B':
        return bz2.decompress(data[5:])
    if mode == b'Z':
        return zlib.decompress(data[5:])
    if mode == b'L':
        return lzma.decompress(data[5:])
    if mode != b'A':
        raise ValueError('Unknown compression mode')
    size, = struct.unpack('>I', data[5:9])
    n, width, start, step, modulus, templates, vocab, minimum, maximum = json.loads(zlib.decompress(data[9:9+size]))
    templates = [t.encode('latin1') for t in templates]
    vocab = [w.encode('latin1') for w in vocab]
    coder = Arithmetic(data[9+size:])
    flags, lens, words = [1,1], [1]*(maximum-minimum+1), [1]*len(vocab)
    result = []
    for i in range(n):
        if coder.symbol(flags):
            length = coder.symbol(lens)+minimum
            body = b' '.join(vocab[coder.symbol(words)] for _ in range(length))
        else:
            body = templates[i % len(templates)]
        result.append(str(i).zfill(width).encode()+b' '+body+b' '+str((start+i*step)%modulus).encode()+b'\n')
    return b''.join(result)


def main():
    args = sys.argv[1:]
    decode = bool(args and args[0] == '--decompress')
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('Usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
