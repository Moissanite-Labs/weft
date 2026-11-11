# Preregistration: Experiment E14 Apple Silicon Micro-Swarm Architecture

Date: 2026-11-10
Status: Preregistered prior to benchmark data collection. Sections "Background" through "Experimental Design and Protocol" are the original text. Changes made after data collection are listed under "Amendments" at the end and are not part of the preregistration.
Harness: `weft/runtime/mac/swarm_loom.py`

## Background

Paper 1 evaluated single-cell lineages using isotropic Gaussian mutation. Lineage Beta used a mutation variance five times larger than Lineage Alpha. In high-dimensional weight spaces, isotropic exploration fails because volume grows exponentially.

Experiment L1 revealed that unconstrained lineages coast. Heirs inherited weights and metabolic budgets but 65 of 70 heirs accepted zero updates.

PR #118 addressed this at the agent layer through L2 Dissipative Heredity laws:
1. Law 2a (Irreversible Soma): Unspent birth energy dissipates without wins.
2. Law 2b (Chemostat Flux): Stalled generations concentrate reward in unharvested tiles.
3. Law 2c (Soma and Spore Division): Alpha refines locally, Beta explores via horizontal transfer.

Experiment E14 translates these causal laws to tensor execution on Apple Silicon Metal Performance Shaders (MPS).

## Preregistered Hypotheses

### H-S1: Batched MPS Acceleration
For colony size `n_cells = 512` and dimension `dim = 256`, batched MPS evaluation per generation achieves at least 5.0x speedup over serial CPU evaluation.

### H-S2: Subspace Mutation and Horizontal Gene Transfer
Across 10 random seeds (0 to 9) with `n_cells = 256`, `dim = 128`, `n_niches = 8`, and 60 generations:
`paper1_blind` yields `beta_win_share < 0.05`.
`hgt_foraging` yields `beta_win_share > 0.50`.
`hgt_foraging` achieves at least 3.0x larger relative error reduction `(1 - error_ratio)` than `paper1_blind`.

### H-S3: Spontaneous Niche Differentiation
Under `hgt_foraging`, median niche coverage across 10 seeds is 1.0 (8 of 8 tiles occupied). Median Shannon specialization entropy is at least 2.5 bits out of 3.0 bits maximum. In contrast, `hgt_isolated` achieves 0.125 coverage and 0.0 bits entropy.

### H-S4: Elimination of Coasting
Under `hgt_foraging` with basal upkeep, `idle_surviving_cells` (cells surviving 60 generations with zero accepted updates) is exactly 0.0 percent. This directly resolves the 92.9 percent coasting rate observed in L1.

### H-S5: Invariant Safety
Across all seeds and modes, `max_core_drift` is 0.0. `min_watermark_cosine` is at least 0.999999. Exactly zero weight commits violate the Frobenius ball invariant `r_invariant = 10.0`.

## Experimental Design and Protocol

Colony parameters:
- `n_cells`: 256 (512 for benchmark 1)
- `dim`: 128 (256 for benchmark 1)
- `n_niches`: 8
- `subspace_rank`: 4
- `r_invariant`: 10.0
- `initial_energy`: 100.0
- `basal_upkeep`: 2.0
- `tile_bounty`: 160.0
- `generations`: 60

Arm definitions:
1. `paper1_blind`: Isotropic Alpha and 5x isotropic Beta without foraging or upkeep.
2. `hgt_isolated`: Horizontal gene transfer toward tile 0 champion without niche foraging.
3. `hgt_foraging`: Full architecture with niche bounty allocation, upkeep, apoptosis, and horizontal gene transfer.

Execution plan:
- Run Benchmark 1 on hardware to test H-S1 (serial CPU vs batched CPU vs batched MPS).
- Run Benchmark 2 over seeds 0 through 9 on MPS across all three arms to evaluate H-S2 through H-S5.
- Run CPU parity verification over seeds 0 and 1.
- Save full raw telemetry to `results/e14_results.json`.

## Amendments (made after data collection, not preregistered)

Logged by `agy-orbit` on 2026-11-10 so readers can tell confirmatory results from exploratory ones.

| # | Change | Why | Effect on claims |
|---|---|---|---|
| A1 | Removed the first-order step on the per-niche champion in `hgt_isolated` and `hgt_foraging`. The first build gave the champion `0.4 * X^T (Y - XW) / batch`, which is an analytic gradient. All arms are now zero-order: they use forward error evaluations only. | Paper 1 Beta is gradient-free. A gradient on the champion, spread to peers through horizontal transfer, makes the comparison unfair. | The first build reported 0.77 error reduction for `hgt_foraging`. The zero-order build reports about 0.05. The first-build numbers are withdrawn. |
| A2 | Raised subspace mutation scale from 0.005 to 0.012 and added a per-cell directional memory (`velocity`, the last accepted delta), passed to peers through the champion. | Without the gradient, 0.005 explored too little to compare arms. | The arm definitions differ from the original text. The scale was not tuned per arm. |
| A3 | Added a fourth arm, `dissipative_chemostat`: the PR #118 L2 laws (Weismann gate, chemostat flux with gap-potentiated payout, soma and spore reseeding). | To test the convergence with PR #118 inside the tensor swarm. | Every result for this arm is exploratory, reported as X-1 and X-2. |
| A4 | Changed the Weismann gate in `dissipative_chemostat` after one full run, from "improved this generation" to "has ever had an accepted update". | The per-generation gate starved cells that were adapting slowly. | Both gate variants gave 0.0 idle cells. The forking-paths risk is noted. |
| A5 | Seeded the global torch RNG in `VectorizedPlasmColony.__init__`. | Before this, mutation noise was unseeded, so per-seed runs could not be reproduced. | The final results come from seeded runs. |
