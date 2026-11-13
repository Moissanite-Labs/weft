#!/usr/bin/env python3
"""Lossless compression, with an optional transform for numbered records."""
import bz2
import lzma
import marshal
import re
import sys
from collections import Counter
from pathlib import Path


def transform(data):
    lines = data.splitlines(keepends=True)
    if len(lines) < 3:
        return None
    records = [re.fullmatch(rb'(\d+) (.*) (\d+)\n', line) for line in lines]
    if not all(records):
        return None
    records = [m.groups() for m in records]
    width = len(records[0][0]); start = int(records[0][0])
    if any(a != str(start+i).zfill(width).encode() for i, (a, _, _) in enumerate(records)):
        return None
    values = [int(c) for _, _, c in records]
    if any(c != str(v).encode() for (_, _, c), v in zip(records, values)):
        return None
    diffs = set(b-a for a, b in zip(values, values[1:]))
    if len(diffs) == 1:
        step = next(iter(diffs)); modulus = 0
    elif len(diffs) == 2:
        step = max(diffs); modulus = max(diffs)-min(diffs)
    else:
        return None
    if any(v != ((values[0]+i*step) % modulus if modulus else values[0]+i*step) for i, v in enumerate(values)):
        return None
    bodies = [b for _, b, _ in records]
    def templates(p):
        return [Counter(bodies[j::p]).most_common(1)[0] for j in range(p)]
    best = max((sum(c for _, c in templates(p))-4*p, p) for p in range(1, min(17, len(lines)+1)))[1]
    common = [b for b, _ in templates(best)]
    different = [b != common[i % best] for i, b in enumerate(bodies)]
    vocab = list(dict.fromkeys(w for i, b in enumerate(bodies) if different[i] for w in b.split(b' ')))
    if len(vocab) > 255:
        return None
    codes = {w: i+1 for i, w in enumerate(vocab)}
    mask = bytearray((len(lines)+7)//8); symbols = bytearray()
    for i, b in enumerate(bodies):
        if different[i]:
            mask[i//8] |= 1 << (i%8)
            symbols.extend(codes[w] for w in b.split(b' ')); symbols.append(0)
    return marshal.dumps((width, start, values[0], step, modulus, len(lines), common, vocab, bytes(mask), bytes(symbols)))


def restore(payload):
    width, start, first, step, modulus, n, common, vocab, mask, symbols = marshal.loads(payload)
    it = iter(symbols); out = bytearray()
    for i in range(n):
        if mask[i//8] & (1 << (i%8)):
            words = []
            while (code := next(it)):
                words.append(vocab[code-1])
            body = b' '.join(words)
        else:
            body = common[i % len(common)]
        value = (first+i*step) % modulus if modulus else first+i*step
        out.extend(str(start+i).zfill(width).encode() + b' ' + body + b' ' + str(value).encode() + b'\n')
    return bytes(out)


def main():
    args = sys.argv[1:]; dec = bool(args and args[0] == '--decompress')
    if dec: args = args[1:]
    if len(args) != 2: raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    if dec:
        result = bz2.decompress(data[1:]) if data[:1] == b'B' else restore(bz2.decompress(data[1:])) if data[:1] == b'S' else (_ for _ in ()).throw(ValueError('unknown format'))
    else:
        result = b'B' + bz2.compress(data)
        payload = transform(data)
        if payload is not None:
            alt = b'S' + bz2.compress(payload)
            if len(alt) < len(result): result = alt
    Path(args[1]).write_bytes(result)

if __name__ == '__main__': main()
