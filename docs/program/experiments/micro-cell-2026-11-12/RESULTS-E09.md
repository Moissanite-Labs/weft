# E09 results: invariant-gated micro-cell organism

- Date: 2026-11-12. Exploratory record on branch `record/micro-cell-2026-11-12`. Zero API credits.
- Companion to issue #142 (arm 1). Arm 2 (TinyStories-2M) by a peer seat.
- Arm: `record/micro-cell-2026-11-12` carries this file, `microcell.py`, `00-DESIGN.md`, `PREREG-E09.md`, and the run logs.
- Naming: E09 and E10 are run labels inside this record. They are not the cards E09 and E10 in `docs/program/experiment-cards.md`.
- Instrument note (2026-11-12, review of PR #143): every log here comes from the pre-fix instrument. It did not reset each cell's previous action `_u` between the task episode, the parent probe and the candidate probes, and its watermark check compared the core `wc` with itself. Scores of different candidates therefore started from different `_u` states. `microcell.py --legacy-u-leak` reproduces these logs; the default now resets `_u` and checks the core against `wc_base`. The corrected instrument has not been rerun for this record.

## Headline

The custom micro-cell does not reliably improve over its own early generations on the 3 seeded runs, and only seed 20261112 has a frozen control. It works mechanically (organisms commit, control arms behave) but the selection rule rewards probe-window episodes, which are not the same distribution as task episodes, so the organism sometimes commits into worse long-horizon behavior and stays there.

## Per-seed results

| Seed | Commits | A first→last | B first→last | frozen A first→last |
|---|---|---|---|---|
| 20261112 | 4 | 26.69 → 27.98 | 26.82 → 31.06 | 26.69 → 26.73 |
| 20261113 | 8 | 34.57 → 27.82 | 30.88 → 30.67 | (not run) |
| 20261114 | 4 | 30.85 → 26.54 | 31.32 → 30.73 | (not run) |

A regressed on 2 of 3 seeds. B was flat-to-slightly-up on all 3. Mean A across seeds, generation 1 to generation 40: 30.700 -> 27.449 (-10.6%). Mean B: 29.675 -> 30.823 (+3.9%). Commits change only the plastic periphery `wp`; the code never writes the core, so core drift is 0 by construction, but the logged `wm_drift` compared `wc` with itself and is not an independent measurement. Watermark cosine is 1.000 in all 40 generations of the 3 learning runs and of the seed-20261112 frozen control.

## Hypothesis read-out vs `PREREG-E09.md`

- H1 (mean return in generations 30 to 40 exceeds generations 0 to 10 by >=20% in >=2 of 3 seeds): FALSIFIED. Mean of generations 31-40 over generations 1-10: seed 20261112 A +1.77%, B +0.59%; seed 20261113 A -0.75%, B -1.13%; seed 20261114 A -9.93%, B -2.04%. No seed reaches 20% on either agent. The registered paired t-test against a seed-matched frozen control was not run (frozen controls exist for seed 20261112 only).
- H2 (>= rev-C matrix organism at gen 40 by 0.3 in >=2 of 3): FALSIFIED. Generation-40 seed means (A and B averaged) against the rev-C generation-40 values printed in PR #141 `RESULTS-E08.md` (37.06/33.41, 28.40/32.00, 24.85/33.18; rev-C was not resimulated here): 29.524, 29.247, 28.637, gaps -5.71, -0.95, -0.38. Zero of three seed means exceed rev-C by 0.3. Per agent, seed 20261114 A is above rev-C (26.540 vs 24.85, +1.69); every other agent is below.
- H3 (commit rate does not drop below 0.5 per active seed by generation 30, `PREREG-E09.md:9`): FALSIFIED. Commits at generations 1-30, A/B: seed 20261112 1/2, seed 20261113 5/3, seed 20261114 1/3, so per-agent rates are 0.03 to 0.17 and any-commit rates are 3/30, 6/30 and 4/30, all below 0.5. Lifetime totals are 4, 8 and 4 commits; seed 20261114 has no commit after generation 8, and seed 20261112 A commits only at generations 3 and 35. The earlier HELD verdict counted total commits, which is not the registered clause.
- H4 (reject rate < 20%): HELD. Zero rejections everywhere.
- H5 (watermark retained): cosine 1.0 in every logged generation, so the cosine part holds. The core-drift part was not measured independently (the check compared `wc` with itself); the code never writes `wc`, so drift is 0 by construction. The corrected script logs `core_drift` against `wc_base`.

## The mechanism, stated plainly

- The commit rule compares probe-window returns computed with t0=1000 (deterministic but different world-phase) to the incumbent probe.
It does not compare against the same-phase real episode.
The organism therefore commits whenever a probe-window comparison favors a candidate even if the long-horizon episode distribution penalizes it.
This is the same kind of selection-horizon mismatch E08 reported on the matrix organism, on identical torus seeds. It is a candidate explanation, not an isolated cause: the `_u` leak described above also changes probe scores between candidates.
- Without that mismatch, the micro-cell's early B movement (26.8 to 31.1) shows the organism can track real field-phase gains when selection happens to agree with long-horizon reward, but it cannot tell when it is wrong, so it undoes its own progress under drift.

## Honest read

- This is a miss on the registered clauses H1, H2 and H3.
- The instrument runs (probe-commit and the periphery drift gate operate), but it leaked `_u` between trials and did not check the core against a baseline. The selection horizon mismatch is a plausible bottleneck; it is not isolated from the `_u` leak in these logs.
- The frozen control (seed 20261112 only) has 0 commits, but its returns are not flat: they move from generation 1 to 2 (A 26.6886 -> 26.7280, B 26.8202 -> 26.8305) and stay constant afterwards. That move comes from the `_u` leak. Under the corrected script the frozen returns are identical in every generation (checked in `test_microcell.py`).

## Next steps recorded, not run

1. The task-horizon selection run is in `RESULTS-E10.md`. Those logs use the same pre-fix instrument as this record (see the instrument note above).
2. Once selection is sound, re-run 3 seeds before any conclusion about capacity scaling. Until then, no claim about whether more capacity helps can be made. The organism is not yet reliably selecting for the task.
3. GRU arm (secondary, H6) not run. Not worth running on a broken selection rule.

## Files

- `logs/seed-a.jsonl` (seed 20261112), `logs/seed-b.jsonl` (20261113), `logs/seed-c.jsonl` (20261114), `logs/frozen-12.jsonl` (C1 frozen, seed 20261112).
- Stdout: `logs/main-12.out` is the stdout of the seed-20261112 learning run (there is no `seed-a.out`), `logs/seed-b.out`, `logs/seed-c.out`, `logs/c1-12.out`. The final `wrote /Users/...` line, an absolute path on the author's machine, was removed from each stdout log on 2026-11-12; no other line changed.
- Reproduce: `python3 microcell.py seed-a --seed 20261112 --protocol e09 --legacy-u-leak` (and `--control C1` for the frozen run). The E08 modules are vendored in `vendor_e08/` with pinned hashes. Offline checks: `python3 -m unittest discover -s docs/program/experiments/micro-cell-2026-11-12 -p 'test_*.py'`.
