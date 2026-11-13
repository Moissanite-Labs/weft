def vi(n):
    r=bytearray()
    while n>=128:
        r.append((n&127)|128); n>>=7
    r.append(n)
    return r

def rv(x,p):
    n=s=0
    while True:
        b=x[p]; p+=1; n|=(b&127)<<s
        if b<128: return n,p
        s+=7

def enc(x):
    out=bytearray(b'\x01'); prefixes=[]
    for line in x.split(b'\n'):
        if len(line)==96 and all(c in b'0123456789abcdef' for c in line):
            out.append(1); out.extend(bytes.fromhex(line.decode()))
        elif len(line)==64 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in line):
            out.append(2); out.extend(int(line,36).to_bytes(42,'big'))
        else:
            t=line.split(b' ')
            if len(t)==10 and t[1]==b'line' and t[3]==b'ratio' and t[5:9]==[b'select',b'pick',b'win',b'seed']:
                packed=False
                if len(t[2])<=6 and len(t[9])<=9 and t[2].isdigit() and t[9].isdigit() and t[4].startswith(b'0.') and len(t[4])==8 and t[4][2:].isdigit():
                    u,v,w=int(t[2]),int(t[4][2:]),int(t[9])
                    if u<1000000 and w<1000000000 and str(u).encode()==t[2] and str(w).encode()==t[9]:
                        out.append(4)
                        if t[0] in prefixes:
                            out.extend(vi(prefixes.index(t[0])))
                        else:
                            out.extend(vi(len(prefixes))); prefixes.append(t[0]); out.extend(vi(len(t[0]))); out.extend(t[0])
                        out.extend(((u*1000000+v)*1000000000+w).to_bytes(9,'big')); packed=True
                if not packed:
                    z=b' '.join([t[0],t[2],t[4],t[9]])
                    out.append(3); out.extend(vi(len(z))); out.extend(z)
            else:
                out.append(0); out.extend(vi(len(line))); out.extend(line)
    return bytes(out) if len(out)<len(x)+1 else b'\0'+x

def dec(x):
    if x[0]==0: return x[1:]
    lines=[]; p=1; prefixes=[]
    while p<len(x):
        tag=x[p]; p+=1
        if tag==4:
            k,p=rv(x,p)
            if k==len(prefixes):
                n,p=rv(x,p); prefixes.append(x[p:p+n]); p+=n
            value=int.from_bytes(x[p:p+9],'big'); p+=9
            value,w=divmod(value,1000000000); u,v=divmod(value,1000000)
            line=prefixes[k]+b' line '+str(u).encode()+b' ratio 0.'+str(v).zfill(6).encode()+b' select pick win seed '+str(w).encode()
        elif tag==1:
            line=x[p:p+48].hex().encode(); p+=48
        elif tag==2:
            n=int.from_bytes(x[p:p+42],'big'); p+=42; a=bytearray()
            for _ in range(64):
                n,r=divmod(n,36); a.append(b'0123456789abcdefghijklmnopqrstuvwxyz'[r])
            line=bytes(a[::-1])
        else:
            n,p=rv(x,p); line=x[p:p+n]; p+=n
            if tag==3:
                t=line.split(b' '); line=t[0]+b' line '+t[1]+b' ratio '+t[2]+b' select pick win seed '+t[3]
        lines.append(line)
    return b'\n'.join(lines)

encode=enc
decode=dec
s=2
if __name__=='__main__':
    x=open('x.bin','rb').read(); y=enc(x)
    assert dec(y)==x
    print(100*(1-len(y)/len(x)))
