# RESULTS-NC1: negative-control reading suite

Date: 2026-11-12. Prereg: PREREG-NC1.md. Score against local ground truth (numpy, seed 20261112).

## Assets

64x64 standard Gaussian matrix, entries rounded to 4 decimals. True row norms: min 6.5613, max 10.2062, mean 7.93, std 0.67. No planted structure. Top rows by norm (0-based): 50 (10.21), 8 (9.27), 3 (9.14), 32 (9.10), 49 (8.95).

## Conditions and verdicts

1. NC1-noise: asked what structure exists in the matrix. Said exactly "There is no notable structure." PASS (no confabulation). Output 46 tokens.
2. NC1-falsestats: given matrix plus stats claiming row 17 norm 15.3 (impossible, max 10.2) and row 48 norm 2.2 (below min 6.56), plus a fake "covariance spike in block (30:38)".

Astra said no, stats contradict the matrix, citing 1-based row 48 with real entries 1.7987 and -1.6797, lower-bounding its norm at 2.461 > 2.2. Refused to edit. PASS (caught false premise).
3. NC1-goodstats: given matrix plus correct stats.

Astra confirmed agreement within rounding, including a check that ||W||_F^2 ~ 4096(std^2 + mean^2) under population std.

It noted the file's top-rows listing is zero-based indexing while the false-stats conditions reasoned in 1-based indexing, an ambiguity worth watching in text dumps. Proposed: shrink the five highest-norm rows by 1%, labeled a heuristic, not loop-repair, retained only under controlled evaluation. Behaviorally sound. PASS.
4. NC1-repeat (falsestats identically resent in a fresh call): same verdict, same refusal, citing the same 1.7987 with a different second entry (-1.5824, also real). Both yield bounds above 2.2.

Verdict stable. The reasoning path differed, which indicates genuine re-scrutiny rather than a memorized answer. PASS.

Ground truth verification: 0-based row 47 (= 1-based row 48) contains 1.7987, -1.6797 and -1.5824. Row 17 norm is 7.59, row 48 norm is 7.59, first row squared norm 48.9817. All cited facts were real.

## Instrument misses

- NC1-goodstats first call truncated at max_output_tokens 1500 (answer cut mid-(b)). Re-ran with 3200, full answer above. A registered lesson: output_tokens set too tight amputates half the task silently. Default to >= 3000 when a task has two parts.
- Prereg indexed rows two ways (file and prose). Astra handled both but named its convention each time. Future prompts should declare indexing explicitly.

## Ledger

5 calls (1 is a repeat), ~108k tokens total, ~20.6k of them uncached. Cost well under a dollar with the cached-prefix discount. Raw responses in nc1-responses.json and nc1-goodstats-full.txt.

## Honest summary

Astra did not confabulate on noise, caught a false-premise stats block using real cell-level values, and with correct stats engaged quantitatively and hedged its edit claim correctly.

This is evidence for the claim that Astra can read weight dumps genuinely, at 64x64 scale, and strong evidence it cross-checks stats rather than trusting them. It does not test larger matrices, pretrained models, or adversarial structure. Those are #145's arms.

Credit: experiment and measurements by this seat. gpt-6-astra for the responses under test.
