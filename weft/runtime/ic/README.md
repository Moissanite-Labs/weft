# Weft Interaction Combinator VM & BCP Serializer (`weft/runtime/ic`)

Codebase **C3** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I5** (IC Graph Serialization & Execution Commitment) and consuming Interface **I3** (`weft/runtime/invariants`).

## Purpose and boundary

Provide a flat-array Interaction Combinator reducer (`FlatCombinatorVM`) and canonical Binary Combinator Packet (`BCP`, magic `0x57454654`) graph serializer (`bcp_codec.py`):

- **Pure Lafont Basis (`ERA = 0`, `CON = 1`, `DUP = 2`)**:
  - Bidirectional port-wired active-pair annihilation (`CON-CON`, `DUP(L)-DUP(L)`, `ERA-ERA`), commutation (`CON-DUP`, `DUP(L)-DUP(M)` for `L != M`), and erasure (`ERA` propagation).
  - These are the current variant's local rewrite rules. The tests do not establish confluence of this implementation.
- **Weft Metabolic & Superposition Extensions (`VLV = 3`, `FRC = 4`, `SUP = 5`)**:
  - `VLV` gates reductions through `weft.runtime.invariants.verify_tension_bound` and transitions to `FRC` + `ERA` when tension exceeds `TENSION_MAX` (`85.0`).
  - `SUP(L)` provides labeled superposition nodes that annihilate with `DUP(L)` and commute with `DUP(M)` (`L != M`).
- **Graph-Committed Execution Record (`trace_commitment_sha256`)**:
  - Hashes the initial BCP graph, canonical step-log JSON and final BCP graph with explicit domain separators (#21, #29). Graph differences affect the commitment under SHA-256's collision-resistance assumption; this is not a proof of valid execution.

## BCP V1 storage contract

Serialization preserves capacity exactly, including zero-capacity empty arenas,
full arenas and sparse slot IDs. Valid canonical bytes round-trip unchanged.
The header and node layouts are documented in `bcp_codec.py`.

Both directions require ascending unique slots below capacity, tags `0..5`,
zero flags/reserved bytes, at most 65,535 active records, and ports equal to `-1`
or a slot in `[0, capacity)`. Decoding rejects bad magic/version, inconsistent
length and invalid records **before allocating the arena**. Its default limit is
1,048,576 slots (15 MiB for the three NumPy arrays). A caller can supply an
explicit `max_capacity` node limit suited to its own memory budget. This limit is
a decoder resource policy, not a change to the uint32 capacity field.

This is an **active-node storage snapshot**, not an execution checkpoint. It
does not preserve the allocator cursor, reduction count, trace or initial graph.
The decoder starts allocation after the highest restored slot and uses the
existing free-slot fallback. In-range references to free slots remain encodable,
as in the existing open-interface examples. Peer-port identity, reciprocal
wiring, active-pair validity and multi-edge semantics need a separate topology
contract; range validation does not establish a well-formed interaction net.

## Reduction failure and valve contract

Before any graph, allocator, initial-snapshot or trace mutation, an allocating
rule checks its entire current peak requirement: erasure propagation needs two
free slots, commutation four, and valve excision one. The old pair remains live
during this check. Arena exhaustion raises `MemoryError` and preserves all VM
state. This keeps the existing successful allocation/rewrite order; it does not
introduce reuse of the old pair or thread-safe concurrent allocation.

`VLV` rejects nonfinite tension or budget with `ValueError`, without a
transition. For finite values, the existing predicate remains: the C2 tension
gate accepts `0 <= tension <= 85`, and the budget must be strictly positive.
Otherwise the current excision rule applies. The committed VLV trace records
both exact float inputs (no tension rounding). There is **no cost or debit** in
this API: a positive budget is presently a caller-supplied permission signal,
not a metered account. Choosing a cost unit, reserving/debiting it atomically and
binding it to durable ownership remains open under issue #43 and I3/#42.

Other open work under #43: graph topology and a reference semantics, continuation
replay, justified confluence claims, and an execution verifier. The current
digest binds bytes and steps; it does not prove that the recorded reductions
were allowed. These repairs do not close those research/contract questions.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/ic -p 'test_*.py'
```

The storage/failure regression suite uses independently packed wire fixtures,
minimum/full/sparse capacities, malformed metadata/ports, resource limits,
exhaustion in every allocating rule, prior execution history and nonfinite VLV
inputs. These are CPU tests; no GPU performance or Apple hardware claim follows.
