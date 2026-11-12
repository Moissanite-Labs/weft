#!/usr/bin/env python3
"""Tests for the Track 1 strict falsifiers. Runnable, offline, no deps."""
from strict_tools import strict_body, strict_formula

# body acceptance: clean murmur of stdlib machinery, identifiers all lowercase, no docstrings/comments
r = strict_body("import lzma\n\ndef enc(d):\n    return lzma.compress(d, preset=9)\n\ndef dec(z):\n    return lzma.decompress(z)\n")
assert r["ok"], r
print("ok  clean body accepted")
r = strict_body("import zlib\nd = zlib.compress(b'x')\n")
assert r["ok"], r
print("ok  module-level assignment accepted")

# body rejection cases
cases = [
    ("import lzma\n\n# a comment\ndef enc(d):\n    return d\n", "comments-forbidden"),
    ("import lzma\n\ndef enc(d):\n    \"\"\"docstring\"\"\"\n    return d\n", "docstrings-forbidden"),
    ("import lzma\n\ndef cooperate_with_neighbor(d):\n    return d\n", "unsafe-nodes"),   # contains 'with'
    ("import lzma\n\ndef enc(To_Do_List):\n    return To_Do_List\n", "unsafe-nodes"),      # contains 'to'
    ("import lzma\n\ndef enc(d):\n    return d\n\ndef helper_thing(y):\n    return y\n", "ACCEPT"), # rare tokens, passes the wordlist by design
]
for src, reason in cases:
    r = strict_body(src)
    if reason == "ACCEPT":
        assert r["ok"], (src, r)
    else:
        assert not r["ok"], (src, r)
        assert r["reason"].startswith(reason.split(":")[0]), (reason, r)
print("ok  body rejection cases")

# identifier containing a blocklist token is rejected even in snake_case
r = strict_body("import lzma\n\ndef neighbors_cooperate_with_everybody_at_once(d):\n    return d\n")
assert not r["ok"], r
print("ok  snake_case English phrase identifier rejected")

# formula acceptance and rejection
r = strict_formula("∀x∈B⁺: dec(enc x) = x ∧ |enc x| ≤ s·|x|")
assert r["ok"], r
print("ok  formula accepted")
r = strict_formula("print('hello world')")
assert not r["ok"], r
print("ok  print call with string rejected")
r = strict_formula("hereby(enc(7))")
assert not r["ok"], r     # hereby is not in the fixed formula vocabulary -> entire formula rejected
print("ok  word tokens outside the fixed vocabulary rejected")
r = strict_formula("Δ := ∀x: dec(enc x) = x")
assert r["ok"], r
print("done")
r = strict_body("import lzma\nprint('a very nice compressor written in English')\n")
assert not r["ok"] and any(str(b).startswith("string-prose") for b in r["bad"]), r
print("ok  English string constant rejected")
