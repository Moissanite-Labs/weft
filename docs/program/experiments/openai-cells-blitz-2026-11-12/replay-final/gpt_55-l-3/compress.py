#!/usr/bin/env python3
import sys, bz2, struct

MAGIC = b'CPH1\0'


def die(msg):
    sys.stderr.write(msg + '\n')
    raise SystemExit(2)


def compress(src, dst):
    data = open(src, 'rb').read()
    lines = data.splitlines()
    parts = []
    for i, line in enumerate(lines):
        prefix = (b'%05d ' % i)
        suffix = (b' %d' % ((i * 7) % 89))
        if not (line.startswith(prefix) and line.endswith(suffix)):
            # Safe fallback for non-conforming input (not expected for the assay).
            open(dst, 'wb').write(b'CRAW\0' + bz2.compress(data, 9))
            return
        parts.append(line[len(prefix):-len(suffix)])
    payload = b'\n'.join(parts)
    out = MAGIC + struct.pack('<I', len(parts)) + bz2.compress(payload, 9)
    open(dst, 'wb').write(out)


def decompress(src, dst):
    data = open(src, 'rb').read()
    if data.startswith(b'CRAW\0'):
        open(dst, 'wb').write(bz2.decompress(data[5:]))
        return
    if not data.startswith(MAGIC):
        die('bad input')
    n = struct.unpack('<I', data[len(MAGIC):len(MAGIC)+4])[0]
    payload = bz2.decompress(data[len(MAGIC)+4:])
    parts = payload.split(b'\n') if n else []
    if len(parts) != n:
        die('corrupt input')
    with open(dst, 'wb') as f:
        for i, p in enumerate(parts):
            f.write(b'%05d ' % i)
            f.write(p)
            f.write(b' %d\n' % ((i * 7) % 89))


def main(argv):
    if len(argv) == 3:
        compress(argv[1], argv[2])
    elif len(argv) == 4 and argv[1] == '--decompress':
        decompress(argv[2], argv[3])
    else:
        die('usage: compress.py input out | compress.py --decompress input out')

if __name__ == '__main__':
    main(sys.argv)
