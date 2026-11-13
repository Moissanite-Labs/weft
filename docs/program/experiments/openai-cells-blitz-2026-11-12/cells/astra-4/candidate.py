"""Reversible table transform; inferred parameters are stored, never assumed."""
import collections
import json


def encode(data):
    if not data.endswith(b'\n'):
        raise ValueError('Not a newline-terminated table')
    rows = [line.split(b' ') for line in data[:-1].split(b'\n')]
    if len(rows) < 2 or any(len(row) < 3 for row in rows):
        raise ValueError('Not a numbered table')
    n = len(rows)
    start = int(rows[0][0])
    width = len(rows[0][0])
    if any(row[0] != str(start + i).zfill(width).encode() for i, row in enumerate(rows)):
        raise ValueError('Nonsequential first column')
    nums = [int(row[-1]) for row in rows]
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus
    if any(row[-1] != str((nums[0] + i * step) % modulus).encode() for i, row in enumerate(rows)):
        raise ValueError('Nonperiodic last column')
    bodies = [b' '.join(row[1:-1]) for row in rows]
    best = None
    for period in range(1, min(n, 32) + 1):
        templates = [collections.Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        cost = sum(len(t) + 4 for t in templates) + sum(len(b) + 1 for i, b in enumerate(bodies) if b != templates[i % period])
        if best is None or cost < best[0]:
            best = cost, templates
    templates = best[1]
    exceptions = [b.split(b' ') for i, b in enumerate(bodies) if b != templates[i % len(templates)]]
    dictionary = sorted({w for row in exceptions for w in row})
    if len(dictionary) > 256 or any(len(row) > 255 for row in exceptions):
        raise ValueError('Dictionary too large')
    ids = {w: i for i, w in enumerate(dictionary)}
    flags = bytearray((n + 7) // 8)
    for i, b in enumerate(bodies):
        if b != templates[i % len(templates)]:
            flags[i // 8] |= 1 << (i % 8)
    lengths = bytes(len(row) for row in exceptions)
    words = bytes(ids[w] for row in exceptions for w in row)
    # Latin-1 provides a reversible JSON representation of arbitrary byte strings.
    header = [n, start, width, nums[0], step, modulus,
              [t.decode('latin1') for t in templates],
              [w.decode('latin1') for w in dictionary]]
    return json.dumps(header, ensure_ascii=True, separators=(',', ':')).encode() + b'\n' + flags + lengths + words


def decode(data):
    header, payload = data.split(b'\n', 1)
    n, start, width, initial, step, modulus, templates, dictionary = json.loads(header)
    templates = [t.encode('latin1') for t in templates]
    dictionary = [w.encode('latin1') for w in dictionary]
    flaglen = (n + 7) // 8
    flags = payload[:flaglen]
    count = sum(x.bit_count() for x in flags)
    lengths = iter(payload[flaglen:flaglen + count])
    words = iter(payload[flaglen + count:])
    result = []
    for i in range(n):
        if flags[i // 8] & (1 << (i % 8)):
            body = b' '.join(dictionary[next(words)] for _ in range(next(lengths)))
        else:
            body = templates[i % len(templates)]
        result.append(str(start + i).zfill(width).encode() + b' ' + body + b' ' + str((initial + i * step) % modulus).encode() + b'\n')
    return b''.join(result)

import bz2
import math
import zlib
import pathlib
import sys

def pack_digits(values, base):
    rank = 0
    for value in reversed(values):
        rank = rank * base + value
    size = ((base ** len(values) - 1).bit_length() + 7) // 8
    return rank.to_bytes(size, 'little')

def unpack_digits(data, base, n):
    size = ((base ** n - 1).bit_length() + 7) // 8
    rank = int.from_bytes(data[:size], 'little')
    values = []
    for _ in range(n):
        rank, digit = divmod(rank, base)
        values.append(digit)
    return bytes(values), data[size:]

def compact(data):
    h, p = data.split(b'\n', 1)
    header = json.loads(h)
    n = header[0]
    flags, p = p[:(n+7)//8], p[(n+7)//8:]
    k = sum(v.bit_count() for v in flags)
    lengths, words = p[:k], p[k:]
    lo, hi = min(lengths, default=0), max(lengths, default=0)
    h = zlib.compress(json.dumps(header + [k,lo,hi], separators=(',', ':')).encode(), 9)
    total = math.comb(n,k)
    size = ((total-1).bit_length()+7)//8
    rank, remaining = 0,k
    for i in range(n):
        zeros = total*(n-i-remaining)//(n-i)
        if flags[i//8] & (1<<(i%8)):
            rank += zeros
            total -= zeros
            remaining -= 1
        else:
            total = zeros
    return len(h).to_bytes(4,'little') + h + rank.to_bytes(size,'little') + pack_digits([v-lo for v in lengths],hi-lo+1) + pack_digits(words,len(header[7]))

def expand(data):
    size = int.from_bytes(data[:4],'little')
    header = json.loads(zlib.decompress(data[4:4+size]))
    p = data[4+size:]
    n = header[0]
    k,lo,hi = header[-3:]
    header = header[:-3]
    total = math.comb(n,k)
    size = ((total-1).bit_length()+7)//8
    rank = int.from_bytes(p[:size],'little')
    lengths,p = unpack_digits(p[size:],hi-lo+1,k)
    lengths = bytes(v+lo for v in lengths)
    words,p = unpack_digits(p,len(header[7]),sum(lengths))
    flags = bytearray((n+7)//8)
    remaining = k
    for i in range(n):
        zeros = total*(n-i-remaining)//(n-i)
        if rank >= zeros:
            flags[i//8] |= 1<<(i%8)
            rank -= zeros
            total -= zeros
            remaining -= 1
        else:
            total = zeros
    return json.dumps(header,separators=(',',':')).encode()+b'\n'+flags+lengths+words

def compress(data):
    plain = b'BC1'+bz2.compress(data)
    try:
        packed = compact(encode(data))
        if decode(expand(packed)) == data and len(packed)+3 < len(plain):
            return b'EC1'+packed
    except (ValueError,ZeroDivisionError,IndexError,OverflowError):
        pass
    return plain

def decompress(data):
    if data[:3] == b'BC1':
        return bz2.decompress(data[3:])
    if data[:3] == b'EC1':
        return decode(expand(data[3:]))
    raise ValueError('Unknown format')

def main():
    args=sys.argv[1:]
    decoding=bool(args and args[0]=='--decompress')
    if decoding: args=args[1:]
    if len(args)!=2: raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data=pathlib.Path(args[0]).read_bytes()
    pathlib.Path(args[1]).write_bytes(decompress(data) if decoding else compress(data))

if __name__=='__main__':main()
