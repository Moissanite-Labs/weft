import sys, bz2, marshal, collections

def compress(data):
    raw = b'B' + bz2.compress(data, 9)
    try:
        lines = data.splitlines()
        rows = [line.split(b' ') for line in lines]
        n = len(rows)
        width = len(rows[0][0])
        first = int(rows[0][0])
        step = int(rows[1][0]) - first
        last = [int(r[-1]) for r in rows]
        modulus = max(last) + 1
        delta = (last[1] - last[0]) % modulus
        assert all(r[0] == str(first + i*step).zfill(width).encode() and r[-1] == str((last[0]+i*delta)%modulus).encode() for i,r in enumerate(rows))
        words = [w for r in rows for w in r[1:-1]]
        vocab = [w for w,c in collections.Counter(words).most_common()]
        assert len(vocab) < 255
        ids = {w:i+1 for i,w in enumerate(vocab)}
        text = b'\x00'.join(bytes(ids[w] for w in r[1:-1]) for r in rows)
        obj = (n,width,first,step,last[0],delta,modulus,vocab,text,data.endswith(b'\n'))
        packed = b'S' + bz2.compress(marshal.dumps(obj),9)
        if len(packed)<len(raw) and decompress(packed)==data:
            return packed
    except (ValueError,IndexError,AssertionError):
        pass
    return raw

def decompress(data):
    if data[:1] == b'B':
        return bz2.decompress(data[1:])
    n,width,first,step,start,delta,modulus,vocab,text,newline = marshal.loads(bz2.decompress(data[1:]))
    lines=[]
    for i,row in enumerate(text.split(b'\x00')):
        lines.append(str(first+i*step).zfill(width).encode()+b' '+b' '.join(vocab[v-1] for v in row)+b' '+str((start+i*delta)%modulus).encode())
    return b'\n'.join(lines)+(b'\n' if newline else b'')

def main():
    args=sys.argv[1:]
    decode=bool(args and args[0]=='--decompress')
    if decode: args=args[1:]
    if len(args)!=2: raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    with open(args[0],'rb') as f: data=f.read()
    result=decompress(data) if decode else compress(data)
    with open(args[1],'wb') as f: f.write(result)

if __name__=='__main__': main()
