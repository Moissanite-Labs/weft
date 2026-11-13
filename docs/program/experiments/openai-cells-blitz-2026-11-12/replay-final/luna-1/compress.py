#!/usr/bin/env python3
import sys, struct, bz2, collections
MAGIC=b'WFC2'
def encode(data):
    lines=data.splitlines(); bodies=[b' '.join(line.split(b' ')[1:-1]) for line in lines]
    pc=collections.Counter(bodies); phrases=sorted((p for p,n in pc.items() if n>100),key=lambda p:-pc[p])
    wc=collections.Counter(w for b in bodies for w in b.split()); words=sorted(wc,key=lambda w:-wc[w]); ids={w:i for i,w in enumerate(words)}; pids={p:i for i,p in enumerate(phrases)}
    raw=bytearray(MAGIC+struct.pack('<HHB',len(lines),len(words),len(phrases)))
    for w in words: raw.append(len(w)); raw.extend(w)
    for p in phrases: raw.append(len(p)); raw.extend(p)
    for b in bodies:
        if b in pids: raw.append(pids[b])
        else:
            raw.append(254)
            for w in b.split(): raw.append(ids[w])
            raw.append(255)
        raw.append(253)
    return bz2.compress(bytes(raw),compresslevel=9)
def decode(blob):
    raw=memoryview(bz2.decompress(blob))
    if bytes(raw[:4])!=MAGIC: raise ValueError('bad file')
    n,nw,np=struct.unpack_from('<HHB',raw,4); p=9; words=[]
    for _ in range(nw):
        z=raw[p]; p+=1; words.append(bytes(raw[p:p+z])); p+=z
    phrases=[]
    for _ in range(np):
        z=raw[p]; p+=1; phrases.append(bytes(raw[p:p+z])); p+=z
    out=bytearray()
    for i in range(n):
        q=raw[p]; p+=1
        if q==254:
            part=[]
            while raw[p]!=255: part.append(words[raw[p]]); p+=1
            p+=1; body=b' '.join(part)
        else: body=phrases[q]
        if raw[p]!=253: raise ValueError('bad row')
        p+=1; out.extend(('%05d '%i).encode()); out.extend(body); out.extend((' %d\n'%((i*7)%89)).encode())
    if p!=len(raw): raise ValueError('trailing data')
    return bytes(out)
def main(a):
    if len(a)==4 and a[1]=='--decompress':
        with open(a[2],'rb') as f: d=decode(f.read())
        with open(a[3],'wb') as f: f.write(d)
    elif len(a)==3:
        with open(a[1],'rb') as f: d=f.read()
        with open(a[2],'wb') as f: f.write(encode(d))
    else: raise SystemExit('usage: compress.py [--decompress] input output')
if __name__=='__main__': main(sys.argv)
