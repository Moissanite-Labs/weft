#!/usr/bin/env python3
import sys
import bz2

def compress(data):
    return b'BZ' + bz2.compress(data, compresslevel=9)

def decompress(data):
    if not data.startswith(b'BZ'):
        raise ValueError('unknown compression format')
    return bz2.decompress(data[2:])

def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == '--decompress':
        func, source, target = decompress, args[1], args[2]
    elif len(args) == 2:
        func, source, target = compress, args[0], args[1]
    else:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(source, 'rb') as f:
        data = f.read()
    result = func(data)
    with open(target, 'wb') as f:
        f.write(result)

if __name__ == '__main__':
    main()
