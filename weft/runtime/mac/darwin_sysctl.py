#!/usr/bin/env python3
"""Darwin sysctl telemetry bridge (homeostasis / membrane tension signals).
Extracted from weft/mac.md and weft/runtime/aywa/weft_daemon.py.
"""

from __future__ import annotations

import json
import subprocess
import sys


def read_darwin_hardware_metrics() -> dict:
    try:
        ncpu = int(subprocess.check_output(["/usr/sbin/sysctl", "-n", "hw.ncpu"], text=True).strip())
        mem_bytes = int(subprocess.check_output(["/usr/sbin/sysctl", "-n", "hw.memsize"], text=True).strip())
        load_str = subprocess.check_output(["/usr/sbin/sysctl", "-n", "vm.loadavg"], text=True).strip().strip("{}").split()
        load_1m = float(load_str[0]) if load_str else 1.0
    except Exception:
        ncpu, mem_bytes, load_1m = 1, 0, 0.0
    cpu_strain = min(1.0, load_1m / max(1.0, float(ncpu)))
    est_temp_c = 41.5 + (cpu_strain * 28.0)
    return {
        "platform": "darwin",
        "ncpu": ncpu,
        "mem_gb": round(mem_bytes / (1024**3), 1),
        "load_1m": load_1m,
        "cpu_strain": round(cpu_strain, 4),
        "est_core_temp_c": round(est_temp_c, 2),
    }


def main() -> int:
    print(json.dumps(read_darwin_hardware_metrics(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
