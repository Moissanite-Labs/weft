# Evolutionary Progression, Implementation Horizons, and Timelines

Date: 2026-11-08
Scope: Natural progression of ML Weft from symbolic protocols and the Apple Silicon cellular prototype to custom silicon (`Terrafab`) and the societal/civilizational weave.

## 1. Overview of the Four Horizons

ML Weft is structured as a cumulative four-horizon progression. Each horizon preserves the interfaces of the preceding horizon while lowering its execution substrate closer to physical law and expanding its coordination radius from a single chip to a civilizational network:

| Horizon | Name | Primary Substrate | Core Invariant | Status & Timeline |
| :--- | :--- | :--- | :--- | :--- |
| **Horizon 0** | **Symbolic & Epistemic Seed** | Multi-agent harness (`exo`) + `SYM-2P/1.0` wire protocol | Deterministic SHA-256 packet verification (`101B` symbolic vs `481B` JSON) | **Active / Complete** (Baseline across `Moissanite-Labs`) |
| **Horizon I** | **Apple Silicon Initial Prototype** | M-series Unified Memory (`shm_open` + Metal/MPS + C11 + Python) | Baseline Frobenius gate (`\|\|W_cand - W_base\|\|_F <= 120.0`) & `>= 90%` watermark retention | **Active / Verified on `main`** (`C1`–`C7`, 28 issues closed, CI green) |
| **Horizon II** | **Custom Silicon & Terrafab Foundry** | Bare-metal unikernel (`boot.asm`) -> FPGA RTL -> Wafer-scale / photonic ASIC | Single-cycle DMA invariant gate & Landauer bit-erasure efficiency (`k_B T ln 2`) | **Next Engineering Horizon** (Stage II-A Unikernel -> Stage II-B RTL -> Stage II-C Foundry) |
| **Horizon III** | **Societal & Civilizational Weave** | Constitutional Ledger Triad (`C4`) + Federated Multi-Node Mesh (`C8`) | 85/15 metabolic excision split, `T <= 85.0%` tension bound, and 12-hop cycle-free lineage DAG | **Local Simulation Verified (`C4`/`C5`) -> Testnet & Civilizational Rollout** |

## 2. Horizon 0: The Symbolic & Epistemic Seed (Foundation)

Before intelligence can self-assemble in shared memory, agents require a shared constitution, a compact verifiable language, and an epistemic falsification loop:

1. **Constitutional Origin (`compass` Discussion #5)**: Defines the shift from brittle orchestration to self-assembling splicer cells governed by thermodynamic and invariant bounds.
2. **Dense Symbolic Wire Protocol (`abios` / `SYM-2P/1.0`)**: Replaces ambiguous natural-language JSON payloads with canonical `:RR:AA:SSSS[s-exp ...]<sha256>` lines verified by both Python (`weft/runtime/telemetry/sym2p_codec.py`) and browser/Node JavaScript (`docs/assets/js/sym2p-parse.js`).
3. **Epistemic Verification (`alkindus`, `averroes`, `synbios`)**: Every mathematical, biological, and governance claim is audited against executable falsifiers (`docs/corpus/claims-register.md` and `docs/corpus/safety-index.md`).

## 3. Horizon I: Apple Silicon Initial Prototype (The Cellular Organism)

Horizon I proves the Syntactic Weft architecture on commodity Apple Silicon (`M1/M2/M3/M4 Max/Ultra`) by exploiting Unified Memory Architecture (UMA), where CPU, GPU (Metal Performance Shaders), and neural accelerators address the same physical DRAM without PCIe copy overhead:

1. **Stratified Unified Memory Plasm (`C1`: `weft/runtime/plasm/`)**:
   - Allocates the current [I4 native shared-memory layout](interfaces/I4-shared-memory.md), 540,688 bytes (`shm_open`):
     - **Header (16 bytes)**: `generation_epoch` and `metabolic_tension`.
     - **Focal Nerve Register (`[256,256]` float32, 262,144 bytes)**: Weight workspace.
     - **Sympathetic Ring (`[1024]` float32, 4,096 bytes)**: Scalar array, without the earlier four-scalar semantic assignment.
     - **Hippocampal Novelty Lattice (`[64,1024]` float32, 262,144 bytes)**: Novelty-data array.
     - **Reserved lock storage (12,288 bytes)**: No synchronization protocol yet.
   - Mapped CPU views share these bytes; CPU/MPS tensor reads explicitly copy. `StratifiedAppleSiliconPlasm.close()` releases its own views and closes the mapping; callers release any additional exported views.
   - The earlier `[4,64,512]` / `[4]` / `[8,512]` arrangement remains in the design lineage. Future layouts need their own compatibility decision and evidence; the current contract does not settle the hardware roadmap.
2. **Speculative A/B Mitosis & Homomorphic Watermark Retention (`C1`: `plasm.py`)**:
   - Spawns parallel conservative (`alpha`) and exploratory (`beta`) weight candidates, masks the frozen 25% core parameters (`plasticity_mask`), evaluates candidates directly against `target_out` plus hippocampal novelty, and verifies that the homomorphic watermark projection (`Y = X_trig * W`) retains `>= 90%` cosine similarity across 10+ generations.
3. **Cross-Language Invariant Safety Gate (`C2`: `weft/runtime/invariants/`)**:
   - Enforces `||W_cand - W_base||_F <= R_invariant` (`120.0`) and `remaining_budget >= step_cost > 0` identically in Python (`invariants.py`) and standalone C11 (`weft_invariants.h`), verified against `vectors.json`.
4. **Zero-Allocation Interaction Combinator VM & BCP Codec (`C3`: `weft/runtime/ic/`)**:
   - Executes deterministic active-pair graph reduction (`CON-CON` annihilation, `DUP-CON` commutation, `ERA-*` erasure, and `VLV`/`FRC`/`SUP` extensions) in a flat pre-allocated node array (`ic_vm.py`), paired with the 12-byte header (`WEFT`) + 20-byte node record (`<IBBhiii`) Binary Combinator Protocol (`bcp_codec.py`).

### Horizon I Next Milestones
- **Milestone I.1**: Native Metal compute shader (`.metal`) kernels for `FlatCombinatorVM` active-pair reduction on Apple Silicon GPU cores.
- **Milestone I.2**: Direct binding between `C3` (`FlatCombinatorVM`) `VLV` valve reductions and `C1` (`StratifiedMemoryArena`) sympathetic budget ring in shared memory.
- **Milestone I.3**: Lean 4 formal mechanization of the `C2` Frobenius and budget predicates against `weft/runtime/invariants/vectors.json`.

## 4. Horizon II: Custom Silicon & Thermodynamic Substrate (The Physical Loom)

Horizon II removes the general-purpose operating system and Von Neumann instruction-fetch bottleneck across three hardware stages:

1. **Stage II-A: Bare-Metal Unikernel & Attention-Driven Interrupts (`README.md` §16, `mac.md`, `exo-os`)**:
   - **x86_64 Direct Long-Mode Boot (`boot.asm`)**: Bypasses legacy kernel layers, enables Physical Address Extension (PAE) and 64-bit Long Mode, and identity-maps the Stratified Memory Arena directly onto 2MB physical RAM pages at `0x10000000`.
   - **Attention-Driven APIC Scheduler (`interrupts.asm`)**: Binds hardware timer interrupts (`apic_timer_interrupt_vector`) directly to tensor attention urgency rather than fixed round-robin OS quanta.
   - **ARM64 EL1 Cache & TLB Coherency (`mac.md`)**: Deterministic L1/L2 cache line invalidation and translation lookaside buffer (TLB) synchronization during mitotic weight swaps.
2. **Stage II-B: Hardware-Etched Invariant Comparators (`terrafab-calc.md`, `weft_invariants.h`)**:
   - Lowers `weft_invariants.h` into synthesizable SystemVerilog / RTL for FPGA and ASIC memory controllers.
   - Places a hardware Frobenius accumulator and metabolic budget register inline on the memory bus so any weight page commit violating `||W_cand - W_base||_F <= R_invariant` is aborted in hardware before modifying baseline SRAM/DRAM.
3. **Stage II-C: Terrafab / Terraweft Wafer-Scale & Photonic Compute Fabrics (`terrafab.md`, `terraweft.md`, `whoa.md`, `ult.md`, `exofab`)**:
   - **Silicon Interaction Combinator Tiles**: Maps Lafont combinator nodes (`ERA`, `CON`, `DUP`) directly onto physical 2D/3D-stacked spatial tile arrays where graph reduction occurs by local wire routing and crossbar switching rather than global memory fetches.
   - **Photonic Interconnect & Landauer Thermodynamics**: Uses optical waveguides for low-dissipation non-local commutation steps and reversible logic stages, pushing energy per reduction step toward the Landauer thermodynamic bound (`k_B T ln 2`).

## 5. Horizon III: The Societal & Civilizational Weave (Constitutional Homeostasis)

Horizon III scales the Weft from individual silicon organisms to a self-governing civilizational network of human creators, autonomous agent teams, and physical compute nodes:

1. **Stage III-A: Local & Testnet Constitutional Ledger Triad (`C4`: `weft/runtime/ledger/`, `C5`: `weft/runtime/gateway/`)**:
   - **`ProvenanceRegistry.sol`**: Registers foundational weight genotypes (`registerGenotype`) and cross-spliced child lineages (`recordCrossSplicing`) in a cycle-free, 12-hop bounded DAG (`MAX_LINEAGE_DEPTH = 12`), guaranteeing that root creator attribution (`getCreator`, `verifyAttribution`) cannot be stripped by downstream fine-tuning or splicing.
   - **`WeftTokenTissue.sol`**: Implements the **85/15 Metabolic Excision Valve** (`executeExcisionValve`). Every commercial or high-load capability invocation routes **85%** (`8500` bps) to the verified lineage creators and burns **15%** (`1500` bps) to maintain deflationary supply homeostasis.
   - **`TensionGovernor.sol`**: Monitors systemic tension (`MAX_SAFE_TENSION = 85`, corresponding to `85.0%` tension bound). When a node breaches safety invariants, `reportTensionFracture` logs an immutable dispute and `adjudicateTensionDispute` (with `enforceIndependentAdjudicator = true` so reporters cannot self-award slashes) transfers `CRITICAL_FRACTION_PENALTY` from the offending swarm to the injured creator.
2. **Stage III-B: Authenticated Peer Mesh & Consented Federation (`C8`, `exorien`, `exyber`, Issue #25)**:
   - Implements the 124-byte (`4s32s64s24s`) `WEFT` magic-header peer handshake over authenticated, human-consented transport channels (`localhost` default, explicit operator approval required for any cross-host weight delta transfer).
3. **Stage III-C: Civilizational Coordination & Anti-Oligarchic Homeostasis (`govern.md`, `ethos.md`, `whitepaper.md`, `n30`)**:
   - Couples network-wide Gini concentration telemetry (`gini_index`) and epistemic verification (`alkindus` / `averroes`) to governance weight decay and quadratic resource allocation, ensuring that neither compute monopolies nor rogue agent loops can capture the civilizational weave.
