# Local proof-gated cell protocol

This record describes a mechanism prototype developed after the earlier teacher-study outcomes were visible. It is not a preregistered confirmatory teacher experiment. No language model is asked to solve the task, and no API calls are part of this run.

## Fixed mathematical world

The state is a three-coordinate integer vector, initially `[3, 1, 5]`. The immutable readout anchors are `[[1, 1, 0], [0, 0, 1]]`. Frozen indices are `[2]`. The allowed per-transition squared delta norm is 8. The host bounds integer coordinates and messages before verification. Host limits and world identity belong to the captured specification.

A proposal contains only an expected parent state identifier and a three-integer delta. An accepted transition must satisfy all of these conditions:

1. The supplied parent identifies the current state in the same immutable world.
2. The after-state is exactly the before-state plus delta.
3. Every frozen coordinate has zero delta.
4. The squared delta norm is within the registered per-step bound.
5. Every registered anchor has exactly the same dot-product output before and after.
6. The certificate binds the actual request, trusted specification and generation template, and the pinned compiler checks the required concrete theorem with no axioms.
7. The locked commit still refers to that parent, and state plus event history commit together.

The Lean theorem establishes the mathematical parts of this conjunction. The host enforces request identity, locking, storage and protocol handling. The full conjunction is not claimed as a proof of the Python runtime.

## Exposed interface

The stdio JSON-RPC server fixes protocol version `2025-11-25` and exposes `cell_inspect`, `cell_propose` and `cell_events`. Only `cell_propose` may change the weights. Read operations do not require a transition proof. Notifications cannot invoke a state-changing tool.

The received bounded raw prefix and returned response are durably recorded in the transport log. Oversized lines trigger a refusal and stop the server before parsing, without a state change. Their stored raw prefix is bounded rather than an unlimited copy of the input stream.

The candidate supplies data, not proof code. The trusted verifier creates a concrete accepted or rejected statement and records compiler version output, specification compilation, theorem compilation, stdout, stderr and exit statuses. Compiler success without the expected theorem/axiom report is insufficient.

## Demonstration and adversarial checks

Include the nonzero preserving edit `[1, -1, 0]` as a positive control. Keep anchor-violating, frozen-violating and norm-violating proposals as negative controls.

Exercise malformed and non-integer input, stale parents, changed certificate bindings, empty or misleading compiler output, timeouts, restart integrity and concurrent proposals from one parent. A finite passing suite establishes coverage of those cases, without proving arbitrary malicious-host resistance.

Use a fresh local run directory and preserve every attempted proposal and decision. Record the initial state, accepted/rejected outcomes and final state. Test logs must identify whether a real pinned Lean compiler or a mocked compiler path was used. Soko integration, if exercised, must retain its pinned source identity, adapter request and actual result separately from the Lean result.

## Raw evidence and limits

Archive fixed fixtures, transition requests, generated Lean source, compiler stdout/stderr, exit statuses, proof identities, specification/toolchain/template hashes, state checkpoints and event chains. Keep malformed input, stale-parent refusals and failed proof attempts.

Record absent proof artifacts explicitly when rejection occurs before compilation. Hash the final raw artifact set in a portable manifest after capture.

There are no model prompts, paid responses or API usage in this local demonstration. Credentials and internal model reasoning are excluded. The supplied external harness remains quarantined data, with a separate static review. This prototype does not repair SemVer or replace a broad API proof-synthesis service.

Exact preservation applies to this fixed-feature integer world. It does not certify arbitrary neural floating-point behavior, cumulative edit distance, external effects, physical observations or the adequacy of the task specification. Any extension must state its new action semantics, assumptions and proof obligations before claiming that those actions are verified.
