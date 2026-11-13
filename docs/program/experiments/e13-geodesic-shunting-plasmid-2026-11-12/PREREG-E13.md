# PREREG-E13: Gauge-Aligned Geodesic Neural Plasmid Splicing Across Multi-Layer Organisms

- **Date:** 2026-11-12
- **Target Issues & PRs:**
  - [Issue #149 — *Breaking through*](https://github.com/Moissanite-Labs/weft/issues/149)
  - [PR #159 — *E12: horizontal BCP combinator-plasmid grafting under a Jacobian null-space gate*](https://github.com/Moissanite-Labs/weft/pull/159) ([Issue #157](https://github.com/Moissanite-Labs/weft/issues/157))
  - [PR #160 — *Run Astra controller pilot and record second-generation overfitting*](https://github.com/Moissanite-Labs/weft/pull/160)
- **Disclosure:** AI-assisted research & execution via Gemini task agent per [`CONTRIBUTING.md`](https://github.com/Moissanite-Labs/weft/blob/main/CONTRIBUTING.md).

## 1. Hypotheses & Preregistered Falsifiers

[Issue #149](https://github.com/Moissanite-Labs/weft/issues/149), [PR #159](https://github.com/Moissanite-Labs/weft/pull/159), and [PR #160](https://github.com/Moissanite-Labs/weft/pull/160) isolated five concrete barriers separating toy linear null-space demos from genuine cross-organism horizontal skill transfer:

1. **Non-Toy Gauge-Scrambled Scale:** Organisms must exceed $8 \to 16 \to 4$ toy ReLU cells, use smooth curved activations (`GELU` with non-zero $\phi''(z)$), initialize from **strictly independent random seeds**, and undergo explicit hidden-layer permutation scrambling (`24 -> 96 -> 96 -> 8`, **12,488 `float32` parameters = 49,952 B**).
2. **Falsifier 1 (Second-Order Curvature Drift):** Finite macro-steps along flat tangent projections $\ker(J_{\text{keep}}(\theta_0))$ incur $O(\|\Delta\theta\|^2)$ nonlinear drift on curved `GELU` manifolds ([PR #159](https://github.com/Moissanite-Labs/weft/pull/159)'s `2/12` misses). **Prediction:** 4-step Minimum-Norm Gauss-Newton Geodesic Fiber Retraction reduces host preservation RMS drift on $X_{\text{keep}}$ by more than $3\times$ across `12/12` seeds.
3. **Falsifier 2 (Readout Nullity Exhaustion):** At $N_{\text{keep}} = 160 > M_2 = 96$ preservation anchors, exact readout null-space `A1` collapses to **0 nullity** (`0/12` transfer). **Prediction:** Empirical Fisher Dormant-Slot Recycling + Spectral Fisher Trust-Subspace Projection retains more than $30$ effective null dimensions and succeeds at $N_{\text{keep}} = 160$.
4. **Falsifier 3 (Cross-Seed Representation Alignment):** Raw hidden-unit diagonal correlation across independent gauge-scrambled seeds will fall below `0.30`, whereas unlabeled Whitened Ridge/Procrustes transport on $256$ ambient probes will achieve median held-out correlation above `0.85` on shifted test data.
5. **Closed-World Hallucination vs. Cortical Lateral Shunting Inhibition (`A3` vs. `A4`):** Closed-world hosts trained solely on active native tasks `{0, 1}` hallucinate non-zero default native outputs (`R^2 < 0`) when novel task `2` arrives, capping purely excitatory null-space grafts (`A3`). **Prediction:** Wiring a single inhibitory synaptic column `W2[native_m2, g_plasmid] < 0` from the plasmid's context receptor silences host closed-world hallucination on novel contexts while Geodesic Retraction cancels resting leakage on native contexts.
6. **Falsifier 4 & Multi-Generation Overfitting ([PR #160](https://github.com/Moissanite-Labs/weft/pull/160)):**
   - **Single-Graft Joint Pass Criterion (evaluated strictly under OOD shift: $+0.25$ mean shift, $1.30\times$ state scale stretch, distractor shift):**
     - Shifted Native Retention: $R^2_{\text{native, after}} \ge R^2_{\text{native, before}} - 0.025$
     - Shifted Novel Skill Transfer: $R^2_{\text{novel, after}} \ge 0.70$
     - Confirmatory bar: `>= 11/12` seeds passing ($p < 0.01$ two-sided binomial sign test).
   - **Multi-Generation 5-Skill Cascade (`G0 [0,1] -> G1 [+2] -> G2 [+3] -> G3 [+4]`):** Comparing an unsplit noisy-validation teacher ([PR #160](https://github.com/Moissanite-Labs/weft/pull/160) baseline) against a **Split-Shift + Fisher-MDL Generalization Gate**, testing strict monotonicity $R^2(G_0) < R^2(G_1) < R^2(G_2) < R^2(G_3)$ on all 5 skills under OOD shift.
