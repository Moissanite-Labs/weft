# Design Note: Dual-Plane Silicon and Compute-in-Memory (Horizon II Extension)

Date: 2026-11-14
Phase: Horizon II (Custom Silicon & Terrafab Foundry) design research. Not adopted. Nothing here changes the roadmap.
Related: `docs/roadmap.md` §4, `docs/design-notes/scwsp-directional-gate.md`, **C2** (`weft_invariants.h`), **C6** (64-byte telemetry frame), I3 (invariant gate)
Source material: a pasted external research collaboration turn, audited and sanitized. Names and situational details from the source are omitted.

## 1. Origin and framing

An external session turn proposed extending Horizon II past the classic bus bottleneck. The pitch in one line: treat
weights not as passive data shuttled to a systolic grid, but as part of the silicon itself. The correct reading is a
horizon extension, not a new product: Horizon II Stage II-A (unikernel) exists as corpus text only. No II-A code
exists in this repository. Stage II-B
(memory-bus admission predicate in RTL) is spec'd on paper only. Stage II-C (wafer-scale/photonic fabric) is
research aspiration. This note captures the ideas, keeps the good ones, and marks what the silicon physics will
not let us ship yet.

One recurring defect in the source text carried over: it prints `K0 ΔW = 0` throughout. That is the wrong matrix
product. The null-space construction builds `ΔW · K0ᵀ = 0` (the perturbation annihilates the preserved key
directions). Every predicate named below uses the correct orientation.

## 2. The pitch, as received, three shifts

**Shift 1. Dual-plane silicon: frozen static warp plus reconfigurable weft fabric.**
A dense, static SRAM/NVM crossbar plane holding the base weights (activations pass through cells via `I = V·G`),
with zero weight movement and zero HBM traffic, adjacent to every tile a small reconfigurable fabric
(CGRA-class, not bit-level FPGA) that takes compact low-rank packets and reconfigures the datapath for the
current token stream. Metaphor: the warp never loosens, the weft always weaves.

**Shift 2. Subspace Memory Management Unit (S-MMU) inside the memory controller.**
Generalizes Stage II-B. The controller holds the canonical orthogonal basis `K0` in on-chip storage and streams the
projection check `ΔW · K0ᵀ = 0` at wire speed on every weight write burst. Out-of-subspace writes are refused
before bytes land. Claimed consequence: true continual test-time weight adaptation because the silicon itself
refuses catastrophic changes to preserved capability.

**Shift 3. Asynchronous spatial dataflow cells over a NoC.**
Drops the lockstep grid entirely. Each cell claims a region of unified SRAM mesh and fires 64-byte packets across
an on-chip router. No host orchestration, no kernel launches, no batching tax. Inspired by dataflow chips such as
Cerebras, SambaNova and Groq.

## 3. What checks out

- CIM is a real research area, not science fiction. Analog crossbars computing via Ohm's and Kirchhoff's laws are
  published and demonstrated in research prototypes (Ielmini and Wong, Nature Electronics 1, 333-343, 2018, and Ambrogio et al., Nature 558, 60-67, 2018). Digital SRAM-based in-memory multiply exists with better precision.
- Apple Silicon really does unify CPU/GPU/accelerator address space. System memory and device translation are
  enforced at page granularity by the MMU/IOMMU. Saying that
  a protection model which knows addresses but not linear algebra is blind to directed weight attacks is accurate.
- Reconfigurable spatial fabrics (CGRAs) are real and faster to configure than FPGAs. They fit low-rank attention
  well because the configuration space is small and structured.
- Dataflow-style chips for deterministic low-latency inference exist in products (Cerebras wafer-scale engine, SambaNova SN40L Reconfigurable Dataflow Unit, arXiv 2405.07518, and Groq LPU). Nothing
  morphological prevents a cell-mesh sketch. The cost model is the hard part.
- 64-byte frames align with `C6`. A packet-driven on-die protocol would reuse machinery, not invent it.
- Stage II-B genuinely needs its predicate sharpened, and the projection predicate from
  `scwsp-directional-gate.md` is the right candidate. The S-MMU is not a new concept. It is II-B generalized from
  Frobenius distance to an algebraic predicate, which the project already identified as the missing half.

## 4. What does not check out

1. **Analog crossbars cannot carry our verification posture.** Weft's guarantees are bit-exact: Python reference,
   C11 header, `vectors.json`, differential streams. Analog arrays drift, vary part-to-part, carry limited effective
   precision (often roughly 6 to 8 bits device-permitting) and have limited endurance (order 10^6 to 10^9 program
   cycles, device-dependent), and burn large energy per program pulse (Ielmini and Wong 2018, and Ambrogio et al.
   2018). Continuous adapter "weaving"
   on an analog warp is not a credible near-term mechanism. Digital logic is the deterministic carrier.
2. **"Safely rewrite weights on every token" is incoherent.** A projection predicate rejects out-of-subspace
   writes. It cannot certify that an in-subspace rewrite is useful, cannot bound harm inside the complement of
   `K0`, and cannot promise no forgetting of unmeasured capabilities. Continual test-time learning is an open
   research problem. No predicate available, or imaginable this decade, closes it.
3. **"K0 in dedicated registers" does not fit in flip-flops.** A rank-64 basis for a 4096-dim model is a
   megabyte-class object. That means on-chip SRAM, with the same access discipline as the weights, not registers.
   The projection check itself is `d²·r` MACs per candidate write. Fine for an admission gate on committed bursts.
   Not fine for per-token evaluation at token rate. Any tape-out premise on this math is fantasy today.
4. **Packets cannot "re-route datapaths" at nanoseconds.** A CGRA runs configurations. abios-class packets can
   select a pre-placed configuration by table lookup. That is real. Arbitrary parse-then-route at wire speed is not
   what CGRAs do and should not be written into a spec.
5. **No existing memory controller admits linear-algebraic writes.** The S-MMU is new IP, described nowhere on any
   datasheet. It belongs in Verilog and simulation before it belongs in prose, and it must state which predicate
   it enforces (ball, projection, or stacked) explicitly.
6. **CI will not protect you here.** The C11 conformance harness is the right reference for the digital side.
   The moment analog elements enter the path, conformance must be redefined as statistical envelopes against
   nominal vectors, not exact bit equality. That decision is a project decision, not a slide.
7. **Calibration is still owed before any of this connects to a trained model.** `K0` today exists only as a toy
   construction. Without a stated harvest and evaluation on a real workload, none of Shifts 1 to 3 has an acceptance
   criterion.

## 5. The honest staged path

**Stage II-A (unchanged).** Unikernel owns the weights. No new work items.
**Stage II-B (version 2).** Keep the Frobenius ball as the fast outer bound. Add the projection predicate
(`||ΔW · K0ᵀ||_F ≤ τ`) as a second comparator in the bus admission path, beside it, not instead of it. Digital
LUTs only. Implement in Verilog, simulate against the existing `vectors.json` plus new projection vectors, and
fail the stage if the predicate does not hold bit-exactly.
**Stage II-C-a.** An emulations-only study of the dual-plane macro: static dense plane plus a small digital CGRA
fabric executing rank-r adapter updates. Measure error rate, energy per adapter write, and area vs a dense-digital
baseline. Analog crossbars appear here only as a bounded comparison point, never as the reference.
**Stage II-C-b.** Wafer scale or photonic only if II-C-a produces numbers that beat the baseline. Otherwise retired
with the evidence filed.
**Cell mesh (NoC).** Hold this against Horizon III, not Terrafab. Homomorphic routing enables peer attribution of
usage paths. It couples to the lineage registry, which is where "whose work this ran" is answered. It is a separate
research program that reuses `C6` frames and the provenance concepts. It is not a memory-controller feature.

## 6. Pressure-test questions, sanitized

1. Which predicate does the bus admission gate enforce: ball alone, projection alone, or the stacked pair?
2. What is the calibration workload set for `K0`, and what does coverage evaluation look like on the target cells?
3. Digital or analog for the weft fabric, and what is the noise budget if analog is allowed at all?
4. How does the conformance harness change when an element enters the path that cannot be bit-exact?
5. Who signs a write that passes the S-MMU, and where does that approval live in the `C4`/`I6` path?
6. What is the smallest silicon artifact that proves the II-B predicate without leaving simulation, and what number
   would let us retire it instead of scaling it?

## 7. Priorities

The S-MMU direction is the buildable one because it extends an existing spec. The spatial cell mesh is the
interesting one but belongs to Horizon III's social fabric, where attribution and consent already live. Both are
research. Neither should pull the plasm/invariants code into premature hardware forks, and neither authorizes a
new codebase. Per CONTRIBUTING.md rule 6, an issue is opened before any new top-level directory or component is
created.

## 8. Status

Research capture and audit. No files executed, no RTL written, no issues filed, no gates touched. The design is
recorded here so it can be measured later instead of remembered differently. PR #187 (directional gate), unmerged
at the time of writing, carries
the predicate definition forward. This note carries the silicon placement forward.

Depends on (unmerged): PR #187. This note should not be merged before #187, or read as standalone.
