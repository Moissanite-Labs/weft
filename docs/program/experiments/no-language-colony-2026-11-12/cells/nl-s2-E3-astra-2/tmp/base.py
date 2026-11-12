def enc(x):
    counts=[1]*256
    total=256
    lo=0; hi=(1<<32)-1; pending=0; bits=[]
    def emit(b):
        nonlocal pending
        bits.append(b)
        bits.extend([1-b]*pending); pending=0
    for c in x:
        a=sum(counts[:c]); r=hi-lo+1
        hi=lo+r*(a+counts[c])//total-1; lo=lo+r*a//total
        while True:
            if hi<2147483648: emit(0)
            elif lo>=2147483648:
                emit(1);lo-=2147483648;hi-=2147483648
            elif lo>=1073741824 and hi<3221225472:
                pending+=1;lo-=1073741824;hi-=1073741824
            else: break
            lo*=2;hi=hi*2+1
        counts[c]+=1; total+=1
        if total>=16384:
            counts=[(v+1)//2 for v in counts];total=sum(counts)
    pending+=1;emit(0 if lo<1073741824 else 1)
    out=bytearray(b'\x01'+len(x).to_bytes(8,'big'))
    for i in range(0,len(bits),8):
        b=0
        for j in range(8): b=(b<<1)|(bits[i+j] if i+j<len(bits) else 0)
        out.append(b)
    return bytes(out) if len(out)<len(x)+1 else b'\x00'+x

def dec(x):
    if x[0]==0:return x[1:]
    n=int.from_bytes(x[1:9],'big');data=x[9:];pos=0
    def bit():
        nonlocal pos
        v=(data[pos//8]>>(7-pos%8))&1 if pos<len(data)*8 else 0
        pos+=1;return v
    counts=[1]*256;total=256;lo=0;hi=(1<<32)-1;value=0
    for _ in range(32):value=value*2+bit()
    out=bytearray()
    for _ in range(n):
        r=hi-lo+1;t=((value-lo+1)*total-1)//r;a=0;c=0
        while a+counts[c]<=t:a+=counts[c];c+=1
        out.append(c)
        hi=lo+r*(a+counts[c])//total-1;lo=lo+r*a//total
        while True:
            if hi<2147483648:pass
            elif lo>=2147483648:lo-=2147483648;hi-=2147483648;value-=2147483648
            elif lo>=1073741824 and hi<3221225472:lo-=1073741824;hi-=1073741824;value-=1073741824
            else:break
            lo*=2;hi=hi*2+1;value=value*2+bit()
        counts[c]+=1;total+=1
        if total>=16384:counts=[(v+1)//2 for v in counts];total=sum(counts)
    return bytes(out)
