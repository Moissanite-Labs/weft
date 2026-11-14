# E11 — Horizontal plasmid transfer (Breaking through)

Status: `[measured]` prereg-faithful reruns, 2026-11-14.  
Issue: [#149](https://github.com/Moissanite-Labs/weft/issues/149).  
Preregistration: `PREREG.md` (unchanged).  
Runner: `run_e11.py` (NumPy, CPU).  
Raw JSON: `results/e11_results.json`.

## Context

`[derived]` Prior Astra / weight-edit work ([#146](https://github.com/Moissanite-Labs/weft/pull/146), [#148](https://github.com/Moissanite-Labs/weft/pull/148)) showed raw coordinate transfer can improve IID targets yet fail shifted retention and permutation. E11 tests whether null-space projection plus alignment beats those baselines on a toy MLP “cell.”

This rerun supersedes the closed PR [#150](https://github.com/Moissanite-Labs/weft/pull/150): the harness now matches `PREREG.md` (tanh readout, `N_j=256`, new task on logit 3, deterministic probe seeds, rank-1 probe readout correction on `plasmid`, corrected alignment diagnostics, and primary checks on every seed where registered).

## Reproduce

```bash
PYTHONPATH=. python3 docs/program/experiments/e11-plasmid-transfer-breaking-through-2026-11/run_e11.py
```

The `commit` field in `results/e11_results.json` is `git rev-parse HEAD` at run time (repository root).

## Pre-registered pass bar vs arms (cross-seed means, 5 seeds)

| Arm | New-task acc | Bar ≥0.80 | Shifted pass (of 4) | Bar ≥3.0 | IID retention | Bar 1.0 | ‖UᵀΔW‖ mean | Bar ≤1e-3 | B train steps |
|-----|-------------|-----------|---------------------|----------|---------------|---------|-------------|-----------|---------------|
| `raw_coord` | 0.617 | fail | 1.8 | fail | 0.60 | fail | n/a | n/a | 0 |
| `perm_taskvec` | 0.636 | fail | 2.8 | fail | 0.80 | fail | n/a | n/a | 0 |
| `null_only` | 0.523 | fail | 4.0 | pass | 1.00 | pass | 1.3e-10 | pass | 0 |
| `plasmid` | 0.727 | fail | 4.0 | pass | 1.00 | pass | 1.2e-10 | pass | 0 |
| `frobenius_gate` | 0.617 | fail | 1.8 | fail | 0.60 | fail | n/a | n/a | 0 |

Bars match `PREREG.md`. `[measured]` Source: `results/e11_results.json` → `pass_bar_table` (certificate bar enforced per seed in `plasmid_primary_verdict`, not on the mean).

## Primary verdict (preregistered plasmid arm)

`[measured]` `plasmid_primary_verdict`: **mixed** (3/6 checks). Passes: shifted retention mean, IID retention on all seeds, `‖UᵀΔW‖_F ≤ 1e-3` on every seed. Fails: new-task mean &lt; 0.80, fewer than 3/5 seeds ≥ 0.80, permuted-sanity gate (new-task acc &lt; 0.95 on several seeds despite full retention probes).

## Overall E11 verdict for #149

**Mixed / primary bars not met.**

- `[measured]` With the **actual new task (logit 3)**, cross-seed **plasmid** reaches mean new-task accuracy **0.727** (rank-1 probe correction helps vs **null_only** at 0.523) but **does not** meet the registered ≥ 0.80 mean or ≥ 3/5 seed rule.
- `[measured]` **Null projection** still gives **perfect shifted retention** and IID retention, with tiny non-interference certificates (~1e-10).
- `[measured]` **Raw coordinate** and **Frobenius-gated** transfer hurt retention (mean shifted pass 1.8/4) while only modestly moving the new task.
- `[measured]` After fixing the permutation correlation indexing, cross-seed activation matching is **moderate** (median correlation ~0.45–0.56; `gramian_alignment_failed: false` on these seeds).
- `[speculative]` Toy MLPs remain a weak stand-in for gauge-scrambled production cells; no scale-up was run (per prereg stop rule).

## Permuted sanity

`[measured]` Known hidden permutation: **IID + all shifted retention probes pass** for `plasmid` on every seed, but **new-task accuracy stays below the registered 0.95 bar** on seeds 17, 29, and 202 (0.78–0.80 range). Seeds 43 and 101 exceed 0.95.

## Nonlinear drift

`[measured]` Post-transfer linearization MAE on the new-task tanh readout is in JSON (`nonlinear_drift_new_task_mae`), computed with per-input first-order grads at the evaluated points (new-task rows are outside `J_keep`).

## Epistemic limits

- Jacobian null-space safety is **first-order** `[derived]`; we report nonlinear drift explicitly.
- Greedy column matching is a minimal Re-Basin stand-in, not full Hungarian / transport.
- No claim about LLM weight surgery, Astra teachers, or production gates.