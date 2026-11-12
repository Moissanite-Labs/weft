# Lossless codec for the structured line format, with an identity fallback.
_H = b'e18a line '
_M = b' ratio 0.'
_T = b' select pick win seed '
_A = b'0123456789abcdefghijklmnopqrstuvwxyz'

def enc(x):
    if not x:
        return x
    try:
        lines = x.split(b'\n')
        terminal = lines[-1] == b''
        if terminal:
            lines.pop()
        n = len(lines)
        if n >= 65536:
            raise ValueError
        tags = bytearray((n+3)//4)
        data = bytearray()
        for i, line in enumerate(lines):
            if line.startswith(_H):
                q = line[len(_H):].split(_M)
                if len(q) != 2:
                    raise ValueError
                z = q[1].split(_T)
                if len(z) != 2 or len(z[0]) != 6:
                    raise ValueError
                a,b,c = int(q[0]),int(z[0]),int(z[1])
                if not (0 <= a < 1000000 and 0 <= b < 1000000 and 0 <= c < 1000000000):
                    raise ValueError
                if _H+str(a).encode()+_M+str(b).zfill(6).encode()+_T+str(c).encode()!=line:
                    raise ValueError
                data.extend(a.to_bytes(3,'big'))
                data.extend(b.to_bytes(3,'big'))
                data.extend(c.to_bytes(4,'big'))
                t=0
            elif len(line)==96 and all(c in b'0123456789abcdef' for c in line):
                data.extend(bytes.fromhex(line.decode()))
                t=1
            elif len(line)==64 and all(c in _A for c in line):
                data.extend(int(line,36).to_bytes(42,'big'))
                t=2
            else:
                raise ValueError
            tags[i//4] |= t << ((i%4)*2)
        packed = b'\0'+n.to_bytes(2,'big')+bytes([terminal])+tags+data
        if len(packed) < len(x):
            return packed
    except (ValueError, OverflowError, UnicodeError):
        pass
    return b'\xff'+x if x[0] in (0,255) else x

def dec(y):
    if not y:
        return y
    if y[0]==255:
        return y[1:]
    if y[0]!=0:
        return y
    n=int.from_bytes(y[1:3],'big')
    end=y[3]
    tags=y[4:4+(n+3)//4]
    pos=4+len(tags)
    out=[]
    for i in range(n):
        t=(tags[i//4] >> ((i%4)*2))&3
        if t==0:
            a=int.from_bytes(y[pos:pos+3],'big')
            b=int.from_bytes(y[pos+3:pos+6],'big')
            c=int.from_bytes(y[pos+6:pos+10],'big')
            out.append(_H+str(a).encode()+_M+str(b).zfill(6).encode()+_T+str(c).encode())
            pos+=10
        elif t==1:
            out.append(y[pos:pos+48].hex().encode())
            pos+=48
        elif t==2:
            v=int.from_bytes(y[pos:pos+42],'big')
            buf=bytearray(64)
            for j in range(63,-1,-1):
                v,r=divmod(v,36)
                buf[j]=_A[r]
            out.append(bytes(buf))
            pos+=42
        else:
            raise ValueError
    return b'\n'.join(out)+(b'\n' if end else b'')
