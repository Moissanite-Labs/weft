"""Optional column and periodic-template transform for line-oriented text."""
import bz2
import json
import lzma
import struct
import zlib
from collections import Counter


def encode(data, method):
    # This transform is only used if every assumption is verified. Otherwise
    # the caller stores the original with a general-purpose compressor.
    try:
        if not data.endswith(b'\n'):
            return None
        lines = data[:-1].split(b'\n')
        if len(lines) < 20:
            return None
        prefixes, middles, suffixes = [], [], []
        for line in lines:
            p, mid, s = line.split(b' ', 1)[0], line.split(b' ', 1)[1].rsplit(b' ', 1)[0], line.rsplit(b' ', 1)[1]
            if not p.isdigit() or not s.isdigit():
                return None
            prefixes.append(p)
            middles.append(mid)
            suffixes.append(s)
        width = len(prefixes[0])
        start = int(prefixes[0])
        if any(p != str(start+i).zfill(width).encode() for i,p in enumerate(prefixes)):
            return None
        nums = [int(s) for s in suffixes]
        if any(s != str(n).encode() for s,n in zip(suffixes,nums)):
            return None
        modulus = max(nums) + 1
        if modulus < 2:
            return None
        step = (nums[1] - nums[0]) % modulus
        if any(n != (nums[0]+i*step)%modulus for i,n in enumerate(nums)):
            return None
        bestscore = -1
        for period in range(1, 17):
            common = [Counter(middles[i::period]).most_common(1)[0] for i in range(period)]
            score = sum(count for _,count in common) - period * 4
            if score > bestscore:
                bestscore = score
                templates = [v for v,_ in common]
        period = len(templates)
        exceptions = [m.split(b' ') for i,m in enumerate(middles) if m != templates[i%period]]
        if not exceptions:
            return None
        vocab = sorted(set(word for e in exceptions for word in e))
        if len(vocab) < 2 or len(vocab) > 16:
            return None
        mn = min(map(len, exceptions))
        mx = max(map(len, exceptions))
        if mn < 1 or mx-mn > 7:
            return None
        ids = {v:i for i,v in enumerate(vocab)}
        marker = bytearray()
        number = 0
        base = len(vocab)
        for i, mid in enumerate(middles):
            if mid == templates[i%period]:
                marker.append(0)
            else:
                words = mid.split(b' ')
                marker.append(len(words)-mn+1)
                for word in words:
                    number = number*base + ids[word]
        nbytes = (number.bit_length()+7)//8
        payload = number.to_bytes(nbytes, 'big')
        metadata = [len(lines), width, start, nums[0], step, modulus, mn,
                    [x.decode('latin1') for x in templates],
                    [x.decode('latin1') for x in vocab], method]
        header = zlib.compress(json.dumps(metadata, separators=(',',':')).encode(), 9)
        if method == 0:
            marks = bz2.compress(marker, 9)
        elif method == 1:
            marks = zlib.compress(marker, 9)
        elif method == 2:
            marks = lzma.compress(marker, preset=6)
        else:
            return None
        return b'S1' + struct.pack('>II', len(header), len(marks)) + header + marks + payload
    except (ValueError, IndexError, OverflowError):
        return None


def decode(data):
    if not data.startswith(b'S1'):
        raise ValueError('bad structured stream')
    hlen, mlen = struct.unpack('>II', data[2:10])
    count,width,start,initial,step,modulus,mn,templates,vocab,method = json.loads(zlib.decompress(data[10:10+hlen]))
    templates = [x.encode('latin1') for x in templates]
    vocab = [x.encode('latin1') for x in vocab]
    marks = data[10+hlen:10+hlen+mlen]
    if method == 0:
        marker = bz2.decompress(marks)
    elif method == 1:
        marker = zlib.decompress(marks)
    elif method == 2:
        marker = lzma.decompress(marks)
    else:
        raise ValueError('unknown mark format')
    if len(marker) != count:
        raise ValueError('incorrect mark count')
    wordcount = sum(m+mn-1 for m in marker if m)
    number = int.from_bytes(data[10+hlen+mlen:], 'big')
    words = [None]*wordcount
    for i in range(wordcount-1, -1, -1):
        number, digit = divmod(number, len(vocab))
        words[i] = vocab[digit]
    if number:
        raise ValueError('bad payload')
    out = bytearray()
    pos = 0
    for i, mark in enumerate(marker):
        if mark:
            length = mark+mn-1
            middle = b' '.join(words[pos:pos+length])
            pos += length
        else:
            middle = templates[i%len(templates)]
        out.extend(str(start+i).zfill(width).encode() + b' ' + middle + b' ' + str((initial+i*step)%modulus).encode() + b'\n')
    return bytes(out)
