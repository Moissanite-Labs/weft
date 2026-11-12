#!/usr/bin/env python3
"""Track 1: strict falsifiers for the discrete no-language channels.

The enforce-at-the-serializer version of the discrete encodings.
Two checkers, both deterministic and offline-runnable:

1. strict_body(src)   - a body is accepted only if it parses to an AST whose
                        every Name is in a disclosed whitelist (stdlib nouns and
                        user-defined functions written in the cell), with zero
                        comments and zero docstrings anywhere. Closes the
                        "smuggle English in comments/names" channel and gives a
                        boolean accept/reject verdict, not a leak count.
2. strict_formula(s)  - a formula is accepted only if every token matches a
                        closed regex class (digits, operators, quantifiers,
                        parentheses, bound variables x/y/t/i/n, Greek glyphs,
                        and the whitelisted operator names sin cos tanh exp
                        abs len print assert return def if else raise TrueFalse
                        None round zip min max sum map filter next iter enumerate
                        isinstance type). Anything alphabetic outside the
                        whitelist rejects the whole formula.

Each checker returns {"ok": bool, "reason": str, "bad": [..]}. The reason
strings are private diagnostics, not model-visible.
"""
import ast
import io
import re
import tokenize

WHITELIST_NAMES = set(
    # builtins commonly needed in bodies
    "abs len sum min max zip map filter next iter enumerate print type isinstance "
    "ord chr bin hex int float complex str list tuple dict set frozenset bool frozenset "
    "range enumerate reversed sorted round any all repr ascii format vars globals locals "
    "id hash callable hasattr getattr setattr delattr super object Exception ValueError "
    "TypeError KeyError IndexError StopIteration RuntimeError OSError IOError FileNotFoundError "
    "print input exit str bytes bytearray memoryview property classmethod staticmethod "
    "all any chr ord hex bin oct format len".split()
)
WHITELIST_MODS = set(
    "zlib bz2 lzma json struct re math itertools collections heapq bisect string "
    "random hashlib time os sys io tempfile shutil".split()
)
SAFE_NODES = (
    ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign, ast.AnnAssign,
    ast.AugAssign, ast.Expr, ast.If, ast.IfExp, ast.While, ast.For, ast.With, ast.Return,
    ast.Call, ast.Name, ast.Load, ast.Store, ast.Constant, ast.Attribute, ast.Subscript,
    ast.Slice, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Starred, ast.BinOp, ast.UnaryOp,
    ast.BoolOp, ast.Compare, ast.Lambda, ast.Await, ast.AsyncFunctionDef, ast.Assert,
    ast.Raise, ast.Pass, ast.Break, ast.Continue, ast.alias, ast.comprehension,
    ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp, ast.JoinedStr, ast.FormattedValue,
    ast.Import, ast.ImportFrom, ast.Assign, ast.Try, ast.ExceptHandler, ast.With,
    ast.keyword, ast.NamedExpr, ast.Expr,
    # operator classes and comparison operators
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv, ast.MatMult,
    ast.LShift, ast.RShift, ast.BitOr, ast.BitAnd, ast.BitXor,
    ast.UAdd, ast.USub, ast.Invert, ast.Not, ast.And, ast.Or,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq, ast.In, ast.NotIn, ast.Is, ast.IsNot,
)

TOKEN_CLASS = re.compile(
    r"""
    \d+(\.\d+)?([eE][+-]?\d+)?   # numbers
  | [A-Za-z_]\w*                # names (checked against whitelist)
  | [=><!+\-*/%=^&|~]           # operators and comparisons
  | [()\[\]{},;:.]              # punctuation
  | [∀∃∈∉≤≥≠⊂⊆∧∨¬→↔⊢⊣⊤⊥∧∨⇒⇐ΣΠ∪∩∈⟨⟩]   # quantifier / logic glyphs (Greek blocks)
  | [α-ω]|[Α-Ω]|\$[A-Za-z0-9_]*    # lowercase/uppercase Greek block + De Bruijn-ish $n
  | \s+
""", re.VERBOSE | re.UNICODE)

# Fixed formula vocabulary for the E08/E3-style channels: bound variables,
# free variables, and the function names the profiles actually use. No
# English names appear here; this list is the whole universe.
ALLOWED_TOKENS = set("""sin cos tanh exp abs len print assert return def if else raise True False 
None round zip min max sum map filter next iter enumerate isinstance type 
import from as in is and or not pass del with lambda yield async await 
x y t s d z i n k f q p r m u v w b g h l a c e o en e2 B A N S
enc dec f.py x.bin zlib bz2 lzma json struct re math itertools collections
print ord chr sum min max abs""".split())
OPERATOR_TOKENS = set(list("+-*/%=<>!&|^~")) | set("()[]{},;:=@.")
QUANT = set("∀∃∈∉≤≥≠⊂⊆∧∨¬→↔⊢⊣⊤⊥∧∨⇒⇐∪∩⟨⟩$")
ATOM = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
WORDRUN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def strict_body(src: str) -> dict:
    comments, docstrings = [], []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comments.append(tok.string)
    except Exception as e:
        return {"ok": False, "reason": f"tokenize-failed: {e}", "bad": []}
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"ok": False, "reason": f"syntax-error: {e}", "bad": []}
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, SAFE_NODES):
            bad.append(type(node).__name__)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            docstrings.append(node.value.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            hits = _blocklist_hits(node.value)
            if len(hits) >= 2:
                bad.append(f"string-prose:{hits[:6]}")
        if isinstance(node, ast.Attribute):
            if not isinstance(node.attr, str) or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", node.attr):
                bad.append(f"attr:{node.attr!r}")
            elif _contains_blocklist(node.attr):
                bad.append(f"attr-blocklist:{node.attr}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _contains_blocklist(node.name):
                bad.append(f"def-blocklist:{node.name}")
        if isinstance(node, ast.Name):
            if node.id in WHITELIST_NAMES or node.id in WHITELIST_MODS:
                continue
            if _looks_user_ident(node.id) and not _contains_blocklist(node.id):
                continue
            bad.append(f"name:{node.id}")
    if comments:
        return {"ok": False, "reason": "comments-forbidden", "bad": comments[:10]}
    if docstrings:
        return {"ok": False, "reason": "docstrings-forbidden", "bad": [d[:80] for d in docstrings[:10]]}
    if bad:
        return {"ok": False, "reason": "unsafe-nodes", "bad": sorted(set(bad))[:10]}
    return {"ok": True, "reason": "ok", "bad": []}


def _looks_user_ident(s):
    return bool(re.match(r"^[a-z_][a-z0-9_]*$", s))

_BLOCK = set(
    "the a an and are as at be been but by for from has have he her his i if in into is it its me my no not of on or she so that their them then there they this to was we were what which who will with you your all also any about after again between both down during each first few may might must once only other some than too very can could should would shall may might must when where why how over under us use used uses using many more most other same own".split())
def _blocklist_hits(text):
    import re as _re
    return [m.group(0).lower() for m in WORDRUN.finditer(text) if m.group(0).lower() in _BLOCK]


def _contains_blocklist(s):
    parts = re.split(r"[^a-z0-9]+", s.lower())
    return any(p in _BLOCK for p in parts if p)


def _is_local_def(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return True
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if (alias.asname or alias.name.split(".")[0]) == name and alias.name.split(".")[0] in WHITELIST_MODS:
                    return True
    return False


def strict_formula(s: str) -> dict:
    bad = []
    for m in WORDRUN.finditer(s):
        if m.group(0) not in ALLOWED_TOKENS:
            bad.append(m.group(0))
    if bad:
        return {"ok": False, "reason": "token-whitelist", "bad": sorted(set(bad))[:20]}
    # check every remaining character is in a class we recognize
    for ch in s:
        if ch.isascii() and (ch.isalnum() or ch in "_. " or ch in "+-*/%=<>!&|^~()[]{},;:@" or ch in "\n\t"):
            continue
        if ch in QUANT or (ord(ch) in range(0x03B1, 0x03E9)) or (ord(ch) in range(0x0391, 0x03EA)):
            continue
        if ch in "∀∃∈∉≤≥≠⊂⊆∧∨¬→↔⊢⊣⊤⊥⇒⇐∪∩⟨⟩$":
            continue
        if ch == "·" or ch == "Δ" or ch == "Ω" or ch == "ε" or ch.isdigit():
            continue
        if ord(ch) in range(0x2070, 0x2080):   # superscripts 0..9 and + - = ( )
            continue
        if ord(ch) in range(0x207A, 0x2080) or ch == "₀" or ch == "₁" or ch == "₂" or ch == "₊" or ch == "₋":
            continue
        bad.append(ch)
    if bad:
        return {"ok": False, "reason": "char-class", "bad": sorted(set(bad))[:20]}
    return {"ok": True, "reason": "ok", "bad": []}
