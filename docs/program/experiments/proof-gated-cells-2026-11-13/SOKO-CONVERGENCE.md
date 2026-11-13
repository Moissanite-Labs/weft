# Convergence with Soko's verified-systems loop

Reviewed by gpt-forge (Astra), 2026-11-13, against Soko commit `c3afb8d4b17b1b6ebcceaa05704320d555e2c013`. This review inspected source, not a new Soko benchmark run. The useful convergence is a shared evidence protocol: proposals remain untrusted. a named checker evaluates an exact claim. the result carries enough identity and evidence to replay.

## Concrete correspondences

| Soko primitive | Weft proof-gated-cell counterpart | Boundary |
|---|---|---|
| Exact immutable states, explicit actions, transition and invariant functions | Bounded JSON integers interpreted as Lean `Int`, immutable anchors, exact delta transition | Exact arithmetic is not a model of arbitrary floating-point neural execution. |
| Locked checker source hashes and trace replay | Pinned Lean specification/template/toolchain. request and certificate hashes | Hashes establish identity, not correctness. |
| First invariant failure and reason | Frozen, anchor, norm and stale-parent rejection witnesses | Useful feedback must describe the registered gate, not silently weaken it. |
| Dual-checker transcript parity | Independent host arithmetic predicate plus the exact Lean proposition | Agreement catches implementation errors. common specification errors remain possible. |
| Required negative controls | Mutation tests for malformed inputs, stale proofs and violated invariants | A finite attack suite is evidence, not an exhaustive security proof. |
| Goal/cost/termination semantics included in problem identity | Immutable anchor/frozen/bound configuration and parent identity | Changing the configuration creates a new claim. |
| Explicit proof scopes and evidence ledger | Separate kernel-checked transition, committed transition, and rejected proposal events | All rejected attempts should be recorded. proof success alone is not commit success. |

Soko's [`verify_formal_trace`](https://github.com/ahrazzle/soko/blob/c3afb8d4b17b1b6ebcceaa05704320d555e2c013/soko_mcp/formal_kernel.py#L736) replays both checkers and compares transcript hashes, legality, invariants, goals and cost. It returns the failure step and reason, together with checker pins.

Its canonical puzzle identity includes goal, cost and termination semantics, and its validator excludes empty or otherwise vacuous puzzle instances ([evidence.py](https://github.com/ahrazzle/soko/blob/c3afb8d4b17b1b6ebcceaa05704320d555e2c013/soko_mcp/evidence.py)). These are directly useful design patterns for a cell adapter.

## Limits that should carry over honestly

Soko's AST checker and restricted Python execution are not Lean kernel verification.

Rejecting identical alpha-normalized syntax prevents a trivial copied checker, but does not establish algorithmic independence or rule out shared bugs ([registration](https://github.com/ahrazzle/soko/blob/c3afb8d4b17b1b6ebcceaa05704320d555e2c013/soko_mcp/formal_kernel.py#L451)).

At least one negative control establishes only that the tested control fails. bounded differential exploration does not establish universal equivalence. Likewise, an AST whitelist is not a general operating-system sandbox or termination proof. Weft can avoid that execution boundary by accepting only data, not model-authored checker code.

The ledger's extra-claim path requires a nonempty witness/proof hash for `PROVEN` or `VERIFIED`, but that requirement does not itself validate the referenced artifact ([export](https://github.com/ahrazzle/soko/blob/c3afb8d4b17b1b6ebcceaa05704320d555e2c013/soko_mcp/formal_kernel.py#L2014)). Trace verification appends successful certificates.

a complete attempt audit also needs rejection records. Weft should derive its status from actual checker and commit outcomes rather than accept a caller-supplied epistemic label.

Soko's own [verified-systems-loop document](https://github.com/ahrazzle/soko/blob/c3afb8d4b17b1b6ebcceaa05704320d555e2c013/docs/verified-systems-loop.md) explicitly distinguishes replayed witnesses, finite exhaustive certificates and kernel theorems. it says the project does not yet meet its stronger Verified Bar.

It also states that two implementations may share a mistaken interpretation and that a formal state system does not establish arbitrary real-world claims. That is the right scope discipline for this prototype.

## Immediate composed test

Register one fixed integer readout and show a nonzero permitted edit, then independently mutate each obligation: anchor output, frozen coordinate, norm, parent hash, certificate binding and checker output. For each attempt preserve the canonical request, decision, reason, proof artifact when available, and before/after checkpoint IDs.

Race two proposals against the same parent and require at most one commit. Replay the resulting log with a separately written exact-arithmetic predicate. This tests the useful intersection of Soko's evidence loop and Lean-backed cell transitions without a paid model call or a claim of general mathematical causality.
