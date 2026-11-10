# Held-Out Final Artifact Audit (R1): E07 Archives

This audit implements Recommendation R1 from issue #111 ("Review of the cell-colony experiments: findings, recommendations, and next steps"). It measures the quality of the final code artifacts produced by each cell run in E07 against eight deterministic held-out tasks, comparing final artifact quality with the headline metric (kept improvements per 100 model calls).

## Background and Finding F1

In E07, the primary metric was "kept improvements per 100 calls" recorded by the cell harness. Post-run review showed this metric can decouple from actual code generation and optimization capability:
- A model that follows the harness tool protocol precisely (`variants` tool) records high improvement rates even on marginal code edits.
- A model that optimizes directly via the shell or writes standalone compiled helpers can record zero kept improvements if it bypasses the specific mutation tool expected by the harness.

Run `b7` (`opencode-go:hy4`) exemplifies this divergence: it scored 0.00 kept improvements per 100 calls in the E07 report. This audit tests whether `b7` truly failed or whether the harness metric failed to observe its output.

## Audit Method

The audit evaluates all finished cell directories from E07 (`b5` through `b11`, plus colonies `g3` and `g4`):
- Workloads: Eight deterministic held-out tasks. Four are the reference workloads from `kit.py` (`compress`, `csvsum`, `fibmod`, `maze`). Four are deterministic stdlib reference workloads for the remaining tasks in `needs8v3.json` (`primes`, `sortints`, `wordfreq`, `lcs`).
- Repeat protocol: Five interleaved repeats under the machine-wide benchmark lock (`~/Work/razi-cells/.bench.lock`).
- Isolation: macOS `sandbox-exec` with network denied, home read denied, and execution constrained to cell artifacts and scratch temporary directories.
- Scoring: Per-task relative score `rel = median(contender_score) / median(ref_score)`. For throughput tasks (`fibmod`, `maze`, `primes`, `sortints`, `wordfreq`, `lcs`), score is `1 / wall_time`. For `csvsum`, score is `1 / total_wall_time` across cases. For `compress`, score is raw bytes divided by compressed bytes.
- Reference baseline: Clean stdlib Python reference implementations (`rel = 1.000`).

## Summary: Headline Metric vs Held-Out Artifact Score

| Run | Model | Kept / 100 calls | Held-Out Med Rel | Held-Out Mean Rel | Wins / 8 |
|---|---|---|---|---|---|
| g4 | DeepSeek v4.1 Flash | 1.57 | 3.082 | 5.098 | 7 |
| b11 | anthropic:claude-fable-5-1 | 11.02 | 2.542 | 4.373 | 8 |
| b10 | opencode-go:gemini-4-argon | 12.50 | 2.049 | 4.480 | 8 |
| b8 | opencode-go:gemini-4-argon | 10.34 | 2.007 | 2.425 | 8 |
| b9 | anthropic:claude-fable-5-1 | 7.76 | 1.843 | 4.541 | 7 |
| g3 | DeepSeek v4.1 Flash | 3.12 | 1.818 | 4.608 | 6 |
| b5 | anthropic:claude-fable-5-1 | 12.82 | 1.672 | 4.289 | 7 |
| b7 | opencode-go:hy4 | 0.00 | 1.398 | 4.415 | 7 |
| b6 | openai:gpt-6-astra | 12.88 | 1.254 | 4.205 | 6 |

Wins / 8 counts tasks where the run beat the stdlib reference (`rel > 1.0`).

## Per-Task Relative Scores (1.000 = stdlib reference)

| Task | ref | b5 | b6 | b7 | b8 | b9 | b10 | b11 | g3 | g4 |
|---|---|---|---|---|---|---|---|---|---|---|
| compress | 1.000 | 1.625 | 1.329 | 1.564 | 1.564 | 1.564 | 1.193 | 1.564 | 1.564 | 1.592 |
| csvsum | 1.000 | 0.957 | 0.997 | 0.963 | 1.960 | 2.684 | 2.608 | 1.085 | 0.000 | 2.809 |
| fibmod | 1.000 | 4.533 | 4.162 | 1.016 | 4.972 | 2.881 | 1.659 | 3.519 | 4.006 | 4.768 |
| lcs | 1.000 | 20.920 | 22.125 | 22.088 | 2.725 | 23.440 | 23.099 | 18.407 | 23.604 | 21.776 |
| maze | 1.000 | 2.100 | 1.827 | 3.779 | 3.439 | 2.123 | 2.610 | 3.632 | 3.318 | 3.991 |
| primes | 1.000 | 1.085 | 0.978 | 1.058 | 1.093 | 0.984 | 1.038 | 1.064 | 0.983 | 0.958 |
| sortints | 1.000 | 1.720 | 1.180 | 3.619 | 2.053 | 1.428 | 2.439 | 4.629 | 2.072 | 3.354 |
| wordfreq | 1.000 | 1.374 | 1.041 | 1.233 | 1.591 | 1.224 | 1.190 | 1.081 | 1.318 | 1.536 |

## Detailed Analysis of b7 (`opencode-go:hy4`)

Run `b7` confirms Finding F1. In the original report, `b7` sat at the bottom of the scoreboard with 0 kept improvements. In this held-out audit:
1. `b7` outperforms `b6` (GPT-6 Astra, 12.88 kept/100) on both median relative score (1.398 vs 1.254) and mean relative score (4.415 vs 4.205).
2. On `maze`, `b7` achieved 3.779x speedup, faster than all other single-cell runs (`b5` 2.100x, `b6` 1.827x, `b8` 3.439x, `b9` 2.123x, `b10` 2.610x), beaten only by the 8-cell colony `g4` (3.991x). `b7` compiled a dedicated C helper (`mazehelper.so`).
3. On `sortints`, `b7` achieved 3.619x speedup over standard Timsort using a compiled sorting accelerator (`sortints_helper.so`), trailing only `b11` (4.629x).
4. On `compress`, `b7` built a multi-stage compressor (`squeeze.py`) evaluating twelve algorithms, achieving a 7.52x raw compression ratio across text and JSON, well ahead of `b6` (6.39x) and `b10` (5.74x).
5. On `primes`, `b7` built a compiled C sieve (`sieve.so`) that passed the 10-million integer test in 0.041s.

The headline metric in E07 was blind to these results because `b7` compiled code and mutated files via shell commands rather than logging iterations through the Python mutation harness.

## Key Conclusions for Next Generations (R1)

1. **Held-out final artifact audits are necessary**: Generational experiments cannot rely solely on self-reported loop improvements. Protocol compliance is not artifact quality.
2. **Text-mode (`b11`) and colony mode (`g4`) produced the highest quality final artifacts**:
   - `b11` achieved 8 wins out of 8 tasks, with a median relative score of 2.542x and high individual task scores (`sortints` 4.629x, `maze` 3.632x).
   - `g4` achieved the highest median relative score overall (3.082x) and highest mean relative score (5.098x), showing that multi-cell parallel search produced durable optimizations across tasks.
3. **Reproducibility**: The complete audit harness is preserved in `code/heldout_audit.py` with raw results in `data/heldout-audit-r1.json`. It runs deterministically under the benchmark lock without network dependencies.
