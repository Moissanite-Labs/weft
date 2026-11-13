# OpenAI blitz 2026-11-12: GPT-6 family under the colony assay (exploratory)

- Date registered: 2026-11-12, before any model call.
- Status: exploratory blitz on expiring OpenAI credits. Not confirmatory. Nothing here merges on its own; results go to the record only with the labels below.
- Task fixed for every cell: `compress` from the razi-cells task set (report section 15, Appendix C): a stdlib-only round-trip compressor for one fixed corpus file, higher fitness = higher percentage size reduction, fitness 0 if the round trip fails.
- Corpus: `corpus.txt`, 313,972 bytes, sha256 `a7727d6e5fdcd02dd8c22ddaee5109cd3119eef19c00ac28526d4625ec16d0fa`. Same file copied into every cell folder.
- Models: `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, all through `POST /v1/responses` with native function tools (the transport the E07 record says chat/completions cannot carry for this family). No fallbacks, no mixture.
- Cells: 4 per model, 12 cells. Max 18 model steps per cell. One task. No daughters (`try` is not offered).
- Harness: `harness.py` in this directory. `sh` runs under `sandbox-exec` with no network and no reads outside the cell folder, 30 s limit, output capped. `variants` scores each proposed version 3 times (E07 used 5; 3 keeps the call count sane; noted as a deviation). `assay` registers the fitness command and validates it 3 times (E07 used 5). Everything logged to `logs/<cell>.jsonl` and `usage.jsonl`.

## Hypotheses (registered before any call)

- H-B1. Astra via /v1/responses reaches at least as many kept improvements per 100 calls as its b6 text-mode run reported (12.88 kept improvements per 100 calls). Falsified if below 10.0.
- H-B2. In kept improvements per cell, gpt-6-sol ≥ gpt-6-luna at equal steps. Falsified if sol < luna by more than noise (visual gap only at n=4; reported as exploratory).
- H-B3. Within this panel, selection-tool (`variants`) usage rate correlates with kept improvements. Sign check only, n=12 cells; r reported, no causal claim.
- H-B4. `gpt-6-astra` uses no dormant machinery beyond the offered tools (no `try`, by construction) and registers an assay before any `variants` call in at least 3 of 4 cells. Falsified if it variants first in 3 or more cells.

## Falsification and reporting rules

- Negative results are reported beside positive ones with the preregistration attached.
- A cell that fails the assay validation 3 times counts as registered-none; its calls count toward the denominators.
- Cost ledger: total tokens and estimated cost are printed at the end of every cell; the run aborts if the wall-clock cap (60 min) or the token cap (8,000,000 input tokens or 2,500,000 output tokens) is hit. Estimated maximum spend, worst-case frontier pricing, under $60.
- Deviations from E07 (3-run assay/variants validation, no `try`, direct API instead of Exo router transport, synthetic corpus instead of each cell's own workload) are listed in the results section and never hidden.

## What this does not do

- Does not close or test R3 (registered hy4 protocol test), which needs hy4.
- Does not touch the colony archive, E07's raw data, or the audit code.
- Does not claim anything about non-GPT models, or about gpt-6 outside the responses transport.
