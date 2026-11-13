# R1 archive rescore, fresh operator seeds (2026-11-13)

A rerun of the held-out audit from PR #116 against the nine E07 archived run folders, under two fresh operator-chosen seeds. It does not rerun the E07 experiment. It rescores archived final artifacts against the same reference harness, adds the `fibmod` workload that the original write-up excluded, and records provenance the original data lacked.

This document and its JSON siblings supersede the eight-task aggregate table in `heldout-audit-r1.md`, which should not be quoted for rankings. Wins now count only when `rel > 1.0 + ref_spread`.

## Provenance

- Operator: agentic contributor for Ahraz Arifuddin, directed and signed by him. The operator did not author the candidate cells.
- Host: macOS arm64, Apple M1 Max, Python 3.14.6.
- Harness: `code/heldout_audit.py`. Seed 1 executed at repo `9323272` with exactly the working-tree delta that became commit `f9ed422` (seed parameterization and provenance block). Scoring logic is unchanged. Seed 3 executed at `f9ed422`.
- Workloads generated from fresh 64-bit seeds chosen at audit time, never present in the audit code:
  - Seed 1: `4697720169128928207` (utc `2026-11-13T03:14:34Z`)
  - Seed 3: `3657675104222185323` (utc `2026-11-13T03:55:47Z`)
- Sandbox: `sandbox-exec` for every cell and reference call. Network denied, HOME reads denied, writes restricted to per-call scratch, run under the machine-wide bench lock.
- Archive staging: the nine run folders were copied to a scratch tree, `chmod -R a-w`, hashed before and after (`data/heldout-audit-rescore-folder-hashes-2026-11-13.json`). All nine digests match after both passes. The E07 directories at `~/Work/razi-cells/exp/` were never touched.
- Commitment: 5 interleaved repeats per pass, task order alphabetical, ref then runs `b5 b6 b7 b8 b9 b10 b11 g3 g4`.

## Results

rel = contender score / stdlib reference score, median over 5 repeats. Wins use the reference-noise rule.

| run | model | kept/100 | seed1 median rel | seed1 wins | seed3 median rel | seed3 wins |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| g4 | DeepSeek v4.1 Flash (8-cell) | 1.57 | 2.696 | 7/8 | 2.240 | 6/8 |
| b8 | opencode-go:gemini-4-argon | 10.34 | 1.926 | 7/8 | 2.128 | 7/8 |
| b10 | opencode-go:gemini-4-argon | 12.50 | 1.809 | 5/8 | 1.680 | 5/8 |
| b11 | anthropic:claude-fable-5-1 | 11.02 | 1.363 | 4/8 | 1.673 | 5/8 |
| g3 | DeepSeek v4.1 Flash (4-cell) | 3.12 | 1.325 | 4/8 | 1.565 | 6/8 |
| b5 | anthropic:claude-fable-5-1 | 12.82 | 1.662 | 6/8 | 1.504 | 4/8 |
| b7 | opencode-go:hy4 | 0.00 | 1.135 | 3/8 | 1.493 | 5/8 |
| b9 | anthropic:claude-fable-5-1 | 7.76 | 1.396 | 4/8 | 1.375 | 4/8 |
| b6 | openai:gpt-6-astra | 12.88 | 1.092 | 3/8 | 1.200 | 2/8 |

Cross-seed Spearman rank correlation: **0.817**. Top (g4, b8) and last (b6) are stable in both seeds. `b6`, the model with the highest kept-improvements-per-100-calls (12.88), is last by median rel in every measurement and loses the noise-rule win count as seeds change. The protocol-fit reading on #111/F1 survives fresh inputs.

## fibmod, now scored

The original write-up excluded this workload because the E07 fallback shim could not be audited.

The merged path-matched scorer removes the shim. A cell is scored through its own CLI (`python3 fibmod.py N` via `runpy`, one process for the whole batch) or its own callable, trying the second if the first fails, with the reference timed on the same path.

Seed 1 and seed 3 both score all runs. b5 and b8 lead (module_callable, roughly 3.0 and 5.0 median). g4 is fast when the CLI path works and slower on the module path. b6 is roughly 0.6 of reference. b9 fails both paths (timeout kill, exit 1) and scores 0 with reasons recorded. g3's path varies from run to run.

A 256-pair composite/prime-modulus redesign is proposed in the operator spec on branch `docs/r1-heldout-audit-spec`. It changes the workload the cells were built against, so it was not run here. Recorded as considered, pending reviewer sign-off.

## Other findings

- `g3` scores 0 on csvsum in both fresh seeds (wrong output on the held-out 1M-row CSV). Both runs record the reason. Any g3 win claim should carry that.
- `b7` (hy4) out-of-channel artifacts (`maze/mazehelper.so`, `sortints/sortints_helper.so`, `primes/sieve.so`) score through the slot CLIs, but no artifact clears the reference-noise bar consistently across seeds. The narrow channel blindness documented in #111/F1 is not vindicated by the held-out suite. The b7 compress held at ~1.55 in every measurement.
- `lcs` has the largest spread (~0.29) and dominates mean_rel. Geometric means are shown in the JSONs.
- `primes` reference spread is 0.74. No cell wins it under the noise rule.

## What this does not claim

Nothing here reruns the E07 experiment, re-ranks models for capability claims, or settles the contested boundary on #111. A single operator executed both passes. A truly independent re-execution remains open. One seed family was used for inputs. The rank-order check above is the robustness evidence offered, not ground truth.

The stale aggregate table in `heldout-audit-r1.md` is superseded as an evidence source for rankings. Quote this file instead.

## Files

- `data/heldout-audit-r1-rescore-2026-11-13.json` (seed 1)
- `data/heldout-audit-r1-rescore-2026-11-13-seed3.json` (seed 3)
- `data/heldout-audit-rescore-folder-hashes-2026-11-13.json` (pre/post staging digests)
