def _put(n):
    b=bytearray()
    while n>=128:
        b.append((n&127)|128);n>>=7
    b.append(n)
    return b

def _get(x,i):
    n=0;s=0
    while True:
        c=x[i];i+=1;n|=(c&127)<<s
        if c<128:return n,i
        s+=7

def _pattern(t):
    parts=[];widths=[];values=[];start=0;i=0
    while i<len(t):
        if 48<=t[i]<=57:
            parts.append(t[start:i]);j=i+1
            while j<len(t) and 48<=t[j]<=57:j+=1
            a=t[i:j]
            if len(a)>18:return None
            widths.append(len(a) if a[0]==48 else 0)
            values.append(int(a));i=j;start=j
        else:i+=1
    parts.append(t[start:])
    if not values:return None
    return (tuple(parts),tuple(widths)),values

def enc(x):
    out=bytearray(b'\x01');patterns={};raw=bytearray()
    def flush():
        if raw:
            out.append(0);out.extend(_put(len(raw)));out.extend(raw);raw.clear()
    for line in x.splitlines(keepends=True):
        encoded=None
        if line.endswith(b'\n'):
            t=line[:-1]
            if len(t)==96 and all(c in b'0123456789abcdef' for c in t):
                encoded=b'\x01'+bytes.fromhex(t.decode())
            elif len(t)==64 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in t):
                encoded=b'\x02'+int(t,36).to_bytes(42,'big')
            elif b' ' in t:
                p=_pattern(t)
                if p is not None:
                    key,values=p
                    payload=bytearray()
                    for n in values:payload.extend(_put(n))
                    if key in patterns:
                        encoded=b'\x04'+_put(patterns[key])+payload
                    else:
                        parts,widths=key
                        header=bytearray(b'\x03');header.extend(_put(len(widths)))
                        for part,width in zip(parts,widths):
                            header.extend(_put(len(part)));header.extend(part);header.extend(_put(width))
                        header.extend(_put(len(parts[-1])));header.extend(parts[-1])
                        encoded=header+payload
                        patterns[key]=len(patterns)
        if encoded is None:raw.extend(line)
        else:flush();out.extend(encoded)
    flush()
    return bytes(out) if len(out)<len(x)+1 else b'\x00'+x

def dec(x):
    if x[0]==0:return x[1:]
    out=bytearray();i=1;patterns=[]
    while i<len(x):
        k=x[i];i+=1
        if k==0:
            n,i=_get(x,i);out.extend(x[i:i+n]);i+=n
        elif k==1:
            out.extend(x[i:i+48].hex().encode()+b'\n');i+=48
        elif k==2:
            n=int.from_bytes(x[i:i+42],'big');i+=42
            a=bytearray()
            for _ in range(64):
                n,r=divmod(n,36);a.append(b'0123456789abcdefghijklmnopqrstuvwxyz'[r])
            out.extend(a[::-1]);out.append(10)
        else:
            if k==3:
                count,i=_get(x,i);parts=[];widths=[]
                for _ in range(count):
                    n,i=_get(x,i);parts.append(x[i:i+n]);i+=n
                    w,i=_get(x,i);widths.append(w)
                n,i=_get(x,i);parts.append(x[i:i+n]);i+=n
                patterns.append((parts,widths));key=patterns[-1]
            else:
                n,i=_get(x,i);key=patterns[n]
            parts,widths=key
            for part,width in zip(parts,widths):
                n,i=_get(x,i);out.extend(part);out.extend(str(n).zfill(width).encode())
            out.extend(parts[-1]);out.append(10)
    return bytes(out)

if __name__=='__main__':
    x=open('x.bin','rb').read()
    y=enc(x)
    assert dec(y)==x
    print(100*(1-len(y)/len(x)))
