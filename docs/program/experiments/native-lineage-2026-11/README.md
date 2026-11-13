# Native lineage selection

The word "native" in this title and directory means the live Python gate in `weft/runtime/invariants/invariants.py` (`verify_weight_update_safety_ex`), which is what this record calls. The C gate and the shared-memory arena are a different path.

A 256 by 256 weight cell with two update rules. Alpha follows stream 0. Beta follows stream 1. The Python gate accepts or rejects the lower-error rule. Distance is measured from the saved baseline, which is the rule `run_weft_plasm_cycle` already uses.

`run_weft_plasm_cycle` is a different loop. There, beta is a shorter step on the same residual, and `papers/01-models-as-cells/paper.md` records beta winning 0 of 120 generations. Here each rule has its own target. No runtime file changes.

## Protocol

Each target is the baseline plus a periphery matrix of length 1. The first 64 rows stay frozen. A step has length 0.25 after those rows are cleared. Isotropic Gaussian noise is drawn on the periphery and rescaled to length 0.05 times the periphery gradient, then added, before that scaling. The lower error on the scored stream wins, and a tie goes to alpha. Novelty weight is 0. A commit also requires the winner error to be no higher than the parent. The other rule is not offered to the gate. `scaled_step` zeroes the core rows of every step, so core drift against the baseline is an invariant with tolerance `1e-12`, not a commit term.

Ten seeds, 20261111 through 20261120. Eight generations. The budget starts at 100 and a commit costs 2.5. If all eight generations committed, the remaining-budget floor would be 80, so the budget half of the gate is untested in this record. Across those seeds the two target directions have mean dot product -0.0017.

The predictions were:

1. On one stream, with radius 120, the mean held error ends below half the start. The match rate (whether the lower-error rule is the one that steps toward the scored stream's target) is reported. It is a consequence of each rule descending its own target, and is not evidence that the scored stream picked a method. A comparison that would test method selection would score two rules that differ in method on the same target.
2. With radius 0.20, nothing commits and the held error stays at the start. This is a sanity check: the step length 0.25 is already longer than the radius. It is reported and is not an exit check.
3. The scored stream switches at generation 5. With radius 120, error falls in both phases. Ratios are per-phase (end of that phase over the start of that phase).
4. The same switch with radius 0.45 commits fewer generations after the switch than before it. A no-switch control at the same radius (scored stream stays 0) is run in the same pass. This contrast is reported and is not an exit check.

## Results

Linux x86_64, CPython 3.13.5, NumPy 2.5.4. This is a rerun with the rescaled 5 percent noise described above. Full counts are in `results.json`.

| Run | Chosen rule matches | Commits | Held error |
| --- | --- | --- | --- |
| Stream 0, radius 120 | 80/80 | 20/80 (generations 1-2 only) | 0.232 of the start |
| Stream 1, radius 120 | 80/80 | 20/80 (generations 1-2 only) | 0.232 of the start |
| Stream 0, radius 0.20 (sanity check) | 80/80 chosen | 0/80 | 1.000 of the start |
| Switch, radius 120 | 80/80 | 20, then 30 | 0.232, then 0.149 of that phase's start |
| Switch, radius 0.45 | 80/80 chosen | 10, then 20 | 0.412, then 0.184 of that phase's start |
| No-switch, radius 0.45 | 80/80 chosen | 10, then 0 | 0.412, then 1.000 of that phase's start |

On the single-stream radius-120 runs the other rule's error was higher by 0.731 of the parent error. After two commits the held error was 0.232 of the start (stream 0 range 0.220 to 0.248; stream 1 range 0.223 to 0.239), which is below half, so prediction 1's error clause held. Later candidates were accepted by the gate (`ok`) and then rejected because the winner error was about 1.98 times the parent: the fixed 0.25 step overshoots once the residual is small.

The radius 0.20 sanity check rejected every generation. The candidate distance was 0.250, and the gate reported `baseline_distance_exceeded`.

With radius 120, all 10 seeds reduced error in both phases of the switch. Phase A committed generations 1 and 2 (20 commits). Phase B, after the switch at generation 5, committed generations 5 to 7 (30 commits).

Prediction 4 failed. The switch at radius 0.45 committed 10 generations in phase A and 20 in phase B (commits by generation: 10, 0, 0, 0, 10, 10, 0, 0). The no-switch control at the same radius committed only generation 1 (10, then 0). Generation 2 was rejected on stream 0: after one 0.25 step the held distance was 0.25, the next candidate reached about 0.464 against radius 0.45, and the gate reported `baseline_distance_exceeded` on every later no-switch row. After the switch, a step toward the other target still fitted inside the ball (generation 5 candidate distance about 0.224, generation 6 about 0.405). Generation 7 was then rejected because the winner error overshot the parent, with the candidate still inside the radius.

The lowest remaining budget in any row was 87.5. The budget half of the gate did not bind.

## Reproduce

```bash
python3 docs/program/experiments/native-lineage-2026-11/run_lineage.py
```

The default `--out` path is under the system temporary directory, so that command leaves the tracked `results.json` unchanged. To refresh the tracked file, pass `--out docs/program/experiments/native-lineage-2026-11/results.json`. A unittest at `test_run_lineage.py` runs the same exit checks into a temporary directory and is invoked from the verify job in `.github/workflows/ci.yml`.

Exit 0 means the P1 error clause (held error below half on both single-stream arms) and both phases of the loose switch held. The radius 0.20 sanity check, the match rates, and the original P4 contrast (phase B commits fewer than phase A) are stored in `predictions` and do not change the exit code.

## Limits

Thirty-two input rows do not determine a 256 by 256 map. The C gate is not called. There is no watermark check and no shared-memory arena. Paper 1 section 7.3 (two update rules whose ranking changes with the data) is tracked in issue #75.
