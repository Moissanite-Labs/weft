# Darwin / Apple Silicon harness

Extracted from `weft/mac.md`:

- `metal_loom.py`: Lineage Alpha / Lineage Beta single-cell mitosis loop (MPS when available).
- `swarm_loom.py`: Vectorized Plasm Colony micro-swarm on Apple Silicon MPS with `StratifiedSwarmArena` zero-copy shared memory. Five zero-order modes: `paper1_blind`, `hgt_isolated`, `hgt_foraging`, `dissipative_chemostat` (PR #118 L2 laws), and `graded_chemostat` (E15 unsolved-gap allocation). Results: `https://github.com/Moissanite-Labs/weft-loom/blob/main/experiments/apple-silicon-swarm-2026-11/` and `https://github.com/Moissanite-Labs/weft-loom/blob/main/experiments/graded-chemostat-e15-2026-11/`.
- `within_shard_midrank_pool` in `swarm_loom.py`: pools cell scores across shards as within-shard mid-rank percentiles, so a per-shard baseline shift cannot reorder cells. Not yet called by `run_swarm_loom_cycle`.
- `darwin_sysctl.py`: sysctl homeostasis telemetry bridge (safe on non-Darwin hosts).

Run `python3 -m unittest discover -s weft/runtime/mac -p "test_*.py"` to run unit tests.
