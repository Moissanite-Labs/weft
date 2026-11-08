# Architecture review: top-level corpus against the build program

Reviewer scope: all38 files in `assign-top_corpus.json`, fully read and recorded in `read-top_corpus.json`, plus `docs/program/build-program.md` and `docs/program/experiment-cards.md` as present on2026-11-08. Source snapshot `a721b12579caba4e04dc31b16731cc2657079207`. This is a conceptual coverage/dependency review, not execution or prototype verification.

**Disposition: request a small set of documentation changes; the central architecture and evidence posture are sound.** The proposed local knowledge workspace is explicitly labeled a proposal, preserves the author's broad intent without pretending it is a selected final product, and supplies a useful bounded integration target. The plan correctly keeps token-free operation, proof-language alternatives, native/browser distinctions, consent and institutions, current/future hardware and historical assistant claims separate. The experiment cards use equal-work baselines, explicit falsifiers and honest unexecuted status. No wholesale rewrite is warranted.

## Requested changes

### 1. Preserve the native-runtime → Chrome transport as an explicit deliverable

`build-program.md:56–60` describes telemetry producers and the renderer primarily around repository frame64/SYM inputs. `ainterface.md:48–125,184–225` instead proposes a **native focal tensor →512 float binary frame→Chrome Canvas** path. Its implementation lacks a compliant WebSocket upgrade, but the requirement is distinct and valuable: the user should be able to inspect the local core working through a current browser. The two buffers have different semantics and sizes; they cannot be silently identified.

Add a C6/C7 integration seam or named subcomponent: compliant loopback transport, explicit source/run ID and payload schema, bounded queue/backpressure, disconnect/reconnect/stale behavior, and end-to-end timestamp measurement. Acceptance should show a real native run changing a browser view, with measured versus fixture provenance and no secret exposed. Keep the existing standalone browser kit useful before this seam lands. A small extension to E01 is sufficient; no new framework is required.

### 2. Split the industrial feedback loop from custom chip fabrication

`build-program.md:73` places Terrafab/fabrication on architecture-simulator→FPGA/packaging→foundry steps. `experiment-cards.md:201–207` correctly identifies **two distinct questions**, but the component's ordered gates still risk making plant control wait for a chip. The author's direct contribution at `terrafab.md:86–138,161–187` is the manufacturing/energy/compute feedback loop and measurable benefit. This can begin with existing sensors, control systems and compute, without a custom ASIC or FPGA.

Separate R6 into (a) plant/resource-loop model→digital twin→bounded hardware-in-the-loop→consented industrial pilot and (b) compute substrate→RTL/synthesis/FPGA→packaging/foundry. Both need dimensional cost/energy accounting and independent external-resource gates; neither should require the other's completion. Preserve the custom silicon vision in `terraweft.md:3–58`, including its unproved analog/reconfigurable assumptions.

### 3. Give R5's independent branches individually resumable gates

`build-program.md:72` groups POSIX, native Apple, NCCL, NVMe, haptics and fan control under a generic emulated-device→board/driver path. The line acknowledges different stacks, but those branches have different prerequisites and no dedicated cards. This risks losing the exact systems the source asks to explore:

- **CUDA/NCCL collectives:** `more.md:59–117`, `README.md:618–639`. CPU semantics/parity first, then a measured NVIDIA multi-rank experiment; this is not an M1 backend and does not require custom boards.
- **Bounded haptic feedback:** `more.md:119–192`, `README.md:682–698,943–956`. Begin a simulated actuator/controller with rated-current/torque/slew limits, stability, watchdog and release criteria. Source85-boundary singularity and arbitrary50A values are failing inputs, not device specifications. The exploration knob must not dissolve hard authorization/invariants.
- **Supported host actuation:** `self.md:73–113`. Establish actual supported API/readback and a recoverable bounded action; current source only computes/simulates fan settings. This need not depend on a new kernel or a fabricated board.
- **NVMe associative retrieval:** `almalga.md:235–260`, `README.md:661–680`. Ordinary retrieval/index/durability baseline precedes kernel/controller and DMA proposals. A no-filesystem label is not a performance result.

Subrows or a short linked appendix with one question, gate and next artifact each will preserve these without bloating the main cards. Their early software experiments can run in parallel with P1/P2 where independent.

### 4. Make the non-graph execution journal explicit before adaptation

C3b/I5 already separates graph encoding, checkpoint and trace; E05/E07 retain candidates and replay. However, the corpus's journal aspiration is broader than the graph VM (`almalga.md:215–231`; `xtra.md:170–199`; `tune.md:159–200`). It includes native model state, user steering, accepted/rejected changes and enough evidence to recreate a run. A graph digest, weight digest or chain record alone is insufficient.

Add an explicit cross-component P1/P2 journal/result contract, used before P3 adaptation: initial state; actual inputs; RNG/configuration; candidate and committed identities; transitions; authorizations; runtime/model/environment versions; timestamps and declared nondeterminism; artifact hashes and retrieval paths. Require replay equivalence only where promised, with clear limitations for GPU/non-deterministic behavior. This can extend I5 or the proposed intent/evaluation contract rather than create another subsystem. The first release unit's replayable example should use it.

## Small corrections and acceptance details

- `experiment-cards.md:3` has spaces inside the audit commit (`a 721b 12579caba...`); replace with the actual40-character commit so it is unambiguous and machine-usable.
- In C4's local acceptance, explicitly include **genesis distribution/liveness**, not just balance arithmetic. `launch.md:91–164,166–233` and `README.md:84–109,330–381` mint all supply to the governor contract without a shown ordinary distribution path. Tests should distinguish policy choice from a mechanically inaccessible initial supply.
- The variant register should preserve README's **within-file regressions**: first token approve at95–99 and registry verifyAttribution at240–251 disappear from the later integrated tape1062–1297; guards and admin transfer also differ. The program says variants are preserved, so ensure the concrete register supports that commitment. No requirement to prefer the first version wholesale.
- E11 sources currently emphasize `mugetsu`/`soc`; the direct OS/ISA/APIC anchors are `README.md:398–533`, `more.md:6–57`, `mac.md:7–64`, and invalid mixed-ISA sketch `almalga.md:883–926`. Add those for stronger traceability.

## What this review accepts

The phase structure is not a compulsory waterfall, and early theory/emulator/RTL work need not wait for a global ledger. Numerical constraints, task fitness, process isolation, action authorization and social legitimacy are treated as different properties. The token-free alternative is useful now rather than waiting for post-scarcity. Human intent modeling is bounded, consented and revocable, with no claim of consciousness preservation. Source recovery preserves variants rather than granting authority to the latest synthesis. The trial hardware/resource ceilings are labeled proposed limits rather than measured requirements. Existing sibling projects are bridges until an explicit integration decision; historical “absorb/replace” language is not made current authority.

The requested changes complete architectural traceability and ordering; they do not challenge those sound decisions or ask to block the current bounded repairs.


## Resolution review — ACCEPT (2026-11-08)

Re-inspected the final component map, integration contracts, execution queue, changed experiment cards and variant addendum. All requested architectural changes and small corrections are resolved:

- **Native→Chrome seam:** C7b and E01’s native-viewer follow-up identify the512-float source separately from I1, with run/source identity, bounded transport, backpressure, stale/reconnect behavior and an actual native-run demonstration gate.
- **Independent industrial loop:** R6a explicitly allows existing sensors/compute and orders plant model, twin, hardware-in-the-loop and pilot independently of R6 fabrication. Facility access and owner decisions remain external gates. R6b additionally preserves constrained own-substrate design experiments without claiming self-manufacture.
- **Hardware/interface branches:** R5a–d now have separate resumable NCCL, haptic, supported-host-actuation and NVMe paths with the requested comparison and hardware limits.
- **Journal before adaptation:** C1e and the whole-runtime journal/result contract explicitly precede P3, retain inputs/state/versions/authorizations/candidate-versus-commit identity, and declare nondeterminism and replay tolerances.
- **Smaller corrections:** C4 includes genesis distribution/liveness; the variants addendum records README’s removed approve/verifyAttribution and guard/admin differences; E11 cites direct ISA sources; the audit SHA is exact and thread links are normalized.

No remaining architectural change request within the38-file top-level review scope. **ACCEPT the revised planning documents for this tranche.** This accepts coverage, ordering and honest evidence framing; it does not certify unexecuted prototypes, hardware performance, contract deployment or future experiments. The earlier findings remain above as the review history, with this resolution as the current disposition.

Reviewed document SHA256 values at acceptance:

- `docs/program/build-program.md`: `83a561ddb92243913ad378bf71a7e694ba7478cbb1c39c882bf4a991ef384a6f`
- `docs/program/experiment-cards.md`: `5e33805ca7c2f8f4ab8b46b77e7e5148e08e8030eb7387a630ee8160d241dd1c`
- `docs/program/variants.md`: `bea6fd437188a1fc508b23566fd2a296f0de71273f2cdb35c9150e6582c20d44`
