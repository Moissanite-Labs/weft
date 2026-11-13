import bz2
import lzma
import re
import zlib

_HEX = re.compile(b'[0-9a-f]{16,4096}')
_BASE36 = re.compile(b'[0-9a-z]{16,4096}')
_ALPHABET = b'0123456789abcdefghijklmnopqrstuvwxyz'

def _put(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out

def _get(d, p):
    n = shift = 0
    while True:
        b = d[p]
        p += 1
        n |= (b & 127) << shift
        if b < 128:
            return n, p
        shift += 7

def _pack(d):
    lines = d.split(b'\n')
    meta = _put(len(lines))
    streams = [bytearray(), bytearray(), bytearray()]
    for line in lines:
        n = len(line)
        if n % 2 == 0 and _HEX.fullmatch(line):
            kind = 1
            packed = bytes.fromhex(line.decode('ascii'))
        elif _BASE36.fullmatch(line):
            kind = 2
            size = ((36 ** n - 1).bit_length() + 7) // 8
            packed = int(line, 36).to_bytes(size, 'big')
        else:
            kind = 0
            packed = line
        meta.extend(_put(n * 3 + kind))
        streams[kind].extend(packed)
    return bytes(_put(len(meta)) + _put(len(streams[0])) + _put(len(streams[1])) + meta + streams[0] + streams[1] + streams[2])

def _unpack(d):
    m, p = _get(d, 0)
    a, p = _get(d, p)
    b, p = _get(d, p)
    pos = [p + m, p + m + a, p + m + a + b]
    count, p = _get(d, p)
    lines = []
    for _ in range(count):
        tag, p = _get(d, p)
        n, kind = divmod(tag, 3)
        size = n if kind == 0 else n // 2 if kind == 1 else ((36 ** n - 1).bit_length() + 7) // 8
        raw = d[pos[kind]:pos[kind] + size]
        pos[kind] += size
        if kind == 0:
            line = raw
        elif kind == 1:
            line = raw.hex().encode('ascii')
        else:
            num = int.from_bytes(raw, 'big')
            buf = bytearray(b'0' * n)
            for i in range(n - 1, -1, -1):
                num, digit = divmod(num, 36)
                buf[i] = _ALPHABET[digit]
            line = bytes(buf)
        lines.append(line)
    return b'\n'.join(lines)

def enc(d):
    d = bytes(d)
    if not d:
        return b''
    candidates = [b'\x00' + d]
    for transformed, data in enumerate((d, _pack(d))):
        for method, compress in enumerate((lzma.compress, bz2.compress, zlib.compress)):
            candidates.append(bytes([1 + transformed * 3 + method]) + compress(data))
    return min(candidates, key=len)

def dec(z):
    if not z:
        return b''
    tag = z[0]
    if tag == 0:
        return z[1:]
    if not 1 <= tag <= 6:
        raise ValueError('invalid encoding')
    transformed, method = divmod(tag - 1, 3)
    data = (lzma.decompress, bz2.decompress, zlib.decompress)[method](z[1:])
    return _unpack(data) if transformed else data
