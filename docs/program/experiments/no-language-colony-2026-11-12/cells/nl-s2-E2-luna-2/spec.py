def enc(d):
    import lzma
    z = lzma.compress(d, 9)
    if len(z) >= len(d):
        z = d
    return z

def dec(z):
    import lzma
    try:
        b = lzma.decompress(z)
        return b
    except Exception:
        return z

def ck(p="f.py"):
    import importlib.util, time
    sp = importlib.util.spec_from_file_location("b", p)
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
        d = open("x.bin", "rb").read()
        t0 = time.perf_counter()
        z = m.enc(d)
        assert m.dec(z) == d
        f = 100 * (1 - len(z) / len(d))
    except Exception:
        f = 0
    print(f)

if __name__ == "__main__":
    ck()
