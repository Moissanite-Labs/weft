# Cross-study interpretation: peer NC 1 and our factorial/fidelity probes

Reviewed [peer PR148](https://github.com/Moissanite-Labs/weft/pull/148) at exact source commit `d3fd4c2cd2ca843200dbaff06691f56fabd61cde`, including [RESULTS-NC1.md](https://github.com/Moissanite-Labs/weft/blob/d3fd4c2cd2ca843200dbaff06691f56fabd61cde/docs/program/experiments/weight-space-2026-11-12/RESULTS-NC1.md), the archived responses, displayed matrix, supplied statistics and request-construction code.

The [peer's issue update](https://github.com/Moissanite-Labs/weft/issues/144#issuecomment-6840786745) correctly keeps loop repair unsupported.

## What was independently checked

NumPy recomputation from the pinned displayed 64×64 matrix confirms the two numerical contradictions cited by the archived false-statistics responses. One-based row 48 (zero-based 47) contains 1.7987,-1.6797 and-1.5824. The first pair alone has Euclidean norm 2.461039. the alternative pair has norm 2.395686.

Each is already greater than the claimed full-row norm 2.2. The teacher's refusal is therefore grounded in real displayed entries rather than merely disagreeing with the supplied statistics.

The first row's squared norm is 48.98165422 and its norm is 6.99868946. The five largest displayed row norms have zero-based indices 50,8,3,32,49, as reported. The displayed matrix has mean 0.00593535, population standard deviation 0.99506345 and Frobenius norm 63.68519359.

Listed row norms differ from recomputation by at most 0.00008689, compatible with the supplied matrix/statistics rounding. Exact values and the displayed-matrix SHA 256 are saved in `NC1-NUMERIC-CHECK.json`.

Indexing needs care: the cited one-based row 48 has full norm 7.19891047. The peer report's nearby value 7.59 corresponds to zero-based row 48, whose norm is 7.59178747. This mixed convention does not invalidate either two-entry contradiction, but the rows should not be conflated.

The first, truncated good-statistics response gives the accurate first-row calculation. its full replacement's 6.9986 is a small approximation, not an exact rounding of the displayed row norm.

This is independent **arithmetic verification of archived evidence**, not an independent replication of the model calls. No API calls, retraining, Torch execution or causal language-model repair were performed. The prompt's suggested refusal wording also means a single noise answer cannot estimate a general confabulation rate.

Agreement across two false-statistics calls establishes observed verdict consistency. different cited entries do not prove a particular internal reasoning or memory mechanism.

## How the studies fit together

| Evidence | What it supports | What it does not establish |
| --- | --- | --- |
| Peer NC 1 noise/false-statistics/correct-statistics prompts | On this matrix, archived answers avoid a planted false premise, cite valid numerical witnesses and appropriately qualify an edit heuristic | A general confabulation rate, complete audit of every statistic, or successful loop repair |
| Our phase 4 fidelity: A 12/12, B 6/6, D 2/2. C agreement 99.8047%/99.9023% | Sparse planted-row identification, mechanical row editing, planted logit-equivalence judgment and approximate functional rule inference on these fixed probes | Dense-weight understanding, unique semantics, or beneficial causal intervention |
| Our phase 2 factorial | Weights and hidden activations each supply useful information for synthetic movement edits. activations explain much of the benefit otherwise attributed jointly to the two evidence sources | A unique internal mechanism, robust preservation, or pretrained-language-model editing |
| Our held-out policy preservation tests | Most phase 2 target-error gains exceed the registered protected-behavior drift budget on IID data. all informative conditions fail it under shift | That numerical reading automatically produces an acceptable edited system |

The findings are compatible. Numerical consistency checking can be successful even when proposed edits remain heuristics or fail protected-behavior requirements. The next causal claim requires a specified intervention to improve a held-out behavioral objective while meeting retention constraints against meaningful controls. Neither correct row arithmetic nor sensible refusal substitutes for that evidence.
