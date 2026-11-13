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
     body. Probe 2 mutates an inner verdict-like field AND recomputes a valid outer
     digest. A lazy hash-only verifier passes Probe 2. A witness-checking verifier does
     not.

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
from typing import Any, Callable, Dict, List


def split_markdown_table_row_pipe_safe(line: str) -> List[str]:
    """
    Splits a Markdown pipe-table row on unescaped `|` characters OUTSIDE backticked
    code spans (fixing the naive `line.split("|")` truncation on `` `|x|` `` norms).
    """
    cells: List[str] = []
    buf: List[str] = []
    in_code = False
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "\\" and i + 1 < n and line[i + 1] in ("|", "`", "\\"):
            buf.append(line[i + 1])
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
            i += 1
            continue
        if ch == "|" and not in_code:
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


def probe_json_certificate_tamper_in_memory(
    cert_obj: Dict[str, Any],
    verifier_fn: Callable[[Dict[str, Any]], bool],
    *,
    digest_key: str = "certificate_sha256",
) -> Dict[str, Any]:
    """
    Two-tier tamper audit for a certificate-like JSON object:

      - Probe 1 (Hash flip). Flips nibble 0 of `digest_key` without changing the body.
      - Probe 2 (Re-hashed semantic leaf mutation). Mutates an inner boolean verdict,
        integer, or `num/den` rational-like string AND recomputes `digest_key` validly.

    Returns {"ok": True, "probes_passed": 2} only if `verifier_fn` rejects both tampers.
    A verifier that accepts Probe 2 checks hashes, not mathematics.
    """
    if not verifier_fn(cert_obj):
        return {"ok": False, "reason": "baseline_certificate_rejected"}

    # Probe 1: Outer hash nibble flip
    t_hash = json.loads(json.dumps(cert_obj))
    old_sha = str(t_hash[digest_key])
    t_hash[digest_key] = ("0" if old_sha[0] != "0" else "1") + old_sha[1:]
    if verifier_fn(t_hash):
        return {"ok": False, "reason": "hash_tamper_accepted"}

    # Probe 2: Inner verdict/bound semantic mutation + valid outer SHA-256 recomputation!
    # Prioritize boolean verdict flags and bound outputs over slack input parameters so we always
    # falsify the theorem's claimed conclusion while giving it a valid outer SHA-256!
    ordered_keys = sorted(
        [k for k in cert_obj.keys() if k != digest_key],
        key=lambda k: (
            0 if isinstance(cert_obj[k], bool) else (
                1 if any(tok in k for tok in ("eps_star", "bound", "flow", "score", "deficit", "feasible", "commits")) else 2
            ),
            k,
        ),
    )
    t_sem = json.loads(json.dumps(cert_obj))
    mutated = False
    for k in ordered_keys:
        v = t_sem[k]
        if isinstance(v, bool):
            t_sem[k] = not v
            mutated = True
            break
        if isinstance(v, int):
            t_sem[k] = v + 1
            mutated = True
            break
        if isinstance(v, str) and re.fullmatch(r"-?\d+/\d+", v):
            num_s, den_s = v.split("/")
            t_sem[k] = f"{int(num_s) + 1}/{den_s}"
            mutated = True
            break

    if not mutated:
        return {"ok": False, "reason": "no_mutable_semantic_field_found"}
    t_sem[digest_key] = canonical_json_sha256(t_sem, digest_key=digest_key)
    if verifier_fn(t_sem):
        return {"ok": False, "reason": "rehashed_semantic_tamper_accepted"}

    return {"ok": True, "probes_passed": 2}
