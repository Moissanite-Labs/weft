#!/usr/bin/env python3
import sys, lzma
MAGIC=b'CP2'
ALPH=b'0123456789abcdefghijklmnopqrstuvwxyz'
VAL={c:i for i,c in enumerate(ALPH)}
def enc(data):
    lines=data.splitlines()
    out=bytearray(MAGIC+len(lines).to_bytes(2,'big'))
    for s in lines:
        if len(s)==96 and all(c in b'0123456789abcdef' for c in s):
            out.append(0); out.extend(bytes.fromhex(s.decode('ascii')))
        elif len(s)==64 and all(c in VAL for c in s):
            out.append(1); a=0
            for c in s: a=a*36+VAL[c]
            out.extend(a.to_bytes(42,'big'))
        else:
            out.append(2); out.append(len(s)); out.extend(s)
    return lzma.compress(bytes(out), preset=9)
def dec(blob):
    d=lzma.decompress(blob)
    if d[:3]!=MAGIC: raise ValueError('bad file')
    n=int.from_bytes(d[3:5],'big'); i=5; out=bytearray()
    for _ in range(n):
        t=d[i]; i+=1
        if t==0: s=d[i:i+48].hex().encode('ascii'); i+=48
        elif t==1:
            a=int.from_bytes(d[i:i+42],'big'); i+=42; v=[0]*64
            for k in range(63,-1,-1): a,r=divmod(a,36); v[k]=r
            s=bytes(ALPH[x] for x in v)
        elif t==2:
            l=d[i]; i+=1; s=d[i:i+l]; i+=l
        else: raise ValueError('bad record')
        out.extend(s); out.append(10)
    if i!=len(d): raise ValueError('trailing data')
    return bytes(out)
def main():
    if len(sys.argv)==4 and sys.argv[1]=='--decompress': open(sys.argv[3],'wb').write(dec(open(sys.argv[2],'rb').read()))
    elif len(sys.argv)==3: open(sys.argv[2],'wb').write(enc(open(sys.argv[1],'rb').read()))
    else: raise SystemExit('usage: compress.py [--decompress] input output')
if __name__=='__main__': main()
