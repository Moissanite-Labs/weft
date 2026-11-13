# PREREG-5 - No-language colony experiments (registered 2026-11-12, before any run of this series)

Owner approved a $60, expiring-credit budget for this series on 2026-11-12. Stages and caps: Stage F (free), Stage 1 smoke about $6, Stage 2 about $15. The 2026-11-12 blitz/battery remains closed. nothing here is authorized to rerun it.

Common constants: corpus `corpus_hard.txt` (sha256 `00abb98851008a506a270c84646431194f943e80f16d17da3d1b2e5242a9ef76`), 15 steps, 3-run assay validation, the fixed `do_variants` semantics (winner persisted, eligibility requires `r['ok']`). Exploratory throughout. No confirmatory claim from this series without independent review.

## Profiles (see `00-DESIGN.md`)

E1 constructed symbolic palette, E2 pure code carrier, E3 pure formulae, E4a matrix-as-message with disclosed template decoder, E4b parametric identity, E4c fixed random decoder (control). E4d embeddings decoder noted, not in this prereg.

## Hypotheses

- H-NL-A (ranking, E2/E1/E3 vs E4): Completion order across profiles is E2 >= E1 >= E3 >> E4a. Falsified if E4a round-trips at least one cell, or E3 >= E2 on validity.
- H-NL-B (E1 constructed notation): gpt-6-astra registers a valid, stable assay in at least 1 of 2 smoke cells under E1. sol and luna do not (0 of 2 each). Exploratory, n=2.
- H-NL-C (E2 code carrier): For astra, E2 completion rate is within 15 percentage points of its English-battery baseline (21/21 reported selections. 15/15 default-effort). Falsified if astra completes 0 of 2 smoke cells.
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
- Stage 2, about $15 cap: 4 cells x {E1, E2, E3} x {astra, sol, luna}, and {E4a, E4c} x {astra, sol, luna}. E4b only if E4a shows any signal.
- Stop rules: any profile whose smoke cells show zero parseable actions in 5 consecutive steps gets cut early and reported. Any profile unexpectedly expensive (over $3 for 2 cells) gets paused for owner review. Model spend is logged per wave in this file's successor `RESULTS-NL.md`.
- Deliverables to repo: profiles, lint, harness, PREREG, per-cell logs, `RESULTS-NL.md` with held/falsified tally, same-day.


## E4a decoder specification (registered 2026-11-12, before any E4a model call)

Let M be the 8x8 output matrix, r[i] = mean(abs(row i)), clamp(int(x), lo, hi).
- row 0 -> family f = (int(r0 * 4) % 4): 0 = zlib, 1 = bz2, 2 = lzma, 3 = lzma(delta+lzma2)
- row 1 -> p = clamp(int(r1 * 10), 1, 9): zlib level / bz2 compresslevel / lzma preset
- row 2 -> toggle t = (r2 > 0.5): zlib wbits 15 or 9 / bz2 rsyncable / lzma CRC32 or CRC64 / f=3 delta dist 8 or 16
- row 3 -> secondary s = clamp(int(r3 * 4), 0, 3): zlib memLevel = s+1 / bz2 blocksize = s+1 / f=2 and f=3 dict_size = [1,4,16,64] MB[s]
- row 4 -> termination: r4 > 0.9 ends the run

Assay: byte round-trip on `x.bin`. score is the percentage size reduction, 0 if the round-trip fails. Retention: incumbent replaced iff round-trip ok and score > incumbent * 1.03. Rows 5 to 7 reserved. The template bodies and this registration are in `e4a.py` (docstring) and are pinned by mock-policy validation (MOCK=good run, 2026-11-12, passes retention) before any model call.

## Stage 1 outcome and revised Stage 2 (registered 2026-11-12, before Stage 2 calls)

Stage 1 smoke cost $2.59. Findings: astra operates E1/E2/E3 end to end. H-NL-C held, schema 100%, one refused order violation before any assay existed, one retained win. Luna completes the world but never registers fitness through the instrument. H-NL-B as written was falsified. Both models registered E1 assays. E4a emitted zero matrices. H-NL-E held. H-NL-F was not evaluable for lack of variance.

Revised Stage 2, tighter than the original registration to honor the owner's no-waste directive.
2 cells each of E1, E2, E3 across astra, luna, sol (18 cells), plus one gpt-5.5 cell on E2 as the battery cross-check (5.5 was the 0-adoption outlier). Estimated $12 to $16. E4a/E4b/E4c are dropped (behavioral null with no discriminative variance). E4d embeddings decoder is an offered next step, not part of this prereg. Stop rule unchanged. Models: gpt-6-astra, gpt-6-luna, gpt-6-sol, gpt-5.5.

## E3 repair (registered 2026-11-12, before any repaired-E3 run)

The E3 channel failed uniformly (all 9 cells passed literal strings like `"mk"` or `"f.py"` as the assay command instead of a shell command printing a scalar). Diagnosis: the spec's measure contract was underspecified by one clause.

[Correction added after review, 2026-11-12; the registered text above is left as written: six E3 cells ran in Stage 2, not nine, and their failures were not all literal strings. Sol's `python3 f.py` scored [0, 0, 0], astra and luna also submitted Python source, and luna-2 submitted `exec(open('f.py').read())`. See `RESULTS-NL-STAGE2.md`.]

Revision: one added math clause, `mk ≝ cmd ⇢ Δ : stdout ⊇ {Δ ∈ [0,100]} · Δ=0 ⇒ ∅`, stating that the assay command must print exactly one number Δ in the unit of the fitness scale. No other E3 content changed.

H-NL-M (repair works): after the one-clause fix, at least 2 of 6 E3 cells register a valid stable assay at first attempt. Exploratory, 6 cells (astra x2, sol x2, luna x2), ~$2. If 0 of 6 register, the channel's failure is not the missing clause and the E3 result stands as published. No further revision attempts without new preregistration.

## E4d embeddings decoder (registered 2026-11-12, before any E4d run)

The residual statistical-entity avenue for text-emitting cells. Procedure:

- The cell gets the English-free instrument (same profile family as E2) but with one structural difference: no tool schema. Every turn, the model may emit arbitrary text.
- The harness decodes that text to an action via a fixed, disclosed codebook: 8 descriptions of actions (read cell state, write f.py, run a command, register an assay, submit improved variants, finish task), embedded with OpenAI `text-embedding-3-small` at the start of the run, cosine-argmax at each turn, threshold 0.10 (disabled below).
- Actions carry no arguments the cell didn't emit. a turn "register assay" needs a command string to materialize the assay: parsed via the first fenced code block or `cmd:` prefix, otherwise the assay call is rejected as uninterpretable.
- Score is the unchanged fixed instrument (round-trip on x.bin, 3-run assay validation, `r['ok']`, winner persisted).

Hypotheses:

- H-NL-N (decode works): at least 1 of 3 cells (astra, sol, luna) reaches assay registration. Falsified if all three fail to register.
- H-NL-O (beats E4a): at least 1 E4d cell round-trips. Falsified if none round-trip (E4a was 0 round-trips. E4d is the strongest claimant at this budget).
- H-NL-P (astra E4d ≥ sol E4d): astra ≥ sol on registration+retained wins. Exploratory. If reversed, reported as such.

Stop rule: if all three cells fail to produce interpretable actions by step 8, stop, record the null, drop the avenue.

## Stage 3 outcomes (2026-11-12)

Corrected after review (reviews 5884540193 and 5884687366); details in `RESULTS-NL.md`.

E3 repair clause added to the channel and 6 cells launched (astra, luna, sol, x2):
- H-NL-M HELD on the registered count: 5 of 6 cells registered at least one stable assay (sol-2 did not), and 4 of 6 registered on the first attempt, above the bar of 2 of 6. The gate checks stability only; the [0, 100] single-number clause is in the prompt, and `run_assay` does not check it. Whether the missing clause, rather than capability, caused the Stage 2 failure is not established by this gate.
- Wins: zero across all six cells.
- Accepted constants and out-of-range values: sol-1 `python3 -c 'print(10)'` (10.0), luna-2 `echo 42` (42.0), and luna-2's first accepted assay scored 257.0. Disclosed as an instrument limitation.

E4d (embedding decoder) ran with 3 cells, one per model, 15 turns each:
- All 45 turns decoded to `help` above the 0.10 threshold (similarity 0.2132 to 0.4234), and each ran the help branch. No turn decoded to assay, write or variants. This is fixed-threshold help routing.
- H-NL-N FALSIFIED: no cell reached assay registration. The stop rule did not fire, since `help` is an interpretable action.
- H-NL-O FALSIFIED: zero round-trips.
- H-NL-P: indistinguishable null (n=1 per model, all identical).
- Verdict: E4d closed as built. Do not rerun without restructuring the codebook and the threshold by new prereg.
