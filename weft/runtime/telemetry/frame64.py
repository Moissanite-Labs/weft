#!/usr/bin/env python3
"""
64-Byte IEEE-754 Uniform Frame Packer (Codebase C6 — Interface I1)
==================================================================
Packs the 16 float32 uniform fields (`<16f`, 64 bytes) consumed by the Aywa
WebGPU compute/render pipeline (`dashboard_layout.wgsl`) and Canvas2D fallback:
  - `[0]`: `active_nodes`
  - `[1]`: `org_tension`
  - `[2]`: `system_time`
  - `[3]`: `gini_index`
  - `[4]`: `user_rounding`
  - `[5]`: `user_density`
  - `[6]`: `user_hue`
  - `[7]`: `user_contrast`
  - `[8..11]`: `node_vel_0` (first 4 repository velocity signals)
  - `[12..15]`: `node_vel_1` (next 4 repository velocity signals)
"""

from __future__ import annotations

import struct
from typing import Dict, List, Sequence

FRAME64_STRUCT = struct.Struct("<16f")


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
    vels = list(velocities)[:8]
    while len(vels) < 8:
        vels.append(0.0)
    return [
        float(active_nodes),
        float(org_tension),
        float(system_time),
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
    return FRAME64_STRUCT.pack(*[float(x) for x in floats_16])


def decode_frame_64b_bytes(blob: bytes) -> List[float]:
    if len(blob) != FRAME64_STRUCT.size:
        raise ValueError(f"Expected 64 bytes, got {len(blob)}")
    return list(FRAME64_STRUCT.unpack(blob))
