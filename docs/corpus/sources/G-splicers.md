<!--
Corpus map source report G. Scope: weft/browser-sources/thread1-splicers-genesis-90133B.md.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# G-splicers: inventory of `thread1-splicers-genesis-90133B.md`

Scope: `/home/user/weft/weft/browser-sources/thread1-splicers-genesis-90133B.md` (4103 lines, read in full), plus `/home/user/weft/weft/browser-sources/README.md` for context. Repo comparison targets: `weft/runtime/core/weft_plasm.py`, `weft/runtime/mac/metal_loom.py`, `weft/runtime/mac/darwin_sysctl.py`, `weft/runtime/aywa/weft_daemon.py`.

Short form used below: `G:<line>` means a line in the transcript.

---

## 1. Per-file summary

### 1.1 `weft/browser-sources/thread1-splicers-genesis-90133B.md` (4103 lines)

**What kind of file it is.** A scraped transcript of a Google AI Mode chat (29 turns, Turn 0 to Turn 28). Every turn ends with the "ShareGood responseBad response…" UI text, which is page clutter. It is the **genesis dialogue** of the Weft corpus. It starts with *Destiny* game lore (Fallen/Eliksni Splicers, Namrask's loom, Strand) and turns that into a software philosophy: the "Agentic Software Loom" (ASL). That philosophy then becomes a "cellular weight-space collective" and finally a chain of nine Python prototypes, each one building on the last. Turn 27 is a manifesto/spec ("ARCHITECTURAL SPECIFICATION: THE AGENTIC SOFTWARE LOOM") and Turn 28 adds a distributed/mesh section.

**Main topics:**
- Loom metaphors: Warp, Weft, "Heedle" (almost certainly a misspelling of *heddle*), Shuttle, Tapestry.
- The Tension Grid safety layer: dampening, vector shift, Edge Snap.
- An autonomy dial plus a cryptographic audit log, the "Paracausal Loom Ledger" (PLL).
- Weight-space programming and the idea that "weights are applications, the OS is the harness".
- Cells: nucleus, membrane, plasm, mitosis, apoptosis.
- POSIX shared-memory tensor buses, process "membranes", A/B mitosis, novelty scoring, fd injection via SCM_RIGHTS, a stratified bus (focal / sympathetic / hippocampus), a rank-2 LoRA plasticity mask, consolidation plus decay, a terminal "jev-ui" dashboard, psutil telemetry, and a UDP mesh.

**Extraction artefacts.**
- MathML was scraped as doubled text, e.g. `Tcap T⁠` (G:317, G:441) and the formula lines G:1901, G:3159, G:3167, G:3211, G:3217, G:3221, G:3271, G:3275, G:3289.
- Some values were lost entirely: G:3273 "(⁠)" and G:3295 "the precise ⁠ parameter adjustments".
- Empty `*` bullet lines appear throughout.
- A stray "POCGo to product viewer dialog for this item." at G:1447.
- `[candid]` markers at G:506, G:794, G:881, G:1014, G:1670, G:2214.

**Duplicate.** The file is reproduced **verbatim** in `weft/browser-sources/missing-turns-supplement.md` lines 8–4105. Apart from the turn-header format (`## Turn N:` vs `## [90133B Turn N]`), a `diff` of G:6-4103 against supplement:8-4105 is empty. Mapping agents for the supplement should not double-count these fragments.

**README discrepancies.**
- `README.md:7` says this tab has "29 turns, 40 `<pre>` blocks". The file has **34 fenced blocks** (19 `text`, 15 `python`).
- The README says the thread runs "through the full multi-node Mac harness". The file actually ends with a generic `psutil` + UDP harness (Turn 28). It contains nothing Mac-specific: no MPS, no sysctl, no M1 Max. The Mac harness lives in `thread1-weft-main-84ADC9.md`.
- `README.md:18` attributes widget 05 (Interaction Combinator net) to "Desktop 8, Turn 21". Turn 21 here is the Python novelty harness, and interaction combinators are never mentioned in this file. `thread1-weft-main-84ADC9.md` has its own Turn 21 (Lean/Bend, line 4077), which mentions interaction nets.
- `docs/` contains nothing from this file.

### 1.2 How the design evolved (which variant is the latest)

| Turn | Lines | Stage | Key additions / changes |
|---|---|---|---|
| 0–2 | G:6–127 | Lore | Splicers, SIVA, Splicer Gauntlet, Namrask's loom, Ada-1's Loom, Strand. |
| 3 | G:131–187 | **Pivot** | Code as topology. Warp = invariants, Weft = adaptive agents. "Re-weave" instead of refactor. Symbiotic tuning. Multi-armed concurrency becomes multi-agent orchestration. |
| 4 | G:191–278 | ASL blueprint | Four layers: Warp / Weft (Shuttle, Logic Threads, Resonance Loops) / Heedle (intent mapping) / Tapestry (ephemeral execution, "unraveling"). |
| 5 | G:282–349 | Tension Grid | Kinetic Boundary Dampening (exponential token cost), Structural Vector Shifting, Edge Snap (yield point, clean severing), haptic "Splicer Interface". |
| 6 | G:353–421 | Trade-offs | Memory paradox, compounded non-determinism, dampening as an economic DoS vector, Edge Snap destroys work, human-in-the-loop fatigue. |
| 7 | G:425–500 | Governor + ledger | Autonomy continuum with thresholds T<0.3 / 0.3–0.7 / ≥0.7. PLL block carries AI% vs human% plus a dual signature. "Deterministic re-weaving" for debugging. |
| 8–9 | G:504–598 | Meta + prior art | Cites DARPA IDAS, FAST, AutoGen, Wasm sandboxing, the "Sys" EDA framework and HACI. Says "the entity that builds a compiler … topological math … first true Splicer". |
| 10–12 | G:602–875 | Weight-space turn | User-supplied claims (GPT-6 Astra, jev-ui, Inkling 2/Tinker). The Tension Grid becomes a weight-hypersphere clamp. The PLL stores weight diffs. "Apps → behaviours", "weights as applications, OS as harness" (Perception Matrix / Weft LoRA layer / Tension Grid / Tapestry). |
| 13 | G:879–925 | Reality check | Admits that haptic tension is "pure engineering sci-fi" and that real enforcement is crypto checks, reward gates and loss thresholds. |
| 14–15 | G:929–1002 | Roadmap + recap | Build the Harness (Wasm), master intent/telemetry engineering, experiment with LoRA, merging and activation engineering. |
| 16 | G:1006–1104 | **Cells** | Cellular weight-space collective: Nucleus (LoRA expert) + Membrane (mini-harness, "given the keys to its own membrane"). **"The Plasm"** is introduced as a consensus matrix / statistical dialectic. Mitosis, apoptosis, regeneration from a "master signed ledger state". |
| 17 | G:1108–1210 | First principles | Four pillars: membrane isolation, metabolic scarcity, receptor signalling (Latent Tensor Bus), genetic stability (weights read-only, mitosis → child LoRA). Loop: polarization → reaction → mitosis → homeostasis. |
| 18 | G:1214–1440 | **Code v1** | `LatentTensorBus` (shm 128×4096), `ModelCell` processes, `TensionGridOrchestrator` (Frobenius norm > 500 triggers Edge Snap). |
| 19 | G:1444–1662 | **Code v2** | `MultiChannelTensorBus` (3×128×4096), `MitoticCell`, `EvolutionaryGovernor` A/B (mutation 0.005 vs 0.08), loss = norm to a zero target. |
| 20 | G:1666–1888 | **Code v3** (separate program) | Dynamic Tool Membrane: `send/recv_file_descriptor` (SCM_RIGHTS), `ToolMutatingCell`, `MembraneToolGovernor`. |
| 21 | G:1892–2158 | **Code v4** | Merges v2 and v3. Shrinks dims to 64×512. Novelty scoring `score = 1/‖out‖ + 0.4·novelty`. Mutation 0.005 vs 0.25. |
| 22 | G:2162–2206 | Proposals | Hippocampus memory, multi-resolution pipes (Focal Nerve / Sympathetic Current / Dialectic Field with peer-to-peer KV-cache exchange), plasticity mask with rank-1/2 LoRA. |
| 23 | G:2210–2471 | **Code v5** | `StratifiedBiomatrixBus` (focal 3×64×512, sympathetic 1×16, hippocampus 32×512), `PlasticOrganismCell` (masked rank-2 LoRA, memory bias 0.05), novelty α 0.5/0.05 switched at tension 50. **Drops** fd tool passing. The Dialectic Field is never built. |
| 24 | G:2475–2727 | **Code v6** | Hippocampus 16, `last_winner` slot, random "live telemetry" every cycle, first **jev-ui terminal dashboard**. Selection becomes **loss-only (novelty dropped)**. Cells no longer read the hippocampus. |
| 25 | G:2731–2794 | Prose | Homeostasis, behavioural speciation, autonomous tool accretion. Endpoint: a Rust/C microkernel where "the model weights become the operating system". |
| 26 | G:2798–3072 | **Code v7** | `IntelligentStratifiedBus` (hippocampus 8). Genotype persisted to `/tmp/*.npy`. Winning delta consolidated at 0.15. "Intelligent decay". Badly broken (see §2). |
| 27 | G:3076–3664 | **Spec + Code v8** | ASL Architectural Specification, sections 1–7 (manifesto). "Production reference" code puts back fd passing, novelty (α 0.45/0.02 switched at tension 40), hippocampus bias, consolidation and decay. |
| 28 | G:3668–4103 | **Spec §8–9 + Code v9 (final)** | Mesh (claims RoCE v2; the code uses plain UDP :9999) plus a psutil "Hardware Peripheral Bridge". `DistributedOrganismHarness`. Selection is **loss-only again**, even though the text says novelty is included. |

**Which variant is the latest.**
- Chronologically, **v9 (Turn 28, G:3728–4089)** is the last.
- Feature-wise, **v8 (Turn 27, G:3305–3660)** is the most complete. It is the only version with novelty, fd tool passing, hippocampus bias and consolidation/decay all together. v9 adds mesh and psutil but silently loses novelty selection.
- v7 (Turn 26) is a broken intermediate.
- None of v1–v9 runs correctly as written (§2, §6).
- The **conceptual** final form is the Turn 27 spec text (G:3078–3297) plus Turn 28 §8 (G:3670–3720).

The repo's `weft_plasm.py` is closest in spirit to v5/v8: fitness + 0.35·novelty, hippocampus depth 8 as in v7, consolidation 0.15, decay factor ≈ 0.04·0.01. `metal_loom.py` is closest to v6/v9: loss-only selection, mutation rates 0.005/0.22, decay base 0.04, consolidation 0.15. Both were heavily rewritten (see §2).

---

## 2. Code fragments

Only the 15 `python` blocks are software. The 19 `text` blocks are ASCII diagrams or equations. They are listed at the end of this section for completeness and are not counted.

Columns: location | language | identifier | what it does | completeness | already extracted? | candidate system (§4).

| # | Location | Lang | Identifier | What it does | Completeness | Already extracted? | System |
|---|---|---|---|---|---|---|---|
| F1 | G:1232–1280 | python | `LatentTensorBus` (v1, Turn 18 step 1) | Creates or attaches a `multiprocessing.shared_memory` block (128×4096 float32) with a numpy view; write/read go through torch. | fragment (part of the 3-block v1 program) | NOT EXTRACTED. Ancestor of `StratifiedAppleSiliconPlasm` in `weft_plasm.py` (diverged). | S1 Plasm bus |
| F2 | G:1290–1344 | python | `ModelCell(mp.Process)` (v1) | Child process. Attaches the bus, uses random 4096² weights, reacts when the hash of the input sum changes, writes `clamp(x@W)` back to the **same** bus. | fragment (needs F1 imports) | NOT EXTRACTED | S2 Cell / governor |
| F3 | G:1352–1421 | python | `TensionGridOrchestrator` + `__main__` (v1) | Starts N cells, polls `‖bus‖_F`, calls `trigger_edge_snap()` (terminate, recreate shm) if > 500. | near-complete once F1–F3 are concatenated | NOT EXTRACTED | S2, S8 Tension Grid |
| F4 | G:1459–1503 | python | `MultiChannelTensorBus` (v2, Turn 19) | Shared-memory bus of 3×128×4096: channel 0 = input, 1 = candidate A, 2 = candidate B. | fragment | NOT EXTRACTED. Becomes the "focal" segment from v5 onward. | S1 |
| F5 | G:1511–1559 | python | `MitoticCell(mp.Process)` (v2) | Random base weights plus a Gaussian mutation delta. Reads channel 0, writes `clamp(x@W)` to its own slot. | fragment | NOT EXTRACTED | S2 |
| F6 | G:1567–1645 | python | `EvolutionaryGovernor` + `__main__` (v2) | If ‖ch0‖ > 10, spawns A (0.005) and B (0.08), sleeps 0.1 s, keeps whichever has the lower ‖out−0‖, writes the winner to ch0, kills both. | near-complete (F4–F6) | NOT EXTRACTED | S2 |
| F7 | G:1708–1742 | python | `send_file_descriptor` / `recv_file_descriptor` (v3, Turn 20) | Passes an fd over an AF_UNIX socket using `SCM_RIGHTS` ancillary data. `recv` returns `fds[0]`, which is correct. | complete helper | NOT EXTRACTED (no SCM_RIGHTS anywhere in `weft/runtime` or `docs`) | S3 Tool Membrane |
| F8 | G:1748–1807 | python | `ToolMutatingCell(mp.Process)` (v3) | Connects to a Unix socket. When `dot(hidden, w) > 0.15`, sends `REQUEST_IO_TOOL`, receives an fd, writes one line to it. | fragment (needs F7) | NOT EXTRACTED | S3 |
| F9 | G:1813–1870 | python | `MembraneToolGovernor` + `__main__` (v3) | Binds `/tmp/harness_receptor.sock`, accepts one cell, opens `workspace_tapestry.txt` for append, sends the fd. | near-complete (F7–F9). Plausibly runs on Linux/macOS. | NOT EXTRACTED | S3 |
| F10 | G:1907–2149 | python | `MultiChannelBiomatrixBus` + `MitoticToolWeaverCell` + `NoveltyDrivenHarness` (**v4**, Turn 21) | Single file merging v2 and v3 at 3×64×512. Each cell requests an fd if `|intent| > 0.02`. Selection = `1/‖out‖ + 0.4·mean‖out−archive‖`. | complete file, but with an indentation bug in cleanup (G:2133–2143) | NOT EXTRACTED | S1+S2+S3 |
| F11 | G:2220–2459 | python | `StratifiedBiomatrixBus` (focal 3×64×512 / sympathetic 1×16 / hippocampus 32×512) + `PlasticOrganismCell` + `OrganismEcosystemGovernor` (**v5**, Turn 23) | Masked rank-2 LoRA cells add a 0.05·mean(hippocampus) bias. Selection = fitness + α·novelty vs hippocampus, with α = 0.5 if tension < 50, else 0.05. Winner's mean is pushed to the hippocampus. | complete file, same indentation bug (G:2441–2453) | NOT EXTRACTED as is. Its three-tier layout is the source of `weft_plasm.py` (diverged: 4 focal channels, 4-float sympathetic ring with thermal_c, hippocampus 8 with a ring pointer, ctypes view, single process, no cells). | S1+S2 |
| F12 | G:2483–2716 | python | `StratifiedBiomatrixBus` (hippocampus 16, sympathetic + `last_winner`) + `PlasticOrganismCell` + `UnifiedOrganismHarness.draw_jev_ui` (**v6**, Turn 24) | Writes random "telemetry" to ch0 every cycle, spawns A (0.005) and B (0.18), keeps the lower norm, redraws a terminal sparkline dashboard. | complete file. Structurally the cleanest; has a timing race. | NOT EXTRACTED. `metal_loom.py` has the same loss-only selection shape (diverged: single process, symmetric `lora@lora.T`, no mask, no shm). | S1+S2+S4 dashboard |
| F13 | G:2808–3063 | python | `IntelligentStratifiedBus` + `PlasticConsolidatingCell` + `SynapticDialGovernorHarness` (**v7**, Turn 26) | Genotype stored at `/tmp/organism_master_genotype.npy`. Cells save `lora_delta` to `*_delta_A/B.npy`. Harness computes `W ← (W + 0.15·Δ_win)·(1 − 0.01·decay·(1+1/T))`. | **broken**: `write_sympathetic` rebinds the array to scalars (G:2862–2864), `read_sympathetic` calls `float(ndarray)` (G:2867), stray `else:` becomes a for-else (G:3036), possible NameError (G:3031) | NOT EXTRACTED. The consolidation/decay formula reappears in `metal_loom.py` lines 51–57 and `weft_plasm.py` line 224. | S2 |
| F14 | G:3305–3660 | python | "AGENTIC SOFTWARE LOOM (ASL) // PRODUCTION-READY ORGANISM HARNESS": `StratifiedBiomatrixBus` (hippocampus 16) + fd helpers + `PlasticOrganismCell` + `OrganismEcosystemGovernor` (**v8**, Turn 27) | Combines all mechanisms: shm bus, masked LoRA cells with hippocampus bias, fd tool injection, novelty (α 0.45/0.02 at tension 40), consolidation 0.15, decay, jev-ui. | complete file, **does not run correctly** (see bug list) | NOT EXTRACTED. Closest relative of `weft_plasm.py`'s selection and consolidation. | S1+S2+S3+S4 |
| F15 | G:3728–4089 | python | "FULL MESHED & SI-BRIDGED ORGANISM CORE": `IntelligentMeshBus` + fd helpers + `PlasticOrganismCell` + `DistributedOrganismHarness` (**v9, final**, Turn 28) | Adds `psutil` telemetry → ch0 (`gather_silicon_telemetry`), a UDP listener on 0.0.0.0:9999 that appends to the hippocampus, and `broadcast_mesh_vector`. Selection is loss-only. | complete file, **does not run correctly** | NOT EXTRACTED. Telemetry idea re-implemented differently in `darwin_sysctl.py` (sysctl, not psutil). No UDP mesh in the repo. | S1+S2+S3+S4+S5 bridge+S6 mesh |

**How the versions relate.**
- Duplicate classes across fragments: `StratifiedBiomatrixBus` appears in F11, F12 and F14 with slightly different signatures (`write_sympathetic` takes 3, 4+last_winner and 4+decay_rate arguments). `IntelligentStratifiedBus` (F13) and `IntelligentMeshBus` (F15) are renames of the same thing. `PlasticOrganismCell` appears in F11, F12, F14 and F15. `send/recv_file_descriptor` appears in F7, F10, F14 and F15.
- F14/F15 `recv` returns the whole array (`return fds`, G:3411, G:3830). F7/F10 correctly return `fds[0]`. This is a regression.
- The whole file is duplicated in `missing-turns-supplement.md` (the same 15 python blocks, offset by +2 lines).
- Constants drift across versions:
  - hippocampus depth: 32 in v5, 16 in v6/v8/v9, 8 in v7 (the spec text at G:3104 says 32×512)
  - "safe" mutation rate: 0.005 or 0.01
  - "bold" mutation rate: 0.08, 0.25, 0.15, 0.18, 0.22, 0.25, 0.22 across versions
  - α_novelty: 0.4; then 0.5/0.05 switched at 50; then 0.45/0.02 switched at 40
  - memory bias: 0.05 in v5, 0.02 in v8/v9
  - decay base: 0.05 in v7/v9, 0.04 in v8

**Bugs and defects by fragment.** Line numbers are transcript lines.
- **All multiprocess versions (F6, F11, F12, F13, F14, F15).**
  - The governor sleeps only 0.10–0.15 s after `start()` with the `spawn` start method (G:1597, G:2405, G:2674, G:2996, G:3581, G:4031). A spawned child has to re-import torch, which usually takes far longer. So the candidate channels are probably read while still zero or left over from the previous generation.
  - In F14/F15 the blocking `accept()`/`recv()` partly synchronises **only** cells that actually send a tool request.
  - There is no locking on shared memory, so torn reads are possible (F1/F2 ping-pong).
  - "Change detection" is `hash(tensor.sum().item())`.
- **F1–F3.** The Edge Snap fires almost by construction. Checked numerically: initial ‖x‖≈362, after one cell pass ≈463, after two ≈593, above the 500 threshold. `trigger_edge_snap` and the `finally` both call `terminate_ecosystem`, so close/unlink runs twice. Harmless.
- **F10 (v4).**
  - The apoptosis/cleanup block (G:2133–2143) is indented under `else:`. When A wins, children are never terminated and the shm/socket are never closed. When B wins, `bus.close()` and `server_sock.close()` run inside the per-cell loop.
  - The harness blocks forever on `conn.recv` (G:2090) if a cell's `|intent| ≤ 0.02`, because that cell never sends.
- **F11 (v5).** Same indentation bug (G:2441–2453): the sympathetic update and apoptosis only run when B wins, and `bus.close()` is inside the loop.
- **F12 (v6).** No structural bug apart from the race. Novelty and the tool membrane were silently dropped. Cells do not read the hippocampus.
- **F13 (v7).**
  - `write_sympathetic` assigns `self.symp_matrix = budget/step/decay` (G:2862–2864), replacing the array with a float. After the first call, `read_sympathetic` returns the decay factor (0.05) for all four values, and the next `write_sympathetic` raises a TypeError.
  - `pruned_core = consolidated_core*…` (G:3031) sits outside the `if os.path.exists(...)`, so it raises NameError if the delta file has not been written yet (likely, because of the race).
  - `else:` at G:3036 becomes a `for…else`, so the UI, sympathetic write and apoptosis run once after the loop. Each generation leaves two orphaned child processes until then.
- **F14 (v8).**
  - (a) The `__init__` indentation (G:3522–3529) creates the socket and bus **only if** `/tmp/asl_master_genotype.npy` does not exist yet. A stale file therefore causes an AttributeError.
  - (b) `recv_file_descriptor` returns the array (G:3411), so `open(injected_fd)` (G:3495) raises TypeError and the cell crashes after its first tool request.
  - (c) The whole selection/consolidation block is nested inside `if signal.startswith("REQ_TOOL_")` inside the 2× accept loop (G:3573–3624). It runs 0–2 times per generation.
  - (d) `consolidated_core_matrix` and `delta_norm_val` are only defined in the B branch (G:3616–3624), so there is a NameError at G:3629 if A wins in the first generation.
  - (e) Harness `recv` deadlocks if a cell never crosses `|intent| > 0.01`.
  - (f) Apoptosis is nested inside `for p in …` (G:3643–3646).
- **F15 (v9).**
  - (a) `return` inside the `for` loop of `gather_silicon_telemetry` (G:3977–3982). Only dims 0–3 are set and dims 4–511 stay zero.
  - (b) `io_activity` is the cumulative bytes since boot divided by 1e9 and clipped (G:3968–3969), so it saturates at 1.0. It is not a "velocity".
  - (c) Selection is nested in the accept loop again (G:4019–4059), so it runs twice per generation.
  - (d) `else:` at G:4057 is attached to `if target_mesh_peer`. With the default `target_mesh_peer=None` (G:4088), every consolidation is reverted (`consolidated_core = core_weights`), so the default run **never learns**.
  - (e) NameError for `consolidated_core` if A wins in the first generation.
  - (f) The `recv` bug is swallowed by `except Exception: pass` (G:3892–3898). Tools silently never write and fds leak.
  - (g) The mesh sends `winning_delta.mean(dim=0)` (a LoRA delta, G:4056), but the listener stores it as a hippocampus memory (G:3944).
  - (h) The `mesh_running` flag cannot stop a blocking `recvfrom` (G:3940), and the listener thread writes the hippocampus with no lock.
- **Cross-platform claim.** "Linux / macOS / Windows" (G:3310, G:1417, G:1670). The SCM_RIGHTS/AF_UNIX paths and `/tmp` paths (F7–F10, F14, F15) are Unix-only.
- **Wrong line references in the prose.** "lines 78–80" (G:2722) and "Lines 116–118" (G:3070) do not match the code blocks. Counting from each block's first line, the telemetry ingestion is at block line ~181 (G:2664) and the decay at ~222–223 (G:3030–3031).

**Text blocks (diagrams or equations, not software).** G:199–235 (ASL layers), G:292–309 (Tension Grid), G:379–390 (trade-off), G:443–452 (autonomy continuum, which has concrete thresholds), G:466–481 (PLL block schema), G:619–639, G:706–722, G:757–775 (hypersphere clamp), G:802–830 (harness OS layers), G:1022–1050 (cellular collective), G:1120–1137, G:1169–1191 (first-principles loop), G:1678–1700 (tool injection cycle), G:2766–2781 (microkernel), G:3098–3106 (bus layout), G:3135–3147 (cell anatomy), G:3177–3205 (selection matrix), G:3245–3255 (Synaptic Dial equation), G:3685–3702 (mesh).

---

## 3. Ideas, claims, mechanisms

### 3.1 Loom and Tension Grid (Turns 3–7)

- **Code as topology: Warp/Weft re-weaving** (G:147–152). Invariants (Warp) are fixed. Adaptive agents (Weft) are re-woven at "tension" points instead of refactoring the codebase. Category: vision-language. Not a testable claim.
- **ASL four layers** (G:239–266). Warp (invariants + Tension Grid), Weft (Shuttle orchestrator, ephemeral Logic Threads, telemetry Resonance Loops), Heedle (intent → topological templates; ambiguity is surfaced to the human instead of raising an error), Tapestry (just-in-time materialisation, then "unraveling" with zero leftover code). Category: theory / vision-language. "Heedle" is very likely a misspelling of *heddle*; consider correcting it in the canon.
- **Kinetic Boundary Dampening** (G:315–319). Instead of denying an action, the cost of an operation grows exponentially as an agent approaches an invariant ("burn increasingly massive amounts of execution tokens"). Category: mechanism / economics. Would be falsified by: under the cost function, an adversary can reach the invariant within a bounded budget. G:394–396 itself names the **economic DoS** weakness.
- **Structural Vector Shifting** (G:323–327). The rest of the system re-balances around an agent's optimisation. Category: vision-language. It is never specified.
- **Edge Snap / yield point** (G:331–335, G:400–402). Each thread has a breaking threshold. When crossed, it is cut off cleanly and its resources returned. The trade-off: in-progress work is destroyed. Category: mechanism. In code it exists only in v1 (G:1399–1404). v5–v9 have no Edge Snap.
- **Haptic Splicer Interface** (G:339–345). Tension is rendered as threads you can see and feel. G:912 retracts this as "pure engineering sci-fi", but G:3291 reinstates it. Category: vision-language. **Contradiction** (see §3.6).
- **Five trade-offs** (G:363–413): memory paradox, non-determinism (unsuitable for avionics, pacing, banking, G:373), economic DoS, broken chain, human-in-the-loop fatigue. Category: theory. These are useful honest-limitations material for a white paper.
- **Autonomy continuum governor** (G:441–456). Green (T<0.3, full AI autonomy) / Yellow (0.3–0.7, shared, haptic alert) / Red (≥0.7, freeze, human must resolve). Category: governance / engineering contract. Would be falsified by: the operator still being overloaded at real event rates. T is never defined as a normalised quantity; the code's T is an unbounded Frobenius norm of ~100–600.
- **Paracausal Loom Ledger (PLL) block** (G:462–481). Fields: thread hash, tension, AI% vs human% mutation share, machine signature, human biometric/intent key. Green-zone changes are signed by the AI alone; red-zone changes need a dual signature (G:494). Category: governance / engineering contract. **Not implemented in any code here.** The key fields are placeholders (`[0xAI_GEN_KEY]`, `[0xHUMAN_SECURE_AUTH]`, G:478–479), not secrets.
- **Deterministic re-weaving / time-travel debugging** (G:486, G:663, G:3293–3297). Replaying signed diffs reproduces the ephemeral tapestry exactly. Category: engineering contract. Would be falsified by: non-deterministic sources the ledger does not record. Every code version seeds with `os.getpid()+time` (G:1531, G:1998, G:2324, G:3439, G:3853) and spawns on wall-clock timing, so replay is impossible with the current code.

### 3.2 Prior art and weight-space claims (Turns 9–13)

- **Prior-art map** (G:551–579). DARPA IDAS, FAST intent-driven Swift (arXiv 1907.08695), AutoGen, Wasm sandboxing of agent tools, "Sys" self-evolving EDA (arXiv 2604.15082), HACI haptic-audio code interface (arXiv 2511.03733), HapticMaster / Core Haptics. Category: roadmap-branch / literature. The citations need checking; this agent could not verify them offline.
- **"First true Splicer" thesis** (G:586–590). The missing piece is a single medium: a compiler that outputs "fluid topological math" connected to tactile feedback. Category: vision / mission statement. This is the thread's mission sentence and is repeated as the user prompt at G:602.
- **External claims supplied by the user and echoed by the model.** These are **unverified** and offline verification was not possible. Category: claim. Treat them as user-supplied premises, not facts.
  - GPT-6 Astra "Weight-Space Programming" (MIT CSAIL): editing 0.016% of weights, writing a network from scratch, an "early November 2026" date (G:605–607, G:890).
  - "jev-ui" / "TypeSafe's Jev" (G:694, G:732, G:897). The two names are inconsistent with each other.
  - Inkling 2 Small on Tinker: a $500 budget autonomously trained a forecaster (G:694–696, G:904).
  - "594-billion-parameter hyper-matrix" (G:753) and "Active Weights (17B)" (G:764).
  - A `tinker://.../weights/final` checkpoint URI (G:738).
  - Turn 13 (G:883) asserts "entirely real".
- **Tension Grid as a weight-hypersphere clamp** (G:652–656, G:751–779, G:850–853). Measure cumulative weight distance from a signed aligned checkpoint. If it exceeds a radius, freeze and roll back. Category: mechanism / engineering contract. Would be falsified by: harmful behaviour changes that stay inside a small L2 ball, since weight norm distance is a weak proxy for behaviour. **This is the one Tension Grid idea the repo actually implements**: `weft_plasm.verify_weight_update_safety` with `R_INVARIANT = 120.0` (weft_plasm.py lines 22–103). No code in this transcript implements it. The v1 "tension" here is the norm of the activations, not of the weights.
- **Weights as applications, OS as harness** (G:789–867). Apps become per-user LoRA/expert deltas trained online. The harness curates perception. Category: vision-language / theory. Would be falsified by: online per-user LoRA adaptation failing to beat prompt/tool baselines at acceptable cost.
- **Deterministic execution handlers** (G:846). The model emits an "intent vector". The harness routes it through hard-coded, invariant boundaries before any side effect (money, disk, network). Category: **engineering contract**, and safety-relevant. This is the most concrete safety design statement in the thread. The fd broker (F7–F9) is its only implementation, and it checks nothing (it opens whatever file is hard-coded).
- **Reality check** (G:887–921). Real today: weight editing on small models, generative UI over component registries, bounded autoresearch, IDAS, Wasm sandboxes. Hype: macro-scale weight rewriting, pixel-level UI without a chassis, haptic tension. Category: theory. This is a candid baseline worth keeping in any white paper.
- **Roadmap** (G:939–969). (1) Build the harness, not the app (Wasm/microcontainers, tools, telemetry, final-syscall guardrails). (2) Intent/telemetry engineering and autonomy logging. (3) LoRA, merging, activation engineering. Category: roadmap-branch.

### 3.3 Cells and first principles (Turns 16–17)

- **Cellular weight-space collective** (G:1012–1088). Each cell is a nucleus (specialised LoRA) plus a membrane (Wasm mini-harness whose "keys" the cell holds itself, G:1059). The **Plasm** is a consensus matrix where cells "negotiate by overlapping their latent representations" (G:1063–1071). Membrane mutation, mitosis into specialised children, apoptosis on compromise, and regeneration "from the master signed ledger state" (G:1088). Category: vision-language / theory. In the code, cells never read each other's outputs; a central governor picks the winner. "Statistical dialectic" names a mechanism that does not exist here.
- **Four first-principles pillars** (G:1139–1161). Category: theory / engineering-contract.
  - Membrane = page-isolated memory plus restricted ISA, with weights read-only from inside (G:1143).
  - Metabolic budget per clock: a cell that burns budget without producing stability starves (G:1149).
  - Receptor signalling = shared latent tensor bus with no text (G:1155).
  - Genotype locked, phenotype mutable, mitosis → child shallow LoRA (G:1161).
  - Would be falsified by: cells being able to rewrite their own weights or other cells' weights. In v7–v9 cells write the delta files that the harness merges into the genotype without checking them.
- **Execution loop** (G:1193–1196). Polarization → reaction → mitosis → homeostasis, where homeostasis is "friction on the bus drops back to zero". Category: mechanism. Every selection objective in the code rewards smaller output norm (or larger, under novelty, see §3.4), so "homeostasis" in the code is shrinking activations, not satisfied intent.

### 3.4 Prototype mechanisms (Turns 18–24)

- **POC primitives** (G:1218–1222). Python + PyTorch + POSIX shm. Membrane = OS process, Plasm = `/dev/shm` float block, metabolic controller = process manager. Category: engineering. True: these are real primitives.
- **"Page-locked memory" / "zero-copy" claims** (G:1429, G:1491, G:3096, G:3110). False as written. `multiprocessing.shared_memory` does not mlock pages, and `write` (`.numpy()`) and `read` (`.copy()`) both copy. The later repo `weft_plasm.py` uses a ctypes view plus `torch.from_numpy`, which avoids one copy.
- **Membrane isolation claims** (G:1430 "no internet access", G:1876 "Absolute Zero Privilege", G:1847 "the cell … lacks security context", G:3151 "cannot peek at the host filesystem"). **False.** `mp.Process` children inherit the parent's full user privileges, network and filesystem access, and the cell code imports `os`/`socket`/`numpy` and writes files itself (G:2932–2934, G:3488). Category: safety-relevant claim. Would be falsified by: any cell `open('/etc/passwd')`, which succeeds.
- **A/B mitosis as process-level speculative decoding** (G:1449–1451). Two mutated children race and the governor verifies. Category: mechanism. The selection is effectively decided by mutation scale, not exploration (next item).
- **Novelty scoring against homogenisation** (G:1895–1901, G:2112–2118; spec G:3213–3223). `score = fitness + α·mean‖out − archive‖`. Category: mechanism. Checked numerically on the v8 setup (512-dim, input std ~1.3): fitness = 1/‖out‖ ≈ 0.002–0.009, while novelty ≈ 1.8 (safe) / 5.2 (bold) against an all-zero archive. **Novelty outweighs fitness by roughly 100–1000×.** It mostly measures the magnitude of the output mean, not uniqueness, so the high-mutation "bold" lineage wins almost every time. Under the loss-only versions (v2, v6, v7, v9) the low-mutation "safe" lineage wins almost every time. Either way the outcome is fixed in advance by the mutation rate. Would be falsified by: logged winners changing with input. They mostly will not.
- **Hippocampus (episodic vector ring)** (G:2170–2175, G:2285–2290, G:3125–3127). A circular stack of winners' mean vectors, fed back as a bias (0.05 / 0.02 × mean). Category: mechanism. A real but tiny mechanism. A "bare-metal HNSW grid" was promised (G:2174) and never built.
- **Multi-resolution pipes** (G:2177–2184). Focal Nerve (bulk), Sympathetic Current (scalars → "attention mask"), Dialectic Field (peer-to-peer KV-cache exchange between cells). Category: mechanism / roadmap. Focal and sympathetic are implemented as shm segments. No cell feeds the sympathetic scalars into anything (v5 reads them but does not use them, G:2350). **The Dialectic Field is never implemented.**
- **Plasticity mask + rank-2 surgical LoRA** (G:2186–2191, G:2329–2343; spec G:3153–3169). The mask is softmax over the row norms of the core weights, normalised by its max. Category: mechanism. Claim: "0.0 = frozen invariant (core alignment laws, safety protocols)". Checked numerically for 512×512 weights with std 0.02: the mask ranges **0.92–1.00**, and zero entries fall below 0.3. So **nothing is protected**, and the "Protected parameters" printout (G:2345) reports 0. The mask is computed from random weights, has nothing to do with alignment, and is per-row rather than per-element. Would be falsified by: the printed protected count. It falsifies itself.
- **jev-ui terminal dashboard** (G:2627–2655, G:2961–2978, G:3531–3551, G:3984–4003). Clears the screen and prints step, budget, tension, winner and a sparkline of the output mean. Category: engineering. It has nothing to do with the "jev-ui" probability-UI framework claimed at G:694. It is a print loop that borrows the name.

### 3.5 After it is built, consolidation, spec, mesh (Turns 25–28)

- **Post-build lifecycle** (G:2739–2758). The system settles into homeostasis tuned to the machine, speciates per user/machine, then accretes tools (cells micro-compile Wasm and request fds). Category: vision / roadmap-branch. Would be falsified by: weights failing to diverge measurably between machines in a long-run log.
- **Bare-metal microkernel endpoint** (G:2762–2787). A Rust/C microkernel hands "total control of the hardware clock lines" to the cell matrix, and "the model weights become the operating system". Category: roadmap-branch / vision. Safety-relevant: it explicitly removes host-OS protections.
- **Synaptic Mutation Dial (consolidation)** (G:2804, G:3024–3025, G:3257–3263). `W ← W + η·Δ_win` with η = 0.15. The text calls it an "exponential moving average" (G:2804, G:3069, G:3259). **It is additive, not an EMA**: an EMA would be (1−η)W + ηW′. Category: mechanism.
- **Intelligent Decay** (G:3027–3031, G:3265–3277). `W ← W·(1 − 0.01·d₀·(1 + 1/T))`. Pressure rises as tension falls. Category: mechanism. Claimed as Hebbian "use it or lose it" pruning of unused connections (G:2802–2804, G:3267, G:3277). **It is uniform weight decay**: every parameter shrinks by the same factor, about 0.04% per generation at T ≥ 10 (computed). Nothing tracks use.
- **ASL Architectural Specification** (G:3078–3297). Sections 1–7: bus, plastic cells, Tension Grid + novelty governor, tool membrane, consolidation/decay, PLL, reference implementation. Category: spec / manifesto. It is the nearest thing in this file to a finished document (§5).
- **Network Mesh "Cross-Splicing Fabric"** (G:3674–3706). Claimed: remote cryptographic tensor plane, RoCE v2 or UDP, nodes stream hippocampus embeddings, cross-node novelty triggers mitosis. Category: mechanism / roadmap. Implemented as plain unauthenticated UDP that carries LoRA-delta means (G:3934–3955, G:4056). There is no cross-node novelty check.
- **Hardware Peripheral Bridge** (G:3710–3720). Claimed: per-core frequencies, thermal throttling, page-fault velocity, cache misses, I/O latency, packet drops. Category: mechanism. Implemented: `cpu_percent`, `virtual_memory().percent` and cumulative disk bytes, placed in 3–4 of 512 dims (G:3963–3982). Would be falsified by: correlating ch0 with machine load, since dims 4+ are zero.

### 3.6 Contradictions

1. Turn 28 text (G:3726, G:4093–4099) says the v9 code includes "Anti-Homogenization Novelty Scoring". The v9 code selects on loss only (G:4033–4046).
2. Spec hippocampus is 32×512 (G:3104). The code uses 16 (G:3340, G:3761), v7 uses 8 (G:2837), v5 uses 32 (G:2244), and the repo `weft_plasm.py` uses 8.
3. Spec decay formula (G:3250, G:3253, G:3271–3275) has no 0.01 factor. The code multiplies by 0.01 (G:3031, G:3629, G:4062).
4. "Exponential moving average" (G:2804, G:3069, G:3259) vs additive update (G:3025, G:3620, G:4051).
5. "Use it or lose it" Hebbian pruning (G:2802, G:3267) vs uniform decay (G:3629).
6. Plasticity mask "approaching 0.0 = frozen invariants" (G:3161) vs a numeric range of ≈0.92–1.0 (G:2332–2334).
7. "Permanently remembering its own successful behaviors" / "over months" (G:3069, G:3263) vs the `finally` blocks that **delete the genotype file** at the end of every run (G:3056, G:3652, G:4081).
8. Edge Snap and regeneration from the "master signed ledger" (G:1088, G:3225–3227) vs no ledger, no signing and no Edge Snap anywhere in v2–v9.
9. Spec says mitosis only if tension > threshold (G:3187). v6–v9 spawn A/B unconditionally every cycle. Only v2 checks (G:1631).
10. Turn 13 calls haptic tension sci-fi (G:912). The spec requires a "haptic friction spike" and a "biometric intent fingerprint signature" (G:3291).
11. Weights read-only from inside the cell (G:1143) vs "the cell is given the keys to its own membrane" (G:1059) and cells writing the deltas that the harness merges into the genotype (G:2932, G:3488, G:3891).
12. Mesh described as "cryptographic" and RoCE v2 (G:3674, G:3681) vs plaintext UDP (G:3936–3955). Mesh described as sharing hippocampus embeddings (G:3683, G:3704) vs code that broadcasts the mean of the winning LoRA delta (G:4056).
13. Cells "negotiate by overlapping latent representations" (G:1071) vs no inter-cell reading in any code since v2.
14. Sympathetic values read "directly from the hardware clock lines" (G:2466) vs reading a float from shm.
15. "Normalizes … storage I/O speeds" (G:4097) vs cumulative byte counters (G:3968).
16. README.md:7 says "40 `<pre>` blocks" vs 34 fenced blocks here. README.md:18 attributes the IC widget to "Desktop 8, Turn 21" vs nothing about interaction combinators in this file.

### 3.7 Safety-relevant items (locations only)

- **No secrets, private keys, RPC URLs, mainnet addresses or live-deploy instructions** in this file. G:478–479 hold placeholder key labels only.
- **Unauthenticated network listener.** UDP bind `0.0.0.0:<mesh_port>` with default 9999 (G:3938, G:4087). It accepts any 2048-byte datagram from anyone and writes it into the hippocampus, which biases every cell (G:3941–3944). The text tells users to point it at a peer IP (G:4086, G:4098).
- **Unchecked genotype merge from a world-writable path.** Delta files under predictable `/tmp` names (`/tmp/organism_master_genotype.npy_delta_*.npy`, `/tmp/asl_master_genotype.npy_delta_{1,2}.npy`, `/tmp/asl_meshed_genotype.npy_delta_*`; G:2932–2934, G:2946, G:3488, G:3511, G:3891, G:3911) are loaded with `np.load` and added to the master weights with no validation (G:3020–3025, G:3617–3620, G:4049–4051). Any local user or process can poison the genotype. These are plain numeric `.npy` arrays, so no pickle; `np.load` defaults to `allow_pickle=False`.
- **Predictable Unix socket paths** (`/tmp/harness_receptor.sock` G:1816, `/tmp/harness_evolutionary.sock` G:2057, `/tmp/asl_harness_receptor.sock` G:3512, `/tmp/asl_meshed_receptor.sock` G:3912). They are created with the default umask and no peer credential check. Any local process that connects and sends `REQ_TOOL_n` receives an open append fd from the harness (G:2091–2098, G:3573–3578, G:4023–4027). They also call `os.remove` on an existing path first (symlink/race hazard).
- **Shared-memory name collision.** On `FileExistsError` the code attaches to any existing shm segment of the same name, then `close()` **unlinks** it (G:1253–1279 and every bus class). It could destroy another program's segment.
- **Files written to the current directory:** `workspace_tapestry.txt` (G:1844), `candidate_output_ch_*.log` (G:2096), `harness_io_channel_*.log` (G:3576), `silicon_io_channel_*.log` (G:4025).
- **Shell call** `os.system('clear')` (G:2633, G:2962, G:3533, G:3985). Benign, but a shell invocation.
- **False isolation claims** that could mislead operators into running untrusted cells: G:1430, G:1876–1878, G:3151, G:3237.
- **Autonomy-expanding vision statements:** models executing external actions such as "sending money" through an intent vector (G:846, where it is gated), the organism weaving its own scaffolding "without a human ever writing a new function patch" (G:2758), and handing "total control of the hardware clock lines" to the weights (G:2785).
- **Code labelled "production-ready" that does not run correctly:** G:3303, G:3308.

---

## 4. Candidate software systems

**S1. Plasm / Stratified Biomatrix Bus** (corpus names: "Latent Tensor Bus", "Plasm", "Biomatrix", "Focal Nerve / Sympathetic Current / Hippocampus").
- Purpose: a shared-memory substrate for passing activations and scalars between processes.
- Inputs/outputs: float32 tensors; [3,64,512] focal, [1,16] sympathetic, [D,512] hippocampus ring.
- Interfaces: written by the governor (S2), read by cells (S2), fed by the telemetry bridge (S5) and mesh (S6), read by the dashboard (S4).
- Fragments: F1, F4, and the bus classes inside F10, F11, F12, F13, F14, F15.
- Dependencies: Python, numpy, torch, `multiprocessing.shared_memory`.
- Status: **shares logic with the existing `weft/runtime/core/weft_plasm.py`**, which descends from this lineage via almalga/ahraz/mac.md (4 focal channels, thermal slot, ring pointer, ctypes view, safety verifier). Not a separate system. The canonical version is the repo one.

**S2. Cellular Evolutionary Governor** (corpus names: "Tension Grid Orchestrator", "Evolutionary/Novelty Governor", "Synaptic Mutation Dial", "Intelligent Decay", "Plastic Organism Cell").
- Purpose: A/B mutate a weight matrix, select one variant, consolidate it into the genotype, decay.
- Inputs: focal ch0, hippocampus, sympathetic. Outputs: updated genotype, winner, tension.
- Interfaces: uses S1; reports to S4; optionally S3 (tools) and S6 (mesh).
- Fragments: F2, F3, F5, F6, the cell and governor classes in F10–F15.
- Dependencies: torch, multiprocessing.
- Status: **shares logic** with `weft_plasm.run_plasm_cycle` (in-process A/B, fitness + 0.35·novelty, consolidation 0.15, decay 0.0004, plus a baseline-distance safety gate) and with `weft/runtime/mac/metal_loom.py` (loss-only, 0.005/0.22, symmetric rank-2, decay 0.04·0.01). The repo versions dropped multiprocessing and fixed the race and indentation bugs. The repo also added what this file only describes: a Tension Grid weight clamp.

**S3. Dynamic Tool Membrane (capability broker)**.
- Purpose: cells hold no ambient file or network access; the harness grants capabilities by passing an open fd over SCM_RIGHTS once a policy check passes.
- Inputs: a `REQ_TOOL_n` message. Outputs: an fd in the cell's fd table.
- Interfaces: the harness policy (the "Harness Invariant Guard", which in practice checks nothing), cell processes.
- Fragments: F7, F8, F9, plus the copies in F10, F14, F15.
- Dependencies: POSIX AF_UNIX, `socket.sendmsg/recvmsg`.
- Status: **genuinely separate and NOT EXTRACTED.** It is the strongest real engineering idea in the file: capability-based tool grants. To be meaningful it would need real OS sandboxing (seccomp, Landlock, sandbox-exec, or Wasm) and a real policy. That is the concrete form of the "deterministic execution handlers" contract (G:846).

**S4. jev-ui terminal dashboard**.
- Purpose: a human view of tension, budget, winner and an activation sparkline.
- Inputs: governor state. Output: terminal text.
- Fragments: `draw_jev_ui` in F12, F13, F14, F15.
- Status: a minimal precursor of the **Aywa dashboard** idea (`weft/runtime/aywa/index.html`, WGSL). It shares nothing at code level. The "jev-ui" name refers to an external, unverified framework. Recommend renaming it so the external claim is not baked into the corpus.

**S5. Hardware Peripheral Bridge (silicon telemetry ingestion)**.
- Purpose: host metrics → normalised focal tensor.
- Inputs: psutil CPU, memory and disk counters. Output: [64,512] tensor.
- Fragment: `gather_silicon_telemetry` in F15 (G:3957–3982).
- Status: conceptually the same role as `weft/runtime/mac/darwin_sysctl.py` (sysctl load/ncpu/mem → cpu_strain, est_temp) and the telemetry in `weft/runtime/aywa/weft_daemon.py`. Different implementation (psutil vs sysctl). Not extracted.

**S6. ASL Network Mesh / Cross-Splicing Fabric**.
- Purpose: nodes share long-term memory vectors.
- Inputs/outputs: 512-float UDP datagrams on port 9999.
- Fragment: `_run_mesh_listener` and `broadcast_mesh_vector` in F15 (G:3934–3955); prose at G:3679–3706.
- Status: **NOT EXTRACTED.** It is the precursor of the multi-node harness discussed in 84ADC9 (per the README). It needs authentication, framing and schema before any use.

**S7. Paracausal Loom Ledger + Autonomy Governor** (spec only).
- Purpose: a signed, append-only log of each change with AI/human share and zone-dependent signature policy, plus replay.
- Prose: G:437–496, G:659–663, G:873, G:3281–3297.
- **No code in this file.** It is the conceptual ancestor of the repo's ledger/provenance contracts (`weft/runtime/ledger/ProvenanceRegistry.sol`). A grep found no autonomy or dual-signature fields there, so the autonomy-share schema is not yet realised anywhere.

**S8. Tension Grid (weight-space safety clamp)** (spec, with partial code elsewhere).
- Purpose: bound drift from a signed baseline and roll back on breach.
- Prose: G:313–335, G:652–656, G:751–779, G:848–853.
- The only code here is v1's activation-norm check (F3). **Realised in the repo** as `weft_plasm.verify_weight_update_safety` (`R_INVARIANT`, budget checks).

**S9. Wasm micro-harness sandbox** (roadmap only).
- Prose: G:561, G:594, G:911, G:943–944, G:975, G:1039, G:1059, G:1100–1101.
- Never built in this file. Every prototype uses plain processes. It is the missing piece that would make S3's isolation claims true.

---

## 5. Documents implied

- **ASL Architectural Specification / manifesto** (G:3078–3297, plus §8 at G:3670–3720). Already structured as a document with an executive summary, numbered sections and equations. This is the **closest to a finished document** in the file. It needs: the math rendering repaired (G:3159–3275), the lost values restored (G:3273, G:3295), the contradictions in §3.6 resolved, its code section (G:3301–3660) replaced by a pointer to the canonical repo implementation, and the external claims (Astra, jev-ui, Inkling) moved to a clearly labelled "user-supplied premises" box.
- **Genesis / origin narrative** (Turns 0–4, G:6–278). The lore-to-architecture origin story, including the Namrask quote that the user picked (G:104, G:131) and the warp/weft mapping (G:145–152). Suitable for a "Why Weft" or ethos preface, and relevant to `weft/ethos.md`.
- **Honest limitations / trade-offs white-paper section** (G:361–413 trade-offs, G:887–921 reality check). Nearly finished prose.
- **Governance spec: autonomy continuum and accountability ledger** (G:437–496, G:3285–3291). Needs a normalised definition of T, the signature scheme, key custody, and what counts as "human haptic %". It ties to the governance docs (`govern.md`) and the ledger contracts.
- **Roadmap / practitioner guide** (G:939–969 plus the T25 lifecycle at G:2739–2787). Branches: near-term harness (Wasm, tools, telemetry), mid-term intent/eval engineering, frontier LoRA/merging; long-term bare-metal microkernel.
- **First-principles spec of digital cellular biology** (G:1116–1196). The four pillars and the execution loop. A good skeleton for a short "invariants" spec once each pillar has a testable acceptance criterion: isolation test, budget-starvation test, no-text bus, genotype immutability.
- **Prior-art survey** (G:546–590). Needs citation checking.
- **Threat model** (implied but never written). The economic DoS from dampening (G:394–396), the mesh injection, the `/tmp` delta poisoning, the socket fd grant, and the false isolation claims all point to a missing threat model document.

---

## 6. Open questions / gaps

- **Tension T is undefined as a quantity.** The governor thresholds (0.3/0.7, G:447) assume a normalised T. The code's T is an unbounded Frobenius norm of activations (~100–600). Weight drift and activation norm are conflated. Which one is "tension"?
- **The fitness target is a zero tensor** (G:1579, G:2109, G:3211). Minimising ‖out‖ rewards silencing the signal. What does "zero friction / intent satisfied" mean for a real task? There is no task objective anywhere.
- **Novelty vs fitness scaling** makes selection a function of mutation scale (§3.4). There is no normalisation, no Pareto selection and no archive of behaviour descriptors.
- **The plasticity mask protects nothing** (numerically 0.92–1.0). Nothing specifies how "core alignment" parameters would be identified.
- **The Plasm "statistical dialectic" / Dialectic Field** (G:1063–1071, G:2184) is never specified or coded: no protocol, no KV-cache format, no consensus rule.
- **Metabolic budget** is a float decremented by a constant (2.2–5.0 per generation) and never enforced. Nothing starves or throttles when it hits zero (contrast G:1149). The repo's `verify_weight_update_safety` does enforce a budget.
- **Edge Snap / apoptosis / regeneration "from the master signed ledger"**: no signing, no ledger and no regeneration exist in code. v2–v9 have no Edge Snap.
- **PLL replay** is impossible with time/pid seeding and wall-clock races. Seeds, inputs and spawn ordering would need to be logged.
- **Membrane isolation**: every "membrane" is an unsandboxed `mp.Process`. Wasm, seccomp and page-isolated restricted-ISA (G:1143) are all promised and never built.
- **Tool membrane policy**: the "Harness Invariant Guard" verifies nothing (G:1841–1851, G:2093). What is the policy language? How is an intent vector decoded into a resource request? Today it is one scalar threshold and a hard-coded filename.
- **Mesh**: no authentication, no encryption, no schema or version, no handling of loss or reordering. RoCE v2 is claimed but not used. The mesh sends LoRA deltas into a memory slot.
- **Hardware bridge**: the `return` bug leaves 508 of 512 dims zero. I/O is cumulative, not a rate. The per-core frequency, thermal, page-fault and cache-miss metrics promised at G:3716–3718 are absent.
- **Persistence**: the "permanent" genotype is deleted on exit. Where should it live, how is it versioned, and how does it tie to the ledger?
- **Cross-platform**: Windows is claimed but the code is Unix-only.
- **The external premises are unverified**: GPT-6 Astra, jev-ui/"TypeSafe's Jev", Inkling 2 / Tinker, arXiv 2604.15082 and 2511.03733. The corpus should mark them as such until checked.
- **Provenance of the extraction**: the README counts (40 `<pre>`) and turn attributions (widget 05 at "Turn 21") do not match this file. The file is fully duplicated in `missing-turns-supplement.md`. Canonicalise one copy.
- **Lineage gap**: the jump from this file's v9 (multiprocess, psutil) to the repo's `weft_plasm.py` (single-process, MPS, safety verifier, watermark) goes through other files (almalga/ahraz/mac.md per the docstring). This file is the origin of the bus/governor design, not the source of the extracted code.
