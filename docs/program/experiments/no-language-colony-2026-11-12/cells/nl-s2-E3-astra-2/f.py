def enc(x):
    if len(x)<64:return x
    out=bytearray(b'\x01')
    for line in x.splitlines(keepends=True):
        body=line[:-1] if line.endswith(b'\n') else line
        tag=0;data=line
        if line.endswith(b'\n') and body and len(body)%2==0 and all(c in b'0123456789abcdef' for c in body):
            tag=1;data=bytes.fromhex(body.decode())
        elif line.endswith(b'\n') and body and all(c in b'0123456789abcdefghijklmnopqrstuvwxyz' for c in body):
            tag=2;data=len(body).to_bytes(4,'big')+int(body,36).to_bytes((len(body)*6+7)//8,'big')
        out.append(tag);out.extend(len(data).to_bytes(4,'big'));out.extend(data)
    out.append(255)
    return bytes(out).ljust(64,b'\x00') if len(out)<len(x)+1 else b'\x00'+x

def dec(x):
    if len(x)<64:return x
    if x[0]==0:return x[1:]
    out=bytearray();p=1
    while x[p]!=255:
        tag=x[p];n=int.from_bytes(x[p+1:p+5],'big');p+=5;data=x[p:p+n];p+=n
        if tag==1:data=data.hex().encode()+b'\n'
        elif tag==2:
            size=int.from_bytes(data[:4],'big');v=int.from_bytes(data[4:],'big');a=bytearray()
            while v:a.append(b'0123456789abcdefghijklmnopqrstuvwxyz'[v%36]);v//=36
            data=bytes(a[::-1]).rjust(size,b'0')+b'\n'
        out.extend(data)
    return bytes(out)
