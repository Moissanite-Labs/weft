# PREREG-E10 — task-horizon commit evaluation for the custom micro-cell (registered 2026-11-12, before any E10 run)

Diagnostic of E09's miss. Hypothesis: the probe-horizon and world-phase mismatch caused the organism to commit into worse long-horizon trades regardless of capacity.

## Design of this arm

Single change vs E09: the probe evaluation now runs on the actual task episode (T=0, 80 steps, same field phase as the deployment episode), not the deterministic 24-step window at T=1000.

Everything else held constant including seeds, architecture, plasticity, invariants, noise level, candidate count, and the 1.01 commit margin floor.

## Registered clauses

- H-E10-A (fix works): mean return at generation 40 exceeds E09's same-seed terminal returns on at least 2 of 3 seeds. Falsified otherwise.
- H-E10-B (capacity now matters): per (seed, agent), the mean return over final 5 gens exceeds the frozen control's same-stage mean return in at least 2 of 3 seeds' agent sides. Falsified otherwise.
- H-E10-C (gate stays honest): rejection rate < 20%, watermark retained, core drift exactly 0.0 in every run. Falsified on any violation.
- H-E10-D (selection is stable): the same candidate committed by the T=1000/24-step probe is not preferred over the task-horizon candidate in >= 30% of gens where they differ. Exploratory; no directional prediction.

## Seeds

Same 3 seeds: 20261112, 20261113, 20261114. Same cell init seeds.

## Cost

Local compute only. 40 generations, 3 seeds, ~2-3 minutes per run.

## Delivery

Committed to branch `record/micro-cell-2026-11-12` as follow-on commits to PR #143; both E09 and E10 land in that one record with misses intact.
