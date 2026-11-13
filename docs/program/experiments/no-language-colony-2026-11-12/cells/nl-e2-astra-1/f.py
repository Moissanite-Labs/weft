import lzma
import re

def _var(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return bytes(out)

def _read(d, p):
    n = shift = 0
    while True:
        b = d[p]
        p += 1
        n |= (b & 127) << shift
        if b < 128:
            return n, p
        shift += 7

def _textpack(d):
    layout = bytearray()
    nums = bytearray()
    p = 0
    for m in re.finditer(b'[0-9]{1,100}', d):
        literal = d[p:m.start()]
        digits = m.group()
        layout += _var(len(literal)) + literal + _var(len(digits))
        nums += int(digits).to_bytes(((10 ** len(digits) - 1).bit_length() + 7) // 8, 'big')
        p = m.end()
    layout += _var(len(d) - p) + d[p:] + _var(0)
    a = lzma.compress(bytes(layout), preset=9)
    b = lzma.compress(bytes(nums), preset=9)
    return _var(len(a)) + a + b

def _textunpack(d):
    n, p = _read(d, 0)
    layout = lzma.decompress(d[p:p+n])
    nums = lzma.decompress(d[p+n:])
    out = bytearray()
    p = q = 0
    while p < len(layout):
        n, p = _read(layout, p)
        out += layout[p:p+n]
        p += n
        n, p = _read(layout, p)
        if n:
            size = ((10 ** n - 1).bit_length() + 7) // 8
            out += str(int.from_bytes(nums[q:q+size], 'big')).zfill(n).encode('ascii')
            q += size
    return bytes(out)

def _textenc(d):
    return min((b'\x00' + lzma.compress(d, preset=9), b'\x01' + _textpack(d)), key=len)

def _textdec(d):
    return lzma.decompress(d[1:]) if d[0] == 0 else _textunpack(d[1:])

def _transform(d):
    meta = bytearray()
    streams = [bytearray() for _ in range(3)]
    for line in d.split(b'\n'):
        n = len(line)
        if n and n % 2 == 0 and re.fullmatch(b'[0-9a-f]+', line):
            k = 1
            b = bytes.fromhex(line.decode('ascii'))
        elif n and n <= 4096 and re.fullmatch(b'[0-9a-z]+', line):
            k = 2
            b = int(line, 36).to_bytes(((36 ** n - 1).bit_length() + 7) // 8, 'big')
        else:
            k = 0
            b = line
        meta += _var(n * 3 + k)
        streams[k] += b
    parts = [lzma.compress(bytes(meta), preset=9), _textenc(bytes(streams[0])), bytes(streams[1]), bytes(streams[2])]
    return b''.join(_var(len(p)) + p for p in parts)

def _inverse(d):
    parts = []
    p = 0
    for _ in range(4):
        n, p = _read(d, p)
        parts.append(d[p:p+n])
        p += n
    meta = lzma.decompress(parts[0])
    streams = [_textdec(parts[1]), parts[2], parts[3]]
    offsets = [0, 0, 0]
    out = []
    p = 0
    alphabet = b'0123456789abcdefghijklmnopqrstuvwxyz'
    while p < len(meta):
        v, p = _read(meta, p)
        n, k = divmod(v, 3)
        size = n if k == 0 else n // 2 if k == 1 else ((36 ** n - 1).bit_length() + 7) // 8
        b = streams[k][offsets[k]:offsets[k]+size]
        offsets[k] += size
        if k == 1:
            b = b.hex().encode('ascii')
        elif k == 2:
            v = int.from_bytes(b, 'big')
            b = bytearray(n)
            for i in range(n-1, -1, -1):
                v, r = divmod(v, 36)
                b[i] = alphabet[r]
            b = bytes(b)
        out.append(b)
    return b'\n'.join(out)

def enc(d):
    if not d:
        return b''
    candidates = [b'\x00' + d, b'\x01' + lzma.compress(d, preset=9), b'\x02' + _transform(d)]
    return min(candidates, key=len)

def dec(z):
    if not z:
        return b''
    if z[0] == 0:
        return z[1:]
    if z[0] == 1:
        return lzma.decompress(z[1:])
    return _inverse(z[1:])
