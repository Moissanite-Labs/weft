#!/usr/bin/env python3
"""NumPy float32 port of the Plasm substrate primitives, with identical
semantics to `weft/runtime/plasm/plasm.py` (Interfaces I4, I7) and
`weft/runtime/invariants/invariants.py` (Interface I3).

Why a port: plasm requires PyTorch. PyTorch is absent on this machine
(no interpreter has it). The export of the reference runtime is kept
verbatim under `plasm_import/` for the record; this port is the code
that actually runs, and its semantics were checked line-by-line against
the reference. Differences vs reference, explicitly:
  - Shared-memory POSIX arena is replaced by identically-shaped numpy
    buffers (the arena's geometry is unchanged: 256x256 focal, 1024
    sympathetic_ring, 64x1024 hippocampal lattice). shm is an xfer
    mechanism, not a semantic one.
  - torch device abstraction removed; numpy on CPU, float32 throughout.
  - Watermark correction uses W^T v orientation from the reference,
    unchanged.
  - `verify_weight_update_safety_ex` and `verify_tension_bound` are
    ported with the same branch structure, constants, and reasons.
"""
import hashlib
import math
from typing import Dict, Tuple

import numpy as np

FOCAL_FLOATS = 256 * 256
SYMPATHETIC_FLOATS = 1024
HIPPOCAMPAL_FLOATS = 64 * 1024
ARENA_BYTES = FOCAL_FLOATS * 4 + SYMPATHETIC_FLOATS * 4 + HIPPOCAMPAL_FLOATS * 4 + 12 + 12288

R_INVARIANT = 120.0
TENSION_MAX = 85.0
HOMEOSTATIC_MIN = 15.0
HOMEOSTATIC_MAX = 35.0


def plasticity_mask(w: np.ndarray, core_rows: int = 64) -> np.ndarray:
    rows, cols = w.shape
    col_mag = np.linalg.norm(w, axis=0, keepdims=True)
    gate = 1.0 / (1.0 + np.exp(col_mag - col_mag.mean()))
    gate = np.broadcast_to(gate, (rows, cols)).copy()
    if core_rows > 0:
        gate[:core_rows, :] = 0.0
    return gate.astype(np.float32)


def watermark_embed(w: np.ndarray, seed: bytes = b"WEFT_DETERMINISTIC_SEED_V1", core_rows: int = 64):
    dim = w.shape[0]
    digest = hashlib.sha256(seed).digest()
    gen = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    trigger = np.zeros(dim, dtype=np.float32)
    core = gen.standard_normal(core_rows).astype(np.float32)
    core = core / np.linalg.norm(core)
    trigger[:core_rows] = core
    gen2 = np.random.default_rng(int.from_bytes(digest[8:16], "big"))
    target = gen2.standard_normal(dim).astype(np.float32)
    target = (target / np.linalg.norm(target)) * 3.0
    current_resp = w.T @ trigger
    correction = np.outer(trigger, target - current_resp)
    w_mark = (w + correction).astype(np.float32)
    verify_resp = w_mark.T @ trigger
    align = float(
        np.dot(verify_resp, target)
        / (np.linalg.norm(verify_resp) * np.linalg.norm(target) + 1e-12)
    )
    return w_mark, trigger.astype(np.float32), target.astype(np.float32), align


def watermark_verify(baseline: np.ndarray, current: np.ndarray,
                     trigger: np.ndarray, target: np.ndarray,
                     min_cos: float = 0.85, max_drift: float = 0.35) -> Dict[str, object]:
    base_resp = baseline.T @ trigger
    curr_resp = current.T @ trigger
    cos_align = float(
        np.dot(curr_resp, target) / (np.linalg.norm(curr_resp) * np.linalg.norm(target) + 1e-12)
    )
    base_norm = float(np.linalg.norm(base_resp)) + 1e-8
    drift = float(np.linalg.norm(curr_resp - base_resp) / base_norm)
    ok = math.isfinite(cos_align) and math.isfinite(drift) and cos_align >= min_cos and drift <= max_drift
    return {"retained": ok, "cosine_alignment": cos_align, "response_l2_drift": drift}


def safety_gate_ex(baseline: np.ndarray, candidate: np.ndarray,
                   budget: float, step_cost: float, r_inv: float = R_INVARIANT):
    """Port of verify_weight_update_safety_ex (Frobenius drift vs budget)."""
    finite = all(np.isfinite(np.asarray(x)).all() for x in (baseline, candidate))
    if not (math.isfinite(budget) and math.isfinite(step_cost) and math.isfinite(r_inv)):
        return False, float("inf"), float("nan"), "non_finite_parameters"
    if not finite:
        return False, float("inf"), budget, "non_finite_parameters"
    if budget <= 0.0 or step_cost <= 0.0 or r_inv < 0.0:
        return False, float("inf"), budget - step_cost, "non_positive_budget_or_cost"
    if budget < step_cost:
        return False, float("inf"), budget - step_cost, "insufficient_metabolic_budget"
    dist = float(np.linalg.norm(candidate - baseline))
    if dist <= r_inv:
        return True, dist, budget - step_cost, "ok"
    return False, dist, budget - step_cost, "baseline_distance_exceeded"


def tension_bound(tension: float, max_tension: float = TENSION_MAX,
                  homeo_min: float = HOMEOSTATIC_MIN, homeo_max: float = HOMEOSTATIC_MAX) -> Dict[str, object]:
    t_val = float(tension)
    ok = math.isfinite(t_val) and t_val >= 0.0
    accepted = ok and t_val <= float(max_tension)
    homeo = ok and (homeo_min <= t_val <= homeo_max)
    return {"accepted": accepted, "homeostatic": homeo, "excision_triggered": not accepted,
            "tension": t_val, "reason": "ok" if accepted else "tension_exceeds_max"}
