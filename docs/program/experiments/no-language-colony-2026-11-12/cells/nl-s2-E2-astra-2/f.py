import bz2,json,lzma,re,zlib

def _var(n):
 b=bytearray()
 while n>127:
  b.append((n&127)|128);n>>=7
 b.append(n)
 return b

def _read(b,p):
 n=s=0
 while True:
  c=b[p];p+=1;n|=(c&127)<<s
  if c<128:return n,p
  s+=7

def _pack(d):
 templates=[];ids={};out=bytearray()
 for line in d.split(b'\n'):
  n=len(line)
  if n>=16 and n%2==0 and re.fullmatch(b'[0-9a-f]+',line):
   out.append(0);out.extend(_var(n));out.extend(bytes.fromhex(line.decode('ascii')))
  elif 16<=n<=4096 and re.fullmatch(b'[0-9a-z]+',line):
   out.append(1);out.extend(_var(n));out.extend(int(line,36).to_bytes((n*517+799)//800,'big'))
  else:
   parts=re.split(b'([0-9]+)',line)
   if any(len(t)>1000 for t in parts[1::2]):
    out.append(2);out.extend(_var(n));out.extend(line);continue
   key=tuple(p if i%2==0 else len(p) for i,p in enumerate(parts))
   if key not in ids:
    ids[key]=len(templates);templates.append([p.decode('latin1') if isinstance(p,bytes) else p for p in key])
   out.extend(_var(ids[key]+3))
   for p in parts[1::2]:out.extend(int(p).to_bytes((len(p)*3322+7999)//8000,'big'))
 header=json.dumps(templates,separators=(',',':'),ensure_ascii=True).encode('ascii')
 return bytes(_var(len(header)))+header+out

def _unpack(b):
 n,p=_read(b,0);templates=json.loads(b[p:p+n]);p+=n;lines=[]
 while p<len(b):
  kind,p=_read(b,p)
  if kind<3:
   n,p=_read(b,p)
   if kind==0:
    size=n//2;line=b[p:p+size].hex().encode('ascii')
   elif kind==1:
    size=(n*517+799)//800;v=int.from_bytes(b[p:p+size],'big');chars=bytearray()
    for _ in range(n):
     v,r=divmod(v,36);chars.append(b'0123456789abcdefghijklmnopqrstuvwxyz'[r])
    line=bytes(reversed(chars))
   else:size=n;line=b[p:p+size]
   p+=size
  else:
   parts=[]
   for t in templates[kind-3]:
    if isinstance(t,str):parts.append(t.encode('latin1'))
    else:
     size=(t*3322+7999)//8000;parts.append(str(int.from_bytes(b[p:p+size],'big')).zfill(t).encode('ascii'));p+=size
   line=b''.join(parts)
  lines.append(line)
 return b'\n'.join(lines)

def enc(d):
 if not d:return b''
 choices=[b'\x00'+d]
 for mode,data in ((0,d),(1,_pack(d))):
  for codec,fun in enumerate((lambda b:lzma.compress(b,preset=9),bz2.compress,lambda b:zlib.compress(b,9))):choices.append(bytes([1+mode*3+codec])+fun(data))
 return min(choices,key=len)

def dec(z):
 if not z:return b''
 if z[0]==0:return z[1:]
 mode,codec=divmod(z[0]-1,3)
 b=(lzma.decompress,bz2.decompress,zlib.decompress)[codec](z[1:])
 return _unpack(b) if mode else b
