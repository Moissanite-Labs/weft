"""Lossless stdlib codec: radix packing for structured text, BZ2 fallback.

The structured format stores line kinds, a shared text prefix, hexadecimal
bytes, base-36 integers, and decimal fields. No source data is needed to decode.
"""
import bz2
import re
import struct
import sys

MAGIC = b'RC1'
RECORD = re.compile(rb'(.*?) line (0|[1-9][0-9]{0,5}) ratio 0\.([0-9]{6}) select pick win seed (0|[1-9][0-9]{0,8})')
HEX = re.compile(rb'[0-9a-f]{96}')
BASE36 = re.compile(rb'[0-9a-z]{64}')
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def pack(values, radix):
    value = 0
    for digit in values:
        value = value * radix + digit
    size = ((radix ** len(values) - 1).bit_length() + 7) // 8
    return value.to_bytes(size, 'big')


def unpack(data, offset, count, radix):
    size = ((radix ** count - 1).bit_length() + 7) // 8
    if offset + size > len(data):
        raise ValueError('truncated stream')
    value = int.from_bytes(data[offset:offset + size], 'big')
    values = [0] * count
    for i in range(count - 1, -1, -1):
        value, values[i] = divmod(value, radix)
    if value:
        raise ValueError('invalid radix stream')
    return values, offset + size


def pack_kinds(kinds):
    # Prefix codes: template=0, hexadecimal=10, base36=11.
    value = 0
    bits = 0
    for kind in kinds:
        if kind == 2:
            value <<= 1
            bits += 1
        else:
            value = (value << 2) | (2 + kind)
            bits += 2
    padding = (-bits) % 8
    return (value << padding).to_bytes((bits + 7) // 8, 'big')


def unpack_kinds(data, offset, count):
    kinds = []
    bit = offset * 8
    for _ in range(count):
        first = (data[bit // 8] >> (7 - bit % 8)) & 1
        bit += 1
        if first:
            kinds.append((data[bit // 8] >> (7 - bit % 8)) & 1)
            bit += 1
        else:
            kinds.append(2)
    return kinds, (bit + 7) // 8


def structured(data):
    trailing = data.endswith(b'\n')
    lines = data[:-1].split(b'\n') if trailing else data.split(b'\n')
    kinds, hexes, words, numbers = [], [], [], []
    prefix = None
    for line in lines:
        if HEX.fullmatch(line):
            kinds.append(0)
            hexes.append(bytes.fromhex(line.decode('ascii')))
        elif BASE36.fullmatch(line):
            kinds.append(1)
            words.append(int(line, 36))
        else:
            m = RECORD.fullmatch(line)
            if m is None:
                return None
            p, a, b, c = m.groups()
            if prefix is None:
                prefix = p
            if p != prefix:
                return None
            kinds.append(2)
            numbers.append((int(a) * 1000000 + int(b)) * 1000000000 + int(c))
    prefix = prefix or b''
    if len(prefix) > 65535:
        return None
    return (struct.pack('>IBH', len(lines), trailing, len(prefix)) + prefix
            + pack_kinds(kinds) + b''.join(hexes)
            + pack(words, 36 ** 64) + pack(numbers, 10 ** 21))


def compress(data):
    candidates = [b'B' + bz2.compress(data, compresslevel=9), b'R' + data]
    packed = structured(data)
    if packed is not None:
        candidates.append(b'S' + packed)
    return MAGIC + min(candidates, key=len)


def decompress(data):
    if data[:3] != MAGIC:
        raise ValueError('unknown format')
    mode, data = data[3:4], data[4:]
    if mode == b'B':
        return bz2.decompress(data)
    if mode == b'R':
        return data
    if mode != b'S':
        raise ValueError('unknown codec')
    count, trailing, plen = struct.unpack('>IBH', data[:7])
    prefix = data[7:7 + plen]
    kinds, offset = unpack_kinds(data, 7 + plen, count)
    nh = kinds.count(0)
    hexes = [data[offset + i * 48:offset + (i + 1) * 48].hex().encode('ascii') for i in range(nh)]
    offset += 48 * nh
    words, offset = unpack(data, offset, kinds.count(1), 36 ** 64)
    numbers, offset = unpack(data, offset, kinds.count(2), 10 ** 21)
    if offset != len(data):
        raise ValueError('unexpected trailing data')
    decoded_words = []
    for value in words:
        word = bytearray(64)
        for i in range(63, -1, -1):
            value, digit = divmod(value, 36)
            word[i] = ALPHABET[digit]
        decoded_words.append(bytes(word))
    records = []
    for value in numbers:
        value, c = divmod(value, 1000000000)
        a, b = divmod(value, 1000000)
        records.append(prefix + (' line %d ratio 0.%06d select pick win seed %d' % (a, b, c)).encode('ascii'))
    streams = [iter(hexes), iter(decoded_words), iter(records)]
    return b'\n'.join(next(streams[k]) for k in kinds) + (b'\n' if trailing else b'')


def main():
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    main()
