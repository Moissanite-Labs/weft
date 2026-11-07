#!/usr/bin/env python3
"""Compatibility re-export for `weft.runtime.telemetry.sym2p_codec` (Codebase C6 / Interface I2)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.telemetry.sym2p_codec import (  # noqa: E402
    encode_sym2p,
    encode_sym2p_line,
    parse_sym2p,
    parse_sym2p_line,
    telemetry_payload_from_harvest,
)

__all__ = [
    "encode_sym2p",
    "encode_sym2p_line",
    "parse_sym2p",
    "parse_sym2p_line",
    "telemetry_payload_from_harvest",
]
