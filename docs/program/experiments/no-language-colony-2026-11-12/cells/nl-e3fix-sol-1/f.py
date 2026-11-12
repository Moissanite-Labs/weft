import zlib

_P = b'e18a line '
_M = b' ratio '
_E = b' select pick win seed '
_HEX = b'0123456789abcdef'
_ALPHA = b'0123456789abcdefghijklmnopqrstuvwxyz'

def _trans(x):
    if not x.endswith(b'\n'):
        return None
    out=bytearray()
    for line in x.splitlines():
        if line.startswith(_P) and _M in line and _E in line:
            try:
                a,b=line[len(_P):].split(_M)
                c,d=b.split(_E)
                nums=(int(a),int(c.replace(b'.',b'')),int(d))
                if len(c)==8 and c[1:2]==b'.' and 0<=nums[0]<2**24 and 0<=nums[1]<1000000 and 0<=nums[2]<2**32 and (_P+str(nums[0]).encode()+_M+(b'0.%06d'%nums[1])+_E+str(nums[2]).encode())==line:
                    out.append(0)
                    for num,n in zip(nums,(3,3,4)):
                        out.extend(num.to_bytes(n,'big'))
                    continue
            except (ValueError,OverflowError):
                pass
        if len(line)==96 and all(ch in _HEX for ch in line):
            out.append(1);out.extend(bytes.fromhex(line.decode()));continue
        if len(line)==64 and all(ch in _ALPHA for ch in line):
            out.append(2);out.extend(int(line,36).to_bytes(42,'big'));continue
        return None
    return bytes(out)

def _untrans(x):
    out=bytearray();p=0;n=len(x)
    while p<n:
        tag=x[p];p+=1
        if tag==0:
            a=int.from_bytes(x[p:p+3],'big');b=int.from_bytes(x[p+3:p+6],'big');c=int.from_bytes(x[p+6:p+10],'big');p+=10
            out.extend(_P+str(a).encode()+_M+(b'0.%06d'%b)+_E+str(c).encode()+b'\n')
        elif tag==1:
            out.extend(x[p:p+48].hex().encode()+b'\n');p+=48
        else:
            a=int.from_bytes(x[p:p+42],'big');p+=42
            v=bytearray(64)
            for i in range(63,-1,-1):
                a,r=divmod(a,36);v[i]=_ALPHA[r]
            out.extend(v+b'\n')
    return bytes(out)

def enc(x):
    if len(x)==1:
        return x
    raw=zlib.compress(x,9)
    mode=1
    transformed=_trans(x)
    if transformed is not None:
        coded=zlib.compress(transformed,9)
        if len(coded)<len(raw):
            raw=coded;mode=2
    if len(raw)>=len(x):
        return b'\x00'+x
    return bytes([mode])+raw

def dec(x):
    if len(x)==1:
        return x
    if x[0]==0:
        return x[1:]
    data=zlib.decompress(x[1:])
    return _untrans(data) if x[0]==2 else data
