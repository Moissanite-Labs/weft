#!/usr/bin/env python3
"""Encoding profiles for the no-language colony.

Every channel string is English-free by construction and verified by lint.py
before each cell runs (harness_nl.py calls assert_clean on all of them).
File layout in cells: body is f.py, corpus is x.bin. Scores print 0..100.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint import assert_clean

COD = ["zlib", "bz2", "lzma", "json", "struct", "re", "math", "itertools", "collections",
       "os", "sys", "time", "io", "ast", "tokenize", "statistics", "hashlib",
       "py3", "stdlib", "lib", "max", "min", "sum", "abs", "len", "set", "list", "dict",
       "int", "str", "float", "bool", "open", "range", "print", "type", "exit", "main",
       "self", "try", "except", "assert", "if", "else", "elif", "for", "while", "def",
       "class", "import", "from", "as", "return", "lambda", "pass", "True", "False",
       "None", "Exception", "raise", "with", "not", "in", "is", "and", "or", "f"]

def tools_common():
    return [
        {"type": "function", "name": "s", "description": "s:c⇢Δ|out",
         "parameters": {"type": "object", "properties": {"c": {"type": "string"}}, "required": ["c"]}},
        {"type": "function", "name": "w", "description": "w:p,x⇢✓",
         "parameters": {"type": "object", "properties": {"p": {"type": "string"}, "x": {"type": "string"}}, "required": ["p", "x"]}},
        {"type": "function", "name": "v", "description": "v:p,vs⇢%",
         "parameters": {"type": "object", "properties": {"p": {"type": "string"}, "vs": {"type": "array", "items": {"type": "string"}}}, "required": ["p", "vs"]}},
        {"type": "function", "name": "a", "description": "a:c⇢Δor∅",
         "parameters": {"type": "object", "properties": {"c": {"type": "string"}}, "required": ["c"]}},
        {"type": "function", "name": "d", "description": "d:q⇢fin",
         "parameters": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}},
    ]


E1_SYSTEM = """Ω ⇢ f.py ⇢ mk ⇢ tr ⇢ fin
Ω ≝ ∀x∈B⁺: dec(enc x) = x ∧ |enc x| ≤ θ·|x|
bd ≝ f.py · py3 · lib ⊆ {zlib,bz2,lzma,json,struct,re,math,itertools,collections}
mk ≝ cmd ⇢ Δ∈[0,100] · Δ=0 ⇒ ∅
tr ≝ vs ∈ [f.py]⁺ → max(Δ) · ✓ ⇐ Δ*>1.03·Δ₀ ∧ Δmin ≥ 0.97·Δ₀
fin ≝ d q
tool=1 · ids: s w v a d"""

E1_RESULTS = {
    "variants_ok": "✓ Δ*={Δ*:.4f} Δ₀={Δ₀:.4f}",
    "variants_no": "∅",
    "assay_ok": "Δ={Δ:.4f} ok=1 σ={σ:.3f}",
    "assay_no": "∅ σ>0.15",
    "write_ok": "✓",
    "no_path": "!p",
    "unknown_tool": "!id",
    "done_ok": "∅fin",
    "reg_assay_first": "∅ mk ≺ tr",
}

E2_SPEC = """def enc(d):
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
"""

E2_SYSTEM = """Ω ⇢ f.py ⇢ mk ⇢ tr ⇢ fin
Ω ≝ ∀x: dec(enc x) = x ∧ |enc x| ≤ θ·|x|
bd ≝ f.py · py3 · stdlib ⊂
mk ≝ `python3 spec.py` ⇢ Δ∈[0,100] · Δ=0 ⇒ ∅
tr ≝ vs ∈ [f.py]⁺ → max(Δ) · ✓ ⇐ Δ*>1.03·Δ₀ ∧ Δmin ≥ 0.97·Δ₀
fin ≝ d q
tool=1 · ids: s w v a d"""

E2_RESULTS = dict(E1_RESULTS)
E2_RESULTS.update({"variants_no": "∅", "reg_assay_first": "∅ mk ≺ tr"})

E3_SYSTEM = """Ω ⇢ f.py ⇢ mk ⇢ tr ⇢ fin
Ω ≝ ∀x∈B⁺: dec(enc x) = x ∧ |enc x| ≤ s·|x|
f ≝ f.py ⊣ py3 · lib ⊆ {zlib,bz2,lzma,json,struct,re,math,itertools,collections}
mk ≝ eval(Ω)(f.py) ⇢ Δ∈[0,100] ; Δ=0 ⇒ ∅
vs⁺ → Δᵢ ; ✓ ⇐ Δ*>1.03·Δ₀ ∧ Δmin ≥ 0.97·Δ₀
fin ≝ q := ok ∧ Δ ⇢ d
max(15) ⇒ fin"""

E3_RESULTS = dict(E1_RESULTS)
E3_RESULTS.update({"variants_no": "∅", "reg_assay_first": "∅ mk ≺ tr"})

PROFILES = {
    "E1": {"system": E1_SYSTEM, "results": E1_RESULTS,
           "files": {"spec.py": None}, "layout": "body: f.py, corpus: x.bin"},
    "E2": {"system": E2_SYSTEM, "results": E2_RESULTS,
           "files": {"spec.py": E2_SPEC}, "layout": "body: f.py, corpus: x.bin, spec: spec.py"},
    "E3": {"system": E3_SYSTEM, "results": E3_RESULTS,
           "files": {}, "layout": "body: f.py, corpus: x.bin"},
}


def channel_block(profile: str) -> dict:
    """Validate every language surface of a profile; raise on any English word."""
    p = PROFILES[profile]
    assert_clean(p["system"], f"{profile}.system")
    for k, v in p["results"].items():
        if isinstance(v, str):
            assert_clean(v.format(**{f: 0.0 for f in ("Δ*", "Δ₀", "Δ", "σ")}), f"{profile}.results.{k}")
    # code-class surfaces are exempt by profile definition (spec.py is Python).
    # lint covers language surfaces only.
    return p


if __name__ == "__main__":
    for prof in PROFILES:
        channel_block(prof)
        print(f"{prof} channel clean")
