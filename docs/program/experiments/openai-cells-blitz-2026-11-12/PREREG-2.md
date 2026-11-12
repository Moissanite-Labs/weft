# PREREG-2 — OpenAI colony battery, 2026-11-12 (exploratory, budget-capped)

- Date registered: 2026-11-12, before any E18 call. Follows PREREGISTRATION.md and RESULTS.md.
- Status: exploratory. Nothing here is confirmatory; everything ships with "exploratory" attached.
- Budget: user directive to spend at least $30 of expiring credits doing valuable experiments. Stop rule: cumulative estimated spend (table below, summed over every API call in this directory, including the earlier blitz) reaches $38; we overshoot $30 honestly rather than scrape it.
- Pricing source: developers.openai.com pricing page, checked 2026-11-12. Standard rates, short context (input <= 272K tokens per request): gpt-6-astra $10 in / $50 out; gpt-6-sol $2/$10; gpt-6.1-terra $1/$5; gpt-6-luna $0.10/$0.50; gpt-5.5 $5/$30; gpt-5.4 $2.50/$15; gpt-5.4-mini $0.75 in / $4.50 out (conservative of the two published figures; marks our estimate up, not down). Cached input billed at 10% (luna, sol, astra, terra) so history replay is not full price.

## Price accounting so far

The 2026-11-12 blitz cost, at the table above: astra 437,017 in x $10 + 43,192 out x $50 = $8.53; sol 371,621 in x $2 + 30,147 out x $10 = $1.04; luna 380,419 in x $0.1 + 36,310 out x $0.5 = $0.06. Blitz total $9.63 (cache ignored, an overestimate).

## E18a — Non-saturating assay

- Corpus `corpus_hard.txt` (44,267 bytes, sha256 `00abb98851008a506a270c84646431194f943e80f16d17da3d1b2e5242a9ef76`): 50% low-entropy templated lines, 30% random hex, 20% random alphanumerics. Same `compress` task, same assay rules.
- 6 cells x 3 models (gpt-6-astra, gpt-6-sol, gpt-6-luna), 18 steps, same harness.
- H-A1: on the saturated corpus, astra's per-cell adoption rate was 4/4; on the hard corpus it stays above 50% of cells adopting at least one variant. Falsified if 0 of 6 astra cells adopt.
- H-A2: sol or luna adopts at least one variant on the hard corpus (the saturated corpus showed none). Falsified if both groups adopt 0.
- H-A3: mean best percentage reduction on hard corpus < 60% for every model (base64-like blocks cap it). Falsified if any model's cells average above 60%, in which case the corpus is not discriminating and E18a is reported as saturating after all.

## E18b — Protocol-fit ladder

- Saturated `corpus.txt` task, 15 steps, 3 cells per model, six models across two generations and four tiers: gpt-5.4-mini, gpt-5.4, gpt-5.5, gpt-6.1-terra, gpt-6-sol, gpt-6-astra.
- H-B1: `variants` use rate (calls to variants per 100 model calls) increases monotonically across the ladder above the $1 tier. Falsified if the ladder is uncorrelated with price tier (Spearman sign check, n=18).
- H-B2: at least 2 of the 3 gpt-5.5 cells call `done`; 0 of 3 gpt-5.4-mini cells call `variants` after assay registration.
- H-B3: astra remains the only model adopting variants in this panel, at any adoption rate above 0.

## E18c — Astra ceiling replication

- 8 additional gpt-6-astra cells on the saturated corpus, 15 steps, identical conditions to the blitz.
- H-C1: astra adoption rate across the blitz 4 + these 8 cells is between 30% and 100% of cells (i.e., the 4/4 was not a fluke). Falsified if total adoptions across 12 cells fall below 3.

## E18d — Embedding fingerprint replication

- Embed every `compress.py` ever written in this directory (all waves) with `text-embedding-3-large`. Report same-model vs cross-model mean pairwise cosine distance, and the permutation p-value (10,000 shuffles) for "same-model pairs are closer".
- H-D1: not supported, replicating the E07 same-model control. Falsified (i.e., support claimed) only if permutation p < 0.01 with the pooled sample.
- Cost note: negligible (one file under 10 KB each, ~50 files).

## Rules

- No corpus, harness or assay text changes between waves except the two documented ones (CORPUS_FILE selection, BLITZ_MAX_STEPS env).
- Failures are logged and reported, not rerun with quieter settings.
- The API key is read from the environment at run time; it never appears in any file in this directory.
- Results go into RESULTS-E18.md with per-wave tables and the running cost ledger against this file's table.
- Preregistered hypotheses may report as falsified; that is the point of registering them.
