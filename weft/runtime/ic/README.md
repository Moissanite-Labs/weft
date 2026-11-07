# Weft Interaction Combinator VM & BCP Serializer (`weft/runtime/ic`)

Codebase **C3** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I5** (IC Graph Serialization & Execution Commitment) and consuming Interface **I3** (`weft/runtime/invariants`).

## Purpose and boundary

Provide a flat-array Interaction Combinator reducer (`FlatCombinatorVM`) and canonical Binary Combinator Packet (`BCP`, magic `0x57454654`) graph serializer (`bcp_codec.py`):

- **Pure Lafont Basis (`ERA = 0`, `CON = 1`, `DUP = 2`)**:
  - Bidirectional port-wired active-pair annihilation (`CON-CON`, `DUP(L)-DUP(L)`, `ERA-ERA`), commutation (`CON-DUP`, `DUP(L)-DUP(M)` for `L != M`), and erasure (`ERA` propagation).
  - Satisfies strong confluence on pure `(ERA, CON, DUP)` nets (#21).
- **Weft Metabolic & Superposition Extensions (`VLV = 3`, `FRC = 4`, `SUP = 5`)**:
  - `VLV` gates reductions through `weft.runtime.invariants.verify_tension_bound` and transitions to `FRC` + `ERA` when tension exceeds `TENSION_MAX` (`85.0`).
  - `SUP(L)` provides labeled superposition nodes that annihilate with `DUP(L)` and commute with `DUP(M)` (`L != M`).
- **Graph-Committed Execution Record (`trace_commitment_sha256`)**:
  - Commits to `SHA256(initial_graph_bcp || step_log_json || final_graph_bcp)` so two distinct initial graphs can never produce colliding execution commitments even when their `(op, a, b)` step tuples match (#21, #29).

## Verification

```bash
python3 -m unittest discover -s weft/runtime/ic -p 'test_*.py'
```
