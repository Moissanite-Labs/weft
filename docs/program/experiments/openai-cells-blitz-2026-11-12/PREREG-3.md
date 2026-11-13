# PREREG-3 — addendum: E18e and E18f (registered 2026-11-12, before any E18e/E18f call)

E18b falsified H-B3 (gpt-6.1-terra adopted once, gpt_61_terra-l-2). Two open questions, two small waves, same task, same step cap, same harness as E18b. The 28.42 USD spent so far (ledger in RESULTS-E18.md) is below the 30 USD floor the owner set; these two waves add about 4 USD, all on questions from the prereg'd battery, not padding.

## E18e — terra replication

- gpt-6.1-terra, 6 cells, saturated corpus, 15 steps, same transport and harness as E18b.
- H-E1: terra adopts at least one variant in at least 1 of 6 cells. Falsified if 0/6 adopt, which would size terra's 1/3 down to noise (~ a binomial 1-of-9 event at 25% adoption).
- H-E2: terra's adoptions per 100 calls exceed those of gpt-5.4 and gpt-5.5 (both 0 across the E18b panel).

## E18f — gpt-5.5 replication

- gpt-5.5, 4 more cells (7 total with E18b), saturated corpus, 15 steps.
- H-F1: gpt-5.5 adoption rate stays at 0 in the additional 4 cells. Falsified if it adopts, which would break the generation-5 null result observed so far (0 adoptions in 3 E18b cells, 15 variants calls, 3 shown).
- H-F2: gpt-5.5 continues to complete without calling done in at least 2 of 4 cells (E18b: 0/3 called done).

## Rules

Same as PREREG-2: logging, environment-variable key, no cherry-picking, negatives reported. Together with E18a-E18d this closes the E18 battery.
