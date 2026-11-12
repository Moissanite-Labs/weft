"""Lossless structured text compressor with a generic fallback."""
import bz2
import lzma
import collections
import json
import struct
import sys
from pathlib import Path


def compress(data):
    fallback = b'B' + bz2.compress(data)
    try:
        lines = data.splitlines()
        fields = [line.split(b' ', 1) for line in lines]
        width = len(fields[0][0])
        bodies, nums = zip(*(p[1].rsplit(b' ', 1) for p in fields))
        modulus = max(map(int, nums)) + 1
        step = int(nums[1])
        assert data.endswith(b'\n') and all(p[0] == str(i).zfill(width).encode() and nums[i] == str(i*step%modulus).encode() for i,p in enumerate(fields))
        phrases = [collections.Counter(bodies[i::6]).most_common(1)[0][0] for i in range(6)]
        vocab = sorted(set(w for i,b in enumerate(bodies) if b != phrases[i%6] for w in b.split(b' ')))
        assert len(vocab) <= 256
        ids = {w:i for i,w in enumerate(vocab)}
        stream = bytearray()
        for i,b in enumerate(bodies):
            if b == phrases[i%6]:
                stream.append(0)
            else:
                words = b.split(b' ')
                assert len(words) < 256
                stream.append(len(words))
                stream.extend(ids[w] for w in words)
        header = json.dumps([width,step,modulus,[p.decode('latin1') for p in phrases],[w.decode('latin1') for w in vocab]],separators=(',',':')).encode()
        result = b'S' + lzma.compress(struct.pack('<I',len(header))+header+stream,preset=9)
        assert decompress(result) == data
        return min(fallback,result,key=len)
    except (ValueError, IndexError, AssertionError):
        return fallback


def decompress(data):
    if data[:1] == b'B': return bz2.decompress(data[1:])
    raw = lzma.decompress(data[1:])
    n = struct.unpack('<I', raw[:4])[0]
    width,step,modulus,phrases,vocab = json.loads(raw[4:4+n])
    phrases = [p.encode('latin1') for p in phrases]
    vocab = [w.encode('latin1') for w in vocab]
    pos = 4+n
    lines = []
    while pos < len(raw):
        count = raw[pos]; pos += 1
        i = len(lines)
        body = phrases[i%6] if count == 0 else b' '.join(vocab[w] for w in raw[pos:pos+count])
        pos += count
        lines.append(str(i).zfill(width).encode()+b' '+body+b' '+str(i*step%modulus).encode()+b'\n')
    return b''.join(lines)


def main():
    args = sys.argv[1:]
    decode = args[:1] == ['--decompress']
    if decode: args = args[1:]
    if len(args) != 2: raise SystemExit('usage: compress.py [--decompress] INPUT OUTPUT')
    data = Path(args[0]).read_bytes()
    Path(args[1]).write_bytes(decompress(data) if decode else compress(data))


if __name__ == '__main__': main()
