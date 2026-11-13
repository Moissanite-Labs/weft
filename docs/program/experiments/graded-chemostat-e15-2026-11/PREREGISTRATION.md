# Preregistration: Experiment E15 - Graded-Difficulty Chemostat, Spore-Fraction Sweep, and Zero-Order Step Cooling

Date: 2026-11-11
Status: Preregistered and committed prior to running `run_e15.py` or collecting benchmark data.
Harness: `weft/runtime/mac/swarm_loom.py`
Runner: `docs/program/experiments/graded-chemostat-e15-2026-11/run_e15.py`

## Motivation and Code Audit Findings

Experiment E14 (`docs/program/experiments/apple-silicon-swarm-2026-11/README.md`) left three explicit follow-ups:
1. Test Law 2b on tiles of graded difficulty (easy to ill-conditioned) to measure whether chemostat flux pulls cells onto stalled hard tiles and cuts worst-tile error against `hgt_foraging`.
2. Sweep the spore fraction in Law 2c (`0.50` in E14 cost 27% of `hgt_foraging`'s error reduction).
3. Settle the Benchmark 1 vectorization speedup under pinned CPU thread counts.

The E14 `dissipative_chemostat` path uses the PR #118 gap-pay rule (`metab.py` `eff_reward`, and `swarm_loom.py` `1 / clamp(1 - sense, min=0.25)` with a 4x cap): payout grows as the remaining distance to the known record shrinks. `graded_chemostat` uses a different allocation rule, `(unsolved_gap / mean_unsolved_gap)^2`, which pays relatively unsolved tiles. The reward rule, the mass-conserving pool update, and the spore inheritance path change together in this mode, so no outcome isolates reward direction. The pool still resets to `tile_bounty` when a tile's best error improves by more than `1e-3`.

Two further changes in the same mode, plus a step-scale question carried from E14:
1. **Cross-niche spore velocity contamination (`swarm_loom.py:503`)**: Recolonized spores reset `W` toward `W0` on `target_niches`, but copied `self.velocity[donor_indices]` from random survivors on *different* tiles.
2. **Fixed `0.012` subspace step overshoot and static `mean_tension = 22.0` (`swarm_loom.py:235, 399`)**: At `dim = 128, subspace_rank = 4`, a masked rank-4 Gaussian step scaled by `0.012` has Frobenius norm `~2.66` (`53%` of the `5.0` target distance), stalling zero-order descent around `4-6%` error reduction.

## Fixed Protocol (Committed Before Execution)

- **Seeds**: 10 non-overlapping seeds, `20261121` through `20261130`.
- **Colony geometry**: `n_cells = 256`, `dim = 128` (`core_rows = 32` frozen), `n_niches = 8`, `subspace_rank = 4`, `r_invariant = 10.0`, `initial_energy = 100.0`, `basal_upkeep = 2.0`, `tile_bounty = 160.0`, `generations = 60`.
- **Graded 8-tile environment**:
  - Target ranks across tiles `m = 0..7`: `tile_ranks = [1, 2, 4, 6, 8, 12, 16, 24]`, each peripheral target normalized to Frobenius norm `0.5 * r_invariant = 5.0`.
  - Input conditioning across tiles `m = 0..7`: `tile_condition_numbers = [1.0, 1.5, 2.0, 3.0, 4.5, 6.0, 9.0, 12.0]`, scaling the singular spectrum of `X_tiles[m]` while matching `||X_tiles[m]||_F` to the baseline isotropic draw.
- **Arms compared on identical seeds (`7` arms x `10` seeds = `70` colony runs)**:
  1. `hgt_foraging` (unchanged E14 baseline, fixed step `0.012`).
  2. `dissipative_chemostat` (unchanged E14 Law 2 implementation, `spore_fraction = 0.50`, fixed step `0.012`).
  3. `graded_chemostat_sp000` (`graded_chemostat` allocation rule and niche-clean Law 2c, `spore_fraction = 0.00`, fixed step `0.012`).
  4. `graded_chemostat_sp125` (`graded_chemostat` allocation rule and niche-clean Law 2c, `spore_fraction = 0.125`, fixed step `0.012`).
  5. `graded_chemostat_sp250` (`graded_chemostat` allocation rule and niche-clean Law 2c, `spore_fraction = 0.25`, fixed step `0.012`).
  6. `graded_chemostat_sp500` (`graded_chemostat` allocation rule and niche-clean Law 2c, `spore_fraction = 0.50`, fixed step `0.012`).
  7. `graded_chemostat_cooled` (`graded_chemostat` allocation rule and niche-clean Law 2c, `spore_fraction = 0.25`, plus zero-order per-cell step-scale cooling `adaptive_step = True`).

## Preregistered Predictions

1. **P1 (Law 2b hard-tile allocation and worst-tile error at fixed step `0.012`)**:
   Comparing `graded_chemostat_sp250` against `hgt_foraging` and `dissipative_chemostat` at the same fixed `0.012` mutation scale:
   - `P1a`: Mean fraction of cells bound to the two hardest tiles (`m in {6, 7}`) at generation 60 is higher in `graded_chemostat_sp250` than in `hgt_foraging`.
   - `P1b`: Mean worst-tile relative error reduction `1 - max_m(best_tile_error_after[m] / E0[m])` is strictly higher in `graded_chemostat_sp250` than in both `hgt_foraging` and `dissipative_chemostat`.
2. **P2 (Law 2a zero coasting and Law 2c spore-fraction trade-off)**:
   - `P2a`: Across all four `graded_chemostat_sp*` arms (`0.00, 0.125, 0.25, 0.50`), `idle_surviving_cells` is `0` on all 10 seeds (`max == 0`), while `hgt_foraging` leaves `idle_surviving_cells > 0` on average.
   - `P2b`: Lowering `spore_fraction` from `0.50` (`graded_chemostat_sp500`) to `0.125` (`graded_chemostat_sp125`) or `0.25` (`graded_chemostat_sp250`) improves mean min-tile error reduction `1 - mean_min_tile_error_ratio` and recovers at least `95%` of `hgt_foraging`'s mean min-tile error reduction at fixed step `0.012`.
3. **P3 (Zero-order homeostatic step-scale cooling)**:
   - `P3a`: `graded_chemostat_cooled` (`adaptive_step = True`, `spore_fraction = 0.25`, forward evaluations only) achieves at least `1.5x` the mean min-tile error reduction of fixed-step `graded_chemostat_sp250`.
   - `P3b`: `graded_chemostat_cooled` exceeds `0.10` (`10%`) mean min-tile error reduction within 60 zero-order generations.
4. **P4 (Pinned-thread vectorization benchmark)**:
   - For `n_cells = 512, dim = 256, n_niches = 8, batch_size = 16`, batched tensor evaluation achieves at least `5.0x` speedup over serial per-cell evaluation under both `torch.set_num_threads(1)` and default multi-core CPU threads on Apple M1 Max. (Metal/MPS is recorded if `torch.backends.mps.is_available()` is true in the execution environment; if macOS `sandbox-exec` blocks Metal IOKit, MPS remains explicitly unmeasured in this run.)
5. **P5 (Invariants across all 70 runs)**:
   - Across all 7 arms and 10 seeds, `max_core_drift == 0.0`, `min_watermark_cosine >= 0.999999`, and `max_committed_distance <= 10.0`.

## Amendment, 2026-11-12

Wording of the #118 gap-pay rule and the `graded_chemostat` allocation rule was corrected after review. The pool reset on a best-error improvement of more than `1e-3` is kept. Predictions and the fixed protocol are unchanged.
