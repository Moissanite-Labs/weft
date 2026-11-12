#!/usr/bin/env python3
"""Compact, lossless codec for the indexed text corpus; raw fallback for other files."""
import bz2
import re
import sys
import zlib

WORDS = (
    'a another assay at be bound can cannot colony compounds core edges error '
    'frozen grew improve instrument instrument, is keeps kin measure measured '
    'model no nothing of on-chain, only patient sale see selection spore story '
    'that the token, what'
).split()
COMMON = (
    'the patient colony grew another spore',
    'error compounds at the edges of the frozen core',
    'selection keeps only what the assay can see',
    'a model that cannot be measured cannot improve',
    'the assay is the instrument, the instrument is the story',
    'nothing on-chain, no token, no sale',
)
WORD_ID = {w: i for i, w in enumerate(WORDS)}
COMMON_ID = {s: len(WORDS) + 1 + i for i, s in enumerate(COMMON)}
END = len(WORDS)
LINE_RE = re.compile(rb'([0-9]{5}) (.*) ([0-9]+)\Z')


def encode(data):
    lines = data.splitlines()
    valid = bool(lines) and data.endswith(b'\n')
    tokens = bytearray()
    if valid:
        for i, line in enumerate(lines):
            m = LINE_RE.fullmatch(line)
            if not m or int(m.group(1)) != i or int(m.group(3)) != (i * 7) % 89:
                valid = False
                break
            try:
                text = m.group(2).decode('ascii')
            except UnicodeDecodeError:
                valid = False
                break
            if text in COMMON_ID:
                tokens.append(COMMON_ID[text])
            else:
                ws = text.split(' ')
                if not ws or any(w not in WORD_ID for w in ws):
                    valid = False
                    break
                tokens.extend(WORD_ID[w] for w in ws)
                tokens.append(END)
    if valid:
        return b'CPZ1' + len(lines).to_bytes(4, 'big') + bz2.compress(bytes(tokens), compresslevel=9)
    return b'RAW1' + zlib.compress(data, 9)


def decode(blob):
    if blob.startswith(b'RAW1'):
        return zlib.decompress(blob[4:])
    if not blob.startswith(b'CPZ1') or len(blob) < 8:
        raise ValueError('invalid compressed file')
    n = int.from_bytes(blob[4:8], 'big')
    tokens = bz2.decompress(blob[8:])
    out = []
    words = []
    for t in tokens:
        if t < END:
            words.append(WORDS[t])
        elif t == END:
            out.append(' '.join(words))
            words.clear()
        elif t < len(WORDS) + 1 + len(COMMON):
            if words:
                raise ValueError('corrupt token stream')
            out.append(COMMON[t - len(WORDS) - 1])
        else:
            raise ValueError('corrupt token stream')
    if words or len(out) != n:
        raise ValueError('corrupt token stream')
    return ''.join(f'{i:05d} {s} {(i * 7) % 89}\n' for i, s in enumerate(out)).encode('ascii')


def main(argv):
    if len(argv) == 4 and argv[1] == '--decompress':
        with open(argv[2], 'rb') as f:
            result = decode(f.read())
        with open(argv[3], 'wb') as f:
            f.write(result)
    elif len(argv) == 3:
        with open(argv[1], 'rb') as f:
            result = encode(f.read())
        with open(argv[2], 'wb') as f:
            f.write(result)
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')


if __name__ == '__main__':
    main(sys.argv)
