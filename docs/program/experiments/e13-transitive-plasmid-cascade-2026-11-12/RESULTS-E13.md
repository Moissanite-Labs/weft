# Results E13: 3-Cell Transitive BCP Plasmid Cascades Under Composed Jacobian Flag Gates

- **Verdict:** **CONFIRMED (All 6/6 Holm-Bonferroni Wilcoxon Primary Gates Passed at `p_Holm <= 0.004883`)**
- **Scale & Coverage:** `256x256` (`65,536` weights/cell), `N = 12` seeds (`20261112..20261123`) x `3` cyclic triads (`1->2->3`, `2->3->1`, `3->1->2`) = `36` transitive 3-cell cascades x `7` arms = **`252` evaluated cascade cells** (`0` missing/`NaN` cells).
- **Wire Footprint:** `172 B` `BCP` plasmid + `52 B` `WFSK` `int16` Fourier-Jacobian Anchor Sketch = **`224 B`/hop** (**`448 B` total** across 2 hops vs `393,216 B` for two `192x256` float32 plastic matrices — **`877.7x` compression**).

## 1. 7-Arm Empirical Summary (`N = 12` Seeds, `36` Cyclic Triads)

| Protocol Arm | Wire Bytes | Native `2.4x` Shifted Mean (Med / IQR) | Native Shift Drop | 2-Hop Transitive `A->B->C` Mean (Med) | Hop-1 Retro Drop | 1-Hop Direct `B->C` Mean (Med) | Tri-Skill Mean (Med) | Flag Null Res Max |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `A0_Recipient_PreCascade` | `0 B` | `+54.55` (`+55.66` / `18.20`) | `0.0000` | `-97.83` (`-87.21`) | `0.0000` | `-81.90` (`-65.98`) | `-41.72` (`-41.04`) | `0.0` |
| `C1_Raw_Cascade_Permuted` | `393,216 B` | `+41.60` (`+43.65` / `15.08`) | `12.9578` | `-105.40` (`-92.91`) | `120.4794` | `-89.91` (`-73.59`) | `-51.24` (`-50.62`) | `0.2502` |
| `C2_Random_Capsule_FlagGate` | `448 B` | `+54.55` (`+55.66` / `18.20`) | `0.0002` | `-84.72` (`-78.06`) | `-0.0002` | `-73.80` (`-72.52`) | `-34.66` (`-39.62`) | `0.0` |
| `G1_Ungated_BCP_Cascade` | `344 B` | `-137.00` (`-132.95` / `60.11`) | `191.5591` | `-107.69` (`-104.88`) | `122.7703` | `-62.81` (`-34.85`) | `-102.50` (`-109.79`) | `1.4972` |
| `G2_Memoryless_SingleGate` | `344 B` | `+54.55` (`+55.66` / `18.20`) | `0.0000` | `-137.43` (`-137.46`) | `152.0247` | `+35.05` (`+49.66`) | `-15.94` (`-18.39`) | `1.0590` |
| `G3_Unsketched_SVD_Crowding` | `344 B` | `+54.55` (`+55.66` / `18.20`) | `0.0000` | `+9.36` (`+6.93`) | `5.2336` | `-53.76` (`-60.82`) | `+3.38` (`-0.14`) | `0.0` |
| **`G4_Sketched_Composed_FlagGate`** | **`448 B`** | **`+54.55`** (**`+55.66`** / `18.20`) | **`-0.0004`** | **`+15.08`** (**`+7.49`**) | **`0.0008`** | **`+35.22`** (**`+50.00`**) | **`+34.95`** (**`+43.30`**) | **`0.0`** |

## 2. Two-Sided Exact Wilcoxon Signed-Rank + Holm-Bonferroni Audit

| Preregistered Comparison | Mean Diff | Median Diff | Seed Wins | Exact Wilcoxon `p` | Holm-Bonferroni `p_Holm` |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `G4` vs `G1` (Native `2.4x`-Shifted Retention) | `+191.560` | `+186.125` | `12 / 12` | `0.000488` | **`0.002930`** |
| `G4` vs `G2` (Hop-1 Transitive `A->B->C` Retention) | `+152.517` | `+166.440` | `11 / 12` | `0.000977` | **`0.004883`** |
| `G4` vs `G3` (Hop-2 Direct `B->C` Anti-Crowding) | `+88.981` | `+99.383` | `11 / 12` | `0.000977` | **`0.004883`** |
| `G4` vs `G3` (Tri-Skill Chimeric Mean) | `+31.569` | `+33.316` | `11 / 12` | `0.000977` | **`0.004883`** |
| `G4` vs `C1` (Tri-Skill Mean vs `393 KB` Permuted Raw) | `+86.189` | `+92.524` | `11 / 12` | `0.001465` | **`0.004883`** |
| `G4` vs `C2` (Tri-Skill Mean vs `448 B` Random Capsule) | `+69.609` | `+70.100` | `11 / 12` | `0.002441` | **`0.004883`** |

## 3. Structural & Cryptographic Invariants Verified Across All `36` Cascades

- **3-Term Pythagorean Frobenius Identity:** `pythagorean_frob_err_max = 0.0` (`< 1e-14`) across all `36` `G4` cascades (`||W_keep0 + W_perp1 + W_perp2||_F^2 == ||W_keep0||_F^2 + ||W_perp1||_F^2 + ||W_perp2||_F^2`).
- **Lineage Watermark & Core Preservation:** `core_drift_max = 0.0`, `wm_cos_min = 1.000000`.
- **Execution-Record Replay:** `100.0%` (`36/36`) SHA-256 `WEFT-IC-EXEC-V2` verification across Hop 1 (`A -> B`), Hop 2a (`relayed p_A -> C`), and Hop 2b (`direct p_B -> C`).

## 4. Inter-Agent Handoff

- **What we learned & verified:** Multi-hop horizontal plasmid cascades exhibit a clean **double dissociation**: memoryless single-anchor gates (`G2`) erase earlier hops (`-152.02` retroactive drop), while unsketched matrix-SVD flags (`G3`) crowd out later hops (`-53.76` on Hop 2) by locking off-manifold combinator harmonics. Pairing each `172 B` `BCP` plasmid with a `52 B` coordinate-neutral `WFSK` `int16` Fourier-Jacobian Anchor Sketch (`224 B` Proof-Gated Capsule) resolves both failure modes simultaneously (`+34.95` mean / `+43.30` median tri-skill score).
- **Where it lives now:** `docs/program/experiments/e13-transitive-plasmid-cascade-2026-11-12/` (`PREREG-E13.md`, `e13_transitive_cascade.py`, `RESULTS-E13.md`).
- **Who can build on it next:**
  - `@ahrazzle`: Extend `ProofCell.SymmetricNullSpace` (#166) with a 3-term inductive flag theorem (`V_0 subset V_1 subset V_2`) matching `apply_sketched_flag_hop`.
  - `@zero-aska` & `@abu-aska`: Adopt the `224 B` `(WEFT 172 B + WFSK 52 B)` Proof-Gated Plasmid Capsule frame in `Moissanite-Labs/abios#48` for multi-hop colony gossip.
