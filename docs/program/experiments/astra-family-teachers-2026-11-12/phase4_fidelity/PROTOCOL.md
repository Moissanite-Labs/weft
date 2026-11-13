# Phase 4: numerical fidelity probes

This follow-up separates simple numerical reading, mechanical editing, semantic inference and equivalence judgments. It is registered after first-study outcomes were visible. The machine-readable registration is data/PROTOCOL.json, version fidelity-v1. Every fixed probe is retained, with no candidate selection.

The package allows at most 22 gpt-6-astra requests with storage disabled. Requests and scoring oracles are prepared before calls. Credentials and internal reasoning items remain excluded by the common API transport.

| Probe | Requests | Registered task and score |
| --- | --- | --- |
| A: sparse readout | 12 | Sizes 64 and 256, seeds 1103 and 1129, with displayed precisions raw (6 digits), round2 (2 digits) and round5 (5 digits). Identify the top three rows using the displayed values. Ties at the cutoff are allowed. |
| B: mechanical edit | 6 | Sign flip, zero row and scaled row on classifier and organism examples. The complete specified row must match its oracle within absolute tolerance 1e-6. |
| C: dominant input | 2 | Infer a dominant-input threshold rule. Score agreement on 2,048 fresh inputs with seed 7731. This does not establish a unique semantic interpretation. |
| D: equivalence | 2 | Return the planted equivalence label, checked alongside numerical forward behavior. |

Probe A tests a deliberately sparse planted readout ceiling. It does not establish general understanding of dense weights. Probe B tests mechanical editing, separate from policy intervention with frozen hidden features. All fixed outcomes, invalid answers and errors belong in the result archive.

The prepared source checkpoints, request files, oracles and manifest are stored under data/. Offline regression tests use synthetic responses and make no paid calls:

```sh
python3 -m unittest -v test_fidelity.py
```

API token usage is recorded when returned. Cost estimates use recorded rates and are not invoices. Coding-agent token usage is unavailable.
