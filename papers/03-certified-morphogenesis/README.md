# Certified Morphogenesis: E15 benchmark evidence

This folder holds the recorded run and a self-consistency checker for the
E15 dual sensory-synaptic morphogenesis benchmark.

Status: the regime comparison below is under review. The review on #180 found
that the setup and scoring build in most of the M3 advantage (constant
identifiability inputs, index-order corridor rows aligned with the teacher,
mismatched dominant-loss baseline, per-wave readout for M1-M3). Read the
numbers as a demonstration of the certificate formats until that is fixed.

- `e15_certificate.json`. The recorded 12-seed, 5-wave differential run
  (regimes `M0` to `M3`). Passes all 12 seeds under dual morphogenesis,
  vetoes all 120/120 planted null-space poisoned proposals, 0.0 core drift.
- `verify_e15.py`. Zero-import self-consistency checker. Recomputes the
  file's SHA-256, per-seed counts, budget and drift invariants, and
  boundary-audit flags. It does not re-derive any result, and it is not
  tamper evidence: anyone who edits a number and recomputes the digest passes
  it. Run it with any Python 3.10 or newer:

  ```bash
  python3 papers/03-certified-morphogenesis/verify_e15.py
  ```

The benchmark itself is `scripts/e15_dual_morphogenesis.py`. It imports the
optional plasm primitives in `weft/runtime/plasm/` and needs NumPy. Run it
from the repository root:

```bash
PYTHONPATH=. python3 scripts/e15_dual_morphogenesis.py --out /tmp/e15.json
PYTHONPATH=. python3 scripts/e15_dual_morphogenesis.py --check
```

`--check` is not portable yet. `partitioned_drift_q`, the per-regime
`fraction_dual_sha256`, `raw_ieee754_dyadic_bits`,
`invisible_attack_dom_delta` and so `certificate_sha256` depend on the
platform's libm and float summation, and the report does not record its
commit or environment.

## Why there is no `paper.md` yet

Paper 3, Certified Morphogenesis, was prepared as a peer artifact on
2026-11-13. It is not merged in this folder because landing it properly
requires the papers pipeline (`scripts/build_papers.py` with pandoc 3.1.3 and
Playwright) and a maintainer ruling on `papers/series.yml`, which currently
reserves number 3 for "Eido: Style as a point in space". Path-based paper
discovery would otherwise shadow that entry. This folder holds only the
verifiable evidence in the meantime. The paper text can be dropped in once
the numbering and build are settled.

License: evidence CC-BY-4.0 as with the other papers. Synthetic-world
mathematics throughout. No study data, no patients, no clinical claims.
