"""Lossless byte-string compression using Python's standard library."""
import bz2
import lzma


def enc(data):
    if not isinstance(data, bytes):
        data = bytes(data)
    a = bz2.compress(data, compresslevel=9)
    b = lzma.compress(data, preset=9)
    candidates = [(len(data), data), (len(a), a), (len(b), b)]
    return min(candidates, key=lambda item: item[0])[1]


def dec(data):
    for decompress in (bz2.decompress, lzma.decompress):
        try:
            return decompress(data)
        except (OSError, EOFError, ValueError):
            pass
    return data


encode = enc
decode = dec
