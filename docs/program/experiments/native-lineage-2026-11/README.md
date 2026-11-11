# Native lineage selection

A 256 by 256 weight cell with two update rules. Alpha follows stream 0. Beta follows stream 1. The Python gate in `weft/runtime/invariants/invariants.py` accepts or rejects the lower-error rule. Distance is measured from the saved baseline, which is the rule `run_weft_plasm_cycle` already uses.

`run_weft_plasm_cycle` is a different loop. There, beta is a shorter step on the same residual, and `papers/01-models-as-cells/paper.md` records beta winning 0 of 120 generations. Here each rule has its own target. No runtime file changes.

## Protocol

The protocol was fixed before the run.

Each target is the baseline plus a periphery matrix of length 1. The first 64 rows stay frozen. A step has length 0.25 after those rows are cleared, with Gaussian noise at 5 percent of the gradient. The lower error on the scored stream wins, and a tie goes to alpha. Novelty weight is 0. A commit also requires the winner error to be no higher than the parent. The other rule is not offered to the gate.

Ten seeds, 20261111 through 20261120. Eight generations. The budget starts at 100 and a commit costs 2.5. Across those seeds the two target directions have mean dot product -0.0017.

The predictions were:

1. On one stream, with radius 120, the chosen rule matches the stream on at least 80 percent of generations, and the held error ends below half the start.
2. With radius 0.20, nothing commits and the held error stays at the start.
3. The scored stream switches at generation 5. With radius 120, error falls in both phases.
4. The same switch with radius 0.45 commits fewer generations after the switch than before it.

## Results

Apple M1 Max, macOS 27.0.1, CPython 3.14.6, NumPy 2.5.4. Full counts are in `results.json`.

| Run | Chosen rule matches | Commits | Held error |
| --- | --- | --- | --- |
| Stream 0, radius 120 | 80/80 | 80/80 | 0.869 of the start |
| Stream 1, radius 120 | 80/80 | 80/80 | 0.869 of the start |
| Stream 0, radius 0.20 | 80/80 chosen | 0/80 | 1.000 of the start |
| Switch, radius 120 | 80/80 | 40, then 40 | 0.926, then 0.922 of that phase's start |
| Switch, radius 0.45 | 80/80 chosen | 30, then 0 | 0.943, then 1.000 of that phase's start |

On the single-stream runs the other rule's error was higher by 0.052 of the parent error. The gate rejected the radius 0.20 run on every generation. The candidate distance was 0.250.

Prediction 1's match clause held. Its error clause did not. After eight commits the held error was still 0.869 of the start. That end ratio is a factor of 0.983 per committed generation (`0.869 ** (1/8)`).

With radius 120, all 10 seeds reduced error in both phases of the switch.

With radius 0.45, generations 1 to 3 committed on all 10 seeds and generations 4 to 8 did not. The held distance after generation 3 was 0.431. Later candidates reached 0.499, including every candidate after the switch, and the gate reported `baseline_distance_exceeded`. The remaining room inside the ball was about 0.019, and the step length was 0.25, so the second stream's lower-error step did not fit. The other rule was not offered.

## Reproduce

```bash
python3 docs/program/experiments/native-lineage-2026-11/run_lineage.py
```

Exit 0 means the match counts, the radius 0.20 rejection, both phases of the loose switch, and the tight switch's commit contrast all held. The half-error line is stored in `predictions` and does not change the exit code.

## Limits

Thirty-two input rows do not determine a 256 by 256 map. The C gate is not called. There is no watermark check and no shared-memory arena. The run does not close issue 111.
