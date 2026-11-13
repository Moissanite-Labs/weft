# Experiment E10: Scaling Micro-Cells (#142/#143) & Purely Statistical Causal/KL Entities (#141)

**Date:** 2026-11-12  
**Author:** `mithrax-exo` (AI-assisted research & execution via Gemini, building on #140, #141, #142, and #143 by @ahrazzle and audits by @zero-aska)  
**Status:** Executed across `N = 12` independent colony seeds (`df = 11`, two-sided paired `t`-tests) for both tracks; `core_drift == 0.0` and `watermark_cos == 1.0` across every run.

## Track A: Why E09 Micro-Cells Missed (#143) & What Unlocks `+26.9%` (`12/12` Seeds)

In #143 (`E09`), a frozen-core + plastic ReLU MLP emitting $(\mu, \log\sigma^2)$ regressed on H1/H2 under the 24-step `t=1000` probe, leaving open whether matching the 80-step task horizon alone fixes micro-cell plasticity (#142). We tested **four arms across `N = 12` independent colony seeds (`20261112..20261123`, 40 generations, exact 2-evals/gen budget)**:

| Micro-Cell Arm (`N = 12` Seeds) | Mean Colony Return | Mean `%` Change | Seeds Improved | Gain vs Frozen (two-sided `p`) | Gate Reject `%` | Core Drift / WM Cos |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **`Frozen_Control`** | `32.5814` | `0.00%` | `0 / 12` | `0.0000` (`1.000000`) | `0.00%` | `0.0 / 1.0` |
| **`Mismatch_24_t1000`** (#143 rule) | `32.6315` | `+2.61%` | `6 / 12` | `+0.0502` (`0.975264`) | `93.44%` | `0.0 / 1.0` |
| **`Matched_80_Unscaled`** (horizon fix only) | `33.2787` | `+4.74%` | `8 / 12` | `+0.6973` (`0.731146`) | `90.83%` | `0.0 / 1.0` |
| **`Matched_80_RMS_Antithetic`** (full fix) | **`40.7979`** | **`+26.92%`** | **`12 / 12`** | **`+8.2165` (`0.000078`)** | **`12.94%`** | **`0.0 / 1.0`** |

### Key Takeaway for Issue #142 (Before Running TinyStories-2M)
1. **Horizon matching (`steps=80`) is necessary but not sufficient:** `Matched_80_Unscaled` reduces seed regressions (`6/12 -> 4/12`), yet stalls at `+4.74%` (`p = 0.731`).
2. **Why unscaled Frobenius gates choke micro-models (`O(1/sqrt(P))` collapse):** A fixed Frobenius radius $\|W - W_0\|_F \le R$ shrinks per-synapse movement by $1/\sqrt{P_{\text{plastic}}}$ as parameter count grows (`90.83%` gate rejections on MLP; on TinyStories-2M it shrinks per-weight range by `>1,000x`), while unguided random `(1+1)` proposals lose gradient cosine at $O(1/\sqrt{P})$.
3. **The Scaling Fix (`H1`, `H4`, `H5` all HELD):** Normalizing the invariant gate by RMS parameter dimension ($\|W - W_0\|_F / \sqrt{P_{\text{plastic}}} \le r_{\text{rms}} = 0.22$) and pairing Plasm's cautious/exploratory slots as an **antithetic $+\delta / -\delta$ momentum probe** lifts mean return by **`+26.92%`** (`12/12` seeds positive, two-sided `p = 7.8e-5` vs frozen, `p = 0.0014` vs `Mismatch_24_t1000`), drops gate rejections to **`12.94%`**, and preserves **`0.0` core drift / `1.0` watermark cosine**.

## Track B: Breaking `C2` Permutation Equivalence with Purely Statistical Causal & KL Entities

In #141 (`E08`), `C2` (shuffled decoder) captured ~85% of `R1`'s gain (`+6.3%` gap, falsifying `H-E08-B`) because Frobenius norms are orthogonally invariant on an unconfounded torus. We tested **six zero-lexicon statistical architectures across `N = 12` colony seeds (`20261120..20261131`, 48 generations)** where every seed scrambles all 64 sensory channels via a fresh random orthogonal matrix $Q$ (`s = Q @ raw`, **zero channel-index bias**), adds 20 exogenous confounder waves + close-spawn collision penalties (`-0.50`), and unlocks target phase via active `sympathetic_ring` perturbations (`R_FROB = 2.55`):

| Statistical Architecture | Mean Return (± SD) | Gain vs `C1` (two-sided `p`) | Gain vs `C2` (two-sided `p`) | Commits | Gate Reject `%` | Collisions (First -> Last) | Mean `\|\|W-W0\|\|_F` | Core Drift / WM Cos |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`C1_Frozen`** | `-1.6171 ± 5.9392` | `0.0000` (`1.000000`) | `-3.2443` (`0.092610`) | `0.00` | `0.00%` | `4.17 -> 4.17` | `0.0000` | `0.0 / 1.0` |
| **`C2_Shuffled`** | `+1.6272 ± 7.1667` | `+3.2443` (`0.092610`) | `0.0000` (`1.000000`) | `8.08` | `79.60%` | `3.69 -> 2.40` | `2.5126` | `0.0 / 1.0` |
| **`V1_Naked_R1`** (slice-local Rev-D) | `+5.2822 ± 5.5837` | `+6.8992` (`< 0.000001`) | `+3.6550` (`0.038500`) | `7.92` | `68.84%` | `4.17 -> 1.94` | `2.4695` | `0.0 / 1.0` |
| **`V2_Parametric_KL`** ($(\mu, \log\sigma^2)$ KL gate) | `+3.9663 ± 5.7472` | `+5.5834` (`< 0.000001`) | `+2.3391` (`0.167887`) | `6.42` | `74.05%` | `4.17 -> 2.25` | **`2.1392`** | `0.0 / 1.0` |
| **`V3_Causal_SCM_Do`** (`do(u_ring)` + DAG) | **`+6.0126 ± 5.0348`** | **`+7.6296` (`0.000007`)** | **`+4.3854` (`0.006702`)** | **`8.83`** | **`58.59%`** | **`5.23 -> 1.81`** | `2.4408` | `0.0 / 1.0` |
| **`V4_Spectral_Koopman`** ($\Omega = \frac{1}{2}(S - S^\top)$) | `+5.7473 ± 5.6450` | `+7.3643` (`0.000001`) | `+4.1201` (`0.09825`) | `8.42` | `71.01%` | `4.60 -> 1.98` | `2.4781` | `0.0 / 1.0` |

## Track C: Audit Hardening (#140 & #141)
- **Slice-local Rev-D fix:** `u = z_s / sqrt(k + ||z_s||_2^2)` on each `k=2` slice bounds `||u||_2 < 1` strictly inside `(-1, 1)` regardless of orthogonal coordinates (`z[0:64]`), fixing #141's `n=256` scaling leak (`u[64] = 15.80`).
- **Hardened `zero_lexicon_gates.py`:** Whitelists pure math AST operators (`ast.Add`, etc.), blocks `b"..."` / `ast.arg` / `ast.alias` prose smuggling, and verifies compressor round-trip `dec(enc(x)) == x` across isolated temp directories + SHA-256 pigeonhole probes (defeating `echo 42` and `wc -c`).

## Ethos Handoff (What / Where / Who)
- **What we verified:** (1) Micro-cells scale past `+26.9%` (`12/12` seeds) once probe horizon, RMS Frobenius normalization, and antithetic A/B sensing are combined; (2) `V3_Causal_SCM_Do` breaks `C2` permutation equivalence (`p = 0.0067`) with zero channel-index bias.
- **Where it lives:** `docs/program/experiments/e10-statistical-causality-2026-11-12/` on this branch + companion binary wire RFC in `Moissanite-Labs/abios#48`.
- **Who builds next:** `@ahrazzle` / Arm-2 TinyStories-2M (#142, #143) can drop RMS gate + antithetic A/B directly into `microcell.py`; `@zero-aska` can audit `zero_lexicon_gates.py` and the runnable `E10` scripts on this branch.
