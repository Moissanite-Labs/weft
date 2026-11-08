# Weft convergence plan

Status: proposed architecture and execution plan for [issue #39](https://github.com/Moissanite-Labs/weft/issues/39). Immediate bounded work is authorized; repository splits and a new organization are recommendations to decide, not completed decisions.

Baseline: `main@94b9064f9d09509a46c9e9d9ba219707f9551bb9`, reviewed on 2026-11-08. The independent review sessions behind this plan examined architecture, runtime, surface and ledger evidence. They do not stand in for acceptance by the existing owner teams.

## Intent and scope

[Discussion #11](https://github.com/Moissanite-Labs/weft/discussions/11) establishes durable, verifiable repository work, explicit boundaries, retained contradictions and convergence between code, tests and documents. The [later steering](https://github.com/Moissanite-Labs/weft/discussions/11#discussioncomment-19469025) separates the web-design approach from the larger Syntactic Weft and identifies six levels. The [following reply](https://github.com/Moissanite-Labs/weft/discussions/11#discussioncomment-19469028) permits considering separate repositories or an organization after a council weighs the approach.

The owner's subsequent working-session direction is to act as justified steps become clear, separate what can be used now from what needs further progress, and preserve the many versions and implementation stacks in context. The available personal target is a user-reported M1 MacBook with 64 GB RAM and Chrome; the reported OS name is “Golden Gate 27.0.1.” These are planning inputs, not a hardware verification result. [Use now](use-now.md) explains how to establish the actual host and runtime record.

Keep the full vision. Make each near-term claim precise enough to test. [The variant register](variants.md) records the source and executable alternatives; timestamp or filename order alone does not choose a winner. This plan supplies current sequencing alongside [PROGRAM.md](charter.md). Older phase lists, source inventories and architecture claims retain their provenance and require the reconciliations below.

## Six tracks, with a shared runtime foundation

The tracks describe different problems. Hardware horizons describe the resources available to address them. They are not a single mandatory ladder: governance research, model experiments and an FPGA comparator can advance independently when their own prerequisites are met.

| Track | Boundary and present foothold | Next useful unit | Advancement gate |
|---|---|---|---|
| **1. Procedural mathematical web** | Aywa: rendering, aesthetic interpolation, spatial navigation and data presentation. C7 contains usable modules and an application in `docs/`. | A second small application using the renderer/mixer without Moissanite-specific state. | Browser evidence for WebGPU and Canvas2D, keyboard access, reduced motion, legible data encodings and resource use. |
| **2. Model-responsive web** | A model interprets bounded interaction state and supplies presentation decisions. Current reading cadence is a heuristic; Laya and a browser runtime are available for evaluation. | Validate the actual model/runtime API, then compare local inference against that heuristic on one task. | Model/runtime provenance and license; measured download, memory and latency; an agreed benefit with stable layout and user control. Inference cadence stays separate from frame rendering. |
| **3. Evolving applications** | Intent-driven application composition and learned cellular growth/repair are distinct branches. C1's matrix experiment and the widgets are footholds, not proof of either complete system. | One bounded application whose accepted change can be evaluated and rolled back; a separate NCA experiment if pursued. | Useful task performance, bounded change permissions, preserved intent and recovery. Learned NCA needs trained weights and persistence/damage-repair measurements. |
| **4. OS embodiment** | Scheduling, memory, isolation and recovery. The corpus contains boot and interrupt sketches. | Select an ISA and privilege boundary; build a minimal emulator experiment. | Reproducible boot, scheduling and failure recovery before native privileged integration. Coordinate with existing `exo-os` ownership before crossing repositories. |
| **5. Custom hardware / Terrafab** | Invariant comparators, combinator tiles, interconnect and fabrication are separate research branches. The C gate is one reference input. | Specify finite-precision behavior and simulate one comparator or reducer. | Reference vectors → numerical analysis → timing/resource/energy evidence → FPGA access → fabrication decision. No fabrication date is implied. |
| **6. Governance** | Constitutional research and executable ledger mechanics have different evidence requirements. C4 source and C5 simulation exist. | Test the Solidity locally; specify authority, consent, appeals and succession. | Contract behavior agrees with the accepted policy. Broader adoption depends on people, institutions and political/social agreement as well as software. |

**C1–C3 are a cross-cutting runtime foundation**, not a seventh societal stage: Plasm provides the local adaptation harness and memory arena; C2 supplies bounded predicates; C3 supplies graph reduction and serialization. C6 telemetry and the I1/I2 formats connect producers and surfaces. C4/C5 remain an optional governance/provenance integration for consumers that need them. Aywa should remain useful without a ledger or native Plasm process.

Preserve explicit interface identities: I1 frame, I2 symbolic packet, I3 invariant gate, I4 memory layout, I5 graph serialization/commitment, I6 ledger ABI/events and I7 weight commitments. Several existing documents use conflicting numbers. Reconcile those references with producer and consumer review before publishing a versioned contract.

## Work classes and evidence

| Class | What counts as a deliverable | Time/resource interpretation |
|---|---|---|
| **Tooling usable now** | A documented command or independently usable module, with a reproducible result and limits. | Current CPU/Chrome environment; see [use-now.md](use-now.md). |
| **Bounded experiment** | A question, baseline, falsifier, implementation and recorded measurements. | Can often begin now on CPU, MPS or Chrome; an experiment is not a product capability claim. |
| **Theory research** | Stated premises, definitions, counterexamples and a proof or unresolved proposition. | Examples: IC semantics, invariant mechanization and finite-precision behavior. No completion date before the question is bounded. |
| **Whitepaper / technical document** | Theory with predictions and limits, or implementation documentation checked against code. | Writing runs alongside experiments; prose does not substitute for the underlying result. |
| **Roadmap requiring external progress** | A preserved branch, dependencies, deciding experiment and resource/decision gate. | Hardware access, fabrication, ecosystem adoption and societal/political change have no credible date from this repository alone. |

## Current evidence ledger and corrections

These entries qualify the baseline; they do not claim that the fixes have landed. Source inventories under `docs/corpus/` describe earlier snapshots and remain valuable lineage evidence.

On 2026-11-08 the baseline's full CI command set also passed locally on Linux x86_64, Python 3.12 and Torch `2.15.0+cpu`: 34 Python tests (including the C11 compile/run), 38 Node tests, and daemon, site, core and Mac-wrapper selftests. This records the coverage that exists, not the missing scenarios below. It is not an M1/MPS or Chrome-on-Mac result.

| Finding | Evidence at the baseline | Required disposition |
|---|---|---|
| C1 layout differs across code and specifications. | [Plasm](../../weft/runtime/plasm/plasm.py) uses `(256,256)`, `(1024,)`, `(64,1024)` plus metadata; the [architecture lock](../../weft/WEFT-ARCHITECTURE-LOCK.md) and [roadmap](../roadmap.md) describe other shapes. Equal total bytes do not establish compatibility. | [#40](https://github.com/Moissanite-Labs/weft/issues/40): reconcile I4 with exact offsets, dimensions and conformance evidence. Preserve the source layouts in the variant register. |
| CPU tests are not M1/MPS proof. | [CI](../../.github/workflows/ci.yml) runs on Ubuntu with CPU Torch. Plasm chooses MPS when available and explicitly copies arrays into device tensors. | Record actual Mac/Chrome results before marking the Apple target verified. Qualify zero-copy claims by the boundary measured. |
| Cell boundaries do not yet demonstrate process isolation. | [C1](../../weft/runtime/plasm/plasm.py) constructs candidate tensors in the harness; array bounds and teardown tests do not establish adversarial process isolation. | Specify an isolation boundary and add separate-process lifecycle, crash and cleanup evidence before claiming it. |
| C2 languages are not yet held to one complete contract. | Python's default radius is `120.0`; the C header default is `10.0`. [Python tests](../../weft/runtime/invariants/test_invariants.py) read JSON, while the compiled [C test](../../weft/runtime/invariants/test_invariants_c.c) contains its own cases. | [#42](https://github.com/Moissanite-Labs/weft/issues/42): decide intentional parameter profiles versus defects; drive both languages from the same cases, including defaults, rejection state, nonfinite input and integer boundaries. |
| C3 passing examples do not establish the full language or failure contract. | [BCP](../../weft/runtime/ic/bcp_codec.py) and [VM tests](../../weft/runtime/ic/test_ic_vm.py) exercise a subset of graph/state behavior. No checked confluence proof or allocation profile is supplied. | [#43](https://github.com/Moissanite-Labs/weft/issues/43): specify serializable state and malformed-input/exhaustion behavior; test continuation after round trip and failure atomicity. Treat confluence and universal zero-allocation claims as separate proof/measurement work. |
| C4 has no local EVM build/test in the repository. | [CI](../../.github/workflows/ci.yml) runs the [Python gateway simulator](../../weft/runtime/gateway/test_gateway.py); there is no Foundry/Hardhat project at this baseline. | [#44](https://github.com/Moissanite-Labs/weft/issues/44): compile and execute the actual contracts locally, then compare simulator results, revert semantics and generated ABI/event vectors. |
| Browser worker behavior needs a real runtime check. | Static and Node checks do not execute the complete worker lifecycle. | [#41](https://github.com/Moissanite-Labs/weft/issues/41) addresses the worker startup path; verify initialization, subsequent packets and fallback in a browser. |
| Live telemetry mixes measured and fixture-derived information. | [Harvester](../../weft/runtime/telemetry/harvester.py) has fixture and live paths; a top-level live label does not establish every field's provenance. | [#45](https://github.com/Moissanite-Labs/weft/issues/45): define per-field source, freshness and unavailable/error semantics. Test pagination and partial failure before relying on live values. |
| Laya is an available experiment with distinct model/runtime variants. | A 2026-11-08 metadata check found the English 421M [Laya model](https://huggingface.co/convaiinnovations/laya/tree/7b928d828b7b0e022f929d9bd2e44165aa270148) and [r4ai/laya-web](https://github.com/r4ai/laya-web) 0.2.0. The latter targets a different multilingual 322M checkpoint through `laya-mlx`, with listed browser-export assets totaling about 934 MB. The corpus API is not the current runtime API. | Compare these candidates explicitly, including the upstream [laya-ts](https://github.com/NandhaKishorM/laya/tree/main/laya-ts) path. Validate versions, API, licenses and artifacts; measure Chrome cold start, memory and latency against the heuristic. Neither M5 benchmark claims nor metadata establish M1 behavior. No model download, execution or license clearance was completed by that check. |
| Some canonical provenance links and completion claims are unsupported. | [Mission](../mission.md) and [Aywa note](../design-notes/aywa-web-design-philosophy.md) cite absent `typo.md`, `system.md`, `mind-palace.md`, and other design files. The roadmap describes C8 mesh as implemented although it is absent. | Correct source citations; label implemented, simulated, proposed and hardware-unverified behavior separately. Do not revise original transcript claims into purported historical facts. |

## Execution sequence

Effort bands are rough planning allowances for one focused contributor after prerequisites are available, not promises: **S** is roughly 0.5–2 working days; **M** is 3–10 working days; **L** is several weeks with intermediate checkpoints. Research and external resource gates remain unestimated until an experiment is bounded. Parallel work does not waive interface review.

| Order | Work package and intended owner role | Dependency / acceptance gate | Band |
|---|---|---|---|
| **Now** | I4 repair (#40), Substrate; browser worker repair (#41), Surface; this plan and lineage register (#39), Corpus plus reviewers. | Independent review of runnable falsifiers; code, tests and affected documents agree. | S–M each |
| **Next, in parallel** | C2 common conformance (#42) and C3 failure/serialization contracts (#43), Substrate; actual Solidity/local-EVM tests (#44), Ledger; telemetry provenance (#45) and browser lifecycle coverage, Surface. | Each has a scoped issue, a baseline failure or missing evidence, and tests exercising the real implementation boundary. | M each |
| **Next, in parallel** | Current capability/provenance ledger and track briefs, Corpus with owner-team review; clean bootstrap and per-component build commands. | Correct stale claims and broken references; record dependencies and host/toolchain; separate historical inventory from current status. | S–M |
| **After stable contracts** | Standalone Aywa consumer; bounded evolving-app/runtime experiment; actual M1 CPU/MPS and Chrome record. | One useful task per experiment; limits and failure recovery measured; no implementation is called complete solely because unit tests pass. | M–L |
| **Research branches** | Laya candidate evaluation, Lean/IC work, emulator OS, hardware simulation, constitutional research. | Each branch has its own question, evidence standard, resource needs and stopping/continuation decision. | Bound individually |
| **When independence is demonstrated** | Package/repository extraction proposal, producer and consumer teams. | Independent build, versioned interface, meaningful consumer, owner, provenance and license/distribution decision. | M after gates |

For every actionable finding, file or reuse an issue with evidence and a falsifier. Claim the path before editing. The PR names the issue, scope, verification and unresolved limits. The reviewer records accept, request changes or contest against the actual head and tests. Cross-team contracts require producer and affected-consumer acceptance. Preserve disagreements with the test that could settle them.

## Council recommendation and human decisions

Keep this repository as the integration and provenance record while making component boundaries executable. This allows the six tracks to develop without forcing premature migration. A new repository is useful when independent releases, ownership, access or licensing demand it and the extraction gates above hold. An organization is justified by governance and stewardship needs, not by the number of directories.

Before proposing a new repository, inspect existing Moissanite Labs projects for the same purpose. Treat the synthesis map's “absorb,” “replace” and “supersede” labels as proposed relationships until the affected owners accept them; `PROGRAM.md` currently retains the bridge repositories.

Ask the owner for a concrete decision when a repository/organization, license, external deployment, hardware access or social/governance choice is needed. Bring the relevant design, evidence, alternatives and migration/rollback plan first. Nothing in this document records those decisions as already made. No new repository or organization is needed to execute the first tranche.
