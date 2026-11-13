# Experiment E15: Graded-Difficulty Chemostat, Spore-Fraction Sweep, and Zero-Order Step Cooling

Status: Complete record, seeded run of 2026-11-11.
Harness: `weft/runtime/mac/swarm_loom.py` (`mode="graded_chemostat"`)
Preregistration: `PREREGISTRATION.md` (committed in `9cedb04` prior to execution)
Runner: `run_e15.py`
Raw data: `results.json`

## Summary

Experiment E15 tested the three open questions from E14 (`docs/program/experiments/apple-silicon-swarm-2026-11/README.md` Next items): graded-difficulty tiles, sweeping the Law 2c spore fraction, and pinned-thread vectorization timing, together with three `graded_chemostat` changes in `swarm_loom.py`: a new unsolved-gap allocation rule and a mass-conserving pool, niche-clean spore velocity reset, and optional zero-order homeostatic step cooling. In the mass-conserving pool, `best_tile_error` is updated with a minimum, the pool grows by `0.5 * tile_bounty * gap_mult` each generation, capped at `8.0 * tile_bounty`, the offer is `min(pool, tile_bounty * gap_mult)`, and the pool is reduced by the unlocked payout. The reward rule, the pool update, and the spore inheritance path changed together, so no outcome in this record isolates reward direction.

Four of eight preregistered prediction clauses held (`P2a`, `P3a`, `P3b`, `P5`) and four failed (`P1a`, `P1b`, `P2b`, `P4`). Both the misses and the wins expose concrete mechanisms:

1. **Why `P1a` failed (zero-order difficulty inversion)**: `P1a` assumed tiles `m = 6, 7` (`rank = 16, 24`, input condition numbers `9.0, 12.0`) would stall hardest. Under zero-order rank-4 probing, the opposite occurred: across every arm, `rank = 1, cond = 1.0` (tile `0`) stalled with the *highest* remaining error (`0.1056` reduction at fixed step `0.012`) because a needle-thin rank-1 target subtends a much smaller solid angle in `96 x 128` weight space than a rank-24 target concentrated along dominant input singular vectors (`0.1583` reduction on tile `7`). The new allocation rule therefore pulled cells onto the *actually* stalled tiles `0..2` (`0.56875` of cells in `graded_chemostat_sp250`, per-seed range `0.09375` to `0.890625`, vs. `0.2836` in `hgt_foraging`), rather than tiles `6..7` (`0.207` vs. `0.346`).
2. **Spore-fraction trade-off (`P2a` held, `P2b` missed by 4 points)**: Law 2a kept `idle_surviving_cells == 0` across all 40 runs of `spore_fraction` in `{0.00, 0.125, 0.25, 0.50}` (`hgt_foraging` mean `0.9`, max `3`). Lowering `spore_fraction` from `0.50` (`0.0514`) to `0.125` (`0.0604`) or `0.00` (`0.0607`) improved mean min-tile error reduction by `18%`, reaching `91.0%` of `hgt_foraging` (`0.0664`), shy of the preregistered `95.0%` bar because Weismann starvation still drives higher turnover (`130.1` vs. `89.5` recolonizations).
3. **Zero-order step cooling breaks the E14 4-6% ceiling (`P3a`, `P3b` held)**: Cooling per-cell mutation scale by `0.90x` on rejected steps and warming by `1.03x` on accepted steps (`mean_step_scale` settling from `0.0120` to `0.00355`) raised mean min-tile error reduction `2.80x` (`0.1636` vs. `0.0585` fixed-step, `2.47x` over `hgt_foraging`) and raised worst-tile error reduction to `0.1742` (`1.77x` over `hgt_foraging`'s `0.0983` and `1.88x` over `dissipative_chemostat`'s `0.0928`) while keeping `0` coasting cells.
4. **Pinned-thread CPU batching (`P4` failed)**: On the committed Apple M1 Max run (`threads = 1`), `torch.matmul(x.unsqueeze(0), w.unsqueeze(1))` ran at `104.7 ms` vs. `64.6 ms` serial (`0.62x`). The serial path in that run timed 32 cells and extrapolated 16x; the batched path timed all 512 cells. That 32-versus-512 working-set gap is a limit on the `0.62x` reading. A later like-for-like timing of all 512 cells on both paths, on a Linux x86_64 host (Intel Xeon, 8 CPUs, CPython 3.13.5, PyTorch 2.15.0+cpu), measured `0.114x` at 1 thread (`76.7 ms` serial vs. `671.3 ms` batched) and `0.467x` at 8 threads (`78.7 ms` vs. `168.5 ms`). The README's cache-thrashing diagnosis, and the sentence that batched speedup requires GPU unified-memory bandwidth, are hypotheses. Multicore and MPS were unmeasured on the committed M1 host (`results.json` records `default_num_threads` 1 and `multicore_1_threads.threads` 1; MPS `available: false`).

## Preregistered Verdicts

Executed on Apple M1 Max (`arm64`, Darwin `27.0.0`, CPython `3.13.16`, NumPy `2.5.3`, PyTorch `2.15.0`, CPU device, seeds `20261121..20261130`, `60` generations). The P4 follow-up timing above is a separate Linux measurement; it does not replace the 70 colony runs.

| Clause | Preregistered threshold | Observed (10-seed mean) | Verdict |
|---|---|---|---|
| `P1a` Hard-tile (`m=6,7`) cell share | `sp250 > hgt_foraging` | `0.207` vs. `0.346` (stalled tiles were `m=0..2`, receiving `0.56875` vs. `0.2836`) | FAILED |
| `P1b` Worst-tile reduction (`0.012` step) | `sp250 > hgt_foraging` and `> dissip` | `0.0951` vs. `0.0983` (`hgt_foraging`), `0.0928` (`dissip`) | FAILED |
| `P2a` Zero coasting across spore sweep | `max_idle == 0` in all `sp*`; `hgt > 0` | `0` max across all 40 `sp*` runs; `hgt_foraging` mean `0.9` (max `3`) | HELD |
| `P2b` Spore sweep recovery | `max(sp125, sp250) > sp500` and `>= 0.95 * hgt` | `0.0604 > 0.0514`, but `0.0604 = 0.910 * 0.0664` (`< 0.95`) | FAILED |
| `P3a` Step cooling ratio | `cooled >= 1.5x sp250` | `0.1636 / 0.0585 = 2.80x` | HELD |
| `P3b` Step cooling magnitude | `cooled > 0.10` | `0.1636` (worst-tile reduction `0.1742`) | HELD |
| `P4` CPU batched vs. serial speedup | `>= 5.0x` on CPU | `0.62x` on the committed M1 run (`104.7 ms` batched vs. `64.6 ms` serial on 1 thread), with the 32-versus-512 working-set gap noted above | FAILED |
| `P5` C1/C2 invariants (all 70 runs) | drift `0`, cos `>= 0.999999`, dist `<= 10` | drift `0.0`, cos `1.0`, max distance `9.60` | HELD |

## All Arms (10-Seed Means)

| Arm | Spore frac | Step | Min-tile red. | Assigned red. | Worst-tile red. | Tile `0` red. | Tile `7` red. | Idle cells | Entropy (bits) | Recolon. |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hgt_foraging` | `0.00` | `0.012` | `0.0664` | `0.1077` | `0.0983` | `0.1060` | `0.1682` | `0.9` | `2.937` | `89.5` |
| `dissipative_chemostat` | `0.50` | `0.012` | `0.0602` | `0.0996` | `0.0928` | `0.1038` | `0.1562` | `0.0` | `2.911` | `97.1` |
| `graded_chemostat_sp000` | `0.00` | `0.012` | `0.0607` | `0.0813` | `0.0968` | `0.1049` | `0.1596` | `0.0` | `1.546` | `130.4` |
| `graded_chemostat_sp125` | `0.125` | `0.012` | `0.0604` | `0.0777` | `0.0954` | `0.1049` | `0.1581` | `0.0` | `1.604` | `130.1` |
| `graded_chemostat_sp250` | `0.25` | `0.012` | `0.0585` | `0.0796` | `0.0951` | `0.1056` | `0.1583` | `0.0` | `1.656` | `130.6` |
| `graded_chemostat_sp500` | `0.50` | `0.012` | `0.0514` | `0.0734` | `0.0952` | `0.1047` | `0.1569` | `0.0` | `1.803` | `130.1` |
| `graded_chemostat_cooled` | `0.25` | cooled (`->0.0036`) | `0.1636` | `0.1745` | `0.1742` | `0.1866` | `0.2414` | `0.0` | `2.289` | `105.5` |

## Limits

- The committed M1 P4 figure compared a 32-cell serial path, extrapolated 16x, with a 512-cell batched path. `run_e15.py` now times all 512 cells on both paths. Multicore and MPS were unmeasured on the M1 host; the Linux follow-up measured 1-thread and 8-thread CPU and left MPS unmeasured. Cache-thrashing and unified-memory explanations remain hypotheses.
- Execution of the 70 colony runs ran inside macOS `sandbox-exec`, which blocks Metal `IOKit` (`torch.backends.mps.is_available() == False`) and POSIX `shm_open`, and required `OMP_NUM_THREADS=1` to avoid dual-`libomp` threadpool contention between NumPy and PyTorch wheels.
- All targets remain synthetic linear maps `Y_m = X_m W*_m` with external output residuals `||X_m W - Y_m||_F`. Removing external `Y*` target supervision is addressed separately in Experiment E16.
- Does not close issue #111.

## Reproduce

```bash
python3 -m unittest discover -s weft/runtime/mac -p "test_*.py"
python3 docs/program/experiments/graded-chemostat-e15-2026-11/run_e15.py
```
