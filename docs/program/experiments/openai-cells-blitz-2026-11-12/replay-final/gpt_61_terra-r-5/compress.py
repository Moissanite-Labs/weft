import bz2, collections, json, math, struct, sys

def encode(data):
    fallback = b'B' + bz2.compress(data, 9)
    try:
        lines = data.splitlines()
        assert len(lines) >= 100 and data == b'\n'.join(lines) + b'\n'
        rows = [line.split(b' ', 1) for line in lines]
        nums = [x[0] for x in rows]
        width = len(nums[0]); first = int(nums[0])
        assert all(x == str(first+i).zfill(width).encode() for i,x in enumerate(nums))
        parts = [x[1].rsplit(b' ', 1) for x in rows]
        texts = [x[0] for x in parts]
        ends = [int(x[1]) for x in parts]
        assert all(x[1] == str(n).encode() for x,n in zip(parts,ends))
        start = ends[0]; step = ends[1]-start; mod = 0
        for i,n in enumerate(ends): mod = math.gcd(mod, n-start-i*step)
        assert mod > 1 and all(n == (start+i*step)%mod for i,n in enumerate(ends))
        templates = [collections.Counter(texts[i::6]).most_common(1)[0][0] for i in range(6)]
        residual = [x.split(b' ') if x != templates[i%6] else [] for i,x in enumerate(texts)]
        assert all(len(x)<256 and b' '.join(x)==texts[i] for i,x in enumerate(residual) if x)
        words = sorted({w for row in residual for w in row})
        assert 2 <= len(words) <= 255 and all(words)
        word_index = {w:i for i,w in enumerate(words)}
        value = 0
        for row in residual:
            for w in row: value = value*len(words)+word_index[w]
        payload = value.to_bytes((value.bit_length()+7)//8, 'big')
        meta = dict(t=[x.decode('ascii') for x in templates], w=[x.decode('ascii') for x in words], a=first, q=width, e=start, d=step, m=mod)
        header = json.dumps(meta, separators=(',',':')).encode()+b'\n'+bytes(map(len,residual))
        compressed = bz2.compress(header, 9)
        result = b'S'+struct.pack('>I',len(compressed))+compressed+payload
        return min((fallback,result), key=len)
    except (ValueError, IndexError, AssertionError, UnicodeError, OverflowError):
        return fallback

def decode(data):
    if data[:1] == b'B': return bz2.decompress(data[1:])
    if data[:1] != b'S': raise ValueError('invalid compressed file')
    size = struct.unpack('>I',data[1:5])[0]
    header, lengths = bz2.decompress(data[5:5+size]).split(b'\n',1)
    m = json.loads(header); words = [w.encode('ascii') for w in m['w']]; templates = [t.encode('ascii') for t in m['t']]
    value = int.from_bytes(data[5+size:],'big'); indices = []
    for _ in range(sum(lengths)):
        value, digit = divmod(value,len(words)); indices.append(digit)
    indices.reverse(); it = iter(indices); lines = []
    for i,n in enumerate(lengths):
        text = b' '.join(words[next(it)] for _ in range(n)) if n else templates[i%6]
        lines.append(str(m['a']+i).zfill(m['q']).encode()+b' '+text+b' '+str((m['e']+i*m['d'])%m['m']).encode())
    return b'\n'.join(lines)+b'\n'

def main():
    if len(sys.argv)==4 and sys.argv[1]=='--decompress':
        src,dst=sys.argv[2:]; fn=decode
    elif len(sys.argv)==3:
        src,dst=sys.argv[1:]; fn=encode
    else: raise SystemExit('usage: compress.py [--decompress] input output')
    with open(src,'rb') as f: data=f.read()
    with open(dst,'wb') as f: f.write(fn(data))
if __name__ == '__main__': main()
