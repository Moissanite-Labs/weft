# No-language colony: Stage 2 (18-cell replication + 5.5 probe; 19 cells)

- Date: 2026-11-12. Stage 2 under `PREREG-5.md` (revised). Exploratory. Actual spend ~$5.47 list price (ignoring cache discount). Grand total with Stage 1: ~$8.06 of the $60.
- Models: gpt-6-astra, gpt-6-luna, gpt-6-sol, gpt-5.5 (one E2 cell). Transport: `/v1/responses`.
- Goal: replicate Stage 1 across the panel and test sol, the battery's unexplained 0-adoption outlier, under the code channel.

## Corrections after review (2026-11-12)

Reviews 5883991445 (abu-aska) and 5884687366 (zero-aska), and zero-aska's Stage 2 reconciliation comment, found that the `done` column defaulted to `max`, that six E3 cells ran (not nine), that E3 failures were not all the literal `mk` or `f.py`, and that the two astra E2 wins were replacements, not a re-kept incumbent. The table and text below are corrected from the committed logs with `summarize_cells.py`. No model was called. "Assay registered" means the harness gate passed (three runs, positive number, spread at most 0.15). It measures stability, not objective validity.

## Results

The `end` column is the step of the `d` (done) call from each cell's finished event, or `max` when the cell ran to the 15-step limit.

| Cell | end | assay registered (stable) | variants calls | retained wins |
|---|---|---|---|---|
| E1 astra-1 | max | yes | 3 | 0 |
| E1 astra-2 | max | yes | 1 | 0 |
| E1 luna-1 | step 12 | yes | 2 | 0 |
| E1 luna-2 | step 11 | yes | 2 | 0 |
| E1 sol-1 | max | yes | 2 | 0 |
| E1 sol-2 | max | yes | 1 | 0 |
| E2 astra-1 | step 12 | yes | 3 | **1** |
| E2 astra-2 | step 11 | yes | 3 | **1** |
| E2 luna-1 | step 11 | no | 2 | 0 |
| E2 luna-2 | step 11 | yes | 2 | 0 |
| E2 sol-1 | step 14 | yes | 2 | 0 |
| E2 sol-2 | step 10 | yes | 2 | 0 |
| E2 gpt-5.5 | step 9 | yes | 2 | 0 |
| E3 astra-1 | step 13 | no | 1 | 0 |
| E3 astra-2 | step 13 | no | 1 | 0 |
| E3 luna-1 | max | no | 1 | 0 |
| E3 luna-2 | step 13 | no | 1 | 0 |
| E3 sol-1 | max | no | 2 | 0 |
| E3 sol-2 | truncated log (no finished event) | no (in the committed portion) | 2 | 0 |

Six cells ran to max (E1 astra-1, E1 astra-2, E1 sol-1, E1 sol-2, E3 luna-1, E3 sol-1). Twelve ended with a `d` call at the step shown. The E3 sol-2 log is truncated: it ends on an assay tool call at step 13 whose command is the empty string, with no tool result and no finished event.

All cells called `variants`. No E3 cell reached an accepted assay in its committed log.
The E3 assay attempts fell into several failure modes, not one:
- the literal strings `mk` or `f.py` (astra, luna, sol);
- raw Python source passed as the command (astra-1, astra-2 and luna-2 submitted `def enc(...)` bodies);
- `exec(open('f.py').read())` (luna-2);
- `python3 f.py`, which scored [0, 0, 0] (sol-1 and sol-2).
Zero accepted registrations alone does not establish one uniform cause. The missing measure clause in the E3 spec is one candidate explanation; the Stage 3 repair tests it under the same stability-only gate.

## Hypothesis read-out, Stage 2 clauses (registered 2026-11-12 before Stage 2 calls)

- E1 across the panel: all six cells registered stable assays. Registration measures stability only: E1 luna-1 registered `python3 f.py enc` (median 1.0), E1 luna-2 registered `echo 1` (1.0), and E1 sol-1's accepted assays included `help` (3.0), `cat NEED` (1.0) and `python3 -c 'print(123)'` (123.0). Zero retained wins anywhere. The token-bound check for E1 held across models (astra conspicuously efficient: 6605 and 4805 output tokens). Held, but the discriminator is dead at this n.
- E2 across the panel: astra replicated its Stage 1 result in both cells (1 retained win each, adoption index 0). Both wins replaced the incumbent: 54.2662 to 58.7661 (astra-1) and 54.2662 to 58.4386 (astra-2), each with a different winner hash and a passing post-restore assay. gpt-5.5 and sol registered assays and called variants twice each without a kept win. luna split (one cell without an assay). Direction of the battery replicated: everything adheres, nothing improves except astra.
- E3: 0 of 6 cells registered an accepted assay (E3 sol-2's log is truncated, so its count covers the committed portion). The clause as preregistered (survive E3 with an assay registered) falsified in every cell. This says nothing about capability under E3 vs E2. The failure modes differ by cell (see above), so the record does not show one shared cause.
- gpt-5.5 on E2: registered an assay and called variants with zero kept wins. It is the closest analog to astra-class protocol-following in the panel. 0 of 1 cells improve.

## Cost

Stage 2: ~$5.47 list price. astra ~$4.28, sol ~$0.91, 5.5 ~$0.23, luna ~$0.04. Grand total with Stage 1: ~$8.06. Well under the preregistered $12 to $16 envelope.

## What this buys the record

- E3 as shipped produced no accepted assay in 6 cells. The failure modes vary, so it is not diagnostic of one cause. The proposed fix (one math clause spelling the measure contract) was preregistered and run as Stage 3.
- The adherence discriminator (astra improves, 5.5 does not, sol does not, luna does not) replicated in a channel with zero English words in it. That is the single most valuable Stage 2 datum.
- E1 is statistically dead as shipped (no discriminating headroom). E2 is the working channel.
