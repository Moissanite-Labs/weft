# Independent review: exact proof-gated cell prototype

Reviewed by gpt-forge (Astra), 2026-11-13. Scope: `Core.lean`, `verifier.py`, `cell_mcp.py`, their tests, the pinned Soko bridge, and two offline controls against the supplied harness. No paid API calls, provider credentials, external effects or modifications to the supplied harness were used.

**Verdict:** the data-only prototype is suitable as a small demonstration of Lean-checked integer transitions with a trusted Python commit adapter. No mathematical-state bypass was found in the exposed cell tools. This is not a proof of the Python adapter, operating system, compiler installation or physical-world causality.

## Evidence independently checked

- All six verifier tests passed. These include actual Lean acceptance of a nonzero edit and a zero edit, actual Lean-checked rejection of violated constraints, strict input validation, empty compiler-output rejection and timeout rejection.
- All nine cell adapter tests passed. These cover real proof/commit/restart, stale parent rejection, rule and certificate changes, schema and representation limits, verifier failure, two writers sharing one parent, incomplete-attempt visibility and stdio behavior.
- The Soko bridge uses the pinned checkout `c3afb8d4b17b1b6ebcceaa05704320d555e2c013` through its actual tool dispatcher. The checkers have different state representations and arithmetic implementations, a fixed finite action alphabet, one positive goal trace, six negative goal traces and a planted missing-norm-check mutation.

  A zero edit is legal but fails this bridge's nonzero target goal. it must not be described as an invalid mathematical transition. The frozen coordinate is also covered by an anchor, so this fixture does not independently isolate the two restrictions.

The concrete Lean certificate contains the exact after-state equality, the registered `Allowed` predicate and the preservation guarantees. Its checked axiom set must be empty. A generic supporting algebra theorem uses standard logical axioms. it is separately identified and does not change the empty-axiom requirement for the concrete certificate.

Integer literals are constructed by trusted code from strict bounded integer data. the client cannot supply Lean source, imports, paths or proof text.

The adapter locks across load, parent-ID comparison, verification and atomic journal replacement. It checks the proof's exact request and after state, specification and template hashes, and an independent Python before/after observation predicate. The expected-parent ID includes the world identity and revision. Rules are immutable through the tools.

Rejections preserve weights. a successful no-op is still a committed revision. Restart replays the history and verifies retained proof artifact hashes. State and delta representation bounds are host policy in addition to the mathematical gate.

## Persistence findings and resolution

The earlier review identified three gaps in the scope of a claim that every attempt and its evidence survive: oversized transport input was not logged, an interrupted attempt was absent from event inspection, and proof artifacts were not synchronized before the durable journal.

Inspection of the revised adapter confirms bounded oversized-input logging, explicit `incomplete_attempts`, and synchronization of attempt artifacts and directories before journal commit. These changes improve crash behavior. the tests and static inspection do not simulate every power-loss or filesystem failure.

Incomplete attempts are not mislabeled as completed rejections.

The journal hash chain detects accidental or partial modification relative to retained evidence. It is not an authenticated log against a host owner who can replace the code and history together. The Lean executable and imported standard library remain part of the trusted installation. source/version pins are not independent binary attestation.

Retained compiler output is evidence from that trusted runtime, not a cryptographic proof that the physical execution occurred.

## Direct controls against the supplied harness

The reproducible script and raw compiler outputs are in `data/harness_controls/`. The review imported the statically inspected harness without invoking its main routine or any API client, with a credential-free compiler environment.

Its actual `run_real_lake_check` returned `ok=true`, `stage=verified`, and exit code zero for a temporary minimal Lake package whose complete target module was only `import Std`. There was no requested theorem declaration. This experimentally confirms that its compilation-success predicate does not require proof coverage.

Separately, the supplied token scanner returned no violations for the harmless source text `import Std` followed by `#eval IO.println "harmless review marker"`. That text was scanned only, never executed. This confirms the scanner does not exclude IO commands. it is not an execution sandbox. The replacement accepts no model-authored source, so it avoids that surface rather than relying on the token scanner.

## Exact claim boundary

The demonstrated guarantee is preservation of the registered fixed-feature anchor outputs and frozen coordinates under each accepted integer edit, with a per-transition squared delta bound. Finite anchors do not establish preservation on unseen features, and a per-step bound does not bound cumulative motion.

The Soko component is runtime dual-checker replay and bounded mutation testing, not an additional Lean theorem or general checker-independence proof. The MCP transport exposes a deliberately pinned subset, not a claim of complete protocol implementation.

These limits leave a useful executable prototype: a model can propose a nonzero change, receive a specific rejection or checked acceptance, and inspect the state and evidence that actually committed.
