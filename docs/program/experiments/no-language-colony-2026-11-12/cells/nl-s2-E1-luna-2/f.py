#!/usr/bin/env python3
"""Small lossless binary codec.  The one-byte tag makes decoding unambiguous."""
import sys
import zlib
import bz2
import lzma

_RAW = b"R"
_CODECS = ((b"Z", zlib.compress, zlib.decompress),
           (b"B", bz2.compress, bz2.decompress),
           (b"L", lzma.compress, lzma.decompress))

def enc(data):
    data = bytes(data)
    best = (_RAW + data)
    for tag, compressor, _ in _CODECS:
        packed = tag + compressor(data)
        if len(packed) < len(best):
            best = packed
    return best

def dec(data):
    data = bytes(data)
    if not data:
        raise ValueError("missing codec tag")
    tag, payload = data[:1], data[1:]
    if tag == _RAW:
        return payload
    for codec_tag, _, decompressor in _CODECS:
        if tag == codec_tag:
            return decompressor(payload)
    raise ValueError("unknown codec tag")

# Friendly aliases for callers that use the specification's names.
encode = enc
decode = dec

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("enc", "dec"):
        raise SystemExit("usage: f.py enc|dec")
    src = sys.stdin.buffer.read()
    sys.stdout.buffer.write(enc(src) if sys.argv[1] == "enc" else dec(src))
