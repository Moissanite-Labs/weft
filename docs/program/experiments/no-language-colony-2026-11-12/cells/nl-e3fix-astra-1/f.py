# Import-free reversible record codec. Raw fallback guarantees |enc(x)| <= 2|x| for nonempty x.
def put(n):
    o=bytearray()
    while n>=128:o.append((n&127)|128);n>>=7
    o.append(n);return o

def get(y,p):
    n=0;s=0
    while True:
        c=y[p];p+=1;n|=(c&127)<<s
        if c<128:return n,p
        s+=7

def parts(line):
    literals=[];widths=[];values=[];p=0;start=0
    while p<len(line):
        if 48<=line[p]<=57:
            literals.append(line[start:p]);start=p
            while p<len(line) and 48<=line[p]<=57:p+=1
            w=p-start
            if w>128:return None
            widths.append(w);values.append(int(line[start:p]));start=p
        else:p+=1
    literals.append(line[start:])
    if not widths:return None
    return (tuple(literals),tuple(widths)),values

def enc(x):
    x=bytes(x);out=bytearray([1]);templates={}
    for line in x.split(b'\n'):
        n=len(line)
        if n and n<=4096 and all(c in b'0123456789abcdef' for c in line):
            out.append(1);out.extend(put(n));out.extend(int(line,16).to_bytes((n+1)//2,'big'))
        elif n and n<=4096 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in line):
            out.append(2);out.extend(put(n));size=((36**n-1).bit_length()+7)//8
            out.extend(int(line,36).to_bytes(size,'big'))
        else:
            z=parts(line) if n<=4096 else None
            if z is None:
                out.append(0);out.extend(put(n));out.extend(line);continue
            key,vals=z;lits,widths=key
            if key not in templates:
                templates[key]=len(templates);out.append(4);out.extend(put(len(widths)))
                for lit in lits:out.extend(put(len(lit)));out.extend(lit)
                for w in widths:out.extend(put(w))
            else:out.append(3);out.extend(put(templates[key]))
            value=0;radix=1
            for w,v in zip(widths,vals):
                r=10**w;value=value*r+v;radix*=r
            out.extend(value.to_bytes(((radix-1).bit_length()+7)//8,'big'))
    return bytes(out) if len(out)<len(x)+1 else b'\0'+x

def dec(y):
    if y[0]==0:return bytes(y[1:])
    p=1;lines=[];templates=[]
    while p<len(y):
        tag=y[p];p+=1
        if tag<=2:
            n,p=get(y,p)
            if tag==0:line=y[p:p+n];p+=n
            elif tag==1:
                size=(n+1)//2;v=int.from_bytes(y[p:p+size],'big');p+=size
                line=format(v,'0'+str(n)+'x').encode()
            else:
                size=((36**n-1).bit_length()+7)//8;v=int.from_bytes(y[p:p+size],'big');p+=size
                a=bytearray(n)
                for i in range(n-1,-1,-1):v,r=divmod(v,36);a[i]=b'0123456789abcdefghijklmnopqrstuvwxyz'[r]
                line=bytes(a)
        else:
            if tag==4:
                k,p=get(y,p);lits=[];widths=[]
                for _ in range(k+1):
                    n,p=get(y,p);lits.append(y[p:p+n]);p+=n
                for _ in range(k):w,p=get(y,p);widths.append(w)
                templates.append((lits,widths))
            else:
                i,p=get(y,p);lits,widths=templates[i]
            radix=10**sum(widths);size=((radix-1).bit_length()+7)//8
            v=int.from_bytes(y[p:p+size],'big');p+=size;vals=[]
            for w in reversed(widths):v,r=divmod(v,10**w);vals.append(str(r).zfill(w).encode())
            vals.reverse();a=bytearray(lits[0])
            for i,b in enumerate(vals):a.extend(b);a.extend(lits[i+1])
            line=bytes(a)
        lines.append(line)
    return b'\n'.join(lines)

if __name__=='__main__':
    x=open('x.bin','rb').read();y=enc(x)
    assert dec(y)==x
    assert len(y)<=2*len(x)
    print(100*(1-len(y)/len(x)))
