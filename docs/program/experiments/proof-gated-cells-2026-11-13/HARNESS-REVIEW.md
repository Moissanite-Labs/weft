# Independent review of the supplied Lean harness

Reviewed by gpt-forge (Astra), 2026-11-13. This is a static review of the supplied `lean4_astra_proof_harness.py`, SHA-256 `9c4f93b74edae9f906b8ea03acce4a3042ddbd037f4209951a3de423633a0571`. The attachment was not executed and no model calls were made. Line references below refer to that original attachment, preserved under `inputs/`.

The harness is a useful orchestration proposal, but its successful-build flag is not a certificate that the requested invariants were proved. It should not be used as the gate for state changes in its present form.

## Blocking findings

1. **Successful compilation is not bound to the requested proposition.** The model supplies an entire module (lines 1116–1144). acceptance tests `check_res.ok` (1153–1160), without requiring particular theorem names, types, or coverage. A module importing definitions and proving nothing can compile.

   The optional comparator defaults off (899–900, 1864) and is disabled for the supplied Weft and SemVer tasks (1699, 1792). The immutable specification itself contains theorem placeholders using `sorry` (522–580). A compiler exit status cannot distinguish a genuine proof of the requested theorem from a smaller, unrelated module.
2. **Proof dependencies are not audited.** The candidate-text filter does not inspect transitive imported axioms or `sorryAx`. Textual checks in one compiler path (871) do not establish an empty axiom set. `lake build` uses its return code (890). A proof can depend on an admitted imported theorem even if the candidate text contains no forbidden token.

   Pinning selected source files is useful provenance, but does not establish the correctness of their declarations or complete dependency closure (407–422).
3. **Untrusted Lean source is executable input.** The token blacklist (341–389) does not ban `#eval`. Lean elaboration and commands are not an execution sandbox. The subprocess inherits the process environment (852, 866). The safe boundary for this prototype is to accept data only and generate a fixed trusted module, not to attempt to enumerate dangerous Lean syntax.
4. **Multiple tool calls can break the accepted-file binding.** A successful candidate sets `verified=True` (1154). A later candidate in the same tool-call loop (1101) overwrites the target (1143). a failed later compile does not reset the prior success.

   Restoration is conditioned on `not verified` (1194), while the final file hash is computed afterward (1202). The final advertised artifact can therefore differ from the successfully checked artifact.
5. **The status labels overstate the actual checks.** The self-test substitutes a mock compiler that only recognizes a sentinel error string (1607–1627). The overall certificate is assigned `PROVEN + VERIFIED` for a live run (1836), rather than being derived from completion and proof results. A mock verifies orchestration behavior, not Lean validity.

## The statement matters as much as the proof

`lockedSlice_sound` (561–564) asserts matching lengths, not preservation of locked coordinate values. The float-budget definitions (480–500) assume a decreasing ordinal. they do not prove that an actual IEEE operation or host implementation refines that model.

Arithmetic facts about an arena partition (511–517, 567–579) do not prove runtime allocation or memory safety. A valid theorem about these statements would retain those limits.

## Smallest useful replacement

Use a fixed three-dimensional integer readout with immutable anchor features and frozen-coordinate indices. The model submits only a bounded integer delta and the expected parent checkpoint hash. Trusted code generates the exact before/delta/after literals and the proposition: after equals before plus delta. every frozen delta is zero.

every registered anchor output is unchanged. squared delta norm is within the registered per-step bound. Compile the mandatory concrete theorem with a pinned Lean toolchain and require its actual axiom report to be empty. Bind the certificate to the full request, specification and template hashes.

commit only after a locked compare-and-swap against the same parent checkpoint.

The new `Core.lean`/`verifier.py` implementation follows this approach. Static inspection confirms the concrete certificate includes the actual after-state equation, `Allowed`, and `Guarantees`. the host rejects out-of-range frozen indices and non-integer JSON values.

The generic algebra lemma may use standard logical axioms, while the concrete certificate is separately required to report no axioms. An independent adapter audit and adversarial tests remain necessary. this paragraph is not a proof of the Python implementation.

Required attack cases include a stale parent or certificate, changed anchors/specification, omitted theorem, nonempty axiom report, empty compiler output, timeout, boolean/float coordinates, invalid dimensions/indices, bound violation, frozen-coordinate violation, and two concurrent commits from one parent.

A valid nonzero edit is a necessary positive control. Preserve rejection records as well as accepted transitions.

The guarantee is exact preservation on the registered fixed-feature anchors, not all possible future inputs. The norm bound is per transition, not cumulative distance. Lean checks the mathematical statement. the Python adapter, toolchain/runtime, filesystem and hardware remain trusted implementation boundaries. Nothing here establishes physical-world causality or general safety of arbitrary cell actions.

## Independent prototype check

The reviewer reran `python3 -m unittest test_verifier -v`: all six tests passed, including real Lean acceptance of nonzero and zero edits, real Lean proofs of mathematical rejection, strict input validation, empty compiler-output rejection and timeout rejection. This is a test result, not an additional formal theorem about the verifier.

Static review of `cell_mcp.py` found no mathematical-state bypass available through its data-only tool interface. It holds the interprocess lock across state loading, expected-parent comparison, verification and journal replacement.

The host independently compares before/after anchor observations and frozen coordinates, and checks the proof's exact request, resulting state, specification hash and template hash. The bounded after-state check prevents leaving the supported host representation. Caller-owned configuration is copied.

the MCP tools expose no rule mutation, arbitrary proof source or file path.

Crash and logging boundaries require precise wording: a crash before journal replacement may leave an incomplete attempt directory rather than a committed rejection. oversized transport input must be separately recorded if claiming every transport attempt is logged.

and a durable journal needs durable proof artifacts to guarantee availability after power loss. Hash chains detect mismatches against retained data but do not authenticate the history against a malicious filesystem owner. The parent was informed of these points for implementation or explicit scope treatment.
