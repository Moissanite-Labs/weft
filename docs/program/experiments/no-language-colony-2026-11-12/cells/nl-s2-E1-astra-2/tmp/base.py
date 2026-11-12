def enc(x):
    x = bytes(x)
    if len(x) < 8: return x
    out = bytearray(b'\x01')
    for line in x.splitlines(keepends=True):
        if line.endswith(b'\n') and len(line) == 97 and all(c in b'0123456789abcdef' for c in line[:-1]):
            out.append(1)
            out.extend(bytes.fromhex(line[:-1].decode()))
        else:
            out.append(0)
            out.extend(len(line).to_bytes(4,'big'))
            out.extend(line)
    return bytes(out) if 8 <= len(out) < len(x)+1 else b'\x00'+x

def dec(x):
    if len(x) < 8: return bytes(x)
    if x[0] == 0:
        return bytes(x[1:])
    out = bytearray()
    i = 1
    while i < len(x):
        t = x[i]; i += 1
        if t == 1:
            out.extend(x[i:i+48].hex().encode()+b'\n'); i += 48
        else:
            n = int.from_bytes(x[i:i+4], 'big'); i += 4
            out.extend(x[i:i+n]); i += n
    return bytes(out)
