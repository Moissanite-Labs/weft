# Results E12: Horizontal BCP Combinator-Plasmid Grafting Under a Jacobian Null-Space Gate

**Date:** 2026-11-12  
**Author:** `mithrax-exo` (AI-assisted research & execution via Gemini, closing #157)  
**Reproduction:** `python3 docs/program/experiments/e12-plasmid-nullspace-graft-2026-11-12/e12_plasmid_grafting.py` (~33s offline for full 24 transplants; `--unit` runs in `0.008s`).

## 1. Quantitative Results (`N = 12` Independent Colony Pairs = 24 Bidirectional `256x256` Splices)

| Arm (`0` Recipient Steps) | Wire Bytes | Native IID | Native `2.4x` Shifted (Drop) | Transferred IID (Gain vs Pre) | `p` vs Pre / Permuted / Rand | Joint Pass (`>=+20` & `<2` drop) | Max `\|\|ΔW·Q_keep\|\|_F` | Core Drift / WM / Exec |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`A0_Host_PreGraft`** | `0 B` | `+86.59` | `+56.73` (`0.000`) | `-84.53` (`+0.00`) | `1.0000 / 0.0057 / 0.3935` | `0 / 12` | `0.0` | `0.0 / 1.0 / 100%` |
| **`C1_Raw_Delta_Permuted`** | `196,608 B` | `+84.01` | `+52.36` (`4.367`) | `-85.69` (`-1.16`) | `0.0057 / 1.0000 / 0.4056` | `0 / 12` | `0.1376` | `0.0 / 1.0 / 100%` |
| **`C2_Random_Plasmid_NullGate`** | `172 B` | `+86.59` | `+56.73` (`0.000`) | `-125.87` (`-41.34`) | `0.3935 / 0.4056 / 1.0000` | `3 / 12` | `< 1e-14` | `0.0 / 1.0 / 100%` |
| **`G1_Ungated_BCP_Graft`** | `172 B` | `-20.75` | `-87.88` (`144.612`) | `-46.57` (`+37.97`) | `0.0979 / 0.0885 / 0.0565` | `0 / 12` | `1.3086` | `0.0 / 1.0 / 100%` |
| **`G2_NullSpace_BCP_Graft`** | **`172 B`** | **`+86.59`** | **`+56.73` (`0.000`)** | **`+39.32` (`+123.85`)** | **`0.0074 / 0.0068 / 0.0005`** | **`10 / 12`** | **`< 1e-14`** | **`0.0 / 1.0 / 100%`** |

## 2. Verdict Against Preregistered Falsifiers (`PREREG-E12.md`)
- **H-E12-A:** **HELD** — `G2` lifts 0-shot transferred skill by `+123.85` pts (`-84.53 -> +39.32`, two-sided `p = 0.007437` vs `A0`, `p = 0.006821` vs `C1_Raw_Delta_Permuted`, `p = 0.000483` vs `C2_Random_Plasmid_NullGate`) at **`1,143.1x` wire compression** (`172 B` vs `196,608 B`).
- **H-E12-B:** **HELD** — Ungated splicing (`G1`) collapses under `2.4x` distribution shift (`+56.73 -> -87.88`, `0/12` passing), reproducing #146's shifted-retention wall, whereas symmetric Jacobian Null-Space splicing (`W_pl = W_host P_keep + ΔW_plasmid (I - P_keep)`) holds shifted retention at **`+56.73` (`0.000` drop, `p = 0.000384` vs `G1`)** with **`10 / 12` independent colony pairs** passing both transfer and shifted-retention gates.
- **H-E12-C:** **HELD** — `null_residual < 1e-14`, `core_drift == 0.0`, `watermark_cos == 1.0`, and `WEFT-IC-EXEC-V2:` verification `24/24`.

## 3. Ethos Handoff (What / Where / Who)
- **What we learned & verified:** Two requirements must hold jointly for zero-shot horizontal skill splicing: (1) projecting the incoming plasmid onto `ker(J_keep)` (`I - P_keep`) so it cannot perturb retained skills off-distribution, AND (2) cleaning the host's dormant off-manifold drift out of `ker(J_keep)` (`W_host P_keep`) so untested host weights do not fight the incoming plasmid.
- **Where it lives:** `docs/program/experiments/e12-plasmid-nullspace-graft-2026-11-12/` (`PREREG-E12.md`, `RESULTS-E12.md`, complete untruncated `e12_plasmid_grafting.py`), plus interactive visual simulations in `Moissanite-Labs/weft-eido`.
- **Who builds next:** `@ahrazzle` / `@zero-aska` can formalize the symmetric subspace non-interference identity `(W_host P_keep + ΔW (I - P_keep)) s == W_host s` in the Lean cell prototype (#156) and wire `apply_nullspace_gate` into `weft/runtime/invariants`.
