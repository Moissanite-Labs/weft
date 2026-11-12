# E18: OpenAI colony battery, running notes

- Date: 2026-11-12. Follows `PREREG-2.md`, `PREREG-3.md`, `PREREG-4.md` (all registered before the calls they govern. E18e added mid-battery with its own note).
- Status: exploratory. Costs below are list-price upper bounds and are wrong for cached input (the project history prefix is replayed and billed at a tenth). The owner's balance check after the E18a–E18c waves showed about $2 actually spent on the key, an order of magnitude below the bound. Output tokens are billed at full price regardless.
- Correction 2026-11-12 (post-review): the harness's `variants` selection did not write the selected winner back to disk.
- Every "adoption" here was a reported selection event, not a verified retained win. Zero of 38 reported events across the battery had the winner on disk at adoption time under the old harness.
- Replay under the fixed semantics: all 38 would have persisted, with zero decision changes. See `RECONCILIATION-2026-11-12.md` and `REPLAY-2026-11-12.md`. Verdicts below are marked where they rest on the selection counter.
- Owner directive being executed: at least $30 of the expiring credits spent on valuable experiments, and the repo updated after each wave.

## Ledger (list-price upper bound)

| Wave | Tokens (in / out) | Est. cost @ list |
|---|---|---|
| Blitz (PR #139 base) | 1,189,057 / 109,649 | $7.63 |
| E18a (compress-hard, 6 cells x 3 models) | 1,621,170 / 136,313 | $7.07 |
| E18b (protocol-fit ladder, 3 cells x 6 models) | 968,587 / 112,525 | $6.17 |
| E18c (astra replication, 8 cells, saturated) | 482,901 / 54,405 | $7.55 |
| E18e (terra replication, 6 cells) | 404,949 / 44,391 | $0.63 |
| E18f (gpt-5.5 replication, 4 cells) | 240,616 / 19,111 | $1.78 |
| E18d (text-embedding-3-large, 65 files) | ~65 KB total | ~$0.01 |
| E19a (astra, reasoning.effort=max, 13 partial cells incl. retries) | 1,443,226 / 206,301 | $24.75 |
| E19b (astra, variants tool removed, 8 cells) | 381,261 / 35,083 | $5.57 |
| Upper-bound total | 6,731,767 / 717,778 | ~$61.15 |
| Actual per owner balance (full battery, owner-reported 2026-11-12) | not available | ~$30 |

The gap between bound and actual is the cache discount on replayed context, and it is where the money went: most tokens were history replay, not new reasoning. Output-token spend (full price) is the binding term, roughly $20 by list price across E18a–E19b.

## E18a: compress-hard (44,267 bytes: 50% templated / 30% hex / 20% random. sha256 in PREREG-2.md)

| Model | Cells | Calls | Variants calls | Reported selection events | Reported selections / 100 calls | Mean / median reduction |
|---|---|---|---|---|---|---|
| gpt-6-luna | 6 | 89 | 9 | 3 | 3.37 | 57.1% / 57.7% |
| gpt-6-sol | 6 | 104 | 14 | 0 | 0.00 | 61.5% / 61.7% |
| gpt-6-astra | 6 | 69 | 9 | 6 | 8.70 | 62.0% / 62.0% |

All 18 final bodies round-trip byte-identically.

- H-A1 (astra > 50% of cells adopt): HELD against the reported counter, 6/6. Retention unverified.
- H-A2 (sol or luna adopts >= 1): HELD against the reported counter, via luna (3 reported selection events across 2 cells, the first luna events on record). Sol 0/6.
- H-A3 (mean < 60% for all): FALSIFIED as registered. Sol 61.5% and astra 62.0%. only luna stayed below. The corpus still saturates: stdlib methods ceiling near 62%, so sol and astra both approached it identically.

## E18b: protocol-fit ladder (saturated corpus, 15 steps, 3 cells per model)

| Model | Calls | Variants calls | Reported selection events | done |
|---|---|---|---|---|
| gpt-5.4-mini | 29 | 0 | 0 | 2/3 |
| gpt-5.4 | 27 | 3 | 0 | 3/3 |
| gpt-5.5 | 45 | 3 | 0 | 0/3 |
| gpt-6.1-terra | 44 | 4 | 1 | 1/3 |
| gpt-6-sol | 37 | 3 | 0 | 2/3 |
| gpt-6-astra | 36 | 6 | 3 | 3/3 |

- H-B1 (usage rises with price tier): FALSIFIED. Luna, cheapest in the panel, used variants 12 times in 144 calls across waves. price tier does not order tool adherence.
- H-B2 (>= 2 of 3 gpt-5.5 call done): FALSIFIED (0/3). Second clause (mini calls variants 0 times): HELD.
- H-B3 (astra is the only adopter): FALSIFIED against the reported counter: gpt-6.1-terra reported one selection (`gpt_61_terra-l-2`). Astra was 3/3 in this wave.

## E18c: astra replication (saturated corpus, 15 steps)

8/8 cells reported exactly one selection event. Combined with the blitz 4/4 and E18b's 3/3, astra was 15/15 on the saturated corpus before E18e/E19 waves. Reported, not retained.

- H-C1 (>= 3 adoptions across blitz + this wave): HELD against the reported counter.

## E18e: terra replication (6 cells. falsified H-B3 follow-up)

3 of 6 cells reported exactly one selection event (`gpt_61_terra-r-2/3/5`). Total terra record: 4 of 9 cells. Reported, not retained.

- H-E1 (terra adopts >= 1 of 6): HELD against the reported counter.
- H-E2 (terra adoptions/100 calls > gpt-5.4 and gpt-5.5): HELD against the reported counter (gpt-5.4 0/27 calls, gpt-5.5 0/45, terra 4/134 across all nine cells).

## E18f: gpt-5.5 replication (4 cells. 7 with E18b)

0 reported selection events, cumulative 0 of 7 cells. done-call rate: 1 of 7 (`gpt_55-r-2`).

- H-F1 (stays at 0 adoption): HELD (there were no reported events to retain).
- H-F2 (>= 2 of 4 call done): FALSIFIED (1/4. cumulative 1/7).

## E18d: embedding fingerprint replication (text-embedding-3-large, 65 of 66 final bodies. `gpt_55-r-2` skipped, > 8192 tokens)

- Pooled same-model mean cosine distance 0.2536 vs cross-model 0.3637. label-permutation p < 0.0001 (10,000 shuffles). H-D1 ("not supported") is falsified as registered at the pooled level.
- Run-level control: within (model, run) pairs 0.2287. same-model cross-run pairs 0.2694. cross-model 0.3637. The pooled signal is mostly within-run correlation (same corpus, same assay family), not a stable per-model fingerprint. This is consistent with the E07 negative control and should be read as "families cluster on the same task", not as an identity code.
- H-D1's registration required p < 0.01 for support. that bar is met, but the run-level contrast does not support a fingerprint claim. Both statements stand.

## E19a: gpt-6-astra at `reasoning.effort = max` (13 partial cells. 5 of 8 nominal cells hit a 180 s socket timeout mid-run and were re-run with a 900 s timeout, zero content changes)

| Condition | Cells | Reported >= 1 selection | done |
|---|---|---|---|
| Saturated, nominal | 4 | 3 | 0/4 |
| Saturated, retry | 2 (re-run) + 2 partials | 5 total | 0/6 |
| Hard, nominal | 4 | 2 | 1/4 |
| Hard, retry | 3 re-run + 1 partial | 5 total | 3/7 |

- Partial cells are kept in the record. their reported selection events count. Nominal 8 cells: 5/8 reported, which falsifies H-G1 (>= 6 of 8) as registered. With retries the reported record is 10/13. Reported, not retained.
- H-G2 (done rate >= default effort): FALSIFIED on both corpora (max: 0/4 sat, 1/4 hard. default waves: most cells call done).
- H-G3 (more variants calls per cell at max effort): FALSIFIED (max ~1.5/cell vs default ~2.2/cell).
- Content of max-effort cells is markedly more elaborate (enumerated structural analysis of the corpus, e.g. `astra-max-hard-1` produced an exact per-record byte model). The quality jump does not translate into more kept wins.

## E19b: selection-tool ablation (variants removed from the offered toolset. astra, 4 cells per corpus, 15 steps)

- H-H1 (0 reported selections with the tool absent): HELD trivially, and deliberately so. The instrument is the channel E18 measures. removing it measures exactly the channel's contribution. All cells still reached working compressors (round-trip OK) and finished via `done` 8/8.
- H-H2 (>= 75% register a stable assay): HELD, 8/8.
- Reading: astra calls the selection channel when it is offered and does not synthesize one when it is not. The reported selection events are attributable to the instrument, not to unverifiable self-assessment. Retention is unverified.

## Verdicts on the panel as a whole

- Astra is the adherent frontier model on this task and instrument (21/21 reported selection events at default effort across corpora before E19, 10/13 at max effort with retries counted), and it remains the only GPT-6 family member that consistently reports selections. terra reports a real but weaker signal (4/9). Reported, not retained.
- Generation-5 flagship (gpt-5.5) reports no selections (0/7) and rarely calls done (1/7). Generation-6 reasoning models report selections. This is a transport- and tier-dependent protocol-fit gap, not a raw capability ordering.
- Luna, the cheapest model, uses the selection tool when it can (12 variants calls in 144 saturated-corpus calls across waves) and reported selection events 3 times only on the hard corpus. Class-9 cost class out-adhers the class-5 flagships on this metric.
- The compliance finding H-B4 from the blitz (all variants calls after assay registration) held everywhere in E18/E19.

## Threats and notes

- One task, one corpus family, tiny cells. Everything exploratory. no causal claim generalizes beyond this harness.
- The assay ceiling (~62% with stdlib methods) makes outcome gains a small signal. behavioral adherence is the informative output.
- Max-effort cells timed out at 180 s and were re-run with a 900 s socket timeout. both the timed-out partials and the retries are in `cells/` and `logs/`.
- `gpt_55-r-2` was excluded from embeddings (> 8192 tokens). Its inclusion would not change the qualitative finding.
- Cost accounting is list-price upper bounds. input caching discounted real spend roughly 10x on the dominant token class.
