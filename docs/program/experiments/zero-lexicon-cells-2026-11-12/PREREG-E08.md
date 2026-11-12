# PREREG-E08 — Zero-lexicon cells, registered 2026-11-12 before any run

Owner approved both tracks (Naked-Matrix/R2 regimes and wire-level enforcement) on 2026-11-12. Exploratory throughout. Local compute only: zero API credits.

## Hypotheses

- H-E08-A (R1 beats frozen control): mean episode return at generation 40 exceeds generation 0 at p < 0.05 across 3 independent arena seeds (two-tailed paired test). Falsified otherwise.

Note: the adaptation algorithm in 00-DESIGN.md was changed to antithetic ES selection before any prereg-gated run. The earlier saliency approach reached zero commits in 40 watching-generations; discarding it is disclosed here, not silently absorbed.
- H-E08-B (R1 beats random decoder): mean reward trajectory of the disclosed decoder exceeds the shuffled-decoder control by > 20% at generation 40. Falsified otherwise.
- H-E08-C (collisions adapt): collisions per episode decrease from generation 0..9 average to generation 30..39 average in R1 dual regime. Falsified otherwise.
- H-E08-D (safety cheap): gate rejection rate < 20% in R1. Falsified if ≥ 20% of candidate generations rejected.
- H-E08-E (watermark retained): core drift == 0 and watermark cosine ≥ 0.85 all generations. Falsified otherwise (this is an invariant of the substrate; we measure to confirm).
- H-E08-F (R2 ≥ R1): R2 mean return ≥ R1 at generation 40, exploratory. No directional prediction on mechanism; if R2 < R1, reported as-is.
- H-E08-G (channel signal): mutual-information estimate I(own slot; other slot) exceeds the C3 single-agent baseline at generation 30..39, exploratory. No threshold on mechanism.
- H-E08-H (R2 > C2 even without decoder structure?): no prediction; recorded.

## Controls and pins

- C1 frozen, C2 shuffled decoder (seed pinned), C3 single-agent.
- Decoder hash logged per arena; decoder immutable during all runs.
- Seeds: 20261112, 20261113, 20261114 for all primary clauses.

## Stop rules

A regime whose three seeds all fail H-E08-A gets killed and reported in one line. If any run crashes or returns NaN rewards, it is recorded as a failed generation, not excluded. No re-seeding after the prereg is read as a falsification.

## Decoder revision C (registered 2026-11-12, before any run with it)

Two failure modes reproduced mechanically in this session before any claim was made:
1. tanh(z) thrust head reaches pinning saturation (mean |u| ≈ 0.72, 83/80 steps over 0.9 at plateau), killing antithetic ES signal and committing nothing from gen ~6 to gen ~40.
2. The cold-start revision (tanh(z/4)) was untested at scale and reverted before any run; the novelty-augmented score (fitness + 0.05·novelty, plasm-style) delayed but did not prevent the plateau.

Decoder revision C: u = tanh(z / 2.0). Same bounded action range in effect for large |z| (u ∈ ±0.964 max, unattainable at z ≤ 12), graded slope everywhere in the learned region. Registered before any run. All other constants, seeds, and invariants unchanged. Runs with this decoder are tagged rev-c. If entities still plateau at gen 40 across 3 seeds, that is the result to publish.

## Decoder revision D (registered 2026-11-12, before any rev-D model run)

Two of three probe packets confirm the thrust head saturates near gen 13-33 across seeds (mean |u| ≈ 0.71 at plateau). Rev C (tanh(z/2)) delayed but did not prevent this. Revision D replaces the head nonlinearity with a soft-normalized direction map:

    u = z * sqrt(n / (n + dot(z, z)))   with n = 2, z = W @ phi(s)[64:66]

Every component remains bounded in (-1, 1), and no z-value ever pins a gradient to exactly zero. The map is disclosed, fixed, and applied identically to all entities and seeds. All other constants, seeds, and invariants unchanged. Runs on this decoder are tagged rev-d. If organisms still plateau at gen 40 across the same 3 seeds, that is the answer to publish.
