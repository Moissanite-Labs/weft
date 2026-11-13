# Independent scientific and code review

Reviewer: gpt-forge independent review subagent, requested model gpt-6-astra. Reviewed 2026-11-12 before paid teacher outcomes were available to this reviewer. Scope: PROTOCOL.md, lab.py, run_experiment.py, teacher_api.py, and test_lab.py. No credentials were read, no paid calls were made, and no external messages were sent.

Production code was not modified. Line references describe the initial reviewed snapshot and may shift during fixes.

## Findings requiring disposition

1. **Candidate reuse does not bind the scored experiment or request (P1 integrity).** `run_experiment.py:98–110` verifies only the response hash when a candidate file exists. Source weights, validation data, request, and CONFIG may change while the cached accepted flag and validation metrics survive.

   `finish()` trusts these flags and ranks their old scores, then applies the chosen patch to the current source. This can make selection no longer correspond to the stated data or gates. Confirmed in a temporary directory: process a valid empty proposal, change one validation target, rerun process.

   the candidate remains identical and its stored metrics differ from fresh evaluation. Bind candidates to experiment/request/config fingerprints and reject mismatches. also bind requests to the packet/history from which they were built. This is a reproducibility defect, not evidence that the current files were changed.

2. **Replay success overstates what is checked (P2).** `run_experiment.py:214–221` reports a deterministic match even when original results do not exist (`old is None`). Replay does not validate the saved artifact manifest or code hashes, and neither finish nor advance checks saved config against runtime CONFIG.

   Successful replay with a real original results file establishes numeric recomputation equality, but not original-request integrity, original code identity, or full artifact immutability. Require an existing result for a match claim. verify manifest and recorded configuration before replay, or explicitly narrow the claim.

   The manifest currently hashes only lab.py and run_experiment.py, excluding teacher_api.py and the protocol.

3. **API artifact retention is broader than the protocol exclusion (P2 preventive).** `teacher_api.py:54–56` saves the complete API response. The protocol excludes internal reasoning traces, but there is no item-level exclusion or whitelist. No returned trace was observed: paid responses were not present during review.

   Save only necessary public response text, status/usage and provenance metadata, excluding reasoning output items. Request `store=False`, fixed official endpoint, in-memory credential handling and exact-key redaction are otherwise appropriate.

4. **Local comparator metadata may contradict its selected patch (P2 reporting).** `lab.local_evolution()` initially selects by composite loss and returns `validation_loss`. `run_experiment.py:149` overwrites its patch using the intended gate and movement MSE without updating that top-level loss.

   The final comparator cell and metrics are correctly recomputed, but the archived trace can associate an obsolete score with the selected patch. Recompute the selected loss/metrics or remove the ambiguous top-level field.

5. **Worker default exceeds the registered request cap (P2 configuration).** `teacher_api.py:22` defaults to 20 calls while the protocol specifies at most 18. Explicit invocation with `--max-calls 18` resolves the immediate mismatch. changing the default avoids accidental excess. Counting input lines rather than successful attempts can stop early after blanks/skips. it cannot exceed the specified invocation cap.

## Scientific checks and claim boundaries

- Request construction exposes training examples and validation aggregates. it does not serialize held-out observations, labels, sibling parameters, or sibling outcomes. Both conditions receive the same source-specific examples. The behavior-only arm removes hidden activations and replaces all numerical tensors with shape/withheld entries.

  Its packet still labels visibility as `weights`, a misleading label worth correcting, but no weights were found in that path.
- Fresh datasets use nonoverlapping RNG seed offsets for the three registered seeds. Within each family, siblings are deliberately correlated and share evaluation observations. Independent source seeds, not individual siblings or rollout repeats, remain the scientific replication unit.
- Teacher selection and the final local-search selection both require improvement in overall and active movement, hazard tolerance, and low-urgency prediction drift, then minimize validation movement MSE. Test/shift/rollout scores are evaluated only during finish after all proposals are available. This supports a held-out outcome claim if the integrity issue above is resolved.
- Active movement means `urgency > 0.35` in lab.evaluate, not all positive-urgency cases. State that exact threshold in the protocol/report. Unchanged context means urgency <= 0. Hazard retention tolerates max(2% of baseline MSE, 0.0002), which can be proportionally substantial at tiny baselines. publish both absolute errors and tolerance rather than describing perfect preservation.
- Sparse patch validation enforces source-relative edits, coordinate uniqueness, finite scalar deltas, coordinate bounds, frozen w1 rows/b1 entries and norm limits. Four hidden activations are frozen, but outgoing w2 columns from those units remain editable. describe this as frozen hidden features, not a fully frozen downstream subnetwork.
- Known-ID transfer correctly remaps w1 rows, b1 entries and w2 columns, and keeps b2 unchanged. The exact-permutation test passes. Raw transfer is a meaningful negative comparison. this experiment does not learn neuron alignment.
- Random directions match the chosen patch's declared coordinate list and L2 norm. Because clipping enforces the per-coordinate bound, directions are not uniformly sampled on a sphere. no uniformity claim should be made. Zero-valued teacher coordinates remain in declared support, so call this declared support if encountered.

  Random controls are posthoc reference draws and must not be selected or counted as new independent teachers.
- The three local-search candidates use fixed norm 0.4, whereas teacher norms can vary up to 2.0. The protocol correctly limits the matching claim to number of proposal evaluations. The gradient diagnostic is appropriately separate and is not bound by the teacher patch norm.
- The 160-step ecology is an additional mechanism check, not proof that the hand-specified imitation target is ecologically optimal. Primary source success needs both >=5% active improvement and retention on held-out IID data in at least two source seeds. Validation acceptance alone is insufficient. shifted and sibling success should be separately described.

## Verification performed

`python3 -m unittest -v test_lab.py`: all seven tests passed. These cover deterministic construction, baseline fit, patch atomicity and limits, exact aligned transfer, support/norm matching, packet visibility and shared rollout determinism. The tests exercise held-out evaluation as existing harness validation but no teacher results were viewed.

A temporary no-op-response replay of process() demonstrated stale candidate reuse after validation mutation. No data or request artifacts were modified by that probe.

This review does not establish API model availability, completed paid rounds, scientific efficacy, replay of a completed study, or publication readiness. Re-review the changed integrity/retention paths before declaring those issues resolved.

## Follow-up before successful teacher responses

Re-read the revised runner and API client after the lead/runner fixes. Candidate records now bind experiment, request and CONFIG fingerprints. the runner regression test confirms changed inputs are rejected. Replay now requires original results and manifest and validates recorded artifacts plus the two computation-module hashes.

The comparator selected validation_loss is recomputed. The API client excludes non-message response items and defaults to 18 calls. These resolve the five principal findings above for their stated scope. API transport/protocol files are still outside the numeric-replay code hash set. do not equate numeric replay with full transport provenance.

Request files are not reconstructed against the current experiment/history before first processing, so preserving the pre-call experiment/request pair remains important.

Additional verification: all 7 lab tests, 7 runner tests, and 5 calibration tests passed (19 total). The newly added calibration is described in CALIBRATION.md and remains scientifically separate. No successful API response was inspected in this review.

Calibration equivalence clarification: an exact output-row swap is the analytic reference, not the only allowed solution. Negating both logits also inverts binary decisions except ties. The pass gate uses held-out inverse-label accuracy, inversion of source predictions and frozen parameters. nonzero logit difference from the swap oracle is reported, not automatically failed.
