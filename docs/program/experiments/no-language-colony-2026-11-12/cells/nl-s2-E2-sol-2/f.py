"""Lossless codec for structured records, with a general-purpose fallback."""
import re
import lzma
import bz2
import zlib

_H = re.compile(rb'e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)\Z')
_X = re.compile(rb'[0-9a-f]{96}\Z')
_B = re.compile(rb'[0-9a-z]{64}\Z')


def _transform(d):
    lines = d.split(b'\n')
    ended = lines[-1] == b''
    if ended:
        lines.pop()
    out = bytearray([ended])
    for line in lines:
        m = _H.fullmatch(line)
        if m:
            a, b, c = (int(t) for t in m.groups())
            if a < 1 << 20 and b < 1 << 20 and c < 1 << 30:
                out.append(0)
                out.extend(((a << 50) | (b << 30) | c).to_bytes(9, 'big'))
                continue
        if _X.fullmatch(line):
            out.append(1)
            out.extend(bytes.fromhex(line.decode('ascii')))
            continue
        if _B.fullmatch(line):
            out.append(2)
            out.extend(int(line, 36).to_bytes(42, 'big'))
            continue
        out.append(3)
        out.extend(len(line).to_bytes(4, 'big'))
        out.extend(line)
    return bytes(out)


def _untransform(d):
    ended = d[0]
    if ended not in (0, 1):
        raise ValueError('invalid records')
    p = 1
    lines = []
    while p < len(d):
        tag = d[p]
        p += 1
        if tag == 0:
            n = int.from_bytes(d[p:p+9], 'big')
            p += 9
            a, b, c = n >> 50, (n >> 30) & ((1 << 20)-1), n & ((1 << 30)-1)
            line = b'e18a line %d ratio 0.%06d select pick win seed %d' % (a, b, c)
        elif tag == 1:
            line = d[p:p+48].hex().encode()
            p += 48
        elif tag == 2:
            n = int.from_bytes(d[p:p+42], 'big')
            p += 42
            chars = bytearray(64)
            for j in range(63, -1, -1):
                n, rem = divmod(n, 36)
                chars[j] = b'0123456789abcdefghijklmnopqrstuvwxyz'[rem]
            line = bytes(chars)
        elif tag == 3:
            n = int.from_bytes(d[p:p+4], 'big')
            p += 4
            line = d[p:p+n]
            p += n
        else:
            raise ValueError('invalid record tag')
        lines.append(line)
    return b'\n'.join(lines) + (b'\n' if ended else b'')


def enc(d):
    transformed = _transform(d)
    choices = [b'R' + d,
               b'Z' + zlib.compress(transformed, 9),
               b'L' + lzma.compress(transformed, preset=9),
               b'B' + bz2.compress(transformed, compresslevel=9)]
    return min(choices, key=len)


def dec(z):
    tag, body = z[:1], z[1:]
    if tag == b'R':
        return body
    if tag == b'Z':
        return _untransform(zlib.decompress(body))
    if tag == b'L':
        return _untransform(lzma.decompress(body))
    if tag == b'B':
        return _untransform(bz2.decompress(body))
    raise ValueError('invalid encoding')
