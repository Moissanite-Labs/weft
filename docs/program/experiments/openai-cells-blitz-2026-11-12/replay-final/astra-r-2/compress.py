import bz2
import json
import sys


def compress(data):
    best = b'B' + bz2.compress(data, 9)
    try:
        lines = data.splitlines(keepends=True)
        fields = [line[:-1].split(b' ', 1) for line in lines]
        width = len(fields[0][0])
        bodies, suffixes = zip(*(rest.rsplit(b' ', 1) for _, rest in fields))
        nums = list(map(int, suffixes))
        modulus = max(nums) + 1
        start = nums[0]
        step = (nums[1] - start) % modulus
        first = int(fields[0][0])
        meta = [first, width, start, step, modulus]
        rebuilt = b''.join(str(first+i).zfill(width).encode() + b' ' + body + b' ' + str((start+i*step)%modulus).encode() + b'\n' for i, body in enumerate(bodies))
        if rebuilt == data:
            payload = json.dumps(meta).encode() + b'\n' + b'\n'.join(bodies)
            candidate = b'S' + bz2.compress(payload, 9)
            if len(candidate) < len(best):
                best = candidate
    except (ValueError, IndexError, ZeroDivisionError):
        pass
    return best


def decompress(data):
    payload = bz2.decompress(data[1:])
    if data[:1] == b'B':
        return payload
    if data[:1] != b'S':
        raise ValueError('invalid format')
    header, payload = payload.split(b'\n', 1)
    first, width, start, step, modulus = json.loads(header)
    return b''.join(str(first+i).zfill(width).encode() + b' ' + body + b' ' + str((start+i*step)%modulus).encode() + b'\n' for i, body in enumerate(payload.split(b'\n')))


if __name__ == '__main__':
    args = sys.argv[1:]
    decode = args and args[0] == '--decompress'
    if decode:
        args = args[1:]
    if len(args) != 2:
        raise SystemExit('usage: compress.py [--decompress] input output')
    with open(args[0], 'rb') as f:
        data = f.read()
    result = decompress(data) if decode else compress(data)
    with open(args[1], 'wb') as f:
        f.write(result)
