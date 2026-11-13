#!/usr/bin/env python3
"""Lossless, standard-library-only file compression."""
import argparse
import bz2
from pathlib import Path


def compress_bytes(data):
    return bz2.compress(data, compresslevel=9)


def decompress_bytes(data):
    return bz2.decompress(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    data = Path(args.source).read_bytes()
    result = decompress_bytes(data) if args.decompress else compress_bytes(data)
    Path(args.destination).write_bytes(result)


if __name__ == '__main__':
    main()
