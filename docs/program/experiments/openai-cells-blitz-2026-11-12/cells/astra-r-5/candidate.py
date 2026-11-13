import bz2,json,math,struct,zlib
from collections import Counter

def radix_size(base, count):
    return ((base ** count - 1).bit_length() + 7) // 8

def pack_digits(digits, base):
    value = 0
    for d in digits:
        value = value * base + d
    return value.to_bytes(radix_size(base, len(digits)), 'little')

def unpack_digits(data, base, count):
    size = radix_size(base, count)
    value = int.from_bytes(data[:size], 'little')
    result = [0] * count
    for i in range(count - 1, -1, -1):
        value, result[i] = divmod(value, base)
    return result, data[size:]

def pack_flags(flags):
    n, k = len(flags), sum(flags)
    total = math.comb(n, k)
    size = ((total-1).bit_length()+7)//8
    rank = 0
    for flag in flags:
        zeros = total * (n-k) // n
        if flag:
            rank += zeros
            total -= zeros
            k -= 1
        else:
            total = zeros
        n -= 1
    return rank.to_bytes(size, 'little')

def unpack_flags(data, n, k):
    total = math.comb(n, k)
    size = ((total-1).bit_length()+7)//8
    rank = int.from_bytes(data[:size], 'little')
    flags = []
    while n:
        zeros = total * (n-k) // n
        flag = int(rank >= zeros)
        flags.append(flag)
        if flag:
            rank -= zeros
            total -= zeros
            k -= 1
        else:
            total = zeros
        n -= 1
    return flags, data[size:]

def model(data):
    lines = data.splitlines()
    width = len(lines[0].split(b' ', 1)[0])
    bodies, numbers = [], []
    for i, line in enumerate(lines):
        index, rest = line.split(b' ', 1)
        if index != str(i).zfill(width).encode():
            raise ValueError('nonsequential')
        body, number = rest.rsplit(b' ', 1)
        bodies.append(body.decode('ascii'))
        numbers.append(int(number))
    step, modulus = numbers[1], max(numbers) + 1
    if numbers != [i * step % modulus for i in range(len(lines))]:
        raise ValueError('nonperiodic')
    options = []
    for period in range(1, min(12, len(lines)) + 1):
        common = [Counter(bodies[j::period]).most_common(1)[0] for j in range(period)]
        options.append((sum(n for _, n in common) - 20 * period, [s for s, _ in common]))
    _, templates = max(options)
    flags = [int(body != templates[i % len(templates)]) for i, body in enumerate(bodies)]
    exceptions = [body.split(' ') for body, flag in zip(bodies, flags) if flag]
    words = sorted(set(w for row in exceptions for w in row))
    ids = {w: i for i, w in enumerate(words)}
    lengths = [len(row) for row in exceptions]
    lo, hi = min(lengths, default=0), max(lengths, default=0)
    metadata = [len(lines), width, step, modulus, templates, words, lo, hi, len(lengths)]
    return metadata, flags, [n-lo for n in lengths], [ids[w] for row in exceptions for w in row]

def encode(data):
    meta, flags, lengths, tokens = model(data)
    header = zlib.compress(json.dumps(meta, separators=(',', ':')).encode(), 9)
    return (b'E1' + struct.pack('<H', len(header)) + header + pack_flags(flags)
            + pack_digits(lengths, meta[7]-meta[6]+1)
            + pack_digits(tokens, max(1, len(meta[5]))))

def decompress(data):
    if data[:2] == b'B1':
        return bz2.decompress(data[2:])
    if data[:2] != b'E1':
        raise ValueError('unrecognized compressed format')
    hs = struct.unpack_from('<H', data, 2)[0]
    n, width, step, modulus, templates, words, lo, hi, k = json.loads(zlib.decompress(data[4:4+hs]))
    flags, stream = unpack_flags(data[4+hs:], n, k)
    lengths, stream = unpack_digits(stream, hi-lo+1, k)
    lengths = [length+lo for length in lengths]
    tokens, stream = unpack_digits(stream, max(1, len(words)), sum(lengths))
    rows = []
    e = p = 0
    for i, flag in enumerate(flags):
        if flag:
            length = lengths[e]
            body = ' '.join(words[t] for t in tokens[p:p+length])
            e += 1
            p += length
        else:
            body = templates[i % len(templates)]
        rows.append(f'{i:0{width}d} {body} {i*step%modulus}\n')
    return ''.join(rows).encode('ascii')

def compress(data):
    raw = b'B1' + bz2.compress(data, 9)
    try:
        result = encode(data)
        if len(result) < len(raw) and decompress(result) == data:
            return result
    except (ValueError, IndexError, UnicodeError, OverflowError, ZeroDivisionError):
        pass
    return raw
