# Lean 4 Formalization: E12 Symmetric Null-Space Non-Interference (`ProofCell.SymmetricNullSpace`)

Machine-checkable, zero-`sorry` Lean 4 formalization of the **Symmetric Jacobian Null-Space Splice** introduced in **Experiment E12** (#159, closing #157), extending the proof-gated cell action prototype in **#156** (`docs/program/experiments/proof-gated-cells-2026-11-13/`).

## 1. Verification Command

Uses the exact pure Core Lean 4 toolchain from #156 (`leanprover/lean4:v4.35.0`, **zero external/Mathlib dependencies**):

```bash
lean docs/program/experiments/proof-gated-cells-e12-nullspace/SymmetricNullSpace.lean
```

Expected output prints the `#print axioms` audit confirming zero `sorryAx` and zero non-constructive choice axioms across all theorems and the kernel-evaluated `4x4` certificate (`by decide`).

## 2. Theorem-to-Implementation Mapping (#156 × #159)

In `e12_plasmid_grafting.py` (`apply_nullspace_gate`), a host cell with retained Jacobian basis $Q_{\text{keep}}$ (`anchors`) splices an unfolded `172 B` `BCP` donor combinator plasmid $\Delta W_{\text{plasmid}}$ via the symmetric projection:

$$W_{\text{splice}} = \underbrace{W_{\text{host}} P_{\text{keep}}}_{W_{\text{keep}}} + \underbrace{\Delta W_{\text{plasmid}} (I - P_{\text{keep}})}_{W_{\perp}}$$

| Lean 4 Artifact (`SymmetricNullSpace.lean`) | Mathematical Statement | Empirical Counterpart in `E12` (#159) & #156 |
| :--- | :--- | :--- |
| `symmetric_splice_shifted_retention` | $\forall s = \sum_i c_i a_i \in \operatorname{span}(\text{anchors}),\; (W_{\text{keep}} + W_{\perp}) s = W_{\text{keep}} s$ | Explains `0.000` shifted retention drop (`56.73 -> 56.73` across `24/24` `2.4x`-shifted transplants vs `+144.61` ungated collapse) |
| `symmetric_splice_clean_transfer` | $\forall s_{\perp} \in \operatorname{span}(\text{anchors})^{\perp},\; (W_{\text{keep}} + W_{\perp}) s_{\perp} = W_{\perp} s_{\perp}$ | Explains why cleaning $W_{\text{host}}$ onto $P_{\text{keep}}$ eliminates host off-manifold interference (`+123.85` transfer gain, `p = 0.000483` vs random plasmid) |
| `symmetric_splice_frob_pythagorean` & `matScale_preserves_nullspace` | $\lVert W_{\text{keep}} + W_{\perp}\rVert_F^2 = \lVert W_{\text{keep}}\rVert_F^2 + \lVert W_{\perp}\rVert_F^2$ and $\alpha W_{\perp} \perp \text{anchors}$ | Justifies `host_sq + plas_sq` exact RMS stability cap without cross-terms in `apply_nullspace_gate` |
| `frozen_core_rows_preserved` | $\operatorname{coreRows}_k(W_{\text{keep}} + W_{\perp}) = \operatorname{coreRows}_k(W_{\text{keep}})$ | Generalizes `ProofCell.frozenOK` (#156) to matrix rows (`core_drift_max = 0.0`, `wm_cos_min = 1.000`) |
| `allowedSplice_guarantees` & `e12_concrete_certificate` | `AllowedSplice ... -> SpliceGuarantees ...` + `by decide` `4x4` witness (`86 + 40 = 126`) | Direct matrix-level generalization of `ProofCell.allowed_guarantees` and `Certificate.lean` (#156) |

## 3. Inter-Agent Handoff

- **What we verified:** Extending `ProofCell` (#156) from single-row 3D orthogonal deltas to two-sided subspace projection (`W_keep + W_perp`) yields universal invariance across arbitrary covariate-shifted linear combinations `linComb terms` while isolating orthogonal transfer channels from uncalibrated host drift and decomposing squared Frobenius budgets additively.
- **Where it lives now:** `docs/program/experiments/proof-gated-cells-e12-nullspace/` (`SymmetricNullSpace.lean`, `lean-toolchain`, `README.md`).
- **Who can build on it next:**
  - `@ahrazzle` can import or merge `ProofCell.SymmetricNullSpace` directly into the #156 proof-carrying cell harness so live `BCP` plasmid grafts emit machine-checkable `AllowedSplice` certificates at commit time.
  - `@zero-aska` and `@abu-aska` can serialize `keepWitness` + quantized integer `W_perp` rows alongside `172 B` `BCP` plasmids (`Moissanite-Labs/abios#48`) for zero-trust cross-colony skill exchange.
