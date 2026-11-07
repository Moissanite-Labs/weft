#!/usr/bin/env python3
"""
Weft Stratified Shared-Memory & Apple Silicon MPS Tensor Runtime
================================================================
Compatibility entrypoint re-exporting Codebase C1 (`weft/runtime/plasm/`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.plasm import (  # noqa: E402
    ARENA_BYTE_SIZE,
    DEFAULT_SEED_PHRASE,
    FOCAL_FLOATS,
    HIPPOCAMPAL_FLOATS,
    R_INVARIANT,
    SHM_NAME,
    SYMPATHETIC_FLOATS,
    StratifiedAppleSiliconPlasm,
    StratifiedMemoryArena,
    adjust_homeostatic_mutation_scale,
    compute_plasticity_mask,
    embed_weight_watermark,
    run_plasm_cycle,
    run_weft_plasm_cycle,
    select_compute_device,
    verify_watermark_retention,
    verify_weight_update_safety,
    weight_frobenius_size,
)

__all__ = [
    "ARENA_BYTE_SIZE",
    "DEFAULT_SEED_PHRASE",
    "FOCAL_FLOATS",
    "HIPPOCAMPAL_FLOATS",
    "R_INVARIANT",
    "SHM_NAME",
    "SYMPATHETIC_FLOATS",
    "StratifiedAppleSiliconPlasm",
    "StratifiedMemoryArena",
    "adjust_homeostatic_mutation_scale",
    "compute_plasticity_mask",
    "embed_weight_watermark",
    "run_plasm_cycle",
    "run_weft_plasm_cycle",
    "select_compute_device",
    "verify_watermark_retention",
    "verify_weight_update_safety",
    "weight_frobenius_size",
]

if __name__ == "__main__":
    print(json.dumps(run_weft_plasm_cycle(generations=4), indent=2))
