# E11 — Horizontal plasmid transfer (Breaking through)

Status: `[measured]` toy pilot complete, 2026-11-13.  
Issue: [#149](https://github.com/Moissanite-Labs/weft/issues/149).  
Preregistration: `PREREG.md` (committed before results).  
Runner: `run_e11.py` (NumPy, CPU).  
Raw JSON: `results/e11_results.json`.

## Context

`[derived]` Prior Astra / weight-edit work ([#146](https://github.com/Moissanite-Labs/weft/pull/146), [#148](https://github.com/Moissanite-Labs/weft/pull/148)) showed raw coordinate transfer can improve IID targets yet fail shifted retention and permutation. E11 tests whether null-space projection plus alignment beats those baselines on a toy MLP “cell.”

## Reproduce

```bash
PYTHONPATH=. python3 docs/program/experiments/e11-plasmid-transfer-breaking-through-2026-11/run_e11.py
```

## Pre-registered pass bar vs arms (cross-seed means, 5 seeds)

| Arm | New-task acc | Bar ≥0.80 | Shifted pass (of 4) | Bar ≥3.0 | IID retention | Bar 1.0 | ‖UᵀΔW‖ | Bar ≤1e-3 | B train steps |
|-----|-------------|-----------|---------------------|----------|---------------|---------|--------|-----------|---------------|
| `raw_coord` | 0.813 | pass | 1.4 | fail | 0.40 | fail | n/a | n/a | 0 |
| `perm_taskvec` | 0.918 | pass | 3.4 | pass | 1.00 | pass | n/a | n/a | 0 |
| `null_only` | 0.958 | pass | 4.0 | pass | 1.00 | pass | 1.5e-4 | pass | 0 |
| `plasmid` | 0.958 | pass | 4.0 | pass | 1.00 | pass | 1.3e-4 | pass | 0 |
| `frobenius_gate` | 0.813 | pass | 1.4 | fail | 0.40 | fail | n/a | n/a | 0 |

Bars match `PREREG.md`. `[measured]` Source: `results/e11_results.json` → `pass_bar_table`.

## Primary verdict (preregistered plasmid arm)

`[measured]` All six preregistered checks in `plasmid_primary_verdict` passed on this toy (including permuted sanity with known gauge).

## Overall E11 verdict for #149

**Mixed.**

- `[measured]` The **plasmid** arm meets every preregistered toy threshold with **zero** training steps on B.
- `[measured]` **Plasmid and `null_only` are numerically identical** on cross-seed runs (alignment is a no-op once the delta is projected into `ker(J_keep)` for this toy). The registered hypothesis that alignment *plus* null beats null alone is **not supported** here.
- `[measured]` **Raw coordinate** and **Frobenius-gated** transfer reproduce the #146 pattern: usable new-task accuracy on some seeds but **poor IID/shifted retention** (mean shifted pass 1.4/4).
- `[measured]` **Activation matching quality is poor** on cross-seed pairs (`gramian_alignment_failed: true` on all five seeds; median hidden correlation below 0.3), yet null projection still retains kept tasks — so the failure mode is recorded, not hidden.
- `[speculative]` Toy MLPs with shared ReLU features are a weak stand-in for gauge-scrambled production cells; no scale-up was run (per prereg stop rule).

## Permuted sanity

`[measured]` With a known hidden permutation, permuted B recovers donor new-task accuracy ≥0.95 and 4/4 shifted retention under `plasmid` on every seed after fixing the relu gauge convention (initial implementation had an incorrect `W2` column map; see commit history).

## Nonlinear drift

`[measured]` Post-transfer linearization MAE on the new-task logit is reported per arm in JSON (`nonlinear_drift_new_task_mae`). Null/plasmid arms stay small; raw transfer is larger.

## Epistemic limits

- Jacobian null-space safety is **first-order** `[derived]`; we report nonlinear drift explicitly.
- Hungarian alignment is a minimal Re-Basin stand-in, not a full transport map.
- No claim about LLM weight surgery, Astra teachers, or production gates.
