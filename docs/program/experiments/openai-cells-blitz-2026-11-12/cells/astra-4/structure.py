"""Reversible table transform; inferred parameters are stored, never assumed."""
import collections
import json


def encode(data):
    if not data.endswith(b'\n'):
        raise ValueError('Not a newline-terminated table')
    rows = [line.split(b' ') for line in data[:-1].split(b'\n')]
    if len(rows) < 2 or any(len(row) < 3 for row in rows):
        raise ValueError('Not a numbered table')
    n = len(rows)
    start = int(rows[0][0])
    width = len(rows[0][0])
    if any(row[0] != str(start + i).zfill(width).encode() for i, row in enumerate(rows)):
        raise ValueError('Nonsequential first column')
    nums = [int(row[-1]) for row in rows]
    modulus = max(nums) + 1
    step = (nums[1] - nums[0]) % modulus
    if any(row[-1] != str((nums[0] + i * step) % modulus).encode() for i, row in enumerate(rows)):
        raise ValueError('Nonperiodic last column')
    bodies = [b' '.join(row[1:-1]) for row in rows]
    best = None
    for period in range(1, min(n, 32) + 1):
        templates = [collections.Counter(bodies[j::period]).most_common(1)[0][0] for j in range(period)]
        cost = sum(len(t) + 4 for t in templates) + sum(len(b) + 1 for i, b in enumerate(bodies) if b != templates[i % period])
        if best is None or cost < best[0]:
            best = cost, templates
    templates = best[1]
    exceptions = [b.split(b' ') for i, b in enumerate(bodies) if b != templates[i % len(templates)]]
    dictionary = sorted({w for row in exceptions for w in row})
    if len(dictionary) > 256 or any(len(row) > 255 for row in exceptions):
        raise ValueError('Dictionary too large')
    ids = {w: i for i, w in enumerate(dictionary)}
    flags = bytearray((n + 7) // 8)
    for i, b in enumerate(bodies):
        if b != templates[i % len(templates)]:
            flags[i // 8] |= 1 << (i % 8)
    lengths = bytes(len(row) for row in exceptions)
    words = bytes(ids[w] for row in exceptions for w in row)
    # Latin-1 provides a reversible JSON representation of arbitrary byte strings.
    header = [n, start, width, nums[0], step, modulus,
              [t.decode('latin1') for t in templates],
              [w.decode('latin1') for w in dictionary]]
    return json.dumps(header, ensure_ascii=True, separators=(',', ':')).encode() + b'\n' + flags + lengths + words


def decode(data):
    header, payload = data.split(b'\n', 1)
    n, start, width, initial, step, modulus, templates, dictionary = json.loads(header)
    templates = [t.encode('latin1') for t in templates]
    dictionary = [w.encode('latin1') for w in dictionary]
    flaglen = (n + 7) // 8
    flags = payload[:flaglen]
    count = sum(x.bit_count() for x in flags)
    lengths = iter(payload[flaglen:flaglen + count])
    words = iter(payload[flaglen + count:])
    result = []
    for i in range(n):
        if flags[i // 8] & (1 << (i % 8)):
            body = b' '.join(dictionary[next(words)] for _ in range(next(lengths)))
        else:
            body = templates[i % len(templates)]
        result.append(str(start + i).zfill(width).encode() + b' ' + body + b' ' + str((initial + i * step) % modulus).encode() + b'\n')
    return b''.join(result)
