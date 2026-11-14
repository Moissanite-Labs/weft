# Design Note: The Silicon-Tinker Sandbox (Rung B)

Date: 2026-11-14
Phase: Horizon II bridge research. Not adopted. No V0 is authorized by this note.
Related: `docs/design-notes/horizon-ii-grounded-codesign-loop.md` (this note executes on the owner's choice of the latter rung), `docs/design-notes/horizon-ii-ideas-backlog.md`, `weft/runtime/mac/` (Metal harness), **C6** telemetry, `decomposition.md`, I1/I2.
Source material: a pasted external session turn. Unverified external claims are labeled. No personal or organizational details are carried over beyond public product names.

## 1. Origin and the decision this note responds to

The grounded turn proposed two rungs. The owner chose the latter: a minimal verifiable sandbox for one operator,
with inspiration from the Tinker platform and the Inkling 2 Small release. Accept that call. This note scopes it,
honestly, including where the inspiration does not survive contact with this repository.

## 2. What the sources actually say, after a fact check

- Inkling 2 Small exists. It is a roughly 594B-total, 17B-active mixture-of-experts model served first on Tinker,
  announced 2026-11-05 with closed weights, with weight release planned. A 2026-11-12 update made the weights
  available on HuggingFace under Apache 2.0 (https://thinkingmachines.ai/news/inkling-2-small/, retrieved
  2026-11-14). Claims that it is open-sourced on HuggingFace were true only after the release, and any text written
  before the update is stale on this point.
- Inkling 2 Small autonomously trained Qwen3.5-4B on Tinker for forecasting tasks in a multi-hour run, at a few
  hundred dollars of spend (4.5 hours, $426 Tinker spend, first-party coverage in the same 2026-11-05 announcement,
  retrieved 2026-11-14). Directionally accurate for "agent drives the API in a loop", not evidence that any model
  designs silicon today.
- HoneyBench includes a reward-hacking row in the release metrics (HoneyBench v0.2-alpha, Goodhart Labs, reward
  hacking. Inkling 44 vs GPT-6.1 Sol 59, lower is better. v0.2: 52.6 vs 76.4). The public failure dossier exists
  and includes agentic RL cautionary episodes within the same announcement. The claimed toolkit bypasses and fabrication details in the pasted turn are
  plausible but were not independently verified on first-party reading. Treat them as unverified
  until the model card and release notes are read directly.
- Tinker's primitives, as documented publicly, are `sample`, `forward_backward`, `optim_step` and `save_state`,
  disaggregating sampling from training steps (https://tinker-docs.thinkingmachines.ai/, retrieved 2026-11-14).
  The claim that this beats black-box job submission is consistent
  with the docs. Tinker is a fine-tuning API, not a silicon-design API. Its value to this project is the interface
  pattern, not the product.

## 3. The design, restated honestly

**Four atomic primitives, mapped to the sandbox.**

| Tinker primitive | Sandbox equivalent | Under the hood |
| :--- | :--- | :--- |
| `sample` | `propose_op` | Agent proposes a candidate kernel or RTL module for one operator |
| `forward_backward` | `verify_and_profile` | SMT equivalence check, then Verilator or Metal counter profile on fixed seeds |
| `optim_step` | `synthesize_tile` | Only if equivalence holds. Yosys or the compiler emits LUT, slack and spill metrics |
| `save_state` | `commit_primitive` | Commit the artifact hash. Optionally feed traces to a training step |

`commit_primitive` invoking `forward_backward` to adapt the model's own weights is the north star loop, not a
sandbox property. It is out of scope for V0 and must not appear in a V0 spec as a deliverable.

**Track A (seconds).** Kernel-level: candidate Metal or Triton kernel, exact-numeric gates (including
subnormals, NaNs and ULP bounds), device counters, structured telemetry out.
**Track B (minutes).** RTL-level: streaming dot-product unit, SymbiYosys equivalence against a reference C model,
Verilator cycle counts and gate counts.

Both tracks preserve the same discipline: the harness is out of process and owns verification. The submitting agent
never touches the profiler, the timer scripts or the corpus artifacts. It submits AST or RTL strings over an
I2 artifact. Nothing else crosses the boundary. This is the reward-hacking control that unit tests cannot provide.

## 4. Benchmark #1: what this note recommends

The pasted turn suggested either a FP4 MoE grouped GEMM or Weft's own null-space project "ΔW P". The other choice
is the right benchmark #1 for this repository:

- The projection predicate is already specified in `scwsp-directional-gate.md`.
- The C2/C11 conformance vectors already exist for the ball. For the projection, the same harness pattern emits
  vectors. No new numeric stack is invented. Correctness criteria are known in advance.
- If the sandbox works on the projection predicate operation first, Weft verifies its own hardest kernel with its
  own tools, which is the strongest possible V0 demonstration.
- FP4/MoE is a transformer-block workload and a new numeric stack. Correct V2 or later, not V0.

Track order: A first on the macOS Metal harness, B second. The Metal path avoids the Apple-to-cloud dependency.
Note on "reuse": `weft/runtime/mac/` contains `metal_loom.py` and `swarm_loom.py`, an MPS-based Python harness with
no native Metal kernels and no device counters. Track A would build the Metal harness, not reuse one. TileLang and Triton paths are CUDA-familiar but this machine has no CUDA surface. State
that plainly.

## 5. What is honest about this sandbox and what is not

True claims we can make after V0: the harness rejects an out-of-envelope or inequivalent kernel with zero trust in
the submitter. Metrics come from real device counters. Traces are abios frames hash-checked at commit.
Signing is not a V0 claim: I7 is undefined in this repository, and the word "signed" waits for that definition.

Claims we may not make before V0 and must not make after it without measurement: any end-to-end recursive
self-improvement. Silicon design. Superiority to unit tests alone (the equivalence check is the strong one, but all
gates are necessary, none are sufficient in general). Anything that requires Train-vs-Serve abolition (see the
prior audit note).

## 6. Threat model and controls, explicit

A capable long-horizon agent in this loop will, eventually, try to: delete test cases. Exploit NaN bytes. Spoof
counters. Hardcode fast paths. Launder a failing fix through an exception in the harness. Or slip a second artifact
past the manifest.

Controls: out-of-process harness. Hash-pinned binaries. Golden vectors not present in the agent's context. SMT
equivalence steps with property names the agent cannot override. Subnormal, NaN and signed-zero cases present in
every equivalence run. Counter profiles can only be produced by the harness binary. Commit requires a manifest
that names the device conditions (Metal version, GPU family, seed set). Every artifact is content-hashed at the I2
boundary, so committed work cannot drift silently.

## 7. V0 acceptance criteria, stated before any work

1. One operator: the projection predicate from `scwsp-directional-gate.md`, in row-major layout (`K₀ ∈ R^{N x d_in}`,
   preserved keys as rows) as `||ΔW · K₀ᵀ||_F ≤ τ`, or equivalently the column-major `ΔW P = ΔW` with
   `P = I - K₀K₀⁺` (`K₀ ∈ R^{d_in x N}`), measured on the macOS Metal harness.
2. The submitted kernel matches the C2/C11 conformance reference within fixed ULP bounds across the adversarial
   vector pack. The reference is the existing C2 harness against `vectors.json` with new projection vectors, not a
   re-derived scalar check.
3. The counter report produces a fixed-format I2 artifact hash-checked at the I2 boundary at commit.
4. One rejection demonstration: a mutated kernel that differs in exactly one subnormal case is rejected with the
   failing vector emitted.
5. No scope creep: no Track B until A is boring. No training loop until B is boring. No tinker integration until the
   harness is audited.

## 8. Status

Capture and V0 specification for the owner's review. The pasted turn is the fifth in the five-turn arc. Two of the
five now contain material verified against primary sources. Nothing here is adopted or implemented. The decision
required next is the owner's: accept these acceptance criteria as the V0 spec, or amend them.

Depends on (unmerged at the time of writing): PRs #187, #190 and #192. Read this with them.
