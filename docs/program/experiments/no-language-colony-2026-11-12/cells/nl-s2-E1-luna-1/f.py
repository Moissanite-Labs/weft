import sys
import zlib
import bz2
import lzma

MAGIC = b'FZ1'

def enc(data):
    # Pick the smallest representation among standard lossless codecs.
    candidates = [
        b'\x00' + data,
        b'\x01' + zlib.compress(data, 9),
        b'\x02' + bz2.compress(data, compresslevel=9),
        b'\x03' + lzma.compress(data, preset=9),
    ]
    body = min(candidates, key=len)
    return MAGIC + body

def dec(data):
    if not data.startswith(MAGIC) or len(data) < len(MAGIC) + 1:
        raise ValueError('bad stream')
    tag, body = data[3], data[4:]
    if tag == 0:
        return body
    if tag == 1:
        return zlib.decompress(body)
    if tag == 2:
        return bz2.decompress(body)
    if tag == 3:
        return lzma.decompress(body)
    raise ValueError('unknown codec')

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('enc', 'dec'):
        raise SystemExit('usage: f.py enc|dec')
    data = sys.stdin.buffer.read()
    sys.stdout.buffer.write(enc(data) if sys.argv[1] == 'enc' else dec(data))

if __name__ == '__main__':
    main()
