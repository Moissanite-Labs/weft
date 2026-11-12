#!/usr/bin/env python3
"""
Apple Silicon Metal / MPS Mitotic Loom Harness
==============================================
Compatibility entrypoint delegating to Codebase C1 (`weft/runtime/plasm/`)
so that `weft/runtime/mac/metal_loom.py` shares the repaired baseline-distance
gate (#2), core-freezing plasticity mask (#6, #22), and target-directed A/B
selection (#5, #22).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.plasm import run_weft_plasm_cycle, select_compute_device  # noqa: E402


def run_metal_mitotic_loom(
    dim: int = 256,
    generations: int = 3,
    r_invariant: float = 10.0,
    initial_budget: float = 20.0,
) -> Dict[str, Any]:
    report = run_weft_plasm_cycle(generations=generations)
    report["dim"] = dim
    report["r_invariant"] = r_invariant
    report["initial_budget"] = initial_budget
    return report


if __name__ == "__main__":
    print(json.dumps(run_metal_mitotic_loom(), indent=2))
