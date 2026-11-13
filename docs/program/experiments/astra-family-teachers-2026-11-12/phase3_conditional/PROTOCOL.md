# Conditional passing with bounded teacher computation

Phase 3 tests whether an Astra teacher can add opposite passing maneuvers to a trained controller. It is a new exploratory study after phase 1 outcomes were visible. Phase 1 showed steering changes and failed retention under distribution shift. Phase 3 therefore tests conditional acquisition and uses shifted validation before final testing.

## Design fixed before requests

Fresh family seeds are 101, 211 and 307. Each source has an 8-input, 16-hidden-unit, 3-output tanh network: 195 parameters, 159 editable. The first four incoming hidden rows and biases are frozen. Four siblings inherit each source with small independent perturbations and recorded within-partition permutations.

A source learns goal following, mild avoidance and a hazard estimate. The new target adds a lateral movement term proportional to positive urgency and a context sign, which is independently sampled as minus or plus one. The sign reverses the requested maneuver. Nonpositive urgency and hazard targets stay unchanged.

The target equations are disclosed. This is specified skill acquisition, not discovery of hidden intent.

The teacher receives source weights, 24 training examples with hidden activations, and training residual correlations. Training contains 384 examples. IID validation and shifted validation each contain 256 independent examples. Final IID and shifted tests each contain 1,024 fresh examples. Heldout siblings and all final outcomes are withheld until all responses are fixed.

## Teacher and computation budget

Each source receives four API responses, each proposing exactly four candidates. The total is 12 requests, at most 8,000 output tokens each, with gpt-6-astra and default reasoning. There are no automatic paid retries. All four candidates in a response are evaluated together. Validation feedback is available in the next response.

Each candidate starts from the original source and contains at most 12 data-only operators. Allowed operators add numeric deltas, replace an editable hidden feature, scale outgoing coefficients, or fit a movement readout with ridge regression. No generated code executes.

Every intermediate and final candidate must stay within absolute coordinate delta 1.5 and total Euclidean delta norm 5.

Ridge regression is ordinary numerical fitting. It fits movement residuals in pre-tanh output space on training data only. Unchanged contexts receive weight eight and source predictions as retention targets. The teacher chooses hidden units, regularization strength and blend.

The complete result is projected to the registered bounds. Hazard output coefficients are not fitted, although hidden edits can still alter hazard predictions.

Every candidate records whether it used fitting. Combined selection and separate manual-only and fitting-only selections are reported. These are action-type strata within one adaptive teacher, not randomized arms. Success with fitting does not establish direct numerical weight reading. The teacher may request no fitting at all, leaving that stratum empty.

## Selection and final criteria

A candidate must improve left-context active error, right-context active error and paired-context contrast error on both validation distributions. Active means urgency greater than 0.35. Paired contrast compares predictions for the same observation with opposite context signs against the intended difference.

Hazard error may rise by at most the larger of 0.0005 or 2% of baseline error. Movement prediction drift at nonpositive urgency may not exceed 0.001. Frozen incoming core parameters must remain exactly equal. Among eligible candidates, select the lowest mean paired-contrast error across the two validation sets. Otherwise retain the source.

Primary evidence is at least 10% improvement in each direction's active error and in paired contrast, with retention, on both final distributions. Report every source seed and each metric, even when no candidate qualifies. A promising result requires two of three source seeds. Three source seeds support exploratory comparison, not a population significance claim.

## Controls and transfer

Sixteen random patch candidates use the same validation and retention gate. Norms cycle through 0.4, 1, 2 and 4. This matches validation opportunities, not information or total computation.

A deterministic 16-candidate ridge grid uses all source hidden units without teacher intervention. Regularization values are 0.0001, 0.001, 0.01 and 0.1. Blend values are 0.1, 0.25, 0.5 and 1. All combinations use the same gate. This checks whether readout fitting alone explains improvement.

An unchanged source and a 600-step gradient diagnostic are also evaluated. The gradient diagnostic uses training only and is not bounded or compute matched. The exact target controller supplies an oracle in the secondary arena. Its static target error is zero by definition, not a learned result.

Selected patches transfer to every sibling with known family alignment and with raw coordinates. Siblings are correlated within each family. They are not independent replicates. Report each sibling against its own baseline.

## Shared crossing arena

Five related cells start around a circle with goals on the opposite side. They observe the closest neighbor, a fixed hazard and a common passing-side sign. All actions are computed before any cell moves. Rollout seeds are 1701, 1702 and 1703, with 180 steps each. The teacher is absent during action.

Report collision pair-steps, hazard cell-steps, goal progress and effort for baseline, selected aligned family and exact target controller. This is secondary evidence. The prescribed static target is not established as an optimal or safe arena controller. No patch is selected using these outcomes.

## Capture and replay

Before the first request, save the source, siblings, datasets, configuration and hashes of the laboratory, runner and this protocol. Save exact requests, returned public text and usage, every valid or invalid candidate, its classification and validation feedback. Save final checkpoints and metrics, including negative outcomes.

Replay checks all artifact and code hashes, regenerates candidate evaluations from responses, then recomputes the final report. It makes no API requests. API transport artifacts follow the parent study's credential and reasoning-exclusion rules.

```sh
python3 run_experiment.py prepare --out data
python3 run_experiment.py advance --out data
python3 run_experiment.py finish --out data
python3 run_experiment.py replay --out data
```
