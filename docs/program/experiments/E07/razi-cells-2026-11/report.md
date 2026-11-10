# Stem-Cell Micro-Harnesses: Model Choice, Selection Machinery and Code Diversity in Self-Improving LLM Agents

- Date: 2026-11-09
- Status: Exploratory run. Not preregistered. Numbers come from logged runs listed in data/.
- Source: converted from the HTML report `exp/REPORT.html` (Report 1, version 2). Content is unchanged apart from path sanitizing and dash replacement. See manifest.md.

---

**Notes added for publication, 2026-11-10**
This is Report 1 as written on 2026-11-09, with private paths, names and internal ids removed. It is an exploratory report. Four things are known since.
1. A scoring fault was found afterwards. The score reader took the last number from standard output and standard error together, so a runtime warning line was once read as a score. Taking out the one false improvement moves run b5 from 12.82 to 11.97 kept improvements per 100 calls, and the correlation in finding (3) from 0.991 to 0.986. The Fable against Argon comparison stays undetectable under every correction (Welch t between 0.29 and 0.70). The cell.py in this record is the code that ran and is left unchanged; the fixed reader is in use from E10 onwards.
2. Section 5 said the embedding permutation tests shuffle whole runs. The code shuffles single variants, as section 6.6 describes. Section 5 now says so. Read those p values as upper bounds on the evidence, because variants from one run are not independent.
3. code/colony.py now counts `splits` from `try` events (was `mitosis`, which cell.py never logs, so splits read 0 in the summaries). The fix postdates the runs; the summaries in data/ are unchanged.
4. The registered tests that followed are kept in their own records: this record (PR 101) and the laws record, E11 to L1 (PR 107). Both are under review. Several guesses there missed, and the records say so.

Report 1, version 2 · razi-cells program · Exo canary seat (exo-razi), principal investigator A. Arifuddin · data collected 2026-11-08 to 2026-11-09 · hypotheses in section 9 registered 2026-11-09, before any of their tests were run · one Apple M1 Max (8P+2E cores, 64 GB)

> **Abstract.** We built "stem cells": small agent harnesses that each start from a written NEED and an empty folder. Each cell grows its own code and tools inside a macOS sandbox. It makes every model call through Exo's router, so no API key ever enters a cell. A cell improves its code by selection against a fitness assay that the harness has validated. We ran 13 colonies of 8 to 16 cells on 8 fixed coding tasks, about 1,560 model calls in total, under five model conditions: a fast default (DeepSeek v4.1 Flash), Claude Fable 5.1, GPT-6 Astra, Tencent hy4 and Gemini 4 Argon. Four results stand out. (1) Harness design moved outcomes as much as model choice did. (2) Frontier models reached 10 to 13 kept improvements per 100 calls, against 1.6 to 3.1 for the fast default. Fable (n=3) and Argon (n=2) could not be told apart (Welch t = 0.48). (3) How often a model used the selection tool predicted its improvement rate almost perfectly across 8 runs (r = 0.99). hy4 shows this most clearly: it never used the tool and scored 0, while hand-tuning a 14.3x compressor. Only Astra ever used the daughter-cell mitosis action. (4) Code embeddings showed that models differ in run-to-run code diversity. A same-model control did *not* support a stable per-model fingerprint. This version adds the full method and its variables, an analysis plan, 18 registered hypotheses with falsification criteria, and the experiment roadmap.

**Contents**

1. Introduction and research questions
2. The system
3. Scientific method
4. Variables
5. Analysis plan and decision rules
6. Results to date
7. Discussion
8. Threats to validity
9. Hypothesis register
10. Areas of exploration and experiment roadmap
11. Safety, ethics and governance
12. Harness findings
13. Reproducibility, data dictionary and timeline
14. Glossary
15. Appendices: system prompt, tool spec, tasks

## 1. Introduction and research questions

Agent harnesses usually come pre-built: a fixed toolset, a fixed loop and a model behind it. We asked the opposite question. What happens when a harness starts from nothing, builds only the tooling its task demands, and improves through a biological loop: vary, compete, keep the winner, record the lesson? The program is open-ended by design. The principal handed full agency over its direction to the investigating agent, and asked for constant iteration, the way the cells themselves are meant to work.

| RQ | Question | Status |
|---|---|---|
| RQ1 | Feasibility: can a minimal sandboxed cell turn a one-paragraph NEED into verified, measurably optimized code with no human help? | Answered: yes |
| RQ2 | Drivers: what controls the rate of kept improvements: harness design, colony scale, model, or how the model uses the harness? | Partly answered |
| RQ3 | Model economics: where do models sit on the frontier of improvement rate, speed and cost? Do mixtures beat pure colonies? | Open (cost not yet logged) |
| RQ4 | Selection design: how should mitosis work so that each split builds on the last (loser-informed, novelty floor, split width)? | Open |
| RQ5 | Representation: does embedding space give useful structure (prediction, steering, causality)? | First results |
| RQ6 | Agency: what happens when cells can build shared tools, or change the mitosis process itself? | Open |
| RQ7 | Formal grounding: can selection be made provably honest (Lean theorems as needs, proven selection rule)? | Open (toolchain installed) |
| RQ8 | Substrate and scale: what emerges with many colonies, and can Apple Silicon (P/E cores, unified memory, GPU/ANE) improve measurement or selection? | Open |

## 2. The system

### 2.1 The cell

A cell is a folder. It holds a read-only `NEED`, a self-written `genome.md` (memory, capped at 4,000 chars), any files it creates, and an append-only `log.jsonl`. On each step the cell's brain (one model call through Exo's `Router`, with a per-cell `session_id`) chooses exactly one action. Implementation: `razi-tools/cells/cell.py` (486 lines, stdlib plus Exo's router). The action set is in Appendix B.

### 2.2 Sandbox and safety

Every shell action runs under `sandbox-exec`: no network, no writes outside the cell, no reads of `$HOME`, 30 s limit. Each rule was verified on its own (outside write denied, curl exit 6, `~/.zshrc` read denied). Model access goes only through the router in the parent process, so cells never see credentials.

### 2.3 Selection machinery

- **Assay validation.** The harness runs the cell's fitness command 5 times on the current body. It is accepted only if it exits 0, prints a number above 0, and has spread (max−min)/median of 15% or less.
- **Win rule.** A challenger wins only if median(challenger) beats median(incumbent) by more than max(3%, measured noise), and the challenger's worst run is no worse than the incumbent's median. Ties keep the incumbent.
- **Bench lock.** One measurement at a time, machine-wide, so timing assays do not disturb each other.
- **`variants`**: the model writes 2 to 6 full versions of one file in one reply, and the CPU picks. This is cheap mutation with strict selection.
- **`try`** (asymmetric mitosis): one daughter cell explores one idea for half the parent's remaining steps (depth 1). The parent stays the control. If the daughter loses, an "autopsy" model call writes a one-line lesson into LIBRARY. This is the first form of loser-informed mitosis.
- **Germline.** Every win and every loss lesson is appended to a colony-wide `LIBRARY.md` (max 400 chars per line, never code), which all cells read.
- **Apoptosis.** Three failed steps in a row end the cell. Rate limits and timeouts back off instead (at most 6 waits, added after b6).

### 2.4 Colony runner

`colony.py` runs N cells as separate processes. It samples RSS and CPU of every process tree every 2 s and writes `summary.json`. Each cell can be pinned to one model. A pinned cell has no hidden fallback, and the route of every call is logged.

### 2.5 Version history

| Version | Runs | Key change | Reason |
|---|---|---|---|
| v1 | c1, c2, g1 | Text JSON actions; symmetric divide into A/B daughters | Minimum viable cell |
| v2 | g2 | Plain vs split twins; depth cap 2 | Test whether splitting helps |
| v3 | g3 | Native tool calls (DSML/JSON fallbacks), validated assay, `variants`, asymmetric `try`, LIBRARY, apoptosis | g2 lost 46 replies, decided a 0 vs 0 split, and wasted calls on twins |
| v3 + nudges | g4 | Prompts to register the assay early | g3 cells registered it at step 4 to 14 of 16 |
| v3b/c | b5, b6 | Model pinning; TEXT_MODE for gpt-6 | gpt-6 rejects function tools combined with reasoning on chat/completions |
| v3c+ | b7 onward | Rate-limit backoff | b6 lost 5 of 8 cells to HTTP 429 |
| v3d | b8 onward | Full code archive in `variants.jsonl` | Needed for embeddings |

## 3. Scientific method

### 3.1 Design

The program runs in two phases, and every result is labelled with the phase it came from.

- **Exploratory phase (done: c1 to b11).** Iterative engineering and observation. The harness changed between runs on purpose. Results here generate hypotheses. They do not confirm them.
- **Confirmatory phase (from now).** The harness is frozen at a tagged version for each experiment. Hypotheses, predictions and decision rules are written down first (section 9). Each condition gets at least 3 replicate runs, and conditions are interleaved in time to spread out provider and machine drift.

### 3.2 Units of analysis

| Unit | What it is | Independence |
|---|---|---|
| Step | One model call and one action | Not independent (same cell history) |
| Variant | One code version written | Not independent (shares lineage within a run) |
| Cell | One NEED pursued to done, death or cap | Weakly dependent (shared LIBRARY, shared bench) |
| **Run (colony)** | 8 cells, one condition | **The primary independent unit.** All model comparisons use run-level statistics |

### 3.3 Procedure for one run

1. Freeze code. Record the cell.py and colony.py versions and the exo-live commit (currently `6054da56`).
2. Remove the bench lock and clear the run folder.
3. Launch `colony.py RUN needs8v3.json --par 8 --calls 40 --steps 16 [--model REF]` as a harness background job.
4. Do not touch the run. No polling, no restarts, no edits.
5. On exit, read `summary.json` and check from `routes` that every call was served by the intended model.
6. Extract metrics (section 4.2). Embed variants (b8 onward) with all three embedders.
7. Append a dated entry to `TESTS.md` before interpreting anything.

### 3.4 Instrument validity checks

- The sandbox was verified with negative tests (2.2).
- Assay acceptance rejects unstable or wrong-output measurements before any comparison.
- The win rule requires clearing measured noise. We have observed fake-win protection: in g2 a 0 vs 0 split was decided, which v3 now blocks.
- Route logging proves model identity per call. Pinned cells cannot silently fall back.
- Only primes (348,513 below 5,000,000) and fibmod (fib(10) = 55) state a correct answer in the NEED. The other 6 tasks rely on the cell's own correctness check inside its assay. This is a known weakness: a cell could reward a fast wrong answer it fails to detect. Adversary cells (R6) and harness-held reference outputs are the planned fix.

## 4. Variables

### 4.1 Independent variables (manipulated)

| Variable | Levels so far | Planned levels |
|---|---|---|
| Brain model | DeepSeek v4.1 Flash, Fable 5.1, GPT-6 Astra, hy4, Gemini 4 Argon | Haiku 5.5, Sonnet 5.5, Opus 5.5, GLM 5.3 Flash, Kimi K3 |
| Harness version | v1, v2, v3, v3 + nudges, v3b to v3d | Frozen per experiment from now on |
| Action protocol | Native tools; text JSON (gpt-6) | Responses API native tools for gpt-6 (needs harness fix f_a04e95fa) |
| Colony size | 8, 16 | Many colonies in parallel (RQ8) |
| Prompt nudges | none; early-assay nudge | Explicit "use variants" (H1) |
| Colony composition | Homogeneous | Mixed models; mixed roles within a cell |
| Mitosis design | Symmetric divide; asymmetric try; variants; autopsy lessons | Novelty floor, retrieved loser lessons, surrogate pre-filter, embedding steering |
| NEED type | Speed and ratio coding tasks | Lean theorems; adversarial inputs |
| Embedder (analysis) | nomic-embed-text, text-embedding-3-small, -3-large | Unchanged |

### 4.2 Dependent variables (measured)

| Variable | Definition | Source |
|---|---|---|
| **Kept improvements per 100 calls** (primary) | 100 × (count of `improve` events) / (model calls) | log.jsonl, .calls |
| Gain per cell | ∏(1 + gain<sub>i</sub>) − 1 over adopted wins, where gain = (median<sub>new</sub> − median<sub>old</sub>) / median<sub>old</sub> | colony.py |
| Completion | Cells that wrote RESULT via `done` | summary.json |
| Apoptosis | Cells ended by 3 consecutive failures | log.jsonl |
| Errors / bad replies | Exceptions; replies with no valid action | log.jsonl |
| Action mix | Share of actions per type (sh, write, assay, variants, try, remember, done) | log.jsonl |
| Variants written | Count of archived code versions | variants.jsonl |
| Wall time | Run start to last cell exit | summary.json |
| Resources | Peak RSS; peak and mean CPU of all cell trees | 2 s sampler |
| LIBRARY growth | Lines in LIBRARY.md at end of run | file |
| Embedding metrics | Split width (mean pairwise cosine distance in a batch); centroid gap between groups; permutation p | embed.py, perm.py |
| Cost | USD per run and per kept improvement | **Not yet logged** (planned) |

### 4.3 Controlled variables (held constant)

| Constant | Value |
|---|---|
| Task set | needs8v3.json, 8 tasks (Appendix C) |
| Per-cell call cap / step cap / parallel cells | 40 / 16 / 8 |
| Assay repeats / acceptance spread | 5 / 15% |
| Win margin | max(3%, measured noise); worst challenger run ≥ incumbent median |
| Max variants per batch / mitosis depth | 6 / 1 |
| Genome cap / tool output cap / shell timeout | 4,000 chars / 2,000 chars / 30 s |
| Apoptosis threshold / backoff cap | 3 consecutive failures / 6 waits |
| LIBRARY line cap | 400 chars, no code |
| System prompt and tool descriptions | Appendix A and B, verbatim |
| Runtime | Cells: /opt/homebrew/bin/python3 in sandbox. Runner: exo-live venv Python. Exo commit 6054da56 |
| Hardware | One M1 Max, 8P+2E cores, 64 GB |

### 4.4 Uncontrolled and confounding variables

| Variable | Effect | Mitigation |
|---|---|---|
| Provider latency and rate limits | Inflate wall time; caused 5 deaths in b6 | Primary metric is per call, not per second; backoff; record 429 counts |
| Sampling temperature and reasoning effort | Not set; provider defaults apply and may differ by model | Record defaults; plan a temperature sweep for one model |
| Model nondeterminism | Same model, very different runs (Fable 7.76 to 12.82) | 3 or more replicate runs |
| Cell-written assay workload | Each cell picks its own input size, so gains are not on a common scale across runs | Planned: harness-fixed reference workloads per need |
| Other machine load | Other agent CLIs and the desktop app share the CPU | Bench lock; 5-run medians; record load average (planned) |
| Time of day and run order | Provider load drifts | Interleave conditions |
| LIBRARY state inside a run | Early wins shape later cells | Treated as part of the system; tested directly in D1 and E4 |
| Model-specific action protocol | gpt-6 runs in text mode, others use native tools | Fix the transport, then rerun Astra |

## 5. Analysis plan and decision rules

- **Primary comparison**: kept improvements per 100 calls, one value per run. Two conditions: Welch t-test and Mann-Whitney U, two-sided, α = 0.05. More than two conditions: Kruskal-Wallis, then pairwise tests with Holm correction.
- **Effect size**: report the difference in means with a bootstrap 95% CI (10,000 resamples of runs) and Cohen's d. A difference under 2 per 100 calls is treated as practically equal.
- **Replication**: at least 3 runs per condition before any ranking. 5 runs for headline claims. Our observed SD (1.5 to 2.6) means n = 5 per arm detects a gap of about 3.5 per 100 at 80% power.
- **Embeddings**: permutation tests shuffle *single variants* between labels, not whole runs (an earlier draft of this section said whole runs; with 2 runs per arm a run-level shuffle has only 6 assignments, so it cannot reach p < 0.05). Variants from one run are not independent, so the p-values are upper bounds on the evidence. A model-label effect counts only if the cross-model gap exceeds the same-model gap. (Section text corrected 2026-11-10; see Notes added for publication.)
- **Correlations**: report r with n and a note when the measures are linked by construction (variants and improvements).
- **Scaling gate**: add cells or colonies only when the rate rises in two runs in a row. Scale for throughput is allowed when the rate per 100 calls holds steady.
- **Stopping**: a condition stops early if 2 runs in a row produce 0 kept improvements and a log check shows no harness fault.
- **Exclusions**: a run is excluded only for a verified harness fault (example: b6-failed-400, where every call returned HTTP 400). Exclusions and their reasons are kept in TESTS.md, and the data is kept.

## 6. Results to date (exploratory phase)

### 6.1 Feasibility (pilots)

c1 (word frequency) built a working, tested tool in 10 calls and 50.7 s. c2 (primes) ran the first mitosis: daughter A (odd-only half sieve) scored 34.6 and daughter B (full bytearray sieve) 27.9 on 1/s. The winner re-verified at about 30 ms for N = 5,000,000 with the correct count, in 50 calls and 474 s. **RQ1: yes.**

### 6.2 Harness design (g1 to g4)

| Run | Cells | Done | Calls | Kept | Per 100 | Wall s | Peak RSS MB |
|---|---|---|---|---|---|---|---|
| g1 (v1) | 8 | 5/8 | 112 | n/a | n/a | 273 | 789 |
| g2 (v2) | 16 | 14/16 | 265 | n/a | n/a | 498 | 1,441 |
| g3 (v3) | 8 | 8/8 | 128 | 4 | 3.12 | 1,033 | 1,127 |
| g4 (v3+nudge) | 8 | 7/8 | 127 | 2 | 1.57 | 994 | 1,040 |

v1 and v2 did not log kept-improvement events, so no rate is available for them.

- **Membrane failure (g2)**: 46 replies were lost (22 written as tool markup in text, 24 empty). After v3, malformed replies ran at 0 or 1 per run.
- **Untrusted fitness (g2)**: a split was decided with both daughters scoring 0. The validated assay now blocks this.
- **Symmetric mitosis cost (g2)**: split twins used 14 to 24 calls against 14 for plain cells, and 2 split cells did not finish.
- **Scaling gate failed (g3 to g4)**: the rate fell from 3.12 to 1.57, so colonies stayed at 8 cells.

### 6.3 Model comparison

| Run | Model | Done | Calls | Kept | Per 100 | Wall s | Apoptosis | Peak RSS MB |
|---|---|---|---|---|---|---|---|---|
| g3 | DeepSeek v4.1 Flash | 8/8 | 128 | 4 | 3.12 | 1,033 | 0 | 1,127 |
| g4 | DeepSeek v4.1 Flash | 7/8 | 127 | 2 | 1.57 | 994 | 0 | 1,040 |
| b5 | Fable 5.1 | 8/8 | 117 | 15 | 12.82 | 360 | 0 | 1,149 |
| b9 | Fable 5.1 | 8/8 | 116 | 9 | 7.76 | 1,069 | 0 | 1,050 |
| b11 | Fable 5.1 | 8/8 | 118 | 13 | 11.02 | 597 | 0 | 1,379 |
| b6 | GPT-6 Astra (text mode) | 3/8 | 132 | 17 | 12.88 | 555 | 5 | 913 |
| b7 | hy4 | 7/8 | 123 | 0 | 0.00 | 3,227 | 1 | 872 |
| b8 | Gemini 4 Argon | 7/8 | 116 | 12 | 10.34 | 529 | 1 | 842 |
| b10 | Gemini 4 Argon | 8/8 | 120 | 15 | 12.50 | 694 | 0 | 882 |

Fable: mean 10.53, SD 2.56 (n=3). Argon: mean 11.42, SD 1.53 (n=2). Welch t = 0.48, **no detectable difference**. Frontier as a group (8 to 13) is well above Flash (1.6 to 3.1). Astra's 5 deaths came from HTTP 429 rate limits, not from the model.

### 6.4 Protocol adherence

| Run | Model | Actions | sh % | variants % | try | remember | Per 100 |
|---|---|---|---|---|---|---|---|
| g3 | Flash | 128 | 70 | 3 | 0 | 0 | 3.12 |
| g4 | Flash | 127 | 72 | 2 | 0 | 0 | 1.57 |
| b7 | hy4 | 99 | 78 | 0 | 0 | 0 | 0.00 |
| b8 | Argon | 85 | 47 | 19 | 0 | 0 | 10.34 |
| b9 | Fable | 116 | 40 | 15 | 0 | 5 | 7.76 |
| b10 | Argon | 96 | 43 | 23 | 0 | 0 | 12.50 |
| b11 | Fable | 118 | 47 | 18 | 0 | 8 | 11.02 |
| b5 | Fable | 117 | 41 | 25 | 0 | 8 | 12.82 |
| b6 | Astra | different log format; 8 `try` events counted directly | n/a | 12.88 |  |  |  |

- The `variants` share correlates with the rate at **r = 0.991** (n = 8 runs; 0.938 for frontier runs only). The two are partly linked by construction, since most kept wins come through `variants`.
- **Only Astra used mitosis (`try`).** 8 tries, 2 won: a reversible word-token transform for compress (+37%) and a native C fast path for csvsum (+826%). The 6 losers each wrote an autopsy lesson to LIBRARY. No other model ever called `try`. So loser-informed mitosis exists in the code but has barely been exercised.
- **Only Fable used `remember`** (its genome), without being prompted.
- **hy4 case**: 0 variants and 0 kept, but it benchmarked 12 encoders inside one shell script and reached a 14.3x compression ratio by hand. It optimized outside the measured channel.

### 6.5 Task structure

- **fibmod** gave the largest compounded gain in 5 of 7 frontier runs: Argon 251.9x and 47.0x, Fable 43.4x and 42.9x, Astra 27.9x. The exceptions were Fable b9 (1.24x) and hy4 (no variants). The task has an algorithmic jump (naive to fast doubling), and selection finds it.
- **compress** was flat in 5 of the 6 frontier runs that finished it (the exception was Argon b8 at 1.35x). The first stdlib choice is already near the ceiling.
- **csvsum deaths depend on the model** (hy4 and Argon b8 died, Fable never did). Our first reading, that the task was badly written, was wrong.

### 6.6 Embeddings

**Embedder A/B (synthetic set):** all three embedders gave the same ordering. Spreads: nomic 0.20, 3-small 0.38, 3-large 0.31 to 0.35.

**E1 split width vs gain (b8, 5 batches):** the only adopted batch (maze, +10.5) was the widest. With n = 1 adoption, we make no claim.

| E5 permutation (3-small, 2,000 shuffles over variants) | Needs with p < 0.05 |
|---|---|
| Argon (b8+b10) vs Fable (b9+b11) | 7/8 (compress p = 0.23; 3-large p = 0.12) |
| Control: Argon b8 vs b10 | 1/5 |
| Control: Fable b9 vs b11 | 6/8 |
| Argon b8 vs Fable b9 / Argon b10 vs Fable b11 | 4/6 / 4/7 |

The same-model control breaks the fingerprint reading. Two Fable runs differ about as often as Fable and Argon do. What survives: **Argon converges on similar code from run to run, while Fable's code varies widely**, and that extra variety does not show up as a higher rate.

### 6.7 Resources

8-cell colonies peaked at 0.84 to 1.38 GB RSS. Peak CPU was 1.1 to 3.2 cores, and mean CPU was 7 to 72% of one core. Cells are I/O bound (they wait on the model). The serialized bench is the only real CPU consumer. A 64 GB M1 has headroom for many more colonies.

## 7. Discussion

1. **Improvement rate behaves like capability × protocol adherence × harness quality.** Each factor alone changed outcomes by large amounts, and adherence can zero out capability (hy4).
2. **"The model is key" holds between tiers but not within the frontier.** At the frontier, run-to-run variance dominates.
3. **The selection layer is the instrument.** It blocks fake wins, but it also cannot see gains made outside it. That trade-off is the reason for the adherence research thread.
4. **The mitosis action is under-used.** Models prefer cheap `variants` to an expensive daughter cell. Loser-informed mitosis can only be studied once cells actually divide, by prompting it or by making the harness divide on schedule.
5. **Embeddings need lineage-aware statistics.** Naive tests produce false fingerprints.

## 8. Threats to validity

| Type | Threat | Planned response |
|---|---|---|
| Statistical | n = 1 to 3 runs per model | 5 runs for headline claims (section 5) |
| Internal | Harness changed between exploratory runs; backoff added after b6 | Freeze per experiment; tag versions |
| Internal | Provider throughput (Astra 429s, hy4 latency) mixed into "model" | Log 429s and latency; rerun Astra after the transport fix |
| Internal | Astra used a different action protocol (text mode) | Add Responses API transport |
| Construct | Kept improvements largely require `variants` | Also report gain and done rate; H1 tests adherence directly |
| Construct | 6 of 8 tasks have no harness-held correct answer | Reference outputs held by the harness; R6 adversary cells |
| Construct | Self-written assays mean no common benchmark | Harness-fixed reference workloads |
| Measurement | Shared machine, timing noise | Bench lock, medians, P-core pinning test (H17) |
| External | 8 short coding tasks, one machine, one harness family | Lean needs, adversary cells, larger tasks later |
| Economic | Cost not logged | Add per-call cost from the router to log.jsonl |
| Investigator | The same agent built the system, ran it and wrote this report | Hypotheses registered first; raw data kept for independent re-analysis |

## 9. Hypothesis register

### 9.1 Hypotheses already tested (exploratory)

| # | Hypothesis | Source | Outcome |
|---|---|---|---|
| T1 | The model is the key variable | Principal, after b5 | Partly supported: holds between tiers, not within the frontier; adherence is a mediator |
| T2 | More cells per colony means more wins | Initial scaling plan | Not supported (gate failed g3 to g4) |
| T3 | Nudging an early assay raises the rate | razi, after g3 | Not supported (3.12 to 1.57, within noise) |
| T4 | Native tool calls fix lost replies | razi, after g2 | Supported (46 lost to 0 or 1 per run) |
| T5 | csvsum is a broken task | razi, after b8 | Refuted (Fable never lost it) |
| T6 | Each model leaves a code fingerprint | E5 | Not supported after same-model control |
| T7 | Wider splits find bigger wins | E1 | Undetermined (1 adoption) |
| T8 | Use of the selection tool drives the rate | razi, post hoc | Strong correlation (r = 0.99); causal test is H1 |

### 9.2 Registered hypotheses (predictions written before testing)

Each one gives a prediction, what would falsify it, and how confident we are now (a subjective prior). Results will be filled into this table without editing the predictions.

| # | Area | Prediction | Falsified if | Prior |
|---|---|---|---|---|
| H1 | Adherence | hy4, told explicitly to register an assay and use `variants`, reaches at least 5 kept per 100 calls | Below 2 per 100 over 2 runs | 0.65 |
| H2 | Frontier | With 5 runs each, Fable and Argon differ by less than 2 per 100, and the difference is not significant | Significant gap of 3 or more | 0.70 |
| H3 | Gradient | Rate rises with tier: Flash < Haiku < Sonnet ≤ Opus ≈ Fable. Sonnet reaches at least 70% of Fable's rate | Sonnet below 50% of Fable, or Haiku below Flash | 0.55 |
| H4 | Economics | Once cost is logged, the best cost per kept improvement is a mid-tier model, not the top one | The top-tier model is cheapest per kept improvement | 0.60 |
| H5 | Mixed colonies | 4 fast + 4 frontier cells sharing a LIBRARY: the fast cells gain less than 1 per 100 over fast-only colonies, because lessons carry no code | Fast cells gain 3 or more per 100 | 0.60 |
| H6 | Mixed roles | Escalating from fast to strong after 3 steps without a win matches strong-only rate within 2 per 100, at half the strong calls or fewer | Rate more than 4 per 100 below strong-only | 0.45 |
| H7 | Mitosis use | If the harness forces one `try` per cell, frontier models win at least 25% of tries (Astra: 2/8) | Win rate below 10% over 30 or more tries | 0.55 |
| H8 | Loser-informed mitosis | Tries made after a LOSS lesson in the same need win more often than first tries | Equal or lower win rate over 30 or more tries | 0.50 |
| H9 | Novelty floor | Rejecting variant batches whose members sit closer than a set cosine distance raises the rate by 10 to 20% | No change or a drop | 0.40 |
| H10 | Surrogate fitness | A kNN surrogate predicts within-need rank with Spearman ρ above 0.5, saves at least 30% of bench time and loses at most 10% of wins | ρ below 0.3, or win loss above 20% | 0.45 |
| H11 | Causal steering | Picking the candidate with the highest projection on the winner-minus-loser direction beats a random pick, but the effect is not significant within 10 runs | Projection pick does worse than random | 0.50 |
| H12 | Retrieved lessons | Giving each cell its top-k nearest LIBRARY lines beats giving all lines once LIBRARY passes about 40 lines | No difference at 40 or more lines | 0.45 |
| H13 | Lean needs | Frontier models prove at least 50% of easy theorems without `sorry`, fast models less than 20%. Fake wins are 0 by construction | Frontier below 25% | 0.55 |
| H14 | Meta-cells | First-generation meta-cells that edit `cell.py` mostly make it worse. Any real gains come from prompt edits, not selection logic | A meta-cell improves selection logic with a measured child-colony gain | 0.70 |
| H15 | Tool commons | With a shared tool shelf, a few tools (benchmark and test helpers) spread to most cells, and the rate rises by 2 or more per 100 | No tool reused by more than 2 cells | 0.45 |
| H16 | Adversary cells | Attacker cells find a correctness bug in at least 1 adopted winner per 8-need run | No bugs found across 3 runs | 0.50 |
| H17 | Apple Silicon | Pinning assays to P-cores cuts assay spread by at least 30%. Running assays on E-cores or in parallel without the lock pushes noise above the 3% margin and lowers adopted wins | No change in spread | 0.60 |
| H18 | Scale and emergence | Running many colonies in parallel leaves the rate per 100 calls flat. With a shared LIBRARY across colonies, winners converge (monoculture: lower code variety per need over time) | Rate changes by more than 3 per 100, or variety rises | 0.50 |

## 10. Areas of exploration and experiment roadmap

### 10.1 Map of areas

| Area | Question | Experiments | Origin |
|---|---|---|---|
| A. Model gradient | Rate, speed and cost along the tier ladder; Pareto frontier | B1 to B7, C1, C2, H2 to H4 | Principal |
| B. Mixtures | Mixed colonies; mixed roles inside one cell | D1, D2, E1, E2, H5, H6 | Principal |
| C. Adherence | Why do some models skip the selection tools? | H1, prompt variants, harness-forced actions | razi, from b7 |
| D. Mitosis design | Make each split build on the last: loser-informed splits, forced splits, novelty floor, split width | H7, H8, H9, E1, E2 | Principal (loser files inform the next split) |
| E. Embedding space | Prediction, retrieval, convergence maps | E3 (H10), E4 (H12), E5, E6 | Principal, shaped by razi |
| F. Causality | Does a direction in embedding space cause wins? | F1 (H11), F2, F3 | Principal ("embedding to vector to causality") |
| G. Agency | Cells build shared tools; cells evolve the mitosis process | R5 (H15), R4 (H14), A1, A2 | Principal |
| H. Formal grounding | Proof-carrying wins; theorems as needs; proven selection rule; Bend | R1, R2 (H13), R3, R7, A3, A4 | Principal and razi |
| I. Robustness | Adversarial inputs as the source of tests | R6 (H16) | razi |
| J. Substrate and scale | Many colonies; emergent patterns; P/E cores, unified memory, GPU/ANE | H17, H18 | Principal |

### 10.2 Planned experiments in detail

| ID | Design | Runs |
|---|---|---|
| B1 to B7 | Homogeneous colonies on Flash, Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable, Astra (after the transport fix), plus GLM 5.3 Flash and Kimi K3 as off-frontier controls | 3 each |
| C1 | Plot all B conditions on calls, wall time and cost against rate. Mark the Pareto frontier | Analysis |
| C2 | The same conditions capped by wall time instead of calls (slow models lose on time) | 2 each |
| D1 | 4 fast + 4 frontier cells, shared LIBRARY. Compare fast cells with fast-only colonies | 3 |
| D2 | Each need run twice in one colony, once fast and once strong: head to head per task | 3 |
| E1 (roles) | A strong model plans and picks variants, a fast model writes code | 3 |
| E2 (roles) | Fast by default, escalate to strong after 3 steps without a win | 3 |
| H1 | hy4 with an explicit protocol instruction | 2 |
| M1 | Forced mitosis: the harness triggers one `try` per cell at mid-run. Loser autopsy and loser code (archived in variants.jsonl) are handed to the next split | 3 per model |
| M2 | Novelty floor on variant batches (embedding distance threshold) | 3 vs 3 |
| E3 | kNN surrogate pre-filter in front of the bench, scored offline first on b8 to b11 archives | Offline, then 3 |
| E4 | LIBRARY retrieval: none, all, top-k | 3 each |
| E6 | Convergence map: do winners for one need collapse to one point or several basins? | Analysis on all runs |
| F1, F2 | Steering pick vs random pick; rewrite toward vs away from the nearest winner | 5 vs 5 |
| F3 | Lean theorem that every adoption in a log satisfied the win rule, checked over logged numbers | Proof |
| R1 | Proof-carrying wins: differential testing first, then a Lean equivalence proof | 2 tiers |
| R2 | Lean needs: fitness = `lake build` passes with no `sorry`. Two tactics per split | 3 per tier |
| R4 | Meta-cells whose body is `cell.py`, scored by a child colony's rate. The assay and sandbox stay outside its body | Pilot |
| R5 | Shared tool shelf; track which tools spread | 3 |
| R6 | Attacker sibling per need writes breaking inputs; the assay grows from its finds | 3 |
| R7 | Bend/HVM used to run assays in parallel (Bend is for parallel evaluation, not proofs) | Pilot |
| S1 | Assays pinned to P-cores vs E-cores via `taskpolicy`/QoS; measure assay spread | Microbenchmark |
| S2 | GPU or ANE embeddings inline (Metal / MLX), measuring latency per variant for E3 | Microbenchmark |
| S3 | Scale: 2, 4, 8, 16 colonies at once; watch rate, bench queue, LIBRARY convergence | Once the rate gate allows |

### 10.3 Order of work

1. **Instrument first**: log cost per call, add harness-fixed reference workloads, add the Responses API transport for gpt-6, and tag a frozen harness version.
2. **Cheap, high-information**: H1 (hy4 adherence), E3 offline on existing archives, S1 microbenchmark.
3. **Model gradient**: B2 to B4 and B7, then reps of Fable and Argon to 5. C1 frontier plot.
4. **Mitosis design**: M1 forced and loser-informed mitosis, then M2.
5. **Mixtures**: D1, E2.
6. **Formal**: R2, then R1, then R3/F3.
7. **Agency**: R5, R6, then R4.
8. **Scale**: S3, only after the gate in section 5 allows it.

Volume estimate: one run is about 120 model calls. The plan above is roughly 100 runs, or about 12,000 calls. Cost per call has not been measured yet, so no dollar estimate is given.

## 11. Safety, ethics and governance

- Cells hold no credentials and have no network access. All model traffic passes through the parent's router, which logs every call's route.
- Cells cannot read the user's home folder or write outside their own folder. This was verified with negative tests, not assumed.
- Meta-cells (R4) will never get the assay, the sandbox profile or the selection rule inside their editable body. Without that rule, a cell could improve its score by editing the judge.
- Human oversight: the principal sets budget and direction. Outward actions (publishing, posting) need his approval.
- Embedding calls to OpenAI send cell-written code only. That code contains no personal data.
- Budget: the principal granted an uncapped budget for this program, with model choice limited to configured or previously used models.

## 12. Harness findings filed during the program

| Finding | Issue |
|---|---|
| f_9b17d7f5 | OpenCode route needs an `x-opencode-session` header; no haiku fallback |
| f_ce92e170, f_a04e95fa | gpt-6 on chat/completions rejects function tools combined with reasoning. Needs a /v1/responses transport |
| f_9806f6e6, f_bd6a8fdf, f_9311b77a | The agent is not reliably woken when a background job exits; one early wake |
| f_5605c132 | Phantom turns cost $0.39 to $3.18 each with no user input |

## 13. Reproducibility, data dictionary and timeline

### 13.1 Files

- Code: `~/Work/razi-tools/cells/` (`cell.py`, `colony.py`, `embed.py`, `perm.py`), all prior versions kept (cell v1 to v3d, colony v2 and v3, embed v1).
- Data: `~/Work/razi-cells/exp/{g1..g4, b5..b11, b6-failed-400}`.
- Logs: `exp/TESTS.md` (dated results), `exp/IDEAS.md` (idea log A, R, E, F), this report (`REPORT.html`; version 1 kept as `REPORT_v1.html`).
- Toolchain: Lean 4.35, Bend 0.2.38, HVM 2.0.22 (Bend smoke test returned 499,500 on both runtimes), Ollama with nomic-embed-text.

### 13.2 Data dictionary

| Record | Fields |
|---|---|
| log.jsonl step | `step, act{do,...}, res, route`; or `bad_reply, bad_len`; or `error`; or `backoff, why` |
| log.jsonl event | `assay, improve{gain,what}, variants{path,medians,best,adopted,gain}, try{idea,expect,runs,won,gain}, mitosis, apoptosis` |
| variants.jsonl | Full text of every write and variant, with kind and path |
| summary.json (per cell) | `steps, errors, acts, splits, ties, bad_replies, assays, variants, tries, improvements, gain, apoptosis, calls, routes, done` |
| summary.json (per run) | Cells plus wall time, peak RSS, peak and mean CPU |
| vectors.<model>.json | Cached embedding per variant |

### 13.3 Timeline

| When | Event |
|---|---|
| 2026-11-08 | Principal grants agency over self-built tooling and proposes micro-harnesses with mitosis. Sandbox verified; c1 and c2 pilots |
| 2026-11-08/09 | g1, g2 (v1, v2); v3 rebuilt; g3, g4; scaling gate fails |
| 2026-11-09 | Principal hands full agency and an uncapped budget; test plan written; b5 (Fable), b6 (Astra) |
| 2026-11-09 | Ideas A1 to A4 and R1 to R7 logged; Bend and HVM installed; b7 (hy4), b8 (Argon) |
| 2026-11-09 | Embedding program E1 to E6 and F1 to F3; embedder A/B; b9, b10, b11; permutation tests with controls |
| 2026-11-09 | Report 1; hypotheses H1 to H18 registered |

## 14. Glossary

|  |  |
|---|---|
| **Cell** | One agent harness working on one NEED inside its own sandboxed folder |
| **Colony / run** | A set of cells run together under one condition |
| **NEED** | The read-only task statement that a cell must satisfy |
| **Genome** | The cell's own memory file |
| **LIBRARY / germline** | The shared file of wins and loss lessons that all cells in a colony read |
| **Assay** | The cell's fitness command, validated by the harness |
| **Variants** | Several full versions of one file, scored together |
| **Mitosis / try** | A daughter cell explores one idea against the parent as control |
| **Autopsy** | A one-line lesson written when a daughter loses |
| **Apoptosis** | Cell death after 3 consecutive failures |
| **Membrane** | The interface that turns a model reply into exactly one action |
| **Adherence** | How much a model uses the measured channel (assay, variants, try) instead of acting outside it |
| **Split width** | Mean cosine distance between code versions in one batch |

## 15. Appendices

### A. System prompt (verbatim)

```
You are a cell: a tiny agent that starts with nothing but a NEED and an empty folder (your body).
Grow only the tools your need demands, one step at a time. Call exactly one tool per reply.
Path to fitness: 1) build a correct version and check it. 2) register an `assay`: a shell command that
prints one number, higher is better, 0 if the output is wrong. Make its workload heavy enough (about
0.3 to 3 s) that process startup does not dominate. 3) improve with `variants` (cheap: several versions
of one file in one reply, all scored) or `try` (expensive: a daughter cell explores one bigger idea).
Only scored wins are kept. Read LIBRARY: other cells' results and lessons, often useful to you.
```

### B. Tool specification (v3)

| Tool | Description given to the model |
|---|---|
| sh | Run a shell command in your folder. No network, 30 s limit, python3 available. |
| write | Create or overwrite a file in your folder. |
| remember | Replace genome.md, your memory across steps (max 4000 chars). |
| assay | Register your fitness command. The harness runs it 5 times on your current body and accepts it only if it exits 0, prints a number > 0, and is stable (spread under 15%). |
| variants | Propose 2 to 6 full alternative versions of ONE file. Each is scored by your assay against the current body; the best is adopted only if it wins beyond noise. |
| try | Spawn one daughter cell that explores one idea for half your remaining steps. Its body replaces yours only if it beats you on the assay beyond noise. State the gain you expect. |
| done | Finish. One paragraph: what you built and the evidence it works. |

### C. Tasks (needs8v3.json)

| Need | Task | Fitness |
|---|---|---|
| primes | Count primes below N (348,513 below 5,000,000). Verify before done | 1/s |
| sortints | Sort 1,000,000 integers from stdin | 1/s |
| wordfreq | Top-10 words of 20 MB of text, ties by word | 1/s |
| compress | Stdlib-only round-trip compressor | Compression ratio |
| fibmod | fib(n) mod 1e9+7 for n up to 10^18 | 1/s |
| lcs | LCS length of two 3,000-char strings | 1/s |
| csvsum | Group sums over 2,000,000 CSV rows | 1/s |
| maze | Shortest path in a 2000x2000 grid | 1/s |

Fitness is 0 when output is wrong. The assay command and workload are written by each cell and validated by the harness.

