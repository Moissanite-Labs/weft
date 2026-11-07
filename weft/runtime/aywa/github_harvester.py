#!/usr/bin/env python3
"""
Aywa / Moissanite-Labs Telemetry Harvester
==========================================
Compatibility entrypoint delegating to Codebase C6 (`weft/runtime/telemetry/harvester.py`).
Fixes Issue #15: removes `suspended_accounts`, marks offline data `"source": "fixture"`,
and supports `--live` GitHub REST API harvesting.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.telemetry.harvester import (  # noqa: E402
    MOISSANITE_REPOS_FIXTURE as MOISSANITE_REPOS,
    compute_gini,
    fetch_live_org_repos,
    harvest_moissanite_telemetry,
    main,
)
from weft.runtime.telemetry.sym2p_codec import encode_sym2p, parse_sym2p  # noqa: E402

__all__ = [
    "MOISSANITE_REPOS",
    "compute_gini",
    "encode_sym2p",
    "fetch_live_org_repos",
    "harvest_moissanite_telemetry",
    "parse_sym2p",
]

if __name__ == "__main__":
    raise SystemExit(main())
