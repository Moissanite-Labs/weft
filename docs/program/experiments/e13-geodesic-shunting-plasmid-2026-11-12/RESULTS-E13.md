# RESULTS-E13: Cortical Lateral Shunting Inhibition + Geodesic Fiber Retraction Achieves 12/12 Gauge-Free Skill Splicing

- **Date Executed:** 2026-11-12, certificate regenerated after the review wording pass (`wall_seconds = 65.87s`; headline numbers unchanged from the original 39.7s run, $N = 12$ independent confirmatory seeds)
- **Script:** `python3 docs/program/experiments/e13-geodesic-shunting-plasmid-2026-11-12/e13_geodesic_plasmid.py`
- **Raw Certificate:** `e13_certificates.json` (rounded summaries plus raw per-seed measurements)
- **Related to:** [Issue #149](https://github.com/Moissanite-Labs/weft/issues/149), [PR #159](https://github.com/Moissanite-Labs/weft/pull/159) ([Issue #157](https://github.com/Moissanite-Labs/weft/issues/157)), and [PR #160](https://github.com/Moissanite-Labs/weft/pull/160)
- **Series id:** This record uses the plasmid-grafting series id E13, following [PR #159](https://github.com/Moissanite-Labs/weft/pull/159)'s E12. The program-card id E13 in `docs/program/experiment-cards.md` is a different protocol ("Executable authority and governance"), and the razi-cells ledger has a separate E13 assay.
- **Disclosure:** AI-assisted research & execution via Gemini task agent per [`CONTRIBUTING.md`](https://github.com/Moissanite-Labs/weft/blob/main/CONTRIBUTING.md).

## 1. Key Discovery: Why Excitatory Null-Space Splicing Hits a Closed-World Wall (and How Lateral Shunting Inhibition Breaks It)

Evaluating 12,488-parameter (`49,952 B`) 3-layer smooth `GELU` organisms (`24 -> 96 -> 96 -> 8`) initialized from independent random seeds exposed a fundamental neuro-computational barrier not visible in linear toy models. Donors are permutation-scrambled after training (an exact hidden-unit symmetry, so `donor.predict` is unchanged). The host is left unscrambled. `PREREG-E13.md` section 1, item 1 says organisms undergo explicit hidden-layer permutation scrambling; this run applies that scramble only to donors.

1. **Closed-World Host Hallucination (`Pre-Graft Novel R² = -0.4792 ± 0.1146`):** A host organism trained only on native skills `{0, 1}` never observes novel context `2` as inactive background; when context `2` arrives, its 80 active native neurons hallucinate default Skill-0 nonlinear dynamics across $\mathbb{R}^8$. Consequently, purely excitatory dormant-slot + geodesic splicing (`A3_gfpt_geodesic_excitatory_only`) lifts shifted novel $R^2$ by $+1.0178$ (`-0.4792 -> +0.5386 ± 0.0384`) while preserving native skills (`0.8765`), yet stalls well below Donor's own shifted ceiling (`0.8563`), scoring `0/12` against the strict `R² >= 0.70` bar.
2. **Cortical Lateral Shunting Inhibition + Gauss-Newton Geodesic Retraction (`A4_gfpt_shunting_geodesic`):** Wiring a single inhibitory synaptic column (`W2[native_m2, slot_m1[0]] = -2.4`) from the plasmid's context-gate receptor into the host's native Layer-2 channels shunts native closed-world hallucinations deep into `GELU` quiescence (`z2 << -3`) whenever the grafted skill activates, while 4-step Minimum-Norm Gauss-Newton Geodesic Fiber Retraction cancels the quiescent resting offset on native contexts (`4.47x` lower host drift than flat tangent `A2`, winning `12/12` seeds). `A4` shifted novel $R^2$ is **`0.8565 ± 0.0202`** against the donor shifted OOD mean of **`0.8563`**, inside a **`1,456 B` `BCP-FP16` neural plasmid (`34.31x` wire compression)** with **`12/12` joint shifted passes** ($p = 0.0004883$).

### Mechanism

The splice is given `skill_idx`. The plasmid writes gate column `W1_p[0, 16+skill_idx] = 2.0`. The splice then zeros the host's native weights on that column and, when shunting is on, sets `W2[native_m2, slot_m1[0]] = -2.4`. Whitened Ridge/Procrustes alignment is measured on unlabeled probes and is not applied in the splice. Donor scrambling, as above, is a post-training symmetry. The host remains in its trained coordinates.

## 2. Confirmatory Single-Graft Results ($N = 12$ Seeds, Evaluated Under OOD Shift)

| Arm | Shifted Native $R^2$ (Mean ± SD) | Shifted Novel $R^2$ (Mean ± SD) | Host Anchor Drift RMS | Joint Shifted Passes |
| :--- | :---: | :---: | :---: | :---: |
| `pre_graft_host` (Native `[0,1]` only) | `0.8889 ± 0.0085` | `-0.4792 ± 0.1146` | `0.000000` | `0/12` |
| `A0_raw_coord_delta` ([PR #146](https://github.com/Moissanite-Labs/weft/pull/146) coord copy) | `0.2495 ± 0.0376` | `-0.0306 ± 0.0248` | `1.769500` | `0/12` |
| `A1_hard_readout_nullspace_160anchors` (`#149` F2) | `0.8889 ± 0.0085` | `-0.4792 ± 0.1146` | `0.000000` | `0/12` (0.0 nullity!) |
| `A3_gfpt_geodesic_excitatory_only` (Shunt off, geodesic on) | `0.8765 ± 0.0101` | `0.5386 ± 0.0384` | `0.048911` | `0/12` (host misfire) |
| `A2_gfpt_flat_no_retraction` (Shunt on, flat tangent; `#159` analog) | `0.8709 ± 0.0121` | `0.8573 ± 0.0203` | `0.220082` | `11/12` (1 drift miss) |
| **`A4_gfpt_shunting_geodesic` (Shunt on, geodesic on)** | **`0.8757 ± 0.0096`** | **`0.8565 ± 0.0202`** | **`0.049253`** | **`12/12` ($p = 0.0004883$)** |

*(Donor reference shifted OOD novel $R^2$: `0.8563`. The `C2` count `12/12` is this script's local Python mirror at `r_invariant=120`, the default in `weft_invariants.h`, and is not a call to that header. The two-sided fair-coin p-value is stored only when the A4 pass count equals `n_seeds`; the preregistered `>= 11/12` bar therefore emits no p-value.)*

## 3. Falsifiers and the Multi-Generation Cascade (Related to [PR #160](https://github.com/Moissanite-Labs/weft/pull/160))

- **Falsifier 1 (Second-Order Curvature Drift):** Flat tangent splicing (`A2`, shunt on) incurs `0.220082` RMS host drift on curved `GELU` layers and drops 1 seed (`11/12`, mirroring [PR #159](https://github.com/Moissanite-Labs/weft/pull/159)'s `10/12`). Four-step Gauss-Newton Geodesic Retraction (`A4`) cuts drift **`4.47x`** to `0.049253` (`12/12` seeds improved) and achieves `12/12` joint passes.
- **Falsifier 2 (Capacity Exhaustion at 160 Anchors > 96 Hidden Width):** Exact readout null-space (`A1`) collapses to **`0.00` dimensions** across all 12 seeds. The reported `A3_spectral_fisher_nullity_mean` of **`43.75`** is `M2` (96) minus the 99.5% energy rank of Layer-2 activations `H2` on the A4 splice; the graft overwrites the lowest Fisher-score neurons.
- **Falsifier 3 (Unlabeled Cross-Seed Representation Alignment):** Raw hidden-unit coordinate correlation across independent donor-scrambled organisms is **`0.1498`** (`< 0.30`), whereas unlabeled Whitened Ridge/Procrustes alignment on 256 ambient probes achieves **`0.9304` median correlation** on fresh shifted inputs. That correlation is a side measurement; it is not used in the splice.
- **Multi-generation 5-skill cascade (`G0 -> G1 -> G2 -> G3`), related to [PR #160](https://github.com/Moissanite-Labs/weft/pull/160):** this script does not rerun that Astra/Lean pilot. The cascade here is a 12,488-parameter synthetic analogue.
  - **Ungated local-validation teacher:** keeps a readout fit to 8 noisy labels when that fit has lower local validation MSE, collapsing 5-skill shifted $R^2$ across generations: `0.1188 (G0) -> -0.5348 (G1) -> -3.4564 (G2) -> -14.2289 (G3)` (`0/12` monotonic seeds).
  - **Split-shift generalization gate:** the implemented loss is shifted MSE + `0.012 *` Frobenius + `3 *` keep MSE (the preregistration called this gate "Fisher-MDL"; the loss has no Fisher term). Strictly monotonic `G0 < G1 < G2 < G3` on **`12/12` seeds**, climbing across three distinct donor grafts from **`0.1188 (G0) -> 0.3408 (G1) -> 0.5180 (G2) -> 0.8266 (G3)`** on all 5 skills simultaneously under OOD shift.

## 4. Honest Limitations & Next Falsifier (`E14`)

- While organisms here are `12,488`-parameter smooth `GELU` MLPs trained independently from scratch via Adam without shared coordinate bases, task contexts are still represented in observed input channels rather than inferred purely from token sequence history. The natural next step (`E14`, [Issue #142](https://github.com/Moissanite-Labs/weft/issues/142)) is testing Lateral-Shunting + Geodesic Fiber Retraction inside self-attention / SwiGLU blocks of `TinyStories-2M` / `Pythia` micro-models where context gates emerge endogenously in residual-stream attention heads.
