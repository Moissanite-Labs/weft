#!/usr/bin/env python3
"""
SYM-2P positional packet codec for Aywa telemetry → shader uniform mapping.
Extracted from weft/design/craft.md and weft/design/build.md.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def encode_sym2p_line(
    *,
    role: int = 1,
    action_state: int = 3,
    sequence: int = 1,
    metrics: dict[str, float | int],
) -> str:
    parts = " ".join(f"({key} {value})" for key, value in metrics.items())
    payload = f"[s-exp {parts}]"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f":{role:02d}:{action_state:02d}:{sequence:04d}{payload}{digest}"


def parse_sym2p_line(line: str) -> dict[str, Any]:
    line = line.strip()
    if not line.startswith(":"):
        raise ValueError("SYM-2P line must begin with role byte marker ':'")
    role = int(line[1:3], 16) if len(line) >= 3 else 0
    action_state = int(line[4:6], 16) if len(line) >= 6 else 0
    sequence = int(line[7:11], 16) if len(line) >= 11 else 0
    payload_start = line.find("[")
    payload_end = line.rfind("]")
    if payload_start < 0 or payload_end < 0:
        raise ValueError("SYM-2P payload s-expression missing")
    payload = line[payload_start + 1 : payload_end].strip()
    trailing = line[payload_end + 1 :]
    claimed_hash = trailing[:64] if len(trailing) >= 64 else ""
    payload_for_hash = line[payload_start : payload_end + 1]
    computed = hashlib.sha256(payload_for_hash.encode("utf-8")).hexdigest()
    metrics: dict[str, float] = {}
    for match in re.finditer(r"\((\w+)\s+([\d.]+)\)", payload):
        metrics[match.group(1)] = float(match.group(2))
    return {
        "role": role,
        "action_state": action_state,
        "sequence": sequence,
        "metrics": metrics,
        "hash_valid": (not claimed_hash) or (claimed_hash == computed),
    }


def telemetry_payload_from_harvest(data: dict[str, Any]) -> str:
    metrics = {
        "active_nodes": int(data.get("active_nodes", 0)),
        "tension": float(data.get("org_tension", 0.0)),
        "gini": float(data.get("gini_index", 0.0)),
    }
    return encode_sym2p_line(sequence=1, metrics=metrics)


if __name__ == "__main__":
    sample = encode_sym2p_line(metrics={"active_nodes": 19, "tension": 0.24, "gini": 0.28})
    parsed = parse_sym2p_line(sample)
    print(sample)
    print(parsed)
