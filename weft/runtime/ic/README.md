# Weft Interaction Combinator VM & BCP Serializer (`weft/runtime/ic`)

Codebase **C3** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I5** (IC Graph Serialization & Execution Commitment) and consuming Interface **I3** (`weft/runtime/invariants`).

## Purpose and boundary

Provide a flat-array Interaction Combinator reducer (`FlatCombinatorVM`) and canonical Binary Combinator Packet (`BCP`, magic `0x57454654`) graph serializer (`bcp_codec.py`):

- **Port-indexed wires (version 2)**: a wire joins two *ports*. For each port the VM stores the peer node (`ports`) and the peer's port (`peer_ports`); `-1` in both marks an open port on the net's boundary. Arity: `ERA` 0, `CON`/`DUP`/`SUP` 2, `VLV`/`FRC` 1.
- **Pure Lafont basis (`ERA = 0`, `CON = 1`, `DUP = 2`)**: annihilation (`CON-CON`, `DUP(L)-DUP(L)`), commutation (`CON-DUP`, `DUP(L)-DUP(M)` for `L != M`), and erasure (`ERA-ERA`, `ERA` against a binary node). Every rule removes the pair's ports and contracts the paths through them, so wires that loop back into the pair are rewired correctly (#66). The tests do not establish confluence.
- **Weft extensions (`VLV = 3`, `FRC = 4`, `SUP = 5`)**: `VLV` gates a reduction through `weft.runtime.invariants.verify_tension_bound` and a positive budget. On pass it vanishes and its peer takes its output wire; on failure it becomes `FRC` (no rule) and a new `ERA` is wired to the peer, forming an active pair that erases it. `SUP(L)` annihilates with `SUP(L)` or `DUP(L)` and commutes otherwise.
- **Checked interface**: `interact(a, b)` accepts only an active pair, two live nodes whose principal ports are wired together. Anything else raises `ValueError` with no change to the net, trace or snapshot.
- **Execution record**: the initial graph is snapshotted at the first reduction (or by `snapshot_initial_graph()`), and the graph is then sealed: `alloc_node`, `connect_ports` and `free_node` raise, so every change is a recorded step. `trace_commitment_sha256` hashes the initial BCP graph, the step-log JSON and the final BCP graph with domain separators (`WEFT-IC-EXEC-V2:`).
- **Replay verifier**: `verify_execution_record(initial_bcp, record)` checks the initial hash, replays every step through `interact` (each must be an active pair giving the recorded op) and compares the final graph and commitment. `verify_execution(initial_bcp, steps, final_bcp, *, strict=True)` (#77) is the same check in the form the issue names: it returns the recomputed commitment and the first failing step. Allocation always takes the lowest free slot, so a graph alone fixes every later step, and replay is exact. The built-in self-test reduces a net with loop-back wires to normal form and passes this verifier.

Paper 2 studied version 1 at commit `a18fc40`. That copy is frozen in
[`papers/02-checkable-computation/studied_c3/`](../../../papers/02-checkable-computation/studied_c3/)
so the paper's numbers still reproduce.

## BCP storage contract (version 2)

Records keep the 20-byte `<IBBhiii` layout. The byte that version 1 reserved now
holds the peer ports: bits `2i..2i+1` give which port of node `p_i` the wire
reaches (`0..2`), or `3` when port `i` is open. Bits 6-7 are zero. Two different
nets can no longer share one encoding (#52).

Serialization preserves capacity exactly, including zero-capacity empty arenas,
full arenas and sparse slot IDs. Valid canonical bytes round-trip unchanged.

Both directions require ascending unique slots below capacity, tags `0..5`,
zero flags, at most 65,535 active records, and ports equal to `-1` or a slot in
`[0, capacity)`. They also check topology: ports beyond a node's arity are open,
open ports are open on both arrays, and every wire is reciprocal between two
distinct ports of live nodes. Decoding rejects any violation **before allocating
the arena**. Its default limit is 1,048,576 slots; a caller can pass an explicit
`max_capacity` suited to its own memory budget.

Version 1 packets still decode. Each peer port is inferred from the far node;
a packet is rejected where that is ambiguous (two wires between the same two
nodes) or the wiring is not well formed. The serializer writes version 2 only.

A snapshot holds the graph, not the reduction count or trace. Because allocation
takes the lowest free slot, the graph is enough to continue a run exactly.

## Reduction failure and valve contract

Before any graph, snapshot or trace mutation, an allocating rule reserves every
slot it needs: erasure two, commutation four, valve excision one. The old pair
stays live during the rule, so new nodes never take its slots. Arena exhaustion
raises `MemoryError` and preserves all VM state.

`VLV` rejects nonfinite tension or budget with `ValueError`, without a
transition. For finite values the C2 tension gate accepts `0 <= tension <= 85`,
and the budget must be strictly positive; otherwise the excision rule applies.
The trace records both exact float inputs. There is **no cost or debit** in this
API: a positive budget is a caller-supplied permission signal, not a metered
account. Choosing a cost unit, debiting it atomically and binding it to durable
ownership remains open under #43 and I3/#42.

Still open: a canonical step encoding that another language can reproduce byte
for byte (#77), and any proof about the rules. The verifier shows a record
follows the rules; it says nothing about why those steps were chosen.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/ic -p 'test_*.py'
```

- `test_ic_vm.py`: each rule, the #66 loop-back cases, crossed vs parallel
  double wires (#52), rejection of non-active pairs, sealing, and a replay
  verifier that catches altered ops, pairs, dropped steps and a swapped graph.
- `test_reference_differential.py`: the six loop-back cases and 300 random
  closed nets (self-loops and double wires included) reduced step for step
  against Paper 2's independent reference semantics, in random order; every
  run must match after each step and replay.
- `test_state_contract.py`: independently packed version 1 and 2 fixtures,
  malformed storage and topology, resource limits, exhaustion in every
  allocating rule and nonfinite `VLV` inputs.

These are CPU tests; no GPU performance or Apple hardware claim follows.
