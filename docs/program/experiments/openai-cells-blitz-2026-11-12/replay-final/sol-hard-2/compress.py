import sys,bz2
A=b'0123456789abcdefghijklmnopqrstuvwxyz'
B=36**64
M=10**21
def w(r,n):return ((r**n-1).bit_length()+7)//8
def encode(data):
 ls=data.splitlines(keepends=True); n=len(ls); tags=0; hs=bytearray(); b=m=0; nb=nm=0
 for line in ls:
  if not line.endswith(b'\n'):break
  s=line[:-1]
  if len(s)==96 and all(c in b'0123456789abcdef' for c in s):
   typ=0;hs.extend(bytes.fromhex(s.decode()))
  elif len(s)==64 and all(c in A for c in s):
   typ=1;b=b*B+int(s,36);nb+=1
  elif s.startswith(b'e18a line '):
   x=s.split()
   if len(x)!=10 or x[0:2]!=[b'e18a',b'line'] or x[3]!=b'ratio' or x[5:9]!=[b'select',b'pick',b'win',b'seed']:break
   try:
    line_num=int(x[2]);seed=int(x[9]);r=x[4]
    if len(r)!=8 or r[:2]!=b'0.' or not r[2:].isdigit() or x[2]!=str(line_num).encode() or x[9]!=str(seed).encode() or not 0<=line_num<1000000 or not 0<=seed<1000000000:break
    ratio=int(r[2:])
   except ValueError:break
   typ=2;m=m*M+(line_num*1000000+ratio)*1000000000+seed;nm+=1
  else:break
  tags=tags*3+typ
 else:
  return b'T'+n.to_bytes(4,'big')+tags.to_bytes(w(3,n),'big')+hs+b.to_bytes(w(B,nb),'big')+m.to_bytes(w(M,nm),'big')
 return b'B'+bz2.compress(data,9)
def decode(data):
 if data[:1]==b'B':return bz2.decompress(data[1:])
 n=int.from_bytes(data[1:5],'big');p=5;t=int.from_bytes(data[p:p+w(3,n)],'big');p+=w(3,n)
 types=[]
 for _ in range(n):t,v=divmod(t,3);types.append(v)
 types.reverse()
 nh=types.count(0);nb=types.count(1);nm=types.count(2)
 h=data[p:p+48*nh];p+=48*nh;b=int.from_bytes(data[p:p+w(B,nb)],'big');p+=w(B,nb);m=int.from_bytes(data[p:p+w(M,nm)],'big');p+=w(M,nm)
 bl=[];ml=[]
 for _ in range(nb):
  b,v=divmod(b,B);buf=bytearray(64)
  for i in range(63,-1,-1):v,d=divmod(v,36);buf[i]=A[d]
  bl.append(bytes(buf))
 bl.reverse()
 for _ in range(nm):
  m,v=divmod(m,M);v,seed=divmod(v,1000000000);ln,r=divmod(v,1000000)
  ml.append(b'e18a line %d ratio 0.%06d select pick win seed %d'%(ln,r,seed))
 ml.reverse();out=bytearray();hi=bi=mi=0
 for typ in types:
  if typ==0:out.extend(h[hi:hi+48].hex().encode());hi+=48
  elif typ==1:out.extend(bl[bi]);bi+=1
  else:out.extend(ml[mi]);mi+=1
  out.append(10)
 return bytes(out)
def main():
 args=sys.argv[1:]
 if len(args)==3 and args[0]=='--decompress':open(args[2],'wb').write(decode(open(args[1],'rb').read()))
 elif len(args)==2:open(args[1],'wb').write(encode(open(args[0],'rb').read()))
 else:raise SystemExit('usage: compress.py [--decompress] input output')
if __name__=='__main__':main()
