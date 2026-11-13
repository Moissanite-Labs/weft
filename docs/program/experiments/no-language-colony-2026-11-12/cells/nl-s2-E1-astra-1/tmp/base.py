def _put(n):
    o=bytearray()
    while n>=128:
        o.append((n&127)|128); n>>=7
    o.append(n)
    return o

def _get(x,p):
    n=s=0
    while True:
        c=x[p]; p+=1; n|=(c&127)<<s
        if c<128: return n,p
        s+=7

_AL=b'0123456789abcdefghijklmnopqrstuvwxyz'

def enc(x):
    out=bytearray(b'\x01')
    for line in x.splitlines(keepends=True):
        if line.endswith(b'\n') and len(line)>1:
            s=line[:-1]
            if all(c in b'0123456789abcdef' for c in s):
                out.append(1); out+=_put(len(s)); out+=int(s,16).to_bytes((len(s)+1)//2,'big'); continue
            if all(c in _AL for c in s):
                out.append(2); out+=_put(len(s)); out+=int(s,36).to_bytes((36**len(s)-1).bit_length()//8+1,'big'); continue
        out.append(0); out+=_put(len(line)); out+=line
    return bytes(out) if len(out)<len(x)+1 else b'\0'+x

def dec(x):
    if x[0]==0:return x[1:]
    p=1; out=bytearray()
    while p<len(x):
        t=x[p]; p+=1; n,p=_get(x,p)
        if t==0: out+=x[p:p+n]; p+=n
        else:
            k=(n+1)//2 if t==1 else (36**n-1).bit_length()//8+1
            v=int.from_bytes(x[p:p+k],'big'); p+=k
            if t==1:s=format(v,'x').encode().rjust(n,b'0')
            else:
                a=bytearray(n)
                for i in range(n-1,-1,-1):v,r=divmod(v,36);a[i]=_AL[r]
                s=bytes(a)
            out+=s+b'\n'
    return bytes(out)

encode=enc
decode=dec
