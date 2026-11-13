# E09 — Invariant-gated micro-cell organisms

Date: 2026-11-12. Follow-on to E08 (zero-lexicon cells, PR #141) and issue #142 (program: invariant-gated micro-model organisms). Exploratory record.

> Correction, 2026-11-12 (review of PR #143). The sections below are the design as registered and are left unchanged. The organism that `microcell.py` actually runs, and that produced every committed log, differs from them:
>
> - Hidden layer: 768 units built from a frozen 256x256 watermarked core `wc` (no row of it is ever written) and a 512x256 periphery `wp`. The watermark is embedded in rows 0..191 of `wc`.
> - Plasticity: only `wp` (512x256) is mutated. `W_mu`, `W_sg` and all four bias vectors keep their initial values. There is no plastic head.
> - Action: `u = mu = tanh((W_mu @ H + b_mu) / 2)`, deterministic. The `log sigma^2` output is computed and discarded; no stochastic arm was run.
> - Gate as run in the committed logs: periphery Frobenius drift vs `wp_base` <= 120 plus the 1.01 probe rule. The watermark call compared `wc` with itself and did not gate acceptance, so the logged `wm_drift` of 0 was not an independent check. From this correction on, `microcell.py` keeps `wc_base` at init, logs `core_drift = ||wc - wc_base||`, calls `watermark_verify(wc_base, wc, ...)` and rejects a candidate when core drift is not exactly 0.0 or the cosine is below 0.85.
> - Episode state: the committed logs were produced without resetting each cell's previous action `_u` between episodes and probes. The corrected script resets it; `--legacy-u-leak` reproduces the committed logs.
> - The GRU arm (1b) and the shuffled-decoder control were not run. The frozen control was run for seed 20261112 only.

## Research question

The E08 matrix organism learns under the invariant gate but plateaus early (antithetic ES finds nothing past ~gen 11 to gen 13 in 3 seeds). It is a ~130-parameter actor. This experiment asks: with ~800K parameters of real nonlinear wiring, gated by the same plasticity mask, watermark, and selection rule, does an organism adapt more, faster, and without saturating?

## Arms

Primary (Arm 1, custom micro-cell):

- Architecture. One-layer MLP-ish recurrent-free cell to start (GRU as the second variant): `enc = phi(s)` 256-dim feature map from E08; hidden layer `H = relu(W1·enc + b1)`, 768 units; output head emits `mu in R^2` and `log sigma^2 in R^2` (thrust direction distribution). Action `u` drawn as `mu` (deterministic) for the control regime, and `mu + sigma*epsilon` for a stochastic probe arm. tanh squashing at the output boundary same shape as E08's `tanh(z/2)`.
- Init. `W1` seeded normal(0, 0.02); `W2` (head) same.
- Plasticity. First 192 rows of `W1` frozen (25%). Remaining 576 rows of `W1` and all of `W2`, `b1`, `b2` plastic. Watermark embedded in the frozen `W1` band using `watermark_embed` from the ported `plasm_np`.
- Gate. Same as E08: Frobenius drift vs `W_base` <= 120 (R_INVARIANT), watermark cosine >= 0.85, core drift exactly 0, plus probe rule: commit iff probe reward >= 1.01 * parent probe.

Secondary (Arm 1b, same shape but GRU): two stacked GRU cells 768 grid, same mask/watermark/gate. Tests whether recurrent state helps under partial observability (field phase).

## Environment (unchanged from E08)

Torus L=20; `H(p,t) = cos(0.35x - 0.6t)·sin(0.22y + 0.6t)`; sensors `s` (16-dim, same layout); thrust from the head; collision/metabolic penalties as in E08; height-functions identical so any delta is attributable to the organism, not the world.

## Controls

- Frozen custom cell (mask never opens): tests that adaptation is reading signal, not drift.
- Random decoder variant (`NOLEX_PHI_SHUFFLE`-equivalent shuffle, pinned seed): tests head-structure dependence.
- E08 matrix organism as the reference baseline (re-run in this seed family for the same seeds).

## Metrics (registered before any run)

Primary:

- M1 mean episode return by generation for 40 generations, 3 seeds (20261112, 20261113, 20261114).
- M2 wall-clock steps to first commit per seed, and commits per 10 generations.
- M3 collisions per episode (zero enforcement same conditions as E08).
- M4 watermark retention cosine each generation; core drift exactly 0.0.

Secondary:

- M5 Frobenius distance W_gen - W_0 by generation.
- M6 lineage divergence L2 between independent seeds, and sibling divergence from a shared parent after a mitosis commit.

Falsifiers:

- F1: no arm reaches mean return above the frozen control on mean across 3 seeds by generation 40. Publish as a miss.
- F2: watermark retention cosine drops below 0.85 in any seed (absolute gate failure — published as failure, not quietly excluded).
- F3: rejection rate above 20% of candidate commits in any seed.

## Deliverables

`docs/program/experiments/micro-cell-2026-11-12/` with this design, prereg with verdicts after the run, logs, decoder fingerprint, port of `plasm_np` (or import), seed-stamped runs, and a PR through review.
