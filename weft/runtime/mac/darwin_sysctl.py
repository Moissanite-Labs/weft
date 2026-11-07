#!/usr/bin/env python3
"""
Darwin / Host Hardware Telemetry Reader
=======================================
Compatibility entrypoint delegating to Codebase C6 (`weft/runtime/telemetry/host_metrics.py`).
Fixes Issue #16: never invents `ncpu=10, mem_gb=64.0` when `sysctl` is unavailable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from weft.runtime.telemetry.host_metrics import (  # noqa: E402
    read_darwin_hardware_metrics,
    read_host_hardware_metrics,
)

__all__ = ["read_darwin_hardware_metrics", "read_host_hardware_metrics"]

if __name__ == "__main__":
    print(json.dumps(read_host_hardware_metrics(), indent=2))
