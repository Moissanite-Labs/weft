# Proposed functional transfer experiment

Status: proposal for a future experiment, not a registered or completed E11 result. This follows the [canonical peer synthesis in issue #149](https://github.com/Moissanite-Labs/weft/issues/149) of the team's November 12 studies. The local `phase5_geometry_probe` checks mathematical boundaries without a teacher or API calls. It does not test learned skill transfer in a colony.

## Question and capability

Can a donor's useful behavioral change transfer to a new policy cell while the recipient preserves specified behaviors? A transferable record should identify the intended input/output effect, the recipient's fitting procedure and the scope of its preservation certificate. A numerical edit remains subject to the recipient's behavioral evaluation before adoption.

Separate three questions: equivariance under an exact hidden-unit permutation, compatibility between independently seeded representations, and retention outside the probes used to construct the update. Success on the first does not establish the other two.

## Transfer record

Use shared observable input and output semantics. A donor supplies fixed synthetic probe inputs and its output differences before and after an accepted edit. Preserve the exact probes, output deltas, donor checkpoints, byte count and provenance. These are transferred behavioral data. A small operator program could become a separate arm, with the grammar and execution cost fixed before trials.

For an explicitly linear-output recipient with fixed hidden features, write its readout as `Y = H B`. Let `H_keep` contain the recipient's features at the designated preservation anchors, including a bias feature if the bias is editable. Compute an orthonormal null-space basis `Z` with a declared singular-value tolerance. Install the minimum-norm solution

```text
Delta_B = Z pinv(H_probe Z) Delta_Y_donor
```

This is a recipient-local least-squares fit, even though it uses no gradient iterations. The preservation certificate records `H_keep Delta_B`, its tolerance, feature and parameter hashes, rank, nullity and edit norm. Exact zero extends to the retained feature span.

A numerical residual bound extends with a factor depending on the span coefficients, so it is not a uniform bound on that entire span. It does not certify unseen nonlinear features or every shifted input.

The completed policy studies use a tanh output. For that architecture, do not treat an output-space delta as a preactivation delta. Specify recipient targets `Y_new = Y_recipient + Delta_Y_donor`, require them strictly inside `(-1, 1)`, and fit `atanh(Y_new) - H B` as the preactivation target.

Freeze feasibility and boundary-margin rules before running, then evaluate the final tanh outputs. Preserving preactivations preserves their tanh outputs, while target-fit error must be assessed in the actual output units.

Report infeasibility rather than silently weakening the constraint. If the retained feature matrix has full column rank, the exact null space is trivial. An approximate-preservation arm may trade drift for improvement, but its tolerance must be separately declared and its results separately reported.

## Comparisons to freeze before execution

| Comparison | What it isolates |
| --- | --- |
| No edit | Recipient baseline |
| Raw donor parameter delta | Cost of mismatched coordinates and representations |
| Known-permutation transport on a functionally identical sibling | Exact coordinate-equivariance check with an oracle map |
| Probe fit without preservation projection | Effect of recipient adaptation |
| Probe fit with preservation projection | Incremental benefit and feasibility cost of the constraint |
| Deterministic constrained optimizer with the same probes and feedback opportunities | Whether a teacher adds useful decisions beyond the numerical solver |

Keep exact-permutation siblings separate from independently seeded recipients. Freeze model architectures, editable parameters, output units, norm limits, probe count, rank tolerance, solve count and validation opportunities.

Register fit-residual and edit-norm rejection rules: a pseudoinverse returning a solution does not establish useful target fit or an acceptable edit. Log task-independent setup costs as well as candidate evaluation. If an Astra arm chooses operators, give its solver control the same observations and candidate budget.

Do not ban raw-coordinate edits merely to make an operator arm win.

## Evaluation

Construct new source families, new recipient families and new arena seeds. Do not tune against the completed studies' holdouts. Register the task targets and the protected contexts before fitting. For the conditional task, evaluate both requested directions and paired-context contrast, rather than allowing their mean to hide a weak direction.

Use independent IID and shifted held-out observations for target error, protected-output drift and hazard error. Include fresh closed-loop arena rollouts as a separate behavioral outcome. Keep the primary pass rule as a conjunction of useful target change and preservation on both distributions. Set numerical thresholds from task units and a separate pilot, then freeze them before the confirmatory run.

Treat independently generated donor families as replication units. Report every family, failed solve, rejected candidate and zero update. Five of five observed passes would describe those five families. it would not be a guarantee about all future organisms. Replication across additional families and shifts is needed to estimate reliability.

## What would be learned

A successful result would show a reproducible form of functional transfer under explicit, checkable retention conditions. A failure may identify insufficient probe coverage, incompatible recipient features, a null space with no useful task direction, or a mismatch between the assay and deployed behavior. Those diagnoses are distinct from hidden-unit permutation.

The useful architectural question is whether a small reserved residual module or other independently testable editable capacity improves the feasibility frontier. Compare that change against the same original architecture and task before treating it as necessary.

The proposal combines existing ideas in alignment, distillation and constrained editing. Novelty and broad machine-intelligence claims require a separate literature assessment and stronger evidence. The immediate next action is to register a matched comparison after the local geometry diagnostic and independent review, without promising a result in advance.
