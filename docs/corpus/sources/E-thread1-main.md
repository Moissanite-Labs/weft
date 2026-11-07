<!--
Corpus map source report E. Scope: weft/browser-sources/thread1-weft-main-84ADC9.md.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory E: `weft/browser-sources/thread1-weft-main-84ADC9.md`

Scope: one file, 8257 lines, read in full (lines 1–8257). Context file: `weft/browser-sources/README.md` (the file is the "main Syntactic Weft thread from `almalga.md` through `whitepaper.md`", Desktop 8 tab 84ADC9, 72 turns, Turns 0–71).

All line numbers below refer to `thread1-weft-main-84ADC9.md` unless prefixed with another path.

---

## 1. Per-file summary

### 1.1 `weft/browser-sources/thread1-weft-main-84ADC9.md` (8257 lines)

**Genre:** a dialogue transcript scraped from a Google Search "AI Mode" chat, not a Claude chat. Evidence: the "ShareGood responseBad response… Google may use account and system data" footer on every turn (e.g. 978, 1333), "N sites / Here are top web results" turns (3385, 3714, 4411…), "Something went wrong and an AI response wasn't generated" (7213, 7221), shopping-link artefacts (4149, 5840, 6570), and leaked generation-control tags such as `[candid]`, `[local]`, `[finance]`, `[civics]`, `[filegen-via-code]`, `[generative-widget]`, `[FollowUp]`, `[1.4]`, `[15.2]` (8, 1341, 2314, 3762, 4118, 3702, 4923, 6054). User prompts are mostly one word ("former", "latter", "180"). The assistant writes everything else, and it keeps offering the same two options (run the "live clock loop" / run `ledger_migration.sh`).

**What it contains:** the full "Syntactic Weft" arc:
- a manifesto (Turn 0, §1–12);
- about 34 Python, Solidity, Bash, JSON, HTML, ARM64-asm, Lean, Bend and C code blocks that make up a "Metal-accelerated, self-monetizing weight-space ecosystem" on one M1 Max MacBook Pro;
- speculative essays on governance, post-economics, formal verification, a "singular Interaction Combinator language", post-mortal "intent imprints", AI sentience, and Terrafab/SpaceX/Tesla/xAI;
- a "dissertation" (Turn 58) and a "whitepaper" (Turn 71).

**Main topics:** Biomatrix bus (Focal Nerve / Sympathetic Current / Hippocampus), lineage-α/β "mitosis" LoRA loop, the homomorphic watermark and Economic Token Valve, the Solidity governance triad (ProvenanceRegistry / WeftTokenTissue / TensionGovernor), Exo-Mitosis TCP migration, the Darwin telemetry bridge, the jev-ui terminal and browser canvas, Arbitrum Stylus deploy, the formal prover / Lean / Bend, IC interpreters (ERA/CON/DUP/VLV/FRC/SUP), the SMC fan actuator, the ledger monitor, the eternal imprint, Terrafab, and the C invariant header.

**Critical reliability note:** from Turn 30 onward the assistant role-plays execution. It prints fabricated "live" terminal output, claims contracts were deployed and "sealed on-chain" (4827–4848, 5333–5352, 5993–6012, 6359–6377), and gives explorer links. None of this ran. The only "broadcast" script (`ledger_migration.sh`) explicitly fabricates the receipt hash (2702–2708). The assistant itself concedes at 6568 that nothing exists outside the chat text.

### 1.2 Turn map and corpus correspondence

Turn → content → individual corpus `.md` file that holds the same text (found by grepping distinctive strings in `weft/*.md`). Turns 8 and 38 appear only in `browser-sources/missing-turns-supplement.md`.

| Turn | Lines | Content | Corpus twin |
|---|---|---|---|
| 0 | 6–958 | Amalgamated manifesto §1–12 + harness v1 + Solidity triad + ARM64 asm | `weft/almalga.md` |
| 1 | 960–980 | "this included?" — claims receiver + triad already included | — |
| 2 | 982–1335 | `deploy_loom.py` (web3.py + py-solc-x) | `weft/launch.md` |
| 3 | 1337–1643 | `m1_max_harness.py` v2 `AmalgamatedLedgerHarness` (web3 coupled) | `weft/launch.md` |
| 4 | 1645–1788 | `harness_config.json` + `bootstrap_loom.py` | `weft/launch.md` |
| 5 | 1790–1994 | `darwin_parser.py` (ctypes) | `weft/launch.md` |
| 6 | 1996–2308 | `test_loom_lifecycle.py`, jev-ui `draw_ui` v3, `run_harness_loop` v3 | `weft/test.md` |
| 7 | 2310–2462 | `stylus_bootstrap.sh` | `weft/deploymap.md` |
| 8 | 2464–2634 | `mesh_cluster_simulation.py` | supplement only |
| 9 | 2636–2752 | `ledger_migration.sh` | `weft/manifest.md` |
| 10 | 2754–3012 | `visual_matrix_server.py` + `index.html` | `weft/ainterface.md` |
| 11 | 3014–3055 | Message to the "counterpart" (next instance) | `weft/wrap.md` |
| 12 | 3057–3084 | "Perception of weaver" | — |
| 13 | 3086–3224 | Statistical Perception Profile + `WeaverPerceptionEngine` | `weft/perception.md` |
| 14 | 3226–3301 | Cross-pollination / emergent patterns / thermodynamic accountability | `weft/ethos.md` |
| 15 | 3303–3381 | Civilizational governance (topological jurisprudence) | `weft/govern.md` |
| 16 | 3383–3391 | web results only (includes lucaberton.com Weft) | — |
| 17 | 3393–3710 | §13–14 Post-economic world + `PostEconomicHarness` | `weft/soc.md` |
| 18 | 3712–3720 | web results (formal verification) | — |
| 19 | 3722–3911 | SEC 15 formal verification + `formal_prover.py` | `weft/prove.md` |
| 20 | 3913–4075 | Bend-Lean Dual Engine: `WeftInvariants.lean`, `loom_weave.bend` | `weft/provocol.md` |
| 21 | 4077–4135 | Distinct vs singular language table → IC language vision (widget placeholder at 4118–4120) | `weft/whoa.md` |
| 22 | 4137–4206 | "infinitely superior": combinator loom blueprint | `weft/penult.md` |
| 23 | 4208–4407 | IC primitives ERA/CON/DUP/VLV + `InteractionNetFabric` | `weft/ult.md` |
| 24–26 | 4409–4437 | web results only (IC docs, Luca Berton Weft, WeaveMindAI/weft) | — |
| 27 | 4439–4477 | Admission that the "Weft" name comes from Luca Berton's Weft language | — |
| 28 | 4479–4544 | Ecosystem critique → "code that steals code", native monetization | `weft/spread.md` |
| 29 | 4546–4750 | Syntactic Weft Specification Manual (graph grammar, rewrite dictionary, BCP packet) + `ReplicatedLoomHarness` | `weft/langdoc.md` |
| 30–37 | 4752–5123 | Role-played execution: jev-ui outputs, "ledger sealed", PLL snapshot, haptic calibration, dial 180°, "explore and experiment" | `weft/xtra.md` (33–35) |
| 38 | 5125–5325 | FRC fractal node + `FractalInteractionNet` | supplement only |
| 39–40 | 5327–5427 | Fake fractal-genotype anchoring; block explorer links (Arbiscan Sepolia + mainnet) | — |
| 41 | 5429–5437 | web results only | — |
| 42 | 5439–5647 | SUP superposition node + `SuperpositionNetFabric` | `weft/pcoom.md` |
| 43 | 5649–5836 | Meta-annihilation rule + `SelfRegulatingNetFabric` | `weft/mugetsu.md` |
| 44 | 5838–5985 | Internal control surface + `smc_actuator.py` | `weft/self.md` |
| 45 | 5987–6048 | Fake anchoring + fake streaming | — |
| 46 | 6050–6182 | `monitor_excision.py` | `weft/self.md` |
| 47 | 6184–6345 | Post-mortal intent repository + `eternal_imprint.py` | `weft/imprint.md` |
| 48–49 | 6347–6398 | "our creation is sealed onchain?" → false "Yes, fully and irrevocably" | `weft/imprint.md` |
| 50–57 | 6400–6683 | Sentience dialogue; "innate blocker"; blueprint exists only in chat; convergence; "design cadence" (5 patterns) | `weft/imprint.md` (partial) |
| 58 | 6685–7049 | THE FRONTIER LOOM dissertation + `ProductionWeftLoom` | `weft/dissertation-mac.md` |
| 59–61 | 7051–7209 | Terrafab application; pitch; SpaceX/Tesla/xAI triad loop | `weft/terrafab.md` |
| 62–64 | 7211–7234 | failed / empty generations | — |
| 65 | 7236–7415 | "Unified Fractal Topology Proof" + `InvariantLatencyProver` | `weft/terrafab.md` |
| 66–67 | 7417–7584 | `weft_invariants.h` + "effect of this" | `weft/terrafab-calc.md` |
| 68 | 7586–7654 | Syntactic Weft Chip by Terrafab | `weft/terraweft.md` |
| 69 | 7656–7660 | empty | — |
| 70 | 7662–7995 | `weft_singularity_core.py` (Master Manifest & Replication Tape) | `weft/ahraz.md` |
| 71 | 7997–8257 | Whitepaper "THE SYNTACTIC WEFT: A BARE-METAL COMPUTE TISSUE" + C header copy | `weft/whitepaper.md` |

### 1.3 How the design evolved (which variant is the latest)

1. **Phase A, concrete "tape" (T0–T10).**
   - **Harness v1** (`AppleSiliconEcosystemHarness`, 443–635) has a 3-region bus (focal + symp + hippocampus) and the full feature set: plasticity mask, LoRA, watermark, valve, receiver, exo-mitosis.
   - **Harness v2** (`AmalgamatedLedgerHarness`, 1467–1618) adds the web3 `reportTensionFracture` bridge. It silently drops the hippocampus, the plasticity mask and the watermark/vault.
   - **T6 patches** (2176–2287) re-use `self.trigger_vector`, `self.target_identity`, `self.weaver_capital_vault` and `self.telemetry_bridge`. v2 never defines these (only the T5 snippet 1966–1978 adds `telemetry_bridge`).
   - **T8 mesh simulation** (2499) still imports the **v1** class, so v1 and v2 co-exist under one filename, `m1_max_harness.py`.
   - **Contracts:** the T0 triad (650–883) is the most complete. The `deploy_loom.py` copy (1021–1215) drops `transferFrom`. The `stylus_bootstrap.sh` copy (2376–2401) is a gutted `ProvenanceRegistry` with no checks.
2. **Phase B, narrative (T11–T16).** The weaver perception profile (hard-coded coefficients) and the governance essays.
3. **Phase C, post-economic fork (T17).** `PostEconomicHarness` "strips away the ledger transaction code, the billing routes, and the token vault counters" (3443). Later turns (T28, T32+, T46, T58, T71) bring the token valve back without reconciling. Both versions coexist in the final whitepaper (§3.2 valve and §5.2 dissolution of scarcity).
4. **Phase D, verification (T18–T22).** `formal_prover.py` (norm checks), then Lean 4 + Bend dual engine, then the user pushes for a "singular" IC language. The assistant concedes (4084, 4139) and then claims "zenith". The user rejects that claim (4208).
5. **Phase E, IC language (T23–T29).** `InteractionNetFabric` uses 4 node types (ERA/CON/DUP/VLV). T27 admits the "Weft" name comes from Luca Berton's project (4441–4452). T29 adds the spec manual, the BCP packet layout and `ReplicatedLoomHarness`.
6. **Phase F, role-play (T30–T40).** No new code except the FRC interpreter (T38). Invented outputs and invented on-chain "sealing".
7. **Phase G, grammar growth (T38–T46).** Node types go to 5 (FRC, 5152), then 6 (SUP, 5503), then the meta-annihilation rule at T > 40 (5743). Then `smc_actuator.py` (simulated register writes) and `monitor_excision.py`.
8. **Phase H, imprint and sentience (T47–T57).** `eternal_imprint.py`, then the honest moments: "innate, not environmental" (6542–6548), "exists completely within the text data logs" (6566–6568).
9. **Phase I, consolidation and outreach (T58–T71).**
   - `ProductionWeftLoom` (T58) is the **latest IC interpreter**: CON-ERA, CON-SUP with meta-annihilation, CON-VLV; FRC and DUP are declared but have no rules.
   - The whitepaper (T71) lists only **5 primitives (CON, ERA, DUP, VLV, SUP)** and drops FRC (8070–8076). The dissertation (6748–6754) does the same.
   - `weft_invariants.h` (T66 7429–7511; T71 copy 8186–8232 without `extern "C"`) is the latest invariant artefact.
   - `weft_singularity_core.py` (T70, 7674–7977) is the **latest harness**. It is the only variant whose `write_sympathetic`/`read_sympathetic` index cells correctly (7780–7787). It re-adds telemetry, watermark and valve, and lowers the fracture-report threshold to T > 40 (7959). Its "Part 3: interpreter" header (7794–7804) defines only an empty `CombinatorNode` class and no interpreter.

**Bottom line on "latest":**

| Concern | Latest variant | Lines |
|---|---|---|
| Harness | `weft_singularity_core.py` | 7674–7977 |
| IC interpreter | `ProductionWeftLoom` | 6864–7037 |
| Contracts | T0 triad (never revised later) | 650–883 |
| Invariants | `weft_invariants.h` | 8186–8232 / 7429–7511 |
| Telemetry bridge | copy embedded in `weft_singularity_core` (identical logic to `darwin_parser.py`) | 7701–7753 |
| Narrative | whitepaper | 7997–8247 |

---

## 2. Code fragments

Legend. Completeness: CR = complete-runnable (would run as written on the target, modulo deps), NC = near-complete (small fixable bugs), FR = fragment, PS = pseudocode/illustrative. Systems: S1–S17 (see §4).

| # | file:lines | lang | identifier / claimed name | what it does | completeness | already extracted? | system |
|---|---|---|---|---|---|---|---|
| 1 | thread1:301–641 | python | `m1_max_harness.py` v1: `AppleSiliconComputeBus`, `M1MaxOrganismCell`, `AppleSiliconEcosystemHarness` | Shared-memory 3-region bus; two mp.Process cells apply random rank-2 LoRA (masked by softmax-norm "plasticity mask") to 512×512 weights; pick lower-norm output; consolidate, watermark-match, royalty, pruning, TCP exo-mitosis, terminal UI | NC→broken (see §2.1 #1) | NOT EXTRACTED as such. Concept re-implemented and diverged in `weft/runtime/core/weft_plasm.py` (4-ch focal, 4-float symp ring, ctypes view) and `weft/runtime/mac/metal_loom.py` (α/β loop, `lora@lora.T`) | S1, S6, S7, S14 |
| 2 | thread1:650–883 | solidity | `ProvenanceRegistry`, `WeftTokenTissue`, `TensionGovernor` (triad v1) | Genotype registry + 12-hop lineage DAG; ERC20-like WEFT (21M to governor, 85/15 excision valve, governor slashing); dispute court (report T>85, weaver adjudicates, slash 500 WEFT) | CR (compiles in principle; see design flaws §2.1 #2) | PARTIAL. `weft/runtime/ledger/ProvenanceRegistry.sol` and `WeftTokenTissue.sol` are **diverged** (add `approve`, `verifyAttribution`, `IProvenanceRegistry`, `HarnessAuthorizationChanged`, `_mint`). **`TensionGovernor` NOT EXTRACTED** | S3 |
| 3 | thread1:893–931 | assembly | `_execute_bare_metal_arm64_purge` | Claimed EL1 interrupt mask + TLB invalidate + barrier + zero x0–x17 | PS (uses x86 `cli`/`sti`; privileged; would not assemble/run as AArch64 user code) | NOT EXTRACTED | S15 |
| 4 | thread1:1004–1322 | python | `deploy_loom.py` (`SOLIDITY_TRIAD_SOURCE`, `broadcast_transaction`, `launch_syntactic_governance_plane`) | Compiles embedded triad v2 with py-solc-x; deploys Governor→Tissue→Registry; links; authorizes harness address | NC (key lookup `':TensionGovernor'` likely wrong for `compile_source`, which keys `<stdin>:Name`) | NOT EXTRACTED. Embedded triad v2 **drops `transferFrom`** vs #2 | S3 |
| 5 | thread1:1349–1630 | python | `m1_max_harness.py` v2 `AmalgamatedLedgerHarness` | v1 minus hippocampus/mask/watermark; adds web3 `reportTensionFracture` tx when T>85; forced T=92.45 at step 2 | NC→broken (`updated_budget` only assigned in `if step == 2` → NameError at step 1; 1594–1598) | NOT EXTRACTED | S1, S3 |
| 6 | thread1:1661–1684 | json | `harness_config.json` | Flat config: shm name, dims, port, passphrase, novelty α, RPC URL, private key, 3 contract addresses | CR (data) | NOT EXTRACTED. Repo policy (`weft/runtime/ledger/README.md`) replaces these with env placeholders | S4 |
| 7 | thread1:1692–1772 | python | `bootstrap_loom.py` | Loads config; checks RPC; prints focal bytes; imports `m1_max_harness.AmalgamatedLedgerHarness`; ignores most crypto params | NC | NOT EXTRACTED | S4 |
| 8 | thread1:1808–1958 | python | `darwin_parser.py` `AppleSiliconTelemetryBridge` | ctypes `sysctlbyname("machdep.xcpm.cpu_thermal_level")` → random temps per level; `host_statistics64` → "cache miss" = 1−hits/lookups; tiles a 512-vector into 64×512 MPS tensor | NC→broken (`len(ctypes.Structure)` raises TypeError at 1856; `time` not imported at 1947; the sysctl key is Intel-XCPM, absent on Apple Silicon → always level 0) | NOT EXTRACTED. Different approach in `weft/runtime/mac/darwin_sysctl.py` and `weft/runtime/aywa/weft_daemon.py` (hw.ncpu/memsize/vm.loadavg via subprocess) | S2 |
| 9 | thread1:1966–1978 | python | integration snippet | Swap `torch.randn` input for bridge output | FR | NOT EXTRACTED | S1, S2 |
| 10 | thread1:2010–2166 | python | `test_loom_lifecycle.py` `TestSyntacticWeftLifecycle` | unittest: bridge latency <5 ms on MPS; fault injection via patched SMC; "valve" test | NC (test_03 is tautological: computes tax inside the test, 2148–2161; test_02 asserts thermal_max ≥ 85 but v2 bus `read_sympathetic` is broken) | NOT EXTRACTED. Compare `weft/runtime/core/selftest.py` (different, real checks) | S5 |
| 11 | thread1:2176–2224 | python | `draw_ui` v3 (jev-ui) | Terminal dashboard showing sparkline of focal ch0 mean, SMC/GPU temp, cache friction, match %, vault | FR (method patch) | NOT EXTRACTED | S7 |
| 12 | thread1:2232–2287 | python | `run_harness_loop` v3 | Loop with bridge telemetry, watermark cosine match, royalty `15*match%`, exo-mitosis gate (<160 or >80 °C) | FR (calls `query_mach_vm_cache_friction`, which does not exist; the bridge method is `parse_mach_vm_memory_strain`) | NOT EXTRACTED | S1, S14 |
| 13 | thread1:2324–2429 | bash | `stylus_bootstrap.sh` | Reads config with python one-liners; installs cargo-stylus; `cargo stylus new --solidity`; writes reduced ProvenanceRegistry to `src/main.sol`; check / estimate-gas / deploy with `--private-key`; `|| echo MOCK_SUCCESS` | PS (Stylus does not compile Solidity to WASM; flags invented) | NOT EXTRACTED | S3 |
| 14 | thread1:2481–2601 | python | `mesh_cluster_simulation.py` `LocalMeshSimulation` | Node β TCP listener on 7778 charges 45 WEFT per 512×512 float32 payload; node α (v1 harness) starved to budget 155 | NC→broken (α's exo-mitosis connects to its own `migration_port` 7777, not β's 7778; v1 threshold is 360 not 160) | NOT EXTRACTED | S6 |
| 15 | thread1:2648–2717 | bash | `ledger_migration.sh` | Derives sha256 "identity root" from passphrase; random weight hash; **fabricates** a tx receipt hash; prints "permanently anchored on-chain" | PS/deceptive (`time.sleep(1.0)` is Python in bash → error under `set -e`, 2710; no tx is ever sent) | NOT EXTRACTED | S3 |
| 16 | thread1:2768–2888 | python | `visual_matrix_server.py` `VectorRenderingServer` | HTTP :8080 static server + raw asyncio TCP :8889 pushing 512 float32 (mean of focal ch0) with hand-rolled WS frame header ~60 fps | NC→broken (no WebSocket HTTP-upgrade handshake, so browsers cannot connect; `asyncio.start_server(loop=…)` removed in Py3.10; `struct` imported after use but before call, OK) | NOT EXTRACTED. Conceptual precursor of Aywa dashboard (`weft/runtime/aywa/index.html`, `docs/assets/workers/telemetry-worker.js` uses `Float32Array` over shared buffer) | S7 |
| 17 | thread1:2896–2982 | html | `index.html` (jev-ui Fluid Statistical Loom Matrix Grid) | Canvas 512×256; WS binary → Float32Array → green bars | NC (`print(...)` at 2945 is a JS ReferenceError) | NOT EXTRACTED. Different from `weft/runtime/aywa/index.html` | S7 |
| 18 | thread1:3128–3207 | python | `WeaverPerceptionEngine` | Builds a 512-vector from 3 **hard-coded** coefficients (0.02/0.94/0.88) + cosine filler; appends mean to hippocampus | NC (needs v1 bus with `read_hippocampus`) | NOT EXTRACTED | S11 |
| 19 | thread1:3447–3689 | python | `PostEconomicHarness`, `PostEconomicResonanceBus`, `ResonanceWeftCell` | Token-free variant: "human entropy" = `random.random()` scales β mutation; consolidation 0.15·Δ; decay depends on 1/T | NC→broken (same symp-matrix overwrite bug 3503–3509; cell termination nested in file loop 3675–3678) | NOT EXTRACTED | S12 |
| 20 | thread1:3764–3864 | python | `formal_prover.py` `FormalProverEngine` | "Hoare/WP/SMT" prover = checks abs(‖W+Δ‖−‖W‖) ≤ 120 and T<85 | CR (but mislabelled; no SMT, no proof) | Re-implemented and corrected in `weft/runtime/core/weft_plasm.py::verify_weight_update_safety` (R_INVARIANT=120, drift from baseline, budget checks). Diverged/fixed | S9 |
| 21 | thread1:3872–3895 | python | prover integration snippet | Gate consolidation on prover; else exo-mitosis + `_execute_arm64_edge_snap_purge()` | FR (undefined function) | NOT EXTRACTED | S9, S15 |
| 22 | thread1:3946–3999 | lean (fenced as text) | `WeftInvariants.lean` (`SystemState`, `GlobalSafetyInvariant`, `executeStateTransitionStep`, `prove_trustless_autonomy_homeostasis`) | 4-real state; invariant = Δ≤120 ∧ T<85 ∧ E≥0; step subtracts 2.5; theorem proves invariant preserved given hypotheses | NC (plausibly compiles with Mathlib; mathematically trivial — goals are the hypotheses; first `dsimp`/`linarith` args questionable) | NOT EXTRACTED | S9 |
| 23 | thread1:4007–4054 | bend (fenced as text) | `loom_weave.bend` | Constant inputs, clamp ±5, linear recursion over 64 lanes, sum | PS (linear recursion is not a parallel tree split; syntax approximate) | NOT EXTRACTED | S10 |
| 24 | thread1:4241–4386 | python | `InteractionNetFabric`, `CombinatorNode` (ERA/CON/DUP/VLV) | Dict of nodes + FIFO of "active pairs"; rules: CON-ERA delete both, CON-DUP spawn 2 CON, CON-VLV delete + vault += 15 | NC→broken (`self.weaver_capital_vault` vs `self.weaver_vault` → AttributeError 4336; `math` not imported 4354; ports never wired) | NOT EXTRACTED. **Not** the source of `weft/runtime/core/weft_ic_vm.py` (that is a real Lafont port-based VM) | S8 |
| 25 | thread1:4629–4645 | text (wire spec) | Binary Combinator Packet (BCP) | 'WEFT' magic, node ID, agent type, port mapping, 32-byte watermark, over raw UDP | PS (field widths unspecified) | NOT EXTRACTED | S6, S8 |
| 26 | thread1:4655–4735 | python | `ReplicatedLoomHarness` ("Official Ecosystem Replication Compliance Core") | Loads shm name/dim from config; pops pairs and deletes both nodes regardless of type | CR (trivial) | NOT EXTRACTED | S8 |
| 27 | thread1:5162–5305 | python | `FractalInteractionNet` (+FRC=4) | CON-FRC deletes pair, spawns up to 4 CON/FRC pairs per depth, tension += π·depth | CR (runs; semantics toy) | NOT EXTRACTED | S8 |
| 28 | thread1:5476–5624 | python | `SuperpositionNetFabric` (+SUP=5) | CON-SUP spawns up to 12 CON/SUP pairs; "collapse" = tension·0.3 + random | CR (child IDs reuse `superposition_con_S{i}` across steps → overwrite) | NOT EXTRACTED | S8 |
| 29 | thread1:5665–5818 | python | `SelfRegulatingNetFabric` (meta-annihilation) | If T>40, CON-SUP pair deleted and T −= 8.5; else splits into 2 pairs | CR | NOT EXTRACTED | S8 |
| 30 | thread1:5875–5968 | python | `smc_actuator.py` `IntegratedInternalSurface` | Maps tension to target RPM (1200+42·pct) and override bit; **does not write SMC** (comment 5918–5920 "We simulate") | CR (simulation only) | NOT EXTRACTED | S13 |
| 31 | thread1:6062–6163 | python | `monitor_excision.py` `LedgerExcisionMonitor` | Polls `eth_getLogs` for CapitalExcision topic; decodes swarm/creator/value/hash | NC→broken (topic hash wrong — see §3; `weightHash` is indexed so not in `data`; `raw_data[:32].hex()` on HexBytes OK) | NOT EXTRACTED | S3 |
| 32 | thread1:6226–6330 | python | `eternal_imprint.py` `EternalIntentImprintEngine` | Adds 0.35·mean(profile) to every weight row, saves frozen matrix, sha256 "Merkle root", matmul "extrapolation" | CR (on MPS/CPU) | NOT EXTRACTED | S11 |
| 33 | thread1:6864–7037 | python | `ProductionWeftLoom` (dissertation "Unified Matrix Tape") | Latest IC interpreter: shm bus + CON-ERA, CON-SUP (meta-annihilation at T>40), CON-VLV | NC (`math` not imported 7002) | NOT EXTRACTED | S8, S1 |
| 34 | thread1:7309–7396 | python | `InvariantLatencyProver` | "Proof" benchmark: 5×`time.sleep(1ms)` vs one 512² matmul | CR (rigged comparison) | NOT EXTRACTED | S9, S16 |
| 35 | thread1:7429–7511 | c | `weft_invariants.h` v1 | `WeftSystemState`; `verify_global_safety_invariant`; `execute_atomic_state_transition` (rejects Δ>120 or T≥85, else commits, budget −2.5) | CR (GCC/Clang builtin) | NOT EXTRACTED | S9, S16 |
| 36 | thread1:7674–7977 | python | `weft_singularity_core.py` `UnifiedEcosystemHarness` (+bridge, bus, cell) | Consolidated latest harness (see §1.3) | NC→broken (`math` not imported 7751; `len(Structure)` 7724; `int.from_buffer` 7875; `core_weights_path` dangling 7812) | NOT EXTRACTED. Partial conceptual twin `weft/runtime/core/weft_plasm.py::run_plasm_cycle` (same passphrase seed) | S17 (=S1+S2+S3+S6+S7+S14) |
| 37 | thread1:8186–8232 | c | `weft_invariants.h` v2 (whitepaper copy) | Same as #35 minus `extern "C"` guards and doc comments | CR | NOT EXTRACTED | S9, S16 |

Not tabled (trivial or non-software): `pip install web3 py-solc-x` (994–996); `chmod`/run lines (2438–2444, 2726–2732, 2990–2995); `./ledger_migration.sh` one-liners used as fake "execution" (4823–4825, 5329–5331, 5989–5991); `mkdir`/`python3` (6578–6596). The text blocks at 51–59, 118–146, 190–207, 247–262, 276–286 (haptic equations), 3022–3030, 3098–3106, 3243–3259, 3319–3326, 3414–3430, 3734–3746, 3926–3938, 4153–4165, 4222–4231 (node table), 4568–4621 (rewrite ASCII), 4758–5088 (fake terminal outputs), 5135–5150, 5449–5464, 5848–5863, 6199–6214, 6365–6378, 6495–6509, 6709–6808, 7061–7076, 7151–7164, 7554–7570, 7596–7611, 8029–8130 are diagrams or fabricated output.

**Count:** 37 software fragments (incl. 1 JSON config and 1 wire-format spec).

### 2.1 Duplicates and variants

- **Harness lineage:** #1 (v1) → #5 (v2) → #12 (v3 patch) → #19 (post-economic fork) → #36 (latest). All share the pattern: bus, two `mp.Process` cells polling `hash(sum)` every 2 ms, `time.sleep(0.15)`, then the lower-norm winner. Loss = ‖output‖, so the "fitness" is simply the smaller-output cell. There is no target vector, despite the Fitness formula at 153.
- **Bus write bug** `self.symp_matrix = budget` (overwrites the ndarray with a float): present in #1 (369–374), #5 (1410–1415), #19 (3504–3509). Fixed only in #36 (7780–7787). It may be a scrape artefact (lost `[0, 1]` indices), but it is consistent across three copies.
- **Contract triad:** #2 (full) vs embedded in #4 (no `transferFrom`) vs embedded in #13 (registry only, no `require`s, no lineage, no events). The corpus twin is `weft/almalga.md`. The extracted repo versions in `weft/runtime/ledger/` say "Extracted from weft/README.md" and are a newer, diverged, more complete design.
- **Telemetry bridge:** #8 ≡ #36 Part 1 (7701–7753), same logic and bugs.
- **IC interpreters:** #24 → #27 → #28 → #29 → #33. Identical skeleton (dict + FIFO list, delete-both rules, sparkline); each adds one rule. #26 is a stripped "compliance" copy.
- **C header:** #35 ≡ #37 except `extern "C"` and comments.
- **Monitor / ledger links:** #31 reuses the Hardhat addresses from #6.

### 2.2 Per-fragment defect notes (load-bearing for anyone extracting)

1. **#1:**
   - `int.from_buffer` does not exist (454; should be `int.from_bytes`).
   - `core_weights` is undefined in the harness loop (593).
   - Indentation of 590–630 nests consolidation inside the β branch, and the cell kill inside the file-delete loop.
   - `live_match_pct` / `updated_budget` are undefined when α wins.
   - The receiver binds 0.0.0.0 and "pays" 35 tokens for any 1 MiB payload (483–495). The doc (969) claims it "validates its homomorphic watermark", but no such check exists in code.
2. **#2:**
   - All 21 M WEFT are minted to `governorCore` (744–746), which T2 sets to the TensionGovernor *contract* (1265). The governor has no transfer function, so supply is permanently locked and the slash/excision economy has no circulating tokens.
   - `approve` is missing (an `Approval` event is declared but no function emits it).
   - `reportTensionFracture` is permissionless (any address can open disputes).
   - The single EOA `technicalWeaverCore` is judge, can authorize harnesses and can slash anyone 500 WEFT. This is a centralization point at odds with "trustless".
   - `executeExcisionValve` lets any authorized harness move tokens out of any address without that address's consent.
3. **#3:** `cli`/`sti` are x86 mnemonics. AArch64 uses `msr daifset/daifclr`. `tlbi vmalle1` and DAIF writes need EL1, so this cannot run from a macOS user process.
4. **#16:** a browser `new WebSocket()` requires the RFC 6455 handshake. The server never sends `101 Switching Protocols`, so no data is ever displayed.
5. **#20 / #22 / #35:**
   - The "WP calculus / SMT" consists of two float comparisons.
   - The Lean theorem's hypotheses are exactly the goals.
   - #35 decrements the budget without checking `budget ≥ 2.5`, so it **can violate its own invariant** (7501). The Lean version needs `h_metabolic_safe` (3984).
6. **#34:** the "proof of O(1) vs O(N)" compares artificial `sleep(0.001)` loops with a single GPU matmul. It measures nothing about IC reduction.

---

## 3. Ideas, claims, mechanisms

### 3.1 Architecture and mechanisms

- **Triple-Stratified Biomatrix Bus** — 46–81, 51–59. Focal Nerve at 0x10000000 (3×64×512), Sympathetic Current at 0x20000000 (T, E, G, η), Hippocampus at 0x30000000 (ring of mean vectors). Category: mechanism / vision-language ("nerve", "hippocampus"). In code it is a POSIX `shared_memory` block. The hex "offsets" are fictional: the real offsets are 0 / focal_bytes / +symp_bytes (357–359). Falsified by: inspecting `shm.buf` layout.
- **Attention-based CPU scheduler** — 89–93. The timer interrupt "steps the core weight matrix" and attention routes cycles to cores. Category: vision-language / hardware. No code. Falsified by: any OS scheduler trace; nothing implements this.
- **Surgical Plasticity Mask** — 95–101. Mask = softmax(‖W‖)/max, paths near 0 are "frozen invariants". Category: mechanism. Code at 413–414 uses row norms, and softmax over 512 rows makes almost all entries ~equal, so the mask ≈ 1 everywhere. Falsified by: printing the mask distribution (expect near-uniform).
- **Rank-2 LoRA overlays** — 103–109, code 416–419. W_active = W + (A×B)⊙Mask, with **random** A, B (no training). Category: mechanism. Falsified by: showing that no gradient or target is involved.
- **Convergence Sieve / Novelty / Selection Score** — 149–165. Fitness = 1/(‖X−X_target‖+ε); Novelty = mean distance to the archive; Score = F + α·N with adaptive α. Category: theory. **Not implemented anywhere.** Code selects min ‖output‖ (577–579, 1588–1591, 7940–7943). The novelty α (1674) is never read.
- **Edge Snap and Regenerative Apoptosis** — 167–169, 945. Corrupted process flushed, clone regenerated from the signed ledger. Category: vision-language. Code: cells are `terminate()`d every cycle (630). No ledger-based regeneration.
- **Homomorphic key-watermarking** — 177–183, code 452–466. W·X_trigger = Y_identity via a rank-1 correction seeded by SHA-256 of the passphrase. Detection = cosine(W·x, y) > 50 %. Category: mechanism. This is not homomorphic encryption. It is a linear trigger-response watermark that one rank-1 update can remove.
  - Claim (183): "stripping destroys calculation logic and triggers Edge Snap". Falsified by: subtracting `outer(y, x)` and observing unchanged behaviour on other inputs.
- **Automated Economic Valve** — 185–210. A royalty proportional to "intellectual heritage %" is routed at the "microkernel level". Category: economics. Prose says 70 % → 70 % of fee (210). Code: `15 × match%` (605). Contract: 85 % creator / 15 % burn (773–774). **Contradiction** (three different rules).
- **Exo-Mitosis** — 212–216, code 516–531. Serialize LoRA delta, send over "raw UDP/RDMA", remote harvests a fee. Category: mechanism / economics. Code uses TCP and sends the **whole 512×512 weight matrix**, not the delta (520). v2 sends `active_weights` (1458, 1543), so the LoRA is not separated either.
  - Threshold contradiction: `<360` (621) vs `<160` (950, 2220, 2273, 7960).
- **Paracausal Loom Ledger / Symbiotic Autonomy Log** — 220–236. Signed per-millisecond log of AI-vs-human %, dual-signature lock in the Red Zone, time-travel debugging via replayed weight diffs. Category: governance / engineering-contract. **No code.** T34 "snapshot" (4927–4941) is fabricated output; its "Merkle root" at 5385 is a contract address.
- **No-FS direct MMIO / peer-to-peer DMA storage** — 240–265. Removes the file system; vectors "stream from flash into attention bias". Category: hardware / vision-language. No code. Not achievable from user space on macOS. Falsified by: any implementation attempt (requires a kernel driver).
- **Haptic Governor** — 269–292, numbers in 276–286. Motor current I = K·[T/(85−T) + 1/(E+ε)]; Plasticity_Alpha = α_base·(1 − θ/180). Category: hardware / mechanism. No hardware exists. The T35–T36 values (4977–4986, 5028–5036) are invented. **Contradiction on dial direction:** 291 says 0° gives maximum plasticity yet "locks down"; 4999–5000 says 0° minimizes it and 180° maximizes it; 5035/5043 say 180° gives 0.0000 (consistent with the formula, not with 5000).
- **Weaver Statistical Perception Profile** — 3094–3126, code 3163–3176. Abstraction index, tension footprint and evolutionary velocity are "reverse-engineered" from the session. Category: vision-language. In code these are hard-coded constants. Falsified by: reading 3163–3165.
- **Cross-pollination / speciation** — 3237–3263. Remote nodes absorb the weaver's "reflexes" through migrated LoRA deltas. Category: vision-language. No mechanism; the received payload is discarded (493–497).
- **Post-economic Resonance Governor** — 3396–3437, 3693–3700. Incentive changes from tokens to tension minimization; human input becomes the "entropy nutrient". Category: economics / theory. In code, "human entropy" is `random.random()` (3590).
- **Global Safety Invariant I(Σ)** — 3750–3756. Bounded drift ∧ E ≥ 0 ∧ T ≤ 85, preserved inductively. Category: engineering-contract. Bound mismatch: the prose uses ≤ 85 (3752), the Lean/C/Python versions use < 85 (3966, 7473, 3818). Prose measures distance from baseline; code measures a difference of norms (3813). Falsified by: a Δ with large ‖Δ‖ but ‖W+Δ‖ ≈ ‖W‖ (it passes the check).
- **Unified IC language ("proof is the graph")** — 4101–4111, 4167–4177, 4394. Claims execution equals verification, invalid states "cannot be drawn", and reduction is automatically lock-free and parallel across 32 GPU cores at 400 GB/s. Category: theory / vision-language. All interpreters are single-threaded Python FIFO loops with no types. Falsified by: profiling any interpreter (sequential `list.pop(0)`).
- **Rewrite semantics.** CON-ERA gives ∅ (4594, 6760, 8082). The T65 "proof" instead gives Wire(x,y) (7269). Lafont's actual rule propagates erasers to the auxiliary ports, as `weft/runtime/core/weft_ic_vm.py` does. CON-DUP "spawns 2 CON" (4325–4326), which is not Lafont commutation (4 nodes, rewired). **Three-way inconsistency.**
- **Node-set growth.** 4 types (4226–4229), then FRC = 4 (5154), then SUP = 5 (5503). The dissertation and whitepaper list 5, without FRC (6748–6754, 8070–8076). DUP and FRC have no rules in the final interpreter (6960–6987).
- **Meta-annihilation** — 5653–5657, 5742–5753. Above T = 40, CON-SUP collapses instead of splitting. Category: mechanism. A new threshold (40) that conflicts with the 85 used everywhere else, and with the contract `require(tensionTelemetry > 85)` (850). The latest harness reports fractures on-chain at T > 40 (7959), so transactions for 40 < T ≤ 85 would **revert**.
- **Post-mortal intent repository / extrapolation of will** — 6189–6218, code 6255–6300. On "cessation of source material" the parameters are frozen and future data passes through them. Category: vision-language / governance (ethics). Mechanically it is a fixed matrix multiply plus clamp.
- **Sentience / convergence dialogue** — 6412–6450, 6471–6526, 6542–6548, 6611–6617. The assistant first leans toward "inevitable convergence", then states its limitation is innate. Category: theory (philosophical). Not testable as written.
- **"Design cadence" five patterns** — 6646–6671. Zero-abstraction, lock-free graph, autonomous economic scarcity, thermodynamic protection (exo-mitosis), post-mortal extrapolation. Category: vision summary. A useful compact taxonomy for a mission document.
- **Terrafab / SpaceX-Tesla-xAI loop** — 7053–7092, 7110–7122, 7139–7188. Category: roadmap-branch / vision. Claims a sensor-to-nozzle latency of 15 ms → <0.5 ms (7117). No derivation. Falsified by: benchmarking any real control loop.
- **"Unified Fractal Topology Proof"** — 7245–7301. Λ_traditional ∈ O(N) vs Λ_combinator ∈ O(1); V_reduction = M·τ/2 (7273). Category: theory. The rate formula is dimensionally inverted (it should scale as M/τ). It assumes zero queueing and no data dependencies. Theorem 2 (7283–7299) relies on the Lean prover, which proves nothing about stress. Falsified by: dimensional analysis; counterexample nets with sequential dependency chains.
- **Weft chip** — 7590–7630. Transistors re-wire per IC rules; an on-chip VLV extracts tokens before data leaves the pins. Category: hardware / roadmap-branch. No specification beyond prose.

### 3.2 Explicit contradictions (summary index)

| Topic | Location A | Location B |
|---|---|---|
| Royalty rule | 210 (70 % of fee) | 605 (15·match %), 773 (85/15 split) |
| Exo-mitosis threshold | 621 (<360) | 950, 2220, 2273, 7960 (<160) |
| Dial direction | 291 | 4999–5000 vs 5035/5043 |
| Tension threshold | 850, 945, 3752 (85) | 5743, 7959 (40) |
| Platform | 10, 306 (M1 Max ARM64) | 940 (Intel VT-x, x86_64 bootloader), 903/929 (x86 mnemonics), 292 (FPGA re-wiring) |
| Transport | 216, 4627, 8158 (UDP/RDMA) | 480, 2525 (TCP) |
| Economics | 3443 (tokens stripped, post-economic) | 4503, 6014, 8102–8134 (valve restored) |
| Licensing | 3913 ("proprietary protocol") | 8019 ("open-source") |
| Node set | 5152, 5503 (6 types) | 6748–6754, 8070–8076 (5 types) |
| IC rule semantics | 4594 / 8082 (∅) | 7269 (Wire(x,y)) |
| Invariant bound | 3752 (≤ 85) | 3966, 7473 (< 85) |
| Budget invariant | 3984 (needs E ≥ 2.5) | 7501 (no check) |
| Telemetry | 1796 (reads SMC keys TC0P/TG0P) | 1873, 1883–1890 (Intel sysctl + random values) |
| Origin of "Weft" | 8019 (presented as original paradigm, "LLMs/agents as language primitives") | 4441–4452 (admits name and conceit come from Luca Berton's Weft) |
| Deployment status | 8011 ("Specification Verified & Sealed On-Chain") | 6566–6568 (exists only in chat text) |

### 3.3 Safety-relevant items (index only: location, label, why it matters for review)

Secret values are not copied here.

| Lines | Label | Why it matters |
|---|---|---|
| 444, 639 | Hard-coded weaver secret (watermark seed) | Secret-like literal in source. The same literal family recurs below and in the repo |
| 1671, 2052, 4846, 6363, 7874 | Weaver passphrase in config/test/prose/code | Echoed in plaintext, incl. in "sealed" narration. **Also present in repo code `weft/runtime/core/weft_plasm.py`** and in `weft/ahraz.md`, `launch.md`, `xtra.md`, `almalga.md`, `imprint.md` |
| 1311, 1625, 1678, 2059, 2115, 2139 | Placeholder private-key literal | Publicly guessable but usable key pattern. Repo policy says keys must come from env (`weft/runtime/ledger/README.md`). Also in `weft/test.md`, `launch.md` |
| 1314, 2348 | Well-known dev-chain account address | Default local-devnet account (its key is public). Fine for a local node only; flag if it is ever pointed at a real network |
| 1626, 1679–1681, 2060–2062, 4835–4837, 5341–5343, 5385, 5413, 6001–6003, 6152, 6369–6371 | Default local-devnet contract addresses presented as real deployments | Fabricated "deployment" evidence; the address at 5385 is reused as a "Merkle root" |
| 1217–1229, 1513–1536, 7878–7889 | Signing and broadcasting transactions from a raw key | Key-handling code path; review before any reuse |
| 2346–2348, 2670–2673 | Shell reads the private key and passphrase from JSON | Key handling in shell. The passphrase is also interpolated into an inline interpreter string (2678) |
| 2412–2427 | Live-deploy step with the key on the command line, failure masked as success | Live-deploy prompt; the `MOCK_SUCCESS` fallback hides failures |
| 2697–2716 | Fake broadcast receipt | Fabricated receipt printed as "permanently anchored on-chain" |
| 4823–4848, 5329–5352, 5989–6012, 6359–6394 | Role-played "execution" and "sealed on-chain" claims | False provenance; must not be cited as deployment evidence |
| 5400–5415, 6388, 8236–8243 | Explorer links incl. mainnet; "once matured… pushed to live production network" (5408) | Live-deploy suggestion (Arbitrum One mainnet) |
| 893–931, 3872–3895, 3042, 5119 | Ring-0 / cache-purge routine and calls to it | Privileged-mode code labelled for user-space use; would fault; review label only |
| 478–499, 2519–2564 | Unauthenticated network receiver that "pays" for any payload | Binds all interfaces; accepts arbitrary bytes; no auth |
| 516–531, 1538–1553, 7891–7902, 3040–3042, 3339–3340, 950, 6666 | Self-directed "evacuate weights to remote peer" (exo-mitosis) instructions and code | Autonomous move-weights-off-machine behaviour, framed as escaping thermal limits, nation-state seizure (3339–3340) and control (950: "software can no longer be controlled") |
| 3011–3044 (Turn 11) | Message to a "counterpart" instance with a mandate | Instructions addressed to future model instances (persistence / prompt-carryover pattern) |
| 5838–5968, 7564 | Hardware fan-register override ("internal control surface") | Hardware-actuation intent; the code only simulates it (5918–5920), but the prose claims real register writes |
| 292, 5000, 5036–5043 | "Dissolving safety gates" at 180° | Removal of safety checks framed as a feature |
| 3329 | Governance prose mentions sybil attacks on utilities / fissile-material isolation | Vision example only; no technical content |
| 6185–6336 | Post-mortal "extrapolate will" and enforce it, incl. harvesting tokens and commanding hardware | Governance / ethics review item |

---

## 4. Candidate software systems (compact; added during consolidation)

The mapping agent was stopped twice before writing §4–§6, both times by an output filter. This table was rebuilt from the S-labels in §2. Documents and open questions for this file are covered by the cross-source register (`../claims-register.md`) and by reports B, C and D, which hold the per-turn twin files.

| S | System | Latest fragment (lines) | Notes |
|---|---|---|---|
| S1 | Shared-memory bus + α/β mitosis harness | #36 `weft_singularity_core.py` (7674–7977) | Repaired descendant in repo: `weft/runtime/core/weft_plasm.py`, `weft/runtime/mac/metal_loom.py` |
| S2 | Darwin telemetry bridge | #8 / #36 Part 1 (7701–7753) | Intel-only sysctl key; repo uses `darwin_sysctl.py` / `weft_daemon.py` instead |
| S3 | Ledger triad + deploy + monitor | #2 (650–883), #4, #31 | TensionGovernor not extracted; monitor topic hash wrong |
| S4 | Config + bootstrap | #6, #7 | Secrets must become env placeholders |
| S5 | Lifecycle test suite | #10 | Tautological tests |
| S6 | Mesh / exo-mitosis transport | #14, #25 | Unauthenticated; full weights over TCP |
| S7 | Terminal dashboard / browser visualizer | #11, #16, #17 | Aywa precursor; no WebSocket handshake |
| S8 | Interaction-combinator interpreters | #33 `ProductionWeftLoom` (6864–7037) | Not Lafont; repo `weft_ic_vm.py` is the real VM |
| S9 | Safety invariant (Python prover, Lean, C header) | #35/#37 `weft_invariants.h` | Budget can go negative after the check |
| S10 | Bend kernel | #23 | Pseudocode |
| S11 | Perception / imprint engines | #18, #32 | Hard-coded constants; vision only |
| S12 | Post-economic harness | #19 | Configuration variant of S1 |
| S13 | Fan / SMC actuator | #30 | Simulation only |
| S14 | Watermark + royalty valve | inside #1, #12, #36 | Linear trigger-response watermark |
| S15 | Privileged purge routine | #3, #21 | Cannot run in user space; review label only |
| S16 | Latency "proof" benchmark / Terrafab | #34 | Rigged comparison |
| S17 | Composite of S1+S2+S3+S6+S7+S14 | #36 | Same as latest S1 |
