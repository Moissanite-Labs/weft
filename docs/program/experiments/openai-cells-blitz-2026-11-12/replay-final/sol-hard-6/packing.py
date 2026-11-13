"""Bit-pack the three telemetry integers into 70 bits."""
def pack(a, b, c):
    return ((a << 50) | (b << 30) | c).to_bytes(9, 'big')

def unpack(data, p):
    n = int.from_bytes(data[p:p+9], 'big')
    return n >> 50, (n >> 30) & ((1 << 20) - 1), n & ((1 << 30) - 1), p + 9
