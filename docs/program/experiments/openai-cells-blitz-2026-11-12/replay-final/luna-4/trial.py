import re,collections,bz2,lzma,zlib
x=open('corpus.txt','rb').read(); lines=x.splitlines(keepends=True)
pat=re.compile(rb'([0-9]{5}) (.*) ([0-9]+)\n')
rows=[pat.fullmatch(l).groups() for l in lines]
f=collections.Counter(r[1] for r in rows); d={b:i for i,(b,n) in enumerate(f.most_common())}
def vi(n):
 o=bytearray()
 while n>=128:o.append((n&127)|128);n>>=7
 o.append(n);return o
v=bytearray(b'LINE1'); v.extend(vi(len(d)))
for b,i in sorted(d.items(),key=lambda x:x[1]):v.extend(vi(len(b)));v.extend(b)
v.extend(vi(len(rows))); prev=0
for a,b,c in rows:
 n=int(a);v.extend(vi(n-prev));prev=n;v.extend(vi(d[b]));v.extend(vi(int(c)))
print('trans',len(v),'bz',len(bz2.compress(v)),'z',len(zlib.compress(v)),'lz',len(lzma.compress(v)))
