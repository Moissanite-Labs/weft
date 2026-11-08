# Weft corpus map

Status: first full pass, 2026-11-07, for Discussion #11 ("Weaving"), PR #12.
Line numbers refer to `main@f67d9dc`.

**Planning addendum, 2026-11-08 (#39):** this is a dated inventory, not a current capability report. Use the [variant and lineage register](../program/variants.md) to compare implementations and the [convergence plan](../program/convergence-plan.md) for current evidence and sequencing. Preserve the original transcripts and historical source reports. Repetition can preserve a different assumption, stack or stage of a design; assess that context before choosing, combining or retiring a variant.

This directory maps every Markdown file under `weft/`: what each file is, where it came from, which code it holds, and what it claims. It is the evidence base for the proposed decomposition in [`../program/decomposition.md`](../program/decomposition.md). Read it before scaffolding a codebase or writing a white paper from the corpus.

| File | What it holds |
|---|---|
| [`claims-register.md`](claims-register.md) | Cross-source register of mechanisms, claims, contradictions, and falsifiers. Each entry marked VERIFIED was re-checked for PR #12. |
| [`safety-index.md`](safety-index.md) | Locations of sensitive material: passphrase literals, key handling, live-deploy prompts, fabricated receipts, unauthenticated listeners. **No values are reproduced.** |
| [`sources/`](sources/) | Eight first-pass inventory reports, one per slice of the corpus. They give per-file summaries, code-fragment tables, claims, candidate systems, implied documents, and gaps. |

## 1. What the corpus is

The corpus is about 2.5 MB of Markdown in 64 files. Almost all of it is **pasted chat transcripts from Google Search "AI Mode" (Gemini)**, not design documents written by the team. Evidence: the "Share / Good response / Bad response… Google may use account and system data" footer, search-result dump turns, and leaked routing tags such as `[candid]` and `[filegen-via-code]`. See `sources/E` §1.1 and `sources/D` §0.

Only three Markdown files are the team's own writing: `weft/MOISSANITE-SYNTHESIS.md`, `weft/WEFT-ARCHITECTURE-LOCK.md` (both dated 2026-11-07), and `weft/browser-sources/README.md`.

There are three source sessions. Every other file is a copy or slice of one of them:

| Source transcript | Lines | Copies elsewhere in the corpus |
|---|---|---|
| `browser-sources/thread1-weft-main-84ADC9.md` (72 turns) | 8,257 | One turn per file: `almalga`, `launch`, `test`, `deploymap`, `manifest`, `ainterface`, `wrap`, `perception`, `ethos`, `govern`, `soc`, `prove`, `provocol`, `whoa`, `penult`, `ult`, `spread`, `langdoc`, `xtra`, `pcoom`, `mugetsu`, `self`, `imprint`, `dissertation-mac`, `terrafab`, `terrafab-calc`, `terraweft`, `ahraz`, `whitepaper`, `process`. The full turn map is in `sources/E` §1.2; the order of the D-slice files is in `sources/D` §0. |
| `browser-sources/thread2-design-main-6C083A.md` | 5,135 | All 19 files of `weft/design/`, as contiguous slices in this order: arrival → art → alive → bio → create → feel → converge → anew → craft → done → eh → build → custom → combine → baryonic → discovery → feeed → core → aywa (`sources/A` §1). |
| `browser-sources/thread1-splicers-genesis-90133B.md` (29 turns) | 4,103 | Repeated almost verbatim as lines 8–4105 of `missing-turns-supplement.md` (`sources/G`, `sources/H`). |

Outliers that come from none of the three sources:
- `weft/more.md`: x86 ring-0, NCCL, and the Haptic Governor, from an earlier session (`sources/D` §0).
- `weft/README.md` §15–24: its distinctive identifiers (`CompleteUnifiedBiomatrixBus`, `PeerHandshakeMatrix`, `apic_timer_interrupt_vector`) appear in no preserved transcript. This is a **provenance gap** (`sources/B` §6).
- `weft/mac.md`, `weft/tune.md`, `weft/emergent.md`, and others in `sources/C` partly overlap the thread1 transcript. `sources/C` §1 gives the per-file details.

`missing-turns-supplement.md` adds **no new content**. Its 43 turns (the header and README say 31) are all verbatim copies from the three transcripts, and 9 of them are empty, error, or search-dump turns (`sources/H` §1).

### Consequences for the build

1. **Compare variants by lineage, assumptions and evidence.** The transcripts show each program evolving and branching across different stacks and goals. §3 records late variants as navigation aids, not automatic winners. Use the [variant register](../program/variants.md), preserve meaningful alternatives, and record why an implementation is selected or repaired.
2. **Narrated execution is not evidence.** From thread1 Turn 30 onward, the assistant role-plays execution. It prints invented terminal output and claims contracts were "sealed on-chain". The transcript itself concedes, at `thread1:6566-6568` and `emergent.md:96-98`, that nothing exists outside the chat. The contract addresses it quotes are the default addresses of a fresh local Hardhat/Anvil devnet (`sources/C` §3, `sources/E` §3.3). PROGRAM.md already says a simulated receipt is not evidence. This map identifies where those receipts are.
3. **External "facts" require dated verification.** The original inventory did not establish the availability or stated behavior of GPT-6 Astra, jev-ui, Inkling 2 on Tinker, Laya, two arXiv IDs, or the reported OS name "macOS Golden Gate 27.0.1". This is not evidence of their absence. See `sources/A` §3.6, `sources/G`, and `sources/D` §0 for the historical findings. For the owner's current device report, record `sw_vers` and runtime probes as described in [use-now.md](../program/use-now.md), rather than substituting a version or inferring compatibility.
4. **Possible name clash.** The transcripts attribute the name "Weft" to Luca Berton's Weft language (`thread1:4441-4452`). The search results also show WeaveMindAI/weft. The genesis thread instead derives the name from the user's loom metaphor (`splicers:133-154`). This needs a recorded decision before the project goes public.

## 2. Counts

| Slice | Files | Lines read | Software fragments | Candidate systems |
|---|---|---|---|---|
| A: `weft/design/` | 19 | ~4,000 | 36 | 12 |
| B: README, almalga, launch, imprint, terrafab*, terraweft, team docs | 9 | 4,300 | 21 | 15 |
| C: dissertation-mac, mac, xtra, whitepaper, self, soc, tune, ahraz, test, emergent, deploymap, govern | 12 | 3,229 | 14 | 16 |
| D: ainterface … wrap | 16 | 2,215 | 15 | 11 |
| E: thread1-weft-main | 1 | 8,257 | 37 | 17 |
| F: thread2-design-main | 1 | 5,135 | 38 | 10 |
| G: thread1-splicers-genesis | 1 | 4,103 | 15 (9 program versions) | 9 |
| H: missing-turns-supplement | 1 | 4,656 | 17 (all duplicates) | 11 (all duplicates) |

The fragment counts overlap heavily because the per-turn files duplicate the transcripts. The `corpus_audit` in `weft/runtime/core/selftest.py` counts 365 fenced blocks across 63 files, and 91 of those are Python blocks that parse.

## 3. Distinct systems after de-duplication

The candidate systems from the eight reports were grouped as follows at the inventory revision. Each "latest variant" is the most recent version in transcript order, not a recommendation to discard its predecessors. The "In repo today" column describes that historical revision; consult the current evidence and variant registers before treating it as present state.

| # | System (corpus name) | Latest corpus variant | In repo today | Shares logic with |
|---|---|---|---|---|
| 1 | **Plasm**: shared-memory bus with focal, sympathetic, and hippocampal regions | `thread1:7674-7977` (`weft_singularity_core.py`) | `weft/runtime/core/weft_plasm.py` (repaired, diverged) | 2, 3 |
| 2 | **Mitosis harness**: α/β LoRA speculation, selection, consolidation | the same file; the most complete is splicers v8 `3305-3660` | `weft_plasm.run_plasm_cycle`, `weft/runtime/mac/metal_loom.py` | 1, 3, 6 |
| 3 | **Safety invariant / Tension Grid gate** (Python prover, Lean, C header) | `weft_invariants.h` `thread1:7429-7511` | `weft_plasm.verify_weight_update_safety` (#2, #7) | 1, 2, 5, 7 |
| 4 | **Interaction-combinator VM and Weft graph language** (ERA, CON, DUP, VLV, FRC, SUP) | `ProductionWeftLoom` `thread1:6864-7037` (a toy, not Lafont) | `weft/runtime/core/weft_ic_vm.py` (a real Lafont VM with ERA/CON/DUP only) | 3 (VLV budget) |
| 5 | **Ledger triad**: ProvenanceRegistry, WeftTokenTissue, TensionGovernor | `weft/README.md:42-383` (V1, the most complete) | two of the three contracts in `weft/runtime/ledger/` (**TensionGovernor missing**) | 6, 3 |
| 6 | **Ledger gateway**: deploy, report, monitor (web3.py) | `deploy_loom.py` `thread1:1004-1322`, `monitor_excision.py` `6062-6163` | none | 5 |
| 7 | **Watermark and royalty valve** (trigger/response) | inside #1/#2 variants | seed only (`weft_plasm.py:190`) | 2, 5 |
| 8 | **Host telemetry** (Darwin sysctl/Mach, org harvester) and the **SYM-2P codec** | `darwin_parser.py` `thread1:1808-1958`; harvester `thread2` Turn 40 | `weft/runtime/mac/darwin_sysctl.py`, `weft/runtime/aywa/{weft_daemon,github_harvester,sym2p_codec}.py` | 9 |
| 9 | **Aywa**: WebGPU organism site, workers, mixer, GPU text, widgets | Turn 41 `SovereignSystemCore` `thread2:4585-4989` | `docs/` Pages seed, `weft/runtime/aywa/index.html`, `weft/browser-sources/widgets/` | 8 |
| 10 | **Mesh**: exo-mitosis transport, handshake, beacon, fd-passing tool membrane | splicers v8/v9; `README` §17/§21 | none | 2, 5 |
| 11 | **Git write-back with OAuth device flow** (stigmergy) | `discovery.md`, `core.md` | none (deferred) | 9 |
| 12 | **Behavioural classifier** ("Laya System 1", ONNX in-tab) | `alive.md`, `craft.md` | none | 9 |

The following are **vision or roadmap only**. They have no runnable code worth extracting:
- bare-metal boot and the privileged purge routine;
- the no-filesystem MMIO tier;
- the Haptic Governor hardware;
- the fan/SMC actuator (simulated);
- the Weft chip and Terrafab;
- the eternal imprint and perception engines (hard-coded constants);
- the post-economic harness (a configuration variant of system 2);
- the Bend kernel;
- the latency "proof" benchmark (a rigged comparison).

The proposed codebases built from this table are in [`../program/decomposition.md`](../program/decomposition.md).

## 4. How to extend this map

- When you find something new, add it to `claims-register.md` with a location and a falsifier. Open an issue if it is actionable.
- Never paste secret-like values into this directory. Cite them as `file:line` in `safety-index.md`.
- If a source report is wrong, correct it in place and note the correction in the commit message. The reports are working documents, not a record.
