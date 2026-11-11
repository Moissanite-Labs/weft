# Probe P0: E14 ideas alone, before the swarm loom

Status: Complete. Run first on 2026-11-10 (seed 0), rerun the same day over seeds 0 to 9.
Script: `probe_p0.py`
Raw data: `results/p0_results.json`

## Result

Paper 1's isotropic Beta won 0 of about 94,000 trials across 10 seeds. Beta using rank-4 subspace mutation plus horizontal transfer won 70.6% of accepted updates and cut error 10.8x faster. Every seed showed the same pattern. This probe is what led to building `swarm_loom.py` and E14.

## Question

In a batched colony on Apple Silicon MPS, can a Beta lineage win if it mutates in a small subspace and copies part of the best peer in its niche? Paper 1's Beta uses 5x Alpha's isotropic noise and loses.

## Setup

| Parameter | Value |
|---|---|
| Cells | 512 (4 niches of 128) |
| Matrix | 256 x 256, top 64 rows frozen |
| Targets | One random 256 x 256 map per niche, 32 inputs each |
| C2 radius | 15.0 (Frobenius distance from start) |
| Generations | 100 |
| Alpha | isotropic noise, scale 0.005 |
| Blind Beta | isotropic noise, scale 0.025 (5x Alpha) |
| HGT Beta | `0.35 * (W_best - W) + 0.008 * U @ V`, rank 4 |
| Device | Apple M1 Max, MPS, torch 2.15.0 |

Zero-order: the probe uses forward errors only. The best cell in each niche has `W_best - W = 0`, so its Beta move is the low-rank term alone. No gradient enters anywhere.

## Results, seeds 0 to 9

| Seed | Blind: Alpha wins | Blind: Beta wins | Blind: error ratio | HGT: Alpha wins | HGT: Beta wins | HGT: error ratio |
|---|---|---|---|---|---|---|
| 0 | 9,738 | 0 | 0.9974 | 3,933 | 8,941 | 0.9722 |
| 1 | 9,546 | 0 | 0.9975 | 3,560 | 8,947 | 0.9732 |
| 2 | 9,317 | 0 | 0.9975 | 3,454 | 8,503 | 0.9731 |
| 3 | 9,562 | 0 | 0.9975 | 3,038 | 9,071 | 0.9728 |
| 4 | 9,455 | 0 | 0.9975 | 3,187 | 8,607 | 0.9737 |
| 5 | 9,417 | 0 | 0.9975 | 4,831 | 8,102 | 0.9752 |
| 6 | 9,358 | 0 | 0.9975 | 3,061 | 8,948 | 0.9729 |
| 7 | 9,602 | 0 | 0.9975 | 3,916 | 9,509 | 0.9724 |
| 8 | 9,384 | 0 | 0.9975 | 3,366 | 8,734 | 0.9722 |
| 9 | 9,351 | 0 | 0.9975 | 4,314 | 8,381 | 0.9746 |

| Summary | Blind Beta | HGT Beta |
|---|---|---|
| Beta share of accepted updates | 0.0% | 70.6% (range 62.6% to 74.9%) |
| Error reduction (1 - ratio) | 0.0025 | 0.0268 |
| Speed vs blind | 1x | 10.8x (range 10.1x to 11.2x per seed) |

Seed 0 matches the original run exactly. Each seed takes about 4.5 seconds for both arms.

## Why blind Beta loses

The frozen-core mask leaves 49,152 free parameters. Isotropic noise scaled 5x raises the useful step along the descent direction 5x. It also raises the curvature penalty across all 49,152 directions 25x, so at this dimension the bigger step nearly always makes things worse.

HGT Beta moves toward a peer that already scores better and explores in a rank-4 subspace with about 2,000 degrees of freedom. The design note works through the math in section 2.2.

## Limits

- One fixed task family (random linear maps) and one size. No sweep of rank, transfer rate or noise scale.
- Transfer copies from the niche's best cell, so diversity within a niche shrinks over time. The probe does not measure that.
- Absolute progress is small: 2.7% error reduction in 100 generations.
- The arms share one RNG stream in a fixed order (blind, then HGT), as in the original command.

## Reproduce

```bash
python3 docs/program/experiments/apple-silicon-swarm-2026-11/probe/probe_p0.py              # seed 0
python3 docs/program/experiments/apple-silicon-swarm-2026-11/probe/probe_p0.py --seeds 0-9 --out results/p0_results.json
```
