import lzma

def enc(d):
    if not d:
        return b''
    z = lzma.compress(d, preset=9)
    return b'\x01' + z if len(z) < len(d) else b'\x00' + d

def dec(z):
    if not z:
        return b''
    if z[0] == 0:
        return z[1:]
    if z[0] == 1:
        return lzma.decompress(z[1:])
    raise ValueError('Invalid encoding')
