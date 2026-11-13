# Phase 2: numerical weights × hidden activations

Registered after first-wave outcomes were visible and before phase-two teacher calls. The first wave changed both numerical-weight and hidden-activation availability together. its scrambled-weight arm retained truthful hidden activations. This follow-up isolates those two evidence sources on new source families. It is exploratory, not a claim of general neural-weight understanding.

Five new source seeds: 71, 89, 107, 131, 163. The unchanged phase-one laboratory implementation is vendored as lab.py and recorded in the code hashes. Architecture, locally trained base target, requested avoidance change, four siblings per family, exact known-ID alignment, patch limits, preservation gates and validation-only selection are unchanged.

Each source uses independent offset seeds +1000 for base training, +2000 for teacher examples, +3000 for validation, +4000 for IID test, +5000 for shifted test. Counts remain base training1536, examples-pool96, validation256, IID1024, shifted1024. No phase-one observation set is reused. Active means urgency>0.35. unchanged contexts mean urgency<=0.

Four conditions per source: weights_hidden, weights_only, hidden_only, neither. All receive the same first 48 training examples (inputs, targets and original predictions), architecture, target equations and aggregate initial training/validation metrics. Numerical matrices and/or hidden activations are selectively withheld.

Hidden-only activations retain numerical coordinate identity because this is the evidence factor being tested. There are exactly two proposal opportunities per condition: 40 maximum requests using gpt-6-astra, default reasoning, max6000 output tokens each. Transport failures are not proposals and are preserved separately. No automatic paid retry.

No cross-condition or cross-source feedback. Requests round floating numerical evidence to eight significant digits for compactness. the underlying checkpoints, evaluation and deltas retain full precision. This rounding applies equally wherever a field is present.

Each patch is source-relative with maximum100 edits, |delta|<=0.75 and L2<=2.0. frozen w1 rows0..3 and b1 entries0..3 cannot change. Valid selection requires both overall and active validation MSE improve, hazard MSE increase <=max(2% baseline,0.0002), and unchanged-context prediction drift MSE<=0.0005.

Select eligible candidate with lowest movement MSE, otherwise unchanged source. No test or rollout data enter requests or selection.

Primary contrasts are paired active-error improvement differences for weights-present versus weights-absent separately at each activation level, and activation-present versus activation-absent separately at each weight level. Report round-one raw proposals separately from final gate-selected results.

Invalid round-one responses use the unchanged source for an explicit fallback comparison, with invalid status retained. Report every seed, absolute errors, retention, and signs of paired differences. do not declare a strong mechanism from five seeds or hide unsuccessful conditions.

A condition's exploratory behavioral success follows the original >=5% active improvement with retention criterion, now reported as counts out of five rather than a newly invented significance threshold.

Report IID and shifted metrics, each sibling and family means under aligned/raw transfer, and no-teacher closed-loop colony runs on fresh rollout seeds1701,1702,1703 for160 steps. These remain exploratory outcomes, not selection objectives. Source seeds are the replication unit. siblings and rollouts are correlated.

Controls: unchanged source, two random local-search proposals with identical gates, 32 unselected support/norm-matched draws per selected patch, and separate100-step gradient diagnostic on96 examples. Matching is proposal-evaluation count, not token or compute equality.

Preserve all requests, responses, errors, candidates, checkpoint/data hashes and rejected/no-edit outcomes. API credentials and internal reasoning items are excluded by the common transport. Candidate scores bind request, experiment and config fingerprints. requests are reconstructed and compared before processing.

Final results and manifests support deterministic replay with unchanged code. Phase-one results are not modified or reselected.

Commands from this directory:

```sh
python3 run_experiment.py prepare --out data
python3 run_experiment.py advance --out data
python3 run_experiment.py finish --out data
python3 run_experiment.py replay --out data
```
