"""Fixed-width packing for corpus record integers."""
WIDTHS = (70, 384, 331)


def pack(values):
    tags = bytearray((len(values) + 3) // 4)
    bits = 0
    buffer = 0
    result = bytearray()
    for index, (tag, value) in enumerate(values):
        width = WIDTHS[tag]
        if value >= 1 << width:
            raise ValueError('record too large')
        tags[index // 4] |= tag << ((index % 4) * 2)
        buffer = buffer << width | value
        bits += width
        while bits >= 8:
            bits -= 8
            result.append(buffer >> bits & 255)
            buffer &= (1 << bits) - 1
    if bits:
        result.append(buffer << (8 - bits))
    return bytes(tags) + result


def unpack(data, count):
    tagslen = (count + 3) // 4
    tags = data[:tagslen]
    payload = data[tagslen:]
    if len(tags) != tagslen:
        raise ValueError('truncated tags')
    buffer = 0
    bits = 0
    pos = 0
    for index in range(count):
        tag = tags[index // 4] >> (2 * (index % 4)) & 3
        if tag == 3:
            raise ValueError('invalid tag')
        width = WIDTHS[tag]
        while bits < width:
            if pos >= len(payload):
                raise ValueError('truncated record')
            buffer = buffer << 8 | payload[pos]
            pos += 1
            bits += 8
        bits -= width
        yield tag, buffer >> bits
        buffer &= (1 << bits) - 1
    if pos != len(payload) or buffer:
        raise ValueError('trailing data')
