"""Reversible record preprocessing. All learned text is stored in the archive."""
import collections
import json
import re
import struct


def prepare(data, layout=0):
    lines = data.splitlines(keepends=True)
    records = []
    for i, line in enumerate(lines):
        m = re.fullmatch(rb'(\d+) (.*) (\d+)\n', line)
        if m is None or m[1] != ('%05d' % i).encode():
            return None
        records.append((m[2], int(m[3])))
    if len(records) < 2:
        return None
    modulus = max(n for _, n in records) + 1
    step = records[1][1]
    if any(n != i * step % modulus for i, (_, n) in enumerate(records)):
        return None
    templates = [collections.Counter(s for s, _ in records[k::6]).most_common(1)[0][0] for k in range(6)]
    vocab = sorted({w for i, (s, _) in enumerate(records) if s != templates[i % 6] for w in s.split(b' ')})
    if len(vocab) > 255:
        return None
    ids = {w: i for i, w in enumerate(vocab)}
    lengths = bytearray()
    words = bytearray()
    merged = bytearray()
    for i, (s, _) in enumerate(records):
        tokens = [] if s == templates[i % 6] else [ids[w] for w in s.split(b' ')]
        if len(tokens) > 255:
            return None
        lengths.append(len(tokens))
        words.extend(tokens)
        merged.append(len(tokens))
        merged.extend(tokens)
    meta = [len(lines), step, modulus, [s.decode('latin1') for s in templates], [s.decode('latin1') for s in vocab], layout]
    header = json.dumps(meta, ensure_ascii=True, separators=(',', ':')).encode()
    return struct.pack('<I', len(header)) + header + (bytes(lengths + words) if layout == 0 else bytes(merged))


def restore(data):
    size, = struct.unpack_from('<I', data)
    n, step, modulus, templates, vocab, layout = json.loads(data[4:4+size])
    templates = [s.encode('latin1') for s in templates]
    vocab = [s.encode('latin1') for s in vocab]
    stream = data[4+size:]
    result = []
    pos = n if layout == 0 else 0
    for i in range(n):
        if layout == 0:
            length = stream[i]
        else:
            length = stream[pos]
            pos += 1
        text = b' '.join(vocab[w] for w in stream[pos:pos+length]) if length else templates[i % 6]
        pos += length
        result.append(('%05d ' % i).encode() + text + (' %d\n' % (i * step % modulus)).encode())
    if pos != len(stream):
        raise ValueError('trailing bytes')
    return b''.join(result)
