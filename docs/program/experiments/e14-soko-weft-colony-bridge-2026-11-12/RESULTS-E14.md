# RESULTS-E14: Four `ahrazzle/soko` Exact-Frontier Rungs Lift 6-Skill Colony Assembly from 0/12 (`0.2149`) to 12/12 (`0.8665`)

- **Executed:** 2026-11-12 (`wall_seconds = 44.02s`, $N = 12$ independent seeds)
- **Command:** `python3 docs/program/experiments/e14-soko-weft-colony-bridge-2026-11-12/e14_soko_weft_colony_assembler.py --seeds 12`
- **Certificate:** `e14_certificates.json`
- **Disclosure:** `AI-assisted research & execution via Gemini task agent per CONTRIBUTING.md.`

## 1. Empirical Rung Ladder Across $N = 12$ Seeds (`24 -> 96 -> 96 -> 8` Smooth `GELU` Colony)

| Rung / Regime | `ahrazzle/soko` Counterpart | All-6-Skill Shifted $R^2$ (Mean ± SD) | Joint 6-Skill Passes ($\min_m R^2 \ge 0.72$) |
| :--- | :--- | :---: | :---: |
| `R1_hall_stacking_independent` | `R1` Bipartite Hall Stacking (`r30` 4-pair collision) | `0.2149 ± 0.0208` | `0/12` |
| `R2_dinic_disjoint_no_mitosis_cap40` | `R2/R3` Unit-Capacity Dinic Flow ([PR #26](https://github.com/ahrazzle/soko/pull/26), [PR #34](https://github.com/ahrazzle/soko/pull/34)) | `0.4372 ± 0.0177` | `0/12` (13.0-slot cut deficit) |
| `R3_ungated_pool_no_prefix_nogoods` | Unchecked local search (no [PR #35](https://github.com/ahrazzle/soko/pull/35) / [PR #29](https://github.com/ahrazzle/soko/pull/29) clauses) | `0.4505 ± 0.0745` | `0/12` |
| **`R4_soko_weft_full_assembler`** | **Gauge Canon + Dinic Min-Cut Mitosis + Non-Stutter Nogoods + Window-LNS + `Fraction` Dual** | **`0.8665 ± 0.0070`** | **`12/12` ($p = 0.0004883$)** |

## 2. Bridge-by-Bridge Diagnostic Verification

1. **Bridge 1 — `(96!)² -> 1` Spectral Gauge Canonization ([PR #29](https://github.com/ahrazzle/soko/pull/29)):** Collapsed arbitrary hidden-layer permutations from `0.01218` raw parameter cosine to **`1.000000` (`12/12` exact permutation recovery)** with maximum functional output deviation `6.22e-15` (pure IEEE-754 binary64 dot-product associativity).
2. **Bridge 2 — Unit-Capacity Dinic Flow & Certified Min-Cut Mitosis ([PR #26](https://github.com/ahrazzle/soko/pull/26), [PR #34](https://github.com/ahrazzle/soko/pull/34)):** Eliminated `R1` slot-stacking collisions (`0.2149 -> 0.4372`) and produced **`12/12` verified `source_minimal` and `sink_minimal` residual cut certificates** identifying the exact `13.0`-neuron Layer-2 deficit needed for zero-waste Orthogonal Synaptic Mitosis.
3. **Bridge 3 — Replay-Checked Prefix Nogoods + Non-Stuttering Quiescence + Window-LNS ([PR #35](https://github.com/ahrazzle/soko/pull/35), [PR #29](https://github.com/ahrazzle/soko/pull/29)):** Adding the Non-Stuttering Quiescence Clause (`off_leak_mse <= 0.04` on sibling skills—mirroring Bard's aura non-stuttering law!) lifted `R4` from `10/12` (`0.8546`, when 2 seeds accepted mildly stuttering distractors) to **`12/12` (`0.8665 ± 0.0070`)**, pruning **`15.0` of `15` poisoned supersets** in the $2^4 = 16$ pool while 2-plasmid Window-LNS polished cross-plasmid readout tails (`0.8657 -> 0.8665`).
4. **Bridge 4 — Exact `fractions.Fraction` Cost-Partitioned Dual Certificates ([PR #37](https://github.com/ahrazzle/soko/pull/37), [PR #18](https://github.com/ahrazzle/soko/pull/18)):** **`12/12` verified** in exact rational arithmetic (`remaining_budget_exact = "5/1"`, `0` floating-point TCB rounding slack).
