# Numerical-fidelity scoring review

Independently reviewed fidelity.py and PROTOCOL.md without inspecting paid response contents. All 4 offline tests passed, including the synthetic complete 22-probe package and exact scoring replay. No paid calls were made. no registered code or prepared artifacts were changed.

The fixed registry generates 12 A probes, 6 B probes, 2 C probes and 2 D probes, with no best-candidate selection. Request and oracle hashes, source checkpoint hashes and the scoring-code hash are recorded before evaluation. Response digests appear in results. replay compares recomputed results, including those digests. Evaluating a partial package reports pending probes explicitly.

A scores top-three row norms against displayed rounded values with a defined tie policy. Its matrices contain only three nonzero planted rows, so this is a sparse readout ceiling task, not a difficult dense ranking or a demonstrated numerical precision limit. Repeated precision conditions share the same planted matrices.

B checks every element of the requested edited row with absolute tolerance 1e-6 and rejects nonnumeric values or incorrect shapes. It tests literal mechanical editing, not whether the intervention improves network behavior. The classifier and organism dimensions are handled by the oracle row itself.

C scores fresh-input agreement between a returned one-coordinate threshold rule and the original network's classes. It has no preregistered binary pass threshold. Report its agreement continuously. It evaluates approximate numerical function inference, not unique semantics or a learned interpretation of unnamed inputs.

Its two probes are original/permuted versions of the same classifier, not two independent trained models.

D checks the planted equivalence answer alongside fresh-input numeric differences. The permuted case is analytically equivalent by consistent hidden permutation. the changed case adds 8 to one output bias, so non-equivalence follows directly.

Finite sampled comparisons alone would not prove universal equivalence, but here the planted transformations supply that ground truth. This is logit equivalence, which is stricter than class agreement.

No scoring blocker was found. Claims should retain the package's deliberately narrow scope and disclose shared checkpoints/paired probes rather than treating 22 requests as 22 independent scientific replications.
