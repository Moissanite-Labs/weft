#!/usr/bin/env python3
"""Compact lossless codec for a corpus of structured text and radix strings."""
import sys

PREFIX = b'e18a line '
MIDDLE = b' ratio 0.'
SUFFIX = b' select pick win seed '
ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'


def pack(data):
    ended = data.endswith(b'\n')
    lines = data.split(b'\n')
    if ended:
        lines.pop()
    tags = bytearray((len(lines) + 3) // 4)
    payload = bytearray()
    for i, line in enumerate(lines):
        if line.startswith(PREFIX) and SUFFIX in line:
            try:
                left, seed = line[len(PREFIX):].split(SUFFIX)
                number, fraction = left.split(MIDDLE)
                assert 1 <= len(number) <= 6 and len(fraction) == 6
                assert number.isdigit() and fraction.isdigit() and seed.isdigit()
                n, f, s = int(number), int(fraction), int(seed)
                assert n < 1000000 and s < 1000000000
                assert str(n).encode() == number and str(s).encode() == seed
                tag = 0
                payload += (n * 1000000000000000 + f * 1000000000 + s).to_bytes(9, 'big')
            except (ValueError, AssertionError, OverflowError):
                tag = 3
        elif len(line) == 96 and all(c in b'0123456789abcdef' for c in line):
            tag = 1
            payload += bytes.fromhex(line.decode())
        elif len(line) == 64 and all(c in ALPHABET for c in line):
            tag = 2
            payload += int(line, 36).to_bytes(42, 'big')
        else:
            tag = 3
        if tag == 3:
            payload += len(line).to_bytes(4, 'big') + line
        tags[i // 4] |= tag << ((i % 4) * 2)
    return b'CP01' + (len(lines) * 2 + ended).to_bytes(4, 'big') + tags + payload


def unpack(blob):
    if blob[:4] != b'CP01':
        raise ValueError('not a CP01 file')
    count_flag = int.from_bytes(blob[4:8], 'big')
    count, ended = divmod(count_flag, 2)
    tags = blob[8:8 + (count + 3) // 4]
    body = memoryview(blob)[8 + len(tags):]
    offset = 0
    lines = []
    for i in range(count):
        tag = (tags[i // 4] >> ((i % 4) * 2)) & 3
        if tag == 0:
            combined = int.from_bytes(body[offset:offset + 9], 'big')
            n, combined = divmod(combined, 1000000000000000)
            f, s = divmod(combined, 1000000000)
            line = PREFIX + str(n).encode() + MIDDLE + f'{f:06d}'.encode() + SUFFIX + str(s).encode()
            offset += 9
        elif tag == 1:
            line = body[offset:offset + 48].tobytes().hex().encode()
            offset += 48
        elif tag == 2:
            n = int.from_bytes(body[offset:offset + 42], 'big')
            chars = bytearray(64)
            for j in range(63, -1, -1):
                n, digit = divmod(n, 36)
                chars[j] = ALPHABET[digit]
            line = bytes(chars)
            offset += 42
        else:
            length = int.from_bytes(body[offset:offset + 4], 'big')
            offset += 4
            line = body[offset:offset + length].tobytes()
            offset += length
        lines.append(line)
    return b'\n'.join(lines) + (b'\n' if ended else b'')


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        src, dst = args[1:]
        output = unpack(open(src, 'rb').read())
    elif len(args) == 2:
        src, dst = args
        output = pack(open(src, 'rb').read())
    else:
        raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(dst, 'wb') as f:
        f.write(output)


if __name__ == '__main__':
    main()
