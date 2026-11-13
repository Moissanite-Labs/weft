# Preregistration E12: Horizontal BCP Combinator-Plasmid Grafting Under a Jacobian Null-Space Gate

**Issue:** #157 (building on #145, #146, #153, and #155)  
**Scale & Sample Unit:** `N = 12` independent colony seeds (`20261112..20261123`), `df = 11` two-sided paired `t`-tests over bidirectional transplants (`A -> B` and `B -> A` averaged within seed = 24 recipient transplants at `256x256` = 65,536 weights/cell, `0` recipient training steps).

## Hypotheses & Pass Criteria
- **H-E12-A (0-Shot Permuted Transfer):** `G2_NullSpace_BCP_Graft` (`172 B` plasmid) beats `A0_Host_PreGraft`, `C1_Raw_Delta_Permuted`, and `C2_Random_Plasmid_NullGate` on held-out transferred skill (`two-sided p < 0.01`).
- **H-E12-B (Shifted Retention Rescue):** Under `2.4x` amplitude surge + `m=5` out-of-band turbulence, `G1_Ungated_BCP_Graft` degrades native skill due to ~45% `m=1` harmonic overlap, whereas `G2_NullSpace_BCP_Graft` preserves native shifted skill (`two-sided p < 0.01` vs `G1`, and `>= 9/12` seeds passing joint `>= +20 pt` transfer gain + `< 2.0 pt` shifted-retention drop).
- **H-E12-C (Algebraic Non-Interference & Substrate Invariants):** `||ΔW_proj Q_keep||_F < 1e-11`, `core_drift == 0.0`, `watermark_cos == 1.0`, and `verify_execution_record == True` across 24/24 transplants.
