# Weft Plasm Substrate & Mitotic Loom (`weft/runtime/plasm`)

Codebase **C1** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interfaces **I4** ([Shared-Memory Layout](../../../docs/interfaces/I4-shared-memory.md)) and **I7** (Weight Commitments) and consuming Interface **I3** (`weft/runtime/invariants`).

## Purpose and boundary

Manage the 3-tier POSIX shared-memory arena (`540,688` bytes) and execute the models-as-cells engineering contract (#6):
- **Boundary isolation**: `StratifiedMemoryArena` (`focal_workspace` 262,144 B, `sympathetic_ring` 4,096 B, `hippocampal_lattice` 262,144 B, header + lock 12,304 B).
- **Speculative A/B child lineages (#5, #22)**: candidate weight matrices `W_cand_a` and `W_cand_b` are evaluated directly against an explicit `target_out` tensor (`Fitness(target) + alpha * Novelty(hippocampus)`) and committed verbatim only when they reduce target error and pass `weft.runtime.invariants.verify_weight_update_safety_ex` and the watermark check.
- **Core-freezing plasticity mask (#6, #22)**: freezes the first `dim // 4` rows (`mask[:core_rows, :] == 0.0`) so core parameters and embedded provenance watermarks experience zero drift (`core_row_drift == 0.0`) while periphery weights adapt.
- **Provenance watermark threat model (#4)**: embeds the linear mark in the frozen core subspace and verifies both cosine alignment and relative L2 trigger-response drift on every cycle. The distance gate alone is not a provenance control: it limits how much the weights move, not which directions, so a candidate that fails the watermark check is never committed.
- **Clean shared-memory teardown (#17)**: releases all ctypes/numpy memoryviews before closing `SharedMemory`.

## Current layout and lineage

The implemented I4 profile is a native ctypes arena with a 16-byte header,
`float32[256,256]` focal workspace, `float32[1024]` sympathetic ring,
`float32[64,1024]` hippocampal lattice, and 12,288 reserved lock bytes.
The [I4 contract](../../../docs/interfaces/I4-shared-memory.md) specifies offsets,
ABI limits, lifecycle, and the alternative layouts preserved from earlier design
iterations. Equal byte counts do not imply compatible layouts. There is no
in-memory version field or synchronization protocol yet.

Zero-copy applies to the mapped ctypes/NumPy CPU views. Tensor reads explicitly
copy into independent CPU/MPS tensors. The `cryptographic_lock` field is reserved
storage, not an implemented lock or cryptographic guarantee.

[`i4-vectors.json`](i4-vectors.json) is a static, independently specified layout
fixture with little-endian golden samples. `test_plasm.py` compares the producer
to that fixture and exercises both directions of byte exchange with a separately
attached raw consumer mapping.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
```
