#!/usr/bin/env python3
"""Stdlib lossless compressor. Usage: compress.py [--decompress] INPUT OUTPUT.

Numeric columns are modeled exactly; periodic messages and exception words are
learned from the input. All dictionaries and model parameters are in the file.
Unstructured input uses a bzip2 fallback.
"""
import bz2
from collections import Counter
import json
import sys
from pathlib import Path

MAGIC = b'CL2'


def render(meta, bodies):
    n, width, first, step, start, delta, modulus = meta
    return b''.join((f'{first + i * step:0{width}d} '.encode() + body +
                     f' {(start + i * delta) % modulus}\n'.encode())
                    for i, body in enumerate(bodies))


def split_records(data):
    if not data.endswith(b'\n'):
        raise ValueError('not newline-terminated records')
    lines = data[:-1].split(b'\n')
    if len(lines) < 2:
        raise ValueError('too few records')
    left, bodies, right = [], [], []
    for line in lines:
        a, rest = line.split(b' ', 1)
        body, b = rest.rsplit(b' ', 1)
        left.append(a)
        bodies.append(body)
        right.append(int(b))
    first = int(left[0])
    step = int(left[1]) - first
    modulus = max(right) + 1
    if modulus <= 0:
        raise ValueError('no modular counter')
    meta = [len(lines), len(left[0]), first, step, right[0],
            (right[1] - right[0]) % modulus, modulus]
    if render(meta, bodies) != data:
        raise ValueError('counters are not predictable')
    return meta, bodies


def token_payload(meta, bodies):
    choices = []
    for period in range(1, min(17, len(bodies) + 1)):
        templates = [Counter(bodies[j::period]).most_common(1)[0][0]
                     for j in range(period)]
        misses = sum(body != templates[i % period] for i, body in enumerate(bodies))
        choices.append((misses + 10 * period, templates))
    templates = min(choices, key=lambda pair: pair[0])[1]
    flags = bytes(body != templates[i % len(templates)] for i, body in enumerate(bodies))
    exceptions = [body.split(b' ') for body, flag in zip(bodies, flags) if flag]
    vocab = sorted({word for words in exceptions for word in words})
    if len(vocab) > 256 or any(len(words) > 255 for words in exceptions):
        raise ValueError('token alphabet too large')
    ids = {word: i for i, word in enumerate(vocab)}
    header = [meta, [t.decode('latin1') for t in templates],
              [w.decode('latin1') for w in vocab]]
    lengths = bytes(map(len, exceptions))
    words = bytes(ids[word] for words in exceptions for word in words)
    return json.dumps(header, separators=(',', ':')).encode() + b'\n' + flags + lengths + words


def compress(data):
    best = MAGIC + b'B' + bz2.compress(data, 9)
    try:
        meta, bodies = split_records(data)
        payload = json.dumps(meta, separators=(',', ':')).encode() + b'\n' + b'\n'.join(bodies)
        candidate = MAGIC + b'S' + bz2.compress(payload, 9)
        if len(candidate) < len(best):
            best = candidate
        candidate = MAGIC + b'T' + bz2.compress(token_payload(meta, bodies), 9)
        if len(candidate) < len(best):
            best = candidate
    except (ValueError, IndexError, OverflowError):
        pass
    return best


def decompress(data):
    if not data.startswith(MAGIC):
        raise ValueError('not a CL2 file')
    payload = bz2.decompress(data[4:])
    mode = data[3:4]
    if mode == b'B':
        return payload
    header, payload = payload.split(b'\n', 1)
    if mode == b'S':
        meta = json.loads(header)
        bodies = payload.split(b'\n')
    elif mode == b'T':
        meta, templates, vocab = json.loads(header)
        templates = [t.encode('latin1') for t in templates]
        vocab = [w.encode('latin1') for w in vocab]
        n = meta[0]
        flags = payload[:n]
        k = sum(flags)
        lengths = iter(payload[n:n + k])
        tokens = iter(payload[n + k:])
        bodies = [b' '.join(vocab[next(tokens)] for _ in range(next(lengths)))
                  if flags[i] else templates[i % len(templates)] for i in range(n)]
    else:
        raise ValueError('unknown codec')
    if len(bodies) != meta[0]:
        raise ValueError('wrong record count')
    return render(meta, bodies)


def main():
    args = sys.argv[1:]
    decoding = bool(args and args[0] == '--decompress')
    if decoding:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit(__doc__)
    source, target = map(Path, args)
    target.write_bytes((decompress if decoding else compress)(source.read_bytes()))


if __name__ == '__main__':
    main()
