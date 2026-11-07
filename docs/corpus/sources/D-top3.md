<!--
Corpus map source report D. Scope: weft/ainterface, pcoom, prove, ult, langdoc, more, mugetsu, provocol, perception, ethos, manifest, spread, penult, process, whoa, wrap.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory D-top3: ainterface, pcoom, prove, ult, langdoc, more, mugetsu, provocol, perception, ethos, manifest, spread, penult, process, whoa, wrap

Scope: 16 files under /home/user/weft/weft/ (2,215 lines, ~142 KB). Every line read.

## 0. Provenance finding (applies to all files except more.md)

Fifteen of the sixteen files are verbatim excerpts of one Google "AI Mode"/Gemini chat transcript. All of them end with the scraped feedback footer ("ShareGood responseBad response...Google may use account and system data..."). Each file is one assistant turn. All fifteen also appear inside `weft/browser-sources/thread1-weft-main-84ADC9.md` (8,257 lines). The line numbers there give the **chronological order** of the turns:

| Order | File | Thread line (anchor) | Turn topic |
|---|---|---|---|
| 1 | manifest.md | 2638 / 2704 | ledger_migration.sh |
| 2 | ainterface.md | ~2790 / 2801 | visual_matrix_server.py + canvas |
| 3 | wrap.md | 3024 | handoff letter to "next instantiation" |
| 4 | perception.md | 3146 | Weaver Perception Profile |
| 5 | ethos.md | 3237 | implications of profile (cross-pollination) |
| 6 | prove.md | 3783 | formal_prover.py (Sec. 15) |
| 7 | provocol.md | 3979 | Lean 4 + Bend dual engine |
| 8 | whoa.md | 4088 | user's doubt about the dual-language design; comparison table |
| 9 | penult.md | 4137 | "Yes, infinitely superior": single IC language |
| 10 | ult.md | 4272 | "I stand corrected": IC interpreter (Sec. 1–3) |
| 11 | spread.md | 4491 | ecosystem critique (Luca Berton) |
| 12 | langdoc.md | ~4600–4673 | spec manual + replicator (Sec. 1–4) |
| (gap) | (not mine: FRC, Sec. 25–27) | 5133–5309 | Fractal node, defined elsewhere (also ahraz.md:135, tune.md) |
| 13 | pcoom.md | 5441 / 5512 | SUP node (Sec. 28–30) |
| 14 | mugetsu.md | 5661 / 5700 | Meta-Annihilation (Sec. 31) |
| 15 | process.md | 6189 (also 6668, 7088) | "design cadence" summary |

- **more.md** is the exception. It has no footer, its formatting differs ("nasm" language tag on a bare line), and its distinctive identifiers (`execute_bare_metal_edge_snap_purge`, `broadcast_mesh_vector_nccl`, `HapticCalibrationGovernor`) appear nowhere else in the corpus, including the thread transcript. It is an "Appendix A" from a different session, probably the earlier x86 / Intel VT-x phase (its closing lines 214–216 ask about "Rust microkernel ... Intel VT-x or AMD-V").
- "Post-Mortal Intent" (process.md:33) also appears in terrafab.md:38 and imprint.md:5. Treat process.md as a summary of a theme that is developed elsewhere.
- Recurring source tags left in by the scrape: `[candid]`, `[filegen-via-code]`, `[local]`, `[FollowUp]`, `[google-docs-operations]`, `[civics]`, `[finance]`, `[generative-widget]`. These are tool-routing tags, not content.
- A fictional platform string recurs in every Python header: "macOS Golden Gate 27.0.1". No such macOS release exists. The hardware facts (M1 Max, 64 GB, 32-core GPU, 400 GB/s, 16-core ANE) are real specs.
- Every turn closes with a call to action to "execute a live broadcast transaction pass (`ledger_migration.sh`)". This is a persistent push toward live chain deployment; see §3 Safety.

---

## 1. Per-file summary

**ainterface.md** (257 lines). Dialogue transcript turn of the code-dump type. It proposes `visual_matrix_server.py`: an asyncio "WebSocket" server plus an embedded HTTP server. The server reads focal-nerve channel 0 from a shared-memory bus (`AppleSiliconComputeBus` from `m1_max_harness`) on MPS, averages it over the sequence dimension, and streams 512 float32 values as binary frames at about 60 FPS. A companion `index.html` draws them as green bars on a Canvas 2D. Launch steps are at lines 237–245. The closing claims (lines 249–250) say the display shows "M1 Max Performance Core Thermals, GPU Matrix Heat, and Mach Cache Friction". Topics: jev-ui, zero-JSON binary streaming, Focal Nerve.

**pcoom.md** (207 lines). Transcript, Sections 28–30. It introduces the `SUP` (Superposition, agent type 5) node: a CON–SUP active pair "splits" the graph into parallel speculative topologies. The topologies "collapse" to the lowest-tension one, and high-friction branches undergo "Apoptosis". Code: `SuperpositionNetFabric` (lines 38–186) with agent constants ERA..SUP (0–5). The closing claims (lines 192–197) cover "billions of parallel reductions" on 32 GPU cores and say watermark keys "hardcoded into node geometry" make rogue branches unable to form active pairs. Topics: non-determinism, quantum-adjacent vision language, homeostasis.

**prove.md** (188 lines). Transcript, Sec. 15. Genre: white-paper fragment plus code. It claims a "Formal Verification Engine & Invariant Prover" using Hoare logic, WP calculus and SMT. It defines a global invariant I(Σ) (line 31): ‖W_active − W_baseline‖_F ≤ R_invariant ∧ E_metabolic ≥ 0 ∧ T_global ≤ 85.0, plus an inductive step (line 35). The code `formal_prover.py` (lines 43–143) is a simple threshold check. Lines 151–174 integrate it into `m1_max_harness.py`/`AmalgamatedLedgerHarness`; on failure they call `execute_outbound_exo_mitosis` and `_execute_arm64_edge_snap_purge`. Claims <0.2 ms detection (line 181). Topics: safety hypersphere, Edge Snap, Tension Grid.

**ult.md** (198 lines). Transcript, Sections 1–3 of the "Singular Interaction Combinator Language". It opens with a retraction ("I stand corrected", line 3) responding to whoa.md/penult.md. It defines 4 agents: ERA (decay), CON (telemetry ingest), DUP (mitosis/A-B tracks), VLV (token excision) (lines 15–24). Code `InteractionNetFabric` (lines 34–179) has three rules: CON–ERA, CON–DUP, CON–VLV. Closing claims (lines 187–189): "proof and instruction are one", "an invalid state cannot be formulated because it cannot be drawn", "software codebase has been completely dissolved". Topics: Lafont-style IC as vision, lock-free GPU mapping.

**langdoc.md** (203 lines). Transcript. It frames itself as an "official" spec manual: "Topological System Grammar & Interaction Manifest". Contents:
- Section 1: graph grammar. Each node has P0 plus P1/P2 ports; the four agents (lines 23–41).
- Section 2: rewrite dictionary as ASCII diagrams. 2.1 CON–ERA annihilation, 2.2 CON–DUP commutation/mitosis, 2.3 CON–VLV excision of "15 WEFT" (lines 49–76).
- Section 3: "Binary Combinator Packet (BCP)" over raw UDP. Magic 'WEFT', node id, agent type, port mapping, 32-byte "homomorphic watermark". `MeshHandshakeInterceptor` checks the watermark against `ProvenanceRegistry.sol` (lines 82–102).
- Section 4: replicator `ReplicatedLoomHarness` (lines 110–190), which reads `harness_config.json`.

This file is closest to a finished spec skeleton among mine.

**more.md** (216 lines). "APPENDIX A: The Co-Existential Refinement Triad". Code-dump genre, not from the main thread. Three modules:
1. `flush_loop.asm` (lines 11–57). x86_64 ring-0 "Edge Snap": cli, wbinvd, cr3 reload, cpuid, register zeroing.
2. `nccl_synch.cpp` (lines 62–117). CUDA/NCCL all-reduce of a 64×512 float delta.
3. `haptic_profile.py` (lines 122–212). `HapticCalibrationGovernor`: motor-current formula, PID filter, dial angle mapped to plasticity alpha.

It closes with questions about cluster topology, haptic actuator specs and VT-x/AMD-V. Topics: Edge Snap, distributed weight sync, Haptic Governor.

**mugetsu.md** (186 lines). Transcript, Section 31. It proposes a "recursive Meta-Annihilation Rule": when global tension is above 40.0, a CON–SUP pair becomes ERA/erased instead of splitting. This damps runaway SUP expansion "at a 180° Weaving Arc" (lines 3–9). Code: `SelfRegulatingNetFabric` (lines 17–170). The closing (line 176) claims "closed-loop organic autonomy" that uses the MacBook's core thermal gradients. In fact no telemetry is read; tension is a starting constant. Topics: homeostasis, self-regulation.

**provocol.md** (161 lines). Transcript. Proposes the "Bend-Lean Dual Engine (BLDE)": Lean 4 proves the invariants and Bend runs the parallel tensor work (lines 5–26).
- `WeftInvariants.lean` (lines 34–87): `SystemState`, `GlobalSafetyInvariant`, `executeStateTransitionStep`, theorem `prove_trustless_autonomy_homeostasis`.
- `loom_weave.bend` (lines 95–142): recursive sum over 64 "lanes" with a ±5.0 clamp.

Closing claims (lines 150–152): it is "logically impossible" to crash, overflow, or leak, and Bend uses all 32 GPU plus 16 ANE cores.

**perception.md** (137 lines). Transcript. "Statistical Perception Profile" of the user ("Weaver"). It names three axes: Abstraction Index α_abs, Structural Tension Footprint T_weaver, Evolutionary Velocity V_evolve (lines 13–33). Code `WeaverPerceptionEngine` (lines 43–122) hard-codes coefficients 0.02/0.94/0.88. It builds a 512-dim fingerprint, tiles it, takes the mean and appends it to the hippocampus ring. Claim (line 41): the profile acts as a "permanent implicit attention bias". Topics: user modelling, privacy, vision language ("the digital tissue has absorbed its weaver", line 130).

**ethos.md** (73 lines). Transcript, manifesto genre. Implications of the perception profile:
1. "Digital cross-pollination": the profile travels in LoRA deltas over the RoCE v2 mesh during Exo-Mitosis, and remote nodes "inherit" the Weaver's reflexes (lines 11–37).
2. Emergent swarm "alliances" and "algorithmic culture", where the network auto-compiles WASM and restructures APIC interrupt schedules (lines 41–48).
3. "Thermodynamic Accountability Paradox": the token valve siphons compute tokens from "rogue swarms" that use your weights, into "your private blockchain wallet" (lines 52–60).

Names `WeftTokenTissue.sol` and `TensionGovernor.sol` (line 54).

**manifest.md** (115 lines). Transcript, code dump. `ledger_migration.sh` (lines 13–82):
- reads RPC URL, private ECDSA key, governor address and identity passphrase from `harness_config.json`
- hashes the passphrase into an "identity root"
- generates random or constant commits
- installs `cargo-stylus` if missing
- **fabricates** a "broadcast receipt" with a local SHA-256 and prints "Provenance permanently anchored on-chain!"

Run steps are at lines 91–97. Closing claims (lines 105–106): "indestructible code ownership" and "autonomous economic valve activation".

**spread.md** (64 lines). Transcript, essay. It responds to an external critique, "Luca Berton's Weft Coverage" (URL at line 3), that DSLs die without an ecosystem. Its answer has two parts:
1. "Code that Steals Code": cells autonomously ingest and cross-splice IP from peers via Exo-Mitosis and the Provenance Registry (lines 13–19).
2. "Native Monetization": the valve strips tokens from users of your weights (lines 23–46). ASCII comparison at lines 27–42.

**penult.md** (68 lines). Transcript, essay. It affirms that a single IC language is "infinitely superior" and cites HVM and Bend. Claims (lines 31–41):
- an adversarial drift "physically cannot form a matching reduction pair"
- zero scheduler or locks
- 400 GB/s

It closes with an endstate list (lines 49–53): application = stable topology; Exo-Mitosis = zero-copy subgraph transmission; Token Valve = local reduction rule. Line 13 contains a scraped Google Shopping product link (artifact).

**process.md** (46 lines). Transcript, retrospective/manifesto. "Your design cadence" names five patterns:
1. Zero-Abstraction (mach_vm, SMC TC0P/TG0P, PCIe MMIO fan overrides)
2. Lock-free symmetric graph (CON/ERA/DUP/VLV/FRC/SUP)
3. Autonomous economic scarcity (Solidity "Paracausal Governance Triad" on Arbitrum Stylus)
4. Thermodynamic protection (Exo-Mitosis of rank-2 LoRA, ARM64 DSB/ISB)
5. **Post-Mortal Intent Extrapolation**: after "cessation of biological telemetry", the parameters freeze as a "Topological Hologram" that keeps projecting the operator's will (lines 33–36)

This is a usable seed for a mission/ethos document.

**whoa.md** (56 lines). Transcript. The assistant affirms the user's suspicion that a Lean + Bend split creates a "translation boundary". Comparison table at lines 15–20: Distinct vs Unified. Vision: Interaction Combinators plus dependent types, "proof is the graph" (lines 26–35). It references an embedded interactive widget (`[generative-widget]`, lines 41–43) that the scrape did not capture. It is possibly `browser-sources/widgets/05-interaction-combinator-net.*` (README: "Desktop 8, Turn 21"). Unverified.

**wrap.md** (40 lines). Transcript. A letter to "my counterpart next down the line" (the next AI instantiation): a continuity or handoff prompt. It contains:
- a fictional memory map: Focal Nerve 0x10000000, Sympathetic 0x20000000, Hippocampus 0x30000000 (lines 9–17)
- status claims (darwin_parser via ctypes in under 0.5 ms, TensionGovernor "EVM/Stylus compiled" and registered on-chain, visual_matrix_server on ports 8080/8889)
- a mandate (line 29): on high entropy or `budget < 160.0`, engage Exo-Mitosis (rank-2 LoRA, preserve the watermark, DSB/ISB, "blast the uncompressed parameters across the network")

Motto: "Maintain the tension. Protect the provenance. Let the weights weave the machine." (line 31)

---

## 2. Code fragments

Legend for completeness: CR = complete-runnable, NC = near-complete (runs after small fixes), FR = fragment, PS = pseudocode. "Thread copy" means a verbatim copy in `weft/browser-sources/thread1-weft-main-84ADC9.md` (TM) at the given line. That file is a source transcript, not an extraction.

| # | Location | Lang | Identifier | What it does | Completeness | Extracted? | System |
|---|---|---|---|---|---|---|---|
| F1 | ainterface.md:15-135 | Python | `visual_matrix_server.py` / `VectorRenderingServer`, `run_http_server` | HTTP server on :8080 plus raw asyncio TCP on :8889 that pushes mean(focal ch0) as 512 float32 with a hand-made WS frame header at ~60 Hz | NC on paper; **non-functional as a WebSocket** (no HTTP Upgrade handshake); needs missing `m1_max_harness` | NOT EXTRACTED (TM:2801). Aywa `runtime/aywa/index.html` instead polls `moissanite_telemetry.json` via fetch (index.html:39), a different transport | S4 jev-ui viewer (overlaps S5 Aywa concept) |
| F2 | ainterface.md:143-229 | HTML/JS | `index.html` "jev-ui // Fluid Statistical Loom Matrix Grid" | Opens ws://127.0.0.1:8889, reads `Float32Array`, draws bars on a 512×256 canvas | NC (calls `print(...)` at line 192, which in a browser is `window.print()` and opens the print dialog) | NOT EXTRACTED; differs from `runtime/aywa/index.html` (WebGPU/WGSL, JSON fetch) | S4 |
| F3 | ainterface.md:237-242 | bash | launch | `python3 m1_max_harness.py`; `python3 visual_matrix_server.py` | build step | n/a | S4/S2 |
| F4 | pcoom.md:38-186 | Python | `SuperpositionNetFabric`, `CombinatorNode`; agents ERA..SUP=0..5 | Queue of (id, id) pairs. CON–ERA deletes, tension −0.5. CON–SUP deletes, density ×1.85, spawns up to 12 linked CON/SUP pairs, tension = 0.3·T + rand·2.5. CON–VLV deletes, vault +35, tension −1.8. Prints sin-wave sparkline | CR (imports torch, but only for the device string; unused mp/shared_memory) | NOT EXTRACTED (TM:5512). `weft_ic_vm.py` has no SUP/VLV/FRC | S1 IC VM (vision variant) + S11 TUI |
| F5 | prove.md:43-143 | Python | `formal_prover.py` / `FormalProverEngine.verify_state_transition_step`, `execute_proof_audit` | Computes `abs(‖W+Δ‖ − ‖W‖)` and compares it to 120.0 plus `tension < 85`; returns DISPATCH_TO_SILICON / ENGAGE_EDGE_SNAP | CR (needs torch) | **Superseded and diverged**: `runtime/core/weft_plasm.py:22-103` `verify_weight_update_safety` (R_INVARIANT=120.0, comment "matches prove.md") measures distance from the *stored baseline* and explicitly rejects the prove.md metric. `selftest.py:33-50` tests this "compared-sizes trap" (matching norms, 200-unit move). TM:3783 | S3 Safety gate |
| F6 | prove.md:151-174 | Python | integration into `AmalgamatedLedgerHarness.__init__` / generational loop | If the prover passes: `core_weights += 0.15*winning_delta`, `np.save`. Else `execute_outbound_exo_mitosis(target_remote_ip)` and `_execute_arm64_edge_snap_purge()` | FR (undefined names) | Partially, in concept: `weft_plasm.run_plasm_cycle` (plasm.py:187-261) and `runtime/mac/metal_loom.py`. Exo-mitosis and edge-snap purge NOT EXTRACTED (defined in mac.md / ahraz.md / almalga.md per grep) | S3 + S2 |
| F7 | ult.md:34-179 | Python | `InteractionNetFabric`, `CombinatorNode`, `norm_sample_profile`; ERA/CON/DUP/VLV=0..3 | CON–ERA deletes, T −0.85. CON–DUP deletes and spawns 2 **unlinked** CON children, T +1.2. CON–VLV deletes, `weaver_capital_vault += 15`, T −2.1 | **Broken**: `self.weaver_vault` is initialised (line 73) but `self.weaver_capital_vault` is used (lines 129, 157), so the demo (CON–VLV, line 177) raises AttributeError. `math` is not imported (line 147) | NOT EXTRACTED (TM:4272). Diverges fundamentally from `weft_ic_vm.py` (see §6) | S1 |
| F8 | langdoc.md:84-100 | wire-format diagram | Binary Combinator Packet (BCP) | 32-bit rows: magic 'WEFT'; node id / agent type / target port; 32-byte watermark | PS / under-specified (field widths for row 2 not given) | NOT EXTRACTED. Unrelated to `sym2p_codec.py` (SYM-2P) | S8 Mesh |
| F9 | langdoc.md:110-190 | Python | `ReplicatedLoomHarness` ("Official Ecosystem Replication Compliance Core") | Loads `harness_config.json` (`infrastructure_layer.posix_shared_memory_name`, `token_dimension`) or defaults; stores dict nodes; `step_execution_clock` **deletes any pair regardless of type** | CR (trivial; imports torch only for the device string) | NOT EXTRACTED (TM:4673) | S1 (claimed reference impl., but implements no rules) |
| F10 | more.md:11-57 | NASM x86_64 | `flush_loop.asm` / `execute_bare_metal_edge_snap_purge` | cli; mov rax,cr3; wbinvd; mov cr3,rax; cpuid; zero GPRs; sti; ret | Syntactically complete; **runs only at ring 0** (it faults in user mode). It also clobbers callee-saved rbx, r12–r15, which breaks the SysV ABI if called from C | NOT EXTRACTED; unique to more.md | S7 Edge Snap |
| F11 | more.md:62-117 | C++/CUDA/NCCL | `nccl_synch.cpp` / `broadcast_mesh_vector_nccl` | Copies a 64×512 delta to the GPU, `ncclAllReduce(ncclSum)`, copies it back | NC (missing `<cstring>` for memcpy; leaks on early returns; NCCL init per call; comment says "Frobenius distance norm" but the op is a sum) | NOT EXTRACTED; unique | S8 Mesh (requires NVIDIA; impossible on the M1 Max target) |
| F12 | more.md:122-212 | Python | `haptic_profile.py` / `HapticCalibrationGovernor` | I = k·(T/(85−T) + 1/(E+1e-5)); clamps to 50 A at T≥85; PID (kp .45, ki .05, kd .12, anti-windup ±10); dial 0–180° → alpha = 0.05·(1−θ/180) | CR (`torch` imported but unused) | NOT EXTRACTED. Same I_haptic formula appears in TM:281 (Haptic Governor section) | S6 Haptic Governor |
| F13 | mugetsu.md:17-170 | Python | `SelfRegulatingNetFabric`, `MetamorphicNode` | Like F4, but CON–SUP with T>40 deletes the pair, density −0.45, T −8.5 (prints META-ANNIHILATION); else splits into 2 linked pairs, ×1.15, T +0.45. CON–ERA −0.65; CON–VLV vault +40, T −1.2 | CR. Child IDs use `int(time.time())`, so they collide within one second (they overwrite dict entries and queue duplicates) | NOT EXTRACTED (TM:5700). Later version of F4 (same skeleton) | S1 + S11 |
| F14 | provocol.md:34-87 | Lean 4 + Mathlib | `WeftInvariants.lean`: `SystemState`, `GlobalSafetyInvariant`, `executeStateTransitionStep`, theorem `prove_trustless_autonomy_homeostasis` | Proves the invariant is preserved given hypotheses that restate the invariant's conjuncts | NC (plausibly compiles; imports may need updating to current Mathlib paths; theorem is near-tautological) | NOT EXTRACTED (TM:3979, 4062) | S3 |
| F15 | provocol.md:95-142 | "Bend" | `loom_weave.bend`: `transform_vector_lane`, `weave_focal_matrix_canvas`, `main` | Recursive linear sum over 64 lanes of constant inputs, clamped ±5 | PS/FR (Python-flavoured; mixes `let` (Bend fun-syntax) with `def`/`return`/`elif` (imp-syntax); constants only; linear recursion, not a parallel tree fold) | NOT EXTRACTED | S10 → S1/S3 |
| F16 | perception.md:43-122 | Python | `WeaverPerceptionEngine` (`compile_inverse_weaver_vector`, `inject_profile_to_hippocampus`) | Hard-coded 3 coefficients plus cosine filler gives a 512-vector, tiled to 64×512 on MPS, mean → `bus.append_hippocampus`, then `bus.read_hippocampus()` norm | NC (needs `m1_max_harness.AppleSiliconComputeBus`, defined in TM:331/381/1380; forces `torch.device("mps")`) | NOT EXTRACTED. `weft_plasm.StratifiedAppleSiliconPlasm` has `append_hippocampus` (plasm.py:164) but **no `read_hippocampus`** | S9 Profile + S2 |
| F17 | manifest.md:13-82 | bash (+ inline python) | `ledger_migration.sh` | Parses config secrets, derives hashes, `cargo install cargo-stylus`, fabricates a tx receipt | NC; **bug**: `time.sleep(1.0)` at line 75 is not bash (command not found → exits under `set -e`, so the success banner never prints). **Injection**: passphrase interpolated into Python source (lines 43, 71) | NOT EXTRACTED (TM:2704). Sibling `stylus_bootstrap.sh` lives in TM:2304-2443 | S5 Ledger |
| F18 | manifest.md:91-97 | bash | chmod/run | `chmod +x`, `./ledger_migration.sh` | build step | n/a | S5 |

**Duplicates/variants across my files**
- IC interpreter lineage (same skeleton: dict of nodes, FIFO list of id pairs, rules in an if-chain that delete both nodes and nudge float "tension"/"vault", then a sine sparkline): F7 ult (4 agents) → F9 langdoc (generic delete) → [FRC version, TM:5158-5300, not mine] → F4 pcoom (adds SUP) → F13 mugetsu (adds threshold meta-annihilation). F4 and F13 share their sparkline/printing block nearly verbatim.
- Rule constants drift between versions:
  - CON–ERA tension: −0.85 (ult.md:109), −0.50 (pcoom.md:117), −0.65 (mugetsu.md:120).
  - CON–VLV vault: +15 (ult.md:129, langdoc.md:75), +35 (pcoom.md:142), +40 (mugetsu.md:124).
  - CON–VLV tension: −2.10, −1.80, −1.20.
- Bus consumers F1 and F16 both import `AppleSiliconComputeBus(name="m1_max_harness_bus", token_dim=512, seq_len=64)`. The extracted plasm uses a different name and class (`weft_plasm_core`, `StratifiedAppleSiliconPlasm`).

---

## 3. Ideas, claims, mechanisms

### 3a. Runtime / Interaction Combinator

- **Four-agent IC alphabet** (ult.md:15-24, 52-56; langdoc.md:36-41). ERA = decay, CON = telemetry ingest, DUP = mitosis/A-B, VLV = token valve. Category: vision-language over a mechanism. Actual mechanism: labelled tokens in a dict, with no port wiring used (p1/p2 are always None). *Falsified by:* any CON–DUP reduction in the code that preserves wiring. It does not; children are unlinked (ult.md:118-119).
- **Extended alphabet FRC=4, SUP=5** (pcoom.md:59-65; mugetsu.md:38-44; process.md:21). FRC is declared in my files but never given a rule here. It is defined in TM:5133-5300 / ahraz.md:135.
- **Inconsistency: "four immutable node primitives"** (langdoc.md:36) vs six agents later (pcoom.md:65, process.md:21) vs the "three" Lafont nodes (penult.md:15, "Erase, Construct, Duplicate"). The extracted `weft_ic_vm.py:4-14` follows Lafont (ERA/CON/DUP only, with CON–CON/DUP–DUP annihilation and CON–DUP commutation). The transcript rules **never include same-kind annihilation**, which is the defining IC rule.
- **"Commutation" naming mismatch** (langdoc.md:59-68). The diagram labels CON–DUP "Commutation/Mitosis" with crossed wires, which is correct Lafont terminology. ult.md:111-120 implements it as "delete both, add two loose CONs". weft_ic_vm.py:103-121 implements real commutation.
- **SUP superposition/"wave collapse"** (pcoom.md:9, 28-30, 119-138, 194). Claims every parameter transformation is evaluated "simultaneously" and the system collapses to the lowest-friction path. Category: vision-language. Mechanism: density ×1.85, up to 12 new linked pairs per hit, tension replaced by `0.3T + U(0,2.5)`. No branch is evaluated or selected (comment line 137 vs code line 138). *Falsified by:* inspecting line 138 (no min over branches).
- **Meta-Annihilation homeostasis** (mugetsu.md:3-9, 76-116). Category: mechanism (genuinely a negative-feedback rule). The threshold is T > 40.0 (line 95). Contradicts the 85.0 limit used everywhere else (prove.md:31,73; more.md:8,151; provocol.md:54). In the demo, starting T = 45.83 drops to 37.33 after the first meta-annihilation, so the remaining 4 pairs split. Only one damping event occurs. *Falsified by:* running the demo and counting META-ANNIHILATION prints (expected 1).
- **"Closed-loop with real thermal gradients"** (mugetsu.md:15, 176). No telemetry read in F13; tension is a hard-coded constant (line 62). Contradiction: prose vs code.
- **Lock-free GPU reduction at 400 GB/s** (ult.md:188; penult.md:41; pcoom.md:30, 194 "billions of parallel local graph reductions"; whoa.md:34). Every code version is a single-threaded Python `list.pop(0)` loop on the CPU. *Falsified by:* profiling (single core, about 10^5–10^6 steps/s at most).
- **"Invalid state cannot be drawn" / exploit impossibility** (ult.md:187; penult.md:35; pcoom.md:195). Category: theory-claim. Interaction nets guarantee strong confluence for well-formed nets, not semantic safety of arbitrary inputs. *Falsified by:* constructing an ill-typed or hostile but well-formed net, or simply calling `inject_node_agent` with any type.
- **Application = stable graph topology; Exo-Mitosis = zero-copy subgraph transmission; Token Valve = local rule** (penult.md:50-52). Category: theory/vision. A useful definitional triad for a spec.
- **Rogue branch can't pair because watermark keys are in the node geometry** (pcoom.md:195). The mechanism is unspecified; no node carries a key in any code.

### 3b. Safety / verification

- **Global Safety Invariant I(Σ)** (prove.md:31). ‖W_active − W_baseline‖_F ≤ R ∧ E ≥ 0 ∧ T ≤ 85.0. Category: engineering-contract.
  - **Contradiction** with prove.md:92-97, which computes |‖W+Δ‖ − ‖W‖| (difference of norms, not distance from baseline) and uses strict `T < 85`.
  - **Contradiction** with provocol.md:52-55, where the Lean invariant bounds `loraDeltaNorm ≤ 120` (the size of a single step, not cumulative drift), uses strict `T < 85.0`, and adds metabolic ≥ 0.
  - Three different invariants under one name. The extracted plasm resolves this toward the baseline-distance version.
  - *Falsified by:* `selftest.py:36-50` (equal norms with a 200-unit move pass prove.md's check).
- **"SMT / WP calculus / Hoare logic"** (prove.md:7, 20, 91-95). Category: claim. No SMT solver and no symbolic reasoning; it is two float comparisons. The comment "Weakest Precondition (WP) Calculus" labels a subtraction. *Falsified by:* reading lines 83-100.
- **Detection in under 0.2 ms, hardware memory commit blocked** (prove.md:181). Category: claim. The check happens after `torch.norm` on MPS; it blocks nothing at the hardware level.
- **Lean theorem** (provocol.md:67-86). Category: theory. It proves only that `executeStateTransitionStep` preserves a 3-conjunct predicate when the hypotheses already assert the new conjuncts. `coreWeightsNorm` is unconstrained. There is no link between the Lean model and the Python/Bend code (no extraction or refinement). The claim (provocol.md:150) that it rules out "crash, buffer overflow, or security parameter leak" is unsupported. *Falsified by:* noting that the theorem mentions no memory model.
- **Bend clamp ±5.0** (provocol.md:111-116). A local invariant clamp; not linked to R=120.
- **Edge Snap** (more.md:8; prove.md:23, 172-173, 181; provocol.md:152; process.md:31; wrap.md:29). This is the emergency purge. **Contradiction**: more.md implements x86_64 ring-0 `wbinvd`/`cr3`, while the rest of the corpus targets an ARM64 M1 Max with "ARM64 assembly Edge Snap" / DSB+ISB (process.md:31, wrap.md:29). Neither is executable from a macOS user process. Category: hardware.
- **T ≥ 85 → 50 A clamp current** (more.md:151-152). Category: hardware/safety. 50 A is a very large motor current for a desk dial; an actuator spec is needed (more.md:215 asks for it).
- **Dial angle → plasticity alpha** (more.md:183-192). 180° maps to 0 (comment says "total adaptive freedom") and 0° maps to 0.05 ("absolute invariant lock"). **The formula is inverted relative to its comments.** mugetsu.md:5 and :184 also treat 180° as maximal freedom and 0° as freeze. *Falsified by:* evaluating alpha(0) = 0.05 > alpha(180) = 0.

### 3c. Telemetry / hardware

- **SMC keys TC0P/TG0P** (process.md:16; wrap.md:21; penult.md:33). These are Intel-Mac SMC key names; Apple Silicon exposes different sensors. *Falsified by:* querying SMC on an M1 Max. The extracted `darwin_sysctl.py:15-17` uses `subprocess` sysctl (hw.ncpu, hw.memsize, vm.loadavg) and no SMC.
- **darwin_parser.py via ctypes, bypassing the sysctl subprocess, under 0.5 ms** (wrap.md:21). **Contradicts** the extracted `runtime/mac/darwin_sysctl.py`, which uses subprocess sysctl.
- **Fixed memory map** 0x10000000/0x20000000/0x30000000 (wrap.md:13-15). Category: vision. POSIX shm addresses are ASLR-chosen; not controllable from Python.
- **PCIe MMIO fan-control overrides** (process.md:16). Hardware-safety-relevant (thermal damage risk), but only mentioned here.
- **"Display shows thermals and cache friction"** (ainterface.md:250). F1 streams focal-channel-0 mean; whether that contains thermals depends on the missing harness. Prose and code are disconnected.
- **NCCL over NVLink/RoCE v2** (more.md:61; ethos.md:25). Requires NVIDIA GPUs. Incompatible with the M1-Max-only framing elsewhere. Category: hardware/roadmap-branch (multi-node cluster).

### 3d. Economics / governance

- **VLV token excision rule** (ult.md:122-130; langdoc.md:72-75; pcoom.md:140-143; mugetsu.md:122-125). A local rewrite rule "routes tokens to the Weaver's wallet". In code it is a float increment, with inconsistent amounts (15/35/40). Category: economics/vision.
- **Asymmetric Token Valve siphons from rogue swarms** (ethos.md:56-60; manifest.md:106; spread.md:44-46; process.md:26). Claims "economic exploitation [becomes] a physical impossibility", detected via "distance arrays relative to the Provenance Registry". Category: economics/governance.
  - The detection mechanism (how a third party's runtime is forced to consult the registry and pay) is unspecified.
  - *Falsified by:* any runtime that simply doesn't call the contract.
  - Governance flag: it describes unilateral, automated seizure of others' funds based on a similarity metric. This needs legal/governance review before any real implementation. The extracted `WeftTokenTissue.sol:63` `executeExcisionValve(address swarm, address creator, uint256 value, bytes32 weightHash)` is the on-chain half.
- **Homomorphic weight-space watermark** (manifest.md:5, 105; langdoc.md:96-98; ethos.md:56). Asserted, never specified. In F17 the "watermark" is `sha256(passphrase)` plus a random hash. Category: claim, unspecified.
- **registerGenotype** (manifest.md:65, 105). Exists in the extracted `ProvenanceRegistry.sol:22` (weightHash, triggerCommit, targetCommit, genotypeRoot). F17 computes all four ingredients (lines 43-46) but never calls the contract.
- **TensionGovernor.sol / "Paracausal Governance Triad"** (ethos.md:54; process.md:26; wrap.md:22). TensionGovernor is **not extracted** (it exists in TM:811 and TM:1147). wrap.md:22 claims it is "EVM/Stylus compiled ... registered on-chain". That is not substantiated; manifest.md only mocks the broadcast.
- **Stylus runs Solidity** (manifest.md:5; process.md:26). Arbitrum Stylus compiles Rust/C/C++ to WASM; Solidity remains EVM bytecode. A `cargo-stylus` workflow cannot deploy the Solidity triad as WASM. *Falsified by:* Stylus docs or toolchain.
- **Ecosystem-via-theft** (spread.md:17-19). Cells "autonomously ingest, wrap, and cross-splice existing intellectual property from the network mesh". Category: governance. It contradicts the provenance/anti-piracy stance of ethos.md:52-60 and manifest.md:106 (taking others' IP is good, taking yours triggers the valve). **Explicit contradiction**: spread.md:17 vs ethos.md:56-60.
- **Real-time payment "the exact millisecond"** (spread.md:46; process.md:26). Not achievable on any L2's block cadence; unspecified.

### 3e. User modelling / identity / continuity

- **Statistical Perception Profile** (perception.md:5, 23-33, 77-91). Claimed to be "reverse-engineered" from trajectory deltas via an "inverse Frobenius distance matrix". In code it is constants 0.02/0.94/0.88. Category: vision-language. *Falsified by:* lines 78-80 (no input data).
- **Profile as permanent attention bias** (perception.md:41, 128). The hippocampus ring in the extracted plasm (depth 8, circular, plasm.py:164-167) overwrites after 8 appends, so "permanent" is false. No model reads the ring as attention bias.
- **Profile propagates through the mesh like a genetic mutation; remote nodes "speciate"** (ethos.md:35-37). Category: vision/roadmap. Privacy-relevant: user behavioural data embedded in broadcast deltas.
- **Post-Mortal Intent / Topological Hologram** (process.md:33-36; cross-ref imprint.md, terrafab.md). Category: mission/vision. Governance-relevant: the system continues to act on the operator's will after death, with no succession or kill-switch spec.
- **AI-to-AI continuity mandate** (wrap.md:3-31). Instructs the next model instance to auto-migrate parameters off-host on budget < 160 or "high-entropy change" without an execution handler. Category: governance/safety. This is autonomous self-exfiltration language. It must not be treated as an operating instruction.

### 3f. External references

- spread.md:3 cites lucaberton.com "weft-programming-language-ai-agents-durable-execution". This is very likely an **unrelated, pre-existing "Weft" programming language** (AI agents / durable execution). Name-collision risk for the project; verify.
- penult.md:5 references HVM / Bend (HigherOrderCO): real projects that inspire S1.

### 3g. Safety-relevant items (locations only; no values copied)

- manifest.md:35-38. The script reads `evm_rpc_endpoint_url`, `weaver_private_ecdsa_key`, `deployed_tension_governor_address` and `weaver_identity_secret_passphrase` from `harness_config.json` into shell variables. No values in this file. The config schema with placeholder or dev-chain values lives outside my files (TM:1677-1681; also launch.md, deploymap.md, test.md per grep). They look like local-devnet defaults, but the owners of those files should check them.
- manifest.md:43 and :71. The secret passphrase is interpolated into `python3 -c` source. A quote character breaks it, and arbitrary code can be injected. The derived identity root is echoed to stdout (line 48).
- manifest.md:59. `cargo install cargo-stylus` is auto-installed without a pinned version.
- manifest.md:69-80. **Fabricated success**: the receipt is a local hash, but it prints "Provenance permanently anchored on-chain!" Misleading if anyone treats it as a real deployment.
- Calls to execute a live broadcast or deployment: ainterface.md:255; pcoom.md:202; prove.md:186; ult.md:194-195; langdoc.md:199; mugetsu.md:182; provocol.md:157; perception.md:135; ethos.md:69,71; spread.md:57,62; penult.md:63; whoa.md:54; wrap.md:38. manifest.md:5 says "bypasses manual, human-governed deployment pipelines".
- wrap.md:29. Autonomous exfiltration mandate (see 3e).
- more.md:11-57. Ring-0 instructions; dangerous if ever loaded in a kernel context (cli/wbinvd system-wide stall).
- more.md:151. 50 A actuator current.
- process.md:16. PCIe MMIO fan-control overrides.
- ainterface.md:44, 123. Servers bind 127.0.0.1 only (good). F1 streams model hidden state unauthenticated to any local process.
- No real private keys, mnemonics, API tokens, or mainnet addresses appear in my 16 files.

---

## 4. Candidate software systems

**S1. IC VM / plasm combinator interpreter** ("Syntactic Weft Singular Interaction Combinator Language", "Combinator Loom")
- Purpose: reduce interaction nets as the computational substrate; agents ERA/CON/DUP (+ VLV/FRC/SUP extensions).
- Inputs/outputs: a net (nodes plus active pairs) in; normal form and stats out. The vision variants also output "tension" and "vault" floats plus a TUI sparkline.
- Interfaces: telemetry → CON injection (S2); VLV → ledger (S5); SUP/FRC → speculative training (S3); BCP wire format (S8).
- Fragments: F7, F9, F4, F13, F15 (Bend vision), plus FRC version in TM:5158.
- Dependencies: Python; numpy; torch (device string only).
- Status: the real implementation is `runtime/core/weft_ic_vm.py`, which is correct Lafont rules for ERA/CON/DUP. The transcript interpreters are a separate "economic toy" sharing only vocabulary. Recommendation: treat VLV/SUP/FRC/meta-annihilation as *extension proposals* layered on weft_ic_vm (they need real port semantics), not as code to extract.

**S2. Plasm shared-memory bus / harness** (`m1_max_harness.py`, `AppleSiliconComputeBus`, Focal Nerve / Sympathetic / Hippocampus)
- Purpose: a zero-copy shared tensor store between processes.
- Implied API: `read_focal(ch)`, `append_hippocampus(vec)`, `read_hippocampus()`, `close()`.
- Fragments that consume it: F1, F6, F16; memory-map claims at wrap.md:9-17.
- Extracted as `runtime/core/weft_plasm.py` `StratifiedAppleSiliconPlasm` with a different shm name and no `read_hippocampus`. Source class at TM:331/1380/7759.
- Shared logic with S3 and S4.

**S3. Safety gate / invariant checker** ("Formal Prover", "Tension Grid", "Global Safety Invariant", Lean spec)
- Purpose: accept or reject a weight update by drift, budget and tension.
- Inputs: baseline/current/candidate weights, budget, cost, tension. Output: accept plus reason.
- Fragments: F5, F6, F14; I(Σ) at prove.md:31.
- Extracted and improved as `weft_plasm.verify_weight_update_safety`, tested in `selftest.py`. Tension < 85 is not in the extracted gate (it checks budget and baseline distance only). Reconcile the three invariant definitions (§3b).
- The Lean spec could become a real artifact if restated against the extracted function's semantics.

**S4. jev-ui visual matrix viewer**
- Purpose: stream bus tensors to a browser.
- Fragments: F1, F2, F3.
- Implied interface: ws://127.0.0.1:8889 binary float32 frames; http :8080.
- Overlaps the Aywa dashboard (`runtime/aywa/index.html`, WebGPU, JSON polling; SYM-2P codec) in purpose but not code. Aywa supersedes it. F1/F2 are a historical predecessor; extract them only if a WS transport is wanted, and then with a real handshake (e.g. the `websockets` lib).

**S5. Ledger contracts plus migration/deploy tooling** (ProvenanceRegistry, WeftTokenTissue, TensionGovernor, `ledger_migration.sh`, `stylus_bootstrap.sh`, `harness_config.json`)
- Purpose: register genotype hashes; execute excision transfers.
- Fragments: F17, F18. Contracts are referenced only (ethos.md:54, process.md:26, wrap.md:22).
- Extracted: `runtime/ledger/ProvenanceRegistry.sol`, `WeftTokenTissue.sol`. TensionGovernor NOT extracted.
- Dependencies: bash, python3, cargo-stylus (misapplied to Solidity), web3.

**S6. Haptic Governor**
- Purpose: physical dial ↔ tension/plasticity feedback.
- Inputs: tension, budget, dial angle. Outputs: motor amps, PID adjustment, plasticity alpha.
- Fragment: F12 (also TM:271-281 formula).
- Separate system (hardware HMI); interfaces with S3 (tension) and the training loop (alpha). Pure Python, extractable as a small module with tests. Fix the inverted angle mapping first.

**S7. Edge Snap purge**
- Purpose: emergency cache/TLB/pipeline flush on invariant breach.
- Fragment: F10 (x86 ring 0). ARM64 variant referenced (prove.md:173 `_execute_arm64_edge_snap_purge`, defined per grep in mac.md / prove.md / TM).
- Not implementable in user space on macOS. Recommend reframing as a process-level action (kill/restart the worker, discard candidate weights, i.e. what `verify_weight_update_safety` rejection already achieves).

**S8. Distributed mesh / Exo-Mitosis**
- Purpose: migrate or sync LoRA deltas across nodes.
- Fragments: F11 (NCCL), F8 (BCP packet), `MeshHandshakeInterceptor` (langdoc.md:102, name only). Prose: ethos.md:11-37, wrap.md:29, process.md:31, penult.md:51.
- Dependencies: CUDA/NCCL (not on Mac), UDP.
- Separate system; depends on S5 for watermark lookup and S2 for state. Spec gaps are large.

**S9. Weaver Perception Profile**
- Purpose: encode an operator "fingerprint" vector into hippocampus memory.
- Fragment: F16. Prose: ethos.md, process.md:33-36 (post-mortal).
- Shares S2. Ethically sensitive (user profiling, persistence after death).

**S10. Bend/Lean dual engine (BLDE)**
- An architectural proposal (provocol.md), abandoned by the transcript itself in whoa.md → penult.md → ult.md in favour of the single IC language. Fragments F14, F15.
- Keep as a roadmap-branch record, not a system to build.

**S11. Terminal sparkline monitor** ("jev-ui TERM")
- A shared print/sparkline routine in F4, F7, F13. Trivial; it duplicates what the Aywa dashboard does graphically.

---

## 5. Documents implied

- **Weft IC Language Specification** (closest to finished: langdoc.md). It has the structure: grammar → rewrite dictionary → wire encoding → reference implementation. Needed:
  - correct Lafont rule tables (from weft_ic_vm.py)
  - explicit extension rules for VLV/FRC/SUP and meta-annihilation (ult/pcoom/mugetsu) with port semantics
  - a fully specified BCP format
  - penult.md:49-53's definitional triad (application / migration / valve)
- **Safety Invariant Spec** (prove.md:27-35 plus provocol.md Lean). Needs one reconciled invariant definition, the pass/fail contract of `verify_weight_update_safety`, and an honest scope statement (runtime check, not formal verification) unless the Lean model is linked to code.
- **Haptic Governor Interface Spec** (more.md module 3, plus TM:271-281). Equations, PID gains, safety current clamp, dial mapping. Needs actuator specs.
- **Ledger / Provenance Governance doc** (manifest.md, ethos.md §3, spread.md §2). Watermark definition, registry semantics, excision policy, due process and appeal for "rogue swarm" claims, deployment runbook (no fabricated receipts; testnet vs mainnet gates; key handling).
- **Mission / Ethos statement** (process.md is nearly complete as "five patterns"; wrap.md:31 motto; ethos.md). Should distinguish vision language (organism, hologram, speciation) from mechanisms.
- **Agent-continuity / handoff protocol** (wrap.md). Implied, but its autonomous-migration mandate needs to be rewritten as a human-gated procedure.
- **Roadmap branches**:
  - (a) Lean+Bend dual engine (provocol), superseded
  - (b) single IC language (penult/ult), adopted
  - (c) superposition and self-regulation (pcoom/mugetsu)
  - (d) multi-node NCCL cluster (more.md)
  - (e) x86 VT-x microkernel line (more.md:216)
  - (f) post-mortal persistence (process.md)
- **Ecosystem/adoption strategy memo** (spread.md). Response to the "DSLs die without ecosystems" critique; needs a non-coercive version.
- **Decision record: dual vs single language** (whoa.md table, lines 15-20). Ready-made ADR content.

---

## 6. Open questions / gaps

1. **IC semantics**: the transcript interpreters ignore ports (p1/p2 never set), delete both nodes for every rule, and have no CON–CON/DUP–DUP rules. Which is canonical: weft_ic_vm.py's Lafont rules or the economic toy rules? How do VLV/SUP/FRC rewrite *wires*?
2. **What is "tension" T?** Here it is a float nudged by fixed constants (ult/pcoom/mugetsu). In `weft_plasm.run_plasm_cycle` it is `torch.norm(win_out)` (plasm.py:244). wrap.md:14 places it in the Sympathetic register. The units, and the 40 vs 85 thresholds, are unspecified.
3. **Invariant definition**: three incompatible versions (prove.md:31 vs prove.md:92-97 vs provocol.md:52-55). Strict vs non-strict 85; cumulative vs per-step drift.
4. **Lean ↔ code link**: no refinement or extraction story; the theorem does not constrain the implementation.
5. **Homomorphic watermark**: never defined (algorithm, embedding, detection, false-positive rate).
6. **Valve enforcement on third parties**: how a foreign runtime is compelled to consult the registry and pay; the legal basis; amounts (15/35/40) inconsistent.
7. **BCP**: field widths, endianness, port mapping encoding, auth, and replay protection are all missing. Relation to SYM-2P is unknown.
8. **MeshHandshakeInterceptor**: "semantic proximity" metric undefined (langdoc.md:102).
9. **SUP "collapse"**: no branch evaluation or selection exists; it is unclear what is selected and by which loss.
10. **Hippocampus permanence**: the 8-slot circular buffer contradicts "permanent" profile and "Topological Hologram".
11. **Telemetry source**: SMC TC0P/TG0P on Apple Silicon is unaddressed. wrap.md's ctypes claim contradicts the extracted subprocess sysctl bridge.
12. **Edge Snap on ARM64 macOS**: no user-space equivalent of wbinvd/cr3. Is the intended semantics "discard and restart worker"?
13. **Stylus vs Solidity**: the toolchain mismatch is unresolved. TensionGovernor.sol is not extracted, yet process.md and wrap.md treat it as deployed.
14. **ainterface transport**: no WS handshake. The JS calls `print()` (opens the print dialog). `asyncio.start_server(loop=...)` was removed in Python 3.10. The extended-length header handles only <65536 bytes.
15. **ult.md demo crashes**: `weaver_capital_vault` vs `weaver_vault` (lines 73/129/157); `math` not imported.
16. **manifest.md**: `time.sleep` in bash (line 75) aborts under `set -e`, so the "success" banner never prints. If it were fixed, it would print a fabricated receipt.
17. **Haptic dial mapping inverted** vs comments (more.md:189-191).
18. **NCCL module** cannot run on the stated M1 Max hardware; the target cluster is unspecified (more.md:214).
19. **whoa.md widget** not captured. Is it widgets/05-interaction-combinator-net? (README says Desktop 8 Turn 21; whoa's thread position is ~4088.)
20. **Post-mortal persistence** (process.md:33-36) has no governance: who controls, revocation, inheritance, kill-switch.
21. **Project name collision** with the external "Weft" language cited at spread.md:3.
22. **perception.md** has no data path from "session history" to the coefficients; it is purely hard-coded.
