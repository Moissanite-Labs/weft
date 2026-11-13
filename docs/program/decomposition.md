# Proposed decomposition: codebases, documents, boundaries

Status: **proposal**, for Discussion #11 and PR #12. This document creates no trees. Per PROGRAM.md, a path is scaffolded only once a filed issue names it. Scaffold issues filed so far: #23 (C2 invariants). The others are filed when their turn in §7 comes, so no path is named before work can start on it.

Evidence: [`../corpus/README.md`](../corpus/README.md) §3 (12 distinct systems after de-duplication) and [`../corpus/claims-register.md`](../corpus/claims-register.md).

## 1. Principles used to draw boundaries

1. **Separate problems, separate codebases.** Code that solves a different problem, uses a different toolchain, sits behind a different trust boundary, or is likely to need a different license or governance later gets its own codebase.
2. **Share code only where the logic really is shared.** Today one rule set is used in several places: the safety invariant (drift from a stored baseline, metabolic budget, tension threshold). It appears in Python, C, Lean, and Solidity in the corpus. That is the one proposed shared library. Everything else talks through **interfaces**: data formats with conformance vectors. It does not talk through imports.
3. **Interfaces are files, not conventions.** Each cross-codebase contract gets a spec under `docs/interfaces/` and a set of golden test vectors that every implementation must pass. The SYM-2P fix in PR #12 (#13) shows the pattern: one golden line, asserted by Python and by Node.
4. **Every claim stays falsifiable.** A codebase README states what is implemented and what the vision name aims for. Biological names stay as vision language (#6, PROGRAM.md), but no README claims an implementation has arrived before the tests show it.
5. **Built to split cleanly.** Each codebase has one owner team ([`teams.md`](teams.md)), its own README, tests, and build. It has no relative imports into another codebase. When separate repos come, each can move with `git filter-repo` and nothing breaks except the vendored interface vectors.

## 2. Codebases

Today the runtime lives in `weft/runtime/{core,aywa,mac,ledger}` and the site in `docs/`. The proposal regroups that code by problem. Moves happen one codebase at a time, each in its own PR, with the old selftests kept green throughout.

| # | Codebase (proposed path) | Purpose | Boundary (in / out) | Depends on | Comes from |
|---|---|---|---|---|---|
| C1 | **plasm**, `weft/runtime/plasm/` | Shared-memory substrate (focal, sympathetic, and hippocampal regions) and the α/β mitosis harness: speculative lineages, selection, consolidation, teardown. | **In:** the shm layout, cell lifecycle, selection, consolidation, MPS/CPU backends. **Out:** network, chain, telemetry collection, UI. | C2 (gate), I3 (host telemetry frame, optional) | `core/weft_plasm.py`, `mac/metal_loom.py` (the same loop in a single process) |
| C2 | **invariants**, `weft/runtime/invariants/` | The safety gate as pure functions: drift from a stored baseline, the remaining-budget precondition, the tension bound, NaN rejection. Python reference, C header, JSON conformance vectors; Lean later. | **In:** pure predicates and their vectors. **Out:** I/O, state, policy dials. | none | `weft_plasm.verify_weight_update_safety` (#2, #7); `weft_invariants.h` (corpus, with the M6 fix) |
| C3 | **ic**, `weft/runtime/ic/` | The interaction-combinator VM and the Weft graph language: node set, rewrite rules, net serialization (BCP), trace commitment. | **In:** reduction, serialization, commitments. **Out:** torch, weights, tokens. VLV's budget effect is expressed through C2, not through ledger calls. | C2 (for VLV only) | `core/weft_ic_vm.py`; corpus VLV/FRC/SUP once specified (PROGRAM.md Phase 4) |
| C4 | **ledger**, `weft/runtime/ledger/` (exists) | The Solidity triad (ProvenanceRegistry, WeftTokenTissue, TensionGovernor), with Foundry tests on a local chain only. | **In:** contracts, ABI, tests. **Out:** keys, RPC, deployment. | I6 (ABI is its output) | `ledger/*.sol`; TensionGovernor from `weft/README.md:269-383` |
| C5 | **gateway**, `weft/runtime/gateway/` | Off-chain bridge: deploy to a local devnet, submit fracture reports, monitor events. The only code that ever holds a key, and only from the environment. | **In:** RPC client, signer from env, event decoding. **Out:** contract source, runtime state. Local devnet by default; a human approves anything else. | C4 via I6 only; C2 (threshold vectors) | corpus `deploy_loom.py`, `monitor_excision.py` (with the L7 fix) |
| C6 | **telemetry**, `weft/runtime/telemetry/` | Everything that *produces* telemetry: host metrics (Darwin sysctl/Mach, an honest Linux path), the org harvester (real GitHub API, optional, rate-limited), the 64-byte frame encoder, and the SYM-2P encoder. | **In:** collection, encoding, the conformance vectors for I1 and I2. **Out:** rendering, shaders. | none | `aywa/{github_harvester,sym2p_codec,weft_daemon}.py`, `mac/darwin_sysctl.py` |
| C7 | **aywa**, the browser organism (today `docs/`; proposed own directory, see #19) | Static Pages site: WebGPU/WGSL renderer, workers, SYM-2P parser, style mixer, GPU text, widgets gallery. | **In:** everything that runs in the visitor's tab. **Out:** collection and harvesting (C6), write-back (C9, deferred). | I1, I2 (consumes C6 output) | `docs/`, `aywa/index.html`, `aywa/dashboard_layout.wgsl`, `browser-sources/widgets/` |

### Proposed but deliberately **not** scaffolded yet

| # | Candidate | Why it waits | What unblocks it |
|---|---|---|---|
| C8 | **mesh**: exo-mitosis transport, peer handshake, beacon, fd-passing tool membrane | Every corpus variant is unauthenticated (S8). It sends whole weights, not deltas, and it overlaps with the self-exfiltration pattern (S9). | A protocol RFC with authentication, consent per migration, and localhost-default binding, plus a governance decision on S9. |
| C9 | **write-back**: OAuth device flow, profiles ledger, "stigmergy" | Token exposure through a third-party proxy, scope, and commits to main (S12). Visitors would need push access. | A threat model; probably an issue-form → Action or fork-and-PR design instead. |
| C10 | **classifier**: "Laya System 1", in-tab ONNX | Unverified model, a 210–420 MB asset against Pages limits, behavioural-telemetry privacy (S16). | A privacy note, a model that can be verified, a size budget. |

### Not codebases (vision or roadmap only)

These are kept as named ideals, but none has code worth extracting:
- bare-metal boot and the privileged purge routine;
- the no-filesystem MMIO tier;
- the Haptic Governor hardware;
- the fan/SMC actuator;
- the Weft chip and Terrafab;
- the eternal imprint and perception engines;
- the post-economic harness (a configuration of C1);
- the Bend kernel;
- the latency "proof" benchmark.

Each becomes a roadmap branch (§4) with its dependencies, not a directory.

### `weft/runtime/mac/` dissolves

`metal_loom.py` is the same mitosis loop as `run_plasm_cycle` on a different backend, so it belongs in C1 as the MPS backend. `darwin_sysctl.py` produces host telemetry and belongs in C6. Keeping a platform-named codebase would split one problem (the harness) along a hardware line.

## 3. Defending the contested boundaries

- **C1 vs C2: why the gate is not inside plasm.** The same predicate is meant to guard weight consolidation (C1), the VLV token effect (C3), on-chain fracture thresholds (C4/C5), and firmware actuation (the corpus C header). The corpus already has four copies that disagree (M6, M7: ≤85 vs <85, a budget that can go negative). Keeping one reference implementation plus vectors is the only way to make "the executable path actually checks the stated rule" (PROGRAM.md) testable across languages.
  - *What would change this:* if, after Phase 4, only C1 uses the gate, fold C2 back into C1.
- **C1: bus and harness together.** The bus layout exists only to serve the harness, and no second consumer exists. Splitting them would create an interface with one user.
  - *What would change this:* a second consumer of the shm layout (for example C3 reading the focal register, or a native cell). The layout spec (I4) is written anyway, so the split stays cheap.
- **C4 vs C5: contracts apart from the gateway.** They use different toolchains (Solidity/Foundry vs Python/web3), different trust (C5 alone can hold a key), and probably different licenses later. Merging them would put key-handling code in the same tree as code meant to be audited and published.
- **C6 vs C7: producer apart from consumer.** Today `weft/runtime/aywa/` mixes harvesting (Python, needs a token) with rendering (JS, runs in the tab). The 64-byte frame and SYM-2P line are the contract between them. The codec bug (#13) came from producer and parser living apart with nothing holding them to the same bytes. The fix is shared vectors, not shared code.
- **C3 apart from C1.** The IC VM is a different computation model with no torch dependency. Its open questions (PROGRAM.md Phase 4: a precise statement of the variant, an execution record that includes the graph) are research problems that do not touch weights.
- **Widgets inside C7.** They are presentation and run only in the tab. The NCA "evidence bar" (PROGRAM.md: Distill-2020-style persistence and damage metrics) would be a research codebase of its own if pursued. That is a roadmap branch, not a widget.

## 4. Documents

Each document is checked against the code it describes. A document that disagrees with the code is a bug in one of them, filed as an issue.

| Document | Path (proposed) | States | Draws on |
|---|---|---|---|
| Mission | `docs/mission.md` | The purpose that outlasts any one implementation | `ethos.md`, `process.md` (the "design cadence" five patterns), PROGRAM.md, #6 comment |
| White paper W1: models as cells | `docs/whitepapers/models-as-cells.md` | Premises, mechanism (speculative lineages under a baseline-distance gate), predictions, limits | #5, #6, `almalga.md` §1–5, C1/C2 tests |
| W2: interaction-combinator substrate | `docs/whitepapers/interaction-combinators.md` | The variant precisely stated; what reduction does and does not guarantee | `ult`, `langdoc`, `pcoom`, `mugetsu`, `weft_ic_vm.py`, M8/M9 |
| W3: provenance and the economic valve | `docs/whitepapers/provenance-and-valve.md` | Watermark threat model (#4), ledger economics, L1–L6 | README §15, `ethos.md`, `spread.md` |
| W4: the organism interface | `docs/whitepapers/organism-interface.md` | Telemetry to geometry; the "honest translation" of sci-fi phrasing into real APIs | `craft.md:54-99`, `build.md:9-17`, `anew.md` |
| W5: constitution vs contract | `docs/design-notes/constitution-vs-contract.md` | Gap between the stated rules (human approval, dual signature) and the single-key contracts (L4) | PROGRAM.md Phase 3, `govern.md`, the triad |
| Technical documents | `docs/tech/<codebase>.md` | Architecture, interfaces, invariants, failure modes, per codebase | the codebase and its tests |
| Interface specs | `docs/interfaces/I1…I7.md` | Byte-level contracts plus conformance vectors | §5 below |
| Wiki (operating memory) | `docs/wiki/` | How the systems fit, how to contribute, the decision log (`docs/wiki/decisions/NNNN-*.md`) | this file, [`teams.md`](teams.md) |
| Roadmap | `docs/roadmap.md` | The full branching space, with dependencies and the order in which branches become possible. No early pruning. | §6 below, the vision-only list in §2 |
| Glossary | `docs/glossary.md` | Each vision name, the ideal it names, and what currently implements it | `craft.md:62-68` template, PROGRAM.md |
| Vision essays | `docs/vision/` | Labelled as vision: the Document Prison manifesto, the Post-App World, the Mind Palace explainer, post-mortal intent | `anew.md`, `feel.md:33-89`, `bio.md`, `imprint.md` |

Per PROGRAM.md, the GitHub Wiki is not used; the "wiki" is a directory reviewed by pull request.

## 5. Interfaces between codebases

| ID | Contract | Producer → consumer | Status |
|---|---|---|---|
| I1 | 64-byte telemetry frame (`16 × f32` little-endian; slot 2 relative clock in `[0, 2^23]` s, wall-clock integer outside frame) | C6 → C7, C1 | Specified in [`docs/interfaces/I1-frame64.md`](../interfaces/I1-frame64.md) and enforced in `frame64.py` (#78). The JS writers (`weft-loom.js`, `telemetry-worker.js`) do not enforce `[0, 2^23]`. |
| I2 | SYM-2P line (role byte, action byte, decimal sequence, s-expression, SHA-256) | C6 → C7 | Fixed and vector-tested in PR #12 (#13). The key vocabulary is still unsettled (`tension`/`gini` vs `con`/`owner`/…). |
| I3 | Safety gate API plus conformance vectors | C2 → C1, C3, C5, C4 (constants) | Python reference exists. Vectors to be written. |
| I4 | Plasm shm layout `[4,64,512]` / `[4]` / `[8,512]` | C1 → cells, daemon | Stated in `WEFT-ARCHITECTURE-LOCK.md`. No spec file. |
| I5 | IC net serialization (BCP) and trace commitment | C3 → C4 (commitments), C8 | The corpus gives no field widths (`thread1:4629-4645`). |
| I6 | Ledger ABI and events (topics computed, not hand-written; see L7) | C4 → C5 | Not yet generated. |
| I7 | Weight hash / commitment scheme (`weightHash`, `genotypeRoot`, trigger/target commitments) | C1 → C4/C5 | **Undefined anywhere in the corpus** (`sources/B` §6). Blocks any real provenance claim. |

## 6. Roadmap branches (seed list; the full roadmap is a later document)

Every direction the corpus opens, with its prerequisites. No branch is pruned here.

- **Substrate:** native Metal kernels for C1 · a shared-memory layout shared with C3 · Hebbian consolidation that is actually use-dependent (M2) · selection that scores what it commits (M1).
- **Language:** a precise IC variant (Phase 4) → VLV/FRC/SUP semantics → a typed graph language → a parallel reducer (HVM-style) → "proof is the graph" (M15), which needs a type system and checker first.
- **Verification:** Lean proofs of the C2 predicates linked to the code via vectors → Lean for IC rewrite confluence.
- **Provenance:** the I7 commitment scheme → a watermark threat model (#4) → ledger economics fixes (L1–L6) → local-devnet integration tests → (owner-gated) any testnet.
- **Interface:** an honest live harvester → GPU text → mixer controls → a reading-reward layout → an in-tab classifier (C10) → the site as protocol interpreter (`craft.md:13-31`).
- **Mesh:** a protocol RFC → authenticated localhost mesh → LAN → consented migration (C8).
- **Hardware (vision):** bare-metal boot · no-FS tier · haptic console · Weft chip / Terrafab. Each needs hardware access no current contributor has.
- **Governance:** constitution vs contract (W5) → dual-signature on the executable path → a trusted-computing-base statement → consent, appeal, and succession (PROGRAM.md Phase 5).
- **Organization:** separate repos per codebase (§1.5) → per-codebase licenses → per-team governance.

## 7. Order of work proposed

1. This map and proposal (PR #12), plus issues for every evaluation.
2. Go-public blockers (#27: #14, #15, #19, #24). These are small, and they gate the owner's stated next step.
3. C2 invariants (#23, vectors first), because C1, C3, and C5 all depend on it.
4. C6/C7 split along I1/I2, with vectors. This finishes the Pages seed honestly (the 43-item design checklist in `sources/A` §5.2).
5. C4 TensionGovernor extraction plus the economics issues (#20), with Foundry tests on a local chain.
6. C1 move (absorbing `mac/metal_loom.py`), then C3 after the Phase 4 IC description (#21).
7. White papers W1–W5, each written against the code at that point.
