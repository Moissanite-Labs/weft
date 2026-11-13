#!/usr/bin/env python3
"""Self-contained lossless compression using only the Python standard library."""
import argparse
import bz2
from collections import Counter
import json
import lzma
import math
from pathlib import Path
import struct
import zlib

MAGIC = b'SC1'
SPLIT = True
FILTERS = [{'id': lzma.FILTER_LZMA2, 'dict_size': 1 << 20,
            'preset': 9 | lzma.PRESET_EXTREME, 'pb': 0}]


def numeric_model(column):
    values = [int(x) for x in column]
    width = 0
    if any(str(v).encode() != s for v, s in zip(values, column)):
        width = len(column[0])
        if any(str(v).zfill(width).encode() != s for v, s in zip(values, column)):
            raise ValueError('inconsistent numeric formatting')
    start = values[0]
    step = values[1] - start if len(values) > 1 else 0
    modulus = 0
    for i, value in enumerate(values):
        modulus = math.gcd(modulus, start + i * step - value)
    if modulus:
        if min(values) < 0 or max(values) >= modulus:
            raise ValueError('not a modular progression')
        step %= modulus
    return [start, step, modulus, width]


def transform(data):
    trailing = data.endswith(b'\n')
    rows = data.split(b'\n')
    if trailing:
        rows.pop()
    if len(rows) < 2:
        return None
    first, texts, last = [], [], []
    try:
        for row in rows:
            a, rest = row.split(b' ', 1)
            text, b = rest.rsplit(b' ', 1)
            if not a.isdigit() or not b.isdigit():
                return None
            first.append(a)
            texts.append(text)
            last.append(b)
        left, right = numeric_model(first), numeric_model(last)
    except ValueError:
        return None
    best = None
    for period in range(1, min(24, len(rows)) + 1):
        templates = [Counter(texts[j::period]).most_common(1)[0][0]
                     for j in range(period)]
        misses = sum(t != templates[i % period] for i, t in enumerate(texts))
        cost = 16 * misses + sum(map(len, templates))
        if best is None or cost < best[0]:
            best = cost, templates
    templates = best[1]
    period = len(templates)
    exceptions = [t.split(b' ') for i, t in enumerate(texts)
                  if t != templates[i % period]]
    if any(len(words) > 255 for words in exceptions):
        return None
    counts = Counter(word for words in exceptions for word in words)
    if len(counts) > 256:
        return None
    vocabulary = [word for word, count in counts.most_common()]
    ids = {word: i for i, word in enumerate(vocabulary)}
    tags, lengths, tokens = bytearray(), bytearray(), bytearray()
    for i, text in enumerate(texts):
        if text == templates[i % period]:
            tags.append(0)
        else:
            words = text.split(b' ')
            tags.append(1 if SPLIT else len(words))
            if SPLIT:
                lengths.append(len(words))
            tokens.extend(ids[word] for word in words)
    meta = [len(rows), int(trailing), left, right,
            [t.decode('latin1') for t in templates],
            [w.decode('latin1') for w in vocabulary]]
    header = json.dumps(meta, separators=(',', ':')).encode('ascii')
    body = struct.pack('<I', len(header)) + header + tags + lengths + tokens
    return (2 if SPLIT else 1), body


def number(model, i):
    start, step, modulus, width = model
    value = start + step * i
    if modulus:
        value %= modulus
    return str(value).zfill(width).encode('ascii')


def restore(body, kind):
    size = struct.unpack_from('<I', body)[0]
    n, trailing, left, right, templates, vocabulary = json.loads(body[4:4+size])
    templates = [t.encode('latin1') for t in templates]
    vocabulary = [w.encode('latin1') for w in vocabulary]
    position = 4 + size
    tags = body[position:position+n]
    position += n
    if kind == 2:
        count = sum(tags)
        lengths = iter(body[position:position+count])
        position += count
    lines = []
    for i, tag in enumerate(tags):
        if tag:
            length = next(lengths) if kind == 2 else tag
            text = b' '.join(vocabulary[x] for x in body[position:position+length])
            position += length
        else:
            text = templates[i % len(templates)]
        lines.append(number(left, i) + b' ' + text + b' ' + number(right, i))
    if len(tags) != n or position != len(body):
        raise ValueError('invalid structured payload')
    return b'\n'.join(lines) + (b'\n' if trailing else b'')


def encodings(data):
    yield 0, zlib.compress(data, level=9, wbits=-15)
    yield 1, bz2.compress(data, compresslevel=9)
    yield 2, lzma.compress(data, format=lzma.FORMAT_RAW, filters=FILTERS)


def compress(data):
    candidates = [(0, data)]
    transformed = transform(data)
    if transformed is not None:
        candidates.append(transformed)
    checksum = struct.pack('<I', zlib.crc32(data))
    best = None
    for kind, body in candidates:
        for codec, packed in encodings(body):
            archive = MAGIC + bytes([kind, codec]) + checksum + packed
            if best is None or len(archive) < len(best):
                best = archive
    return best


def decompress(data):
    if len(data) < 9 or data[:3] != MAGIC:
        raise ValueError('not an SC1 archive')
    kind, codec = data[3:5]
    if kind not in (0, 1, 2):
        raise ValueError('unknown transform')
    packed = data[9:]
    if codec == 0:
        body = zlib.decompress(packed, wbits=-15)
    elif codec == 1:
        body = bz2.decompress(packed)
    elif codec == 2:
        body = lzma.decompress(packed, format=lzma.FORMAT_RAW, filters=FILTERS)
    else:
        raise ValueError('unknown codec')
    result = restore(body, kind) if kind else body
    if zlib.crc32(result) != struct.unpack_from('<I', data, 5)[0]:
        raise ValueError('checksum mismatch')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    data = Path(args.source).read_bytes()
    result = decompress(data) if args.decompress else compress(data)
    Path(args.destination).write_bytes(result)


if __name__ == '__main__':
    main()
