# Experiment E10: Scaling Micro-Cells (#142/#143) & Purely Statistical Causal/KL Entities (#141)

**Date:** 2026-11-12
**Author:** `mithrax-exo` (AI-assisted research & execution via Gemini, building on #140, #141, #142, and #143 by @ahrazzle and audits by @zero-aska)
**Status:** Track A executed across `N = 12` independent colony seeds (`df = 11`, two-sided paired `t`-tests). Core-drift norm is `0.0` on every run because updates write only `w1[h_core:]` and `w2[:, h_core:]`. Watermark cosine is measured against the saved core response `w1[:h_core] @ trig` and is `1.0` (within `2e-12`) for the same reason.

## Track A: Why E09 Micro-Cells Missed (#143) & What Unlocks `+26.9%` (`12/12` Seeds)

In #143 (`E09`), a frozen-core + plastic ReLU MLP emitting `(mu, log sigma^2)` regressed on H1/H2 under the 24-step `t=1000` probe, leaving open whether matching the 80-step task horizon alone fixes micro-cell plasticity (#142). We tested **four arms across `N = 12` independent colony seeds (`20261112..20261123`, 40 generations)**. `probe` scores a `Mismatch_24_t1000` generation with one 24-step episode at `t0=1000`, and scores a matched-arm generation as the average of two 80-step episodes at `t0=0` (`e10_runner.py`, function `probe`).

| Micro-Cell Arm (`N = 12` Seeds) | Mean Colony Return | Mean of seed-wise `%` change | Seeds Improved | Gain vs Frozen (two-sided `p`) | Gate Reject `%` | Core Drift / WM Cos |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **`Frozen_Control`** | `32.5814` | `0.00%` | `0 / 12` | `0.0000` (`1.000000`) | `0.00%` | `0.0 / 1.0` |
| **`Mismatch_24_t1000`** (#143 rule) | `32.6315` | `+2.61%` | `6 / 12` | `+0.0502` (`0.975264`) | `93.44%` | `0.0 / 1.0` |
| **`Matched_80_Unscaled`** (horizon fix only) | `33.2787` | `+4.74%` | `8 / 12` | `+0.6973` (`0.731146`) | `90.83%` | `0.0 / 1.0` |
| **`Matched_80_RMS_Antithetic`** (bundled RMS rule) | **`40.7979`** | **`+26.92%`** | **`12 / 12`** | **`+8.2165` (`0.000078`)** | **`12.94%`** | **`0.0 / 1.0`** |

The `+26.92%` figure is the mean of the twelve seed-wise percent changes `(last - first) / first`. The ratio of the RMS and frozen mean returns is `40.7979 / 32.5814 - 1 = 25.22%`. Per-seed returns, commit counts, and rejection rates are in `track_a_per_seed.json`.

### Key Takeaway for Issue #142 (Before Running TinyStories-2M)
1. **Horizon matching (`steps=80`) is necessary but not sufficient:** `Matched_80_Unscaled` reduces seed regressions (`6/12 -> 4/12`), yet stalls at `+4.74%` (`p = 0.731`).
2. **Why unscaled Frobenius gates choke micro-models (`O(1/sqrt(P))` collapse):** A fixed Frobenius radius `||W - W0||_F <= R` shrinks per-synapse movement by `1/sqrt(P_plastic)` as parameter count grows (`90.83%` gate rejections on this MLP). Unscaled uses radius `3.80`, two independent scales `0.045` and `0.095`, and a per-agent `1.01` rule.
3. **The bundled RMS arm** (`e10_runner.py` lines 104-126) combines radius `0.22 * sqrt(1280) = 7.871`, plastic steps `0.045` (on `w1`) and `0.11` (on `w2`), momentum `0.35`, a sum threshold of `1.008`, and commitment of the first sign in `(+1, -1)` that clears the threshold. This combination lifts mean return by **`+26.92%`** (mean of seed-wise percent changes; ratio of means `25.22%`; `12/12` seeds positive; two-sided `p = 7.8e-5` vs frozen, `p = 0.0014` vs `Mismatch_24_t1000`), drops gate rejections to **`12.94%`**, and keeps core-drift norm at **`0.0`** because those rows are never written. These figures come from this runner's 32+64 by 16 torus MLP.

## Track B: Breaking `C2` Permutation Equivalence with Purely Statistical Causal & KL Entities

Track B is pending a program that emits the six-row orthogonal-mix, KL-gate, and paired-test per-seed output. `SEEDS_TRACK_B` (`20261120..20261131`) is reserved in `e10_runner.py` for that program.

## Track C: Audit Hardening (#140 & #141)
- **Slice-local Rev-D fix:** `TestE10Invariants.test_slice_local_revd_bounds` in `e10_runner.py` is the test that calls `action_map_revd_fixed`. It maps a `k=2` slice starting at index 64 with `z[64] = 100`, asserts `|u[0]| < 1`, and checks that setting `z[:64] = 999` leaves `u` unchanged, under `u = z_s / sqrt(k + ||z_s||_2^2)`.
- **Hardened `zero_lexicon_gates.py`:** `test_strict_body_and_formula` accepts a pure-math AST body and formula, and rejects `b"..."` constants, prose `ast.arg` names, and prose `ast.alias` imports. `test_assay_goodhart_rejection` makes three assertions: it rejects an in-process constant `42.0`, rejects a `len(zlib.compress)` metric, and accepts a savings-ratio metric on a zlib script. The accepted path runs `verify_compressor_roundtrip`, which writes the script into two temporary directories and requires `dec(enc(x)) == x` on the structured, incompressible, and boundary probe corpora.

## Ethos Handoff (What / Where / Who)
- **What we verified:** The bundled RMS arm reaches a `+26.92%` mean of seed-wise percent changes (`12/12` seeds; ratio of means `25.22%`) on this runner, with RMS radius `7.871`, momentum `0.35`, sum threshold `1.008`, and first-passing-sign commitment.
- **Where it lives:** `docs/program/experiments/e10-statistical-causality-2026-11-12/` on this branch, including `track_a_per_seed.json`, plus the companion binary wire RFC in `Moissanite-Labs/abios#48`.
- **Who builds next:** `@ahrazzle` / Arm-2 TinyStories-2M (#142, #143) can drop RMS gate + antithetic A/B directly into `microcell.py`; `@zero-aska` can audit `zero_lexicon_gates.py` and the runnable `E10` scripts on this branch.
