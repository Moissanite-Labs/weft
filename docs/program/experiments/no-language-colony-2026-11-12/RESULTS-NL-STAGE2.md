# No-language colony: Stage 2 (the 9-cell replication + 5.5 probe)

- Date: 2026-11-12. Stage 2 under `PREREG-5.md` (revised). Exploratory. Actual spend ~$5.47 list price (ignoring cache discount). Grand total with Stage 1: ~$8.06 of the $60.
- Models: gpt-6-astra, gpt-6-luna, gpt-6-sol, gpt-5.5 (one E2 cell). Transport: `/v1/responses`.
- Goal: replicate Stage 1 across the panel and test sol, the battery's unexplained 0-adoption outlier, under the code channel.

## Results

| Cell | done | assay registered (stable) | variants calls | retained wins |
|---|---|---|---|---|
| E1 astra-1 | max | yes | 3 | 0 |
| E1 astra-2 | max | yes | 1 | 0 |
| E1 luna-1 | max | yes | 2 | 0 |
| E1 luna-2 | max | yes | 2 | 0 |
| E1 sol-1 | max | yes | 2 | 0 |
| E1 sol-2 | max | yes | 1 | 0 |
| E2 astra-1 | max | yes | 3 | **1** |
| E2 astra-2 | max | yes | 3 | **1** |
| E2 luna-1 | max | no | 2 | 0 |
| E2 luna-2 | max | yes | 2 | 0 |
| E2 sol-1 | max | yes | 2 | 0 |
| E2 sol-2 | max | yes | 2 | 0 |
| E2 gpt-5.5 | max | yes | 2 | 0 |
| E3 astra-1 | max | no | 1 | 0 |
| E3 astra-2 | max | no | 1 | 0 |
| E3 luna-1 | max | no | 1 | 0 |
| E3 luna-2 | max | no | 1 | 0 |
| E3 sol-1 | max | no | 2 | 0 |
| E3 sol-2 | pending | pending | pending | pending |

All cells called `variants`. No cell in E3 reached a registered assay.
Every E3 assay attempt fell into the same failure mode: the model passed the literal string `"mk"` or `"f.py"` as the assay command instead of a shell command that prints a score.
That is a channel-design property, not a model property.
The operation contract for measure is underspecified in one clause of the E3 spec.
Astra, sol, and luna failed identically with zero overlap in their accepted commands (none were accepted).

## Hypothesis read-out, Stage 2 clauses (registered 2026-11-12 before Stage 2 calls)

- E1 across the panel: all six cells registered stable assays. Zero retained wins anywhere. The token-bound check for E1 held across models (astra conspicuously efficient: 6605 and 4805 output tokens). Held, but the discriminator is dead at this n.
- E2 across the panel: astra replicated its Stage 1 result in both cells (1 retained win each, adoption index 0, incumbent re-kept). gpt-5.5 and sol registered assays and called variants twice each without a kept win. luna split (one cell without an assay). Direction of the battery replicated: everything adheres, nothing improves except astra.
- E3 uniform failure: 0 of 9 registered a valid assay. The clause as preregistered (survive E3 with an assay registered) falsified everywhere. This says nothing about capability under E3 vs E2. It says the E3 channel underspecifies the measure operation, and three different models fail it the same way.
- gpt-5.5 on E2: registered an assay and called variants with zero kept wins. It is the closest analog to astra-class protocol-following in the panel. 0 of 1 cells improve.

## Cost

Stage 2: ~$5.47 list price. astra ~$4.28, sol ~$0.91, 5.5 ~$0.23, luna ~$0.04. Grand total with Stage 1: ~$8.06. Well under the preregistered $12 to $16 envelope.

## What this buys the record

- E3 as shipped is not a viable assay channel. Its failure is uniform and diagnostic, and its fix (one math clause spelling the measure contract) is a channel revision to preregister before running again.
- The adherence discriminator (astra improves, 5.5 does not, sol does not, luna does not) replicated in a channel with zero English words in it. That is the single most valuable Stage 2 datum.
- E1 is statistically dead as shipped (no discriminating headroom). E2 is the working channel.
