# Phase-two independent assessment

The factorial separates two useful evidence sources: numerical weights alone and hidden activations alone both improve the specified movement target, while combining them adds little on these five source families. The gains mostly fail the preservation requirement on fresh inputs.

This supports a limited information-ablation finding, not robust preserved skill acquisition or a general claim about weight understanding.

All 40 responses were valid. 34 candidates passed validation and 6 did not. Final selection retained the unchanged source in 2 of 20 conditions, both in the neither arm. Every source family is one replicate: n=5, not 20 independent families or the number of siblings/rollouts. Conditions are paired within sources.

## Selected outcomes

Values are means of each source's percentage reduction in active movement MSE, relative to its own unchanged baseline. Retention includes hazard tolerance, unchanged-context prediction drift and frozen-core equality.

| Evidence | IID improvement | IID retention | IID >=5% + retention | Shifted improvement | Shifted retention |
| --- | ---: | ---: | ---: | ---: | ---: |
| Weights + activations | 19.50% | 1/5 | 1/5 | 19.99% | 0/5 |
| Weights only | 20.10% | 1/5 | 1/5 | 20.81% | 0/5 |
| Activations only | 18.06% | 1/5 | 1/5 | 18.80% | 0/5 |
| Neither | -0.12% | 5/5 | 0/5 | -0.07% | 5/5 |

Seed 163 is the only information-bearing source meeting IID retention in each of the three relevant conditions. All other IID failures, and every shifted failure, arise from unchanged-context movement drift exceeding 0.0005.  no source condition fails the registered hazard tolerance.

Thus the target-error reductions should not be described as preservation successes. They remain numerical behavioral changes with a measured cost to the protected behavior.

## Paired information effects

Entries below are mean paired differences in active-error improvement, in percentage points. Positive means the added evidence helped. Round one measures raw valid proposals before feedback-assisted selection.  selected results include validation filtering and the second response.

| Added evidence / other evidence fixed | Round 1 IID | Selected IID | Round 1 shifted | Selected shifted |
| --- | ---: | ---: | ---: | ---: |
| Weights / no activations | +15.50 | +20.22 | +16.10 | +20.88 |
| Weights / activations present | +2.58 | +1.45 | +2.54 | +1.19 |
| Activations / no weights | +12.06 | +18.17 | +12.51 | +18.87 |
| Activations / weights present | -0.86 | -0.60 | -1.06 | -0.82 |

Weights alone improve over neither for all 5 sources at both stages. Activations alone also improve over neither for all 5 sources. Adding weights when activations are already present helps 4/5 sources.  the selected IID mean of+1.45 points includes one source advantage of+5.67 points and much smaller differences elsewhere.

Adding activations when weights are already present has mixed round-one signs and slightly lowers selected improvement on all 5 sources (0.06–1.61 percentage points). These small differences should not be promoted into a claim that activations intrinsically harm editing.

The phase-one weight/activation confound is now experimentally separated for this task. Hidden activations are a substantial alternative source of coordinate-specific information, consistent with the earlier scrambled-weight result. Numerical weights are independently useful when activations are absent.

Their small incremental value when activations are present suggests overlapping useful information here.  it does not prove the model ignored either field or identify its internal mechanism.

There is one two-response teacher trajectory per source-condition, with no repeated calls at fixed source/prompt. Stochastic model-call variation is not separately estimated.

Evidence availability also changes prompt length and numerical content, and selected comparisons include the threshold gate's discontinuity and possible second-round adaptation to its boundary. Round-one comparisons mitigate feedback/selection concerns but not call variability.

Five source seeds support descriptive paired evidence, not a reliable population significance claim.

This new study used 48 shared examples and rounded teacher-visible values to 8 significant digits, unlike the first wave's larger unrounded packet. Within-phase comparisons remain controlled.  cross-phase magnitudes do not isolate a change in teacher capability. Static target error, sibling transfer and colony collision outcomes are different outcomes and should remain separately reported.

## Verification

The independent reviewer ran `python 3 run_experiment.py replay --out data` after final results were present. Replay verified the registered code and artifact hashes, regenerated candidate evaluations and recomputed results in an isolated directory, returning `deterministic_results_match: true`.

The summary's retention counts were cross-checked against the source records.  paired effects were computed from `factorial_contrasts` in results.json. Frozen code and experimental data were not modified. The only new file from this assessment is this report.
