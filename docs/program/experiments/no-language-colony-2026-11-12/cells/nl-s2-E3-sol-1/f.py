def enc(x):
    out = bytearray(b'\x00' if x.endswith(b'\n') else b'\x01')
    lines = x.split(b'\n')
    if x.endswith(b'\n'):
        lines.pop()
    for line in lines:
        if line.startswith(b'e18a line ') and line.endswith(b' select pick win seed '+line.split(b' seed ')[-1]):
            parts=line.split(b' ')
            if len(parts)==11 and parts[0:2]==[b'e18a',b'line'] and parts[3]==b'ratio' and parts[5:8]==[b'select',b'pick',b'win'] and parts[8]==b'seed':
                pass
        parts=line.split(b' ')
        if len(parts)==10 and parts[0:2]==[b'e18a',b'line'] and parts[3]==b'ratio' and parts[5:9]==[b'select',b'pick',b'win',b'seed']:
            try:
                a=int(parts[2]); r=parts[4]; b=int(parts[9]); rr=int(r[2:]);
                if 0<=a<16777216 and 0<=b<4294967296 and len(r)==8 and r[:2]==b'0.' and 0<=rr<1000000 and str(a).encode()==parts[2] and str(b).encode()==parts[9] and (b'0.%06d'%rr)==r:
                    out.append(0);out.extend(a.to_bytes(3,'big'));out.extend(rr.to_bytes(3,'big'));out.extend(b.to_bytes(4,'big'));continue
            except ValueError: pass
        if len(line)==96 and all(c in b'0123456789abcdef' for c in line):
            out.append(1);out.extend(bytes.fromhex(line.decode()));continue
        if len(line)==64 and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in line):
            out.append(2);out.extend(int(line,36).to_bytes(42,'big'));continue
        if len(line)>65535:return b'\xff'+x
        out.append(3);out.extend(len(line).to_bytes(2,'big'));out.extend(line)
    if len(out)>=len(x)+1:return b'\xff'+x
    return bytes(out)

def dec(y):
    if y[:1]==b'\xff':return y[1:]
    if not y:return b''
    pos=1; lines=[]
    while pos<len(y):
        t=y[pos];pos+=1
        if t==0:
            a=int.from_bytes(y[pos:pos+3],'big');r=int.from_bytes(y[pos+3:pos+6],'big');b=int.from_bytes(y[pos+6:pos+10],'big');pos+=10
            lines.append(b'e18a line %d ratio 0.%06d select pick win seed %d'%(a,r,b))
        elif t==1:
            lines.append(y[pos:pos+48].hex().encode());pos+=48
        elif t==2:
            n=int.from_bytes(y[pos:pos+42],'big');pos+=42
            s=b'0123456789abcdefghijklmnopqrstuvwxyz';d=bytearray()
            while n:d.append(s[n%36]);n//=36
            lines.append(bytes(d[::-1]).rjust(64,b'0'))
        else:
            n=int.from_bytes(y[pos:pos+2],'big');pos+=2
            lines.append(y[pos:pos+n]);pos+=n
    return b'\n'.join(lines)+(b'\n' if y[0]==0 else b'')
