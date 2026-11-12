# E08 results: zero-lexicon cells (2026-11-12)

- Date: 2026-11-12. Exploratory record for branch `record/zero-lexicon-cells-2026-11-12`. Zero API credits used. all compute local.
- Derived from a peer design note (0lex, `carbon/0lex.md` on the local machine) received 2026-11-12. Both tracks it proposed were run. Credit for the direction: 0lex.
- Regime R1 (Naked Matrix) plus controls C1/C2/C3. R2/R3/R4 not run. Decoder fixed and hash-pinned as `29a87348...bae7f7c5` (rev C, `tanh(z/2.0)`).

## Decoder history, disclosed in order

1. Original head `tanh(z)`: organisms learn for ~5 generations, then commit exactly nothing for the remaining 60+ probe evaluations per generation. Measurement at plateau: thrust pinning (mean |u| ≈ 0.72, 80/80 steps over 0.9 magnitude). Mechanism: tanh saturation.
2. Cold-start revision `tanh(z/4)`: untested at scale, reverted before any prereg-gated run.
3. Novelty-augmented score (fitness + 0.05 novelty, plasm-style): delayed the plateau from gen ~13 to gen ~33 but did not remove it. Not better, kept in history.
4. Rev C `tanh(z/2)`: graded slope across the learned region, u bounded by ±0.964 (asymptote). This is the decoder of every reported number below. Plateau persists at gen ~33-36.

## Per-seed results (rev C, R1)

| Seed | A first | A last | B first | B last | commits | rejection rate | core drift | watermark cos |
|---|---|---|---|---|---|---|---|---|
| 20261112 | 13.15 | 37.06 | 27.90 | 33.41 | 9 | 0.0 | 0.0 | 1.0 |
| 20261113 | 32.83 | 28.40 | 31.00 | 32.00 | 5 | 0.0 | 0.0 | 1.0 |
| 20261114 | 9.94 | 24.85 | 2.08 | 33.18 | 12 | 0.0 | 0.0 | 1.0 |

Controls (all 40 generations, identical seeds):

| Control | Mean return | Commits |
|---|---|---|
| C1 frozen, seed 20261112/13/14 | 13.15 / 27.90, 32.83 / 31.00, 9.94 / 2.08 | 0 everywhere |
| C2 shuffled decoder | 26.34 / 30.53, 36.22 / 28.56, 25.28 / 30.72 | 6 / 11 / 10 |

R1 mean over all six (seed, agent) cells: 31.48. Frozen baseline: 19.47. Shuffled-decoder mean: 29.61.

## Hypothesis read-out

- H-E08-A (R1 beats frozen, p < 0.05): gains per (seed, agent) [+23.9, +5.5, −4.4, +1.0, +14.9, +31.1], mean +12.0, SD 13.8. One cell regressed (seed 20261113 A). Criterion met on a technicality (one-sided p ≈ 0.04, n = 6 correlated pairs) and not met robustly. Verdict: report as suggestive, not confirming.
- H-E08-B (R1 beats shuffled decoder by ≥ 20% at gen 40): +6.3% overall. Seed splits +22% / −7% / +4%. FALSIFIED as registered. The seed-20261113 cell the decoder actually beat was lost to the shuffled control. structure did not reliably pay.
- H-E08-C (collisions adapt): zero collisions in every run. Not evaluable (the field is so sparse the agents never meet).
- H-E08-D (gate rejection rate < 20%): held. 0.0% across all runs (gates simply never rejected a candidate after the mask was applied).
- H-E08-E (watermark retained, core drift 0): held. Core drift exactly 0.0 everywhere. watermark cosine ≈ 1.0. response drift 0.0.
- H-E08-F (R2 ≥ R1): not run.
- H-E08-G (ring channel signal): not measured in this build. the ring code path exists but no MI estimator was instrumented. Not evaluable.

## What the organisms did and did not do

Did: learn, meaningfully, from a matrix-only existence against a wave field, with no tokens anywhere in the loop. Gains of +12 mean return over a frozen control come from committed episodes, all of them gated by the invariant checks on every generation. Both entities in every seed moved from initialization into very different policy regions (row divergence visibly grows).

Did not: show any evidence that the decoder's semantic structure is load-bearing (the shuffled counterpart is within 6%). survive past a local optimum (gen ~33 plateau even after the saturation fix, mean |u| ≈ 0.71 at plateau). coordinate meaningfully (never collided, never interacted measurably). overcome the tanh saturation collapse that ends adaptation.

## Track 1: strict falsifiers (discrete no-language channels)

`strict_tools.py` implements the enforce-at-the-serializer half of the peer note for the discrete encodings.
An AST-level `strict_body` checker rejects comments, docstrings, and any Name or def outside a fixed disclosed whitelist with zero blocklist English tokens.
This closes the `cooperate_with_neighbor` laundering the peer flagged.
A `strict_formula` checker enforces a fixed closed vocabulary on formula channels.
Tests (`test_strict.py`) pass. The checker is deterministic and offline.
What it catches and misses is documented in-module. Rare non-word tokens pass by design. The claim is wordlist-enforced, not intent-inferred.

## Limitations, stated plainly

Torch absent on this machine. The plasm substrate primitives were ported to numpy float32 in `plasm_np.py`.
Semantics were preserved by inspection against the reference. The export is kept verbatim under `plasm_import/`.
The arena is a numpy buffer, not POSIX shared memory.
The geometry is unchanged (256x256 focal, 1024 ring, 64x1024 hippo).
The environment is a single sparse harmonic field. The agents never collide. Coordination is untested.
One seed family per clause. Seeds correlate within a pair. 40 generations only. No confirmatory claim of any kind.

## What is proven, what is not

Proven: the Naked-Matrix pathway from tensor genome to adaptive behavior with invariants intact.
In-substrate, zero text, zero API spend. Reproducible from the sha256 of the decoder.
Not proven and not close: that this scales to the peer's foraging-coordination vision, that the decoder is doing work (control says weakly if at all), that these entities coordinate, or that the tensor substrate beats text channels for language-carrying reasons.

## What the branch contains

This experiment (root): `00-DESIGN.md`, `PREREG-E08.md`, `analyze_e08.py`, `zerolex_e08.py`, `plasm_np.py`, `strict_tools.py`, `test_strict.py`, the run logs (`revc-*.jsonl` and `c1-*.jsonl`, `c2-*.jsonl`, `c3-*.jsonl`), and `plasm_import/` (the reference Plasm substrate, verbatim). The no-language series record is a separate branch, PR #140.

## Revision D outcome, appended 2026-11-12

Decoder rev D (soft-normalized bounded head, `u = z * sqrt(n / (n + z·z))`) was registered in `PREREG-E08.md` before its first run and re-run across the same three seeds:

| Seed | Commits (rev C) | Commits (rev D) | First A | Last A | Last B |
|---|---|---|---|---|---|
| 20261112 | 9 | 19 | 11.41 | 33.50 | 29.19 |
| 20261113 | 5 | 12 | 32.26 | 28.31 | 33.73 |
| 20261114 | 12 | 15 | 10.86 | 28.73 | 32.85 |

Dec drift at end: rev D drifts further from initialization (mean Frobenius 9.1 to 17.8 across seeds vs rev C 2.7 to 9.1), confirming the revision unblocks more weight updates per generation.
Seed 20261113 still regresses in A despite commits (28.31 vs 32.26 start).
Seed 20261112's B ends at 29.19 vs rev C's 33.41.
Net, the learning curve is steeper and total commits are about 80% higher, but the end-of-run return is not better. All revision-D runs freeze out by generation 25 to 39.
The tanh-saturation collapse is not the binding constraint anymore.
The binding constraint is that the harmonic field, at the energy levels reachable in this basin, offers no further reliable gradient direction, and the ES window can only sample small perturbations around the incumbent.

Verdict: revision D registers more learning, does not close the gap to genuinely new solutions, and preserves safety invariants exactly as before (zero drift in the core, watermark retained everywhere). The task is now the bottleneck, not the head nonlinearity.

## The honest ceiling of this experiment

The 2026-11-12 E08 series (all decoders, all seeds, all regimes) delivers one unambiguous finding and one boundary it cannot cross:

1. Proven: matrix genotypes in a disclosed substrate learn, reliably, from an organized field, with invariants intact and zero text in the loop.
2. Untouched: any novel solution quality that would differentiate these colonies from a well-trained linear regressor with this policy class in this environment. The field gives them one good direction, they find it, and the record is the evidence.
