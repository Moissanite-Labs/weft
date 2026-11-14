# Design Note: A Directional Gate for Weight Updates

Date: 2026-11-14
Phase: Post-Horizon I design research, not adopted for any crate or runtime path
Related codebases: **C1** (`weft/runtime/plasm/`), **C2** (`weft/runtime/invariants/`), **C4** (`weft/runtime/ledger/`), Horizon II Stage II-B (`docs/roadmap.md` §4), Horizon III Stage III-A (`docs/roadmap.md` §5)
Source material: `Moissanite-Labs/ethos`, `docs/research/2026-11-14-scwsp-brief.md` (audit) and `docs/research/prototypes/` (reference compositor)

## 1. Origin

This note records an analysis of Subspace-Constrained Weight-Space Programming (SC-WSP) and its possible convergence
with this repository. The analysis was done against a captured prototype and its one-page brief. The prototype ran
under numpy 2.5.4. The brief is preserved in the ethos repository as a research artifact at commit `afdb3a4`
(`docs/research/2026-11-14-scwsp-brief.md`). Neither is adopted here.

Findings from the capture, restated because they govern everything below:

- The prototype's own leakage check prints `6.93e+00` and reads as a total failure. It computes `K0 @ dW`, which is
  not the invariant the construction builds. The construction projects the input side of the perturbation into the
  orthogonal complement of the preserved keys, so the guarantee is `dW @ K0.T ~ 0`. Measured on the prototype as
  captured, and re-run 2026-11-14 at ethos commit `afdb3a4`
  (`docs/research/prototypes/2026-11-14-taste-compositor-fixcheck.py`, numpy 2.5.4): `3.68e-15` for the woven
  edit, `2.7e-13` and `2.8e-13` per creator. The null-space machinery is sound.
  Its own test line is wrong.
- `K0` in the prototype is a random 32x128 matrix, not a key cache harvested from a trained model. The demo has the
  right algebraic skeleton. It is not evidence about any particular model, and it is not a reproduction of
  AlphaEdit's construction, which operates on cached keys and covariances of preserved workloads.
- "Exact Frobenius attribution" holds cleanly only when contributors are mutually orthogonal, which the cascaded
  weaving aims for. In general the attribution is a normalized score that sums to one by construction, not a
  conservation law, and not an independent audit.
- The reference brief claims verification the measurements do not support. No number or product in that brief may be
  cited until re-measured on a target checkpoint.

## 2. What exists here today, verified

- **The ball gate** (`weft/runtime/invariants/invariants.py`, `weft_invariants.h`):
  `||W_cand - W_base||_F <= R_INVARIANT` with `R_INVARIANT = 120.0`, a metabolic budget precondition
  (`budget >= cost > 0`), and an optional `locked_mask` that can reject a bit change on marked indices. Conformance
  vectors in `vectors.json`. C11 runner plus a 256-vector C-vs-Python differential stream.
- **The frozen core** (`weft/runtime/plasm/plasm.py`): rows `[0 : core_rows]` of the shared-memory layout are a
  frozen slice (`mask == 0.0` in `plasticity_mask`), and a homomorphic watermark projection is verified on every
  cycle. `plasm/README.md` states the relevant limitation directly: the distance gate alone is not a provenance
  control. It limits how much the weights move, not which directions.
- **Direction-blindness is a documented concern, not a demonstrated catch.** `docs/program/experiment-cards.md` lists
  sign-flipped or divergent updates as a falsifier for the novelty-decay experiments. The runtime audit covers
  "sign-flip distance" in the handwritten C numeric tests, i.e. the distance measurement itself. No recorded
  experiment shows the ball gate passing a sign-flipped update that a directional check would have rejected.
  The story to tell honestly is: the limitation is documented, the directional fix is unbuilt, and the measurement
  has not been run.
- **Horizon II Stage II-B** already proposes lowering the gate into synthesizable RTL on the memory bus, so a
  weight page commit violating the ball is aborted in hardware. The spec today is the ball, not a directional
  predicate.
- **Horizon III Stage III-A** attributes contribution through the `ProvenanceRegistry` (cycle-free, 12-hop DAG,
  `getCreator`, `verifyAttribution`) and meters use through the `WeftTokenTissue` 85/15 excision valve. Attribution
  is a lineage property enforced by registration, not a property derived from the update matrices.
- **CI runs the ledger simulator** (`C4/C5`). It is in-test code, not a research draft. The Solidity sources are
  not compiled in CI. That is the actual boundary to state plainly.

## 3. The convergent design

The honest reading of the SC-WSP material is that it is the directional half of a two-halves problem, and this
repository already holds the other halves. The shape:

1. **One predicate, three gates.** Ball (norm), null-space direction (capability), watermark (provenance). The
   ball bounds total movement. A projection predicate bounds the directions along preserved-knowledge keys. The
   watermark binds the update to a known producer. Each gate catches a different failure. None implies the others.
   A gate stack of the form `||W_cand - W_base||_F <= R AND ||DeltaW . K0^T||_F <= tau AND locked_mask intact`
   composes all three without weakening any of them.
2. **The C11 conformance harness extends naturally.** The projection predicate is three matrix products. It fits
   the same `vectors.json` plus differential-stream machinery already in place for the ball. New vectors, new
   sign checks, same gate philosophy. Nothing about the existing header's 7-argument entry point would change.
   A new, wider entry point would be added and versioned.
3. **Horizon II Stage II-B, specified in one line.** The memory-bus admission predicate becomes
   `||W_cand - W_base||_F <= R AND ||DeltaW . K0^T||_F <= tau AND ||DeltaW||_2 <= gamma . ||W0||_2 AND locked_mask intact`.
   The Frobenius ball stays, beside the projection predicate. This is the correct
   content for "the mathematical specification of the admission gate", and it is a spec for the bus path in the
   Terrafab line, not a claim about any other vendor's silicon.
4. **Lineage artifacts first.** The buildable shared piece across the weft ledger and the ethos catalogue track is
   a content-addressed, cycle-free lineage DAG with attribution shares recorded at import time. Horizon III already
   has the registry shape. The ethos catalogue design needs the same spine. Attribution there is a property of the
   import graph (source-attributed revisions with shares), not of any particular SVD. That piece ships in
   text/JSON and can be built and measured now.
5. **Weight packets stay parked.** Low-rank packets locked to `Null(K0)` are the Plane-2 track. They belong behind
   owner-authorized, self-hosted open-weights runtimes that enforce projection at load time, which do not exist in
   any shipped product discussed here. Nothing in this note authorizes merging packet machinery into the runtime.

## 4. What must be true before any external claim

1. The invariant orientation everywhere is `DeltaW . K0.T`, with the null-space construction stated. Shapes:
   `DeltaW` is d_out x d_in, `K0` is N x d_in with the preserved keys as rows (row-major), so the predicate is
   d_out x N. The column-major AlphaEdit equivalent is `DeltaW P = DeltaW` with `P = I - K K^+`, where `K` is
   the d_in x N key matrix. `K0 DeltaW = 0` is neither form and is not used anywhere in this series.
2. `K0` is harvested from cached activations of a stated workload on a stated checkpoint, with rank, coverage and
   evaluation methodology written down once, plainly.
3. One measured table: before/after quality on two workloads, adapter size in bytes, load time, and one curve of
   sequential-weave behavior.
4. The 16-64 KB packet-size figure is replaced with the honest number for the target network (a rank-4 pair per
   direction across all layers is on the order of megabytes, not tens of kilobytes).
5. "Exact attribution" is printed only with its orthogonality condition attached, or replaced by the
   normalized-score definition.

## 5. Open questions

1. What is the calibration workload set for `K0` on this project's in-progress trained cells, and who owns it?
2. Does the admission predicate in Stage II-B supersede the ball, or sit beside it? (Proposed: beside it.)
3. Where does the attribution-share computation live in the text-space lineage artifact, and what fraction precision
   is committed in the ledger?
4. What is the migration path for `test_invariants_c.c` once a wide entry point exists, before any hardware stage?

## 6. Status

Design research. No code in this repository is changed by this note. The directional predicate is not adopted, measured, or shipped. The roadmap's Horizon II predicate remains the ball. When the calibration workload and at
least item 2 of Section 4 exist, this note should be revisited and either promoted to an interface document
(`docs/interfaces/`) or retired with its findings merged into the gate design.
