# Supplied Living Loom: bounded offline audit

The supplied Node suite passes: **16 tests passed, none failed**, on Node **v22.17.1**. The complete
suite took approximately 0.47 seconds in a disposable scratch copy. Independent small-matrix probes
also passed their assertions. These results support the tested mechanisms, with the boundaries
below. They do not establish general zero forgetting, a formal confluence theorem, browser execution
or WebGPU performance.

The package scripts, test files and imported JavaScript were inspected before execution. Tests
import local modules and Node builtins. One reads the local invariant corpus. The audit invoked Node
directly, installed nothing, ran no npm lifecycle commands, and used no browser, paid API or network
command. README instructions to copy modules into production were treated as supplied data and were
not followed. Inputs remain unchanged. `data/loom-audit/audit.json` records supplied-file hashes,
exact command arguments, Node version, exit codes, timings and newly created files. Both runs
created no files in their scratch workspaces.

Reproduce from this experiment directory, using the archived `.txt` input files restored only inside temporary scratch:

```sh
python3 data/loom-audit/reproduce.py
```

Raw suite and probe stdout/stderr, the probe source and structured numeric results are in `data/loom-audit/`.

1. **Protected subspaces are narrower than zero forgetting.** `aywa-continuum-plasm.js:118–140`
applies left/right complement projections. With orthonormal protected columns `e1`, the input matrix
`[1,2;3,4]` produces delta `[0,0;0,4]`. The protected input `e1` has zero output change, while input
`e2` changes by `[0,4]`. This is the intended finite linear-subspace distinction, not a failure of
orthogonal projection. The README's “0% locked-subspace forgetting” wording must retain that
qualifier. The continuum unit test at lines 45–48 checks a scalar orthogonal inner product and
ancestral retention **greater than 98%**, rather than exact equality on every prior input.
`ancestralRetention` at continuum lines 309–319 compares target-mode captures with target singular
values. It is not a complete previous-checkpoint behavior audit. See `probes.json:
protected_subspace`.

2. **The public projector requires orthonormal columns.** `projectOrthogonalComplement` sequentially
subtracts rank-one projections without checking or constructing orthonormality. Two unit vectors
`e1` and `(e1+e2)/sqrt(2)` leave a residual protected-left projection norm of **2.5** after
projection. Explicit `gramSchmidtColumns` on the same columns reduces the resulting full-span
residual to zero. Internal normal construction does call Gram–Schmidt, so this probe identifies an
API precondition rather than showing that all internal calls fail. Validate that precondition or
orthonormalize at the projector boundary before accepting external basis data. See `probes.json:
nonorthogonal_basis`.

3. **The safety gate certifies binary32 proxies, while the colony keeps binary64 state.**
`aywa-invariant-v2.js:47–59` rounds both operands to binary32 before checking distance and locked
bits. Binary64 values `4294967296` and `4294967424` differ by **128**, exceeding radius **120**, yet
both round to the same binary32 value: the gate accepts and reports distance zero, even with the
coordinate locked. This result is correct for the quantized representation and insufficient for an
unrounded binary64 commit. The colony constructs `candF32` at continuum lines 408–420, then retains
unrounded `chosenB` and `chosenA` at lines 423–424. Bind verification to the exact committed
representation, or state and bound the quantization discrepancy explicitly. The deliberately large
numbers exercise a numeric boundary. This audit does not claim that the seeded demo reaches them.
See `probes.json: float64_vs_float32`.

4. **The supplied browser controller automatically grants the nominal manual consent.** It creates a
colony with `exoManualGate: true`, but `aywa-living-loom.js:186–188` immediately calls
`approvePendingConsent()` when an epoch boundary returns `AWAITING_EXO_CONSENT`. The module-level
unit test demonstrates a pending/approve state machine. The controller wiring does not establish a
human approval requirement. This is a static source finding: no browser was executed. Keep automatic
demonstration mode distinct from an actual user-controlled approval path.

For the next graft experiment, use the useful mechanism with a smaller exact claim: a fixed
six-feature, two-output integer readout. Immutable protected anchors. Explicit before/after output
equality. A nonzero graft in the remaining capacity. And a known signed-permutation sibling. Check
raw-coordinate and correctly mapped transfers separately. Record failure when the protected span
exhausts the feature space. This can test checkable grafting without inheriting the supplied demo's
broader forgetting, consent or numerical-safety claims. It does not by itself establish a
large-model capability or general transfer result.
