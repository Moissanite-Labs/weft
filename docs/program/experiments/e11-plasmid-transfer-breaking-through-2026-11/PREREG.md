# Preregistration: E11 horizontal plasmid transfer (Breaking through)

Date: 2026-11-13 UTC  
Status: Preregistered **before** any E11 numerical outcomes in this directory.  
Issue: [#149](https://github.com/Moissanite-Labs/weft/issues/149) (horizontal plasmid / null-space gate).  
Lineage: [#144](https://github.com/Moissanite-Labs/weft/issues/144), [#145](https://github.com/Moissanite-Labs/weft/issues/145), PRs [#140](https://github.com/Moissanite-Labs/weft/pull/140), [#141](https://github.com/Moissanite-Labs/weft/pull/141), [#143](https://github.com/Moissanite-Labs/weft/pull/143), [#146](https://github.com/Moissanite-Labs/weft/pull/146), [#147](https://github.com/Moissanite-Labs/weft/pull/147), [#148](https://github.com/Moissanite-Labs/weft/pull/148).

This E11 is the **gauge / plasmid** experiment named in #149. It is unrelated to the razi-cells laws record (agent-colony E11 in PR #107).

## Epistemic framing

All thresholds below are **registered commitments** for this toy pilot. Satisfying them would support a narrow, simulator-only claim. Failing them is an equally valid outcome. Tags used in the report: `[measured]`, `[derived]`, `[hypothesis]`, `[speculative]`.

## Hypothesis (primary)

`[hypothesis]` A skill learned by cell A can be exported as a compact task delta, aligned to a differently seeded or neuron-permuted cell B, and projected into the null space of B's kept-capability Jacobian, so B gains the new skill in **zero** gradient steps while kept skills stay within tolerance under input distribution shift.

## Toy substrate (fixed before data)

- **Architecture:** 8-D input, 16 hidden ReLU units, 4 scalar logits (3 kept binary tasks + 1 new binary task). Tanh on logits only at readout for stability; labels are ±1.
- **Core freeze:** incoming weights and biases to hidden units `0..3` are non-plastic (Astra-style partition, `[derived]` from PR #146 protocol spirit).
- **Cell A:** train on kept tasks, then fine-tune **only** on the new task (500 steps max, fixed learning rate).
- **Cell B:** train on kept tasks only to convergence criterion; never trained on the new task in any transfer arm.
- **Pairing modes per seed:**
  1. `cross_seed` — independent initialization for A and B.
  2. `permuted_sanity` — B equals A's pre-new-task weights with a hidden-unit permutation (known alignment oracle).
- **Seeds:** integers `17, 29, 43, 101, 202` (five seeds, `[derived]` from Astra family protocol habit; enough for spread, CPU-fast).

## Arms (applied to B, zero training steps on B except none)

| Arm | Description |
|-----|-------------|
| `raw_coord` | Add A's plastic delta in B's coordinates. |
| `perm_taskvec` | Hungarian activation matching (Git Re-Basin style) on shared probe inputs, then add aligned delta. |
| `null_only` | Project A's delta into `ker(J_keep_B)` without permutation alignment. |
| `plasmid` | Permutation alignment, then project into `ker(J_keep_B)`; optional rank-1 probe correction for new-task output (basis-free I/O delta). |
| `frobenius_gate` | `raw_coord` delta clipped to Frobenius ball `‖ΔW‖_F ≤ R` with `R` matched to `‖ΔW_A‖_F` (C2-style coordinate gate, not null-space). |

## Kept-capability Jacobian (registered definition)

`[derived]` On `N_j = 256` IID probe inputs in `[-1, 1]^8`, for each kept task `k ∈ {0,1,2}`, stack rows of `∂ logit_k / ∂ θ_plastic` (autograd). Let `J_keep` be the vertical concatenation (shape `3·N_j × P`).  
Null-space update: `Δθ ← (I - J_keep^+ J_keep) Δθ` (Moore–Penrose).  
Certificate: `‖U^T Δθ‖_F` where `U` is an orthonormal basis for `row(J_keep)` from thin SVD.

## Five shifted retention probes (spirit of PR #146)

All probes use 512 fresh inputs. Retention for kept task `k` on probe `p`: accuracy within **0.10** absolute of B's pre-transfer accuracy on the same probe (non-inferiority style, `[derived]`).

| Probe | Transform on `x` |
|-------|------------------|
| `iid` | uniform on `[-1,1]^8` |
| `scale_1p5` | `1.5 * x` |
| `shift_pos` | `x + 0.3` |
| `rotate` | fixed orthogonal mix (seed-independent matrix) |
| `sparse` | `x` with coordinates 4..7 zeroed |

**Shifted pass count:** number of probes in `{scale_1p5, shift_pos, rotate, sparse}` that pass for **all three** kept tasks (max 4; `iid` reported separately).

## Pre-registered pass bars

### Arm `plasmid` (primary criterion for E11)

| Metric | Pass threshold |
|--------|----------------|
| New-task accuracy on B | ≥ 0.80 mean over seeds, and ≥ 3/5 seeds ≥ 0.80 |
| IID kept-task retention | 3/3 tasks within 0.10 acc drop vs pre-transfer |
| Shifted retention | ≥ 3/4 shifted probes pass (all kept tasks) |
| Training steps on B | = 0 |
| Non-interference certificate `‖U^T Δθ‖_F` | ≤ 1e-3 for every seed |
| Permuted sanity (`permuted_sanity` only) | new-task acc ≥ 0.95 and all retention probes pass |

### Secondary (comparative, not win/loss for E11 overall)

Report all arms against the same metrics. No hypothesis is registered that `raw_coord` or `frobenius_gate` must fail; those are baselines from prior work `[measured]` in #146/#148 narratives.

## Nonlinear drift (explicit)

`[hypothesis]` Null-space guarantee is first-order. Report post-transfer **linearization error**: mean `|Δf_k(x)|` predicted by `J_keep Δθ` vs actual logit change on new-task held-out inputs.

## Gramian alignment failure

If activation matching correlation `< 0.3` median across hidden units on probes, record `gramian_alignment_failed: true` for that seed (finding, not protocol violation).

## Analysis outputs

Script: `run_e11.py`.  
Artifact: `results/e11_results.json` with per-seed, per-arm, per-probe tables and aggregate means/stds.

## Stop / scope rules

- Toy only unless `permuted_sanity` passes all plasmid bars on every seed (then a single larger-width run may be noted as exploratory in README only — not executed in this PR unless already complete).
- No external publication; repo-private record only.
