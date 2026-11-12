#!/usr/bin/env python3
import sys, zlib, re
MAGIC=b'CP01'
HEX=re.compile(rb'^[0-9a-f]+$')
ALNUM=re.compile(rb'^[0-9a-z]+$')
META=re.compile(rb'^e18a line ([0-9]+) ratio 0\.([0-9]{6}) select pick win seed ([0-9]+)$')
def putvar(n,out):
    while n>=128: out.append((n&127)|128); n>>=7
    out.append(n)
def getvar(data,pos):
    n=shift=0
    while True:
        b=data[pos]; pos+=1; n|=(b&127)<<shift
        if b<128:return n,pos
        shift+=7
def pack6(s):
    val=0
    for c in s: val=val*36+(c-48 if c<=57 else c-87)
    nbytes=((36**len(s)-1).bit_length()+7)//8
    return val.to_bytes(nbytes,'big')
def unpack6(data,n):
    val=int.from_bytes(data,'big'); out=bytearray(n); alphabet=b'0123456789abcdefghijklmnopqrstuvwxyz'
    for i in range(n-1,-1,-1): val,r=divmod(val,36); out[i]=alphabet[r]
    if val: raise ValueError('bad packed token')
    return bytes(out)
def encode(src):
    out=bytearray(); lines=src.splitlines(keepends=True); putvar(len(lines),out)
    for line in lines:
        nl=line.endswith(b'\n'); s=line[:-1] if nl else line
        m=META.fullmatch(s)
        if m:
            typ=3; b=bytearray()
            for v in m.groups(): putvar(int(v),b)
            flags=int(nl)
        elif len(s)>=2 and len(s)%2==0 and HEX.fullmatch(s): typ,b,flags=0,bytes.fromhex(s.decode()),int(nl)
        elif len(s) and ALNUM.fullmatch(s): typ,b,flags=1,pack6(s),int(nl)
        else: typ,b,flags=2,s,int(nl)
        out.append(typ|(flags<<2)); putvar(len(s),out); putvar(len(b),out); out.extend(b)
    return MAGIC+zlib.compress(bytes(out),9)
def decode(blob):
    if not blob.startswith(MAGIC): raise ValueError('bad file')
    d=zlib.decompress(blob[len(MAGIC):]); n,p=getvar(d,0); out=bytearray()
    for _ in range(n):
        f=d[p]; p+=1; typ,nl=f&3,bool(f&4); size,p=getvar(d,p); blen,p=getvar(d,p); b=d[p:p+blen]; p+=blen
        if typ==0:s=b.hex().encode()
        elif typ==1:s=unpack6(b,size)
        elif typ==2:s=b
        elif typ==3:
            a,q=getvar(b,0); r,q=getvar(b,q); seed,q=getvar(b,q)
            if q!=len(b):raise ValueError('bad metadata')
            s=('e18a line %d ratio 0.%06d select pick win seed %d'%(a,r,seed)).encode()
        else:raise ValueError('bad record')
        if len(s)!=size:raise ValueError('bad length')
        out.extend(s)
        if nl:out.append(10)
    if p!=len(d):raise ValueError('trailing data')
    return bytes(out)
def main():
    if len(sys.argv)==4 and sys.argv[1]=='--decompress':
        with open(sys.argv[2],'rb') as f:data=decode(f.read())
        with open(sys.argv[3],'wb') as f:f.write(data)
    elif len(sys.argv)==3:
        with open(sys.argv[1],'rb') as f:data=f.read()
        with open(sys.argv[2],'wb') as f:f.write(encode(data))
    else:raise SystemExit('usage: compress.py [--decompress] input output')
if __name__=='__main__':main()
