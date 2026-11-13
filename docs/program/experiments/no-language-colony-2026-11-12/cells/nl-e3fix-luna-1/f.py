import bz2
import lzma
import struct
import zlib

_RAW = 0
_ZLIB = 1
_BZ2 = 2
_LZMA = 3


def _hex_transform(data):
    """Pack long ASCII-hex lines and escape NULs in the remaining text."""
    chunks = data.splitlines(keepends=True)
    if not chunks:
        return None
    out = bytearray(b"HX1")
    packed = 0
    for chunk in chunks:
        if chunk.endswith(b"\n"):
            line, ending = chunk[:-1], b"\n"
            if line.endswith(b"\r"):
                line, ending = line[:-1], b"\r\n"
        elif chunk.endswith(b"\r"):
            line, ending = chunk[:-1], b"\r"
        else:
            line, ending = chunk, b""
        if (len(line) >= 32 and len(line) % 2 == 0 and
                len(line) // 2 <= 65535 and
                all(c in b"0123456789abcdefABCDEF" for c in line)):
            raw = bytes.fromhex(line.decode("ascii"))
            out.extend(b"\x00\x01")
            out.extend(struct.pack(">H", len(raw)))
            out.extend(raw)
            out.extend(ending)
            packed += 1
        else:
            out.extend(chunk.replace(b"\x00", b"\x00\x00"))
    return bytes(out) if packed else None


def _hex_inverse(data):
    if not data.startswith(b"HX1"):
        raise ValueError("invalid transformed data")
    pos = 3
    out = bytearray()
    while pos < len(data):
        if data[pos] != 0:
            out.append(data[pos])
            pos += 1
            continue
        if pos + 1 >= len(data):
            raise ValueError("truncated transformed data")
        tag = data[pos + 1]
        if tag == 0:
            out.append(0)
            pos += 2
        elif tag == 1:
            if pos + 4 > len(data):
                raise ValueError("truncated transformed data")
            n = struct.unpack(">H", data[pos + 2:pos + 4])[0]
            pos += 4
            if pos + n > len(data):
                raise ValueError("truncated transformed data")
            out.extend(data[pos:pos + n].hex().encode("ascii"))
            pos += n
            # A packed hex line is followed by its original line ending.
            if pos < len(data) and data[pos] == 13:
                out.extend(b"\r")
                pos += 1
                if pos < len(data) and data[pos] == 10:
                    out.extend(b"\n")
                    pos += 1
            elif pos < len(data) and data[pos] == 10:
                out.extend(b"\n")
                pos += 1
        else:
            raise ValueError("invalid transform escape")
    return bytes(out)


def _compressed(data):
    return (
        zlib.compress(data, 9),
        bz2.compress(data, compresslevel=9),
        lzma.compress(data, preset=9),
    )


def enc(data):
    """Encode nonempty bytes, choosing the smallest lossless representation."""
    data = bytes(data)
    if not data:
        raise ValueError("enc expects a nonempty byte string")

    best = bytes((_RAW,)) + data
    for tag, body in enumerate(_compressed(data), 1):
        candidate = bytes((tag,)) + body
        if len(candidate) < len(best):
            best = candidate

    transformed = _hex_transform(data)
    if transformed is not None:
        for tag, body in enumerate(_compressed(transformed), 4):
            candidate = bytes((tag,)) + body
            if len(candidate) < len(best):
                best = candidate
    return best


def dec(payload):
    """Inverse of enc."""
    payload = bytes(payload)
    if not payload:
        raise ValueError("invalid encoded data")
    tag, body = payload[0], payload[1:]
    if tag == _RAW:
        if not body:
            raise ValueError("invalid raw representation")
        return body
    if tag in (_ZLIB, 4):
        result = zlib.decompress(body)
    elif tag in (_BZ2, 5):
        result = bz2.decompress(body)
    elif tag in (_LZMA, 6):
        result = lzma.decompress(body)
    else:
        raise ValueError("unknown encoding")
    return _hex_inverse(result) if tag >= 4 else result
