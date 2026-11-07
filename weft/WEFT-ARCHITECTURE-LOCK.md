# Weft Sovereign Architecture Lock

Date: 2026-11-07
Status: Active North-Star Specification

## 1. Core Architectural Thesis

The Weft corpus (`weft/`) establishes the primary architectural north star for the system. It replaces layered, allocation-heavy software stacks with a hardware-synchronized execution fabric organized into seven modular codebases (`C1`–`C7`):

1. **Stratified Unified Memory Plasm (`C1`: `weft/runtime/plasm/`)**: A zero-copy POSIX shared-memory (`shm_open`, 540,688 bytes) and Apple Silicon Metal Performance Shaders (`mps` / CPU fallback) tensor substrate divided into three regions:
   - **Focal Nerve Register (`[4, 64, 512]` float32)**: High-frequency sensory and target-directed speculative inference channels.
   - **Sympathetic Ring (`[4]` float32)**: Real-time system tension, metabolic budget, clock step, and estimated load thermal state.
   - **Hippocampal Novelty Lattice (`[8, 512]` float32)**: Circular memory buffer that enforces anti-homogenization pressure during mitotic selection while preserving a 25% frozen core plasticity mask and linear watermark retention (`>= 90%`).
2. **Invariants and Thermodynamic Safety Gate (`C2`: `weft/runtime/invariants/`)**: Pure Python and C11 (`weft_invariants.h`) safety predicates enforcing baseline-relative Frobenius distance (`||W_cand - W_base||_F <= R_invariant`), metabolic budget pre-checks, tension bounds (`T <= 85.0`), and integer-exact 15%/85% royalty excision splits verified against shared cross-language test vectors (`vectors.json`).
3. **Zero-Allocation Interaction Combinator VM & BCP Codec (`C3`: `weft/runtime/ic/`)**: A flat-array Lafont Interaction Combinator reducer (`ERA=0`, `CON=1`, `DUP=2`, `VLV=3`, `FRC=4`, `SUP=5`) where computation proceeds by deterministic active-pair annihilation (`CON-CON`), commutation (`DUP-CON`), erasure (`ERA-*`), and metabolic valve gating (`VLV`) without garbage collection, paired with a 12-byte header (`WEFT`) + 20-byte node record (`<IBBhiii`) BCP binary graph serializer (`bcp_codec.py`) and SHA-256 execution trace commitment.
4. **Homomorphic Provenance Triad & Off-Chain Gateway (`C4`: `weft/runtime/ledger/`, `C5`: `weft/runtime/gateway/`)**: Cycle-free, 12-hop bounded lineage attribution (`ProvenanceRegistry.sol`), 85%/15% metabolic excision (`WeftTokenTissue.sol`), and independent tension adjudication (`TensionGovernor.sol`), paired with a pure-Python Keccak-256 ABI topic verifier and localhost-guarded gateway simulator.
5. **Host & Organization Telemetry + Aywa Spatial Surface (`C6`: `weft/runtime/telemetry/`, `C7`: `weft/runtime/aywa/` & `docs/`)**: Honest host hardware probing (`darwin-sysctl`, `linux-procfs`, or `unavailable`), SHA-256 verified `SYM-2P/1.0` wire packets, a 64-byte IEEE-754 uniform buffer (`16 x float32`), circular-hue Barycentric Aesthetic Mixing, and a single-pass WebGPU / high-DPI Canvas2D spatial interface.

## 2. Adaptive Operating Principles

Per owner direction on 2026-11-07, team operating principles adapt to the Weft north star:

- **Continuous Capability Synthesis**: Preserve human purpose and capability identity across repository boundaries while composing the strongest verified mechanisms from `Moissanite-Labs` into the Weft runtime.
- **Hardware-Grounded Verification**: Every architectural claim must execute against real host metrics and deterministic falsifiers (`unittest`, `node --test`, `cc -std=c11`, `selftest.py`, `site_selftest.py`) and report `"source": "unavailable"` or `"source": "fixture"` honestly when hardware or network APIs are absent.
- **Zero-Loss Source Fidelity**: All 144 DOM-extracted turns (plus the 3 pre-window turns preserved in `README.md`, `more.md`, and `mac.md`), 191 repaired fenced code blocks (`34 + 110 + 47`), and 5 sandboxed interactive simulation widgets from the two origin Google Chrome sessions are preserved in `browser-sources/` and verified by automated AST and fence checks.
