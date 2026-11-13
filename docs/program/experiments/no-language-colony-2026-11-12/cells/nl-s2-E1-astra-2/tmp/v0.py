def _put(out,n):
    while n >= 128:
        out.append((n&127)|128); n >>= 7
    out.append(n)

def _get(x,i):
    n=0; s=0
    while True:
        c=x[i]; i+=1; n|=(c&127)<<s
        if c<128: return n,i
        s+=7

def _split(s):
    lit=[]; nums=[]; start=0; i=0
    while i<len(s):
        if 48<=s[i]<=57:
            lit.append(s[start:i]); start=i
            while i<len(s) and 48<=s[i]<=57: i+=1
            nums.append(s[start:i]); start=i
        else: i+=1
    lit.append(s[start:])
    return tuple(lit),nums

def enc(x):
    x=bytes(x)
    if len(x)<16: return x
    lines=x.split(b'\n')
    groups={}
    for line in lines[:-1]:
        if b' ' in line:
            k,ns=_split(line)
            if ns: groups.setdefault(k,[]).append(ns)
    models=[]; lookup={}
    for k,rows in groups.items():
        if len(rows)<3: continue
        fields=[]
        for j in range(len(rows[0])):
            vals=[r[j] for r in rows]
            if all(v==vals[0] for v in vals): fields.append((0,vals[0]))
            else:
                width=len(vals[0]) if all(len(v)==len(vals[0]) for v in vals) else 0
                size=(max(int(v) for v in vals).bit_length()+7)//8
                fields.append((1,(width,size)))
        lookup[k]=len(models); models.append((k,fields))
    out=bytearray(b'\x01'); _put(out,len(models))
    for k,fields in models:
        _put(out,len(fields))
        for lit in k:
            _put(out,len(lit)); out.extend(lit)
        for flag,v in fields:
            out.append(flag)
            if flag==0: _put(out,len(v)); out.extend(v)
            else: out.extend(v)
    for line in lines[:-1]:
        if line and len(line)%2==0 and all(c in b'0123456789abcdef' for c in line):
            out.append(1); _put(out,len(line)//2); out.extend(bytes.fromhex(line.decode()))
        elif len(line)>=16 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in line):
            out.append(2); _put(out,len(line)); n=int(line,36)
            size=((36**len(line)-1).bit_length()+7)//8
            out.extend(n.to_bytes(size,'big'))
        else:
            k,ns=_split(line)
            if k in lookup:
                out.append(3); _put(out,lookup[k]); fields=models[lookup[k]][1]
                for v,(flag,spec) in zip(ns,fields):
                    if flag:
                        width,size=spec
                        if not width: _put(out,len(v))
                        out.extend(int(v).to_bytes(size,'big'))
            else:
                out.append(0); _put(out,len(line)); out.extend(line)
    out.append(4); out.extend(lines[-1])
    return bytes(out) if 16<=len(out)<len(x)+1 else b'\x00'+x

def dec(x):
    if len(x)<16: return bytes(x)
    if x[0]==0: return bytes(x[1:])
    count,i=_get(x,1); models=[]
    for _ in range(count):
        nf,i=_get(x,i); lits=[]; fields=[]
        for j in range(nf+1):
            n,i=_get(x,i); lits.append(x[i:i+n]); i+=n
        for j in range(nf):
            flag=x[i]; i+=1
            if not flag:
                n,i=_get(x,i); fields.append((0,x[i:i+n])); i+=n
            else:
                fields.append((1,(x[i],x[i+1]))); i+=2
        models.append((lits,fields))
    out=bytearray(); alphabet=b'0123456789abcdefghijklmnopqrstuvwxyz'
    while i<len(x):
        t=x[i]; i+=1
        if t==4:
            out.extend(x[i:]); break
        n,i=_get(x,i)
        if t==0: out.extend(x[i:i+n]); i+=n
        elif t==1: out.extend(x[i:i+n].hex().encode()); i+=n
        elif t==2:
            size=((36**n-1).bit_length()+7)//8
            value=int.from_bytes(x[i:i+size],'big'); i+=size
            buf=bytearray(n)
            for j in range(n-1,-1,-1): value,r=divmod(value,36); buf[j]=alphabet[r]
            out.extend(buf)
        else:
            lits,fields=models[n]
            for j,(flag,spec) in enumerate(fields):
                out.extend(lits[j])
                if flag:
                    width,size=spec
                    if not width: width,i=_get(x,i)
                    value=int.from_bytes(x[i:i+size],'big'); i+=size
                    out.extend(str(value).zfill(width).encode())
                else: out.extend(spec)
            out.extend(lits[-1])
        out.append(10)
    return bytes(out)
