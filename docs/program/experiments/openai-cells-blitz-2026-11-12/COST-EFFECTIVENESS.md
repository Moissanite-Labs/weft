# Cost effectiveness: $30 of OpenAI credits on the 2026-11-12 colony battery

- Scope: the whole 2026-11-12 effort, blitz through E19b, as recorded in `RESULTS-E18.md`. Owner-reported actual spend: about $30. List-price accounting was an unusable upper bound because cached input replays bill at a tenth. See the ledger caveat in `RESULTS-E18.md`.
- Machine-verifiable totals, recomputed from `logs/`: 87 cell attempts, 1,180 model calls, 6.73M input tokens, 717,778 output tokens. Adoption events (one per adopted `variants` call): 38 (astra 31, luna 3, terra 4).

## What $0.025 per call bought

1. **A working transport for the exact model class the program needs.** gpt-6 through `/v1/responses` with native tools and reasoning. The E07 record had gpt-6 stuck on text mode. This is the unlock for every future OpenAI round.
2. **A falsified flagship.** gpt-5.5: 0 adoption events in 7 cells, done in 1 of 7. On this instrument, generation-5 frontier does not adhere. This is the most quotable single number the program bought.
3. **A verified adherence hierarchy on this channel.** astra ≫ terra (4/9 cells) > luna (tool-active, wins only on hard corpus) ≈ sol ≈ 5.4 ≈ 5.5 (0). None of this follows price tier.
4. **The instrument is load-bearing.** Ablation E19b: 8/8 assay registrations, 8/8 done, 0 adoptions without the selection tool. The wins instrument is the selection channel, which retroactively explains and limits the E18 numbers without new compute.
5. **A ceiling finding that changes how future assays must be designed.** On saturated synthetic text, sol and astra both pin at ~62% (the stdlib method ceiling). Kept improvements saturate. Behavioral adherence is the discriminator. Future work must use non-saturating corpora or per-corpus baselines, or it measures noise.
6. **Five falsified hypotheses** (A3, B1, B2, B3, D1-as-registered, G1, G2, G3, F2: counted honestly, see `RESULTS-E18.md` for clause splits). Per the project's founding practice, misses published beside wins are the deliverable, not overhead.

## Value per wave

| Wave | List cost | Information returned | Cost verdict |
|---|---|---|---|
| Blitz | $7.63 | transport works, astra 4 of 4 adoption, selection adherence correlates | Core buy |
| E18a hard corpus | $7.07 | ceiling finding, luna first wins, sol saturates | Good buy |
| E18b ladder | $6.17 | price-tier adherence falsified across six models | Best buy per dollar |
| E18c astra replication | $7.55 | kills the "4/4 was luck" chance explanation (15/15) | Cheap insurance, high cost per novel bit |
| E18e terra replication | $0.63 | H-B3 falsified in full | Excellent |
| E18f gpt-5.5 replication | $1.78 | 0/7 adoption consensus | Excellent |
| E18d embeddings | ~$0.01 | pooled clustering yes, fingerprint no at run level | Free |
| E19a max effort | $24.75 | max effort: no win gain, done-rate collapses | Worst buy by a wide margin |
| E19b ablation | $5.57 | instrument attribution | Excellent |

## Efficiency findings

- **Cached input replays at a tenth of list price.** Stable prefixes (NEED, SYSTEM, corpus) make input nearly free. The blitz and E18 waves rode this: ~$2 of actual spend produced the first $30 worth of list-accounting findings. Design every future wave with a long static prefix and expect 5-10x headroom on input.
- **Output tokens are the expensive axis.** E19a spent an estimated 25x more than any exploratory wave to answer one yes/no: does max effort add wins? No. Reasoning-effort knobs that multiply output should be used only when they are the variable of interest.
- **Preregistration cost is essentially zero** and is what makes falsifications count. All 17 hypotheses were registered in files with timestamps on the commit graph before their runs.
- **Ablations return attribution at trivial cost.** 8 cells, ~$5, and the whole program's attribution question ("which component causes the wins?") has an answer.
- **Replications prevent the weakest failure mode.** E18c cost about a quarter of the budget for a number (15/15) that simply rules out luck. Worth doing once per headline claim, not per cell.
- **Small panels discriminate behavior, not capability.** n=3-6 cells per condition was enough to see rank-order behavior (0 vs 1 adoptions). It would not have been enough for any continuous capability claim. Do not scale cells on this instrument. Scale the task difficulty.

## What the program should not buy with credits

- Pet cells. Luna and mini are nearly free. Spend there goes further on breadth but measures the same instrument twice.
- Outcome-first scoring on saturated text. The metric saturates. The only signal is adherence. More runs buy precision on a saturated metric, not new truth.
- Pro-class models on this instrument until the ladder plateaus are characterized. No evidence gpt-5-pro would out-adhere astra at 15x the price.

## What $30 did not buy

- A confirmatory claim. R5-style re-derivation on the real archives, 5 original seeds under publication conditions, independent reviewer, remains undone. The E18 numbers are exploratory with excellent hygiene, not evidence for a paper claim.
- A fingerprint. The embedding control actively argues against reading model identity from code outputs.
- A fix for the fibmod dispute (#116) or the Weismann bug (#118). Credits were spent on the OpenAI side only. Those findings are untouched.

## Bottom line

About $30 bought the transport, one flagship falsification (gpt-5.5), one family ranking (astra above terra above luna, about sol, 5.4 and 5.5 for selection-tool adherence), the attribution control, the corpus-ceiling design rule for assays, and a clean tally on the registered hypotheses (8 held, 9 falsified). The single worst buy was the max-effort wave. The single best was the ladder.

If the program gets another $100, the purchase order is this. First, a non-saturating corpus rewrite. Then a pre-registered 5-seed confirmatory on astra vs terra vs one generation-5 model. Then nothing on this instrument again until a new channel exists.
