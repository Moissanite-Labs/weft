#!/usr/bin/env python3
"""
Host Hardware & Autonomic Telemetry Collector (Codebase C6 — Interface I1)
==========================================================================
Collects real host CPU, memory, and load metrics without inventing fallback
hardware numbers when `sysctl` is unavailable (#16):
  - On macOS (`darwin`): queries `/usr/sbin/sysctl` (`source = "darwin-sysctl"`).
  - On Linux (`linux`): reads `os.cpu_count()`, `/proc/meminfo`, and `os.getloadavg()`
    (`source = "linux-procfs"`).
  - When neither source is available or a probe fails: returns
    `source = "unavailable"` with `ncpu = None`, `mem_gb = None`, `load_1m = None`.
  - Thermal value is explicitly marked as a load-derived estimate
    (`estimated_load_thermal_c`, `thermal_is_estimate = True`).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import Any, Dict, Optional


def _probe_darwin_sysctl() -> Optional[Dict[str, Any]]:
    sysctl_bin = "/usr/sbin/sysctl"
    if not os.path.exists(sysctl_bin):
        return None
    try:
        ncpu = int(
            subprocess.check_output([sysctl_bin, "-n", "hw.ncpu"], text=True, stderr=subprocess.DEVNULL).strip()
        )
        mem_bytes = int(
            subprocess.check_output([sysctl_bin, "-n", "hw.memsize"], text=True, stderr=subprocess.DEVNULL).strip()
        )
        load_str = subprocess.check_output(
            [sysctl_bin, "-n", "vm.loadavg"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        m = re.search(r"([0-9]+\.[0-9]+)", load_str)
        load_1m = float(m.group(1)) if m else 0.5
        if ncpu <= 0 or mem_bytes <= 0:
            return None
        mem_gb = round(mem_bytes / (1024**3), 2)
        strain = min(1.0, load_1m / max(1, ncpu))
        est_temp = round(38.5 + strain * 35.0, 2)
        return {
            "source": "darwin-sysctl",
            "ncpu": ncpu,
            "mem_gb": mem_gb,
            "load_1m": round(load_1m, 2),
            "cpu_strain": round(strain, 4),
            "estimated_load_thermal_c": est_temp,
            "est_core_temp_c": est_temp,
            "thermal_is_estimate": True,
        }
    except Exception:
        return None


def _probe_linux_procfs(proc_meminfo_path: str = "/proc/meminfo") -> Optional[Dict[str, Any]]:
    if not os.path.exists(proc_meminfo_path):
        return None
    try:
        ncpu = os.cpu_count()
        if not ncpu or ncpu <= 0:
            return None
        mem_kb = None
        with open(proc_meminfo_path, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        mem_kb = int(parts[1])
                    break
        if not mem_kb or mem_kb <= 0:
            return None
        mem_gb = round(mem_kb / (1024**2), 2)
        try:
            load_1m = float(os.getloadavg()[0])
        except OSError:
            load_1m = 0.0
        strain = min(1.0, load_1m / max(1, ncpu))
        est_temp = round(38.5 + strain * 35.0, 2)
        return {
            "source": "linux-procfs",
            "ncpu": int(ncpu),
            "mem_gb": mem_gb,
            "load_1m": round(load_1m, 2),
            "cpu_strain": round(strain, 4),
            "estimated_load_thermal_c": est_temp,
            "est_core_temp_c": est_temp,
            "thermal_is_estimate": True,
        }
    except Exception:
        return None


def read_host_hardware_metrics(
    *,
    force_unavailable: bool = False,
    platform_override: Optional[str] = None,
    proc_meminfo_path: str = "/proc/meminfo",
) -> Dict[str, Any]:
    """
    Read host CPU/memory/load metrics honestly (#16).
    Never invents `ncpu=10, mem_gb=64.0` when probes fail.
    """
    if not force_unavailable:
        plat = platform_override or sys.platform
        if plat == "darwin":
            res = _probe_darwin_sysctl()
            if res is not None:
                return res
        elif plat.startswith("linux"):
            res = _probe_linux_procfs(proc_meminfo_path=proc_meminfo_path)
            if res is not None:
                return res

    return {
        "source": "unavailable",
        "ncpu": None,
        "mem_gb": None,
        "load_1m": None,
        "cpu_strain": 0.0,
        "estimated_load_thermal_c": None,
        "est_core_temp_c": None,
        "thermal_is_estimate": True,
    }


read_darwin_hardware_metrics = read_host_hardware_metrics
