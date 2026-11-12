#!/usr/bin/env python3
import sys, lzma, zlib, bz2, json, struct
from collections import Counter

# Model a sequence of numbered records when its numeric fields and templates
# can be verified exactly; otherwise use a general-purpose XZ stream.
def packbits(items):
    out=bytearray(); acc=0; n=0
    for value,width in items:
        acc=(acc<<width)|value; n+=width
        while n>=8:
            n-=8; out.append((acc>>n)&255); acc &= (1<<n)-1
    if n: out.append(acc<<(8-n))
    return bytes(out)

class Bits:
    def __init__(self,data): self.data=data; self.pos=0
    def get(self,n):
        v=0
        for _ in range(n):
            v=(v<<1)|((self.data[self.pos//8]>>(7-self.pos%8))&1); self.pos+=1
        return v

def best(data):
    options=[b'R'+data, b'Z'+zlib.compress(data,9), b'B'+bz2.compress(data), b'X'+lzma.compress(data,preset=6)]
    return min(options,key=len)

def unbest(data):
    return {b'R':lambda x:x,b'Z':zlib.decompress,b'B':bz2.decompress,b'X':lzma.decompress}[data[:1]](data[1:])

def model(data):
    lines=data.splitlines(keepends=True)
    if len(lines)<2 or not all(x.endswith(b'\n') for x in lines): return None
    try:
        rows=[(a,b,c) for a,b,c in (line[:-1].split(b' ',1)[0:1]+line[:-1].split(b' ',1)[1].rsplit(b' ',1) for line in lines)]
        width=len(rows[0][0]); start=int(rows[0][0]); tails=[int(r[2]) for r in rows]
        mod=max(tails)+1
        if mod<2: return None
        step=(tails[1]-tails[0])%mod; offset=tails[0]
        if any(a!=str(start+i).zfill(width).encode() or c!=str((offset+i*step)%mod).encode() for i,(a,b,c) in enumerate(rows)): return None
        mids=[r[1] for r in rows]
        scores=[]
        for p in range(1,min(16,len(rows))+1):
            counts=[Counter(mids[r::p]).most_common(1)[0] for r in range(p)]
            scores.append((len(rows)-sum(c for _,c in counts)+2*p,p,[x for x,_ in counts]))
        _,period,defaults=min(scores)
        exceptions=[s for i,s in enumerate(mids) if s!=defaults[i%period]]
        if not exceptions: return None
        seqs=[s.split(b' ') for s in exceptions]
        words=sorted(set(w for s in seqs for w in s))
        if len(words)>8 or not words: return None
        lo=min(map(len,seqs)); hi=max(map(len,seqs)); lb=(hi-lo).bit_length(); wb=(len(words)-1).bit_length()
        if hi>255: return None
        ids={w:i for i,w in enumerate(words)}; flags=[]; stream=[]
        for i,s in enumerate(mids): flags.append((int(s!=defaults[i%period]),1))
        for seq in seqs:
            stream.append((len(seq)-lo,lb)); stream.extend((ids[w],wb) for w in seq)
        hdr=[len(rows),width,start,mod,step,offset,[s.decode('latin1') for s in defaults],[s.decode('latin1') for s in words],lo,lb,wb]
        h=zlib.compress(json.dumps(hdr,separators=(',',':')).encode(),9); flagdata=best(packbits(flags)); payload=best(packbits(stream))
        return b'S2'+struct.pack('>II',len(h),len(flagdata))+h+flagdata+payload
    except (ValueError,IndexError,OverflowError): return None

def decode(data):
    size,fs=struct.unpack('>II',data[2:10]); hdr=json.loads(zlib.decompress(data[10:10+size])); n,width,start,mod,step,offset,defaults,words,lo,lb,wb=hdr
    defaults=[s.encode('latin1') for s in defaults]; words=[s.encode('latin1') for s in words]; flags=Bits(unbest(data[10+size:10+size+fs])); bits=Bits(unbest(data[10+size+fs:])); out=bytearray()
    for i in range(n):
        if flags.get(1):
            length=lo+bits.get(lb); middle=b' '.join(words[bits.get(wb)] for _ in range(length))
        else: middle=defaults[i%len(defaults)]
        out.extend(str(start+i).zfill(width).encode()+b' '+middle+b' '+str((offset+i*step)%mod).encode()+b'\n')
    return bytes(out)

def main():
    args=sys.argv[1:]
    if len(args)==3 and args[0]=='--decompress':
        data=open(args[1],'rb').read(); result=decode(data) if data.startswith(b'S2') else lzma.decompress(data); dest=args[2]
    elif len(args)==2:
        data=open(args[0],'rb').read(); fallback=lzma.compress(data,preset=9); candidate=model(data); result=min((fallback,candidate),key=len) if candidate is not None else fallback; dest=args[1]
    else: raise SystemExit('usage: compress.py [--decompress] input output')
    with open(dest,'wb') as f: f.write(result)
if __name__=='__main__': main()
