# Experiment E16: Endogenous Recurrent Markov-Blanket Cells Without External Target Supervision

Status: Complete record, seeded run of 2026-11-11.
Interfaces exercised: `weft/runtime/plasm` (C1 watermark), `weft/runtime/invariants` (C2 gate and tension bound), `weft/runtime/telemetry/frame64` (I1 64-byte frame).
Preregistration: `PREREGISTRATION.md` (committed in `864e7fd` prior to execution)
Runner: `run_e16.py`
Raw data: `results.json`

## Summary

Experiment E16 removes external ground-truth matrix targets (`Y* = X W*`) and harness-held symbolic belief variables. Sixty-four cells, each owning a single `32 x 32` weight matrix `W_i` (`core_rows = 8` frozen with the deterministic C1 provenance watermark, gated by `verify_weight_update_safety_ex` at `R = 12.0` and `verify_tension_bound` at `TENSION_MAX = 85.0`) and a `32`-float recurrent activation vector `h_i(t)`, forage across a periodic ring `[0, 1)` populated by drifting nutritive (`+1`) and toxic (`-1`) patches that have identical static unsigned concentration `C(x)`. Halfway through each `40`-generation run (`generation 20`), spatial gradient and probe-echo polarities invert.

Four of eight preregistered prediction clauses held (`P1a`, `P2a`, `P5a`, `P5b`) and four compound clauses failed on one sub-clause (`P1b`, `P2b`, `P3`, `P4`):

1. **Endogenous survival without external `Y*` (`P1a` held)**: `full_endogenous` maintained `17.36` mean colony energy vs. `14.23` in unselected `blind_drift` (`+22.0%`), doubled nutrient-vs-toxin ingestion selectivity (`0.3307` vs. `0.1491`), and reduced C2 tension excisions (`4,176` vs. `4,995`).
2. **Issue #75 `< 15.0` tension band reachability vs. C2 excision cost (`P1b` split — failed overall)**: `open_loop_tension_75` (`20.0 + 2.5 * ||W - W0||_F`) recorded `0` of `25,600` cell-generations below `15.0` and `0` excisions (`max <= 50.0`), whereas `full_endogenous` visited all three I3 bands (`5,501` in `< 15.0`, `7,540` in `[15.0, 35.0]`, `12,559` in `> 35.0`) and higher food selectivity (`0.3307` vs. `0.3006`). However, `open_loop_tension_75` posted slightly higher mean standing energy (`17.84` vs. `17.36`) because coupling visceral starvation above `85.0` to C2 excision (`energy = 0`) culled `4,176` stressed cells early instead of letting them coast.
3. **Recurrent interoceptive taste-aversion made active probing redundant (`P2a` held, `P2b` failed)**: Zeroing recurrent feedback (`memory_lesion`) degraded both food selectivity (`0.3307 -> 0.3052`) and colony energy (`17.36 -> 17.01`), confirming that cross-tick state in `h_i(t)` is causally used. Disabling the paid exteroceptive probe (`probe_lesion`, saving `0.03` ATP/tick) did *not* hurt (`17.59` energy, `0.3337` selectivity): because somatic toxin load (`z[:, 15]`) and energy deviation (`z[:, 14]`) remained observable, intact recurrent memory solved food-vs-poison discrimination via post-ingestive taste aversion without paying probe cost.
4. **Efference copy cut locomotor waste and excisions without changing patch occupancy (`P3` split — failed overall)**: Removing motor efference copy (`reafference_lesion`) lowered mean energy (`17.36 -> 17.04`), degraded food selectivity (`0.3307 -> 0.3030`), and raised C2 starvation excisions (`4,176 -> 4,616`), while patch-residence rate tied (`0.3257` vs. `0.3257`).
5. **Paid signaling reduced chatter volume without evolving referential correlation (`P4` split — failed overall)**: Charging `c_sig = 0.05` ATP lowered mean signal amplitude relative to `free_signaling` (`0.2863` vs. `0.2951`), confirming metabolic pressure against constant emission, but `40` zero-order generations under `0.03` budding jitter were insufficient to evolve referential valence correlation (`|corr| = 0.059` vs. `0.069`, both near noise).
6. **Baldwinian vs. Lamarckian crossover under generation-20 receptor inversion (`P5a` held)**: In the stationary pre-shock phase (`generations 10..19`), `lamarckian_soma` (copying adult `W` with low newborn variance `0.025`) outperformed `full_endogenous` (`18.19` vs. `16.88`). After the generation-20 receptor inversion shock, `full_endogenous` (inheriting assimilated germline priors `W_germ` with wiped newborn state and fresh developmental variance `0.14`) recovered `+2.53` energy (`16.74 -> 19.27`) vs. `+1.37` (`16.55 -> 17.92`) in `lamarckian_soma` (`1.85x` larger recovery).
7. **C1/C2/I1 conformance across all 80 runs (`P5b` held)**: `max_core_drift == 0.0`, `min_watermark_cosine == 0.99999988`, `max_committed_distance <= 12.0` (`1e-5` float32 tolerance), and `3,200 / 3,200` emitted 64-byte `frame64` packets round-tripped cleanly.

## Preregistered Verdicts

Executed on Apple M1 Max (`arm64`, Darwin `27.0.0`, CPython `3.13.16`, NumPy `2.5.3`, PyTorch `2.15.0`, seeds `20261131..20261140`, `8` arms x `10` seeds = `80` runs, `30.2` s total).

| Clause | Preregistered threshold | Observed (10-seed mean / total) | Verdict |
|---|---|---|---|
| `P1a` Endogenous vs. blind drift | `full > blind` (`gen 10..19` and all `40`) | `16.88 > 14.06` (`10..19`); `17.36 > 14.23` (all `40`) | HELD |
| `P1b` Visceral tension vs. `#75` open-loop | `open_loop` `<15` == `0`; `full` visits all 3 bands & higher energy | `0` vs. `5,501 / 7,540 / 12,559` bands (held), but energy `17.36 < 17.84` due to `4,176` vs. `0` C2 excisions | FAILED |
| `P2a` Recurrent memory lesion | `full > memory_lesion` (selectivity and energy) | selectivity `0.3307 > 0.3052`; energy `17.36 > 17.01` | HELD |
| `P2b` Epistemic probe lesion | `full > probe_lesion` (selectivity and energy) | selectivity `0.3307` vs. `0.3337`; energy `17.36` vs. `17.59` (interoceptive taste-aversion bypassed probe) | FAILED |
| `P3` Corollary-discharge lesion | `full > reafference_lesion` (energy and residence) | energy `17.36 > 17.04` (held; selectivity `0.3307 > 0.3030`), residence tied `0.3257` vs. `0.3257` | FAILED |
| `P4` Paid vs. free signaling | `paid_amp < free_amp` and `paid_corr > free_corr` | amp `0.2863 < 0.2951` (held), `|corr|` `0.059 < 0.069` (neither evolved referential code) | FAILED |
| `P5a` Post-shock recovery (`gen 20` flip) | `baldwinian_delta > lamarckian_delta` | `+2.534 > +1.373` (`1.85x`; post-shock energy `19.27` vs. `17.92`) | HELD |
| `P5b` C1/C2/I1 invariants (all 80 runs) | drift `0`, cos `>= 0.999999`, dist `<= 12`, `400` frames/arm | drift `0.0`, cos `0.99999988`, max dist `12.000003`, `400/400` frames/arm | HELD |

## All Arms (10-Seed Means)

| Arm | Energy (all 40) | Pre-shock (`10..19`) | Shock (`20..22`) | Post-shock (`30..39`) | Recovery delta | Food selectivity | Signal amp | `|corr|` | `<15` / `[15,35]` / `>35` | Excisions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| `full_endogenous` | `17.36` | `16.88` | `16.74` | `19.27` | `+2.53` | `0.3307` | `0.2863` | `0.059` | `5501 / 7540 / 12559` | `4176` |
| `blind_drift` | `14.23` | `14.06` | `14.28` | `14.14` | `-0.14` | `0.1491` | `0.3362` | `0.008` | `3105 / 7614 / 14881` | `4995` |
| `open_loop_tension_75` | `17.84` | `17.30` | `17.75` | `19.83` | `+2.07` | `0.3006` | `0.2932` | `0.076` | `0 / 12967 / 12633` | `0` |
| `memory_lesion` | `17.01` | `16.49` | `16.37` | `18.86` | `+2.49` | `0.3052` | `0.2993` | `0.088` | `5448 / 7392 / 12760` | `4310` |
| `probe_lesion` | `17.59` | `16.93` | `17.46` | `20.01` | `+2.55` | `0.3337` | `0.2683` | `0.055` | `5576 / 7580 / 12444` | `3983` |
| `reafference_lesion` | `17.04` | `16.41` | `16.34` | `19.06` | `+2.72` | `0.3030` | `0.2785` | `0.056` | `5505 / 7185 / 12910` | `4616` |
| `free_signaling` | `17.86` | `16.51` | `17.49` | `20.17` | `+2.67` | `0.3405` | `0.2951` | `0.069` | `5945 / 7454 / 12201` | `4185` |
| `lamarckian_soma` | `17.34` | `18.19` | `16.55` | `17.92` | `+1.37` | `0.3109` | `0.2583` | `0.141` | `6304 / 7703 / 11593` | `4378` |

## Limits

- **Toy environment**: A 1D periodic ring with 8 Gaussian patches and `32 x 32` recurrent cells demonstrates basic homeostatic foraging, interoceptive memory, and Baldwinian plasticity, not sentience or general cognition.
- **Interoceptive shortcut**: To isolate active epistemic probing (`P2b`), toxic damage must be delayed across multiple ticks so immediate post-ingestive `toxin` sensing (`z[:, 15]`) cannot substitute for pre-ingestive probing.
- **Signaling horizon**: Evolving referential signaling (`P4`) likely requires non-overlapping kin groups or delayed toxin lethality where self-tasting is fatal and neighbor warnings carry high marginal survival value.
- Does not modify `weft/runtime/plasm/plasm.py` (which has frozen Paper 1 `--check` baselines) and does not close issue #111.

## Reproduce

```bash
python3 docs/program/experiments/endogenous-cells-e16-2026-11/run_e16.py
```
