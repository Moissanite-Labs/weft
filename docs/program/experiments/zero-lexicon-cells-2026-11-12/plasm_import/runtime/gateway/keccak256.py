#!/usr/bin/env python3
"""
Pure-Python Keccak-256 (Ethereum / Solidity Event & Function Topic Hasher)
==========================================================================
Implements the original Keccak-f[1600] sponge with `0x01` domain separator
used by Ethereum (`keccak256`), distinct from NIST FIPS-202 SHA3-256 (`0x06`).
"""

from __future__ import annotations

RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]

ROT = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
]

MASK64 = (1 << 64) - 1


def _rol64(val: int, shift: int) -> int:
    return ((val << shift) | (val >> (64 - shift))) & MASK64


def _keccak_f1600(state: list[list[int]]) -> None:
    for rc in RC:
        c = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rol64(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x][y] ^= d[x]

        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rol64(state[x][y], ROT[x][y])

        for x in range(5):
            for y in range(5):
                state[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y])

        state[0][0] ^= rc


def keccak256(data: bytes | str) -> bytes:
    if isinstance(data, str):
        data = data.encode("utf-8")
    rate_bytes = 136  # (1600 - 512) // 8
    padded = bytearray(data)
    padded.append(0x01)
    while len(padded) % rate_bytes != 0:
        padded.append(0x00)
    padded[-1] |= 0x80

    state = [[0] * 5 for _ in range(5)]
    for offset in range(0, len(padded), rate_bytes):
        block = padded[offset : offset + rate_bytes]
        for i in range(rate_bytes // 8):
            lane = int.from_bytes(block[8 * i : 8 * (i + 1)], "little")
            state[i % 5][i // 5] ^= lane
        _keccak_f1600(state)

    out = bytearray()
    for y in range(5):
        for x in range(5):
            if len(out) < 32:
                out.extend(state[x][y].to_bytes(8, "little"))
    return bytes(out[:32])


def keccak256_hex(data: bytes | str, prefix: bool = True) -> str:
    digest = keccak256(data).hex()
    return f"0x{digest}" if prefix else digest
