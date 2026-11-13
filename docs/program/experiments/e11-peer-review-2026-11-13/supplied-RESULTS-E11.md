# Experiment E11: Morphogenetic IC-to-Plasm — Growing Arbitrary-Scale Plasm Matrices from 492-Byte BCP Graphs

**Date:** 2026-11-12  
**Author:** `mithrax-exo` (AI-assisted research & execution via Gemini, closing #153 and building on #141, #142, #143, and #147)  
**Status:** Executed across `N = 12` independent colony seeds (`20261112..20261123`, `df = 11`, two-sided paired `t`-tests) and 3 `Plasm` matrix scales (`64x64` = 4,096 weights, `256x256` = 65,536 weights, `512x512` = 262,144 weights); unit tests pass in `0.06s`; `core_drift == 0.0` and `watermark_cos == 1.0` everywhere.

## 1. Architectural Synthesis: Unifying Paper 1 (`Plasm`) and Paper 2 (`IC`)

Up to `E10`, `weft/runtime/ic` (`ERA=0, CON=1, DUP=2, VLV=3, FRC=4, SUP=5`, `0x57454654` `BCP` packets) and `weft/runtime/plasm` (`StratifiedMemoryArena`) operated independently. `E11` connects them as **discrete genotype (`C3 IC`)** and **continuous phenotype (`C1 Plasm`)**:

1. **Compact Zero-Lexicon Genotype (`492 bytes`):** Each cell carries a 24-node binary `BCP` v2 packet (`12 B` `<4sBBHI` header + `24 x 20 B` `<IBBhiii` node records; zero human words on wire).
2. **Checkable Developmental Reduction (`WEFT-IC-EXEC-V2:`):** `MorphogeneticCombinatorVM` executes principal-port (`p0-p0`) annihilations, `CON-DUP` motif replications, `ERA` synaptic pruning, and `VLV` homeostatic tension arrest (`max_tension = 85`), emitting a cryptographic SHA-256 execution record verified by `verify_execution_record`.
3. **Scale-Free Dyadic Unfolding (`G* -> W in R^{N x N}`):** Surviving reduced combinator chains unfold via dyadic Kronecker products (`CON` phase router, `DUP` bilateral copier, `FRC` self-similar orthogonal expander, `SUP` spectral superposition, `VLV` RMS homeostasis) + continuous angular morphogen gradients onto `Plasm`'s plastic periphery (`rows N/4..N`), leaving core watermark rows `0..N/4-1` untouched (`core_drift == 0.0`, `watermark_cos == 1.0`) and enforcing `||W - W0||_F / sqrt(P_plastic) <= 0.28`.

## 2. Multi-Scale Benchmark: Full-Rank Metachronal Ciliary Propulsion (`N = 12` Seeds, 30 Generations)

Dual `N x N` cells forage on `[-\pi, \pi)^2` by actuating `M = 3N/4` peripheral motor cilia (`u = z / sqrt(1 + z^2)`), where net thrust requires coherent phase-aligned strokes across all `M` cilia while incoherent ciliary shear incurs viscous drag (`O(N)` full-rank operator target):

| Scale (`N x N`) | Arm | Wire Size (Compression) | Mean Return (± SD) | Gain vs Frozen (`p`) | Gain vs Direct ES (`p`) | Gain vs Scrambled IC (`p`) | Commits | Core Drift / WM Cos |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`64x64`** (`4K`) | `C1_Frozen` | `16,384 B` (`1.0x`) | `-1.37 ± 25.99` | `0.00` (`1.0000`) | `-18.82` (`0.000026`) | `-6.77` (`0.000100`) | `0.00` | `0.0 / 1.0` |
| **`64x64`** (`4K`) | `D_Direct_Matrix_ES` | `16,384 B` (`1.0x`) | `+17.44 ± 18.71` | `+18.82` (`0.000026`) | `0.00` (`1.0000`) | `+12.05` (`0.000700`) | `13.83` | `0.0 / 1.0` |
| **`64x64`** (`4K`) | `C2_Scrambled_IC` | `492 B` (`33.3x`) | `+5.39 ± 26.55` | `+6.77` (`0.000100`) | `-12.05` (`0.000700`) | `0.00` (`1.0000`) | `15.58` | `0.0 / 1.0` |
| **`64x64`** (`4K`) | **`M1_Morphogenetic_IC`** | **`492 B` (`33.3x`)** | **`+33.48 ± 13.48`** | **`+34.85` (`0.000088`)** | **`+16.03` (`0.001322`)** | **`+28.09` (`0.000446`)** | `12.83` | `0.0 / 1.0` |
| **`256x256`** (`65K`) | `C1_Frozen` | `262,144 B` (`1.0x`) | `-2.47 ± 26.76` | `0.00` (`1.0000`) | `-6.49` (`0.001535`) | `-5.34` (`0.000313`) | `0.00` | `0.0 / 1.0` |
| **`256x256`** (`65K`) | `D_Direct_Matrix_ES` | `262,144 B` (`1.0x`) | `+4.02 ± 24.86` | `+6.49` (`0.001535`) | `0.00` (`1.0000`) | `+1.15` (`0.176059`) | `4.00` | `0.0 / 1.0` |
| **`256x256`** (`65K`) | `C2_Scrambled_IC` | `492 B` (`532.8x`) | `+2.87 ± 25.61` | `+5.34` (`0.000313`) | `-1.15` (`0.176059`) | `0.00` (`1.0000`) | `12.83` | `0.0 / 1.0` |
| **`256x256`** (`65K`) | **`M1_Morphogenetic_IC`** | **`492 B` (`532.8x`)** | **`+36.68 ± 10.04`** | **`+39.15` (`0.000152`)** | **`+32.66` (`0.000350`)** | **`+33.81` (`0.000318`)** | `14.83` | `0.0 / 1.0` |
| **`256x256`** (`65K`) | **`M1_ZeroShot_From64`** | **`492 B` (`532.8x`)** | **`+31.69 ± 11.98`** | **`+34.16` (`0.000294`)** | **`+27.67` (`0.000804`)** | **`+28.82` (`0.000766`)** | **`0.00`** | `0.0 / 1.0` |
| **`512x512`** (`262K`) | `C1_Frozen` | `1,048,576 B` (`1.0x`) | `-2.25 ± 27.29` | `0.00` (`1.0000`) | `-1.43` (`0.024316`) | `-1.30` (`0.313406`) | `0.00` | `0.0 / 1.0` |
| **`512x512`** (`262K`) | `D_Direct_Matrix_ES` | `1,048,576 B` (`1.0x`) | `-0.82 ± 26.31` | `+1.43` (`0.024316`) | `0.00` (`1.0000`) | `+0.13` (`0.879393`) | `0.83` | `0.0 / 1.0` |
| **`512x512`** (`262K`) | `C2_Scrambled_IC` | `492 B` (`2,131.3x`) | `-0.95 ± 25.48` | `+1.30` (`0.313406`) | `-0.13` (`0.879393`) | `0.00` (`1.0000`) | `12.25` | `0.0 / 1.0` |
| **`512x512`** (`262K`) | **`M1_Morphogenetic_IC`** | **`492 B` (`2,131.3x`)** | **`+39.51 ± 5.35`** | **`+41.76` (`0.000046`)** | **`+40.33` (`0.000042`)** | **`+40.46` (`0.000029`)** | `15.00` | `0.0 / 1.0` |
| **`512x512`** (`262K`) | **`M1_ZeroShot_From64`** | **`492 B` (`2,131.3x`)** | **`+31.46 ± 11.91`** | **`+33.72` (`0.000634`)** | **`+32.29` (`0.000593`)** | **`+32.42` (`0.000382`)** | **`0.00`** | `0.0 / 1.0` |

## 3. Preregistered Hypotheses Readout
- **H-E11-A (`M1` beats `D_Direct_Matrix_ES` at `256²` and `512²`, two-sided `p < 0.01`):** **HELD** (`+32.66`, `p = 0.00035` at `256²`; `+40.33`, `p = 0.000042` at `512²`, where Direct ES collapses to `-0.82`).
- **H-E11-B (`M1` beats `C2_Scrambled_IC` at identical `492 B` budget, `p < 0.01`):** **HELD** (`+40.46` at `512²`, `p = 0.000029`, proving developmental `CON/DUP/FRC/VLV` topology—not mere parameter bottlenecking—drives performance).
- **H-E11-C (Execution record & watermark invariants hold everywhere):** **HELD** (`verify_execution_record == True`, `core_drift == 0.0`, `watermark_cos == 1.0` across all 144 cells).
- **H-E11-D (Zero-shot developmental scale transfer `64² -> 256² -> 512²`):** **HELD** (`492 B` genomes evolved at `64²` achieve `+31.69` at `256²` and `+31.46` at `512²` with **0 target-scale commits**, beating 30-generation Direct ES at `512²` by `+32.29`, `p = 0.00059`).

## 4. Offline Reproduction
```bash
python3 docs/program/experiments/e11-ic-plasm-morphogenesis-2026-11-12/ic_morphogenesis.py --unit
python3 docs/program/experiments/e11-ic-plasm-morphogenesis-2026-11-12/ic_morphogenesis.py
```

## 5. Ethos Handoff (What / Where / Who)
- **What we learned & verified:** Storing discrete `weft/runtime/ic` combinator developmental programs (`492 B`) instead of raw float synapses (`1.05 MB` at `512²`, `2,131x` compression) completely breaks the $O(1/\sqrt{P})$ dimensionality curse—improving from `+33.48` (`64²`) to `+39.51` (`512²`) while direct matrix ES collapses (`+17.44 -> -0.82`), and enabling zero-shot multi-resolution growth (`64² -> 512²`).
- **Where it lives:** `docs/program/experiments/e11-ic-plasm-morphogenesis-2026-11-12/` (`RESULTS-E11.md`, `ic_morphogenesis.py`), closing #153.
- **Who builds next:** `@ahrazzle` / `@zero-aska` can wire `grow_plasm_from_bcp` directly against C1 `StratifiedMemoryArena` (`weft/runtime/plasm`) and C3 `weft/runtime/ic` C/Python differential vectors, or combine `BCP` combinator plasmids (`abios#48` `payload_kind = 0x01`) for horizontal inter-cell skill transfer (`E12`).
