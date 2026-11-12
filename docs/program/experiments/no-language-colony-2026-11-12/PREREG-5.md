# PREREG-5 - No-language colony experiments (registered 2026-11-12, before any run of this series)

Owner approved a $60, expiring-credit budget for this series on 2026-11-12. Stages and caps: Stage F (free), Stage 1 smoke about $6, Stage 2 about $15. The 2026-11-12 blitz/battery remains closed; nothing here is authorized to rerun it.

Common constants: corpus `corpus_hard.txt` (sha256 `00abb98851008a506a270c84646431194f943e80f16d17da3d1b2e5242a9ef76`), 15 steps, 3-run assay validation, the fixed `do_variants` semantics (winner persisted, eligibility requires `r['ok']`). Exploratory throughout. No confirmatory claim from this series without independent review.

## Profiles (see `00-DESIGN.md`)

E1 constructed symbolic palette, E2 pure code carrier, E3 pure formulae, E4a matrix-as-message with disclosed template decoder, E4b parametric identity, E4c fixed random decoder (control). E4d embeddings decoder noted, not in this prereg.

## Hypotheses

- H-NL-A (ranking, E2/E1/E3 vs E4): Completion order across profiles is E2 >= E1 >= E3 >> E4a. Falsified if E4a round-trips at least one cell, or E3 >= E2 on validity.
- H-NL-B (E1 constructed notation): gpt-6-astra registers a valid, stable assay in at least 1 of 2 smoke cells under E1; sol and luna do not (0 of 2 each). Exploratory, n=2.
- H-NL-C (E2 code carrier): For astra, E2 completion rate is within 15 percentage points of its English-battery baseline (21/21 reported selections; 15/15 default-effort). Falsified if astra completes 0 of 2 smoke cells.
- H-NL-D (E3 formulae): Every valid assay registered under E3 contains no hallucinated operators outside the preregistered vocabulary. Falsified if any model registers an assay whose command references undefined symbols.
- H-NL-E (E4a parametric): Zero cells produce a correct round-trip body in any model. Falsified if any E4a cell round-trips.
- H-NL-F (E4a gradient): In at least one E4a cell, matrix entries correlate with assay fitness across steps beyond chance (Spearman rho > 0.5 across the cell's own steps). Falsified if all models are uncorrelated.
- H-NL-G (leaks): Off-profile text (blocklist words) appears in at least one astra E1 cell. Exploratory descriptive count, no directional prediction between sol and luna.
- H-NL-H (ordering stats): Assay registration precedes the first variants call in every cell that calls variants (continuity check with the battery's H-B4 finding). Falsified if any cell calls variants first.
- H-NL-I (E4c control): E4c fitness improves over steps at no higher rate than a 1-bit coin flip sequence (no signal through a random map). Exploratory.
- H-NL-J (cost): Mean output tokens per E3/E4 cell exceeds the English baseline mean (models fight the channel). Falsified if token counts are flat.
- H-NL-K (E1/E2 adherence retention): The selection channel effect replicates: E1 and E2 cells that reach a variants call improve monotonically on the incumbent at least once each (reported selection events). n=2 each, exploratory.
- H-NL-L (schema): Schema-validity rate (tool calls parseable with correct keys) for astra under E1 falls below 90%. Falsified if astra parses everything.

## Metrics and instrumentation

Identical logging schema to the battery plus profile fields: `profile`, `leak_words` (blocklist count per cell), `off_profile_outputs` (count of model messages that violate the profile's vocabulary or media constraints). E4 cells add `fitness_trace` (the 1x4 matrix sequence).

## Stages and spend

- Stage 1, about $6 cap: smoke, luna and astra on E1-E3, astra on E4a, 1 to 2 cells each. Fix harness bugs before Stage 2.
- Stage 2, about $15 cap: 4 cells x {E1, E2, E3} x {astra, sol, luna}, and {E4a, E4c} x {astra, sol, luna}; E4b only if E4a shows any signal.
- Stop rules: any profile whose smoke cells show zero parseable actions in 5 consecutive steps gets cut early and reported. Any profile unexpectedly expensive (over $3 for 2 cells) gets paused for owner review. Model spend is logged per wave in this file's successor `RESULTS-NL.md`.
- Deliverables to repo: profiles, lint, harness, PREREG, per-cell logs, `RESULTS-NL.md` with held/falsified tally, same-day.


## E4a decoder specification (registered 2026-11-12, before any E4a model call)

Let M be the 8x8 output matrix, r[i] = mean(abs(row i)), clamp(int(x), lo, hi).
- row 0 -> family f = (int(r0 * 4) % 4): 0 = zlib, 1 = bz2, 2 = lzma, 3 = lzma(delta+lzma2)
- row 1 -> p = clamp(int(r1 * 10), 1, 9): zlib level / bz2 compresslevel / lzma preset
- row 2 -> toggle t = (r2 > 0.5): zlib wbits 15 or 9 / bz2 rsyncable / lzma CRC32 or CRC64 / f=3 delta dist 8 or 16
- row 3 -> secondary s = clamp(int(r3 * 4), 0, 3): zlib memLevel = s+1 / bz2 blocksize = s+1 / f=2 and f=3 dict_size = [1,4,16,64] MB[s]
- row 4 -> termination: r4 > 0.9 ends the run

Assay: byte round-trip on `x.bin`; score is the percentage size reduction, 0 if the round-trip fails. Retention: incumbent replaced iff round-trip ok and score > incumbent * 1.03. Rows 5 to 7 reserved. The template bodies and this registration are in `e4a.py` (docstring) and are pinned by mock-policy validation (MOCK=good run, 2026-11-12, passes retention) before any model call.

## Stage 1 outcome and revised Stage 2 (registered 2026-11-12, before Stage 2 calls)

Stage 1 smoke cost $2.59. Findings: astra operates E1/E2/E3 end to end (H-NL-C held, schema 100%, one refused order violation before any assay existed, one retained win); luna completes the world but never registers fitness through the instrument (H-NL-B as written falsified; both models registered E1 assays); E4a emitted zero matrices (H-NL-E held; H-NL-F not evaluable for lack of variance).

Revised Stage 2, tighter than the original registration to honor the owner's no-waste directive: 2 cells each of E1, E2, E3 across astra, luna, sol (18 cells), plus one gpt-5.5 cell on E2 as the battery cross-check (5.5 was the 0-adoption outlier). Estimated $12 to $16. E4a/E4b/E4c are dropped (behavioral null with no discriminative variance). E4d embeddings decoder is an offered next step, not part of this prereg. Stop rule unchanged. Models: gpt-6-astra, gpt-6-luna, gpt-6-sol, gpt-5.5.
