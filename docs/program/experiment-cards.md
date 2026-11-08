# Weft experiment cards

Status: proposed, unexecuted protocols for [issue #49](https://github.com/Moissanite-Labs/weft/issues/49), derived from the complete-corpus audit at `a721b12579caba4e04dc31b16731cc2657079207`. These cards make the vision testable without choosing one implementation lineage by age. They complement the [build program](build-program.md), [convergence plan](convergence-plan.md), [variant register](variants.md), [use-now guide](use-now.md), and [reading evidence](audit/notes-threads_design.md).

The owner's target is a reported M1 MacBook with 64 GB unified memory and Chrome. Actual chip, OS build, Chrome and native backend versions remain to be recorded. Linux CPU or software-rendered Chromium results are separate evidence. Resource ceilings below are proposed bounds for initial experiments, not measured requirements, performance promises or assertions that OS/browser quotas already enforce them. Stop or reduce a workload when the host reports memory pressure, the adapter is lost, allocation fails, or responsiveness materially degrades. Log the stop as a result. Do not silently expand a ceiling.

## Recording contract

Before each experiment, record its question, condition order, primary outcome, acceptable regression bound, seeds/input fixtures, dependency versions, exact commit and stopping budget. Set the meaningful quality threshold before observing outcomes; a latency improvement alone does not satisfy a usefulness claim. If a threshold cannot yet be justified, label the run exploratory and use it to design the next test.

Retain configuration, code/model/asset hashes, environment, commands, raw machine-readable measurements, failures, stdout/stderr, representative screenshots where relevant, and a concise result/decision note with alternatives and limits. Store approved experiment artifacts in proposed `docs/program/experiments/<card-id>/<run-id>/`; large artifacts may use an in-repo manifest referring to private retained storage after its location is established. Do not create an implied component tree until its issue identifies the path. Each run's manifest distinguishes measured, derived, fixture and unavailable values. An absent result is not a pass. Preserve negative results and the exact next question.

For personal studies, retain consent and task-level observations in an appropriately private record; the shared repository receives aggregate results and redacted fixtures, not passwords, tokens, device identifiers or unrelated personal content. This follows the corpus's own privacy/consent aims and makes results reusable.

| Card | Track | Class | Can begin on present hardware? |
| --- | --- | --- | --- |
| E01 Procedural surface and semantics |1| Tooling experiment | Yes, Chrome and fallback renderer |
| E02 Local decisions versus heuristics |2| Model comparison | API/assets check now; bounded inference after prerequisites |
| E03 Mind-palace teaching |1/2| Product/learning experiment | Yes, no model required |
| E04 Composable aesthetic slices |1/2| Tooling and social interaction | Local composition now; shared writing after authority design |
| E05 Intent-driven application |3| Bounded application experiment | Yes, one local task and fixed capability set |
| E06 Learned NCA |3| ML/research experiment | Small CPU/MPS training; browser inference separately |
| E07 Cell adaptation, novelty and decay | Shared C1–C3 /3| Runtime experiment | Small matrices now; real adapters later |
| E08 Consented preference prediction |2/3/6| Personalization research | Yes, with voluntary labels and revocation |
| E09 Typed versus latent communication | Shared substrate /3| Representation research | Small compatible models; no frontier-scale assumption |
| E10 Invariant/reducer proof bridge | Shared substrate /5| Theory plus conformance | Yes, CPU and proof tooling |
| E11 OS capability embodiment |4| Emulator experiment | Yes, bounded emulator; native Apple boot later |
| E12 Hardware comparator and equal-work model |5| Simulation/R&D | Software simulation now; FPGA/fabrication later |
| E13 Executable authority and governance |6| Contract/scenario research | Local simulator/EVM; institutional adoption separately |

These tracks are not a compulsory staircase. E01, E03 and E04 can create useful tools while E06 or E10 remains inconclusive. An optional ledger, trained model, custom OS or fabricated chip must justify its own contribution.

## E01 — Does procedural rendering improve the useful surface while preserving semantics?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 2–3,21–24,37–39; procedural shape/state mapping, repository visualization, noise and glyphs. [Browser audit](audit/notes-browser.md) records current implementation evidence; [PR46](https://github.com/Moissanite-Labs/weft/pull/46) addresses a subset of telemetry refresh behavior.

**Question and usefulness:** Can the field communicate repository state and support navigation as clearly as a straightforward accessible list while offering the intended mathematical visual expression?

**Baseline:** the same labeled repository fixtures in a semantic HTML list/table, plus the current Canvas 2D fallback. **Manipulated variable:** WebGPU field versus fallback/list; separately compare motion on/off and visual encoding channels one at a time. **Fixed factors:** data, freshness, viewport, content, labels, task order/counterbalancing, network fixture, device and browser. Keep the field's styling independent of source metrics.

**Measurements:** task completion/correctness (identify a stalled review, locate a repo, explain a displayed metric), keyboard/focus/screen-reader availability, reduced-motion behavior, resize/DPR correctness, frame-time distribution, CPU time, memory and observed energy proxy if available. Record actual renderer and any software adapter. Include root/nested routes, updated sequence, rejected packet, stale producer, fetch failure, recovery and device loss; record the end-to-end producer/consumer delay rather than just poll interval.

**Falsifier/stop:** the interface misrepresents a fixture, conceals failure, prevents an essential action, loses content semantics, or cannot meet its preregistered task/regression bound. Stop a condition on adapter loss or unbounded work; do not average failures away. A decorative improvement without task benefit can remain an optional aesthetic mode.

**Initial resource bound:** at most 64 repository fixtures and three specified viewport sizes; one browser tab, a 10-minute steady-state run per condition, and 256 MiB explicitly allocated renderer buffers. Measure total browser/driver memory separately because buffer totals are not host memory. Scale only after this run explains cost.

**Prerequisites:** truthful fixture labels, stable parser/renderer contract, inspectable legend and semantic controls. **Retain/output:** screenshots, task traces, browser logs, timing/memory samples and renderer configuration under `experiments/E01/`; accepted behavior becomes C7/browser tooling and its documented limits.

**Native-viewer follow-up (C7b):** compare a recorded512-float focal-state fixture with the same schema emitted by an actual local C1 run over a compliant loopback transport. Keep it separate from the16-float I1 organization frame. Record run/source IDs, queue bounds, end-to-end age, stale/disconnect/reconnect and backpressure behavior; no direct POSIX-memory access is assumed in Chrome. Source: `ainterface.md:48–125,184–225`.

## E02 — Does a local decision model beat a cheap heuristic for a bounded presentation task?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 4–5 and 12–18. [Convergence plan](convergence-plan.md) records distinct English 421M and multilingual 322M Laya/runtime candidates; do not interchange their claims or checkpoints.

**Question and usefulness:** Does model inference improve a specified presentation decision enough to justify cold-start, RAM, power and maintenance costs? Begin with explicit choices such as compact/spacious/helpful-summary requested by a participant. Treat inference of reading engagement from scroll/dwell as a separate hypothesis, not ground truth.

**Baseline:** explicit preference only, existing cadence heuristic, and a fixed no-adaptation control. **Manipulated variable:** decision mechanism (heuristic versus one pinned model/runtime pair); compare a second model only as a separate condition. **Fixed factors:** identical recorded interaction windows, questions/options and output schema, smoothing, renderer, decision cadence, task labels, browser/device and cache state. Inference cadence is independent of animation frames.

**Measurements:** held-out decision correctness, calibration/abstention, override frequency, task success, perceived comfort, inference latency percentiles, cold asset bytes/time, warm cache behavior, peak memory and frame impact. Report WASM CPU and WebGPU independently. Test missing adapter, failed download, cancellation and model unload. Verify network requests before calling a run local/offline.

**Falsifier/stop:** the model fails its preregistered quality gain or causes unacceptable regression versus the heuristic; predictions change essential controls without explicit permission; interaction signals are treated as proof of emotion; unsupported API or artifact/license ambiguity prevents reproduction. Failure means retain the simpler useful mechanism while preserving the research branch.

**Initial resource bound:** one model loaded at a time, no default-site integration, at most 1.5 GiB fetched experiment assets after a manifest inspection, a 1 GiB bounded local cache, ten minutes warm inference per condition and a 4 GiB measured-process target. Browser/driver memory accounting is imperfect: record host pressure and stop if the target is exceeded or unavailable accounting prevents bounding the run. These are experiment limits, not claims about Laya's needs. No model download was performed for this card.

**Prerequisites:** pinned checkpoint/runtime/API/license records; explicit model-loading UI; worker lifetime and finite/bounded-output validation; a labeled dataset independent of training/prompt tuning. **Retain/output:** asset manifest, decision fixtures, condition results, error cases and runtime adapter under `experiments/E02/`; advance to model-responsive tooling only on measured benefit.

## E03 — Does an interactive mind palace teach the architecture better?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 6–8; user explicitly asks for a better way to learn the technical concepts and an animation of how parts cooperate.

**Question and usefulness:** Does manipulating a faithful telemetry→decision→uniform→shader diagram help a learner predict and debug the system?

**Baseline:** a short prose explanation with the same facts and a static diagram. **Manipulated variable:** interactive biological/spatial representation versus baseline; then optional spatially stable versus rearranging layout. **Fixed factors:** concepts, examples, available time, reading level and question difficulty. Use counterbalanced disjoint examples so repetition does not masquerade as teaching.

**Measurements:** immediate and delayed explanation accuracy, prediction of which layer changes a pixel, ability to distinguish model/heuristic/simulation, time to locate a fault, recall of provenance and perceived cognitive effort. A single-owner pilot is exploratory; do not generalize from it to all users.

**Falsifier/stop:** metaphor produces systematic misconceptions (for example treating GPU pixels as independently trained minds), harms recall, or obscures actual data flow. Revise the mapping rather than dropping the author's wonder/biological vocabulary. Stop motion that interferes with the task.

**Initial resource bound:** no model, at most 8 concept nodes, one local browser tab,20 minutes per study session,128 MiB application-owned assets/buffers; record actual cost. **Prerequisites:** verified component definitions and keyboard/semantic alternatives. **Retain/output:** lesson version, questions/rubric, redacted responses, screenshots and outcome under `experiments/E03/`; resulting learning surface can ship independently of neural adaptation.

## E04 — Can users compose, exchange and understand aesthetic slices?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 30–35. Preserve the progression from explicit taste to modular sharing and an in-page ecosystem.

**Question and usefulness:** Can composable preferences improve fit without confusing authorship, weakening readability or overwriting another user's choices?

**Baseline:** two complete preset themes and manual settings. **Manipulated variable:** binary blend, normalized N-way composition and per-feature slice selection; test shared suggestions separately from locally selected styles. **Fixed factors:** same available rounding/density/hue/contrast traits, data, content, task and validation limits. Preserve circular hue semantics and deterministic fallback at zero or antipodal vectors.

**Measurements:** time to reproduce a requested style, resulting readability/task success, successful canonical export/import, explanation of contributors/influence, reset/revert success, and behavior with invalid/nonfinite/negative/oversized inputs. For a shared-registry prototype, test concurrent updates, duplicate/fork identities, ownership, permission denial, revocation and stale revisions. A displayed profile is not authenticated merely because a hash matches.

**Falsifier/stop:** mixing causes illegible content or unbounded values; importing/exporting changes meaning; user cannot undo; two writers silently lose each other's contribution; another user's preference changes a private selection without agreed semantics. Do not proceed from local import/export to automatic global influence until that choice is explicit.

**Initial resource bound:**16 active slices,256 candidate library entries, at most 1 MiB total imported profile data, no model, one browser tab and local files first. Use a temporary private test branch for an authorized shared-writing experiment; no public write or automatic deployment. **Prerequisites:** strict profile schema, attribution fields, immutable version IDs, local persistence and authorization design for writes. No public CORS authentication proxy and no copied corpus OAuth client identity.

**Retain/output:** canonical vectors, property tests, import/export fixtures, composition examples, concurrency traces and user feedback under `experiments/E04/`; local mixer/profile tooling first, shared registry/auth as a separately reviewed component.

## E05 — Can an intent-driven application change itself usefully and recover?

**Source intent:** [splicers genesis](../../weft/browser-sources/thread1-splicers-genesis-90133B.md), turns 3–4,12,16–20; [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 12–15. Applications-as-behaviors is an architectural hypothesis with several possible realizations.

**Question and usefulness:** Can a bounded adaptive tool satisfy a new user constraint with less rework while preserving existing requirements and a complete rollback path?

**Baseline:** fixed implementation plus explicit configuration. **Manipulated variable:** model-generated configuration/component composition versus a small adapter or generated program; evaluate each separately, not as interchangeable forms of adaptation. **Fixed factors:** one local task (for example organizing fixture notes into a chosen view), input corpus, acceptance suite, available capabilities, seed/checkpoint, execution time and side-effect policy.

**Measurements:** held-out task correctness, user correction count, time/compute to adapt, preservation of prior requirements, error visibility, deterministic replay where possible, rollback and crash recovery. Include ambiguous intent and a requested change outside capabilities. Compare the actual accepted artifact with the artifact evaluated; score neither a different candidate nor an uncommitted output.

**Falsifier/stop:** adaptation changes undeclared state, bypasses the action broker, fails a retained requirement, or costs more than the configuration baseline without compensating benefit. A task evaluator must be independent of the candidate that seeks acceptance.

**Initial resource bound:** one task, fixture-only working directory, at most 2 speculative candidates, ten adaptation attempts,30 minutes total native compute and 8 GiB peak working-set target; no network/file writes outside the experiment workspace. Model size follows the cap rather than assuming 64 GB permits any checkpoint.

**Prerequisites:** accepted authority/action schema, scoped process sandbox or equivalent capability boundary, executable task/retention suite, artifact journal and rollback. Ordinary Python subprocesses alone do not establish sandboxing. **Retain/output:** intent revisions, candidates, tests, chosen artifacts and replay bundle under `experiments/E05/`; accepted result becomes an independently useful app/harness example, not a claim that all applications are obsolete.

## E06 — Is the self-healing visual rule learned, persistent and generalizable?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 9–11, plus the NCA widget line; [PROGRAM.md](../../PROGRAM.md) sets growth, persistence and damage metrics rather than the hand-coded widget as the evidence bar.

**Question and usefulness:** Does a trained local rule recover a target under unseen perturbations better than coordinate-aware reconstruction or a hand-coded CA, at acceptable cost?

**Baseline:** current heuristic widget, a coordinate-aware target repaint, and a static image reset. **Manipulated variable:** learned NCA rule; separately ablate hidden channels, stochastic updates, training damage augmentation and global conditioning. **Fixed factors:** target, grid, damage masks, update budget, random seeds, dtype/backend and evaluation horizon. Learned rule inference must not receive hidden target coordinates unavailable to its baseline definition.

**Measurements:** held-out growth success, target error, recovery time after unseen cuts, survival/persistence over a longer horizon than training, sensitivity to seed/scale/update rate, model bytes, memory and step time. Record failures and collapse modes. Test typography/action semantics separately; regrowing an image does not prove a functioning application.

**Falsifier/stop:** rule only works on training masks, drifts after the observation window, needs target-aware repainting to recover, or offers no useful advantage over the simple control. Stop training at its preregistered compute budget rather than tuning until one attractive example appears.

**Initial resource bound:**64×64grid, at most 16 state channels and a small documented rule network;30 minutes initial training per condition, three seeds,8 GiB host-memory target. Measure CPU and MPS separately; browser inference on the exported artifact is another run. These caps are a pilot design, not an adequacy guarantee.

**Prerequisites:** a cited/versioned training recipe with license, train/evaluation split, export parity checker and clear widget label. **Retain/output:** weights, training configuration, damage/seed corpus, full trajectory metrics and selected videos under `experiments/E06/`; theory note for observed mechanisms and a bounded browser demo if export parity passes.

## E07 — Do novelty and decay improve adaptation without erasing useful behavior?

**Source intent:** [splicers genesis](../../weft/browser-sources/thread1-splicers-genesis-90133B.md), turns 19,21–23,26–28; [runtime audit](audit/notes-runtime.md) distinguishes actual C1 behavior from the variants.

**Question and usefulness:** Can constrained exploration and intelligent forgetting improve task-switch adaptation while retaining quality, diversity and reproducibility?

**Baseline:** no adaptation, fitness-only adaptation, and fixed small learning/decay settings. **Manipulated variable:** novelty term, archive policy, protected plasticity mask, consolidation rate and usage-sensitive decay, one at a time before a factorial combination. **Fixed factors:** same saved parent weights, input/target tasks, candidate seeds, budget, dimensions, evaluation examples, backend and publication rules.

**Measurements:** actual committed task error, held-out utility, diversity in a behaviorally meaningful representation, retained-task performance, drift from saved baseline, rejected/accepted candidate counts, measured compute and restart reproducibility. Run a stationary task, a switch, a recurrence of an earlier task and a distribution shift. Compare archive mean-distance with quality-constrained diversity; uniform weight shrinkage is a separate control from usage-sensitive decay.

**Falsifier/stop:** novelty wins through magnitude inflation or lower task quality; decay fails to preserve protected parameters or produces divergent/sign-flipped updates; repeated seeds do not explain differences; promoted weights fail to reproduce scored output; insufficient/unready candidates are selected. Freeze external side effects until acceptance.

**Initial resource bound:** current small matrix dimensions first,2 candidates/generation, at most 100 generations per condition, five fixed seeds and 1 GiB explicit tensor/arena allocation; cap a condition at 15 minutes. A real-model adapter follow-up gets a separate 8 GiB/30-minute pilot budget and new task/retention evidence. **Prerequisites:** #40/#47 I4 contract, #42 numeric semantics, truthful committed-state reporting, deterministic RNG, ownership/epoch/readiness and teardown tests.

**Retain/output:** candidate and accepted weights/deltas, complete input/configuration, scores, state transitions, rejection causes and replay record under `experiments/E07/`; a benchmarked adaptation harness plus a theory note separating numerical invariants from semantic safety.

## E08 — Can a living user's chosen preferences be predicted with useful abstention?

**Source intent:** [design thread](../../weft/browser-sources/thread2-design-main-6C083A.md), turns 5,12,30–35; [imprint](../../weft/imprint.md) and [top-level audit](audit/notes-top_corpus.md); [PROGRAM.md](../../PROGRAM.md) separates a testamentary policy, a testable preference model and unsupported claims of survival.

**Question and usefulness:** Can a voluntary, correctable preference model reduce repeated settings work while respecting explicit instructions and changes of mind?

**Baseline:** user-selected saved settings and a recency/frequency rule. **Manipulated variable:** lightweight preference model versus the rule; separately compare explicit labels with optional interaction-derived features. **Fixed factors:** same consented tasks/options, held-out time period, feedback opportunities, abstention policy and available actions. Do not use mouse motion as a diagnostic label or infer an unobserved inner state.

**Measurements:** future-choice prediction, calibration, abstention, override/undo frequency, satisfaction, sensitivity to changed preference, deletion/retraining behavior and performance by context. Use a prospective held-out segment; tuning on past choices alone cannot establish future alignment. One-person results remain specific to that participant.

**Falsifier/stop:** explicit user choice is overridden, prediction is less useful than saved settings, corrected preferences fail to propagate, retained data cannot be deleted, or uncertainty is hidden. Consent withdrawal stops collection and triggers the documented deletion path. A successful model predicts choices; it does not establish continuity of consciousness, identity or legal authority after death.

**Initial resource bound:** a voluntary pilot of at most 100 labeled choices, local encrypted/private storage with an explicit retention date, no large model requirement,1 GiB computation target and 15 minutes per evaluation condition. **Prerequisites:** consent/feature purpose, accessible correction/reset, temporal split and abstention rules. **Retain/output:** redacted protocol, schema, aggregate metrics and deletion/revocation test evidence under `experiments/E08/`; raw personal labels remain in the agreed private location. A whitepaper can state findings and limits; societal/succession policy is E13, not implied by predictive accuracy.

## E09 — When is latent communication better than typed or textual messages?

**Source intent:** [splicers genesis](../../weft/browser-sources/thread1-splicers-genesis-90133B.md), turns 16–18,22,28; Focal/Sympathetic/Dialectic and KV-cache proposals. The corpus assumes shared latent meaning more often than it demonstrates it.

**Question and usefulness:** Does a compatible latent representation reduce cost/latency without losing task meaning, inspectability or version interoperability?

**Baseline:** compact typed records and a text representation carrying identical task information. **Manipulated variable:** aligned latent vectors, learned projection, or compatible-model KV transfer; treat these as separate protocols. **Fixed factors:** information content, task split, models/checkpoints, dtype, transport, hardware, serializer and evaluation budget. Separate serialization savings from reduced model reasoning or different information access.

**Measurements:** downstream task accuracy, bytes, encode/decode/inference time, RAM, cross-version transfer, perturbation sensitivity and recovery after corrupted/nonfinite/out-of-order messages. A shared-memory zero-copy view must be measured at that boundary; CPU→MPS/WebGPU upload may still copy.

**Falsifier/stop:** latent channels only work with accidental shared coordinates, lose meaning after version change, underperform a typed baseline, or lack an inspectable way to reject malformed state. Arbitrary raw tensor shape equality does not establish semantic compatibility.

**Initial resource bound:** two small compatible models or linear toy agents,512-dimensional messages, at most 1,000 held-out exchanges,2 GiB total tensor allocation and 30 minutes per condition; local loopback only. **Prerequisites:** precise message/schema/version semantics, seed/task baselines and bounded transport. **Retain/output:** encoders/projections, paired fixtures, benchmark and compatibility matrix under `experiments/E09/`; promote only demonstrated transport/representation combinations. Remote mesh and migration retain their separate consent gate.

## E10 — Which mathematical claim survives contact with the actual numeric and graph semantics?

**Source intent:** [prove](../../weft/prove.md), [langdoc](../../weft/langdoc.md), [provocol](../../weft/provocol.md), [runtime audit](audit/notes-runtime.md); current repair issues [#42](https://github.com/Moissanite-Labs/weft/issues/42) and [#43](https://github.com/Moissanite-Labs/weft/issues/43).

**Question and usefulness:** Can a narrowly stated invariant or graph rewrite property be proved in a formal model and connected to the executable implementation by explicit conformance evidence?

**Baseline:** current Python/C examples and an independent simple reference reducer. **Manipulated variable:** defined arithmetic profile, topology representation, rule/scheduler or failure policy. **Fixed factors:** exact contract, input graph corpus, finite precision/overflow assumptions and pre/post-state definition. Distinguish mathematical reals, float32/64 and bounded integers; distinguish pure/labeled/metabolic calculi.

**Measurements/artifacts:** proof kernel check, counterexample search, shared-vector parity, finite boundary cases, malformed topology rejection, continuation after serialization, failure atomicity and schedule comparison on defined small graphs. A theorem about real-number norm bounds does not prove a Python memory boundary or external-action policy.

**Falsifier/stop:** counterexample, unproved premise, mismatch with actual numeric semantics, or a rule whose peer-port identity cannot be represented. Reduce the claim to what can be justified rather than labeling the full architecture proven.

**Initial resource bound:** CPU-only, graphs up to 8 nodes for exhaustive pilot enumeration, at most 100,000 generated cases,2 GiB memory and 30 minutes per solver run. These are search limits, not proof limits or completeness claims. **Prerequisites:** producer/consumer agreement on I3/I5 contracts; known theorem tooling and versioned dependencies. **Retain/output:** definitions, proofs, failing witnesses, checked vectors and mapping to implementation under `experiments/E10/`; proof/technical note plus conformance tests. GPU/RTL claims require additional refinement evidence.

## E11 — Can an OS embodiment enforce a smaller, testable capability boundary?

**Source intent:** [splicers genesis](../../weft/browser-sources/thread1-splicers-genesis-90133B.md), turn 25; [README](../../weft/README.md):398–533 (x86 boot/APIC), [more](../../weft/more.md):6–57, [mac](../../weft/mac.md):7–64 and [almalga](../../weft/almalga.md):883–926 (mixed-ISA defects), alongside [mugetsu](../../weft/mugetsu.md), [soc](../../weft/soc.md) and [top-level audit](audit/notes-top_corpus.md). This is track 4, not a prerequisite for useful Chrome/native tools.

**Question and usefulness:** Does a minimal emulated kernel improve isolation, bounded scheduling and recoverability for one cell workload compared with an existing-OS sandbox?

**Baseline:** a scoped existing-OS process/Wasm harness with the same capability contract. **Manipulated variable:** one selected emulated ISA/kernel boundary. **Fixed factors:** toy workload, denied actions, scheduling quantum, budget, IPC protocol and state/recovery criteria. Do not compare a weaker sandbox with a differently privileged kernel and attribute all differences to architecture.

**Measurements:** boot reproducibility, allowed/denied accesses, quota exhaustion, scheduler fairness, deterministic crash recovery, IPC correctness and trusted computing base size. Fault-inject malformed requests and killed workers. A successful emulator boot does not establish Apple native boot or hardware security.

**Falsifier/stop:** cell escapes assigned capabilities, failures corrupt adjacent state, the kernel adds no demonstrable benefit relative to the simpler harness, or architecture-specific reset assumptions are invalid. Native privileged code is outside this pilot.

**Initial resource bound:**2 virtual CPUs,1 GiB guest RAM, a 2 GiB disk image and ten-minute boot/workload runs; one emulator instance. **Prerequisites:** select ISA and emulator, explicit memory/capability/scheduling spec, existing-OS baseline, issue naming prototype path and coordination with existing OS owners before cross-repo work. **Retain/output:** boot image/hash, toolchain, serial traces, fault fixtures and capability matrix under `experiments/E11/`; advance to native-device feasibility only after the comparison justifies it.

## E12 — Does a hardware comparator or Terrafab loop beat an equal-work baseline?

**Source intent:** [terrafab](../../weft/terrafab.md), especially 86–87 and 161–187; [terrafab-calc](../../weft/terrafab-calc.md), [soc](../../weft/soc.md) and [top-level audit](audit/notes-top_corpus.md). Author asks for measurable gains and a closed manufacturing/energy/compute loop. These are two related but distinct experiments.

**Question A:** can one finite-precision invariant comparator or graph-reduction tile meet its exact software contract with a plausible area/timing/energy tradeoff? **Baseline:** optimized CPU implementation on the same inputs. **Manipulated variable:** comparator datapath/precision or tile rule implementation. **Fixed factors:** task, input corpus, accepted semantics and work performed. **Measurements:** functional parity, overflow/rounding behavior, simulated cycles, synthesis area/timing if a selected target is available; label energy estimates by model and uncertainty. **Falsifier:** disagreement at any required boundary, or advantage disappearing when baseline work is equal. Injected sleeps are not a valid CPU comparator.

**Question B:** under which assumptions can a manufacturing feedback loop increase useful output per energy/resource cost? **Baseline:** fixed scheduling/control on the same plant/demand model. **Manipulated variable:** control policy; **fixed factors:** demand, energy, material constraints, failure rates and model assumptions. **Measurements:** throughput, yield, energy/material consumption, control stability and sensitivity to uncertain costs. **Falsifier:** gains depend on impossible units, ignored capital/delay or favorable-only assumptions.

**Initial resource bound:** software simulation only, one small comparator/tile,4 GiB RAM target and 30 minutes per simulation/synthesis trial; plant simulation limited to an explicitly bounded toy scenario. No FPGA purchase, fabrication or live industrial actuation. **Prerequisites A:** E10 finite numerical/graph contract and a selected simulation target. **Prerequisites B:** dimensionally consistent plant/resource model, cited input assumptions, stable baseline controller and independent equal-work accounting; B does not require the IC proof, FPGA or new chip. **Retain/output:** vectors, RTL/model, synthesis/simulation reports, sensitivity tables and rejected assumptions under `experiments/E12/`; technical whitepaper. FPGA access, hardware-in-loop, industrial pilot and fabrication are separate resource/owner gates.

## E13 — Do executable permissions match the proposed constitution, and what remains social?

**Source intent:** [splicers genesis](../../weft/browser-sources/thread1-splicers-genesis-90133B.md), turn 7; [govern](../../weft/govern.md), [constitution-versus-contract note](../design-notes/constitution-vs-contract.md), [runtime audit](audit/notes-runtime.md) and [#44](https://github.com/Moissanite-Labs/weft/issues/44). This card separates ledger mechanics, authority policy and institutional legitimacy.

**Question and usefulness:** Can a chosen local policy enforce consent, delegation, revocation, independent approval, appeal and reproducible accounting for the exact actions it governs?

**Baseline:** current Python gateway plus actual locally compiled Solidity, and a token-free signed event journal. **Manipulated variable:** accepted policy/role design or economic mechanism; evaluate separately. **Fixed factors:** same action traces, identities/keys, integer units/rounding, initial balances/state, transition ordering and failure outcomes. Do not silently choose disputed rounding, attribution or dual-signature semantics.

**Measurements:** simulation/EVM parity for balances/events/reverts, unauthorized-action rejection, role compromise cases, replay/nonce behavior, consent revocation, appeal/succession scenario outcomes, and whether a participant can inspect/contest a decision. A human+agent signature may still share one controlling authority; model that trust assumption explicitly.

**Falsifier/stop:** stated policy can be disabled by an unnoticed privileged path, failed action leaves mutated state, provenance registration can be mistaken for ownership, a participant cannot revoke/appeal as specified, or the token-free baseline meets the need with less complexity. Successful local tests do not settle legal standing, fairness, adoption or political legitimacy.

**Initial resource bound:** local ephemeral chain only, no keys with real funds, at most 1,000 bounded action traces,4 GiB RAM target and 30 minutes per run. **Prerequisites:** Solidity compile/test setup, explicit normative decisions, declared trusted computing base and representative stakeholder scenarios. **Retain/output:** policy version, contract/compiler hashes, traces, counterexamples and contested alternatives under `experiments/E13/`; executable conformance and constitutional research note. Public deployment, real money, organizational adoption and succession policy each require a separate concrete decision.

## How results change the program

For each card, conclude one of: **implement** (measured utility and contract satisfied), **iterate** (bounded unresolved issue with next test), **research** (definitions/evidence missing), **retain as an alternative** (useful under different conditions), or **defer behind an external gate**. A failed implementation does not erase the author's goal; it identifies which mechanism did not establish it. A compelling demo does not skip the other gates.

No experiments, model downloads, human studies, privileged operations, chain deployments or external measurements were performed to write these cards. They are ready-to-scope protocols; execution reports must name their actual environment and outcomes.
