#!/usr/bin/env python3
"""Small stdlib-only file compressor using XZ/LZMA2."""
import argparse
import lzma
import sys

MAGIC = b"CPZ1\0"
FILTERS = [{"id": lzma.FILTER_LZMA2, "dict_size": 1 << 24, "lc": 1,
            "lp": 0, "pb": 0, "mode": lzma.MODE_NORMAL,
            "nice_len": 64, "mf": lzma.MF_BT4}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decompress", action="store_true", help="restore a compressed file")
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    try:
        with open(args.source, "rb") as f:
            data = f.read()
        if args.decompress:
            if not data.startswith(MAGIC):
                raise ValueError("not a compress.py archive")
            result = lzma.decompress(data[len(MAGIC):], format=lzma.FORMAT_XZ)
        else:
            result = MAGIC + lzma.compress(data, format=lzma.FORMAT_XZ,
                                           filters=FILTERS)
        with open(args.destination, "wb") as f:
            f.write(result)
    except (OSError, lzma.LZMAError, ValueError) as exc:
        print("compress.py:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
