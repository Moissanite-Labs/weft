# Experiment E16: Endogenous Recurrent Markov-Blanket Cells Without External Target Supervision

Status: Complete record, seeded run of 2026-11-11 on Apple M1 Max. The verdicts and tables below are that M1 record. A pinned Linux x86_64 rerun on 2026-11-12 flips P2a (and P4) and is reported under Host scope.
Interfaces exercised: `weft/runtime/plasm` (C1 watermark), `weft/runtime/invariants` (C2 gate and tension bound), `weft/runtime/telemetry/frame64` (I1 64-byte frame).
Preregistration: `PREREGISTRATION.md` (committed in `864e7fd` prior to execution). The executable runner arrived in `048db94d` four minutes later. Dated deviations are listed under Amendments in that file.
Runner: `run_e16.py`
Raw data: `results.json` (M1 Max, 2026-11-11). Linux companion: `results-linux-x86_64-2026-11-12.json`.

## Summary

Experiment E16 removes external ground-truth matrix targets (`Y* = X W*`) and harness-held symbolic belief variables. Sixty-four cells, each owning a single `32 x 32` weight matrix `W_i` (`core_rows = 8` frozen with the deterministic C1 provenance watermark, gated by `verify_weight_update_safety_ex` at `R = 12.0` and `verify_tension_bound` at `TENSION_MAX = 85.0`) and a `32`-float recurrent activation vector `h_i(t)`, forage across a periodic ring `[0, 1)` populated by drifting nutritive (`+1`) and toxic (`-1`) patches that have identical static unsigned concentration `C(x)`. Halfway through each `40`-generation run (`generation 20`), spatial gradient and probe-echo polarities invert.

On the committed M1 record, four of eight preregistered prediction clauses held (`P1a`, `P2a`, `P5a`, `P5b`) and four compound clauses failed on one sub-clause (`P1b`, `P2b`, `P3`, `P4`):

1. **Endogenous survival without external `Y*` (`P1a` held)**: `full_endogenous` maintained `17.36` mean colony energy vs. `14.23` in unselected `blind_drift` (`+22.0%`), doubled nutrient-vs-toxin ingestion selectivity (`0.3307` vs. `0.1491`), and reduced C2 tension excisions (`4,176` vs. `4,995`).
2. **Issue #75 `< 15.0` tension band reachability vs. C2 excision cost (`P1b` split, failed overall)**: `open_loop_tension_75` (`20.0 + 2.5 * ||W - W0||_F`) recorded `0` of `25,600` cell-generations below `15.0` and `0` excisions (`max <= 50.0`), whereas `full_endogenous` visited all three I3 bands (`5,501` in `< 15.0`, `7,540` in `[15.0, 35.0]`, `12,559` in `> 35.0`) and higher food selectivity (`0.3307` vs. `0.3006`). `open_loop_tension_75` posted slightly higher mean standing energy (`17.84` vs. `17.36`) because coupling visceral starvation above `85.0` to C2 excision (`energy = 0`) culled `4,176` stressed cells early instead of letting them coast. Tension and excision tallies include dead cells. Sigma resets to `init_sigma` at every generation start, so the tension controller lasts for the three bouts inside a generation. The probe echo multiplies the signed field at the current tick.
3. **Recurrent memory lesion (`P2a` held on M1; failed on pinned Linux)**: On the M1 record, zeroing recurrent feedback (`memory_lesion`) degraded both food selectivity (`0.3307` to `0.3052`) and colony energy (`17.36` to `17.01`). A pinned Linux rerun flips this clause: selectivity `0.3043` vs. `0.3330` and energy `16.91` vs. `17.48`, with `memory_lesion` ahead on both. See Host scope. Disabling the paid exteroceptive probe (`probe_lesion`, saving `0.03` ATP/tick) raised M1 energy to `17.59` and selectivity to `0.3337` (`P2b` failed). Intact recurrent memory and the interoceptive toxin and energy channels were available in both arms; a follow-up that removes those channels is what would test a taste-aversion mechanism.
4. **Efference copy and patch occupancy (`P3` split, failed overall)**: On the M1 record, removing motor efference copy (`reafference_lesion`) lowered mean energy (`17.36` to `17.04`) and food selectivity (`0.3307` to `0.3030`), and raised C2 starvation excisions (`4,176` to `4,616`). Patch-residence was `0.325672` for `full_endogenous` and `0.325683` for `reafference_lesion`; the lesion arm is higher by `1.09e-5`. On pinned Linux the lesion arm is also ahead on energy (`17.46` vs. `16.91`) and residence (`0.339333` vs. `0.328050`).
5. **Paid signaling (`P4` split, failed overall on M1)**: Charging `c_sig = 0.05` ATP lowered mean signal amplitude relative to `free_signaling` (`0.2863` vs. `0.2951`), but `40` generations under `0.03` budding jitter left referential valence correlation near noise (`|corr| = 0.059` vs. `0.069`). The same clause holds on the pinned Linux rerun (amplitude `0.2848` vs. `0.3086` and `|corr|` `0.1049` vs. `0.1004`). Signal amplitude is averaged over live cells.
6. **Baldwinian vs. Lamarckian crossover under generation-20 receptor inversion (`P5a` held on the 10-seed mean)**: In the stationary pre-shock phase (`generations 10..19`), `lamarckian_soma` outperformed `full_endogenous` (`18.19` vs. `16.88`). After the shock, `full_endogenous` recovered `+2.53` energy (`16.74` to `19.27`) vs. `+1.37` (`16.55` to `17.92`) in `lamarckian_soma` (`1.85x`). The ten per-seed recovery deltas (`full` minus `lamarckian`) are `+17.81`, `+4.25`, `+0.38`, `-2.50`, `+3.55`, `-3.28`, `-3.75`, `-9.09`, `-0.03`, `+4.26`; five of ten seeds are positive. Dropping seed `20261131`, where `lamarckian_soma` falls to `-15.69`, flips the means: `full` `+2.58` vs. `lamarckian` `+3.27`. The late-run rise is shared: `memory_lesion`, `probe_lesion`, `reafference_lesion`, and `free_signaling` have recovery means from `+2.49` to `+2.72`. These arms also differ as one package: the child called Baldwinian takes `0.35` of the parent's adult soma into the germline, `init_sigma` is `0.14` vs. `0.025`, and lamarckian birth noise is halved. A follow-up that varies the inheritance rule alone is what would support an inheritance claim.
7. **C1/C2/I1 record across all 80 M1 runs (`P5b` held, scoped)**: Frozen rows stay frozen and the watermark reads back (`max_core_drift == 0.0`, `min_watermark_cosine == 0.99999988`). Feeding `z[:, 0:8]` is what would let the core affect behavior; this runner leaves those columns at zero, so the frozen rows multiply zeros. The M1 runner projected each somatic bout onto the `R = 12` ball and called `verify_weight_update_safety_ex` only at reproduction (`12,800` accepts per selection arm). Observed `max_committed_distance` was `12.00000286`, and the M1 verdict used a `1e-5` tolerance against the preregistered `<= 12.0` check. The current runner routes somatic commits through the same gate; a rejecting gate leaves `W` and the unused budget unchanged. On the pinned Linux rerun of that runner, selection arms accepted all `76,800` somatic writes (or all but one or eight), and `max_committed_distance` was `12.0`. Each generation packs an I1 frame through `pack_uniform_frame_64b` and counts a packet only when the decoded floats match the packed values. Energy CV, mean energy, toxin, sigma, and polarity stay beside the frame.

## Preregistered Verdicts (Apple M1 Max record, 2026-11-11)

Executed on Apple M1 Max (`arm64`, Darwin `27.0.0`, CPython `3.13.16`, NumPy `2.5.3`, PyTorch `2.15.0`, seeds `20261131..20261140`, `8` arms x `10` seeds = `80` runs, `30.2` s total). Thread count and deterministic algorithms were unset on that host.

| Clause | Preregistered threshold | Observed (10-seed mean / total) | Verdict |
|---|---|---|---|
| `P1a` Endogenous vs. blind drift | `full > blind` (`gen 10..19` and all `40`) | `16.88 > 14.06` (`10..19`); `17.36 > 14.23` (all `40`) | HELD |
| `P1b` Visceral tension vs. `#75` open-loop | `open_loop` `<15` == `0`; `full` visits all 3 bands and higher energy | `0` vs. `5,501 / 7,540 / 12,559` bands (held), but energy `17.36 < 17.84` due to `4,176` vs. `0` C2 excisions | FAILED |
| `P2a` Recurrent memory lesion | `full > memory_lesion` (selectivity and energy) | selectivity `0.3307 > 0.3052`; energy `17.36 > 17.01` | HELD (M1 only) |
| `P2b` Epistemic probe lesion | `full > probe_lesion` (selectivity and energy) | selectivity `0.3307` vs. `0.3337`; energy `17.36` vs. `17.59` | FAILED |
| `P3` Corollary-discharge lesion | `full > reafference_lesion` (energy and residence) | energy `17.36 > 17.04` (held; selectivity `0.3307 > 0.3030`), residence `0.325672` vs. `0.325683` | FAILED |
| `P4` Paid vs. free signaling | `paid_amp < free_amp` and `paid_corr > free_corr` | amp `0.2863 < 0.2951` (held), `|corr|` `0.059 < 0.069` | FAILED |
| `P5a` Post-shock recovery (`gen 20` flip) | `baldwinian_delta > lamarckian_delta` | `+2.534 > +1.373` (`1.85x`; post-shock energy `19.27` vs. `17.92`); five of ten seeds; leave-one-seed flip on `20261131` | HELD (mean) |
| `P5b` C1/C2/I1 invariants (all 80 runs) | drift `0`, cos `>= 0.999999`, dist `<= 12`, `400` frames/arm | drift `0.0`, cos `0.99999988`, max dist `12.000003` with a `1e-5` tolerance, `400/400` frames/arm (length-only check in the M1 runner) | HELD (scoped) |

## All Arms (10-Seed Means, M1 record)

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

## Host scope

The committed verdicts are the M1 file. Pinning the runner to one CPU thread and `torch.use_deterministic_algorithms(True)` and rerunning all 80 colonies on Linux x86_64 (Intel Xeon, Linux `6.12.113+`, CPython `3.13.5`, NumPy `2.5.4`, PyTorch `2.15.0+cpu`, `54.2` s) does not reproduce those dynamics.

| Clause | M1 record | Pinned Linux x86_64, 2026-11-12 |
|---|---|---|
| `P1a` | HELD (`16.88 > 14.06` pre-shock; `17.36 > 14.23` all 40) | HELD (`15.70 > 14.09` pre-shock; `16.91 > 14.21` all 40) |
| `P2a` | HELD (selectivity `0.3307 > 0.3052`; energy `17.36 > 17.01`) | FAILED (selectivity `0.3043 < 0.3330`; energy `16.91 < 17.48`) |
| `P3` | FAILED (energy `17.36 > 17.04`; residence `0.325672 < 0.325683`) | FAILED (energy `16.91 < 17.46`; residence `0.328050 < 0.339333`) |
| `P4` | FAILED (amp held; `|corr|` `0.059 < 0.069`) | HELD (amp `0.2848 < 0.3086`; `|corr|` `0.1049 > 0.1004`) |
| `P5a` | HELD on the 10-seed mean (`+2.53` vs. `+1.37`) | HELD on the 10-seed mean (`+3.10` vs. `+0.89`) |
| `P5b` | HELD, scoped; max dist `12.00000286` | HELD, scoped; max dist `12.0`; `76,800/76,800` somatic gate accepts on `full_endogenous` |

Full pre-shock energy is `16.88` on M1 and `15.70` here. An earlier unpinned Linux host (NumPy `2.5.4`) flipped `P3` to held. A later 4-thread Linux re-check matched this pinned run on `P2a` and `P3`.

The Linux file was produced by the current runner, which routes somatic commits through `verify_weight_update_safety_ex` and averages signal amplitude over live cells. A same-host rerun of the original projection-only runner gave identical `full_endogenous`, `memory_lesion`, `reafference_lesion`, and `lamarckian_soma` headline energy, selectivity, residence, and recovery means. Gating changed `max_committed_distance` from `12.00000286` to `12.0` and moved `blind_drift` (18,767 somatic rejects across 10 seeds) and a few other arms slightly. Signal-amplitude means differ by about `8e-4` on `full_endogenous` because dead cells are excluded.

## Limits

- **Toy environment**: A 1D periodic ring with 8 Gaussian patches and `32 x 32` recurrent cells demonstrates basic homeostatic foraging, interoceptive memory, and plastic inheritance, at this scale.
- **Host-specific clauses**: `P2a` and `P4` change verdict between the M1 record and the pinned Linux rerun. `P3` fails on both, for a larger margin on Linux. Treat those clauses as M1-scoped unless a later run is bit-reproducible across hosts.
- **Inheritance package**: `P5a` compares the 0.35 adult-soma share, the 0.14 vs. 0.025 sigma, and the halved lamarckian birth noise together. A follow-up that varies the inheritance rule alone is what would support an inheritance claim.
- **C1 scope**: Frozen rows stay frozen and the watermark reads back. Feeding `z[:, 0:8]` is what would let the core affect behavior.
- **Interoceptive shortcut**: To isolate active epistemic probing (`P2b`), toxic damage must be delayed across multiple ticks so immediate post-ingestive `toxin` sensing (`z[:, 15]`) cannot substitute for pre-ingestive probing.
- **Signaling horizon**: Evolving referential signaling (`P4`) likely requires non-overlapping kin groups or delayed toxin lethality where self-tasting is fatal and neighbor warnings carry high marginal survival value.
- Does not modify `weft/runtime/plasm/plasm.py` (which has frozen Paper 1 `--check` baselines) and does not close issue #111.

## Reproduce

The committed `results.json` is the M1 record. Rerunning on another host writes a new file and will not match those numbers.

```bash
python3 docs/program/experiments/endogenous-cells-e16-2026-11/run_e16.py
```

The runner pins one CPU thread and enables deterministic PyTorch algorithms. To leave the committed M1 file untouched, set `WEFT_E16_RESULTS` to another path.
