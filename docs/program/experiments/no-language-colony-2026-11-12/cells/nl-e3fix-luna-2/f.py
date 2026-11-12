import bz2
import lzma
import zlib

# Wire format: one method byte followed by a raw or standard compressed stream.
_RAW, _ZLIB, _BZ2, _LZMA = range(4)


def enc(data):
    """Encode bytes losslessly, choosing the shortest available representation."""
    data = bytes(data)
    best = bytes((_RAW,)) + data
    best_len = len(best)
    for method, payload in (
        (_ZLIB, zlib.compress(data, 9)),
        (_BZ2, bz2.compress(data, compresslevel=9)),
        (_LZMA, lzma.compress(data, preset=6)),
    ):
        candidate_len = len(payload) + 1
        if candidate_len < best_len:
            best = bytes((method,)) + payload
            best_len = candidate_len
    return best


def dec(blob):
    """Decode an enc() result."""
    blob = bytes(blob)
    if not blob:
        raise ValueError("empty encoded stream")
    method, payload = blob[0], blob[1:]
    if method == _RAW:
        return payload
    if method == _ZLIB:
        return zlib.decompress(payload)
    if method == _BZ2:
        return bz2.decompress(payload)
    if method == _LZMA:
        return lzma.decompress(payload)
    raise ValueError("unknown encoding method")

encode = enc
decode = dec
