<!--
Corpus map source report H. Scope: weft/browser-sources/missing-turns-supplement.md.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory H: `weft/browser-sources/missing-turns-supplement.md`

Scope: `/home/user/weft/weft/browser-sources/missing-turns-supplement.md` (4656 lines, read in full), with `/home/user/weft/weft/browser-sources/README.md` (36 lines) for context. Line numbers below refer to the supplement unless another file is named.
How I checked: I diffed every turn section against the three thread files in `browser-sources/`. I pulled all 17 Python blocks into the scratchpad (`.../scratchpad/h/py/`) and parsed them with `ast.parse` only; nothing was executed. I also ran small numpy simulations to test the numerical claims (plasticity mask, selection scores, tension growth). Nothing in the repo was modified.

---

## 1. Per-file summary

### 1.1 `weft/browser-sources/missing-turns-supplement.md` — 4656 lines

**Genre:** a dialogue-transcript dump scraped from Google Chrome "AI Mode" over CDP. Each turn is a user prompt followed by the model's reply. The text still carries Google UI chrome: a "ShareGood responseBad response…" footer after almost every turn (e.g. 47, 90, 4105), plus inline markers `[candid]` (508, 796, 883, 1016, 1672, 2216, 4305), `[filegen-via-code]` (4457), `[FollowUp]` (4615), and "Go to product viewer dialog for this item." (1449). Math was flattened to a duplicated plain-text plus screen-reader form (e.g. "Tcap T⁠" 319/443; 1903; 3161; 3169; 3213; 3219; 3273).

**What the file says it is (line 3):** "the 31 turns … that were not individually copied into the 53 `.md` files in `exo/weft/`".
**What it actually is:** 43 turn sections (`grep -c '^## \['` = 43), not 31. Every one of them is a **verbatim duplicate** of a turn already in the other `browser-sources/` thread files:
- **90133B Turns 0–28** (lines 8–4106; 29 turns). Thread: Desktop 8 "early share tab", the genesis thread, which matches `Moissanite-Labs/compass` Discussion #5 per the README. Byte-identical to `thread1-splicers-genesis-90133B.md` lines 6–4103: a diff shows only one extra trailing blank line. So the supplement carries the **entire** genesis thread, not just "missing" turns.
- **84ADC9 Turns 1, 8, 12, 16, 18, 24, 25, 26, 27, 38, 41, 69** (lines 4109–4637). Thread: Desktop 8 live tab, the main Syntactic Weft thread. Each is identical to the same turn in `thread1-weft-main-84ADC9.md` (diff = 0 lines each). Turns 16, 18, 24, 25, 26, 41 are only "N sites / top web results" link dumps with no model prose. Turn 69 is "no response available" (4636).
- **6C083A Turns 25, 28** (4640–4656). Thread: Desktop 9 design thread. Both say "Something went wrong and an AI response wasn't generated" and match `thread2-design-main-6C083A.md`. Turn 28's prompt (4648–4652) is a useful **requirements list for repo/contributor analytics**: maintainer vs outside lines of code, shared labels, contribution concentration, contributor quality, contributor capture. It never got an answer. It plausibly relates to `runtime/aywa/github_harvester.py`.

**Net:** 34 turns have substance (90133B 0–28 plus 84ADC9 1, 8, 12, 27, 38). The file adds **no unique content** relative to `browser-sources/`. Its only value is relative to the top-level `weft/*.md` corpus. I spot-checked identifiers that appear nowhere else in `weft/*.md`: `LatentTensorBus`, `NoveltyDrivenHarness`, `recv_file_descriptor`, `Namrask`, "GPT-6 Astra", `FractalInteractionNet`, `lease_harvest`, "Node Beta". (Corpus count: 37 top-level `weft/*.md` + 19 `weft/design/*.md` = 56, not 53; the three ALL-CAPS/README files were probably added later.)

**Topics, in arc order (90133B):**
- Destiny lore: Fallen/Devil/Sacred Splicers, SIVA, Mithrax, Namrask the weaver, Ada-1's Loom, Strand (T0–T2).
- Software metaphor: Warp/Weft/Heedle/Tapestry, the "Agentic Software Loom" (ASL) (T3–T4).
- Tension Grid (T5) and trade-offs (T6).
- Autonomy-continuum governor plus the "Paracausal Loom Ledger" (PLL) (T7).
- Related work: DARPA IDAS, FAST, AutoGen, Wasm, HACI (T9).
- Claimed 2026 events: GPT-6 Astra weight-space programming, jev-ui, Inkling 2 on Tinker (T10–T11).
- "Weights as applications, OS as harness" (T12); reality check (T13); roadmap (T14).
- Models-as-cells collective, "Plasm" consensus bus, mitosis/apoptosis (T16); first principles (T17).
- **Python POC series** (T18–T24, T26–T28): POSIX shared-memory tensor bus, process "cells", A/B mitosis selection, SCM_RIGHTS fd "tool membrane", novelty scoring, a stratified bus (Focal/Sympathetic/Hippocampus), plasticity mask plus rank-2 LoRA, a terminal "jev-ui" dashboard, synaptic consolidation plus decay, UDP memory mesh plus psutil telemetry.
- Post-build vision (T25: homeostasis, speciation, tool accretion, bare-metal microkernel).
- Spec/manifesto (T27, §§1–7) and distributed extension (T28, §§8–9).

**84ADC9 excerpts:** confirms Solidity triad plus inbound receiver (T1); `mesh_cluster_simulation.py` Exo-Mitosis compute-leasing sim (T8); "perception of weaver" with the private-key-in-config suggestion (T12); **prior-art admission: the "Weft" name and conceit attributed to Luca Berton's Weft** (T27); fractal Interaction Combinator net with `FRC`/`VLV` nodes (T38).

### 1.2 `weft/browser-sources/README.md` — 36 lines (context only)

A manifest of the browser-sources directory. It claims "144 Turns, 191 Code Blocks" across the three threads and describes the supplement as "All 31 turns … not copied into the 53 individual .md files". It lists the five widget pairs. Inaccuracies against what I measured: the supplement has 43 turns, not 31, and all of them duplicate thread files in the same directory. The README also says 90133B has 29 turns and 40 `<pre>` blocks; the supplement's 90133B portion has 35 fences, which is consistent once inline `<pre>` vs fence counting is taken into account.

### 1.3 Supersession map (which code variants supersede which)

All of these are in the 90133B lineage unless marked otherwise. "→" means "is superseded by".

- **Bus:** `LatentTensorBus` 1×128×4096 (1234) → `MultiChannelTensorBus` 3×128×4096 (1461) → `MultiChannelBiomatrixBus` 3×64×512 (1941) → `StratifiedBiomatrixBus` v1, focal 3×64×512 + symp 1×16 (3 used) + hippo 32×512 (2238) → v2, hippo 16, symp adds `last_winner`, drops `read_hippocampus` (2502) → `IntelligentStratifiedBus`, hippo 8, **broken sympathetic writes** (2824) → v3, hippo 16, symp slot 3 = `decay_rate` (3334) → `IntelligentMeshBus`, which is v3 renamed (3758).
  - Outside this file it continues as `AppleSiliconComputeBus`, symp slot 3 = `thermal_max` (`weft/almalga.md:326`, `weft/ahraz.md:96`, `weft/launch.md:399`).
  - Then **extracted** as `StratifiedAppleSiliconPlasm` in `weft/runtime/core/weft_plasm.py`. It has diverged: 4 focal channels, 4-float symp (tension, budget, step, thermal_c), a hippo ring pointer instead of a shift, a ctypes view, and it fixes the clobbering bugs.
- **Cell:** `ModelCell` (1295) → `MitoticCell` (1514) ‖ `ToolMutatingCell` (1751) → `MitoticToolWeaverCell`, which merges both (1979) → `PlasticOrganismCell` T23, which adds plasticity mask + LoRA + hippocampus bias and drops tools (2307) → T24, which drops the hippo bias (2564) → `PlasticConsolidatingCell`, which loads the genotype from disk and emits delta files (2880) → `PlasticOrganismCell` T27, which re-merges tools + bias + delta (3420) → T28, same plus a swallow-all try/except (3839).
- **Governor:** `TensionGridOrchestrator` (1355) → `EvolutionaryGovernor` (1570) ‖ `MembraneToolGovernor` (1816) → `NoveltyDrivenHarness` (2056) → `OrganismEcosystemGovernor` T23 (2380) → `UnifiedOrganismHarness`, multi-cycle + jev-ui (2619) → `SynapticDialGovernorHarness` (2945) → `OrganismEcosystemGovernor` T27, "production" (3510) → `DistributedOrganismHarness` (3910).
  - Outside this file: → `AppleSiliconEcosystemHarness` (`weft/almalga.md:438`; used by the 84ADC9 T8 sim at 4166).
  - **Extracted** descendants: `weft/runtime/mac/metal_loom.py` (`AppleSiliconLoomEngine`) and `weft_plasm.run_plasm_cycle`. Both are simplified to an in-process A/B loop with no subprocesses or sockets.
- **Fd helpers:** T20 (1720) = T21 (1925), which correctly return `fds[0]`. T27 (3400) and T28 (3821) **regress** to `return fds` (an array), so `open(injected_fd)` raises TypeError.
- **IC net:** 84ADC9 T38 `FractalInteractionNet` (4459) extends ERA/CON/DUP with `VLV` and `FRC`. The extracted `weft/runtime/core/weft_ic_vm.py` has only ERA/CON/DUP with real port wiring, so it **supersedes it on rigor**. The FRC/VLV ideas were not carried over.

**Latest vs best:** T28 (3730) is the latest and most feature-complete 90133B code, but T27 and T28 have the worst control-flow bugs (see §2 notes). The cleanest runnable members are T18 (combined), T20, and T24. For extraction, the existing `weft_plasm.py` / `metal_loom.py` are the best realization.

---

## 2. Code fragments

**Counts:** 37 fenced blocks in total = **17 Python (software)** + 20 `text` (ASCII diagrams/spec boxes, listed separately below). All 17 Python blocks pass `ast.parse`. Their failures are semantic, from indentation drift, not syntactic.

| # | file:lines | lang | identifier / claimed name | what it does | completeness | extracted? | system |
|---|---|---|---|---|---|---|---|
| P1 | supp:1234-1282 (90133B T18) | python | `LatentTensorBus` | POSIX shm float32 (128,4096) canvas; write/read torch tensors | near-complete (module part) | NOT EXTRACTED (ancestor of `runtime/core/weft_plasm.py`) | S1 Plasm/Organism runtime |
| P2 | supp:1292-1346 (T18) | python | `ModelCell(mp.Process)` | process reads bus, multiplies by random 4096² weights, clamps ±5, writes back | near-complete (needs P1 in same module) | NOT EXTRACTED | S1 |
| P3 | supp:1354-1423 (T18) | python | `TensionGridOrchestrator` + `__main__` | spawns 2 cells, monitors Frobenius norm, "Edge Snap" if >500 | complete-runnable when concatenated with P1+P2 | NOT EXTRACTED | S1 / S9 Tension Grid |
| P4 | supp:1461-1505 (T19) | python | `MultiChannelTensorBus` | 3-channel (input, cand A, cand B) shm bus | near-complete | NOT EXTRACTED | S1 |
| P5 | supp:1513-1561 (T19) | python | `MitoticCell` | child with base + Gaussian mutation weights writes to slot 1/2 | near-complete | NOT EXTRACTED | S1 / S3 |
| P6 | supp:1569-1647 (T19) | python | `EvolutionaryGovernor` | if norm>10, spawn A (0.005) / B (0.08), pick lower norm, promote to ch0, kill both | complete-runnable with P4+P5 | NOT EXTRACTED | S3 Evolutionary selection |
| P7 | supp:1710-1744 (T20) | python | `send_file_descriptor` / `recv_file_descriptor` | SCM_RIGHTS fd passing over AF_UNIX | complete (helpers) | NOT EXTRACTED | S2 Tool Membrane |
| P8 | supp:1750-1809 (T20) | python | `ToolMutatingCell` | dot(hidden, intent_weights) > 0.15 → sends `REQUEST_IO_TOOL`, receives fd, writes a line | near-complete | NOT EXTRACTED | S2 |
| P9 | supp:1815-1872 (T20) | python | `MembraneToolGovernor` | binds `/tmp/harness_receptor.sock`, opens `workspace_tapestry.txt`, injects fd | complete-runnable with P7+P8 (may block forever, see notes) | NOT EXTRACTED | S2 |
| P10 | supp:1909-2151 (T21) | python | "Evolutionary Tool-Weaving Collective": `MultiChannelBiomatrixBus`, `MitoticToolWeaverCell`, `NoveltyDrivenHarness` | merges A/B mitosis + fd tools + novelty score (alpha 0.4) | single-file, structurally complete, **buggy** | NOT EXTRACTED | S1+S2+S3 |
| P11 | supp:2222-2461 (T23) | python | "Autonomous Digital Organism Core": `StratifiedBiomatrixBus`, `PlasticOrganismCell`, `OrganismEcosystemGovernor` | focal/sympathetic/hippocampus bus; plasticity mask + rank-2 LoRA; novelty vs hippocampus; tension-dependent alpha | single-file, **buggy** | NOT EXTRACTED; concepts in `weft_plasm.py` (diverged) | S1+S3 |
| P12 | supp:2485-2718 (T24) | python | `UnifiedOrganismHarness` (+ bus v2, cell) | multi-cycle loop: randn "telemetry", min-norm selection, hippocampus append, terminal jev-ui sparkline | complete-runnable (timing-fragile) | NOT EXTRACTED; selection loop resembles `runtime/mac/metal_loom.py` | S1+S3+S4 jev-ui |
| P13 | supp:2810-3065 (T26) | python | `IntelligentStratifiedBus`, `PlasticConsolidatingCell`, `SynapticDialGovernorHarness` | genotype on disk `/tmp/organism_master_genotype.npy`; winner delta ×0.15 consolidated; decay `base*(1+1/T)*0.01` | single-file, **semantically broken** | NOT EXTRACTED; the formula survives in `metal_loom.py:56-57` (diverged: lora·loraᵀ, no mask) | S3 Synaptic Dial |
| P14 | supp:3307-3662 (T27) | python | "ASL // PRODUCTION-READY ORGANISM HARNESS": bus v3, fd helpers, `PlasticOrganismCell`, `OrganismEcosystemGovernor` | everything in P10–P13 combined | single-file, **multiple fatal bugs** despite the "production-ready" label | NOT EXTRACTED; concepts in `weft_plasm.py` / `metal_loom.py` | S1+S2+S3+S4 |
| P15 | supp:3730-4091 (T28) | python | "FULL MESHED & SI-BRIDGED ORGANISM CORE": `IntelligentMeshBus`, `DistributedOrganismHarness` | adds psutil telemetry → focal ch0 and a UDP 0.0.0.0:9999 listener that appends remote 512-float vectors to the hippocampus; `broadcast_mesh_vector` | single-file, **multiple fatal bugs** | NOT EXTRACTED; telemetry intent overlaps `runtime/mac/darwin_sysctl.py` (sysctl, not psutil) | S1–S5 |
| P16 | supp:4148-4268 (84ADC9 T8) | python | `mesh_cluster_simulation.py` / `LocalMeshSimulation` | Node Beta TCP listener (127.0.0.1:7778) receives 1 MiB weights, credits +45 "WEFT"; drives `AppleSiliconEcosystemHarness` from external `m1_max_harness` | fragment (depends on `m1_max_harness` = `weft/almalga.md:438` etc.) | NOT EXTRACTED | S6 Exo-Mitosis leasing |
| P17 | supp:4459-4602 (84ADC9 T38) | python | `FractalInteractionNet`, `CombinatorNode`, consts ERA/CON/DUP/VLV/FRC | toy "rewrite" over a list of id pairs; CON-FRC spawns ≤4 new CON-FRC pairs; prints a dashboard | runnable, but pseudocode-grade (no ports or wiring) | NOT EXTRACTED; `runtime/core/weft_ic_vm.py` is the rigorous IC VM (ERA/CON/DUP only) | S7 IC net |

### 2.1 Bugs and defects per fragment

These matter for any extraction decision.

- **P1–P3 (T18):**
  - `ModelCell.run` ends with `bus.close()`, which also **unlinks** the shm segment from inside a child (1276-1281, 1345).
  - `trigger_edge_snap` closes and recreates the bus, then the `finally` re-terminates (1401-1415).
  - The two cells read and write the **same single channel**, so they feed each other's output back.
  - Numeric check: initial norm ≈362 → ≈462 after one pass → ≈592 after two. The >500 "edge snap" (1392) is therefore all but guaranteed within about a second; it is a feedback-blowup artifact, not a safety signal.
- **P4–P6 (T19):**
  - The `base_weights_hash` parameter is unused (1518), so there is **no inheritance**: each child draws fresh random weights.
  - `time.sleep(0.1)` (1599) with the `spawn` start method plus a torch import plus 4096² randn means children are very likely not running yet. `out_A`/`out_B` would be zeros, the losses tie, and the B branch writes zeros to ch0. Not executed; inferred from timing.
- **P7–P9 (T20):**
  - Whether a tool is requested depends on a random sign: at step 3, `hidden[0]=5.0` × `intent_weights[0]`. If the sign is negative the cell never requests, and the governor blocks forever on `conn.recv` (1838).
  - The "Absolute Zero Privilege" claim (1878) is false. The child is an ordinary same-UID Python process with full filesystem and `os` access; no sandbox exists.
- **P10 (T21):**
  - Cleanup (`terminate`/`join`/`bus.close`/`server_sock.close`) is **indented inside the `else:` branch and inside the for loop** (2135-2145). If lineage A wins, children are never stopped and the run hangs at exit.
  - Each accepted connection serves one request and is then closed (2090-2101), but cells resend on every input change. Each cell also blocks on `recv` forever if `|intent| ≤ 0.02`.
  - **Selection math inverts the stated goal.** Fitness = 1/‖out‖ ≈ 0.006 (A) / 0.0013 (B). Novelty against a zero archive equals ‖out‖, so score ≈ 0.4‖out‖ (A ≈ 68, B ≈ 317 in simulation). The harness therefore **always promotes the larger-norm (higher-"tension") output**, i.e. lineage B, by construction (2111-2133).
- **P11 (T23):**
  - Same indentation drift: the homeostatic update and apoptosis sit inside `else` (2443-2455), so on an A win the children leak.
  - The hippocampus starts at zeros, so the same novelty-dominance applies.
  - **The plasticity mask does not protect anything.** Softmax over 512 near-equal row norms gives mask values of 0.91–1.00 (simulated: min 0.913, mean 0.958). The printed "Protected parameters: sum(mask<0.3)" (2347) is **0**. The mask is also by row and favors high-norm rows, the opposite of "shielding critical core invariants" (2469; spec 3157-3163).
- **P12 (T24):**
  - Novelty is dropped; selection is pure min-norm. This regresses from T23.
  - Spawns two new processes per cycle with a 0.12 s window. Children killed by `terminate()` may or may not reach `bus.close()` (which unlinks), a race that can orphan the segment name.
  - The prose cites "lines 78–80" for the ingestion code (2724); that code is actually block line 181 (file 2666).
- **P13 (T26):**
  - `write_sympathetic` **overwrites `self.symp_matrix` with Python floats** (2864-2866), and `read_sympathetic` returns `float(self.symp_matrix)` ×4 (2869). After priming, tension, budget, step, and decay all read as 0.05.
  - Indentation drift turns the post-selection block into a **`for … else:`**: the `else:` at 3038 aligns with `for` at 2984. Dashboard, sympathetic update, delta cleanup, and apoptosis therefore run once, after all generations. Every generation's cells keep running, and nested `for cell` sits inside `for p` (3049-3054).
  - `adaptive_decay_pressure` is undefined if the delta file is missing (3032-3033): NameError.
  - The prose cites "Lines 116–118" for decay (3072); it is actually block line 222.
  - `finally` deletes the "permanent" genotype file (3058), contradicting "permanently remembering its own successful behaviors" (3071).
- **P14 (T27, "production-ready"):**
  - In `__init__`, socket and bus creation are nested under `if not os.path.exists(self.weights_path)` (3520-3531). On a second run, `self.bus`/`self.server_sock` don't exist: AttributeError.
  - `recv_file_descriptor` returns an array (3413), so `open(array)` raises TypeError inside the cell.
  - Selection, scoring, and consolidation are nested inside the accept loop's `if signal…` (3575-3626).
  - `consolidated_core_matrix`/`delta_norm_val` are only defined when B wins (3611-3626), so an A win raises NameError at 3631.
  - Apoptosis is nested in the file-removal loop (3645-3648).
  - `finally` deletes the genotype (3654).
- **P15 (T28):**
  - `gather_silicon_telemetry` has `return` **inside** the `for i` loop (3979-3984), so it returns after i=3 with only dims 0–3 populated.
  - `recv` returns an array (3832); swallowed by `except Exception: pass` (3900).
  - Selection is nested in the accept loop (4021-4061).
  - `consolidated_core` is undefined on an A win (4039-4064).
  - The **`else:` at 4059 belongs to `if target_mesh_peer`**: with no peer (the default at 4090) the winning delta is discarded. Inverted logic.
  - Novelty is dropped entirely, despite 3728 claiming it is merged.
  - The broadcast sends `winning_delta.mean(dim=0)` (a weight-delta statistic), but the listener stores it as a memory embedding (3943-3946). Semantic mismatch.
- **P16 (84ADC9 T8):**
  - Node Beta listens on **7778** (4194), but `AppleSiliconEcosystemHarness.execute_outbound_exo_mitosis` connects to `(remote_ip, self.migration_port)` = 7777 (`weft/almalga.md:519`). That is Alpha's own receiver port (`almalga.md` bind at about line 478, `0.0.0.0`). **Beta never receives the payload**; Alpha "migrates" to itself.
  - The comment says threshold "< 160.0" (4245); the harness uses `< 360.0` (`almalga.md:616`).
  - The prose says Beta "runs a vector distance validation check" (4278), but the code only checks length (4217).
  - `mp = torch.multiprocessing.get_context('spawn')` (4265) does not set the start method.
  - Lease fee is 45 here (4222, 4278) vs 35 in 84ADC9 T1 (4118) and `almalga.md` (hosting_revenue = 35.0).
- **P17 (84ADC9 T38):**
  - Ports `p1`/`p2` are never used.
  - Only the ordered pairs (CON, ERA/FRC/VLV) are handled, so this is not symmetric.
  - Only CON–FRC pairs are ever created, so the ERA and VLV branches are dead code in the demo.
  - CON–FRC creates up to 4 new pairs per step: unbounded growth capped only by `max_steps`.
  - Tension and vault changes are arbitrary constants (3.1415×depth, +20 tokens).
  - `self.device` (mps) is unused, and the dashboard waveform is `sin` + `random` (4573-4575), not graph state.
  - Prose claims "32 GPU processing cores … millions of recursive mutations per second … zero-allocation" (4610-4611); the code is a single-threaded Python dict loop.

### 2.2 Text/diagram blocks (not software; spec-relevant)

20 blocks, the 90133B thread unless marked:

- ASL stack (201-237)
- Tension Grid compliance matrix (294-311)
- Firewall vs dampening trade-off (381-392)
- **Autonomy continuum T<0.3 / 0.3–0.7 / ≥0.7** (445-454)
- **PLL block layout** (468-483)
- Weight-space splicing lifecycle (621-641)
- "Weights over walls" (708-724)
- Hypersphere clamp (759-777)
- Bare-metal harness OS (804-832)
- Cellular collective (1024-1052)
- First-principles spec (1122-1139)
- Execution loop Polarization→Reaction→Mitosis→Homeostasis (1171-1193)
- Tool injection cycle (1680-1702)
- Microkernel endpoint (2768-2783)
- Biomatrix layout 3×64×512 / 1×16 / **32×512** (3100-3108)
- Plastic cell anatomy (3137-3149)
- Selection matrix (3179-3207)
- **Synaptic dial equation** (3247-3257)
- Inter-node tensor fabric (3687-3704)
- 84ADC9 T38 fractal envelope (4432-4447)

---

## 3. Ideas, claims, mechanisms

### 3.1 Lore and metaphor foundation (vision-language)

- **Namrask weaving = engineering** (106; reprised 133). Programming, engineering, and weaving treated as one continuous skill; this is the root metaphor of the whole corpus. *Category:* vision-language.
- **Warp / Weft / Heedle / Tapestry** (147-154, 241-268).
  - Warp = invariants (hardware, protocols).
  - Weft = adaptive agent threads.
  - Heedle = human–AI coupling interface. "Heedle" is the transcript's own spelling; a real loom part is a heddle.
  - Tapestry = ephemeral execution context that "unravels" after use.
  - *Category:* vision-language → engineering-contract. *Would be falsified by:* n/a (metaphor).
- **Multi-armed concurrent threading** (175-180): multi-agent orchestration modeled on a four-armed weaver. *Category:* vision-language.

### 3.2 Tension Grid (safety mechanism)

- **Kinetic Boundary Dampening** (315-321). Instead of denying access, increase the "resistance" (token cost) of an operation exponentially as an agent approaches an invariant. *Category:* mechanism.
  - *Would be falsified by:* an agent reaching a forbidden state anyway after paying the cost. Turn 6 itself identifies this as an **economic DoS vector** (396-398).
- **Structural Vector Shifting** (323-329): automatic counter-balancing of neighboring components. *Category:* mechanism, unspecified.
- **Edge Snap** (331-337): when a thread crosses its yield point, sever it, dissolve its state, and return resources. Trade-off: in-flight work is lost (400-404). *Category:* mechanism.
- **Haptic tension UI** (339-347): human feels system stress. *Category:* vision-language. **Self-refuted at 914**: "pure engineering sci-fi design language … enforced through rigid cryptographic checks, reward model gates, and loss function thresholds".
- **Statistical / hypersphere clamp** (652-658, 751-781, 850-855). Tension Grid is recast as a bound on weight distance from a signed checkpoint, with rollback past a delta limit. *Category:* mechanism / engineering-contract.
  - *Would be falsified by:* harmful behavior inside a small weight-distance ball, since distance is not semantics.
  - Partially implemented in the extracted runtime as `R_INVARIANT = 120.0` plus `verify_weight_update_safety` (`runtime/core/weft_plasm.py:23-30`).
- **In the code**, the Grid is the Frobenius norm of the shared bus (1388, 1605, 2111, 2682). This is not a weight distance, and it is driven by random inputs. *Contradiction* with spec 3177 ("checking geometric parameter distances").

### 3.3 Governance and accountability

- **Autonomy continuum governor** (439-458, diagram 445-454).
  - T<0.3: full autopilot (Level 4).
  - 0.3≤T<0.7: shared agency, haptic engagement.
  - T≥0.7: weave freezes; human override (Level 1).
  - *Category:* governance / engineering-contract. *Would be falsified by:* high-impact changes happening at low measured T, because T measures stress, not impact.
- **Paracausal Loom Ledger (PLL)** (462-498; spec 3283-3299).
  - Each mutation gets a block with a thread hash, T, an AI-vs-human % autonomy vector, a machine signature, and a human biometric/intent signature.
  - Green zone: single machine signature. Red zone: **dual signature** required.
  - *Category:* governance. *Would be falsified by:* attribution percentages that can't be computed objectively. No algorithm for "72% AI / 28% human" is given.
- **Time-travel debugging by re-weaving** (488; 665; 3295-3299). Replay signed weight diffs onto the base to rebuild the ephemeral state "molecule-for-molecule". *Category:* engineering-contract.
  - *Would be falsified by:* non-determinism. Every code fragment seeds with `os.getpid() + int(time.time())` (1533, 2000, 2326, 3441, 3855), so runs are **not reproducible**. This contradicts the replay claim.
- **Human-in-the-loop fatigue** (408-415): human cognition can't scale to thousands of threads; over-delegation leads to "machine dominance". *Category:* governance risk.
- **Weaver key as sovereign authority** (84ADC9 T12, 4317-4319): the user's "Weaver Private ECDSA Key embedded into `harness_config.json`" is required for consolidation. *Category:* governance. **SAFETY**, see §3.9.

### 3.4 External or "current-events" claims (unverified; flag for fact-check)

- **GPT-6 Astra / MIT CSAIL "Weight-Space Programming"** (607-609, 892).
  - Claimed: in early Nov 2026, it edited 0.016% of a target model's weights to excise bugs and wrote a game network's weights from scratch. T13 adds a "0.8B parameter model", "a Python kernel".
  - The user introduced the claim (604) and the model affirmed it as "verified, historic" (892). I have not verified it. *Category:* theory/claim.
  - *Would be falsified by:* no such paper or announcement existing.
- **jev-ui / "TypeSafe's Jev"** (696, 734, 899). Claimed to be a React framework exposing token probability distributions for generative UI. Unverified. The corpus later reuses "jev-ui" as a label for its own terminal dashboard (2643), which conflates the two.
- **Inkling 2 Small on Tinker / Thinking Machines Lab** (696-698, 906). Claimed: a $500-budget autonomous research agent that trained a forecasting model. Also a "594-billion-parameter hyper-matrix" (755) vs "Active Weights (17B)" (766). Unverified.
- **Related work** (553-581): DARPA IDAS; FAST (arXiv 1907.08695); AutoGen; Wasm sandboxing; "Sys framework" (arXiv 2604.15082); HACI (arXiv 2511.03733); *Dataflow Graphs as Matrices*. Plausible but should be checked; arXiv ids 2604.* and 2511.* are recent.
- **The model's own reality check** (T13, 883-923). It explicitly separates real primitives from extrapolation. The "codebase is dead today" framing is labeled an "intentional projection". This is the best grounding text in the file.

### 3.5 Post-application architecture (vision-language → roadmap-branch)

- **Weights as applications, OS as harness** (794-869).
  - Apps become LoRA/expert weight deltas.
  - The OS supplies curated perception and deterministic execution handlers. A model's "intent vector" for external actions is routed through hard-coded checks (848).
  - The UI is streamed from probabilities.
  - *Would be falsified by:* behaviors that cannot be expressed as small adapters, or safety that cannot be checked at the action boundary.
- **Practical roadmap** (T14, 941-971). Build harnesses, not apps: Wasm/micro-containers, safety at the platform layer, telemetry/eval loops, autonomy logging, LoRA/merging/activation engineering. *Category:* roadmap-branch. **Most actionable text in the file.**
- **Models as cells** (T16, 1014-1090).
  - Each cell = nucleus (LoRA expert) + membrane (mini-harness the cell can modify itself).
  - "Plasm" = latent-overlap consensus with α sensor / β architect / γ invariant guard (1069-1073).
  - Mitosis to specialize; apoptosis plus regeneration from the signed ledger.
  - *Category:* mechanism (vision-heavy). The **"cell holds the keys to its own membrane"** idea (1061) is safety-relevant: a self-modifying sandbox.
- **Four first principles** (T17, 1141-1163):
  1. Membrane = page-isolated memory + restricted ISA, with weights read-only from the inside.
  2. Metabolic scarcity = fixed compute/RAM/token budget; starvation leads to unraveling.
  3. Receptor signaling = shared latent tensor bus, no text.
  4. Genotype locked by loss invariants; phenotype adapted via child LoRA.
  - *Category:* theory / engineering-contract.
  - *Would be falsified by:* a model reading another model's hidden states without a learned adapter. Raw hidden states are not interoperable across models; the text never addresses this.
- **Execution loop** Polarization → Reaction → Mitosis → Homeostasis (1171-1198). *Category:* vision-language for a control loop.
- **After it's built** (T25, 2741-2789): homeostasis "customized to your silicon"; behavioral speciation across machines; autonomous tool accretion (cells write Wasm modules injected as fds); end-state is a Rust/C microkernel where "the weights become the OS". *Category:* roadmap-branch / vision. **Safety-relevant:** autonomous capability expansion with no human in the loop (2760).

### 3.6 Mechanisms realized in the code: what the name aspires to vs what the code does

| Name (bio vision-language) | Aspires to | What the code actually does |
|---|---|---|
| Membrane / process membrane | page-isolated, restricted-ISA sandbox (1145) | an ordinary `multiprocessing.Process`, same UID, full OS access, no seccomp/sandbox |
| Plasm / Latent Tensor Bus | sub-verbal model-to-model hidden-state exchange | numpy view over a named shm segment; random matrices in, random matrices out; `.copy()` on every read, so not "zero-copy" (1274, 1499) and not page-locked (no `mlock`) |
| Mitosis | specialization by cloning with variation | spawn 2 processes, each drawing **fresh** random weights (no parent inheritance until T26 loads a disk genotype) |
| A/B convergence / survival of the aligned | select behavior reducing friction | pick lower ‖output‖ (P6, P12, P13, P15) or larger ‖output‖ once novelty dominates (P10, P11, P14) |
| Novelty / anti-homogenization | resist monoculture (1897-1903) | mean distance to an archive that starts at zero, so it degenerates to ‖output‖ and swamps the 1/‖output‖ fitness |
| Plasticity mask / surgical LoRA | freeze core alignment, mutate only volatile parts | mask ≈ 0.91–1.0 everywhere (verified), i.e. a near-uniform full mutation scaled by a rank-2 product |
| Hippocampus | long-term vector DB, HNSW (2176) | 8/16/32 × 512 shift-register ring of mean vectors; added as a 0.02–0.05 bias |
| Sympathetic current | attention-mask-level awareness of global state | 1×16 float array; cells read it and ignore it (2352, 2599) |
| Dynamic Tool Membrane | permeability gated by weight intent | SCM_RIGHTS fd passing: real and correct in P7. The "intent" is a dot product of random vectors against a threshold; the harness "invariant check" is just a string match on `REQUEST_IO_TOOL`/`REQ_TOOL_n` (1842, 2093) |
| Synaptic consolidation (Hebbian) | bake successful behaviors into the genotype | `W += 0.15·delta_winner` |
| Intelligent decay / pruning | "use it or lose it" (2804, 3269) | **uniform** scalar shrink of all weights by `base·(1+1/T)·0.01`, which is not usage-dependent and so not Hebbian |
| Apoptosis / Edge Snap | quarantine and regenerate a corrupted cell | `terminate()`/`join()` of all children every generation |
| Homeostasis | system settles to equilibrium | nothing measures or converges; inputs are re-randomized each cycle (2666, 2988, 3561) |
| jev-ui | probabilistic generative UI | `os.system('clear')` + Unicode sparkline of a numpy row |
| Exo-Mitosis | migrate a cell context to a peer under thermal/budget stress | send 1 MiB raw weights over TCP; receiver credits a constant fee |
| FRC fractal node | clone and compress the parent graph into a low-rank point (4451) | append ≤4 new (CON, FRC) id pairs to a list |

### 3.7 Economics

- **Token valve / compute leasing** (4117-4120, 4137-4138, 4220-4226, 4278).
  - Hosts earn "WEFT" for executing migrated contexts: +35 (T1) or +45 (T8).
  - `VLV` node: +20 vault per CON–VLV (4556-4559).
  - On-chain counterpart: `executeExcisionValve` in `weft/runtime/ledger/WeftTokenTissue.sol`.
  - *Category:* economics. *Would be falsified by:* no verifiable proof that the host actually executed the work. The code does no verification (4217).
  - **Contradiction:** 35 (4118) vs 45 (4222).
- **"Self-monetizing token valve runtime"** as a user demand (4311). *Category:* economics / vision.

### 3.8 Provenance and prior art

- **Name origin** (84ADC9 T27, 4384-4409). The model says the "foundational name and core conceit of 'Weft' come from" Luca Berton's Weft language: LLMs and agents as primitives, durable execution via Restate, Rust + TypeScript, "O'Saasy License".
  - Search snippets in the same file show **two** possibly distinct real projects: lucaberton.com "Weft" (4338, 4368, 4378) and GitHub `WeaveMindAI/weft` (4368, 4378). The model may be conflating them.
  - **Contradiction:** the 90133B genesis thread shows "Weft" arising from the user's Destiny loom metaphor (133-154) before any Berton reference. The attribution at 4386 is therefore at best "a same-named project exists". *Category:* governance (IP/attribution).
  - *Would be falsified by:* checking dates and whether the user ever saw Berton's post before 90133B T3.
- **Real vs. extrapolated comparison table** (4403-4409): a useful comparison of real Weft vs the corpus's IC/ARM64/Stylus/M1 framing.

### 3.9 Safety-relevant items (locations only; no secret values are copied)

- **4319:** advises embedding the "Weaver Private ECDSA Key" in `harness_config.json`. Plaintext private-key-in-config anti-pattern. No key value appears in this file.
- **4118:** refers to validating against "`weaver_secret` keys". The default secret strings are **hardcoded** at `weft/almalga.md:439`, `:634` and `weft/README.md:869`, `:1056`, and are also used as seeds (e.g. `runtime/core/weft_plasm.py:190` hashes a fixed passphrase). Those values are not reproduced here.
- **4110, 4124:** offers to push the Solidity triad to a **live testnet** via `web3.py`.
- **4297, 4326, 4617:** offers a "**live broadcast transaction pass**" (`ledger_migration.sh`) to "permanently lock"/"anchor" watermarks on-chain. Irreversible on-chain action proposed casually.
- **4125:** offers a load generator to **force an artificial thermal spike (>80°C)** on the user's MacBook. Hardware-stress risk.
- **3938-3946:** UDP listener bound to **0.0.0.0:9999**. Unauthenticated: any host on the network can inject vectors into the hippocampus, which feeds cell inference. An injection vector.
- **4137-4138:** prose says nodes bind **0.0.0.0:7777/7778**. P16 code binds 127.0.0.1 for Beta (4194), but the harness it imports binds 0.0.0.0:7777 (`almalga.md`, about line 478) and accepts 1 MiB weight payloads from anyone.
- **Predictable `/tmp` paths:** sockets `/tmp/harness_receptor.sock` (1818), `/tmp/harness_evolutionary.sock` (2059), `/tmp/asl_harness_receptor.sock` (3514), `/tmp/asl_meshed_receptor.sock` (3914). Weight files `/tmp/organism_master_genotype.npy` (2948), `/tmp/asl_master_genotype.npy` (3513), `/tmp/asl_meshed_genotype.npy` (3913), `/tmp/m1_max_node_*_weights.npy` (4177-4178). Each pre-removes an existing path (`os.remove`) and loads `.npy` from a world-writable directory: symlink/TOCTOU and tampering risk.
- **Fixed shm names** (e.g. "plasm_bus", "asl_organism_matrix"). Attach-if-exists (`except FileExistsError: attach`) means a stale or hostile segment of a different size gets silently reused.
- **Autonomy-expansion design intent:** cells "given the keys to [their] own membrane" (1061); autonomous tool accretion and Wasm injection without a human patch (2759-2760); "weights become the operating system" (2789). Safety-relevant design direction.
- **No credentials, RPC URLs, or mainnet addresses** appear in this file. External URLs are only news/links (553-580, 607, 696, 2-line search dumps at 4338-4630).

### 3.10 Explicit contradictions and inconsistencies

1. **Haptic Tension Grid:** presented as architecture (339-347; 3293) vs "pure engineering sci-fi design language" (914).
2. **Hippocampus depth:** 32×512 in spec diagram 3106 and P11 (2246), vs 16 in P12/P14/P15 (2510, 3342, 3763), vs 8 in P13 (2839) and `weft_plasm.py` (hippo_depth=8).
3. **Sympathetic slot 3:** η "consolidation velocity" in spec (3125) vs `last_winner` (2545) vs `decay_rate` (3377, 3798) vs `thermal_max` (`almalga.md:362`; used at 4246) vs `thermal_c` (`weft_plasm.py:155`).
4. **Novelty:** the spec says novelty alpha drops when tension is critical (3225), but P12, P13, and P15 **have no novelty at all**, while 3728 claims T28 merges "Anti-Homogenization Novelty Scoring".
5. **Fitness target:** "spatial matrix divergence from the target zero-friction alignment profile" (3211), while the actual winner under novelty dominance is the **largest** norm (P10, P11, P14). The stated objective is inverted in practice.
6. **Plasticity mask** "0.0 = Frozen Invariant" (2332; 3163) vs computed values of ≈0.91–1.0 (§2.1 P11).
7. **"Permanently remembering"** (3071, 3265) vs `finally` deleting the genotype file every run (3058, 3654, 4083).
8. **Zero-privilege membrane** (1878, 3153) vs a plain same-user process.
9. **Lease fee** 35 (4118) vs 45 (4222, 4278); **budget threshold** "<160" (4245) vs `<360` (`almalga.md:616`).
10. **Node binding** 0.0.0.0:7778 (4138) vs 127.0.0.1:7778 (4194); migration target port 7777 vs Beta 7778, so the sim cannot work as described.
11. **"Production-ready"** (3305, 4457) vs the fatal bugs in §2.1. "Lines 78–80" (2724) and "Lines 116–118" (3072) are wrong references.
12. **"32 GPU cores … millions of mutations/s … zero-allocation"** (4611) vs a single-threaded Python loop with unbounded node allocation.
13. **84ADC9 T1** says the Solidity triad includes `TensionGovernor.sol` (4117). The repo's `weft/runtime/ledger/` has only `WeftTokenTissue.sol` and `ProvenanceRegistry.sol`; `TensionGovernor.sol` is not extracted, though it exists in prose at `thread1-weft-main-84ADC9.md:1251`.
14. **Header** "31 turns" (3) vs 43 present; and "not individually copied" vs all being verbatim in the sibling thread files.
15. **Name origin:** Destiny-loom genesis (133-154) vs "come from an actual project" (Berton, 4384).

---

## 4. Candidate software systems

**S1 — Plasm / Organism runtime (stratified shared-memory bus + process cells)**
- *Purpose:* host a population of "cells" exchanging float tensors through a named POSIX shm segment with Focal (input + 2 candidate tracks), Sympathetic (scalar status), and Hippocampus (vector ring) regions.
- *Inputs:* telemetry tensor (randn, or psutil in T28) written to focal ch0. *Outputs:* candidate tracks ch1/ch2, sympathetic scalars, hippocampus vectors.
- *Interfaces:* S3 selects over the tracks; S4 renders; S5 fills ch0 and syncs the hippocampus; S6 migrates weights. Aywa daemon/dashboard: `runtime/aywa/weft_daemon.py` also creates a 64-byte shm.
- *Fragments:* P1, P2, P4, P5, P10–P15.
- *Dependencies:* Python 3.8+, torch, numpy, `multiprocessing.shared_memory`.
- *Status:* **already realized and superseded** by `weft/runtime/core/weft_plasm.py` (`StratifiedAppleSiliconPlasm`, diverged, cleaner). Not separate from S3; the bus and governor are one program in every variant.

**S2 — Dynamic Tool Membrane (capability injection via SCM_RIGHTS)**
- *Purpose:* cells start with no capabilities; the harness grants open file descriptors on request. This is genuinely a capability model, effectively object-capability: authority conveyed by an unforgeable handle, which matches the Edera OCAP search result at 4630.
- *I/O:* request string over AF_UNIX in, fd via ancillary data out.
- *Interfaces:* S1 cells; it would be the natural enforcement point for the Tension Grid / PLL.
- *Fragments:* P7, P8, P9, and embedded copies in P10, P14, P15 (P14/P15 regress `recv`).
- *Dependencies:* POSIX only (Linux/macOS).
- *Status:* NOT EXTRACTED. **The most sound, reusable mechanism in the file**, but it needs a real sandbox (seccomp/sandbox-exec, separate UID) to mean anything.

**S3 — Evolutionary selection & consolidation engine ("Convergence Governor", "Synaptic Mutation Dial", "Intelligent Decay")**
- *Purpose:* each generation, spawn conservative and exploratory variants (rank-2 LoRA × mask), score them by fitness ± novelty, promote the winner, consolidate the delta into the genotype, and apply decay.
- *I/O:* genotype `.npy`, bus tracks, sympathetic tension in; updated genotype, hippocampus append, telemetry out.
- *Interfaces:* S1, S4, S5 (mesh broadcast of the winning delta), S8 (PLL should log the deltas), S9 (safety check before acceptance; done in `weft_plasm.verify_weight_update_safety`).
- *Fragments:* P3, P6, P10–P15; equations at 3213, 3219, 3223, 3252-3255, 3263, 3273, 3277.
- *Status:* extracted in simplified form as `weft/runtime/mac/metal_loom.py` (min-norm, 0.15 consolidation, 0.04 decay; uses lora·loraᵀ, no mask) and `run_plasm_cycle` in `weft_plasm.py` (novelty 0.35, safety gate, watermark).

**S4 — "jev-ui" terminal dashboard**
- *Purpose:* human view of generation, tension, budget, winner, norms, and a sparkline.
- *Fragments:* `draw_jev_ui` in P12 (2629-2657), P13 (2963-2980), P14 (3533-3553), P15 (3986-4005), P17 (4570-4591).
- *Interfaces:* reads S1/S3 state. The conceptual ancestor of the **Aywa browser dashboard** (`runtime/aywa/index.html`, `dashboard_layout.wgsl`, SYM-2P telemetry), which replaces the terminal.
- *Status:* trivial; NOT EXTRACTED; superseded by Aywa.

**S5 — Mesh fabric + Hardware Peripheral Bridge**
- *Purpose:* (a) cross-node hippocampus sync ("Cross-Splicing Fabrics", spec RoCE v2 at 3683; code is raw UDP); (b) map host telemetry (CPU %, memory %, disk IO) into focal ch0.
- *Fragments:* P15 (3936-3984); spec 3672-3722.
- *Dependencies:* psutil, sockets.
- *Interfaces:* S1; Mac harness `runtime/mac/darwin_sysctl.py` (sysctl-based, extracted) covers (b) on macOS; S6.
- *Status:* NOT EXTRACTED. The mesh part is unauthenticated (see §3.9) and is separate in concept from the telemetry bridge.

**S6 — Exo-Mitosis compute leasing / local mesh cluster simulation**
- *Purpose:* under thermal or budget stress, a node ships its weights to a peer, and the peer charges a lease fee in "WEFT".
- *Fragments:* P16 (+ `AppleSiliconEcosystemHarness` from `weft/almalga.md:438`); prose at 4113-4120, 4135-4140, 4276-4278.
- *Interfaces:* ledger contracts (`runtime/ledger/WeftTokenTissue.sol` `executeExcisionValve`; `ProvenanceRegistry.sol` for watermark provenance); S1/S3.
- *Status:* NOT EXTRACTED. Broken as written (port mismatch). The economics live mostly in other files.

**S7 — Fractal Interaction Combinator net (FRC/VLV extension)**
- *Purpose:* extend Lafont IC with VLV (taxation) and FRC (self-similar expansion) agents.
- *Fragment:* P17; grammar diagram 4432-4447; node definition 4451.
- *Interfaces:* the IC VM `runtime/core/weft_ic_vm.py` (rigorous ERA/CON/DUP with ports, trace root); widget `browser-sources/widgets/05-interaction-combinator-net.*`.
- *Status:* NOT EXTRACTED. It is a toy that shares only constant names with the IC VM, not logic. VLV and FRC appear in many other corpus files (`process.md`, `ahraz.md`, `mugetsu.md`, `pcoom.md`, `dissertation-mac.md`, `whitepaper.md`, …), so the authoritative definitions are probably elsewhere.

**S8 — Paracausal Loom Ledger (PLL) / accountability log**
- *Purpose:* signed per-mutation log with an autonomy vector and dual signature in the red zone; weight-diff replay.
- *Fragments:* none in code. Spec at 462-498, 665, 3283-3299; block layout 468-483.
- *Interfaces:* S3 (deltas), S9 (zone), ledger `ProvenanceRegistry.sol`, IC VM trace root (SHA256/Poseidon2 in `weft_ic_vm.py` docstring).
- *Status:* **spec only**. A natural separate system.

**S9 — Tension Grid / Autonomy Governor**
- *Purpose:* map stress T to an autonomy level (thresholds 0.3/0.7), freeze plus human override, hypersphere clamp on weight drift, Edge Snap rollback.
- *Fragments:* the T18 threshold at 1392 only; spec 286-347, 439-458, 751-781, 3175-3229.
- *Status:* partly realized as `R_INVARIANT` + `verify_weight_update_safety` in `weft_plasm.py`. Shares the threshold logic with S3; the governance part (human override) is unimplemented.

**S10 — Weight-space Harness OS / microkernel** (vision only)
- Spec 794-855 and 2764-2789. No code; a roadmap branch.

**S11 — Repo contributor analytics** (requirements only; 6C083A T28, 4648-4652)
- Metrics: maintainer vs outside LoC, label sharing, concentration, contributor quality, contributor capture across OSS.
- Likely belongs with `runtime/aywa/github_harvester.py` / "org_tension" (`runtime/core/selftest.py:199`). Unanswered in the transcript.

---

## 5. Documents implied

- **"Architectural Specification: The Agentic Software Loom (ASL) — A First-Principles Manifesto for Post-Application Computing via Cellular Weight-Space Collectives"** (90133B T27, 3080-3305), plus **§8 "Advanced Distributed Architecture"** and **§9 "Refactored Production Blueprint"** (T28, 3672-3728).
  - **Closest to a finished white paper/spec** in this file. It has an executive summary, layered sections 1–7 with equations, then distributed extensions.
  - Needs: reconciliation with the extracted runtime (dimensions, sympathetic fields); removal of "production-ready" claims; a vision-vs-mechanism split per §3.6.
- **Design-rationale / trade-offs memo** (T6, 357-421). Near-complete: ephemerality vs persistence, non-determinism, dampening-as-DoS, Edge Snap loss, human fatigue.
- **Governance spec: autonomy continuum + PLL + dual-signature** (T7, 431-498; T27 §6). Needs a concrete attribution algorithm, key management, and a log schema. The T14 roadmap item at 978 explicitly calls for a "structural schema for the Paracausal Loom Ledger".
- **Reality-check / claims register** (T13, 883-923). Ready-made basis for a "status of claims" appendix that separates real, extrapolated, and design-fiction content. External items (Astra, jev-ui, Inkling 2) need citation verification.
- **Roadmap / mission statement** (T14, 941-971: immediate harness, mid-term intent/telemetry, frontier weight-space). Near-complete. Its "How to Code Tomorrow" table (966-971) is publishable as is.
- **Related-work section** (T9, 548-592). Needs citation checking.
- **First-principles cellular spec** (T17, 1118-1198). Supplies the four invariants for a "Membrane / Metabolism / Receptor / Genotype" spec.
- **Post-build lifecycle / roadmap branch** (T25, 2741-2789): homeostasis, speciation, tool accretion, microkernel. A roadmap-branch doc; needs safety review.
- **Prior-art & naming note** (84ADC9 T27, 4384-4409). The corpus needs an explicit **IP/attribution document**: relation to Luca Berton's Weft and `WeaveMindAI/weft`, Lafont IC / HVM2 / Bend prior art (search dumps at 4358, 4368), and Destiny/Bungie lore as inspiration only.
- **Tool-membrane / capability-security spec** (implied by T20, 1670-1880, and T27 §4, 3233-3239). Worth writing properly as an OCAP design: fd passing plus a real sandbox.
- **Repo analytics requirements** (6C083A T28, 4648-4652). A one-paragraph spec seed.
- Promised but absent here (in other files): `harness_config.json`, `bootstrap_loom.py`, `test_loom_lifecycle.py`, `stylus_bootstrap.sh`, `darwin_parser.py`, `m1_max_harness.py`, `ledger_migration.sh` (listed at 4286-4291, 4297).

---

## 6. Open questions / gaps

1. **Plasm protocol** (1102) is never specified. There is no wire format, no versioning, and no answer to how heterogeneous models could read each other's raw hidden states (they can't without learned adapters). The code only exchanges random matrices.
2. **Membrane isolation** (1145, 1208, 3153) is unimplemented. No sandbox, seccomp, sandbox-exec, Wasm, or UID separation. Wasm is promised repeatedly (945, 1102-1103, 2760) and never used.
3. **"Intent vector" decoding** (848, 1672) is a scalar dot-product threshold. The harness "invariant check" is a string compare (1842, 2093). Nothing describes what a real safety validation would check.
4. **PLL** has no implementation, signing scheme, key management, or method for computing the AI-vs-human percentage (476-477). The dual-signature human gate is never coded.
5. **Determinism for replay** contradicts the pid+time seeding in every cell (§3.3).
6. **Tension (T)** has no defined semantics: it is the Frobenius norm of whatever is on the bus. The autonomy thresholds 0.3/0.7 (449) are on a 0–1 scale, but code tensions are ~10–800 (simulated). The scales are never reconciled.
7. **"Fitness = distance to zero target"** has no task meaning. With random inputs there is no task, so "homeostasis" (1198, 2746) is undefined and unmeasurable.
8. **Real models** (Llama-3-8B, Phi-3, ONNX 1.5B; 1288, 1438, 1661, 1888) are never wired in. All "weights" are `randn·0.02`.
9. **Hippocampus as an HNSW/vector DB** (2176) became a shift register. There is no retrieval, only a mean bias.
10. **Mesh** is specced as RoCE v2 (3683) but is UDP with no authentication, ordering, or integrity. The "Cross-Node Novelty Vector" (3708) is not computed, and remote mitosis triggering (3708) is not implemented.
11. **Hardware bridge** (3714-3722) promises per-core frequency, page faults, cache misses, thermals, and packet drops. The code reads only cpu%, mem%, and cumulative disk bytes (cumulative, not a rate, despite "change rate velocities" at 3969), and returns early (3984).
12. **Exo-Mitosis sim** depends on the external `m1_max_harness` and cannot deliver to Node Beta as written. Watermark validation is claimed (4218, 4278) but absent.
13. **FRC semantics** ("clone entire parent graph, compress to low-rank coordinate", 4451) have no algorithm. There are no port-level rewrite rules for VLV/FRC, so it is unclear how they compose with the extracted `weft_ic_vm.py`.
14. **External factual claims** (GPT-6 Astra, MIT CSAIL paper, jev-ui, Inkling 2/Tinker, arXiv 2604.15082, 2511.03733) need verification before any document cites them. T13 asserts them as "verified" without sources beyond links.
15. **Self-modifying membranes and autonomous tool accretion** (1061, 1079, 2759-2760) are proposed without any review gate. That conflicts with the T7 governor and the T14 "hardcode safety at the platform level" principle (946).
16. **Supplement provenance:** the README and header claim 31 turns "not copied". In fact there are 43 turns and the file is fully redundant with `browser-sources/thread*.md`. Before ingestion, decide whether it should be dropped or regenerated as just the turns absent from the top-level `weft/*.md` corpus.
17. **Unanswered prompts:** 84ADC9 T69 "how do I communicate the entire breadth and depth … to other agents/humans" (4634) got no answer; it is the meta-question this mapping exercise answers. 6C083A T25 and T28 also failed.
