#!/usr/bin/env python3
"""
Apple Silicon Metal / MPS Mitotic Loom Harness
==============================================
Compatibility entrypoint delegating to Codebase C1 (`weft/runtime/plasm/`)
so that `weft/runtime/mac/metal_loom.py` shares the repaired baseline-distance
gate (#2), core-freezing plasticity mask (#6, #22), and target-directed A/B
selection (#5, #22).

Report contract (#51): the arguments a caller passes here are the ones that
actually execute. `r_invariant` and `initial_budget` are forwarded into
`run_weft_plasm_cycle`, which returns an `effective_config` describing the
execution. `dim` is validated against the fixed 256x256 focal arena; it is
not a free parameter. No field in the returned report is echoed without
being forwarded.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.plasm import run_weft_plasm_cycle  # noqa: E402

ARENA_DIM = 256


def run_metal_mitotic_loom(
    dim: int = ARENA_DIM,
    generations: int = 3,
    r_invariant: Optional[float] = None,
    initial_budget: float = 100.0,
) -> Dict[str, Any]:
    if int(dim) != ARENA_DIM:
        raise ValueError(
            f"metal loom executes the fixed {ARENA_DIM}x{ARENA_DIM} I4 focal arena; "
            f"dim={dim!r} is not an executable configuration. Resize the arena layout "
            f"in weft/runtime/plasm instead of changing this argument."
        )
    return run_weft_plasm_cycle(
        generations=generations,
        r_invariant=r_invariant,
        initial_budget=initial_budget,
    )


if __name__ == "__main__":
    print(json.dumps(run_metal_mitotic_loom(), indent=2))
