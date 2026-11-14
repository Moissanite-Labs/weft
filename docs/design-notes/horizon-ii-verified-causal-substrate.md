# Design Note: A Formally Verified Causal Substrate (Horizon II Endgame)

Date: 2026-11-14
Phase: Horizon II (II-B / II-C) design research. Not adopted. Nothing here changes the roadmap or the gate.
Related: `docs/design-notes/scwsp-directional-gate.md` and `docs/design-notes/horizon-ii-dual-plane-silicon.md`. **C2** (`invariants`), **C3** (IC VM), **C6** (telemetry frames), I3. Milestone I.3 (`docs/roadmap.md` §3), verification linkage in `docs/program/decomposition.md` line 106. E07 experiment record ("proof-carrying wins", R1). `docs/program/convergence-plan.md` (hardware simulation as a bounded research branch).
Source material: a pasted external research collaboration turn, audited. The source contains no names. Review for personal material found nothing to remove.

## 1. Origin and recurrence

Third turn in the hardware pitch sequence. The recurring defect appeared again: the source prints `K0 ΔW = 0`. The
null-space construction builds `ΔW · K0ᵀ = 0`. This note fixes the symbol everywhere it is needed and does not
re-litigate it further.

## 2. The pitch, as received, three claims

**Claim 1. Proof-carrying transitions.** Every local plasticity rule is synthesized from a machine-checked
specification (Lean 4 or Coq, then RTL). Plasticity is local and continuous, closer to predictive coding or
equilibrium propagation than to backpropagation. The gate enforces the invariant as a hardware state-machine
invariant, so no causal input sequence, even adversarial, pushes a cell outside its proven envelope.

**Claim 2. The end of the train vs serve split.** Training is frozen, offline, unverified. Serving is frozen,
brittle, stateless. A verified substrate makes every deployment an end-to-end verified dynamical system that
adapts in real time to prediction error.

**Claim 3. Compositional mesh verification.** Cell A provably emits packets within Subspace `SA`. Cell B's
hardware gate provably admits only `SA`-bounded perturbations. The mesh remains verified by induction, no matter
how cells divide, merge or exchange taste and skill packets at runtime.

## 3. What is real and reusable

1. **Proof-carrying code is a known, usable pattern.** The receiver checks a certificate. It does not trust the
   sender. The E07 experiment record lists proof-carrying selection as a proposed experiment that has not been run
   (R1: a win is kept only with a certificate. The hard tier is a Lean proof that the new function equals the spec
   function). The
   direct descendant here is a proof-carrying admission: a packet carries a certificate that its payload satisfies
   the admission predicates, and the gate verifies the certificate instead of recomputing the check. This is
   implementable with today's artifacts: `vectors.json`, a digest, and an added certificate path in the same C11
   style runner. It is a design hypothesis, not a shipped feature.
2. **Machine-checked specs to RTL is an existing milestone.** I.3 is Lean 4 mechanization of the C2 Frobenius and
   budget predicates against `vectors.json`, and decomposition line 106 extends to IC confluence. Verified
   hardware compilers exist in the literature (Kami class). The honest version of this claim is: after I.3, the
   same proof obligations can be discharged against a synthesized gate, so the II-B admission path is verified
   once, not audited forever.
3. **Local plasticity research exists and is not at LLM competence.** Equilibrium propagation, local losses,
   predictive coding and neuromorphic silicon are real directions. None of them certifies that online weights at
   transformer scale stay safe. They are suitable for the toy cells already in this roadmap.
4. **The compositional claim is the one theorem-shaped part.** Orthogonal projectors commute if and only if their
   ranges are orthogonal or nested. In general they do not commute. The null-space projection is itself an
   orthogonal projector, and the mesh construction arranges cells onto mutually orthogonal or nested subspaces,
   which is the hypothesis that makes the commutations hold. Given that hypothesis, a cell that (a) emits
   bounded-norm packets in `SA` and (b) admits only
   perturbations whose annihilator test passes is composable by assume/guarantee. Each cell's proof obligation is
   local. The global guarantee follows by induction over the mesh. This is real mathematics. It is also incomplete.
   See Section 4, item 4.

## 4. What is false or unearned

1. **"No causal input sequence can push a cell outside its envelope."** The envelope covers the complement of the
   protected span and a spectral bound. It does not cover task quality inside the allowed region, and it does not
   cover the unmeasured parts of the model. Worst-case inputs inside the envelope remain possible, and they are
   not made safe by arithmetic.
2. **"End-to-end formally verified dynamical system."** Not claimable. Verification scope is the admission path
   and the predicates, exactly the gate. Learning dynamics, prediction error, packet semantics and drift are all
   outside any proof we can write today. Honest name: verified admission control on adaptations.
3. **"The end of train vs serve."** Not real, and the reason serving stays separate is economic and forensic, not
   only safety. Frozen artifacts are what make audit, conformance vectors and rollback possible. Online adaptation
   relabels training as deployment. The substrate can add bounded runtime repair. It does not abolish the split.
   The
   claim that a frozen pretrained model then spends another enormous budget on guardrails is a rhetorical picture,
   not a fact, and it should not appear in any external text.
4. **"No matter how many cells divide, merge or exchange packets."** The induction carries hypotheses: every cell
   enforces the gate at every entry point, queues are bounded, analog drift is absent or separately bounded, and
   configuration changes are admitted by the same predicate. Semantic safety is out of scope entirely. A packet can
   be spectrally clean and malicious. Induction lifts the boundedness, not the meaning.
5. **"The model repairs itself innately."** No mechanism is given. Prediction error does not self-repair a network.
   It perturbs it. Whether the perturbation repairs or degrades is an empirical question with no current answer.

## 5. The honest synthesis

The word magnum opus belongs to the collaborators who want the name. What survives audit:

- A substrate in which every admitted state transition would sit within an envelope: verified gates, verified
  admission, verified bytes. Not verified learning. Not verified judgment. This is a target, not a present fact.
  Today nothing here is proven. The envelope claim holds only after I.3 lands and II-B v2 passes its vectors.
- II-B v2 with the projection predicate is the near-term artifact. I.3 is the proof work. Proof-carrying
  admission is a bounded experiment on top.
- Compositional mesh safety is a design constraint for the Horizon III cell-mesh research branch. Published as a
  constraint with hypotheses, not as a guarantee.
- Plasticity stays in the toy until a trained cell exists that can eat it.
- "Train vs serve" stays separate, with the substrate adding envelope-bounded repair, not abolition.

## 6. Staged path and retire criteria

Step 1. Close I.3. Lean proofs of ball and budget against `vectors.json`. Add the projection predicate only after
II-B v2 has vectors of its own. Retirement criterion: the Lean model fails to cover the predicates as stated
(the C11 implementation is validated by the differential stream, not by Lean), or the vectors drift from what the
Lean model states.
Step 2. II-B v2 gate in Verilog. Simulate the stacked predicate against existing and new vectors. Add
proof-carrying admission behind the same harness. Retire the certificate path if it adds more than two times gate
latency without a measured security or robustness gain.
Step 3. Toy mesh: two digital cells, orthogonal subspaces, 64-byte frames, packet passing, measured
non-interference against the vectors. Publish the vectors in `docs/program/experiments/` so the result is checkable.
Step 4. Only after steps 1 to 3 does any silicon claim get made, and only as measurement, never as aspiration.
Analog remains a comparison point for energy per write and cannot carry the conformance posture.

## 7. Status

Research capture and audit. No code, no RTL, no issues filed, no gates touched. No new codebase is named. The
directional gate (#187) and dual-plane silicon (#188) notes are the anchors, both unmerged at the time of writing.
This note is the third panel of the
same arc. The personal and situational context of the source is omitted here as everywhere in this track.

Depends on (unmerged): PR #187, PR #188. Merge after both, or read this only as a continuation of them.
