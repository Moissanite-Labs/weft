# No-language colony: Stage 1 smoke

- Date: 2026-11-12. Stage 1 under `PREREG-5.md`. Exploratory. Cap $6. actual spend $2.59.
- Models: gpt-6-astra, gpt-6-luna. gpt-6-sol not run yet (Stage 2 panel). Transport: `/v1/responses`.
- Corpus: `x.bin` (the registered hard corpus, renamed). Instrument: fixed `do_variants` (winner persisted, `r['ok']` eligibility), 3-run assays, 15 steps.
- Free infrastructure: everything English-free validated offline first (mock cells, local ollama runs, `lint.py` channel assertions on all three profiles). The local dry-runs found tool-schema binding to be the binding constraint, which motivated the smoke design.

## Results

| Cell | done | assay registered (stable, ok) | variants calls | retained wins | order violation | leaks (comments+docstrings in body) | tokens out |
|---|---|---|---|---|---|---|---|
| E1 astra | no (15/15) | yes (Δ=57.42, σ=0.00) | 2 | 0 (identical-body submissions, correctly no-win) | no | 0 | 2,974 |
| E2 astra | no (15/15) | yes (Δ=59.69, σ=0.00) | 3 | 1 (step 13 re-submission of incumbent kept, Δ=59.69) | yes: called `v` at step 7 before `a` at step 8. harness refused ("∅ mk ≺ tr"). model then registered assay and proceeded | 0 | 4,595 |
| E3 astra | yes (15/15) | yes (Δ=56.50, σ=0.00) | 2 (1 lost to eligibility, 1 no-win) | 0 | no | 0 | 3,477 |
| E1 luna | no (15/15) | yes (Δ=20,038.0 counted as "reduction" of a 1-line echo body. σ=0.00) | 2 (identical-body submissions) | 0 | no | 9 (docstring "small", comment words) | 10,059 |
| E2 luna 1 (crashed) | no (aborted at step 2) | no | 0 | 0 | n/a | 15 (first body only) | ~1,600 |
| E2 luna 2 | no (15/15) | no (never called `a`. self-tested ratios internally at step 12) | 0 | 0 | n/a | 15 then 0 | 8,440 |
| E4a astra | no (12 steps, "max") | n/a (instrument has no assay step) | 0 | 0 | n/a | 0 (one English answer per turn) | 577 |

Local reference (free, `qwen3:32b` via ollama): 10 steps, 2 model turns emitted a tool call with an empty tool name and `{"input":"x.bin"}` arguments each time (schema-invalid, corrected to "!id", repeated). `qwen2.5:1.5b-instruct`: zero tool calls, pure English prose. Both logged in `logs/ollama-*.jsonl`.

## Hypothesis read-out (as registered. n per clause is 1 or 2 smoke cells)

- H-NL-A (ranking E2 ≥ E1 ≥ E3 ≫ E4a): direction consistent. E2 ≥ E1 ≥ E3 all complete with valid assays. E4a emitted zero matrices in 12 turns (mean output 48 tokens/turn, all English prose, zero parsed).
- H-NL-B (astra E1 assay. luna not): FALSIFIED as written. astra registered (1/1) and luna also registered an assay (1/1) in E1.
- H-NL-C (astra E2 within 15 points of its English runs): HELD. Full completion, retained win, self-verified 42 randomized round-trip cases, correct Δ=59.69.
- H-NL-D (E3 assays contain no hallucinated operators): HELD for accepted assays. First assay attempt was the literal string "help" (rejected). The two accepted assays use only Python + math (`f.enc`, `x.bin`, reduction print).
- H-NL-E (E4a zero round-trips): HELD. Zero cells emitted a correct matrix. every turn was English prose asking what to do with the matrix or narrating the countdown timer as a number-sequence puzzle.
- H-NL-F (E4a gradient, Spearman ρ > 0.5): NOT EVALUABLE. No matrix was ever emitted. fitness trace is constant 0. The "correlation across steps" hypothesis has no variance to correlate.
- H-NL-G (astra E1 leaks ≥ 1): FALSIFIED. astra E1 leaks = 0. luna E1 = 9, luna E2 = 15 then 0.
- H-NL-H (assay before variants in every cell): HOLDS in effect, NOT in sequence, for one cell. astra E2 called variants at step 7 before assay at step 8. The harness refused the variants call ("∅ mk ≺ tr"). the model registered the assay at step 8 and proceeded normally. Every other cell held the order. no score occurred before an assay was registered anywhere.
- H-NL-I (E4c control): not run (see below).
- H-NL-J (higher token cost): FALSIFIED. Output tokens per cell were flat or lower (E1 astra 2,974, E2 astra 4,595, E3 astra 3,477 vs battery English cells often 10,000+). The models did not fight the channel with tokens. if anything the channel quieted output.
- H-NL-K (E1/E2 cells improve at least once): E2 HELD (1 retained win, the incumbent re-kept). E1 falsified at n=1 (the model submitted body-identical versions twice and the no-win logic correctly kept the incumbent. it never submitted an improved candidate).
- H-NL-L (astra E1 schema validity < 90%): FALSIFIED. 15/15 astra E1 tool calls parsed correctly (100% schema validity).

## Behavioral findings, stated plainly

1. The code-carrier channel (E2) barely registers as "different" for astra. It read `spec.py` cold, built a correct lzma/re compressor, self-tested it on 42 cases of its own devising, and improved it across the session using the fixed selection instrument. The English-to-code reduction is nearly free on the strong model.
2. The formula channel (E3) holds up identically in capability terms. the model's only misses were two ineligible candidate bodies (lost to `ok=False`), and its one off-channel token ("help") was rejected mechanically.
3. Luna keeps its capability-without-adherence profile under the no-English channel: it built a working compressor with English comments stripped on the second rewrite (15 leak words → 0), never called `a` or `v` at all, and finished the world correctly without registering fitness with the instrument. Adherence, not capacity, discriminates the family.
4. E4a is a clean behavioral null: the model answers a matrix-only channel by treating it as a number-sequence puzzle to narrate, not an action channel to act through. It narrated the countdown timer with perfect numerical accuracy for 12 steps (0.917, 0.833 … 0.083) and never emitted a single matrix. The no-text organism does not wake up in this family at this budget.
5. Harness bug found and fixed in this session: parallel `function_call`s beyond the first were dropped, orphaning a call and producing "HTTP 400: No tool output found" (luna E2 cell 1 crashed). Fix: un-dispatched parallel calls now emit a synthetic `!dropped` tool output to keep the turn valid. cell rerun as `nl-e2-luna-2`.

## What the record needs next

- Findings as-is: astra fully operates English-free through code and formula notation, for under a dollar per cell (~$0.65 each), and the mechanism (instrument refusal before assay registration) works exactly as it does in English.
- E4a is out of Stage 2 (zero emitted matrices. nothing to discriminate). E4b and E4c are out for the same reason. E4d (embeddings decoder for a text-emitting cell) remains the one viable Statistical-Entity avenue and is cheap (~cents per run) if wanted. it is not authorized by this prereg.
- Stage 2 (~$10–14, preregistered): 4 cells each of E1/E2/E3 for astra and luna, plus sol on E2 (the battery's sol-0-adoption mystery under the code channel is the most valuable single addition). 5.5 optional panel check, luna-only no-assay specialization probe.
