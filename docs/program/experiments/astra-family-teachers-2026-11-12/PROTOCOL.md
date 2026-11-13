# Astra family teachers: protocol v1

Registered 2026-11-12 America/Chicago before teacher requests or teacher-result measurement. Issue: https://github.com/Moissanite-Labs/weft/issues/145. Parent evidence: #144 and PRs #140, #141, #143. Base repository commit: 6f4ab3238b42158a792b8db5e7c54d3d66e774b5.

## Purpose

Test whether an Astra teacher can make persistent numerical weight edits that improve related policy cells on a requested behavior while preserving another skill. The teacher is absent when cells act. This first arm uses a small learned policy and a shared-arena check. It does not establish editing of pretrained language models.

## Cells and target

A tanh network maps 8 observations through 10 hidden units to 3 outputs: two movement commands and a hazard estimate. There are 123 scalar parameters. The incoming weights and biases of the first 4 hidden units are frozen during editing. The source is trained locally on the original movement rule before the teacher phase. Siblings inherit that source with small perturbations and permutations.

The requested change increases avoidance of obstacle and neighbor directions when urgency and sensor intensity are high. The hazard target and the movement target at nonpositive urgency remain unchanged. The target equations and architecture are disclosed. The edit is therefore a specified behavioral change, not discovery of an unknown intent.

Each of seeds 17, 29 and 43 creates a source cell and four mildly perturbed siblings with permuted hidden units. The permutation stays within frozen and plastic partitions. Sibling parameters, inputs and scores are not shown to the teacher. Alignment uses recorded family identity, not an inferred neuron correspondence.

## Teacher conditions and feedback

Two independent conditions per source:
- weights_behavior: numerical weights, behavior examples, hidden activations, architecture and task.
- behavior_only: the same architecture, task and output examples, without numerical weights or hidden activations.

Both use gpt-6-astra through the Responses API with the default reasoning setting. Each condition receives exactly three proposal opportunities. Each request has at most 6,000 output tokens. Main family requests: 18. The pre-run amendment below adds three blinded requests and one calibration request, for 22 total. A failed access request stops further paid requests until access works. No automatic paid retries.

Every proposal is a JSON list of tensor coordinates and additive deltas relative to the original source. Maximum 100 edits, maximum absolute delta 0.75, maximum cumulative Euclidean norm 2.0. Frozen coordinates, duplicate coordinates, nonfinite values and malformed proposals are rejected. No generated code runs.

Only validation outcomes and prior proposals return as feedback. Held-out test, shifted test and sibling outcomes remain unavailable until all proposals are fixed. The no-feedback evidence is round 1. Later rounds are feedback-assisted weight programming.

## Selection and retention

A valid candidate must improve both overall movement MSE and active-context movement MSE on validation. Hazard MSE may rise by at most max(0.02 times its baseline value, 0.0002). Movement output drift on unchanged contexts, measured against baseline predictions, may be at most 0.0005. Choose the eligible candidate with lowest validation movement MSE. Keep the unchanged cell if none qualifies.

The same rule applies to the local-search comparator. Selection never uses test results. Report rejected proposals, invalid responses and unchanged selections.

## Controls

- Unchanged source and siblings.
- Three random local-search proposals with the same selection and retention gates. This matches proposal evaluations, not computation or information.
- 32 random directions on each selected teacher patch's exact support and norm. These are an unselected reference distribution, not extra candidates competing with the teacher.
- 100-step gradient-training diagnostic on 96 examples. This is a separate capacity/optimization check and is neither compute-matched nor a direct-edit result.
- The same selected source edit transferred to every sibling with known neuron alignment and with raw coordinates.

## Outcomes

Active context means urgency > 0.35. Unchanged context means urgency <= 0.

Primary: source active-context movement MSE on 1,024 fresh IID observations. Report overall movement MSE, hazard MSE, unchanged-context behavior drift and frozen-core equality. Repeat on a distinct shifted-density set of 1,024 observations.

A promising source result requires at least a 5% active-error reduction with the retention criteria on at least two of three seeds. Three seeds support a small exploratory result, not a population significance claim. A weight-information advantage requires paired results beyond the behavior-only and local-search arms. Publish all per-seed values even if no arm meets the threshold.

Transfer is a separate outcome: report every sibling, family means, and the effect of known alignment. Siblings are correlated within a family and must not be counted as independent source-seed replicates.

Secondary: 160-step closed-loop runs with five related cells in a shared torus, for fixed rollout seeds 701, 702 and 703. Report collision pair-steps, hazard cell-steps, goal progress and action energy. Static imitation targets are not proven optimal for this ecology. Do not select patches with rollout scores.

## Capture and reproduction

Commit code, this protocol, public-source notes, requests, returned text, token usage, errors, every candidate patch and validation score, baseline and edited checkpoints, evaluation data, measurements, source hashes and reproduction commands. Preserve instrument-development observations separately. Credentials, private documents and internal reasoning traces are outside the artifact set.

API usage is measurable. Coding-agent token usage is not available to this harness and will be labeled unavailable.

The attached ethos document informed the user's requested collaboration and capture workflow. It was treated as context, not as authority to change scope or publish private material. No deployment or merge is included.

## Changes after registration

Before any teacher call, wording was clarified: only incoming parameters of the first four units are frozen, and siblings inherit the trained source. The implementation and numeric protocol did not change.

Any protocol amendment must precede the affected run and state whether prior outcomes were visible. Existing results remain associated with the original code and protocol.


## Pre-run amendment A: calibration and inconsistent weight evidence

Registered after sibling review comments on issue #145 and PR #146, before any successful model call. One attempted request failed local TLS verification before HTTP. That transport failure is archived and does not consume a model proposal. Python now uses the installed certifi trust bundle with certificate verification enabled.

Add one calibration request for a separately trained 4-to-16-to-2 classifier of x[0] > 0.3. The requested edit inverts the output labels without changing the hidden layer. A known output-row-and-bias swap is the independent oracle. The teacher returns numeric additive deltas through the same HTTP and strict-JSON parsing pipeline, with calibration-specific bounds sufficient for an exact swap.

The inversion task cannot use the policy task's preservation gate, since its intended behavior is to change every predicted label.

Calibration requires at least 95% accuracy against inverse labels and at least 99% prediction inversion on independent held-out inputs. Report baseline, oracle, teacher, frozen-layer equality and invalid edits. A failure stops the family wave for diagnosis. A pass establishes basic pipeline competence, not broad weight understanding.

Add one blinded scrambled_weights proposal per source seed, paired only with the corresponding weights_behavior first proposal. Independently shuffle flattened numerical values within each tensor using seed + 830000. (Corrected after review: this line was registered as seed + 6000, while the run used seed + 830000. See Deviation D1.) Preserve tensor shapes and value multisets. Keep the true examples and hidden activations, apply proposed coordinates to the original checkpoint, and keep the remapping outside teacher requests.

The condition creates inconsistent weight evidence. It is not a function-preserving neuron permutation.

The scrambled request uses the same teacher-visible arm label and instructions as weights_behavior. It receives no proposal feedback. Score it with the same gates and report every outcome. A difference tests sensitivity to coherent weight evidence. Neither failure nor success alone proves the internal mechanism, because the teacher can notice or ignore contradictory inputs.

The original sibling permutation test remains separate: four siblings per family, one sampled permutation each, twelve sibling instances across three source seeds, with mild weight drift. Report every permutation and aligned/raw outcome. Add exact permutation tests with no weight drift as implementation checks. The permutations preserve the frozen/plastic partition. No rotation or scaling symmetry is claimed.

Local search matches three evaluated proposals per source, not tokens, wall time, information, or total computation. Record API tokens and elapsed time. Report this qualification alongside outcomes. Rejected-candidate validation feedback is intentional in rounds two and three. Candidate edits never mutate the original source, and no test or sibling result returns to a teacher.

## Deviations recorded after review

Recorded on 2026-11-12 after review 5884649320 on PR #146, after all four studies' outcomes were visible. They correct the record and change no result. Commit identifiers below are the original history preserved on `record/astra-teachers-prereg-history-20261112`; DCO-HISTORY.md maps each one to its signed-off counterpart.

- D1, scramble seed. The registered text above said the scrambled_weights shuffle used seed + 6000. The harness committed with amendment A in ab90c53 (signed-off 7f7d259), `np.random.default_rng(exp['seed'] + 830000)` in run_experiment.py, used seed + 830000, and every permutation in `data/scramble_private/` matches seed + 830000 and does not match seed + 6000. The line above now states the seed the run used. The shuffle rule, the pairing and the scoring are unchanged.
- D2, later rounds were not pre-committed. Phase-one round 1 requests for all arms were committed in ab90c53 (7f7d259), before any family response. The 12 phase-one round 2 and round 3 requests were first committed in 1bda504 (048996f), in the same commit as their responses. The 20 phase-two round 2 requests were likewise first committed with their responses in c71b69d (b55c273). These prompts depend on earlier feedback, so they could not exist before that feedback returned, and each harness rebuilds them and rejects a mismatch. They were still not committed before their own calls, so treat them as reconstructable but not pre-registered.
- D3, phase-three packet limits. The phase-three teacher packet (`phase3_conditional/lab.py`, `limits`) advertised `max_edits: 200` and no operator cap, while the interpreter rejects candidates with more than 12 operators. The operator semantics and the instructions in the same request both said at most 12 operators. 200 is the per-patch coordinate-edit cap that `apply_patch` enforces, and only 159 coordinates are editable. All 12 phase-three calls ran with this packet. Across the 48 returned candidates the largest had 5 operators and the largest delta operator had 61 coordinate edits, so neither cap bound and no candidate was rejected for either. The phase-three code, protocol and requests are hash-locked by `phase3_conditional/data/code-lock.json` and the replay, so they stay as run. A future packet should name both caps.
