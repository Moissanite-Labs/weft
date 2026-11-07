# Weft Plasm Substrate & Mitotic Loom (`weft/runtime/plasm`)

Codebase **C1** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interfaces **I4** (Shared-Memory Layout) and **I7** (Weight Commitments) and consuming Interface **I3** (`weft/runtime/invariants`).

## Purpose and boundary

Manage the 3-tier POSIX shared-memory arena (`540,688` bytes) and execute the models-as-cells engineering contract (#6):
- **Boundary isolation**: `StratifiedMemoryArena` (`focal_workspace` 262,144 B, `sympathetic_ring` 4,096 B, `hippocampal_lattice` 262,144 B, header + lock 12,304 B).
- **Speculative A/B child lineages (#5, #22)**: candidate weight matrices `W_cand_a` and `W_cand_b` are evaluated directly against an explicit `target_out` tensor (`Fitness(target) + alpha * Novelty(hippocampus)`) and committed verbatim only when they reduce target error and pass `weft.runtime.invariants.verify_weight_update_safety_ex`.
- **Core-freezing plasticity mask (#6, #22)**: freezes the first `dim // 4` rows (`mask[:core_rows, :] == 0.0`) so core parameters and embedded provenance watermarks experience zero drift (`core_row_drift == 0.0`) while periphery weights adapt.
- **Provenance watermark threat model (#4)**: embeds the linear mark in the frozen core subspace and verifies both cosine alignment and relative L2 trigger-response drift on every cycle.
- **Clean shared-memory teardown (#17)**: releases all ctypes/numpy memoryviews before closing `SharedMemory`.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
```
