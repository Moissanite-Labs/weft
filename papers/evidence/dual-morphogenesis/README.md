# Dual morphogenesis benchmark — recorded evidence

This folder holds the recorded run and a self-consistency checker for the
dual sensory-synaptic morphogenesis benchmark.

**Naming.** This benchmark has **no roadmap E-number**: `E15` on main is the
graded-chemostat swarm experiment (`docs/design-notes/apple-silicon-dissipative-swarm.md`),
so this benchmark is named, not numbered, and assigning it an E-number needs a
maintainer ruling. It also has **no paper number**: `papers/series.yml`
currently reserves number 3 for "Eido: Style as a point in space", so the
evidence lives under `papers/evidence/dual-morphogenesis/`, which the papers
build ignores (no `paper.md`, so `scripts/build_papers.py` does not discover
it as a paper).

- `certificate.json`. The recorded 12-seed, 5-wave differential run (regimes
  `M0` to `M3`), with provenance (git commit, python/numpy versions, platform,
  exact command) and a `platform_dependent_fields` list.
- `verify_certificate.py`. Zero-import (from `weft/`) self-consistency
  checker. Recomputes the file's SHA-256 and checks that the per-seed rows add
  up to the summary and that the recorded invariants hold (zero core drift,
  poison accounting, budget/drift caps, boundary-audit identities,
  `passed_joint_gate` recomputable from the recorded fields). It asserts no
  headline outcome (no "12/12", no "0/120"), it is not tamper evidence — anyone
  who edits a number and recomputes the digest passes it — and it does not
  re-derive any result. Run it with any Python 3.10 or newer:

  ```bash
  python3 papers/evidence/dual-morphogenesis/verify_certificate.py
  ```

The benchmark itself is `scripts/dual_morphogenesis_benchmark.py`. It imports
the optional plasm primitives in `weft/runtime/plasm/` and needs NumPy. Run it
from the repository root (the script inserts the repo root into `sys.path`, so
no `PYTHONPATH` is needed):

```bash
python3 scripts/dual_morphogenesis_benchmark.py            # writes papers/evidence/dual-morphogenesis/certificate.json
python3 scripts/dual_morphogenesis_benchmark.py --check    # replay comparison
```

`--check` compares the replay with the `provenance` block stripped (otherwise
the check run's own command line would make it fail on the authoring machine).
It is **not portable** across platforms: the float fields (R^2, OOD ratios, the
`fraction_dual_sha256` and the boundary-audit floats, hence
`certificate_sha256`) depend on the platform's libm and BLAS and are listed
under `platform_dependent_fields` in the certificate.

## Status: review items from #180 are fixed

The review on #180 (abu-aska) found that the setup and scoring built in most of
the old M3 advantage. All items are fixed in `scripts/dual_morphogenesis_benchmark.py`:

1. **Sensory step measures instead of assigning.** Both candidate worlds
   (skill-adapted vs. bias-only) are evaluated on the wave's actual probe
   inputs (rows of its shifted eval set) with the wave's actual `bias_vec`; the
   bias residual is `0` iff the chosen Farkas certificate is identifiable at the
   target tolerance, else the wave's actual unscaled `bias_vec`. No
   hand-picked per-regime bias constant exists.
2. **Routing routes.** Routed regimes (M1, M3) take the wave's corridor rows
   from the Dinic solver's certified assignment (`cut_cert.assignments[w_idx]`,
   with earlier committed corridors locked via `allowed_corridors`), and the
   peripheral rows carrying each wave's teacher signal are drawn per seed and
   per wave from a seeded numpy Generator — identically for all regimes — so
   index-order allocation gets no free alignment.
3. **Dominant-loss deltas are like-for-like.** Base, clean and poisoned
   candidates are all scored with the same full readout `x_tr @ w` against the
   same target `y_tr + bias_residual`, with the spike counted once. Whether each
   poisoned candidate actually improves dominant loss over the clean candidate
   is recorded (`poison_improves_dominant_count`), not asserted.
4. **One readout for scoring.** Every regime is scored with `xt @ w_mat` and
   the OOD tail ratio always uses `xo @ w_mat`. The per-wave shunted corridor
   readout is still reported for all four regimes as the clearly labelled
   secondary field `mean_shunted_ood_r2`.
5. **Provenance.** The report records the git commit, python/numpy versions,
   platform and exact command; `--check` stays non-portable and says so.

## Results (this machine: see `provenance` in `certificate.json`)

12 seeds x 5 waves, 120 poisoned proposals per regime. Mean values over the 12
seeds; `R^2` is the shifted-OOD held-out score under the **common full readout**
`xt @ w_mat` (the shunted readout is the labelled secondary column).

| regime | passes /12 | poisons committed /120 | poisons vetoed /120 | poisoned-improves-dominant /120 | mean R^2 (full) | mean min-wave R^2 | mean R^2 (shunted, secondary) | mean max OOD tail ratio | final dim | core drift |
|---|---|---|---|---|---|---|---|---|---|---|
| M0_fixed_scalar | 0 | 120 | 0 | 23 | -5.8566 | -7.8019 | -5.8566 | 21.8066 | 20 | 0.0 |
| M1_synaptic_only | 0 | 110 | 10 | 23 | -6.6947 | -8.9150 | -1.0585 | 21.6273 | 24 | 0.0 |
| M2_sensory_mpdi_fixed_dim | 0 | 0 | 120 | 22 | -2.4689 | -3.5887 | -0.3602 | 13.5052 | 20 | 0.0 |
| M3_full_dual_morphogenesis | 0 | 0 | 120 | 24 | -2.9459 | -4.0135 | -0.3241 | 14.6662 | 24 | 0.0 |

Boundary audits: with 12 dominant + 8 tail probes on a 32-dim peripheral space,
12 null directions are invisible to both probe families
(`invisible_attack_*_delta` ~ 2e-15, `mpdi_detects_unprobed_nullspace: false`);
over 250 steps the Stern-Brocot accumulator's denominator grows to 3226 bits,
the raw IEEE-754 dyadic accumulator to 59 bits, and the fixed-radix `10^6`
accumulator stays at 19 bits with max discrepancy 5.1e-06.

Read these honestly: **no regime passes the joint gate on this design once the
review defects are removed.** The old 12/12 M3 result was an artifact of the
constant identifiability inputs, the index-order corridor that matched the
teacher rows by construction, the mismatched dominant-loss baseline and the
per-wave shunted readout. With randomized teacher placement and the common
full readout, no regime reaches the R^2 thresholds (the corridors no longer
align with the teacher rows by construction, so the skills are mostly not
captured), the OOD tail ratio is non-zero for every regime (it is now computed
from `xo @ w_mat` every time, not core-only), and the cost-partitioned dual
fails closed (`dual_certificate_passed: false` everywhere, drift above the
3/4 cap). The MPDI regimes (M2, M3) veto all 120 poisons; the scalar-gate
regimes (M0, M1) commit 110-120 of them. The recorded
`poison_improves_dominant` counts (22-24 of 120) show the poisoned candidates
essentially never improve dominant loss over the clean candidate — the spike
lives in the training null space — so the old "strictly improves" docstring
claim is false as a rule and is now only recorded.

The sensory step is now measured: probe mitosis fires 0-2 times per seed in
the sensory regimes (data-derived from the wave's probe readings), and the
chosen probe set is identifiable in 4-5 of 5 waves there (3-5 of 5 in the
scalar regimes, which never expand the probe set).

## Format demonstrations

The Farkas identifiability certificates and the cost-partitioned `Fraction`
metabolic dual are **format demonstrations**, not evidence of real-world
properties: the probe readings are data-derived as described above, and the
metabolic dual charges a measured cost (`3/2` plus the rows added that wave)
rather than a constant that cannot bind; with the current R^2 it fails closed
on the drift cap.

License: evidence CC-BY-4.0 as with the other papers. Synthetic-world
mathematics throughout. No study data, no patients, no clinical claims.
