def enc(x):
    x = bytes(x)
    n = len(x)
    # LZ77 stream: one control byte per group of eight tokens.
    out = bytearray()
    chains = {}
    pos = 0
    while pos < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            best_len = 0
            best_dist = 0
            if pos + 3 <= n:
                key = x[pos:pos+3]
                cand = chains.get(key, ())
                max_len = min(65553, n-pos)
                # Newest candidates first; a bounded chain keeps runtime predictable.
                for q in reversed(cand):
                    dist = pos-q
                    if dist > 4096:
                        break
                    if x[q] != x[pos] or x[q+1] != x[pos+1] or x[q+2] != x[pos+2]:
                        continue
                    length = 3
                    while length < max_len and x[q+length] == x[pos+length]:
                        length += 1
                    if length > best_len:
                        best_len, best_dist = length, dist
                        if length == max_len:
                            break
            if best_len >= 3:
                flags |= 1 << bit
                code = ((best_dist-1) << 4) | (best_len-3 if best_len <= 17 else 15)
                out.append((code >> 8) & 255)
                out.append(code & 255)
                if best_len >= 18:
                    extra = best_len-18
                    out.append((extra >> 8) & 255)
                    out.append(extra & 255)
                end = pos + best_len
            else:
                out.append(x[pos])
                end = pos + 1
            while pos < end:
                if pos + 3 <= n:
                    key = x[pos:pos+3]
                    lst = chains.get(key)
                    if lst is None:
                        chains[key] = [pos]
                    else:
                        lst.append(pos)
                        # Retain only a useful window; discard old entries.
                        if len(lst) > 128:
                            del lst[:-64]
                pos += 1
        out[flag_at] = flags
    # Raw form is a one-byte tag plus the original bytes, giving a strict
    # expansion bound of 2 for every nonempty input.
    raw = bytearray([0])
    raw.extend(x)
    if len(out) + 5 < len(raw):
        result = bytearray([1])
        result.extend(((n >> 24) & 255, (n >> 16) & 255, (n >> 8) & 255, n & 255))
        result.extend(out)
        return bytes(result)
    return bytes(raw)


def dec(y):
    y = bytes(y)
    if not y:
        raise ValueError('empty encoding')
    if y[0] == 0:
        return y[1:]
    if y[0] != 1 or len(y) < 5:
        raise ValueError('invalid encoding')
    n = (y[1] << 24) | (y[2] << 16) | (y[3] << 8) | y[4]
    src = 5
    out = bytearray()
    while len(out) < n:
        if src >= len(y):
            raise ValueError('truncated encoding')
        flags = y[src]
        src += 1
        for bit in range(8):
            if len(out) >= n:
                break
            if flags & (1 << bit):
                if src + 2 > len(y):
                    raise ValueError('truncated match')
                code = (y[src] << 8) | y[src+1]
                src += 2
                dist = (code >> 4) + 1
                low = code & 15
                if low == 15:
                    if src + 2 > len(y):
                        raise ValueError('truncated extended match')
                    length = 18 + (y[src] << 8) + y[src+1]
                    src += 2
                else:
                    length = low + 3
                if dist > len(out) or len(out) + length > n:
                    raise ValueError('invalid match')
                for _ in range(length):
                    out.append(out[-dist])
            else:
                if src >= len(y):
                    raise ValueError('truncated literal')
                out.append(y[src])
                src += 1
    if src != len(y):
        raise ValueError('trailing data')
    return bytes(out)
