#!/usr/bin/env python3
"""
Weft Flat-Array Interaction Combinator Virtual Machine
======================================================
Compatibility entrypoint re-exporting Codebase C3 (`weft/runtime/ic/`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.ic import (  # noqa: E402
    BCP_MAGIC,
    BCP_VERSION,
    FlatCombinatorVM,
    deserialize_graph_bcp,
    graph_state_sha256,
    run_combinator_self_test,
    run_ic_verification,
    serialize_graph_bcp,
)

__all__ = [
    "BCP_MAGIC",
    "BCP_VERSION",
    "FlatCombinatorVM",
    "deserialize_graph_bcp",
    "graph_state_sha256",
    "run_combinator_self_test",
    "run_ic_verification",
    "serialize_graph_bcp",
]

if __name__ == "__main__":
    print(json.dumps(run_combinator_self_test(), indent=2))
