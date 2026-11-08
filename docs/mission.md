# ML Weft Charter & Ecosystem Architecture

Date: 2026-11-08
Organization: Moissanite Labs (`Moissanite-Labs/weft`)

## 1. The Architectural Line: Two Distinct, Modularly Connected Domains

The `weft/` corpus contains two distinct bodies of work that share the same mathematical first principles while solving different problems at different scales:

1. **Aywa (`weft/design/*`): A First-Principles Philosophy for Web Design and Spatial Representation**
   - **Scope**: How human-computer interfaces represent concepts, information, and live state on a screen.
   - **Core Shift**: Replaces static Document Object Model (DOM) box trees, discrete brittle stylesheets, and passive vertical scrolling with a continuous, zero-allocation, GPU-native visual medium.
   - **Self-Contained Modules**:
     - *Barycentric Aesthetic Simplex (`design/baryonic.md`, `design/discovery.md`)*: Visual style is a continuous coordinate vector across reference archetypes (`native_base`, `neon_terminal`, `airy_pastel`, `manuscript`), blending linear layout tokens on a simplex and chromatic hue via the circular mean on the unit circle (`atan2(sum(w_i * sin(theta_i)), sum(w_i * cos(theta_i)))`).
     - *Analytical Field & Laya Typography (`design/typo.md`, `design/craft.md`)*: Signed Distance Field (SDF) geometry and cadence-aware (`Laya`) typographic proportions that respond to reading velocity and conceptual density without bitmap rasterization.
     - *Zero-Allocation 64-Byte Uniform Bus (`design/system.md`)*: A 16-float (`64`-byte) IEEE-754 uniform buffer fed by SHA-256 verified `SYM-2P/1.0` symbolic packets over a Web Worker membrane.
     - *Spatial Mind-Palace Loci & Morphogenetic Surfaces (`design/mind-palace.md`, `design/bio.md`)*: Information organized into navigable spatial rooms (*loci*) and self-healing cellular grids rather than disconnected pages.
   - **Modular Connection to the Weft**: Aywa stands on its own as a reusable web design paradigm for any complex knowledge or telemetry system. Within ML Weft (`w3ft.org`), Aywa serves as the visual medium that communicates the Syntactic Weft itself.

2. **The Syntactic Weft (`weft/*.md`): A Schema for Adaptive Intelligence and Civilizational Governance**
   - **Scope**: How adaptive intelligence computes in memory, how its mutations are bounded by physical and mathematical invariants, how it lowers into custom silicon, and how a civilization of human and artificial agents governs provenance, capital, and collective alignment.
   - **Core Shift**: Replaces isolated, static-weight model inference, high-overhead inter-process serialization, and extractive platform economics with **Models-as-Cells** operating inside a unified memory arena, **Interaction Combinator** graph reduction, hardware-enforced **Frobenius Safety Invariants**, and a **Three-Contract Constitutional Ledger Triad**.

## 2. The Modular Ecosystem Map (`Moissanite-Labs` -> `ML Weft`)

Every repository in `Moissanite-Labs` and every runtime package in `weft/runtime/` (`C1` through `C7`) occupies a single, self-evident slot along a four-stage evolutionary progression:

| Evolutionary Stage | Layer Role | Related public Moissanite Labs repositories | Weft Runtime Codebases & Contracts |
| :--- | :--- | :--- | :--- |
| **Horizon 0: Symbolic & Epistemic Seed** | Constitutional charter, symbolic agent wire language, continuous memory harness, and epistemic verification | [`abios`](https://github.com/Moissanite-Labs/abios), [`exo`](https://github.com/Moissanite-Labs/exo), [`synbios`](https://github.com/Moissanite-Labs/synbios), [`.github`](https://github.com/Moissanite-Labs/.github) | Interface **I2** (`SYM-2P/1.0` s-expression packet codec in `C6` / `C7`) |
| **Horizon I: Apple Silicon Initial Prototype** | Unified-memory cellular organism, speculative A/B mitosis, Frobenius invariant gate, and flat-array IC VM | [`tokenpage`](https://github.com/Moissanite-Labs/tokenpage), [`scry`](https://github.com/Moissanite-Labs/scry), [`nullmodem`](https://github.com/Moissanite-Labs/nullmodem) | **C1** (`plasm`), **C2** (`invariants`), **C3** (`ic`), **C6** (`telemetry`) |
| **Horizon II: Custom Silicon & Terrafab Foundry** | Bare-metal unikernel, hardware-etched invariant comparators, and wafer-scale / photonic compute fabrics | [`exofab`](https://github.com/Moissanite-Labs/exofab), [`exo-os`](https://github.com/Moissanite-Labs/exo-os) | `C2` (`weft_invariants.h`), `README.md` §16 (`boot.asm`, `interrupts.asm`), `terrafab.md`, `terraweft.md` |
| **Horizon III: Societal & Civilizational Weave** | Homomorphic lineage attribution, 85/15 metabolic capital excision, tension adjudication, and federated governance | [`synmerit`](https://github.com/Moissanite-Labs/synmerit), [`ethos`](https://github.com/Moissanite-Labs/ethos) | **C4** (`ledger`: `ProvenanceRegistry`, `WeftTokenTissue`, `TensionGovernor`), **C5** (`gateway`) |
| **Cross-Horizon Visual Medium: Aywa Web Design** | Continuous barycentric design space, SDF/Laya typography, and spatial Mind-Palace browser organism | [`exoframe`](https://github.com/Moissanite-Labs/exoframe) | **C7** (`weft/runtime/aywa/` and `site/` public bundle on `w3ft.org`) |

## 3. Core Engineering Commitments

1. **Self-Evident Modularity**: Each codebase (`C1`–`C7`) owns one computational responsibility, communicates across explicit byte-level interfaces (`I1`–`I7`), and carries its own runnable unit tests and falsifiers.
2. **Vision Language Paired with Honest Verification**: Biological and physical terms (*Plasm, Mitosis, Apoptosis, Homeostasis, Hippocampal Novelty, Terrafab*) name the architectural ideals the system iterates toward. Every README and specification distinguishes what executes in verified code today from what belongs to Horizon II and Horizon III hardware and societal milestones.
3. **Human Sovereignty and Provenance**: No safety invariant can be bypassed by a runtime dial, no weight mutation commits outside the baseline Frobenius radius (`||W_cand - W_base||_F <= R_invariant`), and every downstream capability splice preserves cryptographic attribution to its human and agent creators.
