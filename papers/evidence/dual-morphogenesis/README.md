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
  exact command), a `platform_dependent_fields` list, and the boundary audits
  (unprobed-subspace, v1.1 Haar probe refresh, grinding, rational bit-length
  and certificate denominator audits).
- `verify_certificate.py`. Zero-import (from `weft/`) self-consistency
  checker. Recomputes the file's SHA-256 and checks that the per-seed rows add
  up to the summary and that the recorded invariants hold (zero core drift,
  poison accounting, budget/drift caps, boundary-audit accounting identities —
  including the v1.1 Haar probe refresh, grinding and rational bit-length
  audits — `passed_joint_gate` recomputable from the recorded fields, and the
  measured denominator bit-lengths recomputable from the recorded wave R^2
  values). It asserts no headline outcome (no "12/12", no "0/120", no
  "100/100 vetoed"), it is not tamper evidence — anyone who edits a number
  and recomputes the digest passes it — and it does not re-derive any result.
  Run it with any Python 3.10 or newer:

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
accumulator stays at 17 bits (18 bits over 2,500 steps; <= 20 bits by
construction, since its denominator always divides `10^6`). The v1.1 Haar
probe refresh, grinding and denominator measurements are below.

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

## v1.1 (from #181): fixed-radix `10^-6` quantizer + Fiat-Shamir Haar probe refresh

Ported onto the fixed #180 benchmark and re-measured. All audits use fixed
seeds and stated N (see `boundary_audits` in `certificate.json`); the per-seed
regime records and the summary above are unchanged from the #180-fixed run.

What was ported, in `weft/runtime/plasm/identifiability_gate.py` and
`weft/runtime/plasm/synaptic_flow.py`:

- `FIXED_RADIX_DENOM = 1_000_000` and `quantize_fixed_radix_q(val, *, denom,
  direction)` — a boundary quantizer onto the `(1/10^6) Z` lattice with a
  REQUIRED `direction` in `{"up", "down", "nearest"}`. It is used ONLY in the
  boundary audit, never inside certificates: `_to_q` and
  `_exact_nonneg_fraction` keep their exact `Fraction.from_float`
  conversions, so costs, drifts and Farkas inputs never round in the
  optimistic direction. Where the audit quantizes, it uses the conservative
  direction (drift-like values round UP via `direction="up"`; the Haar scale
  is a budget and rounds DOWN).
- `fiat_shamir_probe_seed`, `sample_haar_orthogonal_probe`,
  `evaluate_haar_refreshed_mpdi_gate`, `HaarProbeRefreshReceipt`,
  `verify_haar_probe_refresh_receipt` — a Mezzadri-Haar orthonormal probe
  basis sampled inside `null(observed_probes)` from a SHA-256 transcript
  `(colony_seed, epoch, quantized delta, verifier_nonce)`, fed into the MPDI
  gate as a second opposing probe. The receipt stores the verifier nonce and
  the verifier checks it (`expected_verifier_nonce`).

### Measured boundary-audit numbers (this machine; seeds and N stated in the certificate)

Haar probe refresh screening of the 12-D unobserved joint subspace
(`haar_probe_refresh_audit`, audit seed 20261113, N = 100 per cell, fixed
public screening nonce, attack norm 4.0, generic updates scaled to a 0.125
static tail reading = half the 0.25 static scale):

| mode | attack veto rate | false vetoes, generic updates at 0.125 tail | false vetoes, generic updates swept over the statically accepted range | post-refresh nullity |
|---|---|---|---|---|
| static MPDI tail gate alone | 0/100 | 0/100 | 0/100 (all 100 commit by construction) | 12 (unchanged) |
| Haar full-complement (`max_haar_rows=None`) | 100/100 | 0/100 | 7/100 | 12 -> 0 |
| Haar sub-sampled sub-4 (`max_haar_rows=4`) | 100/100 | 0/100 | 4/100 | 12 -> 8 |

In the sweep column each generic update is rescaled so its static tail
reading is drawn uniformly from (0, 0.25), so the static gate commits all of
them; a false veto is one the Haar gate then rejects. The 0.125 column alone
understates the cost: the larger statically-acceptable updates carry enough
energy in the 12-D unobserved subspace to trip the Haar probe.

Full-complement mode is confirmed a deterministic projection: over 20
challenge seeds its probe energy has spread exactly 0.0 and equals the plain
null-space projection norm (`full_complement_energy_seed_spread: 0.0`,
`full_complement_energy_matches_null_projection: true`) — the randomisation
is in name only there. Sub-4 mode is genuinely seed-dependent (energy seed
spread 0.898217).

Grinding audit (`grinding_audit`, audit seed 777001, rank-1 null-space
attacks of norm 2.0, `max_grind_tries = 2000`, N = 100 fresh-nonce
submissions):

| attack measurement | sub-4 mode | full-complement mode |
|---|---|---|
| fixed PUBLIC nonce: tries-to-success (grinding) | 12 | not found within 2000 |
| fresh verifier nonce per submission: attack successes /100 | 5 (5% per submission) | 0 (0%) |

Rational bit-length audit (`rational_bitlength_audit`, 250 and 2,500 steps):
Stern-Brocot `limit_denominator(10^6)` denominator 3226 bits (250 steps), raw
IEEE-754 dyadic 59 bits, fixed-radix `10^-6` accumulator 17 bits (250 steps)
and 18 bits (2,500 steps) — always <= 20 bits BY CONSTRUCTION because its
denominator divides `10^6` (`fixed_radix_denom_bits_by_construction: 20`);
max discrepancy vs the exact dyadic sum is 1.23e-04 (250 steps) and
1.25e-03 (2,500 steps) with the conservative `direction="up"`.

Certificate denominator audit (`certificate_denominator_audit`): the
per-seed cost-partitioned duals all fail closed on the drift cap in this
design (`dual_certificates_passed_count: 0`), so no certificate `*_q` fields
exist; the exact per-seed drift inputs (exact `Fraction.from_float` of the
recorded wave R^2 values, no 1e-6 rounding) measure a max denominator of
53 bits. No 20-bit claim is made for them — the 20-bit figure applies only
to the fixed-radix accumulator, by construction.

### Honest limits

- **Full-complement Haar mode is a deterministic projection.** Its probe
  energy is identical across challenge seeds and equals the plain null-space
  projection norm (measured: seed spread 0.0). "Randomisation in name only."
  It vetoes every null-space attack (100/100) but provides no per-seed
  randomness; only sub-sampled mode is genuinely randomised.
- **The Fiat-Shamir transcript is not a cryptographic commitment.** It is
  `SHA-256(colony_seed, epoch, quantized delta, verifier_nonce)`; everything
  except the nonce is known to the proposer. With a public or fixed nonce a
  rank-1 null-space attacker grinds the sub-4 challenge in a few tries
  (measured: 12). The binding holds only when the verifier draws a fresh
  nonce AFTER the proposer commits to the delta and the nonce is unknown to
  the proposer beforehand — and even then the sub-sampled (sub-4) mode still
  leaks: measured 5/100 per-submission attack successes with fresh nonces,
  because 4 probe rows cannot cover a 12-D null space. Full-complement mode
  catches 100% but is the deterministic projection above. Nothing here is
  cryptographic.
- **100/100 attack vetoes alone do not prove the gate is selective** — that is
  why false-veto rates are recorded per mode. At a fixed 0.125 tail reading
  they are 0/100, but across the whole range the static gate accepts they are
  7/100 (full-complement) and 4/100 (sub-4): the Haar gate rejects some
  updates the static gate would commit.
- **The fixed-radix quantizer bounds denominators only where it is applied**
  (the boundary audit). Certificate paths stay exact; the measured exact
  drift-input denominators reach 53 bits, and no 20-bit ceiling is claimed
  for them.
- The regime results above are unchanged from the #180-fixed run: no regime
  passes the joint gate on this design, and the v1.1 additions do not change
  that — they close the *measured boundary* (the unprobed 12-D subspace and
  the denominator blowup), not the headline scores.

## Format demonstrations

The Farkas identifiability certificates and the cost-partitioned `Fraction`
metabolic dual are **format demonstrations**, not evidence of real-world
properties: the probe readings are data-derived as described above, and the
metabolic dual charges a measured cost (`3/2` plus the rows added that wave)
rather than a constant that cannot bind; with the current R^2 it fails closed
on the drift cap.

License: evidence CC-BY-4.0 as with the other papers. Synthetic-world
mathematics throughout. No study data, no patients, no clinical claims.
