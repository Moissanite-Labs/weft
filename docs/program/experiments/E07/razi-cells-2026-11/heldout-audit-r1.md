# Held-Out Final Artifact Audit (R1): E07 Archives

This audit implements Recommendation R1 from issue #111. It scores the final code directories from E07 runs `b5` through `b11` plus colonies `g3` and `g4` against eight deterministic held-out workloads, then lines those scores up against the headline metric (kept improvements per 100 model calls).

## Background and Finding F1

E07 ranked cells by kept improvements per 100 calls from the harness loop. That number can diverge from what the artifacts actually do: a model that always uses the `variants` tool logs improvements even on weak edits, while a model that rewrites via the shell or drops in compiled helpers can log zero kept improvements when it never touched the mutation path the harness counts.

Run `b7` (`opencode-go:hy4`) is the clean example: 0.00 kept/100 in the E07 scoreboard. The question is whether the run failed or the metric failed to see its output.

## Audit method

- **Workloads:** Eight tasks with fixed generators seeded `heldout-r1-{task}-20261110`. Four match `kit.py` (`compress`, `csvsum`, `fibmod`, `maze`). Four are stdlib references for the remaining `needs8v3.json` tasks (`primes`, `sortints`, `wordfreq`, `lcs`).
- **Repeats:** Five interleaved passes under `~/Work/razi-cells/.bench.lock`.
- **Isolation:** macOS `sandbox-exec` (network denied, `$HOME` read denied, writes limited to scratch). Without `sandbox-exec`, the harness refuses to run archived cell code unless `--no-sandbox` is passed explicitly (offline checks only, not for claiming an archive rescore).
- **Scoring:** `rel = median(contender) / median(reference)`. Throughput tasks use `1 / wall_time`; `csvsum` sums case time; `compress` uses raw/compressed bytes.
- **Wins:** `rel > 1 + ref_spread` (beats reference timing noise), not bare `rel > 1`.
- **Cell folders:** The audited directories live in the E07 archive, not in this repository. Committed `data/heldout-audit-r1.json` lists `cell_folder_sha256` as `not_recorded` for this run; the revised harness hashes each run folder at audit time on the next macOS pass.
- **fibmod:** The committed fibmod column is **invalidated**. The shim on the original macOS run could score fibmod from audit-local `_b7_fib` code when a cell had no callable (that fallback is removed now). Without the archive we cannot say which runs used it. CLI-only cells (E07: `python3 fibmod.py N`) are timed via `cli_runpy`, one process using `runpy` per index. Those scores remain in the JSON for forensics but are excluded from every aggregate below until the archive is rescored with `score_path` recorded per cell.

## Summary: headline metric vs held-out score (seven tasks; fibmod excluded)

Aggregates use seven tasks. Geometric mean is shown where every task rel is positive (`g3` omits it because `csvsum` scored 0).

| Run | Model | Kept / 100 | Med rel | Mean rel | Geom rel | Wins / 7 |
|---|---|---:|---:|---:|---:|---:|
| g4 | DeepSeek v4.1 Flash | 1.57 | 2.809 | 5.145 | 2.944 | 6 |
| b10 | opencode-go:gemini-4-argon | 12.50 | 2.439 | 4.883 | 2.473 | 5 |
| b8 | opencode-go:gemini-4-argon | 10.34 | 1.960 | 2.061 | 1.938 | 6 |
| b5 | anthropic:claude-fable-5-1 | 12.82 | 1.625 | 4.255 | 2.092 | 5 |
| b7 | opencode-go:hy4 | 0.00 | 1.564 | 4.901 | 2.490 | 4 |
| b9 | anthropic:claude-fable-5-1 | 7.76 | 1.564 | 4.778 | 2.318 | 5 |
| b11 | anthropic:claude-fable-5-1 | 11.02 | 1.564 | 4.494 | 2.496 | 4 |
| g3 | DeepSeek v4.1 Flash | 3.12 | 1.564 | 4.694 | — | 5 |
| b6 | openai:gpt-6-astra | 12.88 | 1.180 | 4.211 | 1.813 | 4 |

`b7` sits above `b6` on median rel (1.564 vs 1.180) yet both show 4 wins of 7 under `rel > 1 + ref_spread`. Mean and geometric means are pulled up by `lcs`, where all runs but `b8` score about 18× to 24× reference (`b8` is 2.7×); geometric mean is the fairer single-number summary when `lcs` dominates the arithmetic mean.

## Per-task relative scores (1.000 = stdlib reference)

| Task | ref | b5 | b6 | b7 | b8 | b9 | b10 | b11 | g3 | g4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| compress | 1.000 | 1.625 | 1.329 | 1.564 | 1.564 | 1.564 | 1.193 | 1.564 | 1.564 | 1.592 |
| csvsum | 1.000 | 0.957 | 0.997 | 0.963 | 1.960 | 2.684 | 2.608 | 1.085 | 0.000 | 2.809 |
| fibmod | — | *inv* | *inv* | *inv* | *inv* | *inv* | *inv* | *inv* | *inv* | *inv* |
| lcs | 1.000 | 20.920 | 22.125 | 22.088 | 2.725 | 23.440 | 23.099 | 18.407 | 23.604 | 21.776 |
| maze | 1.000 | 2.100 | 1.827 | 3.779 | 3.439 | 2.123 | 2.610 | 3.632 | 3.318 | 3.991 |
| primes | 1.000 | 1.085 | 0.978 | 1.058 | 1.093 | 0.984 | 1.038 | 1.064 | 0.983 | 0.958 |
| sortints | 1.000 | 1.720 | 1.180 | 3.619 | 2.053 | 1.428 | 2.439 | 4.629 | 2.072 | 3.354 |
| wordfreq | 1.000 | 1.374 | 1.041 | 1.233 | 1.591 | 1.224 | 1.190 | 1.081 | 1.318 | 1.536 |

*fibmod: invalidated pending archive rerun (see above).*

### compress

For compress, `b7`, `b8`, `b11`, and `g3` all land on the same median ratio (7.52403), which matches `bz2.compress(level=9)` plus one byte per case on the held-out generator. `b5` (7.817) and `g4` (7.658) score higher. There is no evidence in the committed data that `b7` built a twelve-algorithm pipeline ahead of `b6` (6.39) on this workload.

### maze

`b7` reaches 3.779× on maze, ahead of `b11` (3.632); the gap is about 4%, inside `b7`'s own repeat spread on maze (0.249) while maze reference spread is 0.0875. Colony `g4` leads at 3.991×. Names like `mazehelper.so` appear in the archive write-ups; this repository does not contain those binaries, so they are cited as seen in the archive, not verified here.

### sortints

`b7` at 3.619× is strong and trails only `b11` (4.629×). A compiled helper (`sortints_helper.so` in the archive) is plausible but not checkable from the repo alone.

### primes

The primes workload is a single `python3 primes.py 10000000` invocation. Reference medians sit near 15–20 executions per second (roughly 0.05–0.06 s wall), with reference spread 0.161. `b7` at rel 1.058 sits inside that noise band; the data do not support a sub-0.05 s claim or a ranking story on primes alone. Interpreter startup dominates much of the timed path.

## b7 and Finding F1 (scoped to validated tasks)

With fibmod withheld and wins counted at `rel > 1 + ref_spread`, `b7` still shows real artifact strength on **maze** and **sortints**, and high **lcs** multiples that inflate arithmetic means. Several tasks (`primes`, `wordfreq`, `compress` tied at bz2-9) sit inside reference noise or shared shallow optima.

We suspect the headline metric likely missed `b7` because shell-side compilation and direct file edits may not have registered as harness improvements, though that link is not established from these timing tables alone.

## Reproducibility

Generators and harness: `code/heldout_audit.py`. Raw rows: `data/heldout-audit-r1.json`. Full reproduction needs macOS `sandbox-exec` and the E07 cell archive (`/tmp/e07-archive-copy` on the original host). Workloads are deterministic; wall-clock timings are not. Among committed rows the largest contender repeat spread is 0.496 on **wordfreq** for `b6`; reference spreads for this audit top out at 0.258 on `wordfreq`. Timing repeats no longer zero out after a single failure (each repeat is scored independently). Labels `fibmod_invalidated`, per-task `invalidated`, and `score_path` values such as `unknown_prior_run` on the committed JSON were added by hand for this R1 artifact; a fresh harness run does not emit them unless you post-process or invalidate fibmod explicitly.
