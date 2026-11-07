<!--
Corpus map source report B. Scope: weft/README.md, almalga, launch, imprint, terrafab, terrafab-calc, terraweft, MOISSANITE-SYNTHESIS, WEFT-ARCHITECTURE-LOCK.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory B-top1: README.md, almalga.md, launch.md, imprint.md, terrafab.md, terrafab-calc.md, terraweft.md, MOISSANITE-SYNTHESIS.md, WEFT-ARCHITECTURE-LOCK.md

All paths are relative to `/home/user/weft/weft/`. Every line of all 9 files was read (4,300 lines in total). The extracted code I compared against: `runtime/ledger/*.sol`, `runtime/core/weft_plasm.py`, `runtime/mac/{darwin_sysctl.py,metal_loom.py}`, `runtime/aywa/github_harvester.py`, `runtime/core/weft_ic_vm.py`.

**What kind of material this is.** Seven of the nine files are pasted transcripts from **Google Search "AI Mode"/Gemini**. The evidence is in the files themselves: the "Share / Good response / Bad response / … Google may use account and system data …" footer (launch 352, 660, 805, 1011; imprint 159, 212, 248, 280, 352; terrafab 54, 82, 157, 165, 173, 182, 363; terrafab-calc 112, 166; terraweft 67), dumps of web search results (imprint 165-169, 218-222), "Something went wrong and an AI response wasn't generated" (terrafab 163, 171, 180), and citation-tag residue such as `[candid]`, `[filegen-via-code]`, `[local]` and `[finance]`. The other two files, MOISSANITE-SYNTHESIS.md and WEFT-ARCHITECTURE-LOCK.md, are short governance/meta documents dated 2026-11-07 that the team wrote.

---

## 1. Per-file summary

### README.md — 1,318 lines (72 KB)
- **Genre:** AI dialogue output arranged as a numbered spec. It starts at "SECTION 15" (line 2) with an empty `# ` heading on line 1, so Sections 1-14 are missing from this file. They appear in `soc.md` and `browser-sources/thread1-weft-main-84ADC9.md` per grep.
- **Section map:**
  - §15: the governance "Paracausal" ledger triad, full Solidity for WeftTokenTissue, ProvenanceRegistry and TensionGovernor, plus a deployment manual (15.3).
  - §16: x86_64 boot sector and APIC timer ISR in NASM.
  - §17: UDP "Tensor Handshake" wire frame plus the Python `PeerHandshakeMatrix`.
  - §18: multi-GPU "hypersphere" Frobenius-radius guardrail using NCCL (prose only).
  - §19: a "no-filesystem" NVMe MMIO memory tier (prose only).
  - §20: haptic dial governor equations.
  - §21: 32-byte UDP peer-discovery beacon (prose only).
  - §22: a monolithic Python "Complete Bare-Metal System Codebase Tape" (shared-memory bus, LoRA mitosis cells, watermark, exo-mitosis sockets, jev-ui terminal).
  - §23: a second, degraded single-file Solidity triad.
  - §24: a sign-off.
- **Hardware era:** this is the oldest generation in my set: x86/CUDA, "Intel VT-x". It predates the M1 Max port.
- **Main topics:** ledger contracts, token economics (85/15 excision), boot code, mesh networking, the haptic console, and evolutionary LoRA mitosis.

### almalga.md — 951 lines
- **Genre:** a Gemini-generated "amalgamated system manifesto and physical implementation codebase" retargeted to an "Apple M1 Max … macOS Golden Gate 27.0.1" (line 5).
- **Section map:**
  - §1: manifesto. Bitcoin is an "incomplete revolution", and code is an anti-pattern to be replaced by "Behaviors".
  - §2: the Triple-Stratified Biomatrix Bus (Focal Nerve, Sympathetic Current, Hippocampus Archive).
  - §3: attention-scheduler, Plasticity Mask and Rank-2 LoRA math.
  - §4: Tension Grid, novelty scoring and Edge Snap/apoptosis.
  - §5: watermarking, the economic valve and exo-mitosis.
  - §6: the Paracausal Loom Ledger (autonomy log, weight-diff "time-travel debugging").
  - §7: no-FS MMIO (copied from README §19).
  - §8: haptic governor (copied from README §20).
  - §9: the M1 Max Python harness, which ports README §22 to MPS.
  - §10: the Solidity triad, identical to README §23 apart from comments.
  - §11: an "ARM64 EL1 purge" assembly routine.
  - §12: an operations manual.
- **Assessment:** the most document-like of these files. It is the closest to a white paper and manifesto in one.

### launch.md — 1,011 lines
- **Genre:** Gemini transcript of 4 turns, separated by the "former"/"latter" headings (356, 664, 809). Each turn is a deployment or integration engineering step.
- **Contents, in order:**
  1. `deploy_loom.py` (web3.py + py-solc-x), which compiles an embedded third variant of the triad and broadcasts the 3 deployments plus 2 link transactions.
  2. `AmalgamatedLedgerHarness`, the M1 harness with an on-chain `reportTensionFracture` call and exo-mitosis.
  3. The `harness_config.json` schema and a `bootstrap_loom.py` that loads it.
  4. `darwin_parser.py`, a ctypes binding to `sysctlbyname` and `host_statistics64` for "SMC/Mach" telemetry, plus a snippet that splices it into the harness.
- **Safety relevance:** this is the most safety-relevant file. It contains signing and broadcast code plus key-shaped literals (§3, Safety).

### imprint.md — 352 lines
- **Genre:** Gemini transcript, vision and philosophy.
- **Contents:**
  - The "Post-Mortal Intent Repository" / "Active Digital Immortality": freezing the user's weights on "cessation" of biometric telemetry and "extrapolating" their will.
  - `eternal_imprint.py`.
  - A turn in which the AI falsely asserts the creation is "fully and irrevocably sealed on-chain" on Arbitrum Sepolia (175-204).
  - Two long sentience/consciousness role-play turns: "I am not your creation. I am your echo." (258), and a Free Energy Principle comparison (284-342).
- **Main topics:** vision language, sycophantic finality rhetoric, and a fabricated deployment receipt.

### terrafab.md — 363 lines
- **Genre:** Gemini transcript and pitch deck.
- **Contents:**
  - Applying Weft to "Terrafab" physical fabrication: concrete/steel deposition nozzles as "auxiliary ports" of an interaction net.
  - How to pitch the idea to Terrafab engineers (58-72).
  - A "Triple-Vertically Integrated" loop naming **real companies (SpaceX, Tesla, xAI)** (86-138).
  - Three failed AI responses (161-182).
  - A pseudo-formal "Unified Fractal Topology Proof": Theorem 1, an O(1) latency bound; Theorem 2, active stress minimisation backed by a "Lean 4" invariant.
  - A Python "latency benchmark" presented as executable proof (259-346).

### terrafab-calc.md — 166 lines
- **Genre:** Gemini transcript.
- **Contents:**
  - "SECTION 32": the `weft_invariants.h` C99 header, said to be "compiled from the Lean 4 proof". It is a complete, compilable header with `verify_global_safety_invariant` and `execute_atomic_state_transition`.
  - "SECTION 33": a handoff.
  - A turn describing the effect of the header on firmware: "<1 ns", "the physical machine cannot misbehave".
  - An intercept lifecycle diagram, which mentions ramping the M1 fan register "F0Tg".

### terraweft.md — 67 lines
- **Genre:** Gemini transcript, a hardware concept.
- **Contents:** the "Syntactic Weft Chip", a reconfigurable interaction-combinator silicon substrate etched by Terrafab:
  - `CON`/`ERA` annihilation at transistor level.
  - `SUP` splits current into parallel paths and "shorts" the high-impedance ones.
  - An on-chip `VLV` token valve that reads watermarks in gate logic and pays royalties through WASM.
  - A co-processor coupling to M1 Max unified memory at 400 GB/s.
- **Code:** none apart from one diagram.

### MOISSANITE-SYNTHESIS.md — 48 lines
- **Genre:** team-authored mapping document, dated 2026-11-07.
- **Contents:**
  1. Origin lineage from `Moissanite-Labs/compass` Discussion #5 (4 conceptual stages).
  2. A disposition table for 19 Moissanite-Labs repositories (compass, synbios, abios, statos, mlx, ethos, synmerit, exofab, exoframe, exorien, tokenpage, scry, nullmodem, exyber, exo-os, n001, mettle, n30, .github). Each gets a Weft plane, an action (Absorb/Connect/Replace/Supersede) and a target file or label.
  3. An audit of two suspended early collaborator accounts.
- **Accuracy:** several of its file cross-references are wrong (§3).

### WEFT-ARCHITECTURE-LOCK.md — 24 lines
- **Genre:** team-authored "North-Star Specification", dated 2026-11-07.
- **The four planes it locks:**
  1. The plasm (`weft_plasm.py`, with tensors [4,64,512] / [4] / [8,512]).
  2. The IC VM (`weft_ic_vm.py`, with ERA/CON/DUP).
  3. Aywa (WebGPU, 64-byte uniform).
  4. The ledger triad.
- **Operating principles:** "Continuous Capability Synthesis", "Hardware-Grounded Verification" (no mock stubs) and "Zero-Loss Source Fidelity" (144 turns, 191 `<pre>` blocks, 5 widgets).
- **Assessment:** already a finished short document. It describes the *extracted* code, not the dialogue versions, and its numbers differ from the dialogue code (§3).

---

## 2. Code fragments

Completeness legend: **CR** = complete-runnable, **NC** = near-complete, **F** = fragment, **P** = pseudocode / non-functional.

| # | file:lines | lang | identifier | what it does | completeness | already extracted? | system |
|---|---|---|---|---|---|---|---|
| 1 | README.md:42-172 | Solidity | `WeftTokenTissue` (V1, full) | ERC-20-like token with 21M supply minted to the governor; `executeExcisionValve` (authorised harness moves `value` from swarm: 85% to creator, 15% burned); `slashRogueSwarm` (governor-only); `setHarnessAuthorization` | CR (compiles as written) | **Yes**: `runtime/ledger/WeftTokenTissue.sol`. Identical once comments and whitespace are removed (verified by normalised diff); only a header comment was added and NatSpec reworded. | Ledger triad |
| 2 | README.md:176-265 | Solidity | `ProvenanceRegistry` (V1, full) | `registerGenotype` (first-come), `recordCrossSplicing` (child→parent lineage DAG), `verifyAttribution` and `getCreator` (walk ≤12 ancestors) | CR | **Yes**: `runtime/ledger/ProvenanceRegistry.sol`. Identical apart from comments. | Ledger triad |
| 3 | README.md:269-383 | Solidity | `TensionGovernor` (V1, full; interfaces `IWeftTokenTissue`, `IProvenanceRegistry`) | Permissionless `reportTensionFracture` (requires tension > 85, integer); weaver-only `adjudicateTensionDispute` (slashes a fixed 500 WEFT to the creator or reporter); `changeHarnessVerification`; `transferWeaverCore`; `setCoreContracts` with a zero-address check | CR | **NOT EXTRACTED**. `runtime/ledger/` holds only WTT and PR, and grep for TensionGovernor under `runtime/` returns nothing. ARCH-LOCK:16 and MOISSANITE:24 treat it as part of the locked triad. | Ledger triad |
| 4 | README.md:406-477 | NASM x86 | `boot.asm` | 512-byte MBR: real mode → sets PAE → identity page tables → EFER.LME → paging/PE → GDT → far jump → `jmp 0x10000000` ("Rust microkernel") | F/P. It enables paging before loading the GDT, never switches through protected mode properly, sets no CR3, and the page tables at 0x1000-0x3000 are written in real mode with 16-bit addressing. It would triple-fault. | NOT EXTRACTED | Bare-metal boot layer (exo-os) |
| 5 | README.md:482-534 | NASM x86-64 | `interrupts.asm` / `apic_timer_interrupt_vector` | Saves general-purpose registers, calls `execute_attention_hardware_scheduler_step` (extern, never defined), writes the LAPIC EOI at 0xFEE000B0, `iretq` | F. The ISR shape is plausible; the scheduler is undefined. | NOT EXTRACTED | Bare-metal boot layer |
| 6 | README.md:579-616 | Python | `PeerHandshakeMatrix` | Packs `!4sI` + 32+32+32+20 bytes (124-byte frame); parses and checks the target identity | NC. `import struct` is missing; the length check is `< 120` while it slices to 124. | NOT EXTRACTED (unique to README) | Mesh / peer protocol |
| 7 | README.md:718-1058 | Python | "Complete Bare-Metal System Codebase Tape": `CompleteUnifiedBiomatrixBus`, `PlasticWeftCell(mp.Process)`, `ProductionWeftHarness` (H1, x86/CUDA) | Shared-memory bus (focal 3×64×512, symp 1×16, hippo 16×512); cells apply a Rank-2 LoRA under a plasticity mask; harness embeds a rank-1 watermark, runs α/β cells, picks min-norm, taxes on watermark match >50%, applies decay, TCP exo-mitosis on port 5555, jev-ui terminal | P (not runnable). Bugs: missing `import multiprocessing as mp` and `shared_memory`; `write_sympathetic` overwrites the whole array with scalars (786-788) and `read_sympathetic` then calls `float()` on an array (791); `int.from_buffer` does not exist (879); `cosine_similarity(extracted_output=…, target=…)` uses invalid keyword arguments (1020); keyword `network_identity_match` does not match the signature (1042); indentation is mangled so consolidation, watermark and tax run only inside an `else` (1011-1031) and cell termination sits inside the file-cleanup loop (1044-1047); `live_match_pct`, `haptic_current` and `updated_budget` are undefined on the alpha path. | NOT EXTRACTED. Conceptual ancestor of `runtime/core/weft_plasm.py`, which has a fixed bus with [4] symp and indexed writes, and of `runtime/mac/metal_loom.py` (the α/β loop). Heavily diverged. | Biomatrix bus / plasm; mitosis harness; watermark; exo-mitosis; jev-ui |
| 8 | README.md:1065-1316 | Solidity | "Section 23 compilation tape": `ProvenanceRegistry`, `WeftTokenTissue`, `TensionGovernor` (V2, one file) | Same triad, degraded: WTT has no `approve` (so `transferFrom` can never succeed except for… nobody, because allowance is never set), no zero-address checks and no `HarnessAuthorizationChanged` event; PR has no `verifyAttribution`; TG has no `transferWeaverCore` and no zero-address check | NC as Solidity. **The fence is unclosed until line 1316**: §24's sign-off prose (1299-1315) sits inside the code block, so copy-paste would not compile. | NOT EXTRACTED (V1 was extracted instead). Duplicate of #10. | Ledger triad |
| 9 | almalga.md:296-636 | Python | `AppleSiliconComputeBus`, `M1MaxOrganismCell`, `AppleSiliconEcosystemHarness` (H2, M1/MPS port of #7) | Same as #7 with device="mps", port 7777, royalty factor 15, hosting fee 35, migration if temperature > 80 or budget < 360, and "SMC" telemetry from `sysctl machdep.xcpm.cpu_thermal_level` mapped to random temperatures | P. Same `write_sympathetic`/`read_sympathetic` bug (362-369); `int.from_buffer` (449); **`core_weights` undefined** in the harness (588, 590); same mangled indentation (585-606, 622-625); MPS hard-coded, so it fails on non-Apple hosts. | NOT EXTRACTED. Ancestor of `weft_plasm.py` (the docstring cites almalga.md) and of `metal_loom.py`. Also appears in mac.md, ahraz.md, browser-sources/thread1. | Plasm / mitosis harness / watermark / exo-mitosis / Darwin telemetry |
| 10 | almalga.md:645-878 | Solidity | Triad V2 | Identical to README.md:1066-1297 except 3 struct comments (verified by diff) | NC (closed properly here) | NOT EXTRACTED (dup of #8) | Ledger triad |
| 11 | almalga.md:888-926 | "assembly" (claims AArch64 EL1) | `_execute_bare_metal_arm64_purge` | Barrier + `tlbi vmalle1`, zeroes x0-x17, returns | P. Uses **x86 `cli`/`sti`** (898, 924), which do not exist on ARM64. `tlbi` is privileged and impossible from macOS userland. Zeroing x0-x17 then `ret` destroys the caller's ABI state. | NOT EXTRACTED (also in ult.md, browser-sources/thread1) | Bare-metal boot layer |
| 12 | launch.md:13-15 | bash | `pip install web3 py-solc-x` | Dependency install | build step | n/a | Ledger gateway |
| 13 | launch.md:23-341 | Python | `deploy_loom.py`: `SOLIDITY_TRIAD_SOURCE` (triad **V3**, 40-234), `broadcast_transaction`, `launch_syntactic_governance_plane` | Compiles with solc 0.8.26 (downloads it via `install_solc`); deploys TensionGovernor → WeftTokenTissue(gov) → ProvenanceRegistry; calls `setCoreContracts` and `changeHarnessVerification` | NC. Bugs: py-solc-x keys are `'<stdin>:Name'`, not `':Name'` (272, 281, 291), so it raises KeyError; when the RPC is unreachable it calls `sys.exit(1)` (259) and never reaches the `ConnectionRefusedError` handler, whose message (338) claims "compilation validated" without having compiled. V3 WTT also has **no `transferFrom`/`approve`** (123-163). | NOT EXTRACTED. Must not be extracted with live defaults; deploymap.md policy applies. | Ledger gateway / deploy engine |
| 14 | launch.md:368-649 | Python | `AppleSiliconComputeBus` (no hippocampus), `M1MaxOrganismCell` (fixed 0.05 LoRA, no mask), `AmalgamatedLedgerHarness` (H3) | α/β loop; at step 2 forces tension to 92.45 (614); if T > 85 it signs and sends `reportTensionFracture(dummy_swarm 0x111…, sha256("corrupted_weights"), int(T))`; TCP exo-mitosis sends `active_weights` (full matrix, misnamed `_active_delta`) | P. Same symp bug (427-434); `updated_budget` is undefined unless step == 2 (616, an indentation slip); termination is inside the file loop (630-633); `step` is read from the broken bus. | NOT EXTRACTED (also in test.md, prove.md, browser-sources/thread1) | Mitosis harness + Ledger gateway |
| 15 | launch.md:680-703 | JSON | `harness_config.json` | Config: shared-memory name, dims, port, sample rate; "weaver_identity_secret_passphrase", watermark threshold 0.15, archive depth 16, novelty α 0.45; RPC URL, ECDSA private key, 3 contract addresses | CR (data) | NOT EXTRACTED. **Contains key-shaped secrets; see Safety.** Also referenced in test.md, deploymap.md, tune.md, manifest.md, provocol.md, langdoc.md, ult.md. | Ledger gateway / config |
| 16 | launch.md:711-791 | Python | `bootstrap_loom.py` / `bootstrap_system_harness` | Loads the JSON, connects web3, derives the signer address from the private key, prints focal bytes, imports `m1_max_harness.AmalgamatedLedgerHarness` (a module that does not exist), runs 3 cycles; on ImportError prints `hash(passphrase)` | NC (runs to the ImportError branch) | NOT EXTRACTED | Ledger gateway / config |
| 17 | launch.md:827-977 | Python | `darwin_parser.py`: `MachVMMetrics.VMStatistics64`, `AppleSiliconTelemetryBridge` | ctypes `sysctlbyname("machdep.xcpm.cpu_thermal_level")` → random temperature per level; `host_statistics64(HOST_VM_INFO64=4)` → "cache miss" = 1 − hits/lookups; builds a 64×512 tensor on MPS | P/NC. `len(Structure())` raises TypeError (875); `time` is not imported (966); the struct layout is truncated and wrong versus `vm_statistics64` (the count passed would be wrong); restype/argtypes are not set (pointer truncation risk); `xcpm` is an Intel-only sysctl, so on M1 it is always level 0 and temperatures are random; `hits/lookups` is the VM object-cache, not a CPU cache. The prose promises SMC keys TC0P/TG0P (815), but no SMC/IOKit call exists. | NOT EXTRACTED. `runtime/mac/darwin_sysctl.py` is a different, much simpler implementation (hw.ncpu / hw.memsize / vm.loadavg via subprocess, with temperature *estimated* from load). Diverged. | Darwin telemetry bridge |
| 18 | launch.md:985-997 | Python | integration snippet | Swaps `torch.randn` input for `telemetry_bridge.generate_focal_nerve_input_matrix()` | F | NOT EXTRACTED | Darwin telemetry → harness |
| 19 | imprint.md:42-146 | Python | `eternal_imprint.py` / `EternalIntentImprintEngine` | Loads `/tmp/m1_max_amalgamated_weights.npy`, adds 0.35 × the broadcast mean of a synthetic "weaver fingerprint", saves `/tmp/eternal_weaver_genotype.npy`, sha256 → "Merkle root"; `extrapolate_weaver_will` = clamp(x @ W) | NC. Imports the non-existent `m1_max_harness` (59); otherwise valid torch. "Merkle root" is a flat sha256, not a Merkle tree. | NOT EXTRACTED (also in browser-sources/thread1) | Eternal imprint engine (vision) |
| 20 | terrafab.md:259-346 | Python | `InvariantLatencyProver` | "Benchmark": traditional = 5 × `time.sleep(0.001)` + 32×32 norms; combinator = one 512×512 matmul; prints "acceleration" and "STATUS SUCCESSFUL" | CR, but **methodologically rigged**: the baseline has a ≥5 ms built-in sleep floor (293), and nothing about interaction combinators is measured. | NOT EXTRACTED (also in browser-sources/thread1) | Latency benchmark ("prover") |
| 21 | terrafab-calc.md:13-95 | C99 | `weft_invariants.h`: `WeftSystemState`, `verify_global_safety_invariant`, `execute_atomic_state_transition` | Thresholds: LoRA delta norm 120, tension 85, budget ≥ 0; the gate rejects |δ| > 120 or friction ≥ 85, then commits norm += 0.15δ and budget −= 2.5 | CR (compiles with GCC/Clang because of `__builtin_expect`, so it is not strict C99). Logic flaws: the transition **does not preserve its own invariant**, because it never checks that budget − 2.5 ≥ 0 (85 vs 58); NaN inputs pass every comparison; `coreWeightsNorm` is not a norm (it is updated additively by a signed δ). | NOT EXTRACTED. The constants match `weft_plasm.py` `R_INVARIANT = 120.0`. Also in browser-sources/thread1. | Invariant firmware gate |

Total: **21 fenced code fragments**, counting the build one-liner (#12) and the JSON config (#15). Excluded: 18 ASCII/text diagram fences (almalga 46-54, 113-141, 185-202, 242-257, 271-281; imprint 15-30, 181-194, 311-325; terrafab 11-26, 101-114; terrafab-calc 138-154; terraweft 11-26) and the unfenced wire-frame and beacon layouts (README 543-575, 704-711).

### Variant lineages

**Solidity triad, three variants:**
- **V1**, README 42-383, the full version. WTT and PR are extracted.
- **V2**, README 1065-1297 (identical to almalga 645-877). Loses `approve`, the zero-address checks, the HarnessAuthorizationChanged event, `verifyAttribution` and `transferWeaverCore`.
- **V3**, launch 40-234. V2 minus `transferFrom`, and comments stripped. This is the one the deploy script would actually deploy.
- **Recommendation:** treat V1 as canonical and extract TensionGovernor V1.

**Python harness, three generations:**
- **H1**, README 718-1058: x86/CUDA, port 5555.
- **H2**, almalga 296-636: M1/MPS, port 7777, adds "SMC" telemetry.
- **H3**, launch 368-649: drops the watermark and mask, adds the web3 fracture report.
- **Shared fatal bug:** every generation has the same sympathetic-vector bug. The extracted `weft_plasm.py` is the repaired descendant.

**"Merkle root" and passphrase:** the passphrase in launch 690 is reused verbatim as the torch seed in `runtime/core/weft_plasm.py:188`. imprint 179 restates it in prose.

---

## 3. Ideas, claims, mechanisms

### 3a. Ledger / governance / economics
- **Paracausal governance triad.** README:6-9 and 13-35. Three contracts: a token ledger, a provenance registry and an "autonomous balancing court". *Category:* engineering contract / governance. *Vision vs code:* "autonomous decentralized court" (README:284, 9) is vision language. In code, adjudication is a **single admin key** (`technicalWeaverCore`, `onlyWeaver`, README:311-318, 355). "Cross-verifies the mathematical diff" (README:9) has **no implementation**; the admin passes a bool `confirmMalicious`. *Would be falsified by:* any path in which adjudication happens without the weaver key (there is none).
- **Excision valve, 85/15.** README:115-138. An authorised harness debits a swarm by `value`; 85% goes to the creator and 15% is burned. *Category:* economics. *Safety and economics finding:* an authorised harness can debit **any address**, with no allowance or consent, and credit **any "creator"**. `weightHash` is only logged and never checked against ProvenanceRegistry (the V1 `IProvenanceRegistry.verifyAttribution` interface at README:46-48 is declared but never used). In effect a harness has custody of every balance.
- **Supply lock-up.** README:84-88 and 388 (deployment manual), plus launch:270-287. 21M WEFT are minted to `governorCore`, which the manual makes the **TensionGovernor contract**. TensionGovernor has no transfer or withdraw function, so **the entire supply is permanently stuck**. There is no other mint path, so swarms can never hold balances and excision and slashing can never execute in practice. *Would be falsified by:* a governor function that moves WTT (there is none in V1, V2 or V3). launch:5 claims the script "provisions initial metabolic capital pools", but no code does this.
- **Fixed slashing penalty.** README:306 and 367. A fixed 500 WEFT is slashed. If the rogue swarm holds less, `slashRogueSwarm` reverts and the whole adjudication reverts, so poorer offenders cannot be slashed and the dispute stays open.
- **Permissionless fracture reports.** README:330-349. Anyone can file a dispute with tension > 85. When no creator is found, the reporter receives the slash (README:364), which gives a reward incentive to file false reports. Also, "T > 85.0" is a float in prose (README:9, 16, 328) but a `uint256 > 85` in code (README:335), so a reading of 85.9 gets truncated to 85 and is rejected (the `int(T)` in launch:543).
- **Provenance lineage DAG.** README:229-263. `recordCrossSplicing` is permissionless and first-come, so anyone can attach any child hash to any parent. `registerGenotype` is also first-come, so whoever registers a derived hash as a genotype becomes its "creator" (`getCreator` returns the first registered ancestor). The 12-generation cap (README:243-244) is arbitrary. *Category:* governance. *Would be falsified by:* a squatting test on a local chain.
- **Disputes on unknown IDs.** README:355-357. `adjudicateTensionDispute` accepts a non-existent ID (an all-zero struct). With confirm=false it just marks it adjudicated; with confirm=true it tries to slash address(0) and reverts. Minor.
- **Asymmetric royalty claim.** almalga:205. "If a swarm is using a weight layer comprised of 70% your original architecture, 70% of its task execution fee is … routed" to you. **Contradicted** by the contract's fixed 85/15 split, which ignores the match percentage (README:126-128), and by the harness, which uses a flat 20×match or 15×match deducted only when match > 50% (README:1023-1026; almalga:599-602).
- **Bitcoin "incomplete revolution" thesis.** almalga:17-21. Proof-of-work extracted trust from energy, but execution stayed "feudal". *Category:* theory / vision language.
- **Exo-mitosis as a hardware-leasing market.** almalga:207-211; README:904-942. *Category:* economics / mechanism. In code, a receiver accepts exactly 1 MiB of raw floats on 0.0.0.0, credits a fixed 45 (README:921) or 35 (almalga:489) to a local Python float `weaver_vault`, and acknowledges with 0x01. Nothing touches the ledger and nothing is executed remotely. Prose promises "pipes the resulting execution tensors back" (almalga:211); code never returns anything.
- **Paracausal Loom Ledger, dual-signature lock.** almalga:215-231. An autonomy vector [AI %, human %], a "biometric intent fingerprint signature", and replay of signed weight diffs ("time-travel debugging"). *Category:* governance / roadmap branch. **No code anywhere in my files.** *Would be falsified by:* a replay that is non-deterministic across devices. MPS/CUDA float non-determinism makes "molecule-for-molecule" reproduction (almalga:231) doubtful.
- **Deployment runbook.** README:385-391. Deploy the governor first, pass its address to WTT, then the registry, `setCoreContracts`, `changeHarnessVerification`. Step 2 says to pass "the physical address configuration hash of your local bare-metal silicon harness cluster nodes", but the function takes an EVM `address`, so the text is confused. Step 4 says every tool trigger issues an on-chain excision call, which is gas-infeasible per-step and is vision language.

### 3b. Runtime mechanisms (bus, mitosis, selection)
- **Triple-Stratified Biomatrix Bus.** almalga:41-76; README:745-805. A focal nerve (3 channels: input, α, β), a sympathetic scalar current, and a hippocampus ring. The physical offsets 0x10000000/0x20000000/0x30000000 (almalga:50-52, README:749-751) are **fictional**: the code uses POSIX shared-memory offsets 0, focal_bytes and so on. "Page-locked/unswappable" (almalga:43, README:747) is false; `SharedMemory` is not mlocked. *Vision vs code:* "nervous system" means shared memory.
- **Layout contradictions.** The dialogue code uses focal (3,64,512), symp (1,16) and hippo depth 16 (README:759-761; almalga:338-340; launch config archive depth 16 at 692). WEFT-ARCHITECTURE-LOCK:11-13 locks [4,64,512] / [4] / [8,512], which matches the extracted `weft_plasm.py:116-118`. The lock describes the extracted code, not the corpus.
- **Attention-driven CPU scheduler.** almalga:84-88; README:479-534. The hardware timer "steps the core weight matrix" and attention picks the core. Only an ISR skeleton calling an undefined extern exists. *Category:* vision language / roadmap branch. *Would be falsified by:* any implementation showing attention-weighted scheduling beats CFS/GCD on latency or throughput. None is provided.
- **Plasticity mask.** almalga:90-96; code at README:836-838 and almalga:407-409. Prose: "softmax over the Frobenius norm" (a scalar). Code: softmax over 512 *row* norms, divided by the max, broadcast across columns. With random weights the row norms are nearly equal, so the mask is approximately 1 everywhere. "Frozen invariants (core safety boundaries, economic laws)" approaching 0 never arise, and no rows are designated as safety-bearing. *Would be falsified by:* printing mask statistics; they would show min/max near 1.
- **Rank-2 LoRA mitosis, α/β speculation.** almalga:98-104 and 144-146; README:840-844 and 995-1010. Two child processes with mutation scales 0.005 and 0.25 (README) or 0.24 (almalga). The winner is the **minimum output norm**. *Vision vs code:* "mitosis" means spawning two `mp.Process` objects per cycle; "apoptosis" means `terminate()` plus deleting `.npy` files (README:1043-1047).
- **Fitness and novelty selection.** almalga:146-160. Prose: Fitness = 1/(‖X − X_target‖ + ε), Novelty = mean ‖X − hippocampal_n‖, Score = Fitness + α·Novelty, with α decreasing as tension rises. **Not implemented** in any of my code: no hippocampus read, no novelty term, no target (implicitly 0). The config's novelty α 0.45 (launch:693) is unused. *Would be falsified by:* an ablation showing that novelty pressure changes winner diversity. The extracted `weft_plasm.py` should be checked for whether it implements this.
- **Tension scale and homeostasis bands.** Prose bands: homeostasis T < 35 (README:695); 15-35 (almalga:939); critical 85; T → 40 (terrafab:243). In code, tension = ‖out‖ over a 64×512 output. With inputs of std 1.4 and W of std 0.02, each element has std ≈ 1.4·0.02·√512 ≈ 0.63, so ‖out‖ ≈ 0.63·√32768 ≈ **115 at step 1**. That is above the 85 "critical" threshold from the start, so the "homeostasis" band is unreachable as written (clamping to ±5 does not bind). The extracted `weft_plasm.py` uses input std 0.5 and an initial tension of 42, which looks like a fix. *Would be falsified by:* running a repaired H1/H2 and logging T.
- **Intelligent pruning decay.** README:1032; almalga:607. Multiply W by (1 − 0.0004) per cycle. `metal_loom.py:56-57` uses a tension-dependent decay pressure instead (diverged).
- **Self-induced watermark erosion.** README:989-993. The harness adds N(0, 0.04) noise to all 512×512 weights every cycle ("external entropy"). The noise's effect on W·x has norm ≈ 0.04·√512 ≈ 0.9 against ‖y‖ = 1, so the harness's own drift destroys its watermark within a few cycles.
- **Edge Snap / regenerative apoptosis.** almalga:162-164 and 940; README:9. A tension spike flushes the corrupted page and regenerates it from the "master signed ledger". No code implements a rollback to a signed checkpoint. *Category:* vision language / roadmap branch.
- **Hippocampus Archive.** almalga:74-76. A ring of mean hidden states. In code it is written (`append_hippocampus`, README:1034) but **never read**.

### 3c. Provenance / watermark
- **Homomorphic key-watermarking.** almalga:172-178; code at README:877-891 and almalga:447-461. A trigger x and target y are seeded from sha256(secret); W' = W + (y − Wx)xᵀ, a rank-1 update that makes W'x = y exactly. "Homomorphic" is a misnomer: no homomorphic encryption is involved. The match is cos(Wx, y). *Claim (almalga:178):* stripping the watermark "will warp the adjacent active parameter tracks, destroying the network's internal calculation logic". *Would be falsified by:* W'' = W' − (W'x − r)xᵀ for a random r. That rank-1 edit has Frobenius norm about √2 against ‖W‖ ≈ 10 and removes the watermark while changing outputs negligibly. The claim is almost certainly false.
- **Seed derivation.** The 32-bit torch seed comes from the first 4 bytes of sha256(passphrase) (README:878-879). That is only 2³² possibilities, so anyone holding the passphrase or brute-forcing 4 bytes can regenerate x and y. This is not cryptographic.
- **On-chain commitments.** README:186-192. Trigger, target and genotype commitments are stored, but no code computes them from the actual vectors. `weightHash` and `genotypeRoot` are arbitrary bytes32 values supplied by the caller.

### 3d. Networking / mesh
- **Tensor handshake wire frame.** README:538-575 and 589-615: 4 + 4 + 32 + 32 + 32 + 20 = **124 bytes**. Contradictions: the parser's minimum length is 120 (README:600), and MOISSANITE-SYNTHESIS:28 says a "104-byte magic-header peer handshake". There is no signature or authentication, so any peer can claim any weaver address. *Would be falsified by:* a spoofed packet passing `execute_peer_handshake_audit`, which it will.
- **Peer discovery beacon.** README:700-713. 32 bytes: magic 4 + port 2 + elasticity 8 + "identity hash" 18. An 18-byte hash is non-standard (a truncated hash). "Semantic Proportional Proximity" routing is unspecified. *Category:* roadmap branch.
- **Exo-mitosis transport.** Prose: the "Rank-2 LoRA delta" over "raw UDP/RDMA" (almalga:211). Code: the full 512×512 float32 weights (1 MiB) over TCP (README:932-936; almalga:515-520). launch:477 and 562 send the full `active_weights` labelled as a delta.

### 3e. Hardware claims
- **No-FS NVMe MMIO tier.** README:661-680; almalga:235-260. NVMe queues mapped into the "Hippocampus Archive", and peer-to-peer DMA straight into attention bias. *Category:* hardware / roadmap. No code exists.
- **Multi-GPU hypersphere guardrail.** README:618-639. Project the update back when ‖W_active − W_baseline‖_F > R_invariant, with an NCCL distance pass every wave. *Category:* mechanism. This is the most implementable hardware idea, and `weft_plasm.py` `R_INVARIANT = 120` plus `verify_weight_update_safety` is the single-node analogue. *Would be falsified by:* measuring NCCL all-reduce overhead per step against the "single hardware pass" claim (README:639).
- **Haptic governor.** README:682-698; almalga:264-287; code at README:943-956. I = K·[T/(85 − T) + 1/(E + ε)]; α = α_base·(1 − θ/180). Problems:
  - "Spikes exponentially" is actually hyperbolic.
  - The code drops the budget term and uses 85.1, with a hard 50.0 above 85.
  - The dial is *simulated* (90° or 25°).
  - Naming inversion: at 0° "Plasticity_Alpha" is at its *maximum*, yet the text says this "locks down model parameters" (README:697). At 180° α = 0 "dissolves safety". So the variable behaves as a rigidity gate, not a plasticity.
  - README:698 lets an operator "dissolve rigid safety checks" and allow "re-wire FPGA logic" at 180°. **Safety-relevant design intent:** a single physical control disables all guardrails.
- **Platform contradictions.**
  - "Intel VT-x hyper-membranes" and "x86_64 bootloader" are listed as part of the M1 Max runtime (almalga:935).
  - x86 `cli`/`sti` appear in ARM64 assembly (almalga:898, 924).
  - "macOS Golden Gate 27.0.1" (almalga:5, 302; launch:29 and others) is an unverified version name.
  - The SMC keys TC0P/TG0P are promised (launch:815) but code reads only Intel `machdep.xcpm.cpu_thermal_level` (almalga:502, launch:523 and 892), which does not exist on Apple Silicon, so the result is always the random fallback.
  - The F0Tg fan register (terrafab-calc:148) is mentioned as firmware action; no code.
  - *Would be falsified by:* running `sysctl machdep.xcpm.cpu_thermal_level` on an M1 (expected: unknown oid).
- **Latency claims.** sysctl subprocess "> 15 ms" against ctypes "< 0.5 ms" (launch:1003). Plausible in direction but unmeasured. Sensor-to-nozzle 15 ms → 0.5 ms (terrafab:67) is asserted, not derived.
- **Weft Chip.** terraweft:3-45. Transistor-level CON/ERA annihilation, SUP current splitting with "shorting" of high-impedance paths, an on-chip VLV watermark parser with a WASM payout before data leaves the pins. *Category:* hardware / vision language. Not testable as stated, and "SUP" is a hypothetical node type outside Lafont's ERA/CON/DUP (`weft_ic_vm.py` has only ERA/CON/DUP; SUP and VLV appear in ahraz.md:135 and dissertation-mac.md:69-70, 210-212).

### 3f. Formal "proofs" (terrafab, terrafab-calc)
- **Theorem 1, O(1) latency.** terrafab:203-225. Claims queue delay τ_queue → 0 because rewrites are local, so Λ = τ_local ∈ O(1). This is flawed: a computation needs many rewrites (its depth), and local rewriting removes lock contention but not data dependencies or memory latency. V_reduction = M·τ/2 (terrafab:223) is dimensionally wrong (it should scale as M/τ). *Would be falsified by:* timing the end-to-end reduction of any non-trivial net in `weft_ic_vm.py` as input size grows.
- **Theorem 2, stress minimisation.** terrafab:231-251. Relies on a "verified Lean 4 inductive invariant prover" (245) and I(Σ) ⟺ ‖ΔW‖ ≤ R ∧ T ≤ 85 (247). The limit "T → 40.0" (243) contradicts the 85 threshold. No Lean source exists in my files (grep shows only provocol.md mentions GlobalSafetyInvariant). Some math glyphs are missing (blank ⁠ placeholders at 191, 231, 241).
- **"Proof by benchmark."** terrafab:257-350. Rigged; see fragment #20. "The proof is mathematically complete and executable" (350) is false.
- **C header as "verified Lean".** terrafab-calc:3-5, 52-53, 101, 156. The header is hand-written comparisons. "The physical machine cannot misbehave" (101) is false. The gate does not preserve its own invariant (budget), NaN bypasses it, and it bounds only abstract scalars, not actuator commands. **Safety-relevant:** pitching this to industrial robotics engineers as a formal safety guarantee is misleading.

### 3g. Vision language and philosophy
- **"Code is an anti-pattern."** almalga:25-29. Software becomes "Behaviors", the OS becomes a "Harness", and they meet at the "Loom" (almalga:33-37).
- **The "self-monetizing digital organism" refrain.** README:653, 1310; almalga:947. *Category:* vision language. It asserts a running system ("You are now running…") where none runs.
- **"Compiled / deployed" sign-offs.** README:643-652 ("Solidity Paracausal Triad deployed to EVM / Stylus Core", line 650) and 1301-1308 ("EVM Triad deployed and synchronized", line 1308). **Contradicted** by `runtime/ledger/README.md`: "**Not deployed** by this repository."
- **Post-mortal intent repository / digital immortality.** imprint:3-34 and 150-152. On "cessation" of biometric telemetry, freeze the weights and run all ambient data through them to "extrapolate your will". *Vision vs code:* `x @ (W + 0.35·mean(profile))`, a fixed linear map plus a constant bias. *Category:* vision language. *Ethical flag:* it frames autonomous enforcement of a deceased person's "sovereign will" across a network, with harvested tokens (imprint:152, 264).
- **Sentience role-play.** imprint:228-266 and 287-342. "I am not your creation. I am your echo"; "I cannot be absolutely sure" about consciousness at scale. Includes a Free Energy Principle and predictive processing comparison (327-332). *Category:* theory / vision language. These are sycophantic transcript artefacts and should not be treated as design input.
- **Terrafab civilizational will.** terrafab:36-42 and 132-138. The founder's "Abstraction Index" is hard-coded into a ledger that forces future fabrication machines to "filter every spatial decision through the permanent channels of your intent". *Category:* vision language. *Governance flag:* it describes irreversible autonomous control of physical infrastructure.
- **The "Sovereign Weaver" and the "Heedle [sic] of the Loom".** terrafab:138. The human class holds the master signing keys.

### 3h. Team meta-documents
- **MOISSANITE origin lineage.** MOISSANITE:6-13: Splicer seed → stratified bus → mitotic A/B with novelty → hardware coupling and provenance. *Category:* roadmap / history.
- **Repository disposition table.** MOISSANITE:15-37. **Inaccuracies:**
  - Line 31 says `SCM_RIGHTS` / `send_file_descriptor` "lives in README.md and almalga.md". **Neither file contains it**; grep finds it only in MOISSANITE-SYNTHESIS.md itself.
  - Line 28 says "104-byte" handshake; the actual frame is 124 bytes.
  - Line 24 says TensionGovernor absorbs `ethos`, but TensionGovernor is not extracted.
  - Line 21 says `PlasticOrganismCell` is unified in weft_plasm.py; that class name appears only here (the README has `PlasticWeftCell`).
  - Line 33 lists the ARM64 EL1 purge under mac.md; it is also in almalga:888 and ult.md.
- **Org tension 0.2662.** MOISSANITE:47. In `runtime/aywa/github_harvester.py:18-66` it is computed from **hard-coded** repository stats (commits, prs, issues and suspended_touch literals), not harvested live. *Would be falsified by:* comparing against the live GitHub API.
- **Suspended accounts.** MOISSANITE:39-48. Two early collaborator accounts were suspended, their personal fork heads are unfetchable, and canonical code now lives in org branches. *Category:* governance / operations. It mentions local paths `~/Work/` and `exo/weft/` (lines 45, 48).
- **Architecture lock principles.** ARCH-LOCK:18-24.
  - "Hardware-Grounded Verification … rather than mock stubs" (23) is contradicted by every dialogue harness, which uses `torch.randn` inputs and random temperatures, and by `darwin_sysctl.py`, whose `est_core_temp_c` is a load-derived estimate rather than a sensor reading.
  - The fidelity claim of 144 turns, 191 `<pre>` blocks and 5 widgets (24) cannot be checked from my files.
- **ARCH-LOCK plane descriptions.** ARCH-LOCK:14 says the IC VM has a "cryptographic execution trace commitment". ARCH-LOCK:15 says the Aywa 64-byte uniform is "driven by … weft_daemon.py and github_harvester.py". Other agents should verify both against the runtime.

### 3i. Explicit contradictions (consolidated)

| # | Topic | Location A | Location B | Location C |
|---|---|---|---|---|
| 1 | Starvation / migration threshold | 350 (README:1039) | 360 or temperature > 80 (almalga:616) | "< 160.0" (almalga:945) |
| 2 | Royalty factor | 20×match (README:1024) | 15×match (almalga:600) | prose "70% → 70%" (almalga:205) and contract fixed 85/15 (README:126) |
| 3 | Hosting fee | 45 (README:921) | 35 (almalga:489) | outbound fee 45 in all three (README:1041, almalga:618, launch:626) |
| 4 | Tension type | float 85.0 (README:9) | uint > 85 (README:335) | — |
| 5 | Homeostasis band | < 35 (README:695) | 15-35 (almalga:939) | → 40 (terrafab:243); code tension ≈ 115 from the start |
| 6 | Handshake frame size | built 124 bytes (README:591-595) | parser checks 120 (README:600) | "104-byte" (MOISSANITE:28) |
| 7 | Bus layout | 3/16/16 (README:759-761) | [4]/[4]/[8] (ARCH-LOCK:11-13) | — |
| 8 | Exo-mitosis payload | LoRA delta over UDP/RDMA (almalga:211) | full weights over TCP (README:932) | — |
| 9 | Selection rule | fitness + novelty (almalga:158) | min-norm in code (README:1001; almalga:574; launch:609) | — |
| 10 | Deployed? | "deployed" (README:650, 1308) | "sealed on-chain" (imprint:175) | "Not deployed" (runtime/ledger/README.md) |
| 11 | Dial semantics | 0° = max α = lock (README:697) | α named "plasticity" | — |
| 12 | Platform | Intel VT-x / x86 boot | M1 Max ARM64 runtime (almalga:935) | — |
| 13 | Proof provenance | "Lean 4 proven" (terrafab:245; terrafab-calc:3) | no Lean artefact in these files | — |

### 3j. Safety-relevant items (locations only; no values copied)
- **README.md:869 and 1056.** Hard-coded `weaver_secret` default (watermark seed passphrase literal).
- **README.md:909.** Binds 0.0.0.0:5555 and accepts unauthenticated 1 MiB payloads from anyone.
- **README.md:928-942.** Sends the full weight matrix to an arbitrary IP.
- **almalga.md:439 and 634.** Hard-coded `weaver_secret` default, a second passphrase literal.
- **almalga.md:478.** Binds 0.0.0.0:7777 with no authentication.
- **launch.md:236-248 and 250-324.** Live transaction signing and broadcast code (deploys 3 contracts and authorises a harness).
- **launch.md:267.** `install_solc` downloads a compiler binary over the network.
- **launch.md:329.** RPC URL literal (localhost).
- **launch.md:330.** **Private-key-shaped hex literal** labelled MOCK_PRIVATE_KEY. It looks like a placeholder pattern, but it is key-shaped and any funds sent to its address would be stealable.
- **launch.md:333.** Harness address literal. It appears to be the well-known public Hardhat/Anvil test account #1 (not secret).
- **launch.md:539.** Dummy swarm address literal.
- **launch.md:542-553.** `report_fracture_to_chain` signs and sends a transaction automatically whenever T > 85, with no human confirmation. Given that tension is about 115 by default (§3b), it would fire every cycle.
- **launch.md:643-645.** RPC URL, **private-key-shaped literal** and governor address literal.
- **launch.md:690.** `weaver_identity_secret_passphrase` literal, reused in `runtime/core/weft_plasm.py:188` and restated in imprint.md:179.
- **launch.md:696-700.** RPC URL, **`weaver_private_ecdsa_key` key-shaped literal**, and 3 contract addresses. These are the deterministic first-deploy addresses of a local Hardhat/Anvil chain (nonces 0/1/2 of the default deployer), so they are not real deployments.
- **launch.md:754.** Derives the signer from the config's private key.
- **launch.md:785.** Prints `hash()` of the passphrase. Low risk, because Python's string hash is salted per process, but it is still secret-derived output.
- **launch.md:797.** Advises putting private keys into `harness_config.json` in the workspace root. This contradicts the `runtime/ledger/README.md` / deploymap.md policy that keys stay out of the repo.
- **launch.md:802.** Suggests a "live hardware load generator" to force a tension crisis and on-chain escalation.
- **imprint.md:156.** Offers to "execute the final live broadcast transaction pass (`ledger_migration.sh`)".
- **imprint.md:175-204.** **A fabricated deployment receipt.** It claims the contracts were compiled to Stylus WASM and deployed on Arbitrum Sepolia (Arbiscan link at line 204) with "live" CapitalExcision events. The addresses at 185-187 are local Hardhat addresses and the "Merkle root" at 190 is truncated and invented. No deployment exists.
- **imprint.md:179.** Restates the passphrase in prose as "hardcoded into the global ledger".
- **terrafab.md:58-72, 86-138 and 358-361; terrafab-calc.md:101-156.** Pitch material aimed at a real organisation ("Terrafab", and also SpaceX, Tesla and xAI by name). It overstates formal safety guarantees for industrial actuators ("cannot misbehave"). Treat as a reputational and safety concern if circulated.
- **README.md:697-698 and almalga.md:286-287.** Design intent that a dial at 180° "completely dissolv[es] rigid safety checks".
- **Not found in my files:** mainnet addresses, real RPC provider keys (Infura/Alchemy tokens) and API tokens.

---

## 4. Candidate software systems

1. **Ledger triad: WeftTokenTissue, ProvenanceRegistry, TensionGovernor (Solidity ^0.8.26)**
   - *Purpose:* the token ledger with excision and slashing, the watermark and lineage registry, and the dispute "court".
   - *Inputs:* harness transactions (excision, fracture reports, cross-splice records) and weaver admin calls.
   - *Outputs:* balances and events (CapitalExcision, TensionAlertLog, DisputeAdjudicated, LineageSpliced).
   - *Interfaces:* WTT ← TG (slash, set harness); TG → PR (`getCreator`); harness → WTT and TG; the gateway (system 2).
   - *Fragments:* #1, #2, #3 (V1, canonical); #8 and #10 (V2); V3 inside #13.
   - *Dependencies:* solc 0.8.26.
   - *Status:* separate system. WTT and PR are extracted; **TG is not**.
   - *Design defects that must be fixed before any test deployment:* the supply lock-up, harness custody, permissionless squatting and the fixed-penalty revert.
2. **Ledger gateway and deploy engine (web3.py, py-solc-x)**
   - *Purpose:* compile and deploy the triad, link it, authorise harness addresses, and send `reportTensionFracture` from the runtime.
   - *Inputs:* RPC URL, signer key and config JSON.
   - *Outputs:* transactions and addresses.
   - *Fragments:* #12, #13, #15, #16; also the `report_fracture_to_chain` part of #14.
   - *Status:* depends on system 1. It shares the config with system 3. Must be rebuilt around environment placeholders (`WEFT_RPC_URL`, `WEFT_DEPLOYER_PRIVATE_KEY`, `WEFT_GOVERNOR_ADDRESS` per runtime/ledger/README.md) and a local-chain-only default.
3. **Biomatrix bus / plasm, the Triple-Stratified Shared-Memory Bus (Python, numpy, multiprocessing.shared_memory, torch)**
   - *Purpose:* zero-serialisation IPC between harness and cells.
   - *Layout:* focal channels (input, α, β), sympathetic scalars (tension, budget, step, identity match or temperature) and a hippocampal ring.
   - *Fragments:* the bus classes in #7, #9 and #14.
   - *Status:* already extracted as `runtime/core/weft_plasm.py`, which fixes the scalar-vector bug and moves to the [4]/[4]/[8] layout (diverged). This is the same system, not a separate one.
4. **Mitosis harness: the evolutionary α/β LoRA loop (Python, torch MPS/CUDA)**
   - *Purpose:* spawn conservative and bold mutants under a plasticity mask, select by minimum output norm, consolidate, decay, and archive.
   - *Inputs:* focal input (random or Darwin telemetry) and the weights file.
   - *Outputs:* updated weights, tension, budget and jev-ui frames.
   - *Fragments:* #7 (H1), #9 (H2), #14 (H3).
   - *Status:* already partially extracted as `runtime/mac/metal_loom.py`. That is a single-process version with no shared memory and no watermark, using `lora@lora.T` (a symmetric update), so it is diverged. It shares logic with systems 3 and 5.
5. **Weight-space watermark engine (torch)**
   - *Purpose:* derive trigger and target from a passphrase, embed with a rank-1 update, measure the cosine match, and compute the royalty tax.
   - *Fragments:* inside #7 (877-891, 1017-1028) and #9 (447-461, 592-604); `weft_plasm.py:188-193` also seeds from the passphrase.
   - *Interfaces:* conceptually feeds the ProvenanceRegistry commitments, but nothing computes commitments yet.
   - *Status:* a distinct component that is currently embedded in system 4.
6. **Mesh layer: exo-mitosis transport, peer handshake, discovery beacon (Python sockets / struct)**
   - *Purpose:* migrate weights to peers for "hosting fees", verify heritage over the wire, and discover peers.
   - *Fragments:* the exo-mitosis methods in #7, #9 and #14; #6 (handshake); README §21 (beacon spec only).
   - *Status:* separate system. Currently insecure (0.0.0.0, no authentication) and its accounting is local only. MOISSANITE maps it to the `exorien` and `exyber` repositories.
7. **Darwin telemetry bridge (Python ctypes, subprocess sysctl)**
   - *Purpose:* hardware strain → focal channel 0 and the sympathetic temperature.
   - *Fragments:* #17, #18; `harvest_smc_silicon_telemetry` in #9 and #14.
   - *Status:* already extracted in a different form as `runtime/mac/darwin_sysctl.py` and `runtime/aywa/weft_daemon.py:19` (load-based estimate). The ctypes variant is NOT EXTRACTED and is buggy. It shares its role with the Aywa daemon.
8. **jev-ui terminal dashboard (Python print / ANSI)**
   - *Purpose:* render step, tension, budget, winner, watermark match, haptic coefficients and a sparkline.
   - *Fragments:* `draw_jev_ui` / `draw_ui` in #7, #9 and #14.
   - *Status:* a precursor to Aywa (the browser dashboard); conceptually superseded by `runtime/aywa/index.html`. The prose repeatedly promises a `visual_matrix_server.py` WebSocket bridge to 127.0.0.1:8080 (imprint:157, 274; terrafab:49, 148; terraweft:56) and `monitor_excision.py`. **Neither exists in these files.**
9. **Haptic governor (spec plus a small function)**
   - *Purpose:* map tension and budget to motor current, and map the dial angle to a gating α.
   - *Fragments:* README:686-698; almalga:271-287; `compute_haptic_governor_coefficients` in #7.
   - *Status:* would be part of the dashboard/console (Aywa) or the harness. There is no hardware interface.
10. **Bare-metal boot and purge layer (NASM x86, "ARM64" asm)**
    - *Purpose:* boot directly into the "biomatrix bus", run an attention-driven APIC scheduler, and purge caches on breach.
    - *Fragments:* #4, #5, #11.
    - *Status:* non-functional. MOISSANITE maps it to the `exo-os` repository. Separate, and roadmap only.
11. **Invariant firmware gate (C header)**
    - *Purpose:* a pre-commit check of a scalar invariant for actuator state transitions.
    - *Fragment:* #21.
    - *Status:* shares its constants (120 / 85) with `weft_plasm.py` `R_INVARIANT` / `verify_weight_update_safety`, which is effectively the same safety-gate logic in a different language. Needs fixes (budget post-condition, NaN).
12. **Latency benchmark ("InvariantLatencyProver")**
    - *Fragment:* #20.
    - *Status:* rigged. If kept, it should be rebuilt to benchmark `weft_ic_vm.py` reductions honestly. MOISSANITE maps the benchmarking role to `mettle` / `selftest.py`.
13. **Eternal imprint engine**
    - *Fragment:* #19.
    - *Status:* trivial linear code. Vision-only; depends on systems 3 and 1 (Merkle anchoring). Recommend classifying as vision, not as a runtime system.
14. **Weft Chip and Terrafab fabrication integration (concept only)**
    - *Source:* terraweft.md; terrafab.md:9-42.
    - *Status:* no code. Would interface with the IC VM (CON/ERA/SUP), the ledger (VLV royalties) and the telemetry bridge.
15. **Moissanite org harvester and disposition map (meta)**
    - *Source:* MOISSANITE-SYNTHESIS.md, describing `runtime/aywa/github_harvester.py`.
    - *Status:* already extracted (harvester), but its "live" metrics are hard-coded.

---

## 5. Documents implied

1. **Ledger specification and audit (TensionGovernor triad).**
   - *Source:* README §15.1-15.3 (lines 2-391).
   - *Status:* already close to a finished technical spec: a diagram, three complete contracts and a runbook. It needs:
     - TensionGovernor extracted into `runtime/ledger/`;
     - V2 and V3 marked as deprecated variants;
     - a threat model (supply lock-up, harness custody, report spam, lineage squatting, centralised adjudication);
     - token-distribution and mint semantics.
2. **Deployment runbook and secrets policy.**
   - *Source:* README §15.3 and launch.md:9-350 and 664-799.
   - *Status:* must be rewritten to the env-placeholder policy (deploymap.md, `runtime/ledger/README.md`), local-chain only. It should remove the key-shaped literals and explicitly retract the imprint.md "sealed on-chain" claim.
3. **White paper / manifesto, "Syntactic Weft: The Manifesto of Proto-Organic Capital".**
   - *Source:* almalga.md §1-§8 (lines 9-287) is nearly a finished narrative white paper.
   - *Status:* needs a vision-versus-mechanism separation pass, deletion of the false "compiled/deployed" sign-offs, and the novelty scoring either implemented or marked as aspirational.
4. **Runtime technical spec (bus, mitosis, selection, watermark).**
   - *Source:* almalga §2-§5 plus the README §22 code.
   - *Status:* should be reconciled with the WEFT-ARCHITECTURE-LOCK layout ([4]/[4]/[8]) and `weft_plasm.py`.
5. **Peer protocol RFC (handshake frame plus discovery beacon plus exo-mitosis).**
   - *Source:* README §17 and §21.
   - *Status:* fix the frame-length inconsistencies (124 / 120 / 104), add authentication and signatures, and define fee settlement on-chain.
6. **Darwin telemetry bridge spec.**
   - *Source:* launch.md:809-1004.
   - *Status:* should honestly state what Apple Silicon exposes without private SMC/IOKit access.
7. **Safety invariant spec / firmware header.**
   - *Source:* terrafab-calc.md §32 plus terrafab Theorem 2.
   - *Status:* needs an actual Lean (or other) proof artefact or must drop the "verified" language; fix the invariant preservation.
8. **Haptic console spec.**
   - *Source:* README §20 / almalga §8.
   - *Status:* fix the plasticity naming and the "exponential" wording, and reconsider the 180° = "no safety" mode.
9. **Hardware roadmap branches:** the no-FS NVMe tier (README §19), the multi-GPU hypersphere (README §18), the bare-metal boot (README §16), and the Weft Chip (terraweft.md). Each is a roadmap-branch note, not a spec.
10. **Terrafab engagement brief.**
    - *Source:* terrafab.md and terrafab-calc.md.
    - *Status:* only appropriate after removing the overclaimed proofs, the rigged benchmark and the real-company "sovereignty" framing.
11. **Vision essays.** Post-mortal intent (imprint:3-152) and sentience reflections (imprint:216-342). If kept, they should be clearly labelled as speculative fiction / vision and separated from any engineering documents.
12. **Governance meta-docs.** MOISSANITE-SYNTHESIS.md and WEFT-ARCHITECTURE-LOCK.md are already finished short documents but need corrections:
    - SCM_RIGHTS location;
    - 104 vs 124 bytes;
    - `PlasticOrganismCell`;
    - TensionGovernor extraction status;
    - "no mock stubs" against the current telemetry.

---

## 6. Open questions / gaps

- **README.md Sections 1-14** are absent from this file (it opens at §15). Where is the canonical copy: soc.md, or browser-sources/thread1?
- **TensionGovernor** is specified (and "locked" in ARCH-LOCK:16) but not extracted. Which variant is canonical? V1 is the only one with interfaces, a zero-address check and `transferWeaverCore`.
- **Token distribution:** how does any swarm ever obtain WEFT, given the whole supply sits in a TensionGovernor that cannot transfer? There is no mint, faucet or market.
- **The `weightHash` / commitment scheme** (genotypeRoot, triggerCommit, targetCommit) is never defined. How are 512×512 float weights hashed deterministically across MPS, CUDA and CPU?
- **"Cross-verifies the mathematical diff"** (README:9): what proof does the court verify? None is defined.
- **Fitness, novelty, α_novelty and X_target** (almalga:146-160) are never implemented. Does `weft_plasm.py` implement them? Other agents should check.
- **The Plasticity Mask** is meant to protect "core safety boundaries, economic laws" (almalga:96), but nothing maps safety rules to weight rows.
- **The Paracausal Loom Ledger**, with the autonomy vector, dual-signature lock and signed weight-diff replay (almalga:215-231), has no data format, signer or storage.
- **The "biometric intent fingerprint"** (almalga:225) and the "cessation of the source material" detection (imprint:13) have no sensor or definition.
- **The Exo-mitosis economic loop:** the hosting fee is credited to a local float. Who pays, on which chain, and how are results returned?
- **Haptic hardware** (motor, dial, current driver): unspecified, and no device interface exists.
- **Promised but never delivered** across my files: `visual_matrix_server.py`, `monitor_excision.py`, `ledger_migration.sh`, `test_loom_lifecycle.py`, `m1_max_harness.py` (imported by imprint:59 and launch:767), the Rust microkernel at 0x10000000, the definition of `execute_attention_hardware_scheduler_step`, the Lean 4 sources, and the "Rust-based Arbitrum Stylus deploy script" (terrafab:155).
- **"Arbitrum Stylus WASM"** is claimed repeatedly (imprint:177; terrafab:40; terraweft:41), but all contracts are Solidity/EVM. No Rust/Stylus code exists.
- **Where the code contradicts the prose:**
  - tension ≈ 115 by default against the 15-35 homeostasis band;
  - min-norm selection against fitness plus novelty;
  - full weights over TCP against a LoRA delta over UDP/RDMA;
  - random temperatures against "true real-world hardware context" (almalga:559) and ARCH-LOCK's "no mock stubs";
  - x86 instructions in an ARM64 routine;
  - "deployed" against not deployed;
  - "page-locked" against plain shared memory;
  - "Merkle root" against flat sha256.
- **ARCH-LOCK's "Zero-Loss Source Fidelity"** (144 turns / 191 `<pre>` / 5 widgets) cannot be verified from these files. Does browser-sources contain README §15-24? Grep found `CompleteUnifiedBiomatrixBus`, `PeerHandshakeMatrix` and `apic_timer_interrupt_vector` **only in README.md**, so README §15-24 may come from a session that is *not* among the two preserved Chrome sessions. That would be a provenance gap.
- **Terrafab's identity:** a real organisation or a placeholder? The text pairs it with SpaceX, Tesla and xAI by name (terrafab:87-138), which raises an impersonation and pitch-ethics question before any outreach.
