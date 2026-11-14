# Design Note: The Verifiable Kernel and Adapter Harness

Date: 2026-11-14
Phase: highest-value version of the hardware arc. Still design research. Not adopted. No build is authorized by this note.
Related: `docs/design-notes/horizon-ii-grounded-codesign-loop.md`, `horizon-ii-ideas-backlog.md`, `horizon-ii-silicon-tinker-sandbox.md`. `weft/runtime/invariants/`, `weft/runtime/telemetry/`.
Source material: a pasted external session turn, sanitized. External claims verified against public sources on 2026-11-14. No personal names, no audience framing.

## 1. Why this is the highest-value cut

Everything silicon in this arc is a future pipe dream wrapped around a two year and hundreds of millions of
dollars reality. Kernels, by contrast, are the instruction set of the machines we already own. This turn
converges on the same conclusion as this project's own backlog: the highest-value deliverable is a pure-software,
commodity-hardware stack on the exact public artifacts that exist today.

Verified against public sources on 2026-11-14 (retrieved 2026-11-14):

- **JAXBench** is real. An open benchmark for AI-generated Pallas kernels on Cloud TPUs, 50 workloads,
  17 production operators from public MaxText architectures, the best agent results around 1.36x geomean over
  XLA, and a 1.28x measured lift from documentation conditioning (https://arxiv.org/abs/2607.20466).
- **XProf cycle-level TPU profiling** is real. Announced June 2026 with a worked example cutting a tiled matmul
  from 125.5 us to 88 us by eliminating memory stalls through triple buffering
  (https://opensource.googleblog.com/2026/06/unlocking-tpu-performance-deep-kernel-profiling-with-xprof.html).
- **TPU 8t / 8i** exists as the eighth generation, framed for the agentic era, with the 8i as the inference and
  reasoning serving tier (https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive,
  Google Cloud Next 2026 announcements, April 2026).
- **TorchTPU** makes native PyTorch on TPUs real, which matters far more for adapter serving than any silicon
  spec (https://cloud.google.com/blog/topics/ai-infrastructure/torchtpu-is-now-open-source-run-native-pytorch-on-tpus,
  PyTorch Conference 2026, October 2026).

No one internal to this project asserted any of this. It is verifiable from the cited public primary pages.

## 2. The three layers

**Layer 1. Hardware counter to agent feedback.** Convert raw counters (CUPTI, perf, XProf) into compact
deterministic abios frames the model can read directly. `C6` owns telemetry and `I2` owns framing. The I1 render
layout is untouched. Gate: counter logs, or it does not exist.

**Layer 2. Anti-reward-hacking kernel gate.** Wrap candidate Pallas or Triton kernels in an out-of-process gate:
correctness against golden references (subnormals, NaNs, ULP bounds), then deterministic equivalence where the
candidate is in scope (Alive2/IR for the compiler side, SymbiYosys for RTL later). The agent never touches the
timing binary or corpus. Benchmark first: one JAXBench operator replayed under our gate, not headline numbers.
Under rule 5, CI carries the correctness leg only, on the XLA CPU backend against fixed vectors. The TPU profile
leg is an opt-in local run, never a CI dependency.

**Layer 3. Subspace-bounded multi-LoRA admission.** A serving admission filter for hot-swappable LoRA adapters
(vLLM class, TPU-synced): project incoming adapter updates onto the right null space of calibration activations
(`ΔW P = ΔW` convention in this repository), clamp layer-wise spectral norm (`||ΔW||_2 <= gamma`), bound
Lipschitz drift per layer, reject or flag before HBM. This is Plane 2 work: owner-authorized, self-hosted,
serving deployments only. It is the only layer that is architecture rather than measurement, and it still needs a
trained calibration checkpoint to mean anything.

## 3. Ordering, honestly

`horizon-ii-grounded-codesign-loop.md` recommended Rung A first, Rung B second. This note keeps that order:

1. **Rung A / Layer 1** is the cheapest and pays for itself in evidence, even standalone.
2. **Rung B / Layer 2** is the sandbox, already scoped in `horizon-ii-silicon-tinker-sandbox.md`, now with a
   public benchmark (JAXBench) standing in as the operator battery.
3. **Layer 3** is the product-shaped one, gated on a trained calibration run and scope discipline. Not now.

The compound loop only holds if counter telemetry feeds the RL/search loop back into the gate. That last mile is
still not demonstrated anywhere in public. Claiming otherwise in any external text is out.

## 4. What stays in this repository

Everything here is designed to run on commodity hardware or a Cloud TPU VM. No custom silicon. No tapeout. No analog. No
locked runtime dependency. `C2` and `C6` are the two anchors. `C3` is not touched. Plasm is not touched.

## 5. What must NOT be said externally

Any of the following, stated as fact: recursive self-improvement, production deployment, third-party adoption,
"Google will care", timelines, or any performance figure not measured on a target checkpoint. The artifacts speak
for themselves or they do not.

## 6. Open questions before implementation

1. Which JAXBench operator runs under the gate first, and which MaxText architecture does it come from?
2. The I2 counter record layout: is one neutral schema enough for XProf, CUPTI and perf, or is per-source a
   format decision requiring an interface doc?
3. Layer 3 admissions: host-side plugin API, or a vLLM fork? Library versus out-of-tree matters for licensing.
4. Energy-delay product is the honest inner objective. Which measurement path produces it on this machine today?

## 7. Status

Inventory and ordering. Captured with public sources cited by artifact and date. No code, no issues filed,
nothing adopted. The decision before this project remains: whether Rung A / Layer 1 is authorized first.

Notes on the artifact: this turn contained no personal names and no other situational details after review. The
audience framing is excluded. The `ΔW K0 = 0` symbol printed in the source is not an equivalent statement. It is the
banned product. The canonical forms are `ΔW P = ΔW` with `P = I - K₀K₀⁺` (column-major, `K₀ ∈ R^{d_in x N}`) and
`ΔW · K₀ᵀ = 0` (row-major, `K₀ ∈ R^{N x d_in}`). The source would need correcting to one of those.

Depends on (unmerged at the time of writing): PRs #190, #192 and #193. Read this with them.
