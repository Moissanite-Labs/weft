/**
 * ML Weft Architectural Atlas & Interactive Simulator Data (Codebase C7 — w3ft.org)
 * =================================================================================
 * Structured specification of:
 *   1. The two distinct, modularly connected domains:
 *      - Domain A: Aywa Web Design Philosophy (`weft/design/*`, Modules D1–D5)
 *      - Domain B: The Syntactic Weft (`weft/*.md`, Horizons 0–III & Codebases C1–C7)
 *   2. The 4-stage evolutionary progression (Seed -> Apple Silicon -> Custom Silicon -> Civilizational Weave)
 *   3. The 19 Moissanite Labs repositories and 7 Weft runtime codebases
 *   4. The Syntactic Weft Whitepaper sections and Vision-to-Implementation Glossary
 */

export const LOCI = [
  {
    id: "spine",
    index: 0,
    code: "01",
    shortTitle: "Ecosystem Spine",
    title: "The Evolutionary Spine: Two Domains, Four Horizons, One Modular Architecture",
    subtitle:
      "Drawing the line between the Aywa Web Design Philosophy (how concepts and state live in a browser) and the Syntactic Weft (how adaptive intelligence computes, etches into silicon, and governs a civilization).",
  },
  {
    id: "aywa",
    index: 1,
    code: "02",
    shortTitle: "Aywa Web Design",
    title: "Aywa: A First-Principles Philosophy for Morphogenetic & Spatial Web Design",
    subtitle:
      "Encapsulating weft/design/* as a self-contained web design discipline: continuous Barycentric Aesthetic Spaces on the unit circle, analytical SDF & Laya kinetic typography, 64-byte uniform state buses, and spatial Mind-Palace loci.",
  },
  {
    id: "horizon1",
    index: 2,
    code: "03",
    shortTitle: "Horizon I: Apple Silicon",
    title: "Horizon I: Apple Silicon Initial Prototype (The Cellular Organism)",
    subtitle:
      "Verified and running today (Codebases C1, C2, C3, C6): Unified-memory 540,688-byte Stratified Plasm, speculative A/B mitosis with 25% frozen core mask, baseline Frobenius safety gate, and flat-array Interaction Combinator VM.",
  },
  {
    id: "horizon2",
    index: 3,
    code: "04",
    shortTitle: "Horizon II: Custom Silicon",
    title: "Horizon II: Custom Silicon & Terrafab Foundry (The Physical Loom)",
    subtitle:
      "Lowering software contracts into physical law: ring-0 bare-metal unikernel & attention-driven APIC interrupts (Stage II-A), hardware-etched DMA invariant comparators (Stage II-B), and wafer-scale photonic IC tiles (Stage II-C).",
  },
  {
    id: "horizon3",
    index: 4,
    code: "05",
    shortTitle: "Horizon III: Civilizational Weave",
    title: "Horizon III: The Societal & Civilizational Weave (Constitutional Homeostasis)",
    subtitle:
      "Scaling adaptive intelligence into a self-balancing civilizational fabric (Codebases C4, C5): 12-hop homomorphic lineage attribution, the 85/15 metabolic capital excision valve, and independent systemic tension adjudication.",
  },
  {
    id: "whitepaper",
    index: 5,
    code: "06",
    shortTitle: "Whitepaper & Glossary",
    title: "The Syntactic Weft Whitepaper, Timeline Matrix & Engineering Glossary",
    subtitle:
      "Complete first-principles treatise, cross-horizon milestone schedule, and vision-to-implementation glossary mapping every biological and physical metaphor to its verified engineering contract.",
  },
];

export const HORIZONS = [
  {
    stage: "Horizon 0",
    phase: "Foundation Layer (Active)",
    name: "The Symbolic & Epistemic Seed",
    substrate: "Multi-agent continuous harness (exo) + SYM-2P/1.0 symbolic wire protocol",
    invariant: "Deterministic SHA-256 s-expression packet integrity (101B symbolic vs 481B JSON)",
    codebases: ["I2 (SYM-2P/1.0)", "compass", "abios", "exo", "alkindus", "averroes", "synbios"],
    summary:
      "Establishes the founding constitution (compass #5), dense checkable symbolic communication (SYM-2P/1.0), continuous self-watching agent memory (exo), and falsifier-driven epistemic verification before fusing into shared unified memory.",
  },
  {
    stage: "Horizon I",
    phase: "Phase 1 & 2 Complete (Verified on main)",
    name: "Apple Silicon Initial Prototype (The Cellular Organism)",
    substrate: "Apple M-series Unified Memory (POSIX shm_open 540,688B + Metal/MPS + C11 + Python)",
    invariant: "||W_cand - W_base||_F <= 120.0 (Frobenius gate), budget >= cost > 0, watermark >= 90%",
    codebases: ["C1 (plasm)", "C2 (invariants)", "C3 (ic + BCP)", "C6 (telemetry)"],
    summary:
      "Replaces static-weight inference and IPC serialization with Models-as-Cells inside a 3-tier unified memory arena (Focal [256,256], Sympathetic [1024], Hippocampal [64,1024], plus a 16-byte header and 12,288 reserved lock bytes), adapting via speculative A/B mitosis and flat-array Lafont Interaction Combinator graph reduction.",
  },
  {
    stage: "Horizon II",
    phase: "Next Engineering Horizon (Stages II-A -> II-B -> II-C)",
    name: "Custom Silicon & Terrafab Foundry (The Physical Loom)",
    substrate: "Ring-0 bare-metal unikernel (boot.asm) -> FPGA RTL -> Wafer-scale 3D-stacked & photonic ASIC",
    invariant: "Single-cycle DMA hardware Frobenius gate & Landauer bit-erasure efficiency (k_B T ln 2)",
    codebases: ["Stage II-A (boot.asm / APIC)", "Stage II-B (RTL weft_invariants.h)", "Stage II-C (Terrafab / Terraweft)"],
    summary:
      "Eliminates OS context switches and Von Neumann instruction fetch by identity-mapping the tensor bus at 0x10000000, scheduling interrupts by attention urgency, etching the C2 invariant gate into DMA hardware, and executing IC graph rewrites on physical silicon crossbars.",
  },
  {
    stage: "Horizon III",
    phase: "Local Simulation Verified (C4/C5) -> Federated Rollout",
    name: "The Societal & Civilizational Weave (Constitutional Homeostasis)",
    substrate: "Three-Contract Solidity Triad (C4) + Keccak-256 Off-Chain Gateway (C5) + Consented Peer Mesh",
    invariant: "85% weaver / 15% burn excision split, T <= 85.0% tension ceiling, 12-hop cycle-free lineage DAG",
    codebases: ["C4 (ProvenanceRegistry, WeftTokenTissue, TensionGovernor)", "C5 (gateway)", "C8 (consented mesh)"],
    summary:
      "Binds human creators and autonomous cells into a non-extractive constitutional economy: every cross-spliced capability preserves cryptographic root attribution, routes 85% of execution fees to lineage creators while burning 15%, and slashes rogue high-tension swarms via independent adjudication.",
  },
];

export const CODEBASES = [
  {
    id: "C1",
    name: "plasm",
    path: "weft/runtime/plasm/",
    horizon: "Horizon I",
    interfaces: "I3, I4, I7",
    tests: "C1 unit and I4 conformance tests (test_plasm.py)",
    purpose:
      "540,688-byte POSIX shared-memory arena (Focal [256,256], Sympathetic [1024], Hippocampal [64,1024], plus a 16-byte header and 12,288 reserved lock bytes), deterministic close() teardown, neutral seed WEFT-PLASM-SEED-V1, target-directed A/B mitosis, 25% frozen core plasticity mask, and >= 90% linear watermark retention.",
  },
  {
    id: "C2",
    name: "invariants",
    path: "weft/runtime/invariants/",
    horizon: "Horizon I & II",
    interfaces: "I3",
    tests: "8/8 pass (Python + C11 cc -std=c11)",
    purpose:
      "Pure cross-language safety predicates (invariants.py, standalone C11 weft_invariants.h, and vectors.json): baseline-relative Frobenius distance (||W_cand - W_base||_F <= 120.0), positive budget pre-check, NaN/Inf rejection, tension bound (<= 85.0), and 15%/85% integer wei split.",
  },
  {
    id: "C3",
    name: "ic",
    path: "weft/runtime/ic/",
    horizon: "Horizon I & II",
    interfaces: "I5 (BCP)",
    tests: "5/5 pass (test_ic.py)",
    purpose:
      "Zero-allocation flat-array Lafont Interaction Combinator VM (ERA=0, CON=1, DUP=2, plus Weft extensions VLV=3, FRC=4, SUP=5), deterministic active-pair reduction, 12-byte header (WEFT) + 20-byte node record (<IBBhiii) BCP binary codec, and SHA-256 execution trace hash.",
  },
  {
    id: "C4",
    name: "ledger",
    path: "weft/runtime/ledger/",
    horizon: "Horizon III",
    interfaces: "I5, I6",
    tests: "Verified via C5 & site_selftest.py",
    purpose:
      "Three-contract Solidity ^0.8.26 governance triad: ProvenanceRegistry.sol (cycle-free 12-hop bounded lineage DAG), WeftTokenTissue.sol (controlled metabolic allocation + 85/15 excision valve), and TensionGovernor.sol (T > 85 fracture reporting + independent adjudication guard).",
  },
  {
    id: "C5",
    name: "gateway",
    path: "weft/runtime/gateway/",
    horizon: "Horizon III",
    interfaces: "I5, I6",
    tests: "5/5 pass (test_gateway.py)",
    purpose:
      "Pure-Python Keccak-f[1600] (0x01 padding) Ethereum ABI event topic verifier (replacing fabricated 0x8f3e prefixes), localhost-only default RPC guard, environment-only key loader, and deterministic LedgerTriadSimulator.",
  },
  {
    id: "C6",
    name: "telemetry",
    path: "weft/runtime/telemetry/",
    horizon: "Horizon 0 & I",
    interfaces: "I1, I2",
    tests: "4/4 pass (test_telemetry.py)",
    purpose:
      "Honest host hardware probe (darwin-sysctl on macOS, linux-procfs on Linux, source='unavailable' with None fields when absent), Moissanite-Labs harvester (fixture default + --live GitHub API mode, zero personal logins), SYM-2P/1.0 codec, and 64-byte (<16f) frame packer.",
  },
  {
    id: "C7",
    name: "aywa",
    path: "weft/runtime/aywa/ & docs/",
    horizon: "Aywa Web Design",
    interfaces: "I1, I2",
    tests: "10/10 Python + 8/8 Node + site_selftest.py",
    purpose:
      "Browser spatial organism on w3ft.org: unit-circle circular-hue Barycentric Aesthetic Mixer, SHA-256 verified SYM-2P Web Worker poller, high-DPR ResizeObserver WebGPU/Canvas2D renderer, full 16-float + labelData WGSL shader, 5 interactive widgets, and allow-listed dist staging.",
  },
];

export const ECOSYSTEM_REPOS = [
  { name: "compass", horizon: "horizon0", layer: "governance", codebase: "Charter", role: "Founding constitution, SOPs, and origin architecture thread (Discussion #5)", tension: 0.18, commits: 14 },
  { name: "abios", horizon: "horizon0", layer: "substrate", codebase: "I2 / C1", role: "SYM-2P/1.0 dense symbolic agent protocol (101B vs 481B JSON) & cellular lifecycle", tension: 0.22, commits: 27 },
  { name: "alkindus", horizon: "horizon0", layer: "cognition", codebase: "Verification", role: "Epistemic verification, falsifier benchmarking, and mathematical audit core", tension: 0.21, commits: 19 },
  { name: "averroes", horizon: "horizon0", layer: "cognition", codebase: "Verification", role: "Dialectical debate, multi-witness critique, and consensus engine", tension: 0.17, commits: 16 },
  { name: "synbios", horizon: "horizon0", layer: "governance", codebase: "C6", role: "Collaborative agentic development platform & mission-control matrix", tension: 0.20, commits: 24 },
  { name: "mlx", horizon: "horizon1", layer: "substrate", codebase: "C1 (plasm)", role: "Apple Silicon unified-memory zero-copy tensor training & experimentation", tension: 0.25, commits: 31 },
  { name: "statos", horizon: "horizon1", layer: "substrate", codebase: "C1 / C6", role: "Statistical operating system where applications are weight tensors in shared memory", tension: 0.28, commits: 22 },
  { name: "tokenpage", horizon: "horizon1", layer: "substrate", codebase: "C1 / C3", role: "Fixed-size page table and contiguous flat-array memory arena management", tension: 0.19, commits: 18 },
  { name: "khwarizmi", horizon: "horizon1", layer: "substrate", codebase: "C3 (ic)", role: "Algebraic graph reduction & Lafont Interaction Combinator rewrite engine", tension: 0.29, commits: 29 },
  { name: "jazari", horizon: "horizon1", layer: "substrate", codebase: "C2 / C3", role: "Mechanical valve automata, metabolic clockwork, and VLV gate execution", tension: 0.26, commits: 24 },
  { name: "avicenna", horizon: "horizon1", layer: "substrate", codebase: "C6 (telemetry)", role: "Autonomic homeostatic diagnostic loop & sympathetic ring telemetry", tension: 0.28, commits: 22 },
  { name: "mulla-sadra", horizon: "horizon1", layer: "cognition", codebase: "C1 (plasm)", role: "Substantial motion (haraka jawhariyya) & core-freezing weight plasticity", tension: 0.25, commits: 20 },
  { name: "aywa", horizon: "aywa", layer: "interface", codebase: "C7 (aywa)", role: "WebGPU spatial canvas, Barycentric Aesthetic Simplex, and Mind-Palace UI", tension: 0.24, commits: 42 },
  { name: "qalam", horizon: "aywa", layer: "interface", codebase: "C7 (aywa)", role: "Analytical Signed Distance Field (SDF) & Laya kinetic typography engine", tension: 0.19, commits: 31 },
  { name: "alhazen", horizon: "aywa", layer: "interface", codebase: "C7 (aywa)", role: "Optical perception, visual grounding, and viewport-culled spatial geometry", tension: 0.15, commits: 15 },
  { name: "suhrawardi", horizon: "horizon2", layer: "interface", codebase: "Stage II-C", role: "Illuminationist shader pipeline & photonic waveguide interconnect field", tension: 0.21, commits: 17 },
  { name: "tusi", horizon: "horizon2", layer: "substrate", codebase: "Stage II-A", role: "Coupled oscillator kinematics & attention-driven APIC interrupt cadence", tension: 0.16, commits: 14 },
  { name: "khayyam", horizon: "horizon2", layer: "substrate", codebase: "Stage II-B/C", role: "Geometric cubic solver & 3D wafer-scale silicon tile layout", tension: 0.13, commits: 11 },
  { name: "kindi", horizon: "horizon3", layer: "ledger", codebase: "C1 / C4", role: "Cryptographic frequency analysis & homomorphic vector watermark provenance", tension: 0.22, commits: 21 },
  { name: "banu-musa", horizon: "horizon3", layer: "ledger", codebase: "C4 / C5", role: "Differential feedback control & 85/15 metabolic excision valve economics", tension: 0.18, commits: 13 },
  { name: "farabi", horizon: "horizon3", layer: "cognition", codebase: "Horizon III", role: "Polyphonic harmonic scheduling & multi-agent virtuous city governance", tension: 0.14, commits: 12 },
  { name: "biruni", horizon: "horizon3", layer: "cognition", codebase: "Horizon III", role: "Empirical cross-corpus geodesic indexing & multi-node consensus", tension: 0.20, commits: 18 },
  { name: "moissanite-HQ", horizon: "horizon3", layer: "ledger", codebase: "C4 / C5", role: "Organization charter, constitutional court, and sovereign ledger anchor", tension: 0.12, commits: 9 },
];

export const AYWA_MODULES = [
  {
    code: "D1",
    title: "Barycentric Aesthetic Simplex & Circular Hue",
    source: "weft/design/baryonic.md, discovery.md, core.md",
    summary:
      "Visual themes are points on a continuous simplex rather than static CSS classes. Linear parameters (rounding, density, contrast) blend by normalized weights, while chromatic hue interpolates on the unit circle S^1 via atan2(sum(w_i sin theta_i), sum(w_i cos theta_i)) so crimson (0.95) and scarlet (0.05) wrap smoothly across 0.0 red rather than averaging linearly through 0.50 cyan.",
  },
  {
    code: "D2",
    title: "Analytical SDF & Laya Kinetic Typography",
    source: "weft/design/typo.md, craft.md",
    summary:
      "Cells, borders, and procedural glyph matrices are evaluated per pixel via Signed Distance Functions (sdBox) in WGSL, remaining crisp at any DPR or zoom level. Typographic cadence (Laya) couples tracking and alpha/beta lineage weights to scroll velocity.",
  },
  {
    code: "D3",
    title: "Zero-Allocation 64-Byte Uniform Bus & SYM-2P Gate",
    source: "weft/design/system.md, sym2p-parse.js",
    summary:
      "All live state fits in a single 64-byte IEEE-754 uniform buffer (16 float32 slots: active_nodes, org_tension, system_time, gini_index, 4 barycentric tokens, and 8 node velocities). Every inbound SYM-2P/1.0 packet is verified with WebCrypto SHA-256 before touching the buffer.",
  },
  {
    code: "D4",
    title: "Morphogenetic & Cellular Surfaces",
    source: "weft/design/bio.md, method.md, real.md",
    summary:
      "UI regions behave as homeostatic tissues governed by local neighborhood rules: border glow, cell packing, and color temperature respond continuously to systemic tension (homeostatic band 15%–35%, safety ceiling 85%).",
  },
  {
    code: "D5",
    title: "Spatial Mind-Palace Loci",
    source: "weft/design/mind-palace.md, aywa.md, next.md",
    summary:
      "Replaces the 'Document Prison' of endless linear scrolling with distinct spatial rooms (Loci) anchored to a persistent topological canvas. Switching Loci reconfigures both the foreground architectural specification and the background GPU field.",
  },
];

export const WIDGETS = [
  {
    id: "01",
    file: "widgets/01-sdf-laya-kinetic-typography.html",
    jsx: "widgets/01-sdf-laya-kinetic-typography.jsx",
    origin: "Recorded capture: Thread 2 (6C083A) Turn 6",
    title: "01: Procedural Wave Sandbox",
    desc:
      "Canvas2D radial and matrix waves with animation speed, spatial frequency and play/pause controls.",
  },
  {
    id: "02",
    file: "widgets/02-mind-palace-spatial-memory.html",
    jsx: "widgets/02-mind-palace-spatial-memory.jsx",
    origin: "Recorded capture: Thread 2 (6C083A) Turn 19",
    title: "02: Signed-Distance Geometry Explorer",
    desc:
      "SVG circle and box fields with union, subtraction, intersection, smooth union and an interactive distance probe.",
  },
  {
    id: "03",
    file: "widgets/03-morphogenetic-bioelectric-field.html",
    jsx: "widgets/03-morphogenetic-bioelectric-field.jsx",
    origin: "Recorded capture: Thread 1 (84ADC9) Turn 10",
    title: "03: Reflex and Cognitive Flow Diagram",
    desc:
      "Canvas2D animation connecting telemetry, reflex and cognitive systems, uniforms and GPU nodes. Displayed synergy, latency and load are slider-derived examples.",
  },
  {
    id: "04",
    file: "widgets/04-neural-cellular-automata.html",
    jsx: "widgets/04-neural-cellular-automata.jsx",
    origin: "Recorded capture: Thread 1 (84ADC9) Turn 25",
    title: "04: Target-Guided Cellular Automaton",
    desc:
      "A 56×32 grid with eight channels, hand-coded neighborhood rules, a fixed coordinate target, damage and reseeding controls.",
  },
  {
    id: "05",
    file: "widgets/05-interaction-combinator-net.html",
    jsx: "widgets/05-interaction-combinator-net.jsx",
    origin: "Recorded capture: Thread 1 (84ADC9) Turn 40",
    title: "05: Force-Directed Concept Graph",
    desc:
      "Five illustrative agent/code/net nodes move under spring and repulsion forces. Reduction rates, power values and short provenance labels are simulated.",
  },
];

export const GLOSSARY_ITEMS = [
  {
    term: "Syntactic Weft",
    domain: "Architecture",
    ideal: "Unified computational, silicon, and constitutional fabric where intelligence self-assembles under physical invariants and provenance laws.",
    horizon1: "7 modular codebases (C1–C7) verified by Python, C11, and Node.js CI suites.",
    horizon23: "Wafer-scale Terrafab IC silicon coupled to the three-contract constitutional ledger across federated nodes.",
  },
  {
    term: "Aywa",
    domain: "Web Design",
    ideal: "Zero-DOM, continuous, spatial, and bio-responsive web design paradigm in the browser.",
    horizon1: "C7 (docs/ on w3ft.org): WebGPU + High-DPI Canvas2D locus renderer, circular-hue Barycentric Mixer, and 5 simulation widgets.",
    horizon23: "Full GPU-native spatial operating surface with analytical MSDF/Bezier glyph atlases.",
  },
  {
    term: "Barycentric Simplex",
    domain: "Web Design",
    ideal: "Representing visual style as a continuous coordinate vector across archetypes rather than discrete CSS classes.",
    horizon1: "aesthetic-mixer.js: simplex weight normalization + unit-circle circular mean hue (atan2).",
    horizon23: "Per-pixel shader style fields driven continuously by operator attention and semantic load.",
  },
  {
    term: "Models-as-Cells",
    domain: "Horizon I",
    ideal: "Treating models as bounded, isolated cells with explicit lifecycles, speculative A/B children, and deterministic teardown.",
    horizon1: "SovereignOrganismCell and StratifiedMemoryArena.close() in weft/runtime/plasm/plasm.py.",
    horizon23: "Hardware-isolated ring-0 cell partitions with DMA-enforced memory bounds.",
  },
  {
    term: "Stratified Memory Plasm",
    domain: "Horizon I",
    ideal: "Shared unified memory partitioned into fast sensory tensors, autonomic scalars, and episodic novelty memory.",
    horizon1: "540,688-byte POSIX shm_open arena: Focal [256,256] + Sympathetic [1024] + Hippocampal [64,1024], plus a 16-byte header and 12,288 reserved lock bytes. CPU views share storage; tensor reads copy.",
    horizon23: "3D-stacked SRAM/HBM tiers identity-mapped at physical address 0x10000000 (boot.asm).",
  },
  {
    term: "Frobenius Invariant Gate",
    domain: "Horizon I & II",
    ideal: "Hard mathematical boundary refusing any weight update whose drift from the saved baseline exceeds R_invariant.",
    horizon1: "verify_weight_update_safety_ex in invariants.py and C11 weft_invariants.h (R_INVARIANT = 120.0).",
    horizon23: "Inline RTL/ASIC DMA comparator aborting out-of-radius weight page writes in a single bus cycle.",
  },
  {
    term: "Homomorphic Watermark",
    domain: "Horizon I & III",
    ideal: "Cryptographic creator trigger (Y = X_trig * W) that survives fine-tuning and cross-splicing across generations.",
    horizon1: "Core-freezing 25% plasticity mask + linear trigger projection retaining >= 90% cosine similarity over 10+ cycles.",
    horizon23: "On-chain commitment verification in ProvenanceRegistry.sol across 12-hop lineage DAGs.",
  },
  {
    term: "Interaction Combinator VM",
    domain: "Horizon I & II",
    ideal: "Deterministic, garbage-collection-free computation via Lafont graph reduction (ERA, CON, DUP).",
    horizon1: "FlatCombinatorVM (ic_vm.py) + 12B/20B BCP binary graph codec (bcp_codec.py) + SHA-256 trace hash.",
    horizon23: "Terrafab wafer-scale crossbar tiles and photonic waveguides executing active-pair annihilation in hardware.",
  },
  {
    term: "Metabolic Excision Valve",
    domain: "Horizon III",
    ideal: "Non-extractive economic homeostasis routing 85% of execution fees to lineage creators and burning 15%.",
    horizon1: "compute_royalty_split (C2), WeftTokenTissue.sol::executeExcisionValve (C4), and LedgerTriadSimulator (C5).",
    horizon23: "Automated settlement across the federated Moissanite Labs capability weave.",
  },
  {
    term: "Tension Governor",
    domain: "Horizon III",
    ideal: "Constitutional balancing court halting or slashing rogue high-tension swarms (T > 85.0%).",
    horizon1: "verify_tension_bound (C2) and TensionGovernor.sol with enforceIndependentAdjudicator = true (C4/C5).",
    horizon23: "Multi-witness threshold governance with Gini concentration dampening.",
  },
];
