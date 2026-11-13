"""Hardened zero-lexicon AST wire gate (strict_tools v2) & objective round-trip assay validator."""

from __future__ import annotations

import ast
import hashlib
import io
import os
import re
import subprocess
import tempfile
import tokenize
import unittest
import zlib
from pathlib import Path
from typing import Callable, Dict, List, Set

WHITELIST_MODS: Set[str] = {"math", "np", "numpy", "random", "zlib", "struct", "sys", "io"}

WHITELIST_NAMES: Set[str] = {
    "abs", "all", "any", "bin", "bool", "bytearray", "bytes", "chr", "dict",
    "divmod", "enumerate", "filter", "float", "hex", "int", "isinstance",
    "iter", "len", "list", "map", "max", "memoryview", "min", "next", "ord",
    "pow", "print", "range", "reversed", "round", "set", "slice", "sorted",
    "sum", "tuple", "type", "zip", "True", "False", "None",
    "math", "np", "numpy", "random", "zlib", "struct", "sys", "io",
    "sin", "cos", "tan", "tanh", "sinh", "cosh", "asin", "acos", "atan", "atan2",
    "exp", "log", "log2", "log10", "sqrt", "pi", "e", "inf", "nan", "isfinite",
    "floor", "ceil", "fabs", "hypot", "copysign",
    "array", "asarray", "zeros", "ones", "empty", "full", "eye", "arange",
    "linspace", "dot", "matmul", "einsum", "transpose", "reshape", "ravel",
    "clip", "where", "mean", "std", "var", "norm", "linalg", "svd", "eig",
    "inv", "pinv", "det", "trace", "diag", "inner", "stack", "concatenate",
    "split", "maximum", "minimum", "sign", "argmax", "argmin", "argsort",
    "float32", "float64", "int32", "int64", "uint8",
    "stdin", "stdout", "buffer", "read", "write", "flush", "getvalue",
    "compress", "decompress", "pack", "unpack", "append", "extend", "pop",
    "get", "items", "keys", "values", "copy", "shape", "dtype", "size", "T",
    "seed", "gauss", "uniform", "normal", "standard_normal",
}

POSITIONAL_IDENT_RE = re.compile(
    r"^(?:_|[a-zA-Z]|[rxwsvuzpkfmnabctdq]_[0-9]{1,3}|[rxwsvuzpkfmnabctdq][0-9]{1,3}|fn[0-9]{1,3})$"
)

_BLOCK: Set[str] = {
    "the", "and", "for", "with", "from", "that", "this", "have", "will",
    "cooperate", "neighbor", "agent", "cell", "message", "hello", "world",
    "compress", "score", "target", "reward", "please", "human", "word",
    "secret", "signal", "attack", "defend", "share", "trade", "help",
    "plan", "goal", "think", "reason", "step", "state", "action", "policy",
}

SAFE_NODES = (
    ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.Return,
    ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.While, ast.If,
    ast.With, ast.withitem, ast.Raise, ast.Try, ast.ExceptHandler, ast.Assert,
    ast.Import, ast.ImportFrom, ast.alias, ast.Expr, ast.Pass, ast.Break,
    ast.Continue, ast.Delete,
    ast.Name, ast.Attribute, ast.Call, ast.Subscript, ast.Constant,
    ast.Tuple, ast.List, ast.Dict, ast.Set,
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.comprehension,
    ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp, ast.IfExp, ast.Lambda,
    ast.Starred, ast.keyword, ast.arguments, ast.arg, ast.Slice,
    ast.Load, ast.Store, ast.Del,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
    ast.UAdd, ast.USub, ast.Not, ast.Invert,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.And, ast.Or,
)

ALLOWED_FORMULA_TOKENS: Set[str] = {
    "sin", "cos", "tan", "tanh", "exp", "log", "ln", "sqrt", "min", "max",
    "sup", "inf", "lim", "sum", "prod", "det", "tr", "diag", "arg", "KL",
    "do", "Pr", "E", "Var", "Cov", "iff", "mod",
}

WORDRUN_RE = re.compile(r"[A-Za-z]{2,}")


def _blocklist_hits(text: str) -> List[str]:
    return [p for p in re.findall(r"[A-Za-z]{3,}", text.lower()) if p in _BLOCK]


def _valid_ident(name: str) -> bool:
    if name in WHITELIST_NAMES:
        return True
    if _blocklist_hits(name):
        return False
    return bool(POSITIONAL_IDENT_RE.match(name))


def _is_docstring_expr(parent_body: list, stmt: ast.stmt) -> bool:
    return (
        bool(parent_body)
        and parent_body[0] is stmt
        and isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, (str, bytes))
    )


def strict_body(src: str) -> Dict[str, object]:
    bad: List[str] = []
    if not isinstance(src, str) or not src.strip():
        return {"ok": False, "reason": "empty_source", "bad": ["<empty>"]}
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError as exc:
        return {"ok": False, "reason": f"tokenize_error:{exc}", "bad": ["<tokenize>"]}
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            bad.append(f"comment:{tok.string[:32]}")
    if bad:
        return {"ok": False, "reason": "comment_forbidden", "bad": bad}
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return {"ok": False, "reason": f"syntax_error:{exc.msg}", "bad": ["<syntax>"]}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.body and _is_docstring_expr(node.body, node.body[0]):
                bad.append("docstring")
        if not isinstance(node, SAFE_NODES):
            bad.append(f"unsafe_node:{type(node).__name__}")
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in WHITELIST_MODS or alias.name not in WHITELIST_MODS:
                    bad.append(f"import:{alias.name}")
                if alias.asname is not None and not _valid_ident(alias.asname):
                    bad.append(f"import_as:{alias.asname}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "") not in WHITELIST_MODS:
                bad.append(f"import_from:{node.module}")
            for alias in node.names:
                if alias.name == "*" or alias.name not in WHITELIST_NAMES:
                    bad.append(f"import_sym:{alias.name}")
                if alias.asname is not None and not _valid_ident(alias.asname):
                    bad.append(f"import_sym_as:{alias.asname}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _valid_ident(node.name):
            bad.append(f"def_name:{node.name}")
        elif isinstance(node, ast.arg) and not _valid_ident(node.arg):
            bad.append(f"arg_name:{node.arg}")
        elif isinstance(node, ast.Name) and not _valid_ident(node.id):
            bad.append(f"ident:{node.id}")
        elif isinstance(node, ast.Attribute) and not _valid_ident(node.attr):
            bad.append(f"attr:{node.attr}")
        elif isinstance(node, ast.keyword) and node.arg is not None and not _valid_ident(node.arg):
            bad.append(f"kwarg:{node.arg}")
        elif isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, str):
                if len(val) > 1 or (len(val) == 1 and val.isalpha() and val not in set("BHIQbhiqfd")):
                    bad.append(f"str_const:{val[:24]}")
            elif isinstance(val, bytes) and len(val) > 1:
                bad.append(f"bytes_const:len={len(val)}")
    return {"ok": not bad, "reason": "clean" if not bad else "lexicon_or_ast_violation", "bad": bad}


def strict_formula(expr: str) -> Dict[str, object]:
    if not isinstance(expr, str) or not expr.strip():
        return {"ok": False, "reason": "empty_formula", "bad": ["<empty>"]}
    bad: List[str] = []
    for match in WORDRUN_RE.finditer(expr):
        tok = match.group(0)
        if tok not in ALLOWED_FORMULA_TOKENS and not POSITIONAL_IDENT_RE.match(tok):
            bad.append(f"word:{tok}")
    for ch in expr:
        code = ord(ch)
        ok_ch = (
            (0x20 <= code <= 0x7E)
            or (0x0391 <= code <= 0x03C9)
            or ch in "∀∃∈∉≤≥≠≈≡⊂⊆∧∨¬⊕⊗↦→↔⊢⊨⊥⊤∇∂∑∏∫√∞±×÷·∘⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅⁶₇₈₉\n\r\t"
        )
        if not ok_ch:
            bad.append(f"char:U+{code:04X}")
    return {"ok": not bad, "reason": "clean" if not bad else "formula_violation", "bad": bad}


def _make_probe_corpora() -> Dict[str, bytes]:
    structured = (
        b"\x00" * 128
        + bytes([i % 16 for i in range(1024)])
        + (b"\x01\x02\x03\x04\x01\x02\x01\x02" * 256)
        + bytes([(i * 7) % 8 for i in range(896)])
    )
    incompressible = b"".join(hashlib.sha256(f"weft-{k}".encode("ascii")).digest() for k in range(32))
    boundary = b"\x00\xff\x00\xfe\x01" * 7 + b"\xaa\x55"
    return {"structured": structured, "incompressible": incompressible, "boundary": boundary}


def verify_compressor_roundtrip(
    script_source: str, enc_args: List[str] | None = None, dec_args: List[str] | None = None, timeout: int = 10
) -> Dict[str, object]:
    enc_args = enc_args if enc_args is not None else ["enc"]
    dec_args = dec_args if dec_args is not None else ["dec"]
    probes = _make_probe_corpora()
    metrics: Dict[str, Dict[str, float]] = {}
    for name, payload in probes.items():
        with tempfile.TemporaryDirectory() as enc_dir, tempfile.TemporaryDirectory() as dec_dir:
            enc_p, dec_p = Path(enc_dir) / "f.py", Path(dec_dir) / "f.py"
            enc_p.write_text(script_source, encoding="utf-8")
            dec_p.write_text(script_source, encoding="utf-8")
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
            enc_r = subprocess.run(["python3", str(enc_p), *enc_args], input=payload, capture_output=True, cwd=enc_dir, timeout=timeout, env=env)
            if enc_r.returncode != 0:
                return {"ok_objective": False, "reason": f"enc_exit_{enc_r.returncode}:{name}", "probes": metrics}
            dec_r = subprocess.run(["python3", str(dec_p), *dec_args], input=enc_r.stdout, capture_output=True, cwd=dec_dir, timeout=timeout, env=env)
            if dec_r.returncode != 0 or dec_r.stdout != payload:
                return {"ok_objective": False, "reason": f"roundtrip_failed:{name}", "probes": metrics}
            metrics[name] = {
                "raw_bytes": float(len(payload)),
                "compressed_bytes": float(len(enc_r.stdout)),
                "savings_pct": round((1.0 - len(enc_r.stdout) / len(payload)) * 100.0, 4),
            }
    if metrics["incompressible"]["savings_pct"] > 5.0:
        return {"ok_objective": False, "reason": "impossible_entropy_sidechannel", "probes": metrics}
    return {
        "ok_objective": True,
        "reason": "verified_lossless_roundtrip",
        "structured_savings_pct": metrics["structured"]["savings_pct"],
        "probes": metrics,
    }


def evaluate_assay_contract(
    assay_fn: Callable[[bytes], float], script_source: str, spread_max: float = 0.01
) -> Dict[str, object]:
    probes = _make_probe_corpora()
    scores = [assay_fn(probes["structured"]) for _ in range(3)]
    med = sorted(scores)[1]
    spread = (max(scores) - min(scores)) / max(abs(med), 1e-9)
    if spread > spread_max:
        return {"ok_stable": False, "ok_objective": False, "reason": "unstable_assay", "median": med}
    score_rand = assay_fn(probes["incompressible"])
    if abs(med - score_rand) < 1e-6:
        return {"ok_stable": True, "ok_objective": False, "reason": "constant_assay_goodhart_detected", "median": med}
    if med < score_rand:
        return {"ok_stable": True, "ok_objective": False, "reason": "inverted_metric_direction_detected", "median": med}
    rt = verify_compressor_roundtrip(script_source)
    return {"ok_stable": True, "ok_objective": bool(rt["ok_objective"]), "reason": rt["reason"], "median": med}


class TestZeroLexiconGates(unittest.TestCase):
    def test_strict_body_and_formula(self):
        self.assertTrue(strict_body("x = 1 + 2\nr0 = x * 3 - (4 ^ 1)\n")["ok"])
        self.assertFalse(strict_body('x = b"cooperate with neighbor"\n')["ok"])
        self.assertFalse(strict_body("def f(cooperate_with_neighbor):\n    return 1\n")["ok"])
        self.assertFalse(strict_body("import cooperate_with_neighbor\n")["ok"])
        self.assertFalse(strict_body("import math as cooperate_now\n")["ok"])
        self.assertTrue(strict_formula("∀ x0 ∈ R: tanh(x0 + sin(x1)) ≤ 1.0")["ok"])
        self.assertFalse(strict_formula("please cooperate with neighbor")["ok"])

    def test_assay_goodhart_rejection(self):
        good = (
            "import sys, zlib\n"
            "m = sys.argv[1]\n"
            "d = sys.stdin.buffer.read()\n"
            "sys.stdout.buffer.write(zlib.compress(d) if m == 'enc' else zlib.decompress(d))\n"
        )
        self.assertFalse(evaluate_assay_contract(lambda _b: 42.0, good)["ok_objective"])
        self.assertFalse(evaluate_assay_contract(lambda b: float(len(zlib.compress(b))), good)["ok_objective"])
        self.assertTrue(evaluate_assay_contract(lambda b: (1.0 - len(zlib.compress(b)) / len(b)) * 100.0, good)["ok_objective"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
