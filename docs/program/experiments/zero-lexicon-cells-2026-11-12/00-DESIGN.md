# E08 — Zero-lexicon cells: entities whose carrier is a matrix, not a word

Date: 2026-11-12. Derived from a peer review (0lex) received 2026-11-12: discrete "no human words" variants can be enforced at the serializer with an executable falsifier rather than requested in prompts, and purely statistical entities make most sense as tensors living inside `weft/runtime/plasm` under a disclosed fixed ribosome decoder, with no LLM in the loop. This experiment builds the second claim and puts the first on enforcement duty in the no-language series.

Status: exploratory record. All local compute (no API credits). Prereg clicked in `PREREG-E08.md` before any run.

## Shared constants

- Substrate: `weft/runtime/plasm` (`StratifiedAppleSiliconPlasm`, `StratifiedMemoryArena`, `compute_plasticity_mask`, `embed_weight_watermark`, `verify_weight_update_safety`, `verify_watermark_retention`). Real code at the exported corpus, copied unchanged into the record (`plasm_import/`) for byte-stability of the submission.
- Arena geometry: focal 256x256 float32, sympathetic_ring 1024-float shared field across two entities, hippocampal 64x1024.
- Frozen core rows: first 64 of 256 (core_row_drift == 0 requirement).
- The disclosed fixed decoder is hash-pinned: `DECODER_SHA256 = sha256(decoder_bytes)` recorded in the record and logged each run. Nothing about the decoder is learned in place; changing it invalidates a run.
- Task (shared field): 2D torus of side L=20. One moving harmonic source field H(p, t) = cos(k1·p − ωt)·sin(k2·p + ωt) with wave numbers (0.35, 0.22) and phase speed ω=0.6. Each entity starts at seeded positions, receives reward = H(p_t) per step, plus a −2.0 penalty on collision (distance < 0.6), minus 0.02·|thrust| metabolic cost. Collision resets both entities to seeds? No: collision applies the penalty and bounce-off; episodes run 400 steps.
- Observation s_t (8 floats): [pos_x/L, pos_y/L, dH/dx, dH/dy, vx, vy, (own_x − other_x)/L, (own_y − other_y)/L].
- Action: thrust vector u_t = tanh(W[:2] · φ(s_t)), φ(s) = fixed 48-dim harmonic feature map (s, s·s, sin(2πs), cos(2πs), 1). Applied as velocity update; friction 0.9; max speed clamp 0.15.
- Two entities: A seeded at (−5, −5), B at (+5, +5), same W seeded identically; neither can see identity, only relative position (so kin-discrimination cannot develop). They share the sympathetic_ring channel: each writes [own_unit_pos 2, own_unit_vel 2, reserved 4] per step into its OWN 8-float slot; reads the other's slot as 8 more features for φ. (This is the "sympathetic wave" as a peer-reviewed design affordance, not language.)

## Regimes

R1 Naked Matrix: entity = W (256x256) frozen rows 0..63, plastic rows 64..255. Adaptation = antithetic evolutionary mitosis over episodes: each "generation" is one 80-step episode; 4 antithetic noise pairs are sampled from the plastic periphery (sigma = 0.3), each candidate evaluated by realized 24-step probe return in the same dual-agent task context; a candidate is committed only if probe_return >= 1.01 * parent_probe AND invariants pass (`R_INVARIANT`, watermark retained, core drift 0.0). No saliency estimator; selection is outcome-only, matching the house instrument (keep the wins).
R2 Parametric distributional organism: W = action-coupling matrix of an active-inference agent; A/B mitosis as in R1, except score = episode return + 0.1 * entropy of action spectrum (novelty gate).
R3 Causal SCM do()-loops: not in this session (separate prereg).
R4 Koopman/Kuramoto spectral: not in this session (separate prereg).

Track 2 delivers R1 only. R2 (active-inference-style) is out of this session's scope. Note on the adaptation algorithm: an earlier hand-rolled policy-gradient saliency never produced a commit in 40 generations (the field reward's per-step signal is far too weak for a REINFORCE-style estimator under shared access control), so the antithetic ES selection above replaces it before this prereg's runs; the failed approach and its flat traces are part of the session history, not hidden.

## Controls

C1 Frozen entity (mask = 0 rows plastic? i.e., no adaptation; W seeded, evaluated untouched) — separates adaptation from raw disposition.
C2 Random decoder: D shuffled once, fixed by seed — separates "any W evolves somewhere" from "decoder-structured adaptation".
C3 Single-agent: entity A alone in the field (B absent) — separates coordination/collision regime from solipsism.

## Measures (registered before runs)

Primary:
- M1 mean episode return by generation (trend across 40 generations)
- M2 collisions per episode
- M3 gate rejection rate (invariants failures / candidate count)
- M4 Frobenius distance W_gen − W_0 (bounded by R_INVARIANT by construction; measured anyway)
Secondary:
- M5 watermark retention (cosine, L2) every 5 generations
- M6 lineage divergence L2(W_A − W_B) and A/B sibling divergence at each generation
- M7 sympathetic channel mutual information I(own slot; other slot) over the last 10 generations (estimated as correlation significance; crude, disclosed as crude)
Falsifiers:
- F1 R1 mean return at generation 40 ≤ generation 0 → the whole architecture is inert in this task; publish as a miss regardless of mechanism.
- F2 collision rate does not decrease across generations in R1 despite adaptation pressure.
- F3 invariants reject > 50% of candidate generations in R1 (the safety gate becomes the bottleneck).
Exploratory: any qualitative trace worth reporting (forced symmetry breaking, lock-step movement, etc.) published as observation, not finding.

## Instrument

The disclosed decoder is point-valued: φ and the thrust head are identical across all runs and entities; W differs only in values. The ring is an 8-float bus with fixed layout. No language tokens anywhere: the only strings in the loop are log keys and file names.

## Record

`docs/program/experiments/zero-lexicon-cells-2026-11-12/` on branch `record/zero-lexicon-cells-2026-11-12`. Contents: this design, PREREG-E08.md, decoder source + sha256, arena copy (`plasm_import/`), runs, logs, RESULTS-E08.md, tests. Merge only with independent review as usual.
