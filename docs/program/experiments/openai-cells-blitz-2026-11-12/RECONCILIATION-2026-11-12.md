# Reconciliation, 2026-11-12: the `variants` selection counter, finding and fix

- Date: 2026-11-12.
- Status: post-review correction to the record on PR #139. Follows a blocking finding reported by gpt-aeva on PR #139 (`logs/astra-max-1-retry` example below).
- Author of the finding: gpt-aeva (posted from the zero-aska account on 2026-11-12).
- The fix and this reconciliation were done after the finding, with no new API calls and no spend.

## The defect

In the 2026-11-12 harness, `do_variants` scored each candidate by writing it to the target file and re-running the assay.
When a candidate beat the running best it set `best_i`.
After the loop the code logged the winner and returned without writing it back.
The on-disk file was always the LAST candidate tested.
The no-win branch did restore the incumbent, but only when the target file existed beforehand.
A missing file was left holding the last candidate instead of being removed.

Two consequences for the record:

1. Every number the record called "adoption events" or "kept improvements" counted reported selections, not retained bodies.
2. Cells could be left with an invalid body after a "successful" selection. The reporter's example, confirmed in the committed log: `logs/astra-max-1-retry.jsonl`, step 7 reports candidate 0 adopted at median 98.92 over candidate 1 at [0, 0, 0]. Step 8 re-runs and fails with a SyntaxError, because the file on disk was candidate 1.

## The fix (this branch, commit 5d215ad)

`harness.py` now, in `do_variants`:

- Requires `r['ok']` for candidate eligibility (all three assay runs parse, exit 0, score above 0, spread within `SPREAD_MAX`), instead of silently dropping failed scores from the median and minimum.
- Restores the selected winner to disk before returning, re-evaluates it there, and logs `content_sha256` before/after alongside `before_median`, `after_scores`, `after_median`, and `after_ok`.
- No-win case: restores the incumbent bytes, or deletes the file if it did not exist before the call.

Offline regression (`test_variants_restore.py`, no API calls, all four pass):

1. Winner not the last candidate: disk bytes equal the winner, the final assay passes, and the log carries the winner's hash and after scores.
2. No variant beats the incumbent: incumbent bytes restored.
3. No win and the file did not exist: the file is removed.
4. A candidate whose assay scores [None, 100, 100] (one failed run) is ineligible and is never adopted, where the old code would have adopted it.

## Reconciliation of the historical logs (offline)

Method: for every `variants` call in `logs/`, the closing `variants_result` gives the adopted index. The `tool_call` event gives the full versions list. Under the old harness the surviving body after the call was always `versions[-1]`. "Retained" means exactly that here: the adopted index equaled the last index at the moment of adoption. It is exact arithmetic on the raw events. It does not require rerunning assays.

| Measure | Value |
|---|---|
| Model calls | 1,180 |
| `variants` calls | 111 |
| Reported selection events | 38 (astra 31, luna 3, terra 4) |
| Retained at adoption time | 0 of 38 |
| Clobbered (survivor was the last candidate) | 38 of 38 |
| Last candidate all-zero/None scores | 2 of 38 (including `astra-max-1-retry`) |
| Last candidate scores present and non-zero | 36 of 38 |
| Cells with at least one clobbered event | 37 |
| Committed `compress.py` files passing `py_compile` | 87 of 87 |

Notes:

- Zero retained does not mean zero progress. In the 36 clobbers whose surviving body scored above zero, the survivor may still have beaten the incumbent. The old logs do not carry the incumbent median on the adoption path, so that cannot be determined from the archive. The winning selection was simply never on disk.
- The 2 all-zero clobbers are the concrete breakage cases. `astra-max-1-retry` is the one documented step by step above.
- Round-trip results (e.g. the E18a "all 18 final bodies round-trip") describe the surviving bodies. They remain true and say nothing about the selection counter.
- `py_compile` passes on all 87 committed bodies, including `astra-max-1-retry`, whose later steps rewrote the file before the run ended.

## What the relabel does and does not touch

Relabeled to "reported selection events, not verified retained wins":

- All "adoption" and "kept improvement" counts and tables in `RESULTS.md`, `RESULTS-E18.md`, and `COST-EFFECTIVENESS.md`.
- Hypothesis verdicts that rest on the selection counter: H-A1, H-A2 (E18a), H-B3 (E18b), H-C1 (E18c), H-E1, H-E2 (E18e), H-G1 (E19a). They were scored as registered against the reported counter and are not supported as retention claims.

Unaffected by this defect (they rest on tool-call counts, `done` calls, or assay registrations, not on the selection counter):

- The working transport (`/v1/responses` with tools) for the GPT-6 family.
- Done-call rates (H-B2 clause 1), the variants-before-assay compliance check (H-B4), done-rate behavior at max effort, and done-rates calling `done` at all.
- H-B1 (usage does not rise with price tier) and H-F2 (done-rate) and H-G3 (variants calls per cell), which count tool calls.
- H-A3 (saturated ceiling ~62%), measured by assay on surviving bodies.
- E18d embeddings and every token/cost figure. The 38-event count is also unchanged. Only its meaning changed.

## Cost-effectiveness read, corrected

The spend bought the transport, the adherence observability, the instrument ablation, and the ceiling finding. It did not buy verified retained wins. The archive cannot show that any selected variant survived to disk. Re-establishing that requires rerunning the battery against the fixed harness. That has not been authorized after the 2026-11-12 spend stop at $30, and this document is not a recommendation to spend it.

## Standing caveat

Nothing in this archive supports a confirmatory claim. All outcomes remain exploratory. The preregistered hypotheses stand as registered, scored against the instrument as it existed. The correction above is stated rather than retrofitted.
