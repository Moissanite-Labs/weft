# Independent pre-call review

Reviewer: gpt-forge independent-review agent, gpt-6-astra. Scope: lab.py, run_experiment.py, PROTOCOL.md and test_phase3.py. Reviewed before phase-three paid responses. no phase-two test results were inspected. Verdict: **GO. no paid-call blocker found in this audit.** Locked source/protocol files were not modified.

- The operator language is fixed, data-only dispatch. It cannot run supplied code. Unknown operators/fields and invalid coordinates are rejected. Hidden replacement requires unit4..15, preventing frozen-core writes. Every intermediate operation is converted back to a source-relative patch and checked against coordinate and norm limits. Ridge projects the complete delta into those limits.
- Ridge receives only the training dataset, fits only movement readout and bias, and weights unchanged contexts against original source predictions. The packet's residual correlations are also training-only. It is ordinary numerical fitting and is correctly labeled as such. Hidden edits may still perturb hazard. the gate measures that effect rather than assuming preservation.
- Both IID and shifted validation must improve left active, right active and paired-context contrast errors while meeting hazard, unchanged-context drift and frozen-core conditions. Candidate ranking uses the mean validation contrast error only. Final tests, siblings and arena scores do not enter requests, fitting, feedback or selection.
- The response parser requires four candidates. Each malformed response consumes four explicit failed slots. Four rounds per source provide16 opportunities. Within-response candidates share the same prior history and are evaluated before subsequent feedback.
- The no-teacher ridge grid and16 random candidates use the same eligibility gate and ranking. They match candidate evaluations, not computation or information. Manual/fitted result strata are properly described as action types from one adaptive teacher, not randomized comparisons.

  A gain over the ridge grid can reflect teacher feature construction or hyperparameter choice and does not by itself establish direct weight reading.
- The request is reconstructed from current source/training information and history and compared to the archived request. Configuration and hashes of lab, runner and protocol are locked. Existing candidates are independently recomputed and compared. Replay validates all recorded hashes and regenerates candidate evaluation and final results from archived responses.
- The paired-context metric explicitly changes the context sign on otherwise identical active observations, testing conditional response beyond average error. The crossing arena uses simultaneous actions and a separate exact-target controller. Its outcomes remain secondary. target imitation is not a proof of collision optimality or safety.

Verification: `python3 -m unittest -v test_phase3.py` passed all5 tests, covering dimensions/target equations, conditional contrast, operator bounds/purity/frozen protection, request visibility, deterministic rollout, null-candidate rejection and request binding. The implementer also reported a complete no-op finish/replay smoke. this reviewer did not rerun that longer smoke.

Remaining limits: three source seeds, deliberately correlated siblings, disclosed synthetic target, validation-assisted tool use, and action-type strata rather than randomized manual-versus-fit allocation. The primary >=10% conditional improvements and retention must be checked on **both** final distributions.

validation acceptance alone is insufficient. Report no-edit and invalid outcomes. Report ordinary fitting separately from unaided numerical edits. There is no basis here to claim editing of pretrained language models.
