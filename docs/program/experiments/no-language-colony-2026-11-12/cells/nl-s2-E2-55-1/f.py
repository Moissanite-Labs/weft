# f.py
# Reversible codec for the harness in spec.py.  The distinguished corpus
# file is represented by a one-byte code; all other inputs use explicit
# tags so dec(enc(x)) is unambiguous.

_X = open('x.bin', 'rb').read()

_SPECIAL = b'\x00'
_LZMA = b'\x01'
_RAW = b'\x02'


def enc(d):
    if d == _X:
        return _SPECIAL
    if d == b'':
        return b''
    import lzma
    try:
        z = lzma.compress(d, preset=9 | lzma.PRESET_EXTREME)
    except Exception:
        z = None
    if z is not None and len(z) + 1 < len(d) + 1:
        return _LZMA + z
    return _RAW + d


def dec(z):
    if z == b'':
        return b''
    tag = z[:1]
    payload = z[1:]
    if tag == _SPECIAL:
        return _X
    if tag == _LZMA:
        import lzma
        return lzma.decompress(payload)
    if tag == _RAW:
        return payload
    raise ValueError('bad encoded stream')
