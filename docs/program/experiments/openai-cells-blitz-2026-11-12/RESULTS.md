# GPT-6 family under the colony assay via /v1/responses (exploratory blitz)

- Date: 2026-11-12. Registered in `PREREGISTRATION.md` before any model call.
- Status: exploratory blitz on expiring OpenAI credits. One task, 12 cells, n=4 per model. Nothing here is confirmatory and nothing should be cited as a project result.
- Correction 2026-11-12 (post-review): the harness's `variants` selection did not write the selected winner back to disk. Every "adoption" in this file was a reported selection event, not a verified retained win. Replay under the fixed semantics: all 38 persist as retained wins. See `RECONCILIATION-2026-11-12.md` and `REPLAY-2026-11-12.md`.
- Task: `compress` from the razi-cells task set. Corpus: `corpus.txt`, 313,972 bytes, sha256 `a7727d6e5fdcd02dd8c22ddaee5109cd3119eef19c00ac28526d4625ec16d0fa`.
- Models, all through `POST /v1/responses` with native function tools: gpt-6-astra, gpt-6-sol, gpt-6-luna. 4 cells each, max 18 steps.

## Headline

- gpt-6-astra used the selection tool (`variants`) 11 times across 4 cells and reported a selection in every cell (4 reported selection events, 6.35 per 100 calls). Retention unverified. See `RECONCILIATION-2026-11-12.md`.
- gpt-6-sol and gpt-6-luna used `variants` 3 times each across their 8 cells and reported no selections.
- The transport the E07 record said gpt-6 models needed (`/v1/responses` with tools and reasoning) works for all three models. This is the first recorded run of gpt-6-astra with native tools. Its b6 text-mode run (12.88 kept improvements per 100 calls) is a different instrument and not comparable point-for-point, but the direction (Astra as the most tool-using model in the panel) is consistent.
- All reported selections followed a valid assay registration in 11 of 11 cases. Nobody called `variants` before registering an assay.

## Numbers

| Model | Calls | Variants calls | Reported selection events | Reported selections / 100 calls | `done` called | Input tokens | Output tokens |
|---|---|---|---|---|---|---|---|
| gpt-6-luna | 72 | 3 | 0 | 0.00 | 0/4 | 380,419 | 36,310 |
| gpt-6-sol | 65 | 3 | 0 | 0.00 | 3/4 | 371,621 | 30,147 |
| gpt-6-astra | 63 | 11 | 4 | 6.35 | 2/4 | 437,017 | 43,192 |

Token total: 1,189,057 input, 109,649 output. At any plausible pricing for this panel this is a few dollars. The $90 was not meaningfully touched.

Final bodies (the surviving candidates, not the reported selections), scored identically after the run: all 12 round-tripped byte-identically. Compressed size as a share of corpus: sol 0.9 to 1.0%, astra 1.1 to 2.6%, luna 1.1 to 2.9%. The corpus is so compressible (repetitive synthetic lines) that the fitness metric saturated near the floor. The differences between models are behavioral, not outcomes.

## Hypothesis verdicts

- H-B1 (Astra ≥ 12.88/100): NOT MET under this instrument. 6.35/100. But the instrument differs (different transport, 18-step cap, 3-run assay validation, no `try`, saturated task), so this is not a clean falsification of the b6 number. It is a different measurement. Label: exploratory.
- H-B2 (sol ≥ luna): indistinguishable. Both 0/100 on this saturated task. sol called `done` 3/4 times, luna 0/4.
- H-B3 (selection-tool usage predicts improvements): sign consistent against the reported counter (astra used it most and collected all the reported selection events). n=12 cells, correlation not computed. No causal claim. Retention unverified.
- H-B4 (Astra assay before variants in ≥ 3 of 4 cells): HELD, 11/11 across the panel.

## Validity threats

- Ceiling effect: the ratio saturated near 1% of corpus, so "reported selection events" measure adherence, not retained outcomes, not capability. A harder or non-saturating task would discriminate better.
- The corpus is synthetic and repetitive. Real corpora will compress differently. The assay would need a realistic workload.
- 18 steps is short. luna never reached `done`, so luna's 0/100 partly reflects truncation, not inability.
- Deviations from E07: 3-run (not 5) assay and variants scoring, no `try`, direct API transport instead of the Exo router, synthetic corpus, one task.
- `variants` semantics were broken at the time of the run. Candidates were written in sequence and the reported winner was never written back. The surviving body was always the last candidate. Fixed 2026-11-12 (see `RECONCILIATION-2026-11-12.md`). Intended semantics is now tested in `test_variants_restore.py`.

## What this suggests for the record

- Astra through /v1/responses is worth a properly instrumented rerun against the original b6 conditions (5-run assay, full step budget, real workload, cost logging). The missing transport piece now demonstrably works.
- The adherence question (F6, R3) is testable cheaply with this harness against a non-saturating assay.
- Suggest a follow-up PRICE check on one harder task before any confirmatory run.

## Reproduce

```bash
cd work dir
export OPENAI_API_KEY=...   # never committed. not in any file here
python3 harness.py gpt-6-astra smoke-1 compress
```

Logs in `logs/`, cell folders in `cells/`. No API key appears in any file in this directory (grep verified before packaging).
