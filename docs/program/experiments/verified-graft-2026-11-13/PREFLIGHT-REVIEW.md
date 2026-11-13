# Source and transport preflight review

Reviewed by gpt-forge (Sol). This review covers `graft.py`, `prepare_teacher.py`,
`PROTOCOL.md` and the subscription adapter. It is not a review of a completed
teacher trial or the independent Lean implementation.

The visible packet contains weights, paired activations and explicit contracts.
The preparation envelope adds current deployment and previous A feedback. Neither
function exports the source seed, hidden coefficient target, signed permutation
labels or evaluation inputs. Filenames identify seeds to the operator but are not
included in the model message. Calibration makes the full-information problem
identifiable by signed column matching. This is a deliberate strong baseline,
not a leak of an otherwise unidentified task.

The graft validator requires exact bounded integers, rejects booleans, preserves
the protected basis and restricts forks to saturated cases with a distinct
specialist. Fork deployment preserves the original root and uses a declared task
router. This changes capacity and routing, so it cannot demonstrate one matrix
satisfying conflicting tasks. Independent proof implementation and orchestration
need their own audit.

A/B include the same required coordinate basis. Their random additions are fresh,
but the sets are not disjoint. Full rank means zero SSE identifies the target
operator. The protocol explicitly acknowledges these restrictions. The separate
overfitting fixture tests rejection behavior under partial coverage. It does not
turn the main assay into a broad generalization experiment. The current pure
`confirmed` predicate implements strict improvement and the ten-percent margin
on both sets. Ranking, fresh-B access and final lock behavior must also be checked
in the orchestration when ready.

One metadata finding was sent to the runner: the original `proposal_source`
configuration described mechanical controls only, while the protocol now adds a
separately labeled subscription cohort. The runner corrected it to name separate control and real teacher cohorts.
Prepared artifacts must be regenerated against the corrected configuration.
No mathematical defect was found in the reviewed pure functions.

The adapter sends only its fixed instruction and supplied JSON envelope. It has
no tool declarations beyond an empty list, no conversation history, no repository
retrieval and no persistent agent loop. Individual illegal candidates survive
parsing for the evaluator. A malformed response remains observable and consumes
its opportunity. Response text is untrusted data and is never executed.

Six mocked tests pass, including actual installed Hermes request shaping without
auth resolution. Raw stdout/stderr are in `data/validation/oauth-mocks.*.txt`.
The first root authentication attempt failed before inference: a late Hermes
bootstrap re-executed the script after its output directory existed. The fix
completes the supported bootstrap before durable effects. A standalone no-auth
bootstrap-then-unique-directory probe passed. The failed request is retained.
No inference result follows from these checks.

The bounded coordinator was subsequently reviewed. It checks code/data pins
before each new request and reserves the opportunity in a persistent ledger
before launching the worker. A started opportunity is never automatically
retried. A changed prompt stops resumption. Round-two messages are built only
from the visible packet, selected deployment and A-only feedback.

A timeout observability gap was fixed before registration: subprocess deadline
failure now records captured process output, timeout state and whether a real
worker record exists, without fabricating a response. It stops for manual audit.
A second defense excludes parsed candidates unless the terminal event reports
completed status and actual model `gpt-6-astra`. Other terminal identities become
consumed error packages retaining provenance. The evaluator independently checks
bindings. Four coordinator mock tests pass without network or proof compilation,
with logs in `data/validation/coordinator-mocks.*.txt`.
