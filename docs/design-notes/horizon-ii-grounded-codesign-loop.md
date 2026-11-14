# Design Note: The Grounded Co-Design Loop

Date: 2026-11-14
Phase: bridge research between Horizon I and Horizon II. Not adopted. Not a plan for silicon.
Related: `docs/design-notes/horizon-ii-ideas-backlog.md`, `scwsp-directional-gate.md`, `horizon-ii-dual-plane-silicon.md`, `horizon-ii-verified-causal-substrate.md`, `horizon-ii-bio-causal-substrate.md`. I1 (`weft/runtime/telemetry/frame64.py`), I2 (`sym2p_codec.py`), `decomposition.md`, `convergence-plan.md`.
Source material: a pasted external session turn. Audited. All vendor and tool references are public artifacts.

## 1. Origin and the orientation fix, done right

This turn is the first in the hardware arc that got the construction right, and it uses the column-major form.
The preserved keys are `K₀ ∈ R^{d_in x N}` (keys as columns). Projection acts on the right: `ΔW P = ΔW` with
`P = I - K₀ K₀⁺`.
The row-major equivalent used elsewhere in the series is `ΔW · K₀ᵀ = 0` with `K₀ ∈ R^{N x d_in}` (keys as rows).
The two are the same statement read in the two layouts. One document states its shapes once and does not mix them.
The turn
also wrote, correctly, that `K0 ΔW = 0` is not the AlphaEdit condition and does not even have a matching inner
dimension in the general layout. And it conceded the envelope overreach and the 16 to 64 KB figure. Take the win.
The arc is materially better grounded than the previous four turns.

## 2. The north star, in the owner's words

"Turn as much hardware data inward to the model itself so it can iterate on its own hardware architecture and
enter a compounding loop of recursive improvement where it keeps improving its hardware enabling better models to
be created and run, which in turn create better hardware."

Recorded verbatim as intent. The rest of this note decides what portion of that is real, today, with named tools.

## 3. The proposed loop, and what the audit finds in each stage

**Stage 1. Fine-grained introspection.** CUPTI on NVIDIA devices, Linux `perf`, XProf for TPU-side
profiles, cycle-accurate Verilator traces for a design under development. Emits counter logs: stalls, HBM
versus SRAM byte ratios, cache misses, congestion.
Existing and public. None of it is wired into this repository. Any port needs an I2 record, because `frame64.py`
carries a fixed I1 layout and must not be repurposed for a different meaning.

**Stage 2. Compiler and kernel co-evolution.** MLIR, XLA, Triton graph lowering, building on the TVM/Ansor and
AlphaTensor precedents: the model proposes layouts, tilings and fused kernels, measured against real latency
and energy. Gate: equivalence checking (Alive2-style IR checks, SMT solvers) plus tolerance-checked unit tests.
Exists as public research and open-source tooling. Required engineering is large but ordinary. This stage is
nearer to us than any silicon stage.

**Stage 3. Fast-turnaround silicon iteration.** HLS in CIRCT or Chisel to SystemVerilog, targeted at FPGA boards
(Alveo or Versal class) before any ASIC is contemplated. Gate: SMT-based formal equivalence (SymbiYosys), DRC and
timing signoff, Verilator cycle-accurate comparison against a golden model.
Exists publicly. FPGA closure times run minutes for compile but tens of minutes to hours for place and route
(hypothesis, not measured on this project). The ~5 to 10x clock gap between FPGA fabrics and ASICs is an
order-of-magnitude hypothesis, not a measurement. Verilator plus analytical PPA proxies are the
only viable inner loop. Full synthesis is reserved for final candidates.

**Stage 4. Model-hardware co-search.** Hardware-aware NAS and quantization/sparsity co-design. Gate: held-out
capability benchmarks and Weft-style parameter and budget envelopes.
Exists as research discipline. Real wins are modest and measured. Nothing here is turnkey.

## 4. What is true

- Today's runtimes are blind to the silicon beneath them. CUPTI, perf and XProf exist because that blindness is a
  real problem. Nothing closes a model-to-chip loop end to end in public.
- Compiler IR and RTL are genuinely formally verifiable in ways learned weights are not. That asymmetry is the
  whole reason this loop has any floor.
- Two timescales are real: seconds for kernel and microcode changes in software, hours for RTL-on-FPGA.
  The ASIC spin is 18 to 24 months (industry lore, hypothesis, not measured here) and is outside any near-term loop.
- MXFP4 and FP6 block-floating-point formats are public OCP microscaling artifacts.
- Autotuning plus measurement beats autotuning plus FLOP estimates. Always.

## 5. What must not be claimed

- There is no demonstrated public end-to-end loop of a model redesigning its own substrate that compounds.
  Each stage is ordinary, narrow, measured engineering. Compounding is conjectured. It does not exist yet.
- "Recursive self-improvement" is not a capability claim this note, this repository, or these turns are entitled
  to make. The honest unit of progress is one verified kernel rewrite, measured end to end.
- Online adaptation is not established to emit any capability. Whether it does is an empirical question with no
  current answer, and this note claims no such property. Adaptation certainly
  does not excuse the invariant orientation, the envelope
  overreach, the framing-as-fact numbers, or benchmark-free performance stories.
- JasperGold is commercial tooling. Mentioning it is fine. Depending on it is not our posture. SymbiYosys is the
  open path.

## 6. The two rungs, with a recommendation

**Rung A. Extend `C6` telemetry to digest real accelerator counters.** CUPTI on macOS does not exist. The macOS
leg is `perf`-portable sampling (DTrace-like) or a Metal timing harness. The practical port targets Linux GPU
and XLA/TF traces. Emits an I2 artifact candidate, not I1. Whether counter records belong in SYM-2P proper or need
their own interface is an open question carried into #193 to #195. Adds a counter-record schema and vectors, no C-path changes.
Non-invasive. Directly advances the project's telemetry posture and produces the inward data the loop rests on.

**Rung B. A minimal verifiable sandbox for one operator.** One operator, chosen from profiled blind spots (an
attention block or an activation router). Metal plus Triton at the software level, or Verilator plus SymbiYosys
for the RTL-level variant. The model proposes a rewrite, equivalence is checked formally, correctness is checked
against golden vectors, and only then is it measured on real hardware.

Recommendation. Rung A first, then Rung B on top of it. Rung A informs Rung B with evidence instead of targets.
Neither is authorized yet. Neither should be worked without a filed issue naming the interface and the vectors.

## 7. The arc's standing rule, tightened

1. One canonical orientation everywhere. `ΔW P = ΔW` with `P = I - K₀K₀⁺`, `K₀ ∈ R^{d_in x N}`, or the row-major
   `ΔW · K₀ᵀ = 0` with `K₀ ∈ R^{N x d_in}`. One document, one layout, shapes stated.
2. Numbers are measured or labeled hypothesis. No exceptions.
3. Public tool names, no external partnership words, no vendor targeting.
4. Biological analogy is a teaching tool only. Verification is LUTs, vectors and proof.
5. Innovation stays in the admission path and the interface. Nothing else moves until the gate is green.

## 8. Status

Research capture with a grounded recommendation attached. No code, no RTL, no issues filed, nothing adopted.
The decision before this project: whether Rung A is authorized, and on what evidence.

Depends on (unmerged at the time of writing): PRs #187, #188, #189, #190 and #191. Read this with them.
