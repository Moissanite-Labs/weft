#!/usr/bin/env python3
"""Lossless standalone compressor using the Python standard library."""
import lzma
import sys
from pathlib import Path

def compress(data):
    return lzma.compress(data, preset=9)

def decompress(data):
    return lzma.decompress(data)

def main():
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    Path(args[1]).write_bytes((decompress if decode else compress)(Path(args[0]).read_bytes()))

if __name__ == '__main__':
    main()
