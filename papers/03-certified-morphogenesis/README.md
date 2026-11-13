# Certified Morphogenesis: E15 benchmark evidence (v1.1)

This folder holds the independently verifiable evidence for the E15 dual
sensory-synaptic morphogenesis benchmark.

- `e15_certificate.json`. The recorded 12-seed, 5-wave differential run
  (regimes `M0` to `M3`). Passes all 12 seeds under dual morphogenesis,
  vetoes all 120/120 planted null-space poisoned proposals, 0.0 core drift.
  This is v1.1: it also records the two boundary closures from Paper 3 v1.0,
  namely fixed-radix `10^-6` rational denominators capped at 20 bits across
  2,500 steps (versus 3,226 bits for Stern-Brocot), and 100/100 vetoes of
  omniscient double-null-space attacks under the Fiat-Shamir Haar probe
  refresh (versus 0/100 for the static MPDI tail gate alone).
- `verify_e15.py`. Zero-import clean-room checker. Recomputes certificate
  self-consistency: SHA-256, per-seed counts, budget and drift invariants,
  and the v1.1 closure invariants (20-bit denominator ceiling, nullity
  accounting, dual MPDI validity). Environment-agnostic. Run it with any
  Python 3.10 or newer:

  ```bash
  python3 papers/03-certified-morphogenesis/verify_e15.py
  ```

The benchmark itself is `scripts/e15_dual_morphogenesis.py`.
It imports the optional plasm primitives in `weft/runtime/plasm/`, including
`sample_haar_orthogonal_probe`, `evaluate_haar_refreshed_mpdi_gate` and the
fixed-radix `quantize_fixed_radix_q` boundary TCB.

## Why there is no `paper.md` yet

Paper 3, Certified Morphogenesis, was prepared as a peer artifact on
2026-11-13. It is not merged in this folder because landing it properly
requires the papers pipeline (`scripts/build_papers.py` with pandoc 3.1.3 and
Playwright) and a maintainer ruling on `papers/series.yml`, which currently
reserves number 3 for "Eido: Style as a point in space". Path-based paper
discovery would otherwise shadow that entry. This folder holds only the
verifiable evidence in the meantime. The paper text can be dropped in once
the numbering and build are settled.

## Provenance

Derived from a peer artifact dropped 2026-11-13 (Gemini task agent,
Apache-2.0), as v1.1. The Helly corridor worst-case witness in
`weft/runtime/plasm/identifiability_gate.py` additionally re-applies the
mid-segment fix (`true_min_shift_flow`); the v1.1 drop did not include it.
`swarm_loom.py` from the same drop is deliberately excluded: it drops the
Law 2a/2b chemostat economics and density-normalized re-seeding carried by
the merged `weft/runtime/mac/swarm_loom.py` and is not landable here.
Synthetic-world mathematics throughout. No study data, no patients, no
clinical claims. License: evidence CC-BY-4.0 as with the other papers.
