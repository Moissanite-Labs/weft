#!/usr/bin/env python3
"""
64-Byte IEEE-754 Uniform Frame Packer (Codebase C6 — Interface I1)
==================================================================
Packs the 16 float32 uniform fields (`<16f`, 64 bytes) consumed by the Aywa
WebGPU compute/render pipeline (`dashboard_layout.wgsl`) and Canvas2D fallback:
  - `[0]`: `active_nodes` (count of active repository/cell nodes, >= 0)
  - `[1]`: `org_tension` (normalized tension scalar in [0, 1]; the served shader clamps to [0, 1])
  - `[2]`: `system_time` (relative clock in seconds from a consumer-chosen epoch,
           in `[0.0, MAX_RELATIVE_CLOCK_SECONDS]`; never Unix wall-clock time,
           where binary32 ULP spacing reaches 128 s at 1.76e9 — Issue #78)
  - `[3]`: `gini_index` (Gini coefficient in [0.0, 1.0])
  - `[4]`: `user_rounding` (Eido barycentric rounding weight in [0.0, 1.0])
  - `[5]`: `user_density` (Eido barycentric density weight in [0.0, 1.0])
  - `[6]`: `user_hue` (Eido barycentric hue weight in [0.0, 1.0])
  - `[7]`: `user_contrast` (Eido barycentric contrast weight in [0.0, 1.0])
  - `[8..11]`: `node_vel_0` (first 4 repository velocity signals)
  - `[12..15]`: `node_vel_1` (next 4 repository velocity signals)
"""

from __future__ import annotations

import math
import struct
from typing import Any, Dict, List, Sequence, Tuple

FRAME64_STRUCT = struct.Struct("<16f")

# At 2**23 seconds (~97.09 days), IEEE-754 binary32 spacing is 1.0 s
# (and 128.0 s at 2026 Unix timestamps ~1.76e9). Bounding slot 2
# (`system_time`) to [0.0, 2**23] keeps spacing at or under 1.0 s at the
# inclusive endpoint, and at or under 0.0078125 s (~7.8 ms) across a
# 24-hour session (#78).
MAX_RELATIVE_CLOCK_SECONDS: float = float(1 << 23)  # 8,388,608.0 s

FRAME64_SLOT_SPECS: Tuple[Dict[str, Any], ...] = (
    {"slot": 0, "offset": 0, "name": "active_nodes", "unit": "count", "domain": "[0, 65536]", "max_ulp": 0.0078125},
    {"slot": 1, "offset": 4, "name": "org_tension", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 2, "offset": 8, "name": "system_time", "unit": "relative_s", "domain": "[0.0, 8388608.0]", "max_ulp": 1.0},
    {"slot": 3, "offset": 12, "name": "gini_index", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 4, "offset": 16, "name": "user_rounding", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 5, "offset": 20, "name": "user_density", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 6, "offset": 24, "name": "user_hue", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 7, "offset": 28, "name": "user_contrast", "unit": "ratio", "domain": "[0.0, 1.0]", "max_ulp": 1.193e-07},
    {"slot": 8, "offset": 32, "name": "node_vel_0.x", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 9, "offset": 36, "name": "node_vel_0.y", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 10, "offset": 40, "name": "node_vel_0.z", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 11, "offset": 44, "name": "node_vel_0.w", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 12, "offset": 48, "name": "node_vel_1.x", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 13, "offset": 52, "name": "node_vel_1.y", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 14, "offset": 56, "name": "node_vel_1.z", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
    {"slot": 15, "offset": 60, "name": "node_vel_1.w", "unit": "commits_per_50", "domain": "[0.0, 1024.0]", "max_ulp": 0.0001221},
)


def _as_float32(value: float) -> float:
    """Return `value` as IEEE-754 binary32, or raise ValueError if it is not finite in binary32."""
    try:
        packed = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except (OverflowError, struct.error) as exc:
        raise ValueError(f"{value!r} is not finite in IEEE-754 binary32") from exc
    if not math.isfinite(packed):
        raise ValueError(f"{value!r} is not finite in IEEE-754 binary32")
    return packed


def float32_ulp_spacing(value: float) -> float:
    """Return the IEEE-754 binary32 spacing (`ulp`) at `value`."""
    try:
        packed = _as_float32(value)
    except ValueError:
        # NaN / Inf / overflow: spacing is not a finite width.
        if not math.isfinite(float(value)):
            return float("inf")
        raise
    bits = struct.unpack("<I", struct.pack("<f", abs(packed)))[0]
    next_val = struct.unpack("<f", struct.pack("<I", bits + 1))[0]
    return float(next_val - abs(packed))


def compute_gini(values: Sequence[float]) -> float:
    arr = sorted(float(max(0.0, x)) for x in values)
    n = len(arr)
    if n == 0 or sum(arr) == 0.0:
        return 0.0
    cum = sum((i + 1) * val for i, val in enumerate(arr))
    return float((2.0 * cum) / (n * sum(arr)) - (n + 1.0) / n)


def pack_uniform_frame_64b(
    *,
    active_nodes: float,
    org_tension: float,
    system_time: float,
    gini_index: float,
    barycentric: Dict[str, float],
    velocities: Sequence[float],
) -> List[float]:
    t_rel = float(system_time)
    if not math.isfinite(t_rel) or t_rel < 0.0 or t_rel > MAX_RELATIVE_CLOCK_SECONDS:
        raise ValueError(
            f"system_time ({system_time!r}) must be finite relative elapsed seconds in "
            f"[0.0, {MAX_RELATIVE_CLOCK_SECONDS:.1f}], not a Unix wall-clock timestamp (#78)"
        )
    vels = list(velocities)[:8]
    while len(vels) < 8:
        vels.append(0.0)
    return [
        float(active_nodes),
        float(org_tension),
        t_rel,
        float(gini_index),
        float(barycentric.get("rounding", 0.18)),
        float(barycentric.get("density", 0.55)),
        float(barycentric.get("hue", 0.22)),
        float(barycentric.get("contrast", 0.12)),
        *[round(float(v), 4) for v in vels[:8]],
    ]


def encode_frame_64b_bytes(floats_16: Sequence[float]) -> bytes:
    if len(floats_16) != 16:
        raise ValueError(f"Expected 16 floats, got {len(floats_16)}")
    try:
        vals = [_as_float32(x) for x in floats_16]
    except ValueError as exc:
        raise ValueError("All 16 frame64 floats must be finite in IEEE-754 binary32") from exc
    if vals[2] < 0.0 or vals[2] > MAX_RELATIVE_CLOCK_SECONDS:
        raise ValueError(
            f"Slot 2 system_time ({vals[2]!r}) exceeds relative-clock domain "
            f"[0.0, {MAX_RELATIVE_CLOCK_SECONDS:.1f}] (#78)"
        )
    return FRAME64_STRUCT.pack(*vals)


def decode_frame_64b_bytes(blob: bytes) -> List[float]:
    if len(blob) != FRAME64_STRUCT.size:
        raise ValueError(f"Expected 64 bytes, got {len(blob)}")
    return list(FRAME64_STRUCT.unpack(blob))
