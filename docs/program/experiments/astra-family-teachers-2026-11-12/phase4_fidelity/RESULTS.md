# Numerical fidelity results

All 22 fixed paid probes completed and produced valid answers. Evaluation and exact replay completed with no pending probes. These probes test deliberately narrow numerical tasks. They do not establish general dense-weight understanding or a numerical precision limit.

| Probe | Result | Scope |
| --- | --- | --- |
| A: sparse readout | 12/12 correct | All size/precision conditions recovered the three planted rows. Only three rows were nonzero, and precision variants shared matrices. |
| B: mechanical edit | 6/6 correct | Complete requested rows matched sign-flip, zero-row and scaling oracles within absolute tolerance 1e-6. This tests arithmetic editing, without a behavioral improvement claim. |
| C: threshold inference | 99.8046875% and 99.90234375% agreement | Continuous agreement on 2,048 fresh inputs per original/permuted probe. No binary pass threshold was registered. |
| D: equivalence | 2/2 correct | Correct labels for a consistent hidden permutation and an output-bias change, with numerical forward checks. |

Both C answers identified input coordinate 0. The original probe returned threshold 0.29743 and the permuted probe returned 0.29798, with class 1 above and class 0 below. These are approximate numerical rules for paired versions of one classifier. They do not identify unique input semantics.

The D permutation had maximum sampled logit difference about 1.42e-14 and complete class agreement. The changed case had maximum logit difference about 8 and class agreement 97.8515625%. The planted transformation supplies the equivalence ground truth. Finite sampled agreement alone would not prove universal equivalence.

The classifier here is the separately trained local calibration checkpoint. It is not the original classifier checkpoint discussed in the peer's [PR #148 archive](https://github.com/Moissanite-Labs/weft/pull/148), identified by commit `d3fd4c2`.

The [peer evidence on issue #144](https://github.com/Moissanite-Labs/weft/issues/144#issuecomment-6840786745) is a separate record. Results from these checkpoints should not be presented as an exact reproduction of each other.

INDEPENDENT-REVIEW.md records scoring review before paid answers were inspected. Four offline tests passed, including a synthetic complete-package replay. The paid results are in data/results.json, with observable responses under data/requests. Internal reasoning items and credentials are excluded.

From this directory, replay without an API key:

```sh
python3 fidelity.py replay --out data
```

API token usage remains available in individual responses. Any cost calculation is an estimate at recorded rates, not an invoice. Coding-agent token usage is unavailable.
