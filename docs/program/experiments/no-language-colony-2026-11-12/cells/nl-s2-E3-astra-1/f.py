def enc(x):
    if len(x)<1024:return x
    out=bytearray(b'\x01')
    for line in x.splitlines(keepends=True):
        if line.endswith(b'\n'):
            t=line[:-1]
            if len(t)==96 and all(c in b'0123456789abcdef' for c in t):
                out.append(1);out.extend(bytes.fromhex(t.decode()));continue
            if len(t)==64 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in t):
                out.append(2);out.extend(int(t,36).to_bytes(42,'big'));continue
        for i in range(0,len(line),255):
            t=line[i:i+255];out.extend((0,len(t)));out.extend(t)
    return bytes(out) if 1024<=len(out)<len(x)+1 else b'\x00'+x

def dec(x):
    if len(x)<1024:return x
    if x[0]==0:return x[1:]
    out=bytearray();i=1
    while i<len(x):
        k=x[i];i+=1
        if k==0:
            n=x[i];i+=1;out.extend(x[i:i+n]);i+=n
        elif k==1:
            out.extend(x[i:i+48].hex().encode()+b'\n');i+=48
        else:
            n=int.from_bytes(x[i:i+42],'big');i+=42;t=bytearray()
            for _ in range(64):t.append(b'0123456789abcdefghijklmnopqrstuvwxyz'[n%36]);n//=36
            out.extend(t[::-1]+b'\n')
    return bytes(out)
