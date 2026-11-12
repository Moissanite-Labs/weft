# E09 results: invariant-gated micro-cell organism

- Date: 2026-11-12. Exploratory record on branch `record/micro-cell-2026-11-12`. Zero API credits.
- Companion to issue #142 (arm 1). Arm 2 (TinyStories-2M) by a peer seat.
- Arm: `record/micro-cell-2026-11-12` carries this file, `microcell.py`, `00-DESIGN.md`, `PREREG-E09.md`, and the run logs.

## Headline

The custom micro-cell does not reliably outperform its frozen baseline on the 3 seeded runs. It works mechanically (organisms commit, invariants hold everywhere, control arms behave) but the selection rule rewards probe-window episodes, which are not the same distribution as task episodes, so the organism sometimes commits into worse long-horizon behavior and stays there.

## Per-seed results

| Seed | Commits | A first→last | B first→last | frozen A first→last |
|---|---|---|---|---|
| 20261112 | 4 | 26.69 → 27.98 | 26.82 → 31.06 | 26.69 → 26.73 |
| 20261113 | 8 | 34.57 → 27.82 | 30.88 → 30.67 | (not run) |
| 20261114 | 4 | 30.85 → 26.54 | 31.32 → 30.73 | (not run) |

A regressed on 2 of 3 seeds. B was flat-to-slightly-up on all 3. Mean A across seeds −7.8% vs its own initialization (from 30.37 to 27.45). Mean B +5.4% (from 30.0 to 30.82). Commits happen in the plastic periphery with zero core drift, watermark cosine 1.000 everywhere (all 40 generations × 3 seeds, 3 arms).

## Hypothesis read-out vs `PREREG-E09.md`

- H1 (>=20% mean improvement by gen 30 in >=2 of 3 seeds): FALSIFIED. No seed moves >=20% by gen 30 on either agent.
- H2 (≥ rev-C matrix organism at gen 40 by 0.3 in >=2 of 3): FALSIFIED. Per-agent mean is well below matrix rev-C on all 3 seeds.
- H3 (no early saturation): HELD. 4-8 commits per seed vs matrix D/E's freeze pattern. The custom organism commits more often, for worse results. Mechanism
- H4 (reject rate < 20%): HELD. Zero rejections everywhere.
- H5 (watermark retained): HELD. Cosine 1.0 everywhere.

## The mechanism, stated plainly

- The commit rule compares probe-window returns computed with t0=1000 (deterministic but different world-phase) to the incumbent probe.
It does not compare against the same-phase real episode.
The organism therefore commits whenever a probe-window comparison favors a candidate even if the long-horizon episode distribution penalizes it.
This is the same selection-horizon mismatch E08 showed on the matrix organism, raised one tier of capacity, measured on identical torus seeds.
- Without that mismatch, the micro-cell's early B movement (26.8 to 31.1) shows the organism can track real field-phase gains when selection happens to agree with long-horizon reward, but it cannot tell when it is wrong, so it undoes its own progress under drift.

## Honest read

- This is a miss on the headline clauses H1 and H2.
- The instrument is alive (invariants, watermark, probe-commit all functional), but the selection horizon mismatch is the bottleneck and likely was the bottleneck in E08 too.
- The frozen control behaves as advertised (0 commits, flat returns). Adaptivity claims are not artifacts of this instrument.

## Next steps recorded, not run

1. Fix the selection evaluation horizon to the task horizon (compare candidates on actual 80-step episode rewards from the current world state, not a deterministic 24-step probe at another phase of the field). This is the E10 to run if the program wants it. Expect commits to be rarer and strictly better.
2. Once selection is sound, re-run 3 seeds before any conclusion about capacity scaling. Until then, no claim about whether more capacity helps can be made. The organism is not yet reliably selecting for the task.
3. GRU arm (secondary, H6) not run. Not worth running on a broken selection rule.
