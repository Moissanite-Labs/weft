#!/usr/bin/env python3
"""
Pipe-safe Markdown table splitter and two-tier tamper audit for certificate checkers.
(`tools/audit_weft_integrity.py`)
=======================================================================================
Two small utilities for the claims-ledger tooling carried by this repository:

  1. `split_markdown_table_row_pipe_safe(line)`. Splits a Markdown pipe-table row on
     unescaped `|` characters outside inline backtick code spans, so mathematical norm
     bars such as `` `|e_p| <= delta` `` and `\\|x\\|` escapes never split a cell.
     The naive `line.split("|")` truncates those cells and corrupts ledger rows.
  2. `probe_json_certificate_tamper_in_memory(cert_obj, verifier_fn)`. Two probes that
     show whether `verifier_fn` checks the mathematical witness rather than the outer
     SHA-256 alone. Probe 1 flips a nibble of the outer digest without changing the
     body. Probe 2 mutates one inner leaf at a time, nested fields included, AND
     recomputes a valid outer digest. A lazy hash-only verifier accepts every such
     mutation. A witness-checking verifier rejects the one its witness depends on.

The pattern was ported from the offline integrity layer of Foundation-0/project-asma
PR #80 (claims-ledger export, SHA-256 manifest check, checker audit) and adapted for
this repository. Derived from a peer bundle dropped 2026-11-13 (Gemini task agent,
Apache-2.0). Reviewed, trimmed and rewritten here. See issue #175 for the verification
and the reasons the rest of that bundle was not landed.

License: Apache-2.0. Mandate: No token. No sale. Nothing on-chain.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable, Dict, List, Optional


def _backtick_run(line: str, i: int) -> int:
    j = i
    while j < len(line) and line[j] == "`":
        j += 1
    return j - i


def _find_closing_run(line: str, start: int, width: int) -> int:
    """Index of the next backtick run of exactly `width` at or after `start`, or -1."""
    i = start
    while i < len(line):
        if line[i] == "`":
            run = _backtick_run(line, i)
            if run == width:
                return i
            i += run
            continue
        i += 1
    return -1


def split_markdown_table_row_pipe_safe(line: str) -> List[str]:
    """
    Splits a Markdown pipe-table row on unescaped `|` characters OUTSIDE backticked
    code spans (fixing the naive `line.split("|")` truncation on `` `|x|` `` norms).

    A run of N backticks opens a code span that only a later run of exactly N
    backticks closes, as in CommonMark, so `` ``|x|`` `` and `` `` `|` `` `` stay
    whole. Text inside a code span is copied verbatim, backslashes included.
    Outside a span, `\\|`, `` \\` `` and `\\\\` unescape to the next character. An
    opening run with no matching close is kept as a span to the end of the row,
    so a stray backtick never causes a split inside what may be code.
    """
    cells: List[str] = []
    buf: List[str] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "\\" and i + 1 < n and line[i + 1] in ("|", "`", "\\"):
            buf.append(line[i + 1])
            i += 2
            continue
        if ch == "`":
            width = _backtick_run(line, i)
            close = _find_closing_run(line, i + width, width)
            if close < 0:
                buf.append(line[i:])
                i = n
                continue
            buf.append(line[i : close + width])
            i = close + width
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        cells.append("".join(buf).strip())
    # Trim leading and trailing empty cells from outer `| ... |` borders
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def canonical_json_sha256(obj: Dict[str, Any], digest_key: str = "certificate_sha256") -> str:
    body = {k: v for k, v in obj.items() if k != digest_key}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


Path = List[Any]

# Field names that read as a conclusion rather than an input. Only used to order
# the probe-2 mutations so verdicts are tried first; every leaf is still tried.
_VERDICT_TOKENS = ("ok", "valid", "verified", "holds", "claim", "feasible", "pass", "accept", "certif")
_BOUND_TOKENS = ("eps_star", "bound", "flow", "score", "deficit", "commits", "max", "min")
_RATIONAL_RE = re.compile(r"-?\d+/\d+")
MAX_PROBE2_MUTATIONS = 512


def _mutable_leaves(node: Any, path: Path, out: List[Path]) -> None:
    if isinstance(node, dict):
        for k in sorted(node.keys(), key=str):
            _mutable_leaves(node[k], path + [k], out)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            _mutable_leaves(item, path + [idx], out)
    elif isinstance(node, bool) or isinstance(node, int) or isinstance(node, float):
        out.append(path)
    elif isinstance(node, str) and _RATIONAL_RE.fullmatch(node):
        out.append(path)


def _leaf_rank(path: Path) -> tuple:
    names = [str(p).lower() for p in path if isinstance(p, str)]
    last = names[-1] if names else ""
    if any(tok in last for tok in _VERDICT_TOKENS):
        tier = 0
    elif any(tok in last for tok in _BOUND_TOKENS):
        tier = 1
    else:
        tier = 2
    return (tier, len(path), [str(p) for p in path])


def _get_path(obj: Any, path: Path) -> Any:
    for p in path:
        obj = obj[p]
    return obj


def _mutate_leaf(obj: Any, path: Path) -> bool:
    parent = _get_path(obj, path[:-1])
    key = path[-1]
    v = parent[key]
    if isinstance(v, bool):
        parent[key] = not v
    elif isinstance(v, int):
        parent[key] = v + 1
    elif isinstance(v, float):
        if v != v or v in (float("inf"), float("-inf")):
            return False
        parent[key] = v + 1.0 if abs(v) < 1e15 else v * 2.0
    elif isinstance(v, str) and _RATIONAL_RE.fullmatch(v):
        num_s, den_s = v.split("/")
        parent[key] = f"{int(num_s) + 1}/{den_s}"
    else:
        return False
    return True


def _accepts(verifier_fn: Callable[[Dict[str, Any]], bool], cert: Dict[str, Any]) -> bool:
    """True only if the verifier returns True. A raise counts as a rejection."""
    try:
        return verifier_fn(cert) is True
    except Exception:
        return False


def probe_json_certificate_tamper_in_memory(
    cert_obj: Dict[str, Any],
    verifier_fn: Callable[[Dict[str, Any]], bool],
    *,
    digest_key: str = "certificate_sha256",
    verdict_paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """
    Two-tier tamper audit for a certificate-like JSON object:

      - Probe 1 (Hash flip). Flips nibble 0 of `digest_key` without changing the body.
        A missing, empty or non-string digest returns a reason instead of raising.
      - Probe 2 (Re-hashed semantic leaf mutation). Walks every boolean, integer,
        float and `num/den` leaf, nested objects and lists included, mutates one leaf
        at a time and recomputes `digest_key` validly.

    Without `verdict_paths`, probe 2 fails with `rehashed_semantic_tamper_accepted`
    only when the verifier accepts every single-leaf mutation, so the field the
    witness depends on has been tried. The result lists `mutated_paths`. If any
    mutation is rejected the probe passes and reports that leaf as `rejected_path`.
    With `verdict_paths`, each named leaf must be rejected after mutation; the first
    accepted one is reported as `mutated_path`.

    Returns {"ok": True, "probes_passed": 2, ...} only if both tiers are rejected.
    """
    if not _accepts(verifier_fn, cert_obj):
        return {"ok": False, "reason": "baseline_certificate_rejected"}

    # Probe 1: Outer hash nibble flip
    if digest_key not in cert_obj:
        return {"ok": False, "reason": "digest_missing"}
    old_sha = cert_obj[digest_key]
    if not isinstance(old_sha, str):
        return {"ok": False, "reason": "digest_not_a_string"}
    if old_sha == "":
        return {"ok": False, "reason": "digest_empty"}
    t_hash = json.loads(json.dumps(cert_obj))
    t_hash[digest_key] = ("0" if old_sha[0] != "0" else "1") + old_sha[1:]
    if _accepts(verifier_fn, t_hash):
        return {"ok": False, "reason": "hash_tamper_accepted"}

    # Probe 2: single-leaf semantic mutation + valid outer SHA-256 recomputation.
    body = {k: v for k, v in cert_obj.items() if k != digest_key}

    def tamper(path: Path) -> Optional[Dict[str, Any]]:
        t_sem = json.loads(json.dumps(cert_obj))
        if not _mutate_leaf(t_sem, path):
            return None
        t_sem[digest_key] = canonical_json_sha256(t_sem, digest_key=digest_key)
        return t_sem

    if verdict_paths is not None:
        for path in verdict_paths:
            path = list(path)
            try:
                t_sem = tamper(path)
            except (KeyError, IndexError, TypeError):
                return {"ok": False, "reason": "verdict_path_not_found", "mutated_path": path}
            if t_sem is None:
                return {"ok": False, "reason": "verdict_path_not_mutable", "mutated_path": path}
            if _accepts(verifier_fn, t_sem):
                return {"ok": False, "reason": "rehashed_semantic_tamper_accepted", "mutated_path": path}
        return {"ok": True, "probes_passed": 2, "rejected_paths": [list(p) for p in verdict_paths]}

    leaves: List[Path] = []
    _mutable_leaves(body, [], leaves)
    leaves.sort(key=_leaf_rank)
    if len(leaves) > MAX_PROBE2_MUTATIONS:
        return {"ok": False, "reason": "too_many_semantic_fields", "field_count": len(leaves)}
    tried: List[Path] = []
    for path in leaves:
        t_sem = tamper(path)
        if t_sem is None:
            continue
        tried.append(path)
        if not _accepts(verifier_fn, t_sem):
            return {"ok": True, "probes_passed": 2, "rejected_path": path}
    if not tried:
        return {"ok": False, "reason": "no_mutable_semantic_field_found"}
    return {"ok": False, "reason": "rehashed_semantic_tamper_accepted", "mutated_paths": tried}
