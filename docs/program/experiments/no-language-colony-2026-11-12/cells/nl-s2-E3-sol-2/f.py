# A self-describing, lossless coding for the three record types.
_HEX = b'0123456789abcdef'
_DIG = b'0123456789abcdefghijklmnopqrstuvwxyz'
_MARK = b'\xffEXOcodec'
_HEAD = b'e18a line '
_MID = b' ratio '
_END = b' select pick win seed '


def enc(x):
    if not isinstance(x, bytes):
        x = bytes(x)
    # No overhead at all for unrecognized inputs, including one-byte inputs.
    # Prefix-stuff only inputs that might be confused with a coded stream.
    raw = b'\x00' + x if x.lstrip(b'\x00').startswith(_MARK) else x
    records = x.split(b'\n')
    if records[-1] != b'':
        return raw
    out = bytearray()
    for line in records[:-1]:
        if line.startswith(_HEAD):
            try:
                fields = line[len(_HEAD):].split(_MID)
                if len(fields) != 2:
                    raise ValueError()
                tail = fields[1].split(_END)
                if len(tail) != 2:
                    raise ValueError()
                a, b, c = fields[0], tail[0], tail[1]
                if not (a and b and c and len(b) == 8 and b[:2] == b'0.' and
                        all(48 <= v <= 57 for v in a+b[2:]+c)):
                    raise ValueError()
                ai, bi, ci = int(a), int(b[2:]), int(c)
                if (str(ai).encode(), str(bi).encode().zfill(6), str(ci).encode()) != (a, b[2:], c):
                    raise ValueError()
                out.append(0)
                out.extend(ai.to_bytes(3, 'big'))
                out.extend(bi.to_bytes(3, 'big'))
                out.extend(ci.to_bytes(4, 'big'))
                continue
            except (ValueError, OverflowError):
                pass
        if len(line) == 96 and all(v in _HEX for v in line):
            out.append(1)
            out.extend(bytes.fromhex(line.decode('ascii')))
        elif len(line) == 64 and all(v in _DIG for v in line):
            out.append(2)
            out.extend(int(line, 36).to_bytes(42, 'big'))
        else:
            return raw
    packed = _MARK + bytes(out)
    if len(packed) >= len(raw):
        return raw
    return packed


def dec(data):
    if data.lstrip(b'\x00').startswith(_MARK) and data[:1] == b'\x00':
        return data[1:]
    if not data.startswith(_MARK):
        return data
    result = bytearray()
    i = len(_MARK)
    while i < len(data):
        tag = data[i]
        i += 1
        if tag == 0:
            ai = int.from_bytes(data[i:i+3], 'big')
            bi = int.from_bytes(data[i+3:i+6], 'big')
            ci = int.from_bytes(data[i+6:i+10], 'big')
            i += 10
            result.extend(_HEAD + str(ai).encode() + _MID + b'0.' + str(bi).encode().zfill(6) + _END + str(ci).encode() + b'\n')
        elif tag == 1:
            result.extend(data[i:i+48].hex().encode()+b'\n')
            i += 48
        elif tag == 2:
            n = int.from_bytes(data[i:i+42], 'big')
            i += 42
            chars = bytearray(64)
            for j in range(63, -1, -1):
                n, v = divmod(n, 36)
                chars[j] = _DIG[v]
            result.extend(chars+b'\n')
        else:
            raise ValueError('invalid tag')
    return bytes(result)
