#!/usr/bin/env python3
"""
Weft Sovereign Autonomic Daemon (Aywa 64-Byte Telemetry Bridge)
===============================================================
Delegates host hardware probing and organization harvesting to Codebase C6
(`weft/runtime/telemetry/`) so hardware unavailability is reported honestly (#16),
`suspended_accounts` is never emitted (#15), and slot 2 (`system_time`) carries
the one-shot harvest interval (or an explicit `elapsed_seconds`) rather than
wall-clock or thermal proxies (#78).
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.telemetry.frame64 import (  # noqa: E402
    MAX_RELATIVE_CLOCK_SECONDS,
    encode_frame_64b_bytes,
)
from weft.runtime.telemetry.harvester import harvest_moissanite_telemetry  # noqa: E402
from weft.runtime.telemetry.host_metrics import (  # noqa: E402
    read_darwin_hardware_metrics,
    read_host_hardware_metrics,
)

SHM_BRIDGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "data", "moissanite_telemetry.bin")
_DAEMON_START_MONOTONIC = time.monotonic()


def build_unified_64b_frame(
    out_dir: str | None = None,
    *,
    live_github: bool = False,
    elapsed_seconds: float | None = None,
) -> Dict[str, Any]:
    hw = read_host_hardware_metrics()
    moiss = harvest_moissanite_telemetry(out_dir, live=live_github)

    floats = list(moiss["uniform_frame_64b_floats"])
    blended_tension = round(0.65 * float(moiss["org_tension"]) + 0.35 * float(hw["cpu_strain"] or 0.0), 4)
    floats[1] = blended_tension
    rel_s = (
        max(0.0, time.monotonic() - _DAEMON_START_MONOTONIC)
        if elapsed_seconds is None
        else float(elapsed_seconds)
    )
    if not math.isfinite(rel_s) or rel_s < 0.0 or rel_s > MAX_RELATIVE_CLOCK_SECONDS:
        raise ValueError(
            f"elapsed_seconds ({rel_s!r}) must be finite relative seconds in "
            f"[0.0, {MAX_RELATIVE_CLOCK_SECONDS:.1f}]"
        )
    floats[2] = round(rel_s, 4)

    packed = encode_frame_64b_bytes(floats)
    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "moissanite_telemetry.bin"), "wb") as fh:
            fh.write(packed)

    return {
        "status": "PASS",
        "hardware": hw,
        "moissanite_source": moiss["source"],
        "moissanite_nodes": moiss["active_nodes"],
        "org_tension": moiss["org_tension"],
        "gini_index": moiss["gini_index"],
        "shm_frame_64b_head": floats[:8],
    }


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        with tempfile.TemporaryDirectory(prefix="weft-daemon-selftest-") as scratch:
            print(json.dumps(build_unified_64b_frame(scratch), indent=2))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        print(json.dumps(build_unified_64b_frame(here), indent=2))
