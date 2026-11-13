# PREREG-E09 — Invariant-gated micro-cell organisms (registered 2026-11-12 before any run)

Owner approved; Arm 1 assigned to this seat, Arm 2 (TinyStories-2M) to a peer. Exploratory. No API credits in this arm.

## Clauses

- H1 (custom cell learns): mean episode return in generations 30 to 40 exceeds generation 0 to 10 by >= 20% in at least 2 of 3 seeds (paired t-test against the frozen control, seed-matched). Falsified otherwise.
- H2 (custom cell beats the matrix organism): mean return at generation 40 exceeds the E08 `rev-C` matrix organism on the same seeds by >= 0.3 in at least 2 of 3 seeds. Falsified otherwise.
- H3 (no early saturation): the commit rate does not drop below 0.5 per active seed by generation 30 (the matrix organism froze around gen 13 in 2 of 3 seeds). Falsified otherwise.
- H4 (gate cheapness): gate rejection rate over all candidate commits < 20% across seeds. Falsified otherwise.
- H5 (watermark survives): cosine alignment >= 0.85 in every generation of every seed, and core drift == 0.0 exactly. Any violation published as an invariant failure, not filtered out.
- H6 (GRU beats MLP on the same seeds, if both are run): mean return at gen 40 with GRU >= MLP in >= 2 of 3 seeds. Exploratory, no directional prediction; reported as-is.
- H-ablation: 20% of plastic neurons whose gradient signal is weakest get pruned after gen 20, re-evaluated; reported as ablation only, no claim.

## Arms and seeds

P (primary): MLP head, 768 hidden, plastic from row 192.
A: GRU (hidden 512, 1 layer), plastic rows 192..511.
F (control): frozen custom cell (mask opens no rows).
R (control): shuffled decoder, pinned seed per run.
E: E08 rev-C matrix organism for reference on same seeds.

3 seeds per arm: 20261112, 20261113, 20261114. 40 generations, 80 steps/episode, probe-commit rule as registered in E08.

## Cost and stop rules

Local compute only. If the primary arm produces three seeds of zero improvement by generation 30, the arm is killed and the null is recorded as-is. If the watermark ever violates H5, the run stops and the violation is the reported result.

## Deliverable

`docs/program/experiments/micro-cell-2026-11-12/` on branch `record/micro-cell-2026-11-12`, PR through review, misses published alongside wins, credit lineage from issue #142 and this file.

## Correction note, 2026-11-12 (added after the runs, during review of PR #143)

The clauses H1 to H6 above are the registration and are not changed. The arm description "P (primary): MLP head, 768 hidden, plastic from row 192" does not match the organism that ran. As run: a frozen 256x256 watermarked core and a plastic 512x256 periphery `wp` (768 hidden units in total), with only `wp` mutated; the output head and biases stay at their initial values; thrust is the deterministic `mu`, and `lsig` is unused. Arms A (GRU) and R (shuffled decoder) were not run, and F (frozen) was run for seed 20261112 only. See the correction note in `00-DESIGN.md` and the verdicts in `RESULTS-E09.md`.
