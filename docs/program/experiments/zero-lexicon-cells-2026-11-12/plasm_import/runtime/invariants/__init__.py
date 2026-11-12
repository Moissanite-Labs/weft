"""Weft Invariants Gate (Codebase C2)."""
from .invariants import (
    HOMEOSTATIC_TENSION_MAX,
    HOMEOSTATIC_TENSION_MIN,
    R_INVARIANT,
    ROYALTY_UPSTREAM_BPS,
    ROYALTY_WEAVER_BPS,
    TENSION_MAX,
    compute_royalty_split,
    load_conformance_vectors,
    verify_tension_bound,
    verify_weight_update_safety,
    verify_weight_update_safety_ex,
)

__all__ = [
    "HOMEOSTATIC_TENSION_MAX",
    "HOMEOSTATIC_TENSION_MIN",
    "R_INVARIANT",
    "ROYALTY_UPSTREAM_BPS",
    "ROYALTY_WEAVER_BPS",
    "TENSION_MAX",
    "compute_royalty_split",
    "load_conformance_vectors",
    "verify_tension_bound",
    "verify_weight_update_safety",
    "verify_weight_update_safety_ex",
]
