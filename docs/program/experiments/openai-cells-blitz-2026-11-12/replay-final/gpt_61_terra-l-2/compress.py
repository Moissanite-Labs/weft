#!/usr/bin/env python3
"""Lossless record-oriented compression with an LZMA fallback."""
import bz2, collections, json, lzma, struct, sys, zlib


def transform(data):
    lines = data.splitlines(keepends=True)
    if len(lines) < 20 or any(not line.endswith(b'\n') for line in lines):
        return None
    records = []
    try:
        for line in lines:
            left, text = line[:-1].split(b' ', 1)
            text, right = text.rsplit(b' ', 1)
            records.append((left, text, right))
        width, start, suffix = len(records[0][0]), int(records[0][0]), int(records[0][2])
        step = int(records[1][2]) - suffix
        if step <= 0:
            return None
        modulus = next(int(records[i-1][2]) + step - int(records[i][2]) for i in range(1, len(records)) if int(records[i][2]) != int(records[i-1][2]) + step)
        if modulus <= 0:
            return None
        for i, (left, _, right) in enumerate(records):
            if left != str(start+i).zfill(width).encode() or right != str((suffix+i*step)%modulus).encode():
                return None
    except (ValueError, StopIteration):
        return None
    texts = [r[1] for r in records]
    templates = [collections.Counter(texts[i::6]).most_common(1)[0][0] for i in range(6)]
    flags = bytes(text != templates[i%6] for i, text in enumerate(texts))
    exceptions = [text.split(b' ') for i, text in enumerate(texts) if flags[i]]
    if any(not 3 <= len(words) <= 9 for words in exceptions):
        return None
    vocab = [w for w, _ in collections.Counter(w for words in exceptions for w in words).most_common()]
    if len(vocab) != 7:
        return None
    ids = {w:i for i,w in enumerate(vocab)}
    lengths = bytes(len(words)-3 for words in exceptions)
    seq = bytes(ids[w] for words in exceptions for w in words)
    bits = bytearray((len(flags)+7)//8)
    for i,f in enumerate(flags):
        bits[i//8] |= f << (7-i%8)
    meta = json.dumps([len(lines), width, start, suffix, step, modulus, [t.decode('latin1') for t in templates], [w.decode('latin1') for w in vocab]], separators=(',', ':')).encode()
    meta, flagdata = zlib.compress(meta, 9), zlib.compress(bits, 9)
    if len(meta) > 65535 or len(flagdata) > 65535:
        return None
    return b'R1' + struct.pack('>HH', len(meta), len(flagdata)) + meta + flagdata + bz2.compress(lengths+seq, 9)


def restore(data):
    m, f = struct.unpack('>HH', data[2:6])
    n, width, start, suffix, step, modulus, templates, vocab = json.loads(zlib.decompress(data[6:6+m]))
    templates = [x.encode('latin1') for x in templates]
    vocab = [x.encode('latin1') for x in vocab]
    flags = zlib.decompress(data[6+m:6+m+f])
    coded = bz2.decompress(data[6+m+f:])
    count = sum(x.bit_count() for x in flags)
    lengths, seq = coded[:count], coded[count:]
    result = bytearray()
    j = k = 0
    for i in range(n):
        if flags[i//8] & (128 >> (i%8)):
            length = lengths[j] + 3
            text = b' '.join(vocab[x] for x in seq[k:k+length])
            j += 1
            k += length
        else:
            text = templates[i%6]
        result += str(start+i).zfill(width).encode()+b' '+text+b' '+str((suffix+i*step)%modulus).encode()+b'\n'
    return bytes(result)


def main():
    args = sys.argv[1:]
    if len(args) == 2:
        source, dest = args
        with open(source, 'rb') as f: data = f.read()
        output = transform(data)
        if output is None: output = b'L1' + lzma.compress(data, preset=9)
    elif len(args) == 3 and args[0] == '--decompress':
        _, source, dest = args
        with open(source, 'rb') as f: data = f.read()
        if data[:2] == b'R1': output = restore(data)
        elif data[:2] == b'L1': output = lzma.decompress(data[2:])
        else: raise ValueError('unrecognized compressed format')
    else:
        raise SystemExit('usage: compress.py [--decompress] SOURCE DEST')
    with open(dest, 'wb') as f: f.write(output)

if __name__ == '__main__': main()
