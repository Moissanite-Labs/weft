# Preregistration E13: 3-Cell Transitive BCP Plasmid Cascades Under Composed Jacobian Flag Gates

- **Date:** 2026-11-12
- **Status:** Executed & Verified (`N = 12` seeds `20261112..20261123` x `3` cyclic triads = `36` cascades, `252` cells, `$0.00` API spend)
- **Tracking Issue & Lineage:** Closes #172; extends #155 (`E11`), #159 (`E12`), #166 (`ProofCell.SymmetricNullSpace`), and `Moissanite-Labs/abios#48`.

## 1. Falsifiable Hypotheses & Double-Dissociation Design

Across 3 independently channel-permuted `256x256` (`65,536`-weight, `64` frozen watermark rows + `192` plastic cilia rows) specialist organisms `(Cell A, Cell B, Cell C)` specialized on spatial harmonics `(S_1: k=2, S_2: k=3, S_3: k=4)` over a shared contending `k=1` carrier:

1. **H1 (Retroactive Amnesia Falsification — `G4` vs `G2_Memoryless_SingleGate`):** Repeating `E12`'s single-anchor gate `P_{Q_C}` at Hop 2 wipes Hop-1 weights in `(I - P_{Q_C})`, whereas composing `V_1 = V_0 oplus span(Q_{1,perp})` preserves Hop-1 transitive skill `S_A` (`p_Holm < 0.01`).
2. **H2 (Subspace Crowding Falsification — `G4` vs `G3_Unsketched_SVD_Crowding`):** Growing `Q_flag` from unsketched `svd(Delta W_{p_A})` locks untrained off-manifold harmonics of `p_A` and blocks Hop-2 specialist `S_B` (predicted by Lean Theorem 2 in #166), whereas attaching a `52 B` `WFSK` `int16` Fourier-Jacobian Anchor Sketch (`224 B`/hop capsule) cleans `W_{perp,1}` onto `Q_{1,perp}` and leaves `k_B` open (`p_Holm < 0.01`).
3. **H3 (Sketch-Only Hallucination Control — `G4` vs `C2_Random_Capsule_FlagGate`):** Random `172 B` `BCP` plasmids paired with the exact true `52 B` `WFSK` sketches under `G4`'s gate fail tri-skill competence (`p_Holm < 0.01`), proving the `52 B` subspace sketch carries zero motor-policy solution without the evolved `172 B` `BCP` combinator sub-graph.
4. **H4 (Permutation & Shift Robustness — `G4` vs `C1_Raw_Cascade_Permuted` & `G1_Ungated_BCP_Cascade`):** `G4` outperforms `393,216 B` raw float32 weight cascades on tri-skill competence (`p_Holm < 0.01`) and prevents `G1`'s catastrophic `2.4x`-shifted native retention collapse (`p_Holm < 0.01`), with `< 1e-12` flag null-space residual, `< 1e-12` 3-term Pythagorean Frobenius error, and `1.000000` core watermark cosine.
