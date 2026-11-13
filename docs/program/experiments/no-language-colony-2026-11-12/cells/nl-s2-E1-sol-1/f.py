import zlib

def enc(x):
    return zlib.compress(x,9)

def dec(x):
    return zlib.decompress(x)
