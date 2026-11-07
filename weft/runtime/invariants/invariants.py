#!/usr/bin/env python3
"""
Weft Invariants Gate (Codebase C2 — Interface I3)
=================================================
Pure, zero-side-effect safety predicates shared across:
  - C1 (`weft/runtime/plasm/`): mitotic weight update gate
  - C3 (`weft/runtime/ic/`): metabolic valve reduction gate
  - C5 (`weft/runtime/gateway/`): off-chain excision monitor

Provenance:
  - Repaired from `weft/terrafab-calc.md:50-100` (C header) and `weft/README.md:389-504`.
  - Fixes Issue #2 (saved-baseline distance `||W_cand - W_base||_F <= r_invariant`
    instead of the compared-sizes trap `| ||W_cand|| - ||W_base|| |`) and M6
    (pre-check `budget >= cost > 0` before decrementing budget; reject NaN/Inf).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence, Tuple

R_INVARIANT: float = 120.0
TENSION_MAX: float = 85.0
HOMEOSTATIC_TENSION_MIN: float = 15.0
HOMEOSTATIC_TENSION_MAX: float = 35.0
ROYALTY_UPSTREAM_BPS: int = 1500
ROYALTY_WEAVER_BPS: int = 8500

VECTORS_PATH = Path(__file__).resolve().parent / "vectors.json"


def _flatten_floats(arr: Any) -> Iterable[float]:
    """Flatten nested lists, numpy arrays, or torch tensors into Python floats."""
    if hasattr(arr, "detach"):
        arr = arr.detach().cpu().reshape(-1).tolist()
    elif hasattr(arr, "reshape"):
        arr = arr.reshape(-1).tolist()
    if isinstance(arr, (list, tuple)):
        for item in arr:
            if isinstance(item, (list, tuple)):
                yield from _flatten_floats(item)
            elif isinstance(item, str):
                yield float(item)
            else:
                yield float(item)
    else:
        yield float(arr)


def verify_weight_update_safety_ex(
    baseline_w: Any,
    candidate_w: Any,
    r_invariant: float,
    current_budget: float,
    step_cost: float,
) -> Tuple[bool, float, float, str]:
    """
    Evaluate the baseline-relative Frobenius distance and metabolic budget gate.

    Returns `(accepted, baseline_distance, remaining_budget, reason)`.
    Notice that on rejection due to weight safety or non-finite values, the
    caller's budget is not consumed (`remaining_budget == current_budget`), whereas
    on budget precondition failure `remaining_budget` reports `current_budget - step_cost`
    so callers can inspect the deficit.
    """
    b_val = float(current_budget)
    c_val = float(step_cost)
    r_val = float(r_invariant)

    if not (math.isfinite(b_val) and math.isfinite(c_val) and math.isfinite(r_val)):
        return False, float("inf"), float("nan"), "non_finite_parameters"
    if b_val <= 0.0 or c_val <= 0.0 or r_val < 0.0:
        return False, float("inf"), b_val - c_val, "non_positive_budget_or_cost"
    if b_val < c_val:
        return False, float("inf"), b_val - c_val, "insufficient_metabolic_budget"

    # Fast path for torch tensors when available
    if hasattr(baseline_w, "detach") and hasattr(candidate_w, "detach"):
        import torch
        if baseline_w.shape != candidate_w.shape:
            return False, float("inf"), b_val, "shape_mismatch"
        if not bool(torch.isfinite(baseline_w).all().item() and torch.isfinite(candidate_w).all().item()):
            return False, float("inf"), b_val, "non_finite_weights"
        dist = float(torch.linalg.norm(candidate_w - baseline_w).item())
        if not math.isfinite(dist):
            return False, float("inf"), b_val, "non_finite_weights"
        if dist > r_val:
            return False, dist, b_val, "baseline_distance_exceeded"
        return True, dist, b_val - c_val, "ok"

    base_flat = list(_flatten_floats(baseline_w))
    cand_flat = list(_flatten_floats(candidate_w))
    if len(base_flat) != len(cand_flat) or len(base_flat) == 0:
        return False, float("inf"), b_val, "shape_mismatch"

    sq_sum = 0.0
    for b_elem, c_elem in zip(base_flat, cand_flat):
        if not (math.isfinite(b_elem) and math.isfinite(c_elem)):
            return False, float("inf"), b_val, "non_finite_weights"
        diff = c_elem - b_elem
        sq_sum += diff * diff

    dist = math.sqrt(sq_sum)
    if not math.isfinite(dist):
        return False, float("inf"), b_val, "non_finite_weights"
    if dist > r_val:
        return False, dist, b_val, "baseline_distance_exceeded"

    return True, dist, b_val - c_val, "ok"


def _frobenius_norm(arr: Any) -> float:
    if hasattr(arr, "detach"):
        import torch
        return float(torch.linalg.norm(arr).item())
    vals = list(_flatten_floats(arr))
    return math.sqrt(sum(v * v for v in vals))


def verify_weight_update_safety(
    baseline_weights: Any,
    current_weights: Any,
    candidate_weights: Any,
    remaining_budget: float,
    update_cost: float,
    max_baseline_distance: float = R_INVARIANT,
) -> Dict[str, Any]:
    """
    Refuse a weight update unless the remaining budget is finite and positive,
    the candidate is numeric, and drift is measured from the stored baseline
    (not the size delta between current and candidate weights).
    """
    compared_sizes = abs(
        _frobenius_norm(candidate_weights) - _frobenius_norm(current_weights)
    )

    if not math.isfinite(remaining_budget):
        return {
            "accepted": False,
            "reason": "remaining_budget_not_finite",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }
    if remaining_budget <= 0:
        return {
            "accepted": False,
            "reason": "remaining_budget_exhausted",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }
    if not math.isfinite(update_cost) or update_cost <= 0:
        return {
            "accepted": False,
            "reason": "update_cost_not_finite",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }

    accepted, dist, rem, reason = verify_weight_update_safety_ex(
        baseline_weights,
        candidate_weights,
        max_baseline_distance,
        remaining_budget,
        update_cost,
    )
    if reason == "non_finite_weights":
        return {
            "accepted": False,
            "reason": "baseline_distance_not_finite",
            "compared_sizes": compared_sizes,
            "baseline_distance": float("nan"),
            "remaining_budget": remaining_budget,
        }
    if reason == "insufficient_metabolic_budget":
        return {
            "accepted": False,
            "reason": "remaining_budget_underflow",
            "compared_sizes": compared_sizes,
            "baseline_distance": _frobenius_norm(candidate_weights) if hasattr(candidate_weights, "detach") else float("inf"),
            "remaining_budget": rem,
        }
    if not accepted:
        return {
            "accepted": False,
            "reason": reason,
            "compared_sizes": compared_sizes,
            "baseline_distance": dist,
            "remaining_budget": remaining_budget,
        }
    return {
        "accepted": True,
        "reason": "ok",
        "compared_sizes": compared_sizes,
        "baseline_distance": dist,
        "remaining_budget": rem,
    }


def verify_tension_bound(
    tension: float,
    max_tension: float = TENSION_MAX,
    homeostatic_min: float = HOMEOSTATIC_TENSION_MIN,
    homeostatic_max: float = HOMEOSTATIC_TENSION_MAX,
) -> Dict[str, Any]:
    """Check whether organizational/cellular tension is within the invariant bound."""
    t_val = float(tension)
    m_val = float(max_tension)
    if not (math.isfinite(t_val) and math.isfinite(m_val)) or t_val < 0.0:
        return {
            "accepted": False,
            "homeostatic": False,
            "excision_triggered": True,
            "tension": t_val,
            "max_tension": m_val,
            "reason": "negative_or_non_finite_tension",
        }
    accepted = t_val <= m_val
    homeostatic = homeostatic_min <= t_val <= homeostatic_max
    return {
        "accepted": accepted,
        "homeostatic": homeostatic,
        "excision_triggered": not accepted,
        "tension": t_val,
        "max_tension": m_val,
        "reason": "ok" if accepted else "tension_exceeds_max",
    }


def compute_royalty_split(
    gross_wei: int,
    upstream_bps: int = ROYALTY_UPSTREAM_BPS,
) -> Dict[str, int]:
    """Compute the 15% upstream / 85% weaver metabolic valve split in integer wei."""
    gross = int(gross_wei)
    bps = int(upstream_bps)
    if gross < 0 or not (0 <= bps <= 10000):
        raise ValueError("gross_wei must be >= 0 and upstream_bps in [0, 10000]")
    upstream = (gross * bps) // 10000
    weaver = gross - upstream
    return {
        "gross_wei": gross,
        "upstream_bps": bps,
        "upstream_wei": upstream,
        "weaver_wei": weaver,
    }


def load_conformance_vectors() -> Dict[str, Any]:
    with VECTORS_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)
