# Darwin / Apple Silicon harness

Extracted from `weft/mac.md`:

- `metal_loom.py`: Lineage Alpha / Lineage Beta single-cell mitosis loop (MPS when available).
- `swarm_loom.py`: Vectorized Plasm Colony micro-swarm on Apple Silicon MPS with `StratifiedSwarmArena` zero-copy shared memory. Four zero-order modes: `paper1_blind`, `hgt_isolated`, `hgt_foraging`, `dissipative_chemostat` (PR #118 L2 laws). Results: `docs/program/experiments/apple-silicon-swarm-2026-11/`.
- `darwin_sysctl.py`: sysctl homeostasis telemetry bridge (safe on non-Darwin hosts).

Run `python3 -m unittest discover -s weft/runtime/mac -p "test_*.py"` to run unit tests.
