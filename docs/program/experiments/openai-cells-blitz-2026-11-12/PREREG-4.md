# PREREG-4 — E19: max reasoning effort and a selection-tool ablation (registered 2026-11-12, before any E19 call)

Owner's balance after the E18 battery: about $2 spent (list-price accounting was off by an order of magnitude because cached input replays bill at 10%). Owner directive: at least $30 spent, on valuable experiments, and repo updated after each wave.

## E19a — gpt-6-astra at `reasoning.effort = "max"`

- 4 cells on `corpus.txt` (saturated) + 4 cells on `corpus_hard.txt`, 15 steps, same harness and transport; only the reasoning effort differs from E18b/E18a.
- H-G1: astra at max effort keeps its adoption behavior, at least 1 adopted variant per cell in at least 6 of 8 cells. Falsified if adoption collapses below half.
- H-G2: done-call rate at max effort is at least that at default effort (E18b + ladder: 3/3 on saturated, 6/6 on hard). Falsified if max-effort cells call done less often.
- Cost note: max effort multiplies output tokens, which are the expensive part of the astra price ($50/M). This is the intended credit sink and is exactly why the wave is valuable: it tests an untested corner of the adherence question at full price.
- H-G3 (registered, exploratory): max-effort cells complete more variants calls per cell than default-effort cells at equal steps.

## E19b — no-selection-tool ablation (astra)

- The `variants` tool is removed from the offered toolset; the cell gets sh / write / remember / assay / done only, 4 cells on each corpus (8 total), 15 steps.
- H-H1: with no selection tool, adoptions of any file version by the harness are impossible, and the win rate as measured by the harness falls to 0 (registration of the trivial null; any other value indicates an instrumentation bug, not a model result).
- H-H2: the fraction of cells reaching a registered assay stays above 75%. Falsified if most ablation cells fail to register a stable assay without the selection tool available.
- Purpose: attributes the blitz's kept improvements to the selection channel rather than to raw astra competence. The missing control from the original blitz.

## Rules

Same as PREREG-2/3. Counts land in RESULTS-E18.md after the runs; the repo is updated after each wave, per owner instruction.
