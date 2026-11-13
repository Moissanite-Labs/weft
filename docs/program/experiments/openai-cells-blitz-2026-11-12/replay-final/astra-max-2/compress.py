#!/usr/bin/env python3
"""Lossless, standard-library-only file compression.

Usage: python3 compress.py input.txt output.bin
       python3 compress.py --decompress input.bin output.txt
"""
import argparse
import bz2
from pathlib import Path


def compress(data: bytes) -> bytes:
    return bz2.compress(data, compresslevel=9)


def decompress(data: bytes) -> bytes:
    return bz2.decompress(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--decompress', action='store_true')
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    operation = decompress if args.decompress else compress
    try:
        result = operation(args.source.read_bytes())
        args.destination.write_bytes(result)
    except (OSError, EOFError, ValueError) as exc:
        parser.exit(1, f'{parser.prog}: {exc}\n')


if __name__ == '__main__':
    main()
