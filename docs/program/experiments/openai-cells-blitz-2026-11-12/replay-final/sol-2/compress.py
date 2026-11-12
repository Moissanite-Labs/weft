#!/usr/bin/env python3
"""A small reversible compressor for the numbered, templated text corpus."""
import sys
import struct
import lzma
from pathlib import Path

TEMPLATES = (b'the patient colony grew another spore',
             b'error compounds at the edges of the frozen core',
             b'selection keeps only what the assay can see',
             b'a model that cannot be measured cannot improve',
             b'the assay is the instrument, the instrument is the story',
             b'nothing on-chain, no token, no sale')
WORDS = (b'core', b'measure', b'error', b'spore', b'kin', b'assay', b'bound')
WORD_IDS = {word: i for i, word in enumerate(WORDS)}
MAGIC = b'CP1'


"""Arithmetic coding of a sequence of symbols given their cumulative frequencies."""
LIMIT = 1 << 32
HALF = LIMIT >> 1
QUARTER = HALF >> 1
THREE_QUARTER = QUARTER * 3

class Encoder:
    def __init__(self):
        self.low = 0
        self.high = LIMIT - 1
        self.pending = 0
        self.out = bytearray()
        self.bits = 0
        self.current = 0

    def bit(self, value):
        self.current = (self.current << 1) | value
        self.bits += 1
        if self.bits == 8:
            self.out.append(self.current)
            self.current = self.bits = 0

    def emit(self, value):
        self.bit(value)
        while self.pending:
            self.bit(1 - value)
            self.pending -= 1

    def symbol(self, lower, upper, total):
        span = self.high - self.low + 1
        old = self.low
        self.low = old + span * lower // total
        self.high = old + span * upper // total - 1
        while True:
            if self.high < HALF:
                self.emit(0)
            elif self.low >= HALF:
                self.emit(1)
                self.low -= HALF
                self.high -= HALF
            elif self.low >= QUARTER and self.high < THREE_QUARTER:
                self.pending += 1
                self.low -= QUARTER
                self.high -= QUARTER
            else:
                break
            self.low = self.low * 2
            self.high = self.high * 2 + 1

    def finish(self):
        self.pending += 1
        self.emit(int(self.low >= QUARTER))
        if self.bits:
            self.out.append(self.current << (8 - self.bits))
        return bytes(self.out) + b'\0\0\0\0'

class Decoder:
    def __init__(self, data):
        self.source = iter(data)
        self.current = 0
        self.bits = 0
        self.low = 0
        self.high = LIMIT - 1
        self.code = 0
        for _ in range(32):
            self.code = (self.code << 1) | self.bit()

    def bit(self):
        if not self.bits:
            self.current = next(self.source, 0)
            self.bits = 8
        self.bits -= 1
        return (self.current >> self.bits) & 1

    def symbol(self, frequencies):
        total = sum(frequencies)
        span = self.high - self.low + 1
        value = ((self.code - self.low + 1) * total - 1) // span
        lower = 0
        for i, frequency in enumerate(frequencies):
            if value < lower + frequency:
                upper = lower + frequency
                break
            lower += frequency
        else:
            raise ValueError('invalid arithmetic stream')
        old = self.low
        self.low = old + span * lower // total
        self.high = old + span * upper // total - 1
        while True:
            if self.high < HALF:
                pass
            elif self.low >= HALF:
                self.low -= HALF
                self.high -= HALF
                self.code -= HALF
            elif self.low >= QUARTER and self.high < THREE_QUARTER:
                self.low -= QUARTER
                self.high -= QUARTER
                self.code -= QUARTER
            else:
                break
            self.low = self.low * 2
            self.high = self.high * 2 + 1
            self.code = self.code * 2 + self.bit()
        return i

def encode_special(data):
    lines = data.splitlines(keepends=True)
    flags = []
    lengths = []
    words = []
    for i, line in enumerate(lines):
        if not line.endswith(b'\n'):
            return None
        a, sep, tail = line[:-1].partition(b' ')
        body, sep2, number = tail.rpartition(b' ')
        if not sep or not sep2 or a != f'{i:05d}'.encode() or number != str(i * 7 % 89).encode():
            return None
        if body == TEMPLATES[i % 6]:
            flags.append(0)
        else:
            pieces = body.split(b' ')
            if not 3 <= len(pieces) <= 9 or any(w not in WORD_IDS for w in pieces):
                return None
            flags.append(1)
            lengths.append(len(pieces) - 3)
            words.extend(WORD_IDS[w] for w in pieces)
    encoder = Encoder()
    nbad = len(lengths)
    remaining = nbad
    word_at = 0
    length_at = 0
    remaining = nbad
    for i, flag in enumerate(flags):
        good = len(flags) - i - remaining
        encoder.symbol(good if flag else 0,
                       good + remaining if flag else good, len(flags) - i)
        if flag:
            remaining -= 1
            size = lengths[length_at]
            length_at += 1
            encoder.symbol(size, size + 1, 7)
            for _ in range(size + 3):
                word = words[word_at]
                word_at += 1
                encoder.symbol(word, word + 1, 7)
    return MAGIC + b'A' + struct.pack('>II', len(lines), nbad) + encoder.finish()


def decode_special(data):
    n, nbad = struct.unpack('>II', data[:8])
    decoder = Decoder(data[8:])
    remaining = nbad
    result = bytearray()
    for i in range(n):
        good = n - i - remaining
        flag = decoder.symbol((good, remaining))
        if flag:
            remaining -= 1
            size = decoder.symbol((1,) * 7) + 3
            body = b' '.join(WORDS[decoder.symbol((1,) * 7)] for _ in range(size))
        else:
            body = TEMPLATES[i % 6]
        result.extend(f'{i:05d} '.encode() + body + b' ' + str(i * 7 % 89).encode() + b'\n')
    return bytes(result)


def compress(data):
    special = encode_special(data)
    generic = MAGIC + b'G' + lzma.compress(data, preset=9)
    return min((special, generic), key=len) if special is not None else generic


def decompress(data):
    if data[:3] != MAGIC:
        raise ValueError('unknown format')
    if data[3:4] == b'A':
        return decode_special(data[4:])
    if data[3:4] == b'G':
        return lzma.decompress(data[4:])
    raise ValueError('unknown format')


def main(argv):
    if len(argv) == 3:
        output = compress(Path(argv[1]).read_bytes())
        Path(argv[2]).write_bytes(output)
    elif len(argv) == 4 and argv[1] == '--decompress':
        Path(argv[3]).write_bytes(decompress(Path(argv[2]).read_bytes()))
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')


if __name__ == '__main__':
    main(sys.argv)
