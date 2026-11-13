import lzma
import re

_HEX = re.compile(rb'[0-9a-f]+\Z')
_B36 = re.compile(rb'[a-z0-9]+\Z')


def _putvar(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    out.append(n)
    return out


def _getvar(data, pos):
    n = shift = 0
    while True:
        b = data[pos]
        pos += 1
        n |= (b & 127) << shift
        if not b & 128:
            return n, pos
        shift += 7


def _transform(data):
    out = bytearray()
    parts = data.split(b'\n')
    terminated = data.endswith(b'\n')
    if terminated:
        parts.pop()
    for body in parts:
        if _HEX.fullmatch(body) and len(body) % 2 == 0:
            typ = 1
            payload = bytes.fromhex(body.decode('ascii'))
        elif _B36.fullmatch(body):
            typ = 2
            n = int(body, 36)
            payload = n.to_bytes((n.bit_length() + 7) // 8, 'big')
            payload = _putvar(len(payload)) + payload
        else:
            typ = 0
            payload = body
        out.append(typ)
        out += _putvar(len(body))
        out += _putvar(len(payload))
        out += payload
    out += b'\xff' + bytes((terminated,))
    return bytes(out)


def _inverse(data):
    bodies = []
    pos = 0
    terminated = False
    while pos < len(data):
        typ = data[pos]
        pos += 1
        if typ == 255:
            terminated = bool(data[pos])
            pos += 1
            if pos != len(data):
                raise ValueError('trailing data')
            break
        length, pos = _getvar(data, pos)
        plen, pos = _getvar(data, pos)
        payload = data[pos:pos + plen]
        pos += plen
        if len(payload) != plen:
            raise ValueError('truncated data')
        if typ == 0:
            body = payload
        elif typ == 1:
            body = payload.hex().encode('ascii')
        elif typ == 2:
            sz, q = _getvar(payload, 0)
            num = int.from_bytes(payload[q:q + sz], 'big')
            chars = []
            while num:
                num, r = divmod(num, 36)
                chars.append('0123456789abcdefghijklmnopqrstuvwxyz'[r])
            body = ''.join(reversed(chars)).rjust(length, '0').encode('ascii')
        else:
            raise ValueError('bad token')
        if len(body) != length:
            raise ValueError('bad length')
        bodies.append(body)
    else:
        raise ValueError('missing end marker')
    return b'\n'.join(bodies) + (b'\n' if terminated else b'')


def enc(data):
    packed = lzma.compress(_transform(data), format=lzma.FORMAT_ALONE, preset=5)
    if len(packed) < len(data):
        return b'\x00' + packed
    return b'\x01' + data


def dec(data):
    if not data:
        return data
    if data[0] == 0:
        return _inverse(lzma.decompress(data[1:]))
    if data[0] == 1:
        return data[1:]
    return data
