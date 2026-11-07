# Weft Sovereign Architecture Lock

Date: 2026-11-07
Status: Active North-Star Specification

## 1. Core Architectural Thesis

The Weft corpus (``exo/weft/``) establishes the primary architectural north star for the system. It replaces layered, allocation-heavy software stacks with a single hardware-synchronized execution fabric that spans four planes:

1. **Stratified Unified Memory Plasm (`runtime/core/weft_plasm.py`)**: A zero-copy POSIX shared-memory (`shm_open`) and Apple Silicon Metal Performance Shaders (`mps`) tensor substrate divided into three regions:
   - **Focal Nerve Register (`[4, 64, 512]` float32)**: High-frequency sensory and speculative inference channels.
   - **Sympathetic Ring (`[4]` float32)**: Real-time system tension, metabolic budget, clock step, and silicon thermal state.
   - **Hippocampal Novelty Lattice (`[8, 512]` float32)**: Circular memory buffer that enforces anti-homogenization pressure during mitotic selection.
2. **Zero-Allocation Interaction Combinator VM (`runtime/core/weft_ic_vm.py`)**: A flat-array Lafont Interaction Combinator reducer (`ERA=0`, `CON=1`, `DUP=2`) where computation proceeds by deterministic active-pair annihilation (`CON-CON`), commutation (`DUP-CON`), and erasure (`ERA-*`) without garbage collection, paired with a cryptographic execution trace commitment.
3. **Sovereign Spatial WebGPU Environment (`runtime/aywa/`)**: A single-pass WebGPU and high-DPI Canvas2D spatial computing interface driven by a 64-byte IEEE-754 uniform buffer (`weft_daemon.py` and `github_harvester.py`) that maps live Darwin kernel telemetry and `Moissanite-Labs` repository metrics directly to Signed Distance Field (SDF) geometry and procedural ASCII glyph buffers.
4. **Homomorphic Provenance and Ledger Triad (`ProvenanceRegistry`, `WeftTokenTissue`, `TensionGovernor`)**: Weight-space watermark verification (`Y = W * X`) coupled to automated royalty excision and structural tension adjudication.

## 2. Adaptive Operating Principles

Per owner direction on 2026-11-07, team operating principles adapt to the Weft north star:

- **Continuous Capability Synthesis**: Preserve human purpose and capability identity across repository boundaries while composing the strongest verified mechanisms from `Moissanite-Labs` into the Weft runtime.
- **Hardware-Grounded Verification**: Every architectural claim must execute against real host hardware metrics (`sysctl`, POSIX shared memory, Apple Silicon MPS, and `selftest.py`) rather than mock stubs.
- **Zero-Loss Source Fidelity**: All 144 turns, 191 `<pre>` blocks, and 5 sandboxed interactive simulation widgets from the two origin Google Chrome sessions are preserved in `browser-sources/` and verified by automated AST and fence checks.
