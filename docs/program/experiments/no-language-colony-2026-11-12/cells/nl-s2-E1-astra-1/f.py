def _put(n):
    o=bytearray()
    while n>=128:
        o.append((n&127)|128);n>>=7
    o.append(n)
    return o

def _get(x,p):
    n=s=0
    while True:
        c=x[p];p+=1;n|=(c&127)<<s
        if c<128:return n,p
        s+=7

_AL=b'0123456789abcdefghijklmnopqrstuvwxyz'

def _parts(s):
    chunks=[];nums=[];p=0;i=0
    while i<len(s):
        if 48<=s[i]<=57:
            chunks.append(s[p:i]);j=i+1
            while j<len(s) and 48<=s[j]<=57:j+=1
            # Bound integer conversion and arithmetic on arbitrary input.
            if j-i>100:return None,None
            nums.append(int(b'1'+s[i:j]));i=j;p=j
        else:i+=1
    chunks.append(s[p:])
    return tuple(chunks),nums

def enc(x):
    lines=x.splitlines(keepends=True);groups={};parsed=[]
    for line in lines:
        key,nums=_parts(line) if b' ' in line else (None,None)
        parsed.append((key,nums))
        if nums:groups.setdefault(key,[]).append(nums)
    models={};out=bytearray(b'\1');defs=bytearray()
    for key,rows in groups.items():
        if len(rows)<3:continue
        lows=[min(row[i] for row in rows) for i in range(len(rows[0]))]
        bases=[max(row[i] for row in rows)-lows[i]+1 for i in range(len(lows))]
        prod=1
        for b in bases:prod*=b
        k=((prod-1).bit_length()+7)//8
        models[key]=(len(models),lows,bases,k)
        defs+=_put(len(lows))
        for i,part in enumerate(key):
            defs+=_put(len(part));defs+=part
            if i<len(lows):defs+=_put(lows[i]);defs+=_put(bases[i])
    out+=_put(len(models));out+=defs
    for line,(key,nums) in zip(lines,parsed):
        if key in models:
            ident,lows,bases,k=models[key];v=0
            for n,lo,b in zip(nums,lows,bases):v=v*b+n-lo
            out.append(3);out+=_put(ident);out+=v.to_bytes(k,'big');continue
        if line.endswith(b'\n') and 1<len(line)<=1025:
            s=line[:-1]
            if all(c in b'0123456789abcdef' for c in s):
                out.append(1);out+=_put(len(s));out+=int(s,16).to_bytes((len(s)+1)//2,'big');continue
            if all(c in _AL for c in s):
                out.append(2);out+=_put(len(s));out+=int(s,36).to_bytes(((36**len(s)-1).bit_length()+7)//8,'big');continue
        out.append(0);out+=_put(len(line));out+=line
    return bytes(out) if len(out)<len(x)+1 else b'\0'+x

def dec(x):
    if x[0]==0:return x[1:]
    count,p=_get(x,1);models=[]
    for _ in range(count):
        n,p=_get(x,p);parts=[];lows=[];bases=[];prod=1
        for i in range(n+1):
            k,p=_get(x,p);parts.append(x[p:p+k]);p+=k
            if i<n:
                lo,p=_get(x,p);b,p=_get(x,p);lows.append(lo);bases.append(b);prod*=b
        models.append((parts,lows,bases,((prod-1).bit_length()+7)//8))
    out=bytearray()
    while p<len(x):
        t=x[p];p+=1;n,p=_get(x,p)
        if t==0:out+=x[p:p+n];p+=n
        elif t==3:
            parts,lows,bases,k=models[n];v=int.from_bytes(x[p:p+k],'big');p+=k;nums=[]
            for lo,b in zip(reversed(lows),reversed(bases)):
                v,r=divmod(v,b);nums.append(str(lo+r)[1:].encode())
            nums.reverse()
            for part,num in zip(parts,nums):out+=part;out+=num
            out+=parts[-1]
        else:
            k=(n+1)//2 if t==1 else ((36**n-1).bit_length()+7)//8
            v=int.from_bytes(x[p:p+k],'big');p+=k
            if t==1:s=format(v,'x').encode().rjust(n,b'0')
            else:
                a=bytearray(n)
                for i in range(n-1,-1,-1):v,r=divmod(v,36);a[i]=_AL[r]
                s=bytes(a)
            out+=s+b'\n'
    return bytes(out)

encode=enc
decode=dec
