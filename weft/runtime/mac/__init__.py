"""
Apple Silicon / Darwin Runtime Module
=====================================
Includes:
  - `metal_loom.py`: Lineage Alpha / Lineage Beta mitosis loop on Apple Silicon MPS.
  - `swarm_loom.py`: Vectorized Plasm Colony micro-swarm and StratifiedSwarmArena.
  - `darwin_sysctl.py`: Darwin hardware telemetry bridge.
"""

from .darwin_sysctl import (
    read_darwin_hardware_metrics,
    read_host_hardware_metrics,
)
from .metal_loom import run_metal_mitotic_loom
from .swarm_loom import (
    DEFAULT_SWARM_SHM_NAME,
    SWARM_HEADER_SIZE,
    StratifiedSwarmArena,
    SwarmArenaHeader,
    VectorizedPlasmColony,
    compute_swarm_arena_size,
    run_swarm_loom_cycle,
)

__all__ = [
    "DEFAULT_SWARM_SHM_NAME",
    "SWARM_HEADER_SIZE",
    "StratifiedSwarmArena",
    "SwarmArenaHeader",
    "VectorizedPlasmColony",
    "compute_swarm_arena_size",
    "read_darwin_hardware_metrics",
    "read_host_hardware_metrics",
    "run_metal_mitotic_loom",
    "run_swarm_loom_cycle",
]
