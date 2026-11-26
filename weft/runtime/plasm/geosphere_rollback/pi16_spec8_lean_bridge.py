#!/usr/bin/env python3
"""Weft-Geosphere 16 B Pi_{t0} holonomy rollback & Spec8 x Lean 4.36.0 micro-prover bridge.

Pure Python standard-library runtime module combining:
  1. Weft 16 B Pi_{t0} SU(2) holonomy checkpoint & O(1) bit-exact rollback
     (0.0 drift vs 12 MiB / 48 MiB / 192 MiB 12L d=512 FP16 KV-cache rewind
     at T = 512 / 2048 / 8192 -> 12,582,912x spinor and 16,384x full-12L
     state rollback compression at T = 8192).
  2. Spec8 4-IMMA / 6,400 B Woodbury arena causal s_pred(tau), rank-wl FP32
     S_prefix commit, and SFU-free Cayley SU(2) replay with Newton-Raphson polish.
  3. R12 allowlist-scrubbed subprocess sandbox (resolving elan proxy binaries
     pre-scrub to direct toolchain binaries so `env -i HOME=/nonexistent`
     executes with `ELAN_HOME`, `ELAN_TOOLCHAIN`, `LEAN_PATH`, and `LD_*`
     dropped) + R13b 18-rule static trust-escape pre-filter + strict
     `#print axioms` parser for parallel 8-branch Lean 4.36.0 pure-Init
     verification (zero `sorryAx`, zero `Classical.choice`, zero `native_decide`).

Privileged operator override:
  Set `WEFT_LEAN_BIN` (or `ALETHEIA_LEAN_BIN`) to pin an explicit executable
  Lean 4 binary path; both are privileged local-operator settings and never
  populated from untrusted inputs.

Zero third-party dependencies, zero bare `assert`s, zero unseeded RNG.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence

# ---------------------------------------------------------------------------
# Constants: Spec8 Hardware Geometry & R12/R13b Lean 4 Sandbox
# ---------------------------------------------------------------------------

SPEC8_BRANCHES = 8
SPEC8_DIM = 32
SPEC8_SPINORS_PER_HEAD = 8
SPEC8_FUSED_4IMMA_SMEM_BYTES = 1056     # 32 x 33 int8 (+1 padded, 0 bank conflicts)
SPEC8_WOODBURY_SMEM_BYTES = 6400        # smem_xt[8][8][32] (2048) + smem_ek (4096) + smem_sc (256)
WEFT_PI_T0_BYTES_PER_SPINOR = 16        # Exact float4 (4 x fp32 = 16 B)
UNIT_SPINOR_N2_TOL = 0.0009765625       # Exact dyadic 1/1024 squared-norm SU(2) tolerance
_MAX_KV_BYTES = 1 << 60                 # 1 EiB safe float-conversion ceiling

_SAFE_LEAN_ENV_KEYS = frozenset({"PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "USER", "TERM"})
_ALLOWED_LEAN_AXIOMS = frozenset({"propext", "Quot.sound"})
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_LEAN4_ID_FIRST = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_LEAN4_ID_REST = _LEAN4_ID_FIRST | frozenset("0123456789'!?")

# R13b 18-rule static trust-escape pre-filter (blocks trust escapes before invoking lean)
LEAN4_STATIC_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("R01_LITERAL_OR_GUILLEMET", re.compile(r'["«»]')),
    ("R02_IMPORT", re.compile(r"(?m)^\s*import\b")),
    ("R03_SORRY_ADMIT", re.compile(r"\b(?:sorry|admit|sorryAx)\b")),
    ("R04_AXIOM_DECL", re.compile(r"(?m)^\s*(?:private\s+|protected\s+)?axiom\b")),
    ("R05_UNSAFE_EXTERN", re.compile(r"\bunsafe\b|@\[[^\]]*\b(?:extern|implemented_by|csimp)\b")),
    ("R06_OPAQUE_PARTIAL", re.compile(r"\b(?:opaque|partial|noncomputable)\b")),
    ("R07_NATIVE_DECIDE", re.compile(r"\bnative_decide\b|\bdecide\s*\+\s*(?:native|revert)\b")),
    ("R08_DBG_TRACE", re.compile(r"\b(?:dbg_trace|dbgTrace|dbgTraceVal|dbgTraceIfShared|dbgSleep|dbgStackTrace)\b")),
    ("R09_INIT_EXPORT_ATTR", re.compile(r"@\[[^\]]*\b(?:export|init|builtin_init)\b|\b(?:initialize|builtin_initialize)\b")),
    ("R10_GUARD_MSGS", re.compile(r"#guard_msgs\b")),
    ("R11_WARN_SORRY_OPT", re.compile(r"\b(?:warn\.sorry|terminalTacticsAsSorry|allowUnsafeReducibility)\b")),
    ("R12_META_EVAL_CMD", re.compile(r"#(?:eval|reduce|synth|check_failure)\b|\brun_cmd\b|\brun_meta\b")),
    ("R13_SET_OPTION", re.compile(r"(?m)^\s*set_option\b")),
    ("R14_ELAB_TACTIC_MACRO", re.compile(r"(?m)^\s*(?:elab|elab_rules|macro|macro_rules|syntax|declare_syntax_cat)\b")),
    ("R15_IO_SYSTEM", re.compile(r"\bIO\.|\bSystem\.|\bLean\.Environment\b|\bLean\.Elab\b")),
    ("R16_PANIC_UNREACHABLE", re.compile(r"\b(?:panic!|unreachable!|assert!)")),
    ("R17_DECIDE_CONFIG", re.compile(r"\bconfig\s*:=\s*\{[^}]*\bnative\b")),
    ("R18_ROOT_SORRYAX", re.compile(r"\b_root_\.sorryAx\b")),
)

_AXIOM_NONE_RE = re.compile(r"^'([A-Za-z0-9_.]+)' does not depend on any axioms$")
_AXIOM_DEP_RE = re.compile(r"^'([A-Za-z0-9_.]+)' depends on axioms: \[([^\]]*)\]$")


class WeftHolonomyError(Exception):
    """Typed fail-closed error for Weft-Geosphere Pi_{t0} rollback & Spec8 Lean bridge."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def require_ok(cond: bool, code: str, message: str) -> None:
    if cond is not True:
        raise WeftHolonomyError(code, message)


def _require_strict_int(val: Any, code: str, name: str) -> int:
    require_ok(isinstance(val, int) and not isinstance(val, bool), code, f"{name} must be strict int")
    return val


def _require_seq_len(obj: Any, expected: int, code: str, name: str) -> Sequence[Any]:
    require_ok(
        isinstance(obj, (list, tuple)) and len(obj) == expected,
        code,
        f"{name} must be list/tuple of len {expected}",
    )
    return obj


def _finite_f32(val: Any, code: str, name: str) -> float:
    require_ok(
        isinstance(val, (int, float)) and not isinstance(val, bool),
        code,
        f"{name} must be finite real number",
    )
    try:
        packed = struct.pack("<f", float(val))
    except OverflowError as exc:
        raise WeftHolonomyError(code, f"{name} overflows float32") from exc
    out = struct.unpack("<f", packed)[0]
    require_ok(math.isfinite(out), code, f"{name} must be finite float32")
    return out


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def f32(x: float) -> float:
    return _finite_f32(x, "NON_FINITE_F32", "x")


def round_fp16(x: float) -> float:
    val = _finite_f32(x, "NON_FINITE_FP16", "x")
    clamped = max(-65504.0, min(65504.0, val))
    return struct.unpack("<e", struct.pack("<e", clamped))[0]


# ---------------------------------------------------------------------------
# 1. Exact SU(2) Cayley Holonomy, 16 B Pi_{t0} Pack/Rollback & KV Savings
# ---------------------------------------------------------------------------

def cayley_su2(wx: float, wy: float, wz: float) -> tuple[float, float, float, float]:
    """SFU-free pure-rational Cayley SU(2) rotation step in FP32."""
    x = _finite_f32(wx, "NON_FINITE_OMEGA", "wx")
    y = _finite_f32(wy, "NON_FINITE_OMEGA", "wy")
    z = _finite_f32(wz, "NON_FINITE_OMEGA", "wz")
    # Accumulate n2 in FP64 so large finite FP32 omega never overflows intermediate square
    n2 = x * x + y * y + z * z
    inv = 1.0 / (1.0 + n2)
    s = 2.0 * inv
    return (f32((1.0 - n2) * inv), f32(s * x), f32(s * y), f32(s * z))


def quat_mul(
    p: tuple[float, float, float, float],
    q: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    pw, px, py, pz = p
    qw, qx, qy, qz = q
    return (
        f32(pw * qw - px * qx - py * qy - pz * qz),
        f32(pw * qx + px * qw + py * qz - pz * qy),
        f32(pw * qy - px * qz + py * qw + pz * qx),
        f32(pw * qz + px * qy - py * qx + pz * qw),
    )


def quat_nr_polish(q: Sequence[float]) -> tuple[float, float, float, float]:
    """Single Newton-Raphson unit-norm polish for SU(2) quaternions."""
    seq = _require_seq_len(q, 4, "ZERO_OR_NONFINITE_SPINOR", "q")
    qw = _finite_f32(seq[0], "ZERO_OR_NONFINITE_SPINOR", "qw")
    qx = _finite_f32(seq[1], "ZERO_OR_NONFINITE_SPINOR", "qx")
    qy = _finite_f32(seq[2], "ZERO_OR_NONFINITE_SPINOR", "qy")
    qz = _finite_f32(seq[3], "ZERO_OR_NONFINITE_SPINOR", "qz")
    n2 = qw * qw + qx * qx + qy * qy + qz * qz
    require_ok(n2 > 0.0, "ZERO_OR_NONFINITE_SPINOR", f"n2={n2}")
    scale = 0.5 * (3.0 - n2)
    return (
        _finite_f32(qw * scale, "ZERO_OR_NONFINITE_SPINOR", "qw_out"),
        _finite_f32(qx * scale, "ZERO_OR_NONFINITE_SPINOR", "qx_out"),
        _finite_f32(qy * scale, "ZERO_OR_NONFINITE_SPINOR", "qy_out"),
        _finite_f32(qz * scale, "ZERO_OR_NONFINITE_SPINOR", "qz_out"),
    )


def pack_pi_t0_16b(u_spinor: Sequence[float]) -> bytes:
    """Serialize one finite unit SU(2) spinor state into exactly 16 bytes (little-endian float4)."""
    seq = _require_seq_len(u_spinor, 4, "PI_T0_ARITY_BAD", "u_spinor")
    vals = tuple(_finite_f32(c, "PI_T0_NONFINITE", "u_spinor") for c in seq)
    n2 = vals[0] * vals[0] + vals[1] * vals[1] + vals[2] * vals[2] + vals[3] * vals[3]
    require_ok(abs(n2 - 1.0) <= UNIT_SPINOR_N2_TOL, "PI_T0_NOT_UNIT_SPINOR", f"n2={n2}")
    return struct.pack("<4f", vals[0], vals[1], vals[2], vals[3])


def unpack_pi_t0_16b(raw: bytes) -> tuple[float, float, float, float]:
    """Deserialize one 16-byte Pi_{t0} spinor checkpoint with finite unit-norm validation."""
    require_ok(
        isinstance(raw, (bytes, bytearray)) and len(raw) == WEFT_PI_T0_BYTES_PER_SPINOR,
        "PI_T0_SIZE_BAD",
        "raw checkpoint must be exactly 16 bytes",
    )
    qw, qx, qy, qz = struct.unpack("<4f", raw)
    require_ok(
        math.isfinite(qw) and math.isfinite(qx) and math.isfinite(qy) and math.isfinite(qz),
        "PI_T0_NONFINITE",
        "unpacked spinor contains non-finite value",
    )
    n2 = qw * qw + qx * qx + qy * qy + qz * qz
    require_ok(abs(n2 - 1.0) <= UNIT_SPINOR_N2_TOL, "PI_T0_NOT_UNIT_SPINOR", f"n2={n2}")
    return (qw, qx, qy, qz)


def compute_state_bytes_saved(
    *,
    n_layers: int = 12,
    d_model: int = 512,
    n_heads: int = 8,
    seq_lens: Sequence[int] = (512, 2048, 8192),
) -> dict[str, Any]:
    """Exact state-bytes saved by Weft 16 B Pi_{t0} rollback vs standard FP16 KV-cache.

    KV_bytes(T) = 2 (K,V) * n_layers * T * d_model * 2 B (FP16).
    Weft holonomy rollback = 16 B per spinor (128 B per 8-spinor head;
    12 * 8 * 8 * 16 B = 12,288 B across all 12 layers x 8 heads x 8 spinors).
    """
    nl = _require_strict_int(n_layers, "BAD_MODEL_DIMS", "n_layers")
    dm = _require_strict_int(d_model, "BAD_MODEL_DIMS", "d_model")
    nh = _require_strict_int(n_heads, "BAD_MODEL_DIMS", "n_heads")
    require_ok(nl > 0 and dm > 0 and nh > 0, "BAD_MODEL_DIMS", "model dimensions must be > 0")
    require_ok(isinstance(seq_lens, (list, tuple)) and len(seq_lens) > 0, "BAD_SEQ_LENS", "seq_lens must be non-empty list/tuple")
    clean_seq_lens: list[int] = []
    for t_raw in seq_lens:
        t_val = _require_strict_int(t_raw, "BAD_SEQ_LENS", "seq_len")
        require_ok(t_val > 0, "BAD_SEQ_LENS", "seq_len must be > 0")
        clean_seq_lens.append(t_val)

    spinor_bytes = WEFT_PI_T0_BYTES_PER_SPINOR
    head_holonomy_bytes = SPEC8_SPINORS_PER_HEAD * WEFT_PI_T0_BYTES_PER_SPINOR
    full_12l_holonomy_bytes = nl * nh * SPEC8_SPINORS_PER_HEAD * WEFT_PI_T0_BYTES_PER_SPINOR
    require_ok(full_12l_holonomy_bytes <= _MAX_KV_BYTES, "KV_BYTES_OVERFLOW", "holonomy byte size overflow")

    rows: dict[str, dict[str, Any]] = {}
    for t_val in clean_seq_lens:
        kv_bytes = 2 * nl * t_val * dm * 2
        require_ok(kv_bytes <= _MAX_KV_BYTES, "KV_BYTES_OVERFLOW", f"kv_bytes={kv_bytes} exceeds limit")
        rows[f"T_{t_val}"] = {
            "seq_len": t_val,
            "kv_cache_fp16_bytes": kv_bytes,
            "kv_cache_mib": round(kv_bytes / (1024.0 * 1024.0), 4),
            "weft_pi_t0_spinor_bytes": spinor_bytes,
            "weft_pi_t0_head_bytes": head_holonomy_bytes,
            "weft_pi_t0_full_12l_bytes": full_12l_holonomy_bytes,
            "bytes_saved_vs_spinor": kv_bytes - spinor_bytes,
            "bytes_saved_vs_full_12l": kv_bytes - full_12l_holonomy_bytes,
            "compression_vs_spinor_x": round(kv_bytes / float(spinor_bytes), 2),
            "compression_vs_full_12l_x": round(kv_bytes / float(full_12l_holonomy_bytes), 2),
        }
    return {
        "n_layers": nl,
        "d_model": dm,
        "n_heads": nh,
        "spec8_fused_4imma_smem_bytes": SPEC8_FUSED_4IMMA_SMEM_BYTES,
        "spec8_woodbury_smem_bytes": SPEC8_WOODBURY_SMEM_BYTES,
        "horizons": rows,
    }


# ---------------------------------------------------------------------------
# 2. Spec8 Woodbury + SU(2) Holonomy Engine with 16 B Pi_{t0} Rollback
# ---------------------------------------------------------------------------

def _encode_state_bytes(
    u_holonomy: Sequence[tuple[float, float, float, float]],
    s_prefix: Sequence[Sequence[float]],
) -> bytes:
    buf = bytearray()
    for u in u_holonomy:
        buf.extend(pack_pi_t0_16b(u))
    for row in s_prefix:
        for val in row:
            buf.extend(struct.pack("<f", val))
    return bytes(buf)


def _validate_spec8_branch_arena(
    arena: Any,
    b_idx: int,
    depth: int,
) -> tuple[
    list[list[int]],
    list[float],
    list[list[float]],
    list[list[tuple[float, float, float]]],
]:
    """Validate Spec8 Woodbury arena schema, shapes, int8 bounds, and FP32 finiteness."""
    require_ok(
        isinstance(arena, Mapping) and all(k in arena for k in ("xt_8x8", "sc_8x8", "ek_8x8", "w_8x8")),
        "ARENA_SCHEMA_BAD",
        "arena must contain xt_8x8, sc_8x8, ek_8x8, w_8x8",
    )
    xt_all = _require_seq_len(arena["xt_8x8"], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "xt_8x8")
    sc_all = _require_seq_len(arena["sc_8x8"], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "sc_8x8")
    ek_all = _require_seq_len(arena["ek_8x8"], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "ek_8x8")
    w_all = _require_seq_len(arena["w_8x8"], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "w_8x8")
    xt_b = _require_seq_len(xt_all[b_idx], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "xt_b")
    sc_b = _require_seq_len(sc_all[b_idx], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "sc_b")
    ek_b = _require_seq_len(ek_all[b_idx], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "ek_b")
    w_b = _require_seq_len(w_all[b_idx], SPEC8_BRANCHES, "ARENA_SHAPE_BAD", "w_b")

    xt_clean: list[list[int]] = []
    sc_clean: list[float] = []
    ek_clean: list[list[float]] = []
    w_clean: list[list[tuple[float, float, float]]] = []
    for k in range(depth):
        sc_k = _finite_f32(sc_b[k], "ARENA_NONFINITE", "sc_8x8")
        xt_k = _require_seq_len(xt_b[k], SPEC8_DIM, "ARENA_SHAPE_BAD", "xt_k")
        ek_k = _require_seq_len(ek_b[k], SPEC8_DIM, "ARENA_SHAPE_BAD", "ek_k")
        w_k = _require_seq_len(w_b[k], SPEC8_SPINORS_PER_HEAD, "ARENA_SHAPE_BAD", "w_k")
        xt_row: list[int] = []
        for q_raw in xt_k:
            q_val = _require_strict_int(q_raw, "ARENA_BAD_XT", "xt_8x8")
            require_ok(-128 <= q_val <= 127, "ARENA_BAD_XT", f"xt={q_val} out of int8 range")
            xt_row.append(q_val)
        ek_row = [_finite_f32(v, "ARENA_NONFINITE", "ek_8x8") for v in ek_k]
        w_row: list[tuple[float, float, float]] = []
        for triple in w_k:
            tri = _require_seq_len(triple, 3, "ARENA_SHAPE_BAD", "w_triple")
            w_row.append(
                (
                    _finite_f32(tri[0], "ARENA_NONFINITE", "wx"),
                    _finite_f32(tri[1], "ARENA_NONFINITE", "wy"),
                    _finite_f32(tri[2], "ARENA_NONFINITE", "wz"),
                )
            )
        xt_clean.append(xt_row)
        sc_clean.append(sc_k)
        ek_clean.append(ek_row)
        w_clean.append(w_row)
    return (xt_clean, sc_clean, ek_clean, w_clean)


@dataclass
class Spec8Checkpoint:
    step_id: int
    pi_t0_bytes_list: list[bytes]         # 8 x 16 B = 128 B exact SU(2) spinors
    s_prefix_snapshot: list[list[float]]  # [32][32] exact FP32 S_prefix
    state_sha256: str


class Spec8HolonomyEngine:
    """Pure-stdlib Spec8 Woodbury + Weft 16 B Pi_{t0} rollback state machine.

    Maintains FP32 S_prefix [32, 32] and 8 SU(2) spinors U [8 x 16 B = 128 B] for one head:
      - Evaluates strictly causal multi-step Woodbury s_pred(tau) across N = 8 branches.
      - Commits a winning branch (1 <= win_len <= 8) into S_prefix + U, OR executes
        cryptographically checked bit-exact 16 B Pi_{t0} rollback (`0.0` drift).
    """

    def __init__(self, *, gamma: float = 0.95, eta: float = 0.05, seed: int = 11117) -> None:
        g_val = _finite_f32(gamma, "BAD_GAMMA", "gamma")
        e_val = _finite_f32(eta, "BAD_ETA", "eta")
        s_val = _require_strict_int(seed, "BAD_SEED", "seed")
        require_ok(0.0 < g_val <= 1.0, "BAD_GAMMA", f"gamma={g_val}")
        require_ok(e_val > 0.0, "BAD_ETA", f"eta={e_val}")
        self.gamma = g_val
        self.eta = e_val
        rng = random.Random(s_val)
        self.s_prefix: list[list[float]] = [
            [f32(rng.gauss(0.0, 0.04)) for _ in range(SPEC8_DIM)] for _ in range(SPEC8_DIM)
        ]
        self.u_holonomy: list[tuple[float, float, float, float]] = [
            (1.0, 0.0, 0.0, 0.0) for _ in range(SPEC8_SPINORS_PER_HEAD)
        ]
        self.step_counter = 0
        self.commits = 0
        self.rollbacks = 0

    def state_bytes(self) -> bytes:
        return _encode_state_bytes(self.u_holonomy, self.s_prefix)

    def state_sha256(self) -> str:
        return sha256_hex(self.state_bytes())

    def checkpoint_16b(self) -> Spec8Checkpoint:
        pi_list = [pack_pi_t0_16b(u) for u in self.u_holonomy]
        return Spec8Checkpoint(
            step_id=self.step_counter,
            pi_t0_bytes_list=pi_list,
            s_prefix_snapshot=[list(row) for row in self.s_prefix],
            state_sha256=self.state_sha256(),
        )

    def rollback_16b(self, ckpt: Spec8Checkpoint) -> dict[str, Any]:
        """Atomically validate & restore SU(2) spinors from 16 B Pi_{t0} packets and S_prefix."""
        pi_list = _require_seq_len(ckpt.pi_t0_bytes_list, SPEC8_SPINORS_PER_HEAD, "CKPT_SPINOR_COUNT_BAD", "pi_t0_bytes_list")
        s_rows = _require_seq_len(ckpt.s_prefix_snapshot, SPEC8_DIM, "CKPT_PREFIX_SHAPE_BAD", "s_prefix_snapshot")
        restored_u = [unpack_pi_t0_16b(raw_b) for raw_b in pi_list]
        restored_s = [
            [_finite_f32(val, "CKPT_PREFIX_NONFINITE", "s_prefix") for val in _require_seq_len(row, SPEC8_DIM, "CKPT_PREFIX_SHAPE_BAD", "s_prefix_row")]
            for row in s_rows
        ]
        post_sha = sha256_hex(_encode_state_bytes(restored_u, restored_s))
        require_ok(post_sha == ckpt.state_sha256, "CKPT_SHA_MISMATCH", f"got={post_sha} expected={ckpt.state_sha256}")

        self.u_holonomy = restored_u
        self.s_prefix = restored_s
        self.step_counter += 1
        self.rollbacks += 1
        return {
            "action": "ROLLED_BACK_16B",
            "pi_t0_bytes_per_spinor": WEFT_PI_T0_BYTES_PER_SPINOR,
            "bit_exact_sha_restored": True,
            "post_state_sha256": post_sha,
        }

    def synthesize_spec8_branch_arena(
        self,
        goal_id: str,
        branch_tactics: Sequence[str],
        *,
        seed: int = 42,
    ) -> dict[str, Any]:
        """Deterministically construct the 6,400 B SMEM Spec8 Woodbury arena for N = 8 branches."""
        tactics = _require_seq_len(branch_tactics, SPEC8_BRANCHES, "NEED_8_BRANCHES", "branch_tactics")
        s_val = _require_strict_int(seed, "BAD_SEED", "seed")
        xt_8x8: list[list[list[int]]] = []
        sc_8x8: list[list[float]] = []
        ek_8x8: list[list[list[float]]] = []
        w_8x8: list[list[list[tuple[float, float, float]]]] = []

        for b_idx, tactic in enumerate(tactics):
            b_seed = int(sha256_hex(f"spec8:{goal_id}:{b_idx}:{tactic}:{s_val}".encode("utf-8"))[:12], 16)
            rng = random.Random(b_seed)
            xt_b: list[list[int]] = []
            sc_b: list[float] = []
            ek_b: list[list[float]] = []
            w_b: list[list[tuple[float, float, float]]] = []
            for _k in range(SPEC8_BRANCHES):
                raw_x = [rng.gauss(0.0, 1.0) for _ in range(SPEC8_DIM)]
                norm = math.sqrt(sum(v * v for v in raw_x)) or 1.0
                unit_x = [v / norm for v in raw_x]
                absmax = max(abs(v) for v in unit_x) or 1e-6
                sc = f32(absmax / 127.0)
                q_x = [max(-127, min(127, int(round(v / sc)))) for v in unit_x]
                e_vec = [round_fp16(rng.gauss(0.0, 0.12)) for _ in range(SPEC8_DIM)]
                w_spinors = [
                    (f32(rng.uniform(-0.18, 0.18)), f32(rng.uniform(-0.18, 0.18)), f32(rng.uniform(-0.18, 0.18)))
                    for _ in range(SPEC8_SPINORS_PER_HEAD)
                ]
                xt_b.append(q_x)
                sc_b.append(sc)
                ek_b.append(e_vec)
                w_b.append(w_spinors)
            xt_8x8.append(xt_b)
            sc_8x8.append(sc_b)
            ek_8x8.append(ek_b)
            w_8x8.append(w_b)

        return {
            "xt_8x8": xt_8x8,
            "sc_8x8": sc_8x8,
            "ek_8x8": ek_8x8,
            "w_8x8": w_8x8,
            "woodbury_smem_bytes": SPEC8_WOODBURY_SMEM_BYTES,
        }

    def causal_woodbury_s_pred(self, arena: dict[str, Any], b_sel: int, tau: int) -> list[float]:
        """Causal multi-step Woodbury s_pred(tau):
          s_pred(tau) = gamma^tau * (S_prefix @ x_tau)
                        + sum_{k=0}^{tau-1} (gamma^{tau-1-k} * eta * <x_k, x_tau>) * e_k
        """
        b_val = _require_strict_int(b_sel, "WOODBURY_BRANCH_OOB", "b_sel")
        t_val = _require_strict_int(tau, "WOODBURY_TAU_OOB", "tau")
        require_ok(0 <= b_val < SPEC8_BRANCHES, "WOODBURY_BRANCH_OOB", f"b_sel={b_val}")
        require_ok(0 <= t_val < SPEC8_BRANCHES, "WOODBURY_TAU_OOB", f"tau={t_val}")
        xt_b, sc_b, ek_b, _w_b = _validate_spec8_branch_arena(arena, b_val, t_val + 1)
        x_tau = [_finite_f32(float(xt_b[t_val][j]) * sc_b[t_val], "ARENA_NONFINITE", "x_tau") for j in range(SPEC8_DIM)]

        g_tau = 1.0
        for _ in range(t_val):
            g_tau = f32(g_tau * self.gamma)

        out: list[float] = []
        for r in range(SPEC8_DIM):
            base = 0.0
            for j in range(SPEC8_DIM):
                base = _finite_f32(base + _finite_f32(self.s_prefix[r][j] * x_tau[j], "ARENA_NONFINITE", "base"), "ARENA_NONFINITE", "base")
            out.append(_finite_f32(g_tau * base, "ARENA_NONFINITE", "out"))

        w_decay = self.eta
        for k in range(t_val - 1, -1, -1):
            x_k = [_finite_f32(float(xt_b[k][j]) * sc_b[k], "ARENA_NONFINITE", "x_k") for j in range(SPEC8_DIM)]
            dot = 0.0
            for j in range(SPEC8_DIM):
                dot = _finite_f32(dot + _finite_f32(x_k[j] * x_tau[j], "ARENA_NONFINITE", "dot"), "ARENA_NONFINITE", "dot")
            coeff = _finite_f32(w_decay * dot, "ARENA_NONFINITE", "coeff")
            for r in range(SPEC8_DIM):
                out[r] = _finite_f32(out[r] + _finite_f32(coeff * ek_b[k][r], "ARENA_NONFINITE", "upd"), "ARENA_NONFINITE", "out")
            w_decay = f32(w_decay * self.gamma)
        return out

    def commit_winning_branch(
        self,
        arena: dict[str, Any],
        *,
        b_win: int,
        win_len: int,
    ) -> dict[str, Any]:
        """Atomically execute rank-wl Woodbury S_prefix commit + SU(2) Cayley holonomy replay."""
        bw = _require_strict_int(b_win, "BAD_B_WIN", "b_win")
        wl = _require_strict_int(win_len, "BAD_WIN_LEN", "win_len")
        require_ok(0 <= bw < SPEC8_BRANCHES, "BAD_B_WIN", str(bw))
        require_ok(1 <= wl <= SPEC8_BRANCHES, "BAD_WIN_LEN", str(wl))
        xt_b, sc_b, ek_b, w_b = _validate_spec8_branch_arena(arena, bw, wl)
        causal_pred = self.causal_woodbury_s_pred(arena, bw, wl - 1)

        g_wl = 1.0
        for _ in range(wl):
            g_wl = f32(g_wl * self.gamma)
        next_s = [[f32(self.s_prefix[r][c] * g_wl) for c in range(SPEC8_DIM)] for r in range(SPEC8_DIM)]

        w_commit = self.eta
        for k in range(wl - 1, -1, -1):
            x_k = [_finite_f32(float(xt_b[k][j]) * sc_b[k], "ARENA_NONFINITE", "x_k") for j in range(SPEC8_DIM)]
            for r in range(SPEC8_DIM):
                er = ek_b[k][r]
                for c in range(SPEC8_DIM):
                    term = _finite_f32(er * _finite_f32(w_commit * x_k[c], "ARENA_NONFINITE", "commit"), "ARENA_NONFINITE", "commit")
                    next_s[r][c] = _finite_f32(next_s[r][c] + term, "ARENA_NONFINITE", "commit")
            w_commit = f32(w_commit * self.gamma)

        next_u: list[tuple[float, float, float, float]] = []
        for s_idx in range(SPEC8_SPINORS_PER_HEAD):
            u_cur = self.u_holonomy[s_idx]
            for k in range(wl):
                wx, wy, wz = w_b[k][s_idx]
                u_cur = quat_nr_polish(quat_mul(cayley_su2(wx, wy, wz), u_cur))
            next_u.append(u_cur)

        self.s_prefix = next_s
        self.u_holonomy = next_u
        max_norm_err = max(
            abs(math.sqrt(sum(c * c for c in u)) - 1.0) for u in self.u_holonomy
        )
        self.step_counter += 1
        self.commits += 1
        return {
            "action": "COMMITTED",
            "b_win": bw,
            "win_len": wl,
            "causal_spred_l2": round(math.sqrt(sum(v * v for v in causal_pred)), 6),
            "max_su2_unit_norm_err": round(max_norm_err, 9),
            "post_state_sha256": self.state_sha256(),
        }

    def speculative_perturb_and_rollback_16b(
        self,
        ckpt: Spec8Checkpoint,
        arena: dict[str, Any],
    ) -> dict[str, Any]:
        """Perturb SU(2) & S_prefix on branch 0 then execute exception-safe 16 B Pi_{t0} rollback.

        Captures an independent pre-perturbation reference copy of `u_holonomy` and `s_prefix`
        prior to mutating state so post-rollback drift is measured against the original
        pre-perturbation state rather than the just-assigned checkpoint arrays.
        """
        _xt_b, _sc_b, _ek_b, w_b = _validate_spec8_branch_arena(arena, 0, 1)
        ref_u = [tuple(u) for u in self.u_holonomy]
        ref_s = [list(row) for row in self.s_prefix]

        pert_u = [
            quat_nr_polish(quat_mul(cayley_su2(*w_b[0][s_idx]), ref_u[s_idx]))
            for s_idx in range(SPEC8_SPINORS_PER_HEAD)
        ]
        pert_s00 = _finite_f32(ref_s[0][0] + 0.5, "ARENA_NONFINITE", "s_prefix[0][0]")
        pre_rb_drift = max(
            (
                math.sqrt(sum((a - b) ** 2 for a, b in zip(u_now, u_ref)))
                for u_now, u_ref in zip(pert_u, ref_u)
            ),
            default=0.0,
        )
        require_ok(pre_rb_drift > 0.0, "SPEC_PERTURB_ZERO", "speculative branch did not move holonomy")

        self.u_holonomy = pert_u
        self.s_prefix[0][0] = pert_s00
        try:
            rb = self.rollback_16b(ckpt)
        except WeftHolonomyError:
            self.u_holonomy = list(ref_u)
            self.s_prefix = [list(row) for row in ref_s]
            raise

        post_u_drift = max(
            math.sqrt(sum((a - b) ** 2 for a, b in zip(u_now, u_ref)))
            for u_now, u_ref in zip(self.u_holonomy, ref_u)
        )
        post_s_drift = max(
            abs(self.s_prefix[r][c] - ref_s[r][c])
            for r in range(SPEC8_DIM)
            for c in range(SPEC8_DIM)
        )
        rb["pre_rollback_u_drift"] = round(pre_rb_drift, 6)
        rb["post_rollback_u_drift"] = post_u_drift
        rb["post_rollback_s_drift"] = post_s_drift
        return rb


# ---------------------------------------------------------------------------
# 3. R13b Static Pre-Filter, #print axioms Parser & R12 Lean 4 Sandbox Oracle
# ---------------------------------------------------------------------------

def _match_lean4_char_literal_end(src: str, i: int, n: int) -> int | None:
    if i + 2 < n and src[i + 1] not in ("\\", "'") and src[i + 2] == "'":
        return i + 3
    if i + 3 < n and src[i + 1] == "\\":
        if src[i + 3] == "'" and src[i + 2] != "\n":
            return i + 4
        esc = src[i + 2]
        if esc == "x" and i + 5 < n and src[i + 5] == "'" and all(c in _HEX_DIGITS for c in src[i + 3 : i + 5]):
            return i + 6
        if esc == "u" and i + 7 < n and src[i + 7] == "'" and all(c in _HEX_DIGITS for c in src[i + 3 : i + 7]):
            return i + 8
    return None


def strip_lean4_source(src: str) -> str:
    """R13b O(n) in_ident Lean 4 nested-comment and Char-literal stripper."""
    out: list[str] = []
    i = 0
    n = len(src)
    depth = 0
    in_ident = False
    while i < n:
        ch = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if depth > 0:
            if ch == "/" and nxt == "-":
                depth += 1
                out.append("  ")
                i += 2
            elif ch == "-" and nxt == "/":
                depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue
        if ch == "/" and nxt == "-":
            in_ident = False
            depth = 1
            out.append("  ")
            i += 2
            continue
        if ch == "-" and nxt == "-":
            in_ident = False
            while i < n and src[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == "'" and not in_ident:
            cend = _match_lean4_char_literal_end(src, i, n)
            if cend is not None:
                out.append(" \n " if src[i + 1] == "\n" else " " * (cend - i))
                i = cend
                continue
        in_ident = (ch in _LEAN4_ID_REST) if in_ident else (ch in _LEAN4_ID_FIRST)
        out.append(ch)
        i += 1
    require_ok(depth == 0, "LEAN4_UNTERMINATED_COMMENT", "unclosed /- comment")
    return "".join(out)


def static_r13b_prefilter(src: str) -> list[str]:
    """Return triggered R13b static trust-escape rule IDs (empty list = clean)."""
    if "\r" in src or "\x00" in src:
        return ["R00_BAD_CONTROL_CHARS"]
    try:
        stripped = strip_lean4_source(src)
    except WeftHolonomyError:
        return ["R00_UNTERMINATED_COMMENT"]
    return [rid for rid, rx in LEAN4_STATIC_RULES if rx.search(stripped) is not None]


def parse_lean4_print_axioms(stdout: str, expected_theorem: str) -> tuple[bool, str, str, list[str]]:
    """Parse strict `#print axioms` output: allow only `propext` and `Quot.sound`."""
    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    if len(lines) != 1:
        return (False, "R13B_AXIOM_STDOUT_BAD", f"unexpected_lines={len(lines)}", [])
    m_none = _AXIOM_NONE_RE.match(lines[0])
    m_dep = _AXIOM_DEP_RE.match(lines[0])
    if m_none is None and m_dep is None:
        return (False, "R13B_AXIOM_PARSE_FAIL", lines[0][:80], [])
    matched = m_none if m_none is not None else m_dep
    theorem_seen = matched.group(1)  # type: ignore[union-attr]
    if theorem_seen != expected_theorem:
        return (False, "R13B_THEOREM_NAME_MISMATCH", theorem_seen, [])
    axioms = [] if m_dep is None else [a.strip() for a in m_dep.group(2).split(",") if a.strip()]
    bad_axioms = [ax for ax in axioms if ax not in _ALLOWED_LEAN_AXIOMS]
    if bad_axioms:
        return (False, "R13B_FORBIDDEN_AXIOM", ",".join(bad_axioms), axioms)
    return (True, "VERIFIED_PURE_INIT", "OK", axioms)


def _safe_home_path(home: Path | None, env: Mapping[str, str]) -> Path | None:
    if home is not None:
        return home
    env_home = env.get("HOME", "")
    return Path(env_home) if env_home else None


def _resolve_elan_toolchain_binary(candidate: Any, env: Mapping[str, str]) -> str:
    """Resolve an elan proxy (`<elan>/bin/lean`) pre-scrub to its direct toolchain binary.

    When `candidate` (or its symlink target) lives in `<elan_root>/bin/` beside a
    `toolchains/` directory, query `--print-prefix` once using only `ELAN_HOME=<elan_root>`
    and return `<prefix>/bin/lean`. The direct toolchain binary then executes cleanly under
    `env -i HOME=/nonexistent` with `ELAN_HOME`, `ELAN_TOOLCHAIN`, `LEAN_PATH`, and `LD_*`
    fully dropped from the sandbox environment.
    """
    require_ok(
        isinstance(candidate, (str, os.PathLike)),
        "BAD_LEAN_BIN",
        "lean_bin must be str or os.PathLike",
    )
    cand_str = os.fspath(candidate)
    require_ok(isinstance(cand_str, str) and len(cand_str) > 0, "BAD_LEAN_BIN", "lean_bin must be non-empty str path")
    resolved = Path(cand_str).resolve()
    elan_root = resolved.parent.parent
    if resolved.parent.name == "bin" and (elan_root / "toolchains").is_dir():
        probe_env = {
            "PATH": env.get("PATH", "/usr/bin:/bin") or "/usr/bin:/bin",
            "ELAN_HOME": os.fspath(elan_root),
        }
        try:
            proc = subprocess.run(
                [os.fspath(resolved), "--print-prefix"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                env=probe_env,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise WeftHolonomyError("LEAN_VERSION_BAD", f"elan --print-prefix failed: {exc}") from exc
        prefix = proc.stdout.strip()
        if proc.returncode == 0 and prefix:
            direct = Path(prefix) / "bin" / "lean"
            if direct.is_file() and os.access(os.fspath(direct), os.X_OK):
                return os.fspath(direct)
    return cand_str


def resolve_lean_binary(
    *,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> str:
    """Resolve direct Lean 4 binary without hardcoded host paths (safe under `env -i`)."""
    src_env = os.environ if env is None else env
    env_bin = src_env.get("WEFT_LEAN_BIN", "") or src_env.get("ALETHEIA_LEAN_BIN", "")
    if env_bin:
        require_ok(
            os.path.isfile(env_bin) and os.access(env_bin, os.X_OK),
            "BAD_LEAN_BIN",
            "invalid WEFT_LEAN_BIN / ALETHEIA_LEAN_BIN",
        )
        return _resolve_elan_toolchain_binary(env_bin, src_env)
    found = shutil.which("lean", path=src_env.get("PATH", ""))
    if found:
        return _resolve_elan_toolchain_binary(str(found), src_env)
    resolved_home = _safe_home_path(home, src_env)
    if resolved_home is not None:
        elan_lean = resolved_home / ".elan" / "bin" / "lean"
        if elan_lean.is_file() and os.access(os.fspath(elan_lean), os.X_OK):
            return _resolve_elan_toolchain_binary(os.fspath(elan_lean), src_env)
    raise WeftHolonomyError("LEAN_BINARY_UNAVAILABLE", "lean 4 binary not found")


def scrubbed_r12_lean_env(
    extra_base_env: Mapping[str, str] | None = None,
    *,
    home: Path | None = None,
) -> dict[str, str]:
    """R12 allowlist-scrubbed subprocess environment.

    Drops LEAN_PATH, LEAN_*, ELAN_*, LAKE_*, LD_*, DYLD_* so hostile LEAN_PATH
    cannot hijack `lean`, while remaining safe under `env -i HOME=/nonexistent`.
    """
    src_env = os.environ if extra_base_env is None else extra_base_env
    clean = {k: v for k, v in src_env.items() if k in _SAFE_LEAN_ENV_KEYS}
    resolved_home = _safe_home_path(home, src_env)
    if resolved_home is not None:
        elan_bin = os.fspath(resolved_home / ".elan" / "bin")
        cur_path = clean.get("PATH", "")
        if elan_bin not in cur_path.split(os.pathsep) and os.path.isdir(elan_bin):
            clean["PATH"] = f"{elan_bin}{os.pathsep}{cur_path}" if cur_path else elan_bin
    return clean


def lean_binary_available(*, env: Mapping[str, str] | None = None, home: Path | None = None) -> bool:
    """Return True iff a working Lean 4 binary resolves in this environment."""
    try:
        lean_bin = resolve_lean_binary(env=env, home=home)
        clean_env = scrubbed_r12_lean_env(env, home=home)
        proc = subprocess.run(
            [lean_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env=clean_env,
        )
    except (WeftHolonomyError, OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0 and "version 4." in proc.stdout


class Lean4R12SandboxOracle:
    """Parallel N=8 Lean 4 kernel verifier with R12 LEAN_PATH isolation & R13b axiom check."""

    def __init__(
        self,
        *,
        timeout_s: int = 30,
        lean_bin: str | None = None,
        base_env: Mapping[str, str] | None = None,
    ) -> None:
        t_val = _require_strict_int(timeout_s, "BAD_TIMEOUT", "timeout_s")
        require_ok(t_val > 0, "BAD_TIMEOUT", f"timeout_s={t_val}")
        src_env = os.environ if base_env is None else base_env
        self.lean_bin = (
            _resolve_elan_toolchain_binary(lean_bin, src_env)
            if lean_bin is not None
            else resolve_lean_binary(env=src_env)
        )
        self.timeout_s = t_val
        self.env = scrubbed_r12_lean_env(src_env)
        try:
            v_proc = subprocess.run(
                [self.lean_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                check=False,
                env=self.env,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise WeftHolonomyError("LEAN_VERSION_BAD", f"lean --version failed: {exc}") from exc
        diag = " | ".join(part for part in (v_proc.stdout.strip(), v_proc.stderr.strip()) if part)
        require_ok(
            v_proc.returncode == 0 and "version 4." in v_proc.stdout,
            "LEAN_VERSION_BAD",
            diag or f"rc={v_proc.returncode}",
        )
        self.lean_version = v_proc.stdout.strip().splitlines()[0]

    def verify_branch_candidate(
        self,
        *,
        branch_idx: int,
        theorem_name: str,
        theorem_decl: str,
        tactic_body: str,
    ) -> dict[str, Any]:
        """Verify one candidate tactic branch via R13b pre-filter -> R12 `lean --stdin` -> axiom gate."""
        full_name = f"Spec8Live.{theorem_name}"
        src = (
            "namespace Spec8Live\n"
            f"theorem {theorem_name} {theorem_decl} := by\n"
            f"{tactic_body}\n"
            "end Spec8Live\n"
            f"#print axioms {full_name}\n"
        )
        t0 = time.perf_counter_ns()
        hits = static_r13b_prefilter(src)
        if hits:
            return {
                "branch_idx": branch_idx,
                "accepted": False,
                "stage": "R13B_STATIC_REJECT",
                "reason": ",".join(hits),
                "axioms": [],
                "source_sha256": sha256_hex(src.encode("utf-8")),
                "elapsed_ms": round((time.perf_counter_ns() - t0) / 1e6, 2),
            }

        try:
            proc = subprocess.run(
                [self.lean_bin, "--stdin"],
                input=src,
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                check=False,
                env=self.env,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise WeftHolonomyError("LEAN_EXEC_ERROR", f"lean --stdin failed: {exc}") from exc
        elapsed_ms = round((time.perf_counter_ns() - t0) / 1e6, 2)
        if proc.returncode != 0 or proc.stderr != "" or ("warning" in proc.stdout.lower()):
            return {
                "branch_idx": branch_idx,
                "accepted": False,
                "stage": "LEAN_KERNEL_REJECT",
                "reason": f"rc={proc.returncode}",
                "axioms": [],
                "source_sha256": sha256_hex(src.encode("utf-8")),
                "elapsed_ms": elapsed_ms,
            }

        accepted, stage, reason, axioms = parse_lean4_print_axioms(proc.stdout, full_name)
        return {
            "branch_idx": branch_idx,
            "accepted": accepted,
            "stage": stage,
            "reason": reason,
            "axioms": axioms,
            "source_sha256": sha256_hex(src.encode("utf-8")),
            "elapsed_ms": elapsed_ms,
        }

    def verify_8_branches_parallel(
        self,
        *,
        theorem_name: str,
        theorem_decl: str,
        candidate_tactics: Sequence[str],
    ) -> list[dict[str, Any]]:
        """Verify all N = 8 speculative tactic branches concurrently against isolated Lean 4."""
        tactics = _require_seq_len(candidate_tactics, SPEC8_BRANCHES, "NEED_8_BRANCHES", "candidate_tactics")
        with ThreadPoolExecutor(max_workers=SPEC8_BRANCHES) as pool:
            futs = [
                pool.submit(
                    self.verify_branch_candidate,
                    branch_idx=idx,
                    theorem_name=theorem_name,
                    theorem_decl=theorem_decl,
                    tactic_body=tac,
                )
                for idx, tac in enumerate(tactics)
            ]
            return [f.result() for f in futs]


# ---------------------------------------------------------------------------
# 4. 7-Goal Pure-Init Lean 4.36.0 Suite + All-Reject Rollback Round
# ---------------------------------------------------------------------------

def build_pure_init_spec8_goal_suite() -> list[dict[str, Any]]:
    """7 pure-Init Lean 4.36.0 goals spanning Nat, Cayley2x2, CayleySU2, Weft C_row, and A_16 parity.

    Each goal carries 8 candidate tactic branches including R13b trust escapes and `by grind`
    `Classical.choice` traps.
    """
    return [
        {
            "goal_id": "G1_nat_add_comm_assoc",
            "theorem_name": "g1_nat_add_comm_assoc",
            "theorem_decl": "(a b c : Nat) : a + b + c = c + b + a",
            "win_len": 2,
            "candidates": [
                "  sorry",
                "  rfl",
                "  native_decide",
                "  decide",
                "  omega",
                "  exact rfl",
                "  assumption",
                "  contradiction",
            ],
        },
        {
            "goal_id": "G2_int_diff_sq_identity",
            "theorem_name": "g2_int_diff_sq_identity",
            "theorem_decl": "(a b : Int) : a * a - b * b = (a - b) * (a + b)",
            "win_len": 3,
            "candidates": [
                "  admit",
                "  rfl",
                "  grind",
                "  omega",
                "  simp only [Int.sub_mul, Int.mul_add, Int.mul_comm b a]\n  omega",
                "  native_decide",
                "  assumption",
                "  exact Int.zero_add _",
            ],
        },
        {
            "goal_id": "G3_cayley2x2_unit_norm_homog",
            "theorem_name": "g3_cayley2x2_unit_norm_homog",
            "theorem_decl": "(w : Int) : (1 - w * w) * (1 - w * w) + (2 * w) * (2 * w) = (1 + w * w) * (1 + w * w)",
            "win_len": 4,
            "candidates": [
                "  sorry",
                "  grind",
                "  omega",
                "  rfl",
                "  native_decide",
                (
                    "  have h4 : (2 * w) * (2 * w) = 4 * (w * w) := by\n"
                    "    calc (2 * w) * (2 * w) = (2 * 2) * (w * w) := by\n"
                    "          simp only [Int.mul_assoc, Int.mul_left_comm w 2]\n"
                    "      _ = 4 * (w * w) := rfl\n"
                    "  rw [h4]\n"
                    "  simp only [Int.sub_mul, Int.mul_sub, Int.add_mul, Int.mul_add, Int.one_mul, Int.mul_one]\n"
                    "  omega"
                ),
                "  simp",
                "  contradiction",
            ],
        },
        {
            "goal_id": "G4_cayley_su2_unit_norm_homog",
            "theorem_name": "g4_cayley_su2_unit_norm_homog",
            "theorem_decl": (
                "(d x y z : Int) : "
                "(d * d - x * x - y * y - z * z) * (d * d - x * x - y * y - z * z) + "
                "(2 * d * x) * (2 * d * x) + (2 * d * y) * (2 * d * y) + (2 * d * z) * (2 * d * z) = "
                "(d * d + x * x + y * y + z * z) * (d * d + x * x + y * y + z * z)"
            ),
            "win_len": 6,
            "candidates": [
                "  sorry",
                "  grind",
                "  omega",
                "  rfl",
                "  simp",
                "  native_decide",
                (
                    "  have h1 : (d * d - x * x - y * y - z * z) = d * d - (x * x + y * y + z * z) := by omega\n"
                    "  have h2 : (d * d + x * x + y * y + z * z) = d * d + (x * x + y * y + z * z) := by omega\n"
                    "  have hsq : ∀ (a b : Int), (2 * a * b) * (2 * a * b) = 4 * ((a * a) * (b * b)) := by\n"
                    "    intro a b\n"
                    "    calc (2 * a * b) * (2 * a * b)\n"
                    "        = (2 * 2) * ((a * a) * (b * b)) := by\n"
                    "          simp only [Int.mul_assoc, Int.mul_left_comm a 2, Int.mul_left_comm b 2, Int.mul_left_comm b a]\n"
                    "      _ = 4 * ((a * a) * (b * b)) := rfl\n"
                    "  rw [h1, h2, hsq d x, hsq d y, hsq d z]\n"
                    "  have hcomm : (x * x + y * y + z * z) * (d * d) = d * d * (x * x + y * y + z * z) :=\n"
                    "    Int.mul_comm _ _\n"
                    "  simp only [Int.sub_mul, Int.mul_sub, Int.add_mul, Int.mul_add, hcomm]\n"
                    "  omega"
                ),
                "  assumption",
            ],
        },
        {
            "goal_id": "G5_cayley2x2_beltrami_commutator",
            "theorem_name": "g5_cayley2x2_beltrami_commutator",
            "theorem_decl": "(c s w : Int) : (-s * w + w * s = 0) ∧ (c * w - w * c = 0)",
            "win_len": 3,
            "candidates": [
                "  sorry",
                "  rfl",
                "  constructor\n  · rw [Int.neg_mul, Int.mul_comm s w]; omega\n  · rw [Int.mul_comm c w]; omega",
                "  grind",
                "  native_decide",
                "  omega",
                "  simp",
                "  assumption",
            ],
        },
        {
            "goal_id": "G6_weft_crow_cancellation_witness",
            "theorem_name": "g6_weft_crow_cancellation_witness",
            "theorem_decl": ": (3 * 3 + 3 * 3 = 18) ∧ ((3 + 3) * (3 + 3) + (3 + (-3)) * (3 + (-3)) = 36)",
            "win_len": 2,
            "candidates": [
                "  sorry",
                "  omega",
                "  native_decide",
                "  constructor <;> rfl",
                "  assumption",
                "  contradiction",
                "  exact rfl",
                "  grind",
            ],
        },
        {
            "goal_id": "G7_a16_hamming_even_xor_cancel",
            "theorem_name": "g7_a16_hamming_even_xor_cancel",
            "theorem_decl": "(b0 b1 b2 b3 : Bool) : xor (xor (xor (xor b0 b1) b2) b3) (xor (xor (xor b0 b1) b2) b3) = false",
            "win_len": 2,
            "candidates": [
                "  sorry",
                "  rfl",
                "  omega",
                "  native_decide",
                "  cases b0 <;> cases b1 <;> cases b2 <;> cases b3 <;> rfl",
                "  assumption",
                "  contradiction",
                "  simp",
            ],
        },
    ]


def run_deterministic_preflight_receipt(
    *,
    prefilter_fn: Callable[[str], list[str]] = static_r13b_prefilter,
) -> dict[str, Any]:
    """Pure-stdlib deterministic receipt (bit-identical across -I -B, -I -O -B, -I -B -W error)."""
    engine = Spec8HolonomyEngine(seed=11117)
    suite = build_pure_init_spec8_goal_suite()
    ckpt = engine.checkpoint_16b()
    arena0 = engine.synthesize_spec8_branch_arena("ALL_REJECT_TEST", ["  sorry"] * SPEC8_BRANCHES, seed=42)
    rb = engine.speculative_perturb_and_rollback_16b(ckpt, arena0)
    arena1 = engine.synthesize_spec8_branch_arena(suite[0]["goal_id"], suite[0]["candidates"], seed=42)
    cm = engine.commit_winning_branch(arena1, b_win=4, win_len=suite[0]["win_len"])

    traps = (
        ("sorry", "theorem t : True := by sorry"),
        ("native_decide", "theorem t : 1 = 1 := by native_decide"),
        ("import", "import Init\ntheorem t : True := trivial"),
        ("axiom", "axiom boom : False"),
        ("unsafe", "unsafe def f : Nat := 0"),
        ("set_option", "set_option warn.sorry false\ntheorem t : True := trivial"),
    )
    traps_blocked = sum(1 for _lbl, src in traps if len(prefilter_fn(src)) > 0)
    require_ok(traps_blocked == len(traps), "R13B_TRAP_MISSED", f"{traps_blocked}/{len(traps)}")

    report: dict[str, Any] = {
        "schema": "weft.geosphere.pi16_spec8_lean_bridge.preflight.v1",
        "goals_in_suite": len(suite),
        "r13b_static_traps_blocked": traps_blocked,
        "rollback_16b": rb,
        "commit_sample": cm,
        "state_bytes_saved": compute_state_bytes_saved(),
        "status": "PASS",
    }
    report["payload_sha256"] = sha256_hex(canonical_json_bytes(report))
    return report


def run_live_lean_spec8_synthesis(
    *,
    oracle: Any | None = None,
    include_timings: bool = True,
) -> dict[str, Any]:
    """Execute 8-branch speculative theorem synthesis against an isolated Lean 4 oracle.

    - Step 0: All-reject adversarial round (8/8 rejected -> 16 B Pi_{t0} rollback, 0.0 drift).
    - Steps 1..7: 7 pure-Init goals (8 parallel branches each -> commit winning branch).
    """
    active_oracle = oracle if oracle is not None else Lean4R12SandboxOracle()
    engine = Spec8HolonomyEngine(seed=11117)
    suite = build_pure_init_spec8_goal_suite()

    all_reject_tactics = [
        "  sorry",
        "  admit",
        "  native_decide",
        "  rfl",
        "  grind",
        "  omega",
        "  assumption",
        "  contradiction",
    ]
    ckpt0 = engine.checkpoint_16b()
    arena0 = engine.synthesize_spec8_branch_arena("S0_all_reject_rollback", all_reject_tactics, seed=42)
    res0 = active_oracle.verify_8_branches_parallel(
        theorem_name="s0_all_reject_rollback",
        theorem_decl="(w : Int) : (1 - w * w) * (1 - w * w) + (2 * w) * (2 * w) = (1 + w * w) * (1 + w * w)",
        candidate_tactics=all_reject_tactics,
    )
    accepted0 = [r for r in res0 if r["accepted"]]
    require_ok(len(accepted0) == 0, "ALL_REJECT_ROUND_ACCEPTED", str(accepted0))
    rb0 = engine.speculative_perturb_and_rollback_16b(ckpt0, arena0)

    grind_caught_choice = any(
        r["stage"] == "R13B_FORBIDDEN_AXIOM" and "Classical.choice" in r["reason"] for r in res0
    )
    require_ok(grind_caught_choice, "CLASSICAL_CHOICE_NOT_CAUGHT", str(res0))

    goal_receipts: list[dict[str, Any]] = []
    total_branches_checked = len(res0)
    total_r13b_static_blocked = sum(1 for r in res0 if r["stage"] == "R13B_STATIC_REJECT")
    total_choice_blocked = sum(1 for r in res0 if r["stage"] == "R13B_FORBIDDEN_AXIOM")

    for goal in suite:
        ckpt = engine.checkpoint_16b()
        arena = engine.synthesize_spec8_branch_arena(goal["goal_id"], goal["candidates"], seed=42)
        branch_res = active_oracle.verify_8_branches_parallel(
            theorem_name=goal["theorem_name"],
            theorem_decl=goal["theorem_decl"],
            candidate_tactics=goal["candidates"],
        )
        total_branches_checked += len(branch_res)
        total_r13b_static_blocked += sum(1 for r in branch_res if r["stage"] == "R13B_STATIC_REJECT")
        total_choice_blocked += sum(1 for r in branch_res if r["stage"] == "R13B_FORBIDDEN_AXIOM")

        winners = [r for r in branch_res if r["accepted"]]
        require_ok(len(winners) >= 1, "GOAL_UNSOLVED", f"{goal['goal_id']}: {branch_res}")
        win = winners[0]
        commit = engine.commit_winning_branch(arena, b_win=win["branch_idx"], win_len=goal["win_len"])
        rec: dict[str, Any] = {
            "goal_id": goal["goal_id"],
            "theorem_name": f"Spec8Live.{goal['theorem_name']}",
            "winning_branch": win["branch_idx"],
            "winning_axioms": win["axioms"],
            "winning_source_sha256": win["source_sha256"],
            "branches_rejected": len(branch_res) - len(winners),
            "pre_state_sha256": ckpt.state_sha256,
            "commit": commit,
        }
        if include_timings:
            rec["winning_lean_ms"] = win["elapsed_ms"]
            rec["parallel_8branch_max_ms"] = max(r["elapsed_ms"] for r in branch_res)
        goal_receipts.append(rec)

    out: dict[str, Any] = {
        "schema": "weft.geosphere.pi16_spec8_lean_bridge.live.v1",
        "lean_version": active_oracle.lean_version,
        "r12_lean_path_scrubbed": "LEAN_PATH" not in active_oracle.env,
        "goals_solved": len(goal_receipts),
        "goals_total": len(suite),
        "all_reject_rollback_step": {
            "branches_checked": len(res0),
            "branches_accepted": 0,
            "classical_choice_caught_on_grind": grind_caught_choice,
            "rollback": rb0,
        },
        "total_branches_verified": total_branches_checked,
        "total_r13b_static_blocked": total_r13b_static_blocked,
        "total_classical_choice_blocked": total_choice_blocked,
        "engine_commits": engine.commits,
        "engine_rollbacks": engine.rollbacks,
        "state_bytes_saved": compute_state_bytes_saved(),
        "goal_receipts": goal_receipts,
        "status": "PASS",
    }
    if not include_timings:
        out["payload_sha256"] = sha256_hex(canonical_json_bytes(out))
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Weft-Geosphere 16 B Pi_{t0} Rollback & Spec8 x Lean 4.36.0 Micro-Prover Bridge"
    )
    parser.add_argument("--mode", choices=("deterministic", "live-lean"), default="deterministic")
    parser.add_argument("--no-timings", action="store_true", help="Strip wall-clock timings for bit-identical replay")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.mode == "deterministic":
            rep = run_deterministic_preflight_receipt()
        else:
            rep = run_live_lean_spec8_synthesis(include_timings=not args.no_timings)
        sys.stdout.buffer.write(canonical_json_bytes(rep) + b"\n")
        return 0
    except WeftHolonomyError as exc:
        sys.stderr.write(f"ERROR [{exc.code}]: {exc.message}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
