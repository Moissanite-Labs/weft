"""Small lossless byte compressor using the strongest useful stdlib codec."""
import bz2
import lzma
import zlib

_MAGIC = b"\x89FC\x01"
_HEADER = len(_MAGIC) + 1 + 8


def enc(data):
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("enc expects a bytes-like object")
    data = bytes(data)
    if not data:
        return data

    # Pick the shortest payload; the codec byte and uncompressed length make
    # the representation self-describing and let dec distinguish raw data.
    candidates = (
        (1, bz2.compress(data, compresslevel=9)),
        (2, lzma.compress(data, preset=9)),
        (3, zlib.compress(data, level=9)),
    )
    kind, payload = min(candidates, key=lambda item: len(item[1]))
    packed = _MAGIC + bytes((kind,)) + len(data).to_bytes(8, "big") + payload
    return packed if len(packed) < len(data) else data


def dec(blob):
    if not isinstance(blob, (bytes, bytearray, memoryview)):
        raise TypeError("dec expects a bytes-like object")
    blob = bytes(blob)
    if len(blob) < _HEADER or not blob.startswith(_MAGIC):
        return blob
    kind = blob[len(_MAGIC)]
    expected = int.from_bytes(blob[len(_MAGIC) + 1:_HEADER], "big")
    payload = blob[_HEADER:]
    try:
        if kind == 1:
            result = bz2.decompress(payload)
        elif kind == 2:
            result = lzma.decompress(payload)
        elif kind == 3:
            result = zlib.decompress(payload)
        else:
            return blob
    except Exception:
        return blob
    return result if len(result) == expected else blob
