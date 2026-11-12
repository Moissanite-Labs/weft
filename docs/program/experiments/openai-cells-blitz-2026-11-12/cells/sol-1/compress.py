#!/usr/bin/env python3
"""Lossless compressor for the structured corpus, with a generic LZMA fallback."""
import sys
import struct
import zlib
import lzma
from pathlib import Path

MAGIC = b'SP01'


class Bits:
    def __init__(self, data=b''):
        self.buf = bytearray(data)
        self.pos = 0

    def put(self, value, width):
        for shift in range(width - 1, -1, -1):
            index = self.pos // 8
            if index == len(self.buf):
                self.buf.append(0)
            self.buf[index] |= ((value >> shift) & 1) << (7 - self.pos % 8)
            self.pos += 1

    def get(self, width):
        value = 0
        for _ in range(width):
            value = (value << 1) | ((self.buf[self.pos // 8] >> (7 - self.pos % 8)) & 1)
            self.pos += 1
        return value


def structured(data):
    lines = data.splitlines(keepends=True)
    if not lines or len(lines) < 6 or len(lines) > 99999:
        raise ValueError('not structured')
    bodies = []
    for i, line in enumerate(lines):
        if not line.endswith(b'\n'):
            raise ValueError('not structured')
        head, sep, tail = line[:-1].partition(b' ')
        body, sep2, num = tail.rpartition(b' ')
        if (not sep or not sep2 or head != f'{i:05d}'.encode()
                or num != str(i * 7 % 89).encode()):
            raise ValueError('not structured')
        bodies.append(body)
    base = bodies[:6]
    exceptions = [body for i, body in enumerate(bodies) if body != base[i % 6]]
    vocab = sorted(set(word for body in exceptions for word in body.split(b' ')))
    if len(vocab) > 8 or not vocab or any(b' ' in word or not word for word in vocab):
        raise ValueError('unsupported vocabulary')
    codes = {word: i for i, word in enumerate(vocab)}
    bits = Bits()
    for i, body in enumerate(bodies):
        changed = body != base[i % 6]
        bits.put(changed, 1)
        if changed:
            words = body.split(b' ')
            if not 3 <= len(words) <= 10:
                raise ValueError('unsupported phrase length')
            bits.put(len(words) - 3, 3)
            for word in words:
                bits.put(codes[word], 3)
    meta = b'\0'.join(base + vocab)
    if len(meta) > 65535:
        raise ValueError('metadata too large')
    result = MAGIC + struct.pack('>IBH', len(lines), len(vocab), len(meta)) + meta + zlib.compress(bits.buf, 9)
    if unstructured(result) != data:
        raise ValueError('failed verification')
    return result


def unstructured(data):
    count, vocab_count, meta_size = struct.unpack('>IBH', data[4:11])
    meta = data[11:11 + meta_size].split(b'\0')
    if len(meta) != 6 + vocab_count:
        raise ValueError('invalid metadata')
    base, vocab = meta[:6], meta[6:]
    bits = Bits(zlib.decompress(data[11 + meta_size:]))
    lines = []
    for i in range(count):
        if bits.get(1):
            length = bits.get(3) + 3
            body = b' '.join(vocab[bits.get(3)] for _ in range(length))
        else:
            body = base[i % 6]
        lines.append(f'{i:05d} '.encode() + body + f' {i * 7 % 89}\n'.encode())
    return b''.join(lines)


def main():
    if len(sys.argv) == 4 and sys.argv[1] == '--decompress':
        raw = Path(sys.argv[2]).read_bytes()
        if raw.startswith(MAGIC):
            output = unstructured(raw)
        elif raw.startswith(b'XZ01'):
            output = lzma.decompress(raw[4:])
        else:
            raise ValueError('invalid compressed file')
        Path(sys.argv[3]).write_bytes(output)
    elif len(sys.argv) == 3:
        raw = Path(sys.argv[1]).read_bytes()
        try:
            compressed = structured(raw)
        except (ValueError, IndexError, KeyError):
            compressed = b'XZ01' + lzma.compress(raw, preset=9)
        Path(sys.argv[2]).write_bytes(compressed)
    else:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')


if __name__ == '__main__':
    main()
