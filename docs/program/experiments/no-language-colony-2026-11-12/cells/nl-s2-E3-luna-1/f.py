import zlib, bz2, lzma

_ESCAPE = b'\x00RAW\xff'

def _unpack(data):
    # Streams emitted by the compressors below are self-identifying.
    try:
        if data.startswith(b'BZh'):
            return bz2.decompress(data)
        if data.startswith(b'\xfd7zXZ\x00'):
            return lzma.decompress(data)
        if len(data) >= 2:
            cmf, flg = data[0], data[1]
            if (cmf & 15) == 8 and (cmf >> 4) <= 7 and ((cmf << 8) + flg) % 31 == 0:
                return zlib.decompress(data)
    except Exception:
        pass
    return None

def enc(x):
    x = bytes(x)
    raw = _ESCAPE + x if x.startswith(_ESCAPE) or _unpack(x) is not None else x
    best = raw
    for fn in (zlib.compress, bz2.compress, lzma.compress):
        try:
            c = fn(x)
            if len(c) < len(best):
                best = c
        except Exception:
            pass
    return best

def dec(data):
    data = bytes(data)
    if data.startswith(_ESCAPE):
        return data[len(_ESCAPE):]
    x = _unpack(data)
    return data if x is None else x

encode = enc
decode = dec
