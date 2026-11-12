def _put(n):
    b=bytearray()
    while n>=128:
        b.append((n&127)|128); n>>=7
    b.append(n)
    return b

def _get(x,p):
    n=0; s=0
    while True:
        c=x[p]; p+=1; n|=(c&127)<<s
        if c<128: return n,p
        s+=7

def enc(x):
    x=bytes(x)
    o=bytearray(b'\x01'); templates={}
    for line in x.splitlines(keepends=True):
        nl=line.endswith(b'\n'); t=line[:-1] if nl else line
        if t and all(c in b'0123456789abcdef' for c in t) and len(t)%2==0:
            k=1; v=bytes.fromhex(t.decode())
        elif t and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in t):
            k=2; n=0
            for j in range(0,len(t),512):
                chunk=t[j:j+512]; n=n*36**len(chunk)+int(chunk,36)
            v=n.to_bytes((len(t)*5170+7999)//8000,'big')
        elif t and all(32<=c<127 for c in t) and b' ' in t:
            parts=t.split(b' '); sk=bytearray(); values=bytearray()
            for ti,token in enumerate(parts):
                if ti: sk.append(32)
                if token and all(c in b'0123456789.' for c in token):
                    j=0
                    while j<len(token):
                        if token[j]==46:
                            sk.append(46); j+=1; continue
                        end=j
                        while end<len(token) and token[end]!=46: end+=1
                        width=end-j
                        if width>255: break
                        sk+=bytes((0,width))
                        values+=int(token[j:end]).to_bytes((width*3322+7999)//8000,'big')
                        j=end
                    if j!=len(token):
                        sk=bytearray(); break
                else: sk+=token
            if sk and 0 in sk:
                sk=bytes(sk); k=3
                if sk in templates: v=_put(templates[sk])+values
                else:
                    templates[sk]=len(templates)+1
                    v=_put(0)+_put(len(sk))+sk+values
            else: k=0; v=t
        else:
            k=0; v=t
        o+=_put(len(t)*8+k*2+nl); o+=v
    return bytes(o) if len(o)<len(x)+1 else b'\x00'+x

def dec(x):
    if x[0]==0: return bytes(x[1:])
    p=1; o=bytearray(); templates=[]; alphabet=b'0123456789abcdefghijklmnopqrstuvwxyz'
    while p<len(x):
        h,p=_get(x,p); n=h//8; k=(h//2)%4; nl=h%2
        if k==3:
            tid,p=_get(x,p)
            if tid==0:
                size,p=_get(x,p); sk=x[p:p+size]; p+=size; templates.append(sk)
            else: sk=templates[tid-1]
            j=0
            while j<len(sk):
                c=sk[j]; j+=1
                if c: o.append(c)
                else:
                    width=sk[j]; j+=1; size=(width*3322+7999)//8000
                    value=int.from_bytes(x[p:p+size],'big'); p+=size
                    o+=str(value).zfill(width).encode()
            if nl: o.append(10)
            continue
        m=n if k==0 else n//2 if k==1 else (n*5170+7999)//8000
        v=x[p:p+m]; p+=m
        if k==1: v=v.hex().encode()
        elif k==2:
            z=int.from_bytes(v,'big'); a=bytearray(n)
            for j in range(n-1,-1,-1): z,r=divmod(z,36); a[j]=alphabet[r]
            v=a
        o+=v
        if nl: o.append(10)
    return bytes(o)
