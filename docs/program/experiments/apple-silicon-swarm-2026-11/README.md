# Experiment E14: Apple Silicon Micro-Swarm and the PR #118 Convergence

Status: Complete record, final seeded run of 2026-11-11.
Harness: `weft/runtime/mac/swarm_loom.py`
Runner: `run_e14.py` (this folder)
Raw data: `results/e14_results.json`
Preregistration and amendments log: `PREREGISTRATION.md`

## How this folder is ordered

| Stage | What | Where | Status |
|---|---|---|---|
| P0 | E14 ideas alone: subspace + horizontal transfer Beta vs Paper 1 blind Beta, 512 cells on MPS | `probe/` | Complete, 10 seeds. HGT Beta 70.6% of wins vs 0%, error falls 10.8x faster |
| E14 first build | `swarm_loom.py` with three arms | not kept | Withdrawn. The champion cell got a gradient step (amendment A1). Raw data was overwritten and never committed |
| E14 final | Zero-order E14 arms plus the PR #118 convergence arm | this README | Complete, 10 seeds, results below |

The pure E14 arms (`paper1_blind`, `hgt_isolated`, `hgt_foraging`) and the convergence arm (`dissipative_chemostat`) ran in the same seeded run, so they compare directly.

## Result

Three of five preregistered hypotheses held (H-S2, H-S3, H-S5). Two failed: H-S1 (4.55x speedup on the recorded run, threshold 5.0x) and H-S4 (`hgt_foraging` still had 2 to 6 idle cells per seed). The exploratory arm `dissipative_chemostat`, which adds the PR #118 L2 laws, ended coasting completely (0 idle cells in all 10 seeds). It also reduced error 27% less than `hgt_foraging`.

All four arms are zero-order: they use forward error evaluations only. An earlier build gave the champion cell an analytic gradient step. Its numbers (0.77 error reduction) are withdrawn. See amendment A1.

## Preregistered verdicts

| Hypothesis | Threshold | Observed (seeds 0 to 9, MPS) | Verdict |
|---|---|---|---|
| H-S1 MPS speedup, 512 cells x 256 dim, 8 tiles + C2 gate | >= 5.0x vs serial CPU | 4.55x (12.61 ms MPS vs 57.32 ms serial CPU) | FAILED |
| H-S2 Beta win share | < 0.05 blind, > 0.50 `hgt_foraging` | 0.000 blind, 0.907 `hgt_foraging` | HELD |
| H-S2 error reduction | >= 3.0x blind | 33.0x (0.0559 vs 0.0017) | HELD |
| H-S3 niche coverage | median 1.0 | 1.0 (8 of 8 tiles) | HELD |
| H-S3 specialization entropy | median >= 2.5 bits | 2.973 bits mean (`hgt_isolated` 0.0) | HELD |
| H-S4 coasting in `hgt_foraging` | 0 idle cells | mean 4.1, max 6 of 256 | FAILED |
| H-S5 invariants, all 40 runs | drift 0, cosine >= 0.999999, distance <= 10 | drift 0.000000, cosine 1.000000, max distance 8.28 | HELD |

H-S1 is marginal, not a clean miss. The same benchmark code measured 10.03x, 5.42x, 5.03x and 4.55x across four runs on the M1 Max. MPS time held steady at 11.2 to 12.6 ms. Serial CPU time swung from 57 to 113 ms. The speedup depends on CPU load at run time, so it is not a robust 5x. The single-tile batched matmul probe (0.88 ms vs 10.70 ms, 12.2x) is a different, smaller workload.

## Exploratory results (added after data collection)

| Test | Observed | Note |
|---|---|---|
| X-1 coasting in `dissipative_chemostat` | 0 idle cells in all 10 seeds | Both Weismann gate variants gave 0 (amendment A4) |
| X-2 error reduction, chemostat vs blind | 24.1x (0.0410 vs 0.0017) | 27% below `hgt_foraging` |

## All arms, means over 10 seeds

`n_cells = 256`, `dim = 128`, `n_niches = 8`, 60 generations, Apple Silicon MPS.

| Metric | `paper1_blind` | `hgt_isolated` | `hgt_foraging` | `dissipative_chemostat` |
|---|---|---|---|---|
| Beta win share | 0.000 | 0.838 | 0.907 | 0.918 |
| Error reduction (1 - min tile ratio) | 0.0017 | 0.0616 | 0.0559 | 0.0410 |
| Niche coverage | 0.125 | 0.125 | 1.000 | 1.000 |
| Shannon entropy (bits, max 3.0) | 0.000 | 0.000 | 2.973 | 2.952 |
| Idle survivors (of 256) | 173.3 | 0.7 | 4.1 | 0.0 |
| Apoptosis recolonizations | 0.0 | 0.0 | 117.0 | 134.9 |
| Spore births (Law 2c) | 0.0 | 0.0 | 0.0 | 66.0 |
| Max core drift | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Min watermark cosine | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| Max committed distance | 2.46 | 7.63 | 8.23 | 8.28 |

Idle cells per seed in `hgt_foraging`: 6, 3, 4, 3, 3, 3, 6, 6, 5, 2.

## What the comparison shows

`hgt_foraging` and `dissipative_chemostat` share the same mutation operator. They differ only in the three L2 laws, so comparing them isolates what PR #118 adds inside a tensor swarm.

1. Law 2a (Weismann gate) closes a rent loophole. In `hgt_foraging`, a few cells start close enough to a tile to collect top-K bounty every generation without ever adapting. In `dissipative_chemostat`, bounty only banks for cells with at least one accepted update. Unadapted cells starve, die and get replaced. Idle survivors fell from 4.1 to 0.0.
2. The price is error reduction. Recolonization rose from 117 to 135 per run, and half the replacements are spores reset to `W0`. Restarting cells throws away progress, so the mean min-tile error reduction fell from 0.0559 to 0.0410.
3. Law 2b (chemostat flux and gap-potentiated payout) did not get a fair test here. All 8 tiles have the same difficulty (rank-4 targets at equal norm). Law 2b exists to pull cells toward hard, stalled tiles, so its benefit can only show on tiles of graded difficulty. That is the E15 test.
4. `hgt_isolated` posts the highest error reduction because all 256 cells work on tile 0. The metric takes each cell's best tile, so a one-tile colony scores well while covering 1 of 8 niches.

## Limits

- Error reduction is small in absolute terms: 4 to 6% in 60 zero-order generations.
- Benchmark 3 compares CPU and MPS qualitatively. The two devices draw different random streams, so per-seed values differ.
- Mutation scale (0.012) and flux (`0.5 * tile_bounty`) were set by hand and not swept.

## Reproduce

```bash
python3 -m unittest discover -s weft/runtime/mac -p "test_*.py"
python3 docs/program/experiments/apple-silicon-swarm-2026-11/run_e14.py
```

Runs are deterministic per seed on CPU and on MPS (checked with two identical runs on each).

## Next

1. E15: graded-difficulty tiles (easy to ill-conditioned). Test whether Law 2b moves cells onto the hardest tiles and cuts worst-tile error against `hgt_foraging`. Preregister before running.
2. Sweep spore fraction in Law 2c. Even soma and spore splits may restart too often. A lower spore rate could keep 0 coasting at less cost to error.
3. Rerun H-S1 on an idle machine with pinned CPU threads to settle the 5x question.
