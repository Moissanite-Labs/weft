#!/usr/bin/env python3
"""Lossless compression with inferred line structure and a bzip2 fallback."""
import argparse
import bz2
from collections import Counter
import json
from pathlib import Path
import struct
import zlib

MAGIC = b"CEL2"


def _model(data):
    if not data.endswith(b"\n"):
        return None
    lines = data[:-1].split(b"\n")
    if not 2 <= len(lines) <= 20000:
        return None
    rows, numbers = [], []
    try:
        width = len(lines[0].split(b" ", 1)[0])
        for i, line in enumerate(lines):
            prefix, rest = line.split(b" ", 1)
            body, suffix = rest.rsplit(b" ", 1)
            if prefix != str(i).encode().zfill(width):
                return None
            number = int(suffix)
            if suffix != str(number).encode():
                return None
            rows.append(body)
            numbers.append(number)
    except ValueError:
        return None
    modulus = max(numbers) + 1
    if modulus <= 0:
        return None
    start = numbers[0]
    step = (numbers[1] - start) % modulus
    if any(x != (start + i * step) % modulus for i, x in enumerate(numbers)):
        return None
    best_score, templates = -1, None
    for period in range(1, min(32, len(rows)) + 1):
        modes = [Counter(rows[r::period]).most_common(1)[0] for r in range(period)]
        score = sum(count for _, count in modes) - 2 * period
        if score > best_score:
            best_score = score
            templates = [text for text, _ in modes]
    if templates is None:
        return None
    positions = [i for i, row in enumerate(rows) if row != templates[i % len(templates)]]
    exceptions = [rows[i].split(b" ") for i in positions]
    vocab = sorted({word for words in exceptions for word in words})
    indices = {word: i for i, word in enumerate(vocab)}
    records = [[indices[word] for word in words] for words in exceptions]
    lo = min(map(len, records), default=0)
    hi = max(map(len, records), default=0)
    meta = [len(rows), width, start, step, modulus,
            [t.decode("latin1") for t in templates],
            [w.decode("latin1") for w in vocab], lo, hi, len(records), zlib.crc32(data)]
    return meta, positions, records


def _restore(meta, exceptions):
    n, width, start, step, modulus, templates, _, _, _, _, crc = meta
    templates = [t.encode("latin1") for t in templates]
    result = b"".join(str(i).encode().zfill(width) + b" " +
                      exceptions.get(i, templates[i % len(templates)]) + b" " +
                      str((start + i * step) % modulus).encode() + b"\n"
                      for i in range(n))
    if zlib.crc32(result) != crc:
        raise ValueError("checksum mismatch")
    return result


def compress(data):
    fallback = MAGIC + b"B" + bz2.compress(data, compresslevel=9)
    model = _model(data)
    if model is None:
        return fallback
    meta, positions, records = model
    if len(meta[6]) > 256 or meta[8] - meta[7] > 255:
        return fallback
    header = json.dumps(meta, separators=(",", ":")).encode()
    flags = bytearray(meta[0])
    for position in positions:
        flags[position] = 1
    lengths = bytes(len(record) - meta[7] for record in records)
    words = bytes(word for record in records for word in record)
    payload = struct.pack("<I", len(header)) + header + flags + lengths + words
    candidate = MAGIC + b"T" + bz2.compress(payload, compresslevel=9)
    return min((fallback, candidate), key=len)


def decompress(blob):
    if blob[:4] != MAGIC:
        raise ValueError("not a CEL2 file")
    if blob[4:5] == b"B":
        return bz2.decompress(blob[5:])
    if blob[4:5] != b"T":
        raise ValueError("unknown compression method")
    raw = bz2.decompress(blob[5:])
    size = struct.unpack_from("<I", raw)[0]
    meta = json.loads(raw[4:4 + size])
    n, _, _, _, _, _, vocab, lo, _, k, _ = meta
    vocab = [word.encode("latin1") for word in vocab]
    offset = 4 + size
    flags = raw[offset:offset + n]
    offset += n
    lengths = raw[offset:offset + k]
    offset += k
    exceptions = {}
    j = 0
    for i, flag in enumerate(flags):
        if flag:
            length = lo + lengths[j]
            exceptions[i] = b" ".join(vocab[c] for c in raw[offset:offset + length])
            offset += length
            j += 1
    if j != k or offset != len(raw):
        raise ValueError("invalid record stream")
    return _restore(meta, exceptions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decompress", action="store_true")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        data = args.source.read_bytes()
        result = decompress(data) if args.decompress else compress(data)
        args.destination.write_bytes(result)
    except (OSError, ValueError, EOFError, IndexError, struct.error) as exc:
        parser.exit(1, "compress.py: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
