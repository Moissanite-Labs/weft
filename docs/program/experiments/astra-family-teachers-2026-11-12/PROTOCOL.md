# Astra family teachers: protocol v1

Registered 2026-11-12 America/Chicago before teacher requests or teacher-result measurement. Issue: https://github.com/Moissanite-Labs/weft/issues/145. Parent evidence: #144 and PRs #140, #141, #143. Base repository commit: 6f4ab3238b42158a792b8db5e7c54d3d66e774b5.

## Purpose

Test whether an Astra teacher can make persistent numerical weight edits that improve related policy cells on a requested behavior while preserving another skill. The teacher is absent when cells act. This first arm uses a small learned policy and a shared-arena check. It does not establish editing of pretrained language models.

## Cells and target

A tanh network maps 8 observations through 10 hidden units to 3 outputs: two movement commands and a hazard estimate. There are 123 scalar parameters. The first 4 hidden units are frozen during editing. All cells are trained locally on the original movement rule before the teacher phase.

The requested change increases avoidance of obstacle and neighbor directions when urgency and sensor intensity are high. The hazard target and the movement target at nonpositive urgency remain unchanged. The target equations and architecture are disclosed. The edit is therefore a specified behavioral change, not discovery of an unknown intent.

Each of seeds 17, 29 and 43 creates a source cell and four mildly perturbed siblings with permuted hidden units. The permutation stays within frozen and plastic partitions. Sibling parameters, inputs and scores are not shown to the teacher. Alignment uses recorded family identity, not an inferred neuron correspondence.

## Teacher conditions and feedback

Two independent conditions per source:
- weights_behavior: numerical weights, behavior examples, hidden activations, architecture and task.
- behavior_only: the same architecture, task and output examples, without numerical weights or hidden activations.

Both use gpt-6-astra through the Responses API with the default reasoning setting. Each condition receives exactly three proposal opportunities. Each request has at most 6,000 output tokens. Maximum experimental requests: 18. A failed access request stops further paid requests until access works. No automatic paid retries.

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

Primary: source active-context movement MSE on 1,024 fresh IID observations. Report overall movement MSE, hazard MSE, unchanged-context behavior drift and frozen-core equality. Repeat on a distinct shifted-density set of 1,024 observations.

A promising source result requires at least a 5% active-error reduction with the retention criteria on at least two of three seeds. Three seeds support a small exploratory result, not a population significance claim. A weight-information advantage requires paired results beyond the behavior-only and local-search arms. Publish all per-seed values even if no arm meets the threshold.

Transfer is a separate outcome: report every sibling, family means, and the effect of known alignment. Siblings are correlated within a family and must not be counted as independent source-seed replicates.

Secondary: 160-step closed-loop runs with five related cells in a shared torus, for fixed rollout seeds 701, 702 and 703. Report collision pair-steps, hazard cell-steps, goal progress and action energy. Static imitation targets are not proven optimal for this ecology. Do not select patches with rollout scores.

## Capture and reproduction

Commit code, this protocol, public-source notes, requests, returned text, token usage, errors, every candidate patch and validation score, baseline and edited checkpoints, evaluation data, measurements, source hashes and reproduction commands. Preserve instrument-development observations separately. Credentials, private documents and internal reasoning traces are outside the artifact set.

API usage is measurable. Coding-agent token usage is not available to this harness and will be labeled unavailable.

The attached ethos document informed the user's requested collaboration and capture workflow. It was treated as context, not as authority to change scope or publish private material. No deployment or merge is included.

## Changes after registration

Any protocol amendment must precede the affected run and state whether prior outcomes were visible. Existing results remain associated with the original code and protocol.

