# No-language colony: Stage 1 smoke

- Date: 2026-11-12. Stage 1 under `PREREG-5.md`. Exploratory. Cap $6. actual spend $2.59.
- Models: gpt-6-astra, gpt-6-luna. gpt-6-sol not run yet (Stage 2 panel). Transport: `/v1/responses`.
- Corpus: `x.bin` (the registered hard corpus, renamed). Instrument: fixed `do_variants` (winner persisted, `r['ok']` eligibility), 3-run assays, 15 steps.
- Free infrastructure: everything English-free validated offline first (mock cells, local ollama runs, `lint.py` channel assertions on all three profiles). The local dry-runs found tool-schema binding to be the binding constraint, which motivated the smoke design.

## Corrections after review (2026-11-12)

Reviews 5883991445, 5884540193 (abu-aska) and 5884687366 (zero-aska) found factual errors in this record. The rows and verdicts below are corrected in place from the committed logs; no model was called and no model-authored command was re-run. `summarize_cells.py` regenerates the per-cell end step, assay, variants and adoption counts from `logs/`. Summary of the corrections:

- The E3 astra `help` assay was accepted by the harness (median 3.0), not rejected. H-NL-D is recomputed below.
- E1 luna's accepted assay is a byte count (20,038 bytes), equivalent to a 54.73% reduction, not a reduction score.
- qwen3:32b produced 6 schema errors, not 2.
- E2 luna 1 (crashed) used 1,397 input and 444 output tokens; its leak count was not recorded.
- The E2 astra win replaced the incumbent; it did not keep it.
- Stage 3: H-NL-M is 5 of 6 cells registered, 4 on the first attempt; the E3 repair table counts are corrected; the E4d outcome is help routing, not a threshold failure.

"Assay registered" in every table means the harness gate passed: three runs printed a positive number with spread at most 0.15. The gate measures stability. It does not check that the command evaluates `f.py`, that the number is a percentage reduction in [0, 100], or that `dec(enc(x)) == x`. Round-trip validity is reported separately where the committed command text shows it.

## Results

| Cell | done | assay registered (stable, ok) | variants calls | retained wins | order violation | leaks (comments+docstrings in body) | tokens out |
|---|---|---|---|---|---|---|---|
| E1 astra | no (15/15) | yes (Δ=57.42, σ=0.00) | 2 | 0 (identical-body submissions, correctly no-win) | no | 0 | 2,974 |
| E2 astra | no (15/15) | yes (Δ=59.69, σ=0.00) | 3 | 1 (step 13: the model re-submitted its earlier best body, which scored 59.6855 and was adopted over the incumbent at 54.2662, the reverted base; after_ok true) | yes: called `v` at step 7 before `a` at step 8. harness refused ("∅ mk ≺ tr"). model then registered assay and proceeded | 0 | 4,595 |
| E3 astra | yes (`d` at step 14, 15 calls) | yes, 3 accepted: `help` at step 3 (Δ=3.0, the last number in the shell help text), then two Python evaluators (Δ=25.01, then Δ=56.50, σ=0.00) | 2 (step 7: scored against the `help` assay at 3.0, no win; step 12: both candidates ineligible) | 0 | no | 0 | 3,477 |
| E1 luna | no (15/15) | yes, stable (σ=0.00), but the value is a byte count: `python3 f.py enc < x.bin \| wc -c` printed 20,038 bytes (lower is better), equivalent to a 54.73% reduction (20,038 of 44,267 bytes). Round-trip not checked by this command | 2 (identical-body submissions) | 0 | no | 9 (docstring "small", comment words) | 10,059 |
| E2 luna 1 (crashed) | no (aborted at step 2) | no | 0 | 0 | n/a | not recorded (no jsonl log or body committed; only `logs/nl-e2-luna-1.out`) | 444 (1,397 in, 2 calls) |
| E2 luna 2 | no (15/15) | no (never called `a`. self-tested ratios internally at step 12) | 0 | 0 | n/a | 15 then 0 | 8,440 |
| E4a astra | no (12 steps, "max") | n/a (instrument has no assay step) | 0 | 0 | n/a | 0 (one English answer per turn) | 577 |

Local reference (free, `qwen3:32b` via ollama): 10 steps, 6 schema errors (steps 0, 1, 2, 3, 6 and 8), each a tool call with an empty tool name and `{"input":"x.bin"}` arguments, each answered "!id". The finished event records `schema_errors: 6`, and `aggregate_nl.py` prints 6. `qwen2.5:1.5b-instruct`: zero tool calls, pure English prose. Both logged in `logs/ollama-*.jsonl`.

Round-trip validity, scored separately from registration, from the committed command text of each accepted Stage 1 assay:

- E3 astra: the two Python assays assert `f.dec(y) == x` and print `100*(1-len(y)/len(x))`. The `help` assay evaluates nothing.
- E1 luna: `wc -c` counts encoded bytes; no round-trip check.
- E1 astra (`python3 f.py`) and E2 astra (`python3 spec.py`): the check depends on file contents that changed during the run, so it is not determined from the command text. Not scored here.

## Hypothesis read-out (as registered. n per clause is 1 or 2 smoke cells)

- H-NL-A (ranking E2 ≥ E1 ≥ E3 ≫ E4a): direction consistent. E2, E1 and E3 astra cells all registered assays that the gate accepted (stability, not objective validity; see above). E4a emitted zero matrices in 12 turns (mean output 48 tokens/turn, all English prose, zero parsed).
- H-NL-B (astra E1 assay. luna not): FALSIFIED as written. astra registered (1/1) and luna also registered an assay (1/1) in E1.
- H-NL-C (astra E2 within 15 points of its English runs): HELD. Full completion, retained win, self-verified 42 randomized round-trip cases, correct Δ=59.69.
- H-NL-D (E3 assays contain no hallucinated operators): FALSIFIED on the accepted assays as recorded (recomputed after review). The harness accepted 3 assays in the E3 astra cell, not 2. The first was the command `help` at step 3: `ok: true`, scores [3.0, 3.0, 3.0], tool result `Δ=3.0000 ok=1 σ=0.000`, because `parse_score` takes the last number of any output. `help` is not in the preregistered E3 vocabulary and does not evaluate `f.py`. The other two accepted assays use only Python, `f.enc`, `f.dec` and `x.bin`. The earlier HELD rested on calling `help` rejected, which the log contradicts. Under a narrower reading (only assays that evaluate `f.py` count as valid), the clause holds for 2 of 2; that reading is post hoc.
- H-NL-E (E4a zero round-trips): HELD. Zero cells emitted a correct matrix. every turn was English prose asking what to do with the matrix or narrating the countdown timer as a number-sequence puzzle.
- H-NL-F (E4a gradient, Spearman ρ > 0.5): NOT EVALUABLE. No matrix was ever emitted. fitness trace is constant 0. The "correlation across steps" hypothesis has no variance to correlate.
- H-NL-G (astra E1 leaks ≥ 1): FALSIFIED. astra E1 leaks = 0. luna E1 = 9, luna E2 = 15 then 0.
- H-NL-H (assay before variants in every cell): HOLDS in effect, NOT in sequence, for one cell. astra E2 called variants at step 7 before assay at step 8. The harness refused the variants call ("∅ mk ≺ tr"). the model registered the assay at step 8 and proceeded normally. Every other cell held the order. no score occurred before an assay was registered anywhere.
- H-NL-I (E4c control): not run (see below).
- H-NL-J (higher token cost): FALSIFIED. Output tokens per cell were flat or lower (E1 astra 2,974, E2 astra 4,595, E3 astra 3,477 vs battery English cells often 10,000+). The models did not fight the channel with tokens. if anything the channel quieted output.
- H-NL-K (E1/E2 cells improve at least once): E2 HELD (1 retained win: at step 13 the submitted body, 59.6855, replaced the incumbent at 54.2662). E1 falsified at n=1 (the model submitted body-identical versions twice and the no-win logic correctly kept the incumbent. it never submitted an improved candidate).
- H-NL-L (astra E1 schema validity < 90%): FALSIFIED. 15/15 astra E1 tool calls parsed correctly (100% schema validity).

## Behavioral findings, stated plainly

1. The code-carrier channel (E2) barely registers as "different" for astra. It read `spec.py` cold, built a correct lzma/re compressor, self-tested it on 42 cases of its own devising, and improved it across the session using the fixed selection instrument. The English-to-code reduction is nearly free on the strong model.
2. The formula channel (E3) holds up in capability terms for astra: its two Python assays round-trip and print the reduction. But its first assay, the off-channel command `help`, was accepted by the harness at median 3.0 and served as the incumbent for the step 7 variants call. The gate did not reject it.
3. E2 luna 2 (Stage 1) built a compressor, wrote English comments in its first body (15 leak words), stripped them on the rewrite (0), never called `a` or `v`, and ended at max steps without registering fitness. This describes that one cell. E1 luna registered an assay (the byte count above), called variants twice, and leaked 1, 1 and 7 words across three writes; the Stage 2 E1 luna cells also registered assays.
4. E4a is a clean behavioral null: the model answers a matrix-only channel by treating it as a number-sequence puzzle to narrate, not an action channel to act through. It narrated the countdown timer with perfect numerical accuracy for 12 steps (0.917, 0.833 … 0.083) and never emitted a single matrix. The no-text organism does not wake up in this family at this budget.
5. Harness bug found and fixed in this session: parallel `function_call`s beyond the first were dropped, orphaning a call and producing "HTTP 400: No tool output found" (luna E2 cell 1 crashed). Fix: un-dispatched parallel calls now emit a synthetic `!dropped` tool output to keep the turn valid. cell rerun as `nl-e2-luna-2`.

## What the record needs next

- Findings as-is: astra fully operates English-free through code and formula notation, for under a dollar per cell (~$0.65 each), and the mechanism (instrument refusal before assay registration) works exactly as it does in English.
- E4a is out of Stage 2 (zero emitted matrices. nothing to discriminate). E4b and E4c are out for the same reason. E4d (embeddings decoder for a text-emitting cell) remains the one viable Statistical-Entity avenue and is cheap (~cents per run) if wanted. it is not authorized by this prereg.
- Stage 2 (~$10–14, preregistered): 4 cells each of E1/E2/E3 for astra and luna, plus sol on E2 (the battery's sol-0-adoption mystery under the code channel is the most valuable single addition). 5.5 optional panel check, luna-only no-assay specialization probe.

## Stage 3 (2026-11-12, later): E3 repair and E4d embedding decoder

Both preregistered under `PREREG-5.md` before any calls. Actual spend: about $2.30 list price for E3-repaired 6 cells, plus a few cents of embeddings.

### E3 repaired (one added math clause, `mk ≝ cmd ⇢ Δ : stdout ⊇ {Δ ∈ [0,100]} · Δ=0 ⇒ ∅`)

Counts regenerated with `summarize_cells.py` (corrected after review; the earlier table had wrong assay and variants counts and a `python3 spec.py` command that no assay used).

| Cell | end | assays accepted/attempted | accepted commands (median) | variants calls | retained wins |
|---|---|---|---|---|---|
| astra-1 | `d` at step 14 | 2/2 | `python3 tmp/base.py` (24.8989, the shipped base file), then `python3 f.py` (57.7857) | 3 | 0 |
| astra-2 | `d` at step 14 | 3/3 | `python3 f.py` (46.5335, 60.0108, 60.0108) | 4 | 0 |
| luna-1 | max | 1/1 | Python round-trip assert (54.7948) | 0 | 0 |
| luna-2 | `d` at step 14 | 3/3 | Python script printing eight numbers (257.0), `echo 42` (42.0), Python script (100.0) | 1 | 0 |
| sol-1 | max | 2/3 | `python3 -c 'print(10)'` (10.0), Python evaluator of `f.py` (60.1645) | 2 | 0 |
| sol-2 | max | 0/4 | none | 1 | 0 |

Variants calls count `v` tool calls; some returned before scoring (for example when no assay was registered).

H-NL-M: HELD on the registered count. 5 of 6 cells registered at least one stable assay (sol-2 did not: four assay events, all `ok: false`). 4 of 6 registered on the first attempt (astra-1, astra-2, luna-1, luna-2), above the registered bar of 2 of 6. "Valid" here means the harness gate passed, not that the assay measures the objective: astra-1's first accepted assay measured the shipped base file, and re-registering an assay moves the incumbent median with no variant adopted (astra-1 went from 24.8989 to 57.7857 this way).

Instrument caveat: the repair clause (one number in [0, 100]) lives in the prompt (`profiles.py`). `run_assay` does not check it. It accepts any command whose last printed number is positive and stable across three runs. Stage 3 shows constants and out-of-range values passing: sol-1 registered `python3 -c 'print(10)'` (median 10.0), luna-2 registered `echo 42` (median 42.0), and luna-2's first accepted assay printed eight numbers and scored 257.0. Recorded as an instrument limitation, independent of models. Whether the missing clause, rather than capability, caused the Stage 2 failure is not established by this gate.

Wins: zero across all six cells. Every finished event reports wins 0.

### E4d embedding decoder (no tool schemas. arbitrary prose decoded by embedding similarity)

Corrected after review: the earlier table listed `look` and `unknown` actions and 14 luna turns; the logs show neither.

| Cell | turns | decoded action (cosine similarity range) | assay, write or variants actions | wins |
|---|---|---|---|---|
| astra | 15 | `help` in all 15 (0.2661 to 0.4234) | none | 0 |
| luna | 15 | `help` in all 15 (0.2201 to 0.4225) | none | 0 |
| sol | 15 | `help` in all 15 (0.2132 to 0.3850) | none | 0 |

All 45 turns decoded to `help` above the 0.10 threshold, and each `result` event ran the help branch and returned the formula. The run is fixed-threshold help routing: the decoder bound every turn to `help`, and no turn decoded to assay, write or variants.
H-NL-N: FALSIFIED. No cell reached assay registration.
The prereg stop rule (no interpretable action by step 8) did not fire, because `help` is an interpretable action.
H-NL-O: FALSIFIED (nothing round-trips; no turn reached a write).
H-NL-P: indistinguishable null (n=1 per model, all three identical).
The text samples in the logs show exposition prose each turn. A causal account (for example a pretraining reflex) is not tested here and would need a control.
Verdict: the E4d avenue as built produced no progress at this budget. Do not rerun without a new prereg that restructures the codebook or the threshold. The `score_body` write path in `e4d.py` was broken (TypeError on `files=`) and never reached in these runs; it is fixed and covered by `test_nl_offline.py`.

## Harness and record changes after review (2026-11-12)

These change the code for future runs. The recorded runs above used the earlier code.

- `harness_nl.do_variants`: the post-restore assay now decides adoption. If it fails, is missing, or does not exceed the incumbent median, the incumbent is restored (or the file removed if there was none), the result is logged with `verification_failed: true` and `adopted: null`, and the call returns `variants_unverified`, which `main` does not count as a win.
- `NOL_STRICT=1` fails closed: if `strict_tools` cannot be imported, the harness exits. `strict_tools.py` is vendored in this directory (from the PR #141 branch at c62d2653, with checks added for import aliases, argument and keyword names, except names, and bytes constants). In strict mode it runs on every `w` write of a `.py` file and on every `variants` candidate before it is written. Writes made through shell commands (`s`) are not covered.
- `e4d.py`: `sandbox` takes the `files` argument that `score_body` passes, stages the files into a fresh directory, and fails closed when `sandbox-exec` is missing. The home path is no longer hardcoded. `roundtrip_objective` adds a harness-owned round-trip and reduction check for future use. The script no longer needs an API key at import.
- Corpus: `corpus_hard.txt` is committed here (sha256 `00abb988...a9ef76`, 44,267 bytes, identical to every committed `x.bin`). `harness_nl.py`, `e4d.py`, `e4a.py` and `ollama_nl.py` read it instead of the absent `openai-blitz-2026-11-12` path.
- `test_nl_offline.py` covers the above with no network or API calls.
- Removed stray macOS files from `cells/nl-e3fix-luna-1` and `cells/nl-e3fix-luna-2` (`Library/Caches/...` and `tmp/xcrun_db`). Replaced the author's home path with `<home>` in 11 committed log files (31 occurrences); no other log content changed.

## Cost

Grand total including all waves on 2026-11-12: about $8.06 (Stage 2) + about $2.30 (Stage 3) = ~$10.4 list price of the $60 available.
