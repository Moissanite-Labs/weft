import bz2,lzma,zlib,json,collections,struct
b=open('corpus.txt','rb').read();lines=b.splitlines(); bodies=[x.split(b' ',1)[1].rsplit(b' ',1)[0] for x in lines]
templates=[collections.Counter(bodies[j::6]).most_common(1)[0][0] for j in range(6)]
exc=[(i,x) for i,x in enumerate(bodies) if x!=templates[i%6]]
vocab=sorted(set(w for _,x in exc for w in x.split(b' ')));idx={w:i+1 for i,w in enumerate(vocab)}
head=json.dumps([len(lines),5,7,89,[x.decode() for x in templates],[x.decode() for x in vocab]],separators=(',',':')).encode()+b'\n'
flags=bytes(int(x!=templates[i%6]) for i,x in enumerate(bodies));gaps=bytes(i-(exc[j-1][0] if j else -1)-1 for j,(i,x) in enumerate(exc));lens=bytes(len(x.split(b' ')) for i,x in exc);words=bytes(idx[w] for i,x in exc for w in x.split(b' '));inter=b''.join(bytes([gaps[j],lens[j]])+bytes(idx[w] for w in x.split(b' ')) for j,(i,x) in enumerate(exc))
for name,raw in [('flags',head+flags+lens+words),('gaps',head+gaps+lens+words),('inter',head+inter)]:
 for cn,f in [('zlib',lambda b:zlib.compress(b,9)),('bz2',bz2.compress),('lzma',lambda b:lzma.compress(b,preset=9))]:
  print(name,cn,len(f(raw)))
print('exceptions',len(exc),'tokens',len(words),'maxgap',max(gaps))
