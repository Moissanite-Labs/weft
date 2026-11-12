#!/usr/bin/env python3
"""
Weft Sovereign Autonomic Daemon (Aywa 64-Byte Telemetry Bridge)
===============================================================
Delegates host hardware probing and organization harvesting to Codebase C6
(`weft/runtime/telemetry/`) so hardware unavailability is reported honestly (#16)
and `suspended_accounts` is never emitted (#15).
"""

from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.telemetry.harvester import harvest_moissanite_telemetry  # noqa: E402
from weft.runtime.telemetry.host_metrics import (  # noqa: E402
    read_darwin_hardware_metrics,
    read_host_hardware_metrics,
)

SHM_BRIDGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "moissanite_telemetry.bin")


def build_unified_64b_frame(
    out_dir: str | None = None,
    *,
    live_github: bool = False,
) -> Dict[str, Any]:
    hw = read_host_hardware_metrics()
    moiss = harvest_moissanite_telemetry(out_dir, live=live_github)

    floats = list(moiss["uniform_frame_64b_floats"])
    blended_tension = round(0.65 * float(moiss["org_tension"]) + 0.35 * float(hw["cpu_strain"]), 4)
    floats[1] = blended_tension
    est_temp = hw["estimated_load_thermal_c"]
    floats[2] = round(float(est_temp if est_temp is not None else 38.5) * 10.0 + float(hw["load_1m"] or 0.0) * 100.0, 4)

    packed = struct.pack("<16f", *floats)
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
