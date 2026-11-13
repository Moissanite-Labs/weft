import re
import bz2
import zlib

_H = re.compile(rb'e18a line (\d+) ratio 0\.(\d{6}) select pick win seed (\d+)\Z')
_X = re.compile(rb'[0-9a-f]{96}\Z')
_B = re.compile(rb'[0-9a-z]{64}\Z')
_A = b'0123456789abcdefghijklmnopqrstuvwxyz'


def _pack(d):
    lines = d.split(b'\n')
    if lines[-1] == b'':
        lines.pop()
        end = 1
    else:
        end = 0
    if len(lines) > 65535:
        return None
    types = bytearray((len(lines) + 3) // 4)
    parts = []
    for i, line in enumerate(lines):
        m = _H.fullmatch(line)
        if m:
            line_num, ratio, seed = map(int, m.groups())
            if (line_num >= 1 << 20 or ratio >= 1 << 20 or seed >= 1 << 30
                    or m.group(1) != str(line_num).encode()
                    or m.group(3) != str(seed).encode()):
                return None
            t = 0
            b = ((line_num << 50) | (ratio << 30) | seed).to_bytes(9, 'big')
        elif _X.fullmatch(line):
            t = 1
            b = bytes.fromhex(line.decode())
        elif _B.fullmatch(line):
            t = 2
            n = 0
            for c in line:
                n = n * 36 + _A.index(c)
            b = n.to_bytes(42, 'big')
        else:
            return None
        types[i // 4] |= t << (6 - 2 * (i % 4))
        parts.append(b)
    return len(lines).to_bytes(2, 'big') + bytes([end]) + types + b''.join(parts)


def _unpack(p):
    n = int.from_bytes(p[:2], 'big')
    end = p[2]
    types = p[3:3 + (n + 3) // 4]
    j = 3 + len(types)
    lines = []
    for i in range(n):
        t = (types[i // 4] >> (6 - 2 * (i % 4))) & 3
        if t == 0:
            val = int.from_bytes(p[j:j + 9], 'big')
            j += 9
            line_num, ratio, seed = val >> 50, (val >> 30) & ((1 << 20) - 1), val & ((1 << 30) - 1)
            line = b'e18a line %d ratio 0.%06d select pick win seed %d' % (line_num, ratio, seed)
        elif t == 1:
            line = p[j:j + 48].hex().encode()
            j += 48
        else:
            val = int.from_bytes(p[j:j + 42], 'big')
            j += 42
            chars = bytearray(64)
            for k in range(63, -1, -1):
                val, r = divmod(val, 36)
                chars[k] = _A[r]
            line = bytes(chars)
        lines.append(line)
    return b'\n'.join(lines) + (b'\n' if end else b'')


def enc(d):
    if not d:
        return b''
    candidates = [(len(d) + 1, b'\x00' + d)]
    p = _pack(d)
    if p is not None:
        candidates.append((len(p) + 1, b'\x01' + p))
    z = zlib.compress(d, 9)
    candidates.append((len(z) + 1, b'\x02' + z))
    return min(candidates)[1]


def dec(z):
    if not z:
        return b''
    if z[0] == 0:
        return z[1:]
    if z[0] == 1:
        return _unpack(z[1:])
    if z[0] == 2:
        return zlib.decompress(z[1:])
    raise ValueError('unknown format')
