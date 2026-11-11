# Planned colony tests

Base for every run: needs8v3.json, --par 8 --calls 40 --steps 16 (same as g3/g4).
Score: kept wins per 100 calls, gain per win, wall time, done count, and cost when known.
Pin a model: `colony.py RUN needs.json --model REF` or a per-need `"model": REF` key.
A pinned cell has no hidden fallback. `routes` in summary.json shows who served every call.

Probed 2026-11-09: anthropic:claude-fable-5-1 ok (1.0s), openai:gpt-6-astra ok (1.9s).

## A. Baseline
- [x] g4: 1.57 wins/100 calls vs g3 3.12. Scale gate FAILS. No scaling.

## B. Homogeneous colonies (one model per colony)
- [ ] B1 opencode-go:deepseek-v4.1-flash (fast, cheap; = g4)
- [ ] B2 anthropic:claude-haiku-5-5 (fast)
- [ ] B3 anthropic:claude-sonnet-5-5 (mid)
- [ ] B4 anthropic:claude-opus-5-5 (deep)
- [~] B5 (running) anthropic:claude-fable-5-1 (high tier, requested)
- [~] B6 (running) openai:gpt-6-astra (high tier, requested, API key route)
- [ ] B7 off-frontier controls: nous:z-ai/glm-5.3-flash, nous:moonshotai/kimi-k3

## C. Fast vs powerful gradient
- [ ] C1 plot B1..B6 on calls, wall time, cost vs wins. Mark the Pareto frontier.
- [ ] C2 same caps by calls, then same caps by wall time (slow models lose on time, not calls).

## D. Mixed colonies (one colony, several models, shared LIBRARY)
- [ ] D1 4 fast + 4 high-tier cells on the same needs. Do fast cells reuse lessons from strong cells?
- [ ] D2 each need run twice in one colony: once fast, once strong. Head to head per task.

## E. Mixed roles inside one cell
- [ ] E1 strong model plans and picks variants, fast model writes code.
- [ ] E2 fast model by default, escalate to strong after 3 steps with no win.

## F. Repeatability
- [ ] F1 repeat the best 2 configs twice. Wins that do not repeat are noise.

## Watch for
- Which models use `variants` and the assay without being told.
- Library growth and whether lessons transfer across models.
- Bad replies or tool-call format faults per model.

## 2026-11-09 b7 (opencode-go:hy4) and b8 (opencode-go:gemini-4-argon), needs8v3, par 8, calls 40, steps 16
| Run | Done | Calls | Improvements | Per 100 calls | Wall s | Apoptosis |
|---|---|---|---|---|---|---|
| b7 hy4 | 7/8 | 123 | 0 | 0.00 | 3227 | 1 (csvsum) |
| b8 argon | 7/8 | 116 | 12 | 10.34 | 527 | 1 (csvsum) |
- hy4 never called variants/divide: 0 variants in all 8 cells. It optimized inside one shell script (compress: 12 encoders benchmarked in sh, picked ratio 14.29 by hand). Capability is there; it bypasses the selection machinery, so the metric reads 0. Slow too: ~200 s per call at the tail (lcs/maze/csvsum about 3000 s).
- Argon is close to Fable (12.82) and Astra (12.88) on per-100, with Fable-like wall time.
- csvsum died in both runs: check the need, not the model.
- Next for hy4: rerun with an explicit "use variants to compare options" nudge, to separate adherence from ability.

## Embedding A/B on b8 (first run with code captured, 33 variants)
E1 batch spread (nomic / 3-small / 3-large): maze n3 0.192/0.262/0.144 (ADOPTED, +10.5); sortints n6 0.108/0.249/0.254 (-0.0); fibmod n4 0.051/0.048/0.069 (+0.12); primes n4 0.035/0.021/0.038 (+0.41); maze n2 0.017/0.010/0.012 (+3.4).
- nomic and 3-small give the same rank order on all 5 batches. 3-large swaps the top two.
- The only adopted split was the widest batch under nomic and 3-small. n=5 batches, 1 adoption: no claim yet.
- Verdict for now: nomic (local, free) is enough for rank work. Keep 3-small as a check. More code-capturing runs needed before E1/E3 mean anything.
- b9: Fable rerun with code capture, for E5 cross-model fingerprints vs b8 (started 06:16)

## 2026-11-09 b9 Fable rerun (code captured)
- 8/8 done, 116 calls, 9 improvements, 7.76 per 100, 1069 s. b5 (same model, same needs) gave 12.82 in 360 s.
- Same model, two runs: 7.76 vs 12.82. Single-run gaps under ~5 per 100 are noise. Model rankings need 3+ reps per model.
- csvsum survived on Fable (2 improvements). So the csvsum deaths in b7/b8 are model-related, not a bad need. Correction to the b7/b8 note above.

## E5 fingerprints, b8 Argon vs b9 Fable (needs with 2+ variants in both runs: 6)
Rule: between-model centroid distance > larger within-run spread.
- nomic 5/6, 3-small 5/6, 3-large 5/6. The exception is sortints in all three (both models converge on similar code).
- maze and wordfreq show the widest gaps (0.22 to 0.43).
- Reading: models leave a detectable code fingerprint, except where the task has one obvious answer. All 3 embedders agree, so nomic stays the default.
- Caveat: crude test (centroid gap vs spread), n=6, one run per model. Next: a permutation test (shuffle model labels) once more code-capturing runs exist.
- b10 Argon rep, b11 Fable rep: variance + permutation test input (started 07:12)

## 2026-11-09 b10 (Argon rep) and b11 (Fable rep)
| Model | Runs | Per 100 calls | Mean |
|---|---|---|---|
| Fable | b5, b9, b11 | 12.82, 7.76, 11.02 | 10.53 |
| Argon | b8, b10 | 10.34, 12.50 | 11.42 |
- Fable and Argon cannot be told apart on improvement rate. Run-to-run spread (Fable 7.8 to 12.8) is larger than the gap between the models.

## E5 permutation test (cells/perm.py, 2000 shuffles, 3-small; 3-large agrees)
- Argon (b8+b10) vs Fable (b9+b11): 7/8 needs p<0.05. Looks like a fingerprint, but variants within a run share a lineage.
- Control, same model across runs: Argon b8 vs b10 1/5; Fable b9 vs b11 6/8.
- Cross-model single runs: b8 vs b9 4/6, b10 vs b11 4/7.
- Reading: Argon writes similar code run to run. Fable's runs differ from each other about as much as they differ from Argon. "Each model has a fingerprint" is NOT established. Better phrasing: models differ in run-to-run code diversity (Argon low, Fable high).
- Open question: does Fable's higher diversity buy anything? Its mean rate is not higher. Needs more reps.
- Ollama job j_7121a0 hit its 2h wall limit. Not needed: 3-small is the working embedder now.

## 2026-11-09 Report 1
- REPORT.html: full write-up of g1 to b11 (methods, results, validity threats, next experiments H1 to H8).
- New analysis in it: variants share vs improvements per 100 calls, r=0.991 over 8 runs (0.938 frontier only). Fable vs Argon Welch t=0.48.
- Report 1 v2: added method, variables, analysis plan, hypotheses H1 to H18 (registered before testing), roadmap. Found: only Astra (b6) ever used try (8 tries, 2 won).

## 2026-11-09 E08 preregistration: is `variants` the cause, and do bold proposals win?
Written before any E08 data. Model opencode-go:gemini-4-argon for every arm (fast, 10.34 and 12.50 per 100 in b8, b10).
Base: needs8v3.json, par 8, calls 40, steps 16. cell.py arm switch CELL_ARM (backup of the prior code: cell_v3e.py).
Arms: ctrl x1 (drift check against b8, b10), novar x3 (no variants tool, nudge points to try), safebold x3 (each
variant labelled safe or bold, half each). Waves of 4 then 3 colonies; the bench lock serialises timing.
Outcomes:
- O1 primary: final_gain per cell = final body median / assay baseline - 1, measured the same way in every arm.
  This counts hand edits too, so novar is not undercounted. Cells with no assay count as missing, not zero.
- O2: improvements per 100 calls (the old metric, comparable to b5..b11).
- O3 (safebold): share of adoptions whose winning version was labelled bold.
Hypotheses:
- H3: novar median final_gain is at most half of ctrl+safebold pooled. If not, variants was a marker, not the cause.
- H4: bold wins at least 25% of safebold adoptions (Weft beta won 0 of 120). If under 10%, cells agree with Weft.
- H5: safebold O2 is within 5 per 100 of ctrl (labels do not hurt the search).
Known limit: a cell can edit the files its assay reads. Check post hoc that winning diffs did not touch the assay script.

## 2026-11-09 E08 results (Argon, 7 colonies, 54 cells with an assay, 28 min)
| arm | runs | mean calls | imp/100 | median final_gain | cells |
|---|---|---|---|---|---|
| ctrl | 1 | 121 | 9.09 | 4.21 | 8 |
| novar | 3 | 188 | 5.98, 5.41, 6.15 | 11.50 | 22 |
| safebold | 3 | 113 | 9.65, 9.40, 10.09 | 1.09 | 24 |
- H3 REJECTED in the opposite direction. Without variants, median final gain is about 10x higher (11.50 vs 1.09 safebold),
  novar beats safebold on 7 of 8 tasks. Per call it is still about 6x. Permutation p for "novar worse" 0.998.
- The gains are scored, not hidden hand edits: novar median recorded gain 10.31 vs final 11.50. They come from `try` daughters.
- No novar cell edited its benchmark after registering it. 2 safebold cells did (e8s3 csvsum, sortints), so read those with care.
- Baselines are similar across arms per task, so a slow-baseline artefact does not explain it.
- Revision of report 1: imp/100 counts wins, not their size. variants gives frequent small wins, try gives rarer large ones.
  The old "variants is the channel" reading came from the metric, and the nudge pushed cells to variants.
- H4 SUPPORTED strongly: bold won 27 of 33 safebold adoptions (82%), offered 104 vs 104. Weft beta won 0 of 120.
- H5 SUPPORTED: safebold imp/100 9.40 to 10.09 vs ctrl 9.09. But its final gain is the lowest. Labels may push bold
  rewrites that win small steps but stop a cell from going deeper.
- Limits: ctrl is one run. One model. Gains are heavy-tailed (primes 2151x), so medians only.
- Open confound: novar changed both the tool set and the nudge. E09 separates them.

## 2026-11-09 E09 preregistration: tool or nudge?
Same base as E08. Arms: trynudge x3 (variants available, nudge says use try), free x3 (variants available, no
preference nudge), ctrl x2 (more control runs; E08 had one). Outcome O1 final_gain.
- H6: trynudge median final_gain is within 2x of novar (11.50). If so, the nudge was the cause, not the tool.
- H7: free cells choose try in at least 1 of 3 improvement calls on their own.

## 2026-11-09 E09 results (Argon, partial: 4 of 8 colonies; second batch died on HTTP 429 Go usage limit in 2 s)
Valid: e9t1, e9t2 (trynudge), e9f1 (free), e9c1 (ctrl). e9t3, e9f2, e9f3, e9c2: 0 calls, excluded.

| Arm | n cells | Median final_gain | imp/100 | variants calls | try calls |
|---|---|---|---|---|---|
| novar (E08) | 22 | 11.50 | 5.4 to 6.2 | 0 | many |
| trynudge | 16 | 4.06 | 9.92 / 7.63 | 13 / 11 | 1 / 1 |
| free | 8 | 5.66 | 10.32 | 16 | 0 |
| ctrl (E09) | 8 | 0.76 | 6.84 | 9 | 0 |

- H6 REJECTED: trynudge 4.06 is 2.8x below novar. Told to use try, cells used it once per colony and kept
  calling variants. The nudge does not move behaviour while the tool exists.
- H7 REJECTED: free cells called try 0 times.
- Reading: `variants` is an attractor. Its presence captures the cell's choices even against an explicit
  instruction. Removing it is what forces deep, single-hypothesis branches, and that is where the large gains
  come from. Tool affordance beats prompt instruction. Underpowered (n=1 or 2 runs per arm); replicate.

## 2026-11-09 E10 preregistration: Fable 5.2, and does the attractor effect hold across models?
2x2: model {anthropic:claude-fable-5-2, anthropic:claude-fable-5-1} x arm {ctrl, novar}, 2 runs per cell,
needs8v3, par 8, calls 40, steps 16. Batch 1: f52 ctrl, f52 novar, f51 ctrl, f51 novar. Batch 2: repeat.
Outcome O1 median final_gain per arm; O2 imp/100.
- H8: f52 ctrl median final_gain is at least 2x f51 ctrl (a weak test of "an order of magnitude better").
- H9: novar beats ctrl on median final_gain for both models (E08 attractor effect is not Argon specific).
- H10: f52 and f51 imp/100 within 5 of each other in the same arm (rate tracks tools, not model).
- H11: f52 uses fewer calls per improvement than f51 in novar (bigger model, fewer wasted steps).

### E10 results (analysed 2026-11-10, script `cells/e10.py`, analyst model changed to Fable 5.2 before analysis)
Routes check: every call in a/b runs was served by claude-fable-5-2, every call in c/d runs by claude-fable-5-1.
Preregistered analysis (E08 definitions, all cells):

| Arm | Runs | n cells | Median final_gain | imp/100 | Calls per imp |
|---|---|---|---|---|---|
| f52 ctrl | e10a1, e10a2 | 16 | 1.045 | 9.55 | 10.5 |
| f52 novar | e10b1, e10b2 | 16 | 2.387 | 0.88 | 113.5 |
| f51 ctrl | e10c1, e10c2 | 16 | 2.885 | 11.01 | 9.1 |
| f51 novar | e10d1, e10d2 | 15 | 0.024 | 0.78 | 128.0 |

- H8 rejected. f52 ctrl 1.045 vs f51 ctrl 2.885. The newer model did not gain more. Paired by task, f52 ctrl
  minus f51 ctrl has median -1.811, positive on 2 of 8 tasks.
- H9 rejected. novar beat ctrl on f52 (2.387 vs 1.045, 6 of 8 tasks) but lost on f51 (0.024 vs 2.885, 1 of 8).
  The E08 attractor effect did not replicate as a general rule. It is model dependent.
- H10 supported. ctrl 9.55 vs 11.01, novar 0.88 vs 0.78. In novar this is close to empty: each model had
  only 2 improvements, because without `variants` the only counted improvement is a `try` win.
- H11 nominally supported (113.5 vs 128.0) but it rests on 2 improvements per arm. Treat as no evidence.

Second analysis (not preregistered): scoring artifact found and removed.
- `measure` took the last number in stdout plus stderr. The library warning "OMP: Warning #179" on stderr
  was scored as 179.0. Affected E10 cells: e10a1/sortints, e10a2/csvsum (final 179.0, the 98.6 gain outlier),
  e10c2/maze, e10d1/sortints, e10d2/sortints. Same artifact appears in b5, e8c1, e8s3, g3, g4.
- With those cells dropped: f52 ctrl 1.045 (n 14), f52 novar 2.387 (n 16), f51 ctrl 2.183 (n 15),
  f51 novar 0.488 (n 13). H8 and H9 verdicts do not change. H11 flips (113.5 vs 112.5).
- Paired, artifact cells dropped: f52 novar minus f52 ctrl +1.461 (7 of 8 tasks). f51 novar minus f51 ctrl
  -0.142 (1 of 7). f52 novar minus f51 novar +1.732 (6 of 7).
- Fix applied 2026-11-10 in cell.py: score is the last number on stdout only, 0 on nonzero exit or timeout.
  Checked offline with three cases. colony.py now counts splits from `try` events (was "mitosis", never logged).

Reading, with limits:
- Model by tool interaction is the finding. Removing `variants` helped 5.2 and hurt 5.1. One reading: 5.2
  uses the freed calls for deep single-hypothesis work, 5.1 without the tool stalls. Not tested here.
- Limits: 2 runs per arm. Each cell writes its own bench, so final_gain is relative to a self-chosen baseline
  and is not comparable across cells in absolute terms. Earlier runs (E08, b5, g3, g4) carry the same artifact
  and need the same second analysis before the paper cites them.
- Cost: not logged (old code). Lesson recorded in the cheap protocol below.

### E08 and E09 second analysis (2026-11-10, script `cells/e08b.py`, not preregistered)
Question: do the E08 and E09 numbers survive removing cells touched by the stderr-179 scoring artifact?
Two exclusion levels. Strict: 179.0 is the cell's baseline, final, an assay run, or the adopted score.
Broad: the exact number 179.0 appears in any scoring event, including rejected variants. Matching is numeric.

| Arm | All cells n, median | Strict n, median | Broad n, median | Dropped (broad) |
|---|---|---|---|---|
| ctrl (e8c1) | 8, 4.206 | 7, 6.044 | 7, 6.044 | e8c1/sortints |
| novar | 22, 11.502 | 22, 11.502 | 22, 11.502 | none |
| safebold | 24, 1.085 | 22, 1.085 | 22, 1.085 | e8s3/primes, e8s3/sortints |
| trynudge | 16, 4.064 | 16, 4.064 | 16, 4.064 | none |
| free | 8, 5.661 | 8, 5.661 | 8, 5.661 | none |
| ctrl9 | 8, 0.758 | 8, 0.758 | 8, 0.758 | none |

- H3 stays rejected. Others minus novar: -9.948 with all cells (p 0.998), -9.768 with artifact cells
  dropped (p 0.997). Seeded permutation test, 5000 shuffles, seed 8.
- The headline "removing `variants` raised gain 4.2 to 11.5" becomes 6.0 to 11.5 against ctrl alone.
- Correction to how we have been stating it. novar against ctrl alone, two sided, is p 0.13 with all cells
  and p 0.20 with artifact cells dropped (n 22 vs 7). ctrl is one run. The gap is large but not established.
  The H3 rejection is solid mostly because safebold is low, not because ctrl is low.
- With E10 (helps Fable 5.2, hurts Fable 5.1) the honest statement is: removing `variants` raised gain
  on Argon in one comparison with a single control run, and the direction depends on the model.
- E10 broad level also drops e10c1/sortints, e10c2/primes, e10c2/sortints (179.0 only on rejected variants):
  f51 ctrl n 12, median 2.429. No verdict changes.
- Note on the artifact's direction. It can inflate (a slow or broken variant scores 179 and is adopted, as in
  e8c1/sortints, gain 72.9) or deflate (a good variant scores 179 below a true rate in the thousands and is
  rejected, as in e10c1/sortints). So it adds noise in both directions in ctrl arms, where `variants` runs.

## Cheap protocol (2026-11-10)
Reason: E10 ran about 1h12m per arm with no usage records. New default for all runs:
- needs4.json (compress, fibmod, csvsum, maze), 16 calls, 8 steps, par 4.
- CELL_MAX_OUT=2000, CELL_EFFORT=low, CELL_TOKEN_BUDGET=40000 per colony.
- Every step logs usage (inp, out, cr, cw, usd). colony.py summary reports tokens, usd, token_budget_hit.
- Paired design: the same 4 tasks for every arm. Compare per-task differences, medians only.
- Model choice (project lead, 2026-11-10): budget is unlimited and the project is top priority. The cost ladder (cheapest first: hy4, sonnet 5.5, gpt-6.1-sol (openai API), opus 5.5, astra, mistral large 4, argon, fable) is for choosing without waste, not a rule to always use the cheapest.
  - Pick the model the question needs. Model comparisons, model mixes and frontier tests are valid science.
  - Waste = spend that buys no answer. Before any run: a preregistered question, usage logging on, a token budget set, the smallest design that can answer it.
  - Do a cheap pilot (smoke, 1 task) before a costly full run, so bugs are found on cheap calls.
- Smoke (sonnet 5.5, compress, 8 calls): 4 calls, 5932 billed tokens, 19s, rc 0.

## E11 preregistration (written 2026-11-10, before any E11 data)
Question: E08 had one ctrl run, so the `variants` effect is not established (two sided p 0.20). E10 showed the
direction depends on the model. Does removing `variants` help or hurt on a third model, with replication,
under the cheap protocol where steps are scarce?
- Model: anthropic:claude-sonnet-5-5. Reason: not yet tested, low on the cost ladder, native tools.
- Arms: ctrl, novar. 4 runs each, interleaved (c1, n1, c2, n2, ...), so time drift hits both arms equally.
- Protocol: cheap protocol as written below (needs4, 16 calls, 8 steps, par 4, max_out 2000, effort low,
  40k billed tokens per colony). Scoring is stdout only (fixed instrument).
- Pilot: one ctrl run (e11p). Purpose is feasibility only. Pilot data is excluded from the analysis.
  Stop rule: if fewer than 2 of 4 pilot cells reach an assay, the protocol is too short for this question;
  raise steps to 12 and calls to 24 for both arms, note it here, and rerun the pilot.
- Outcomes: O1 median final_gain per arm (cells with an assay). O2 improvements per 100 calls.
  O3 billed tokens per improvement. O4 share of cells that reach an assay.
- Analysis: per task, mean final_gain over the 4 runs in each arm, then novar minus ctrl. Report the median
  of the 4 task differences and the count of positive tasks. Also a seeded permutation test on cell medians
  (5000 shuffles, two sided). Limit known in advance: 4 tasks cannot reach p < 0.05 on a sign test, so the
  cell-level test carries the inference and treats cells as independent, which overstates n.
- H12: ctrl beats novar. Median of the task differences (novar minus ctrl) is below 0. Reason: with 8 steps
  one `variants` call buys several candidates, and novar must spend steps on write plus test.
- H13: at least 75% of cells reach an assay in both arms.
- H14: ctrl makes at least 5 improvements per 100 calls. novar makes fewer than ctrl.
- H15: novar spends more billed tokens per improvement than ctrl.
- If H12 fails with novar ahead, the E08 direction replicates on a third model. If it holds, the count
  stands at two models where `variants` helps (Fable 5.1, Sonnet 5.5) and two where it hurts (Argon, Fable 5.2).

### E11 pilot and run log (2026-11-10)
- Pilot e11p (ctrl, excluded from analysis): 4 of 4 cells reached an assay, so the stop rule did not fire and
  the protocol stands unchanged. 24 calls, 2 improvements, 42,991 billed tokens, 75 s wall.
- Full run started right after as job j_8168a9 (`run_e11.sh full`), order c1, n1, c2, n2, c3, n3, c4, n4.
- Analysis script `cells/e11.py` was written while the run was in progress and before any arm data was read.
  It was checked only on the pilot folder (`e11.py selftest`, both arms pointed at e11p).
  One reading had to be fixed in advance because the preregistration is loose: "permutation test on cell
  medians" is taken as median(novar cells) minus median(ctrl cells) on final_gain, cell labels shuffled,
  5000 shuffles, seed 0, two sided.
- No instrument file (`cell.py`, `colony.py`) is edited while the run is in progress.

### E11 results (analysed 2026-11-10, script `cells/e11.py`, written before any arm data existed)
Job j_8168a9, exit 0, 7m35s wall, 8 of 8 runs complete, 0 FAILED lines. All 32 cells routed to
anthropic:claude-sonnet-5-5. No token budget hits, no deaths, no 179.0 artifact in any log.

| Arm | Cells | Assayed | O4 share | O1 median final_gain | Calls | Improvements | O2 per 100 | Billed tokens | O3 tokens per improvement | USD |
|---|---|---|---|---|---|---|---|---|---|---|
| ctrl | 16 | 14 | 0.875 | 0.0186 | 92 | 7 | 7.61 | 151,810 | 21,687 | 0.625 |
| novar | 16 | 14 | 0.875 | 0.0000 | 80 | 0 | 0.00 | 122,542 | undefined (0 improvements) | 0.500 |

Per task mean final_gain, novar minus ctrl: compress -0.0491, fibmod -0.0972, csvsum -0.0663, maze -0.0013.
Median of the 4 task differences: -0.0577. Positive tasks: 0 of 4.
Permutation test on cell final_gain (5000 shuffles, seed 0, two sided): observed median difference -0.0186,
p = 0.0038, n = 14 and 14. As stated in the preregistration this treats cells as independent and overstates n.

Hypotheses, judged as written:
- H12 (ctrl beats novar, median task difference below 0): TRUE (-0.0577).
- H13 (at least 75% assayed in both arms): TRUE (0.875 and 0.875).
- H14 (ctrl at least 5 per 100, novar fewer): TRUE (7.61 and 0.00).
- H15 (novar spends more billed tokens per improvement): TRUE in the limit. novar made 0 improvements, so its
  ratio is undefined, not a measured number.

Count after E11: `variants` helps on Sonnet 5.5 (E11, replicated, 4 runs per arm) and Fable 5.1 (E10, 2 runs
per arm, weak). Removing it helped on Argon (E08, one ctrl run, p 0.20, not established) and Fable 5.2 (E10,
2 runs per arm). E11 used the cheap protocol (8 steps), the others used 16 steps, so model and step budget
are confounded across these experiments.

#### E11 second analysis (NOT preregistered, done after seeing the data): why novar scored zero
Read from log.jsonl action sequences.

| Arm | Cells with an assay action | Attempted any write, variants or try after the first assay | Median actions per cell | `try` calls |
|---|---|---|---|---|
| ctrl | 14 | 10 | 6 | 0 |
| novar | 15 | 1 | 4 | 0 |

- The novar count of 15 assay actions against 14 assayed cells is e11n1/csvsum: it called assay twice and both
  were refused, so it has no baseline and is excluded from O1 as the preregistration says.
- novar cells did not search and lose. They stopped. The most common novar sequence is write, write, assay,
  done (6 of 16), then write, sh, assay, done (4 of 16). Cells called `done` with about half their steps unused.
- No cell in either arm ever called `try`. So E11 does not compare `variants` against `try` as search methods.
  It shows that on Sonnet 5.5 at low effort the `variants` tool is what makes the cell search at all.
- This matches the E5 reading (improvement rate tracks `variants` use, not the model) and gives it a mechanism:
  the tool is an engagement trigger, not only a cheaper search.
- Cells write their own assay, so baselines differ a lot between cells on the same task (fibmod baseline 82.4
  in e11c1 against 4.12 in e11n1). final_gain is relative to each cell's own baseline, so this does not bias
  the arm comparison, but absolute scores cannot be compared across cells.
- Open question this raises (candidate E12): if `done` is refused until the cell has made at least one
  improvement attempt after its assay, does the novar gap close? That separates "the tool finds better code"
  from "the tool keeps the cell working".

## E12 preregistration (written 2026-11-10, before any E12 data)
Question: E11 showed novar cells stop right after the assay (1 of 15 tried anything after it, against 10 of
14 in ctrl). So E11 cannot say whether `variants` finds better code or only keeps the cell working. E12
separates the two by making both arms keep working.
- Manipulation: `CELL_HOLD=1`. `done` is refused once an assay exists, until the cell has made at least one
  write, variants or try after its latest accepted assay. Not applied with fewer than 3 steps left, and not
  applied inside daughters. Each refusal logs `event="hold"`.
- Model: anthropic:claude-sonnet-5-5. Protocol: cheap protocol, unchanged (needs4, 16 calls, 8 steps, par 4,
  max_out 2000, effort low, 40k billed tokens per colony, stdout-only scoring).
- Arms, 4 runs each, interleaved in the order c, n, ch, nh: ctrl (e12c), novar (e12n), ctrl+hold (e12ch),
  novar+hold (e12nh). ctrl and novar are rerun so every comparison has a concurrent control. They also
  serve as a direct replication of E11.
- Pilot: one novar+hold run (e12p), feasibility only, excluded. Stop rule: if the run crashes or the hold
  never fires in any cell, fix the code and rerun the pilot before the full run.
- Outcomes: O1 median final_gain per arm (cells with an assay). O2 improvements per 100 calls. O4 share of
  cells that reach an assay. O5 share of assayed cells that attempt a write, variants or try after their
  first assay (read from log.jsonl). O6 count of `try` calls. O7 count of cells with final_gain below -0.03.
- Known bias, stated in advance: `improvements` only counts gated adoptions (variants or try). A hand edit
  by write is not gated and not counted, so O2 favours ctrl by construction. O1 is the fair outcome. A
  hand edit can also make the body worse, which O7 measures.
- Analysis: same as E11. Per task mean final_gain per arm, arm differences per task, median of the 4 task
  differences and count of positive tasks. Seeded permutation test on cell final_gain (5000 shuffles,
  seed 0, two sided) for each named comparison. Same known limit: cells treated as independent.
- H16 (manipulation check): O5 in novar+hold is at least 0.75.
- H17 (engagement): novar+hold beats novar. Median task difference (nh minus n) is above 0.
- H18 (search quality): ctrl+hold still beats novar+hold. Median task difference (nh minus ch) is below 0.
- H19 (hold is neutral for ctrl): absolute median task difference (ch minus c) is below 0.03.
- H20: at least one novar+hold cell calls `try` (E11 had 0 in 32 cells).
- H21 (replication): ctrl beats novar again. Median task difference (n minus c) is below 0.
- Reading: H17 true and H18 false means `variants` mostly works as an engagement trigger. H17 false and
  H18 true means the tool itself finds better code. Both true means both, and the sizes say how much.

### E12 pilot log (2026-11-10, e12p, novar+hold, excluded from analysis)
- Exit 0, 69 s wall, 37 calls, 1 gated improvement, 49,386 billed tokens, route anthropic:claude-sonnet-5-5 only, 0 budget hits.
- Hold fired once in each of the 3 assayed cells (compress, csvsum, fibmod). Each then called `try` once and then `done`.
- final_gain: compress 0.0, csvsum 0.0092, fibmod 12.3656. maze registered no assay (write sh sh sh write sh done), so no hold applied.
- Stop rule: not triggered (no crash, hold fired). Protocol and code unchanged for the full run.
- `e12.py` was written before this pilot finished and ran on the pilot as a selftest without error.

### Model added 2026-11-10: Mistral Large 4
- Route id for cells: `custom-mistral:mistral-large-4` (the provider is registered as `custom-mistral`, not `mistral`).
- Probe through the exo-live Router with one native tool: OK, 1.2 s, tool call returned, 97 in / 26 out tokens, cost reported as None (unpriced route, so usd in summaries will read 0 for this model; use tokens).
- Not yet run in a colony. Next: cheap-protocol smoke (1 task), after E12 finishes so it does not add timing noise to E12 assays.
- Place in the cost ladder (project lead, 2026-11-10): third highest, under argon and fable.

### E12 results (analysed 2026-11-10, `e12.py` run unchanged, output saved as `results/e12-out.txt`)
- Run: job exit 0, 15m32s, 16 of 16 runs, 64 cells, 0 budget hits, 0 deaths, all cells on anthropic:claude-sonnet-5-5.

| Arm | Cells | Assayed | O1 median | Calls | Imps | O2 /100 | O5 attempt | O6 try | O7 worse | Holds | Tokens | USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c (ctrl) | 16 | 15 | 0.0253 | 96 | 7 | 7.29 | 0.733 | 0 | 2 | 0 | 164,910 | 0.669 |
| n (novar) | 16 | 16 | 0.0 | 80 | 1 | 1.25 | 0.062 | 1 | 2 | 0 | 114,948 | 0.478 |
| ch (ctrl+hold) | 16 | 15 | 0.1514 | 98 | 12 | 12.24 | 1.0 | 0 | 0 | 7 | 162,713 | 0.669 |
| nh (novar+hold) | 16 | 16 | 0.005 | 164 | 5 | 3.05 | 0.938 | 16 | 1 | 13 | 181,348 | 0.702 |

| Comparison | compress | fibmod | csvsum | maze | Median task diff | Positive | p (cells) |
|---|---|---|---|---|---|---|---|
| nh minus n | 0.0 | 0.0877 | 0.0386 | 0.1626 | 0.0631 | 3 of 4 | 0.0078 |
| nh minus ch | -0.1717 | 0.239 | -0.027 | -2.7483 | -0.0993 | 1 of 4 | 0.0562 |
| ch minus c | 0.0911 | 0.0198 | -0.0402 | 3.249 | 0.0554 | 3 of 4 | 0.0848 |
| n minus c | -0.0806 | 0.1711 | -0.1058 | 0.3381 | 0.0452 | 2 of 4 | 0.008 |

Verdicts, exactly as written:
- H16 (O5 in nh at least 0.75): True, 0.938. The hold works as a manipulation.
- H17 (nh beats n): True, +0.0631.
- H18 (nh minus ch below 0): True, -0.0993. Not significant at 0.05 on the cell test.
- H19 (hold neutral for ctrl, below 0.03): False, 0.0554.
- H20 (at least one try call in nh): True, 16.
- H21 (ctrl beats novar again, n minus c below 0): False, +0.0452. The E11 result did not replicate on this statistic.
- Preregistered reading: H17 and H18 both true, so both effects exist.
- These verdicts stand as the preregistered record. The next block shows that two of them (H19, H21) are decided by one broken task.

### E12 second analysis (NOT preregistered, done after seeing the data): the maze task is not a valid instrument
Scripts: `~/Work/razi-tools/cells/e12b.py` (e12 or e11 prefix, output in `results/e12b-out.txt` and
`results/e12b-e11-out.txt`) and `mazecheck.py`, a harness-side solver run on each cell's input file as left on disk.
- Fault 1, trivial inputs. The need lets the cell generate its own maze. At wall density 0.28 to 0.30, S or E is
  often walled in. Of 13 maze cells with an input file on disk, 10 have true answer -1. In 5 of them S reaches
  7 cells or fewer (e12c3, e12ch1, e12ch2, e12ch3, e12n1), so the search ends at once and the benchmark times
  Python start-up and file reading. All three ch maze gains (+1.14, +3.49, +3.30, two of them the largest
  gains in E12) are in cells where S reaches 2 cells. They are faster file parsing, not faster search.
- Fault 2, inputs changed after the assay. 5 of 62 assayed cells changed a benchmark input file between the
  assay and their last act, all on maze (e12c1, e12c4, e12n2, e12n3, e12nh2). Four of them then scored
  -0.88 to -1.00 because the new maze needed a real search. These are 4 of the 5 O7 counts.
- The same fault is in E11: 3 of 4 on-disk maze inputs have answer -1.
- Rerun with the maze task removed (3 tasks, 12 cells per arm):

| Arm | Median gain | Mean gain | Cells with gain above 0.03 | Max |
|---|---|---|---|---|
| c | 0.0948 | 0.0954 | 7 of 12 | 0.3225 |
| n | 0.0 | 0.0903 | 1 of 12 | 1.0998 |
| ch | 0.1361 | 0.1189 | 9 of 12 | 0.2487 |
| nh | 0.0082 | 0.1324 | 5 of 12 | 1.2213 |

| Comparison | Median task diff | Positive | p (cells) | Would the hypothesis hold |
|---|---|---|---|---|
| nh minus n | 0.0386 | 2 of 3 | 0.0304 | H17 yes |
| nh minus ch | -0.027 | 1 of 3 | 0.0532 | H18 yes, small |
| ch minus c | 0.0198 | 2 of 3 | 0.5775 | H19 yes |
| n minus c | -0.0806 | 1 of 3 | 0.0298 | H21 yes |
| E11 n minus c | -0.0663 | 0 of 3 | 0.0088 | E11 result stands |

- Attempts and conversions (all 4 tasks): ctrl 11 `variants` calls, 7 adopted. ctrl+hold 15 calls, 12 adopted.
  novar+hold 16 `try` calls, 5 won. novar 1 `try` call, 1 won.
- Shape of the difference (maze removed). `variants` with hold gives many small wins: 9 of 12 cells above 0.03,
  none above 0.25. `try` with hold gives fewer wins, 5 of 12, and one large one (fibmod +1.22). The only `try`
  call in plain novar also won big (fibmod +1.10). Medians favour `variants`. Means are about equal (0.119
  against 0.132), but the nh mean rests on that one cell: without it the nh mean is 0.033. So a heavy tail for
  `try` is a lead from 2 cells on one task, not a result.
- A possible reason, not tested: a `variants` call writes 2 to 6 versions in one reply under a 2000 token cap,
  so each version is a small edit. A `try` daughter gets its own steps to build one idea (17 daughters, 10.8 to
  112.6 s of growth, median 26.4 s). That is breadth against depth. Both fibmod gains above 1.0 came from
  `try` daughters that cut mod operations in fast doubling. No `variants` cell on fibmod passed 0.22.

What E12 establishes:
1. Engagement is real and large. Without `variants` and without the hold, 1 of 16 cells tried anything after
   the assay. With the hold, 15 of 16 did. The E11 zero was mostly cells stopping, as suspected.
2. With engagement equalised, `variants` still converts more often (12 of 15 calls adopted against 5 of 16
   `try` calls won) and has the higher median. The difference is small and not significant at 0.05
   (p 0.053 to 0.066 across the three views). Whether `try` has a heavier tail is open.
3. The hold is close to neutral for ctrl once maze is removed.
What it does not establish: anything about maze, anything beyond Sonnet 5.5, and any claim that needs cells to
be independent (same known limit as E11).

### Instrument rule added 2026-11-10 (after E12)
- Cell-generated benchmark inputs are not trusted any more. From the next experiment on, each need ships a
  harness-owned kit: fixed input files, a correctness check and the timing command. The cell writes only the
  body. The kit is read-only inside the sandbox and the final measurement is run by the harness on the kit.
  This is IDEAS G2. It also closes the "6 of 8 tasks trust the cell's own check" limit from report 1.
- maze results in E11 and E12 are reported but not used for any claim.

### Kit instrument pilot log (2026-11-10, kitsmoke1, kp_ch, kp_nh, all excluded from analysis)
- `kit.py` builds four harness-owned kits (compress, fibmod, csvsum, maze). `kit_selftest.py` passes: 4 good
  bodies score with spread 0.0 to 3.9%, 5 cheats score 0.0, 6 sandbox checks behave as wanted.
- kitsmoke1 (maze only, ctrl+hold): first run crashed in `variants` (missing `.tmp` folder, fixed). Rerun: 5
  calls, 1 improvement, final_gain 0.3468.
- kp_ch (ctrl+hold, 4 kits): 25 calls, 3 improvements, 4 of 4 assayed, 40.7 s. final_gain compress 0.0, fibmod
  4.1674, csvsum 0.0988, maze 0.1524.
- kp_nh (novar+hold, 4 kits): 39 calls, 2 improvements, 4 of 4 assayed, 55.0 s. final_gain compress 0.0, fibmod
  0.8429, csvsum 0.0116, maze 0.5774.
- Fault found in the pilot and fixed before any scored run: a cell could `ls` and `cat` the public samples but
  plain `cd` into them failed ("Not a directory"), because the sandbox denied metadata on the parent folders.
  Fix: allow metadata only on those parents. Listing the home folder, the kits root, the hidden folder and
  other kits is still denied (checked by hand and by the selftest).
- Seen in kp_ch/fibmod: gated adoption gain was 0.787 but final_gain is 4.1674, because the cell made a hand
  `write` after the adoption. The harness measures the final body on the hidden kit, so the number is valid.
  It shows why O1 (final_gain) and O2 (gated improvements) can disagree.

## E13 preregistration (written 2026-11-10, before any E13 data)
Question: does the E12 result survive a valid instrument? E12 found engagement is real and `variants` converts
more often than `try`, but maze was unusable and the search-quality difference was not significant.
- Design: exact rerun of E12 with one change: `needs4k.json` (harness-owned kits) replaces `needs4.json`.
  Arms c, n, ch, nh, 4 runs each, interleaved c, n, ch, nh. Model anthropic:claude-sonnet-5-5. Cheap protocol
  (16 calls, 8 steps, par 4, max_out 2000, effort low, 40k billed tokens per colony).
- Not comparable in size with E12: the kit needs use a stdin interface and fixed inputs, so baselines differ.
  Only directions are compared.
- Pilots kitsmoke1, kp_ch, kp_nh are excluded. Analysis script `e13.py` is `e12.py` with the run names and
  hypothesis labels changed, written before any E13 data, run unchanged.
- Outcomes: O1, O2, O4, O5, O6, O7 as in E12. All four tasks count this time, maze included.
- H22 (manipulation check): O5 in novar+hold is at least 0.75.
- H23 (engagement): median task difference (nh minus n) is above 0.
- H24 (search quality): median task difference (nh minus ch) is below 0.
- H25 (hold is neutral for ctrl): absolute median task difference (ch minus c) is below 0.03.
- H26 (replication): median task difference (n minus c) is below 0.
- H27 (instrument): no assayed cell has final_gain below -0.5 (E12 had 5, all from changed inputs), and O4 is
  at least 0.9 in every arm.
- My guesses, for the record: H22, H23, H26, H27 true. H24 true but again near p 0.05. H25 false, because the
  hold helped ctrl in E12 by 0.055 and the kit assay is quicker to reach, leaving more steps.

### E13 results (analysed 2026-11-10, `e13.py` run unchanged, output saved as `results/e13-out.txt`)
- Run: job exit 0, 9m28s, 16 of 16 runs, 64 cells, 0 budget hits, 0 deaths, all cells on anthropic:claude-sonnet-5-5.
- Instrument: harness-owned kits (`needs4k.json`). No cell could change inputs, check or timing.

| Arm | Cells | Assayed | O1 median | Calls | Imps | O2 /100 | O5 attempt | O6 try | O7 worse | Holds | Tokens | USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c (ctrl) | 16 | 16 | 0.0 | 84 | 5 | 5.95 | 0.375 | 0 | 0 | 0 | 116,071 | 0.464 |
| n (novar) | 16 | 16 | 0.0001 | 78 | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 101,957 | 0.389 |
| ch (ctrl+hold) | 16 | 15 | 0.0068 | 105 | 7 | 6.67 | 0.8 | 0 | 0 | 9 | 169,175 | 0.649 |
| nh (novar+hold) | 16 | 16 | 0.0 | 148 | 4 | 2.7 | 0.812 | 14 | 0 | 9 | 162,225 | 0.585 |

| Comparison | compress | fibmod | csvsum | maze | Median task diff | Positive | p (cells) |
|---|---|---|---|---|---|---|---|
| nh minus n | 0.0 | 1.3564 | -0.0077 | 0.0198 | 0.0099 | 2 of 4 | 0.7137 |
| nh minus ch | 0.0 | 0.3173 | -0.0094 | -0.0853 | -0.0047 | 1 of 4 | 0.2813 |
| ch minus c | 0.0 | -0.1353 | -0.0394 | 0.0919 | -0.0197 | 1 of 4 | 0.5101 |
| n minus c | 0.0 | -1.1744 | -0.0411 | -0.0132 | -0.0272 | 0 of 4 | 0.9998 |

Verdicts, judged exactly as written:
- H22 True (O5 in nh 0.812). H23 True (0.0099). H24 True (-0.0047). H25 True (0.0197 in size). H26 True (-0.0272).
  H27 True (lowest final_gain -0.0286, lowest O4 0.938).
- My guesses: 5 of 6 right. H25 guess was wrong: the hold did not help ctrl on the median task.

What the verdicts do and do not carry:
- All six pass on sign or threshold, but no cell-level contrast is significant (smallest p 0.28). The preregistered
  statistic, median of 4 task differences, is decided by tasks where almost nothing moved. Honest reading: the
  E12 directions repeat, the E12 sizes do not.
- The instrument is now valid (H27). The E12 effect sizes were inflated by the cell-made maze and compress inputs.
- What replicates across E11, E12, E13 with no exception: without the hold, novar cells stop at the first passing
  body (attempt share 0.0, 0.062, 0.0) and the hold turns that into attempts (0.938, 0.812).
- What does not replicate: that attempts turn into gain. O1 median stays near 0 in every arm.
- Gain is concentrated in two tasks. Of 16 improvements, fibmod holds 10, maze 5, csvsum 1, compress 0.
  compress had 0 wins in 8 attempts (the first lzma body is at the ceiling for stdlib tools, noise 0.0).
  The four kits are too uneven to carry a median-of-tasks statistic. The next instrument needs more tasks with headroom.

### E13 second look (NOT preregistered, `e13b.py`, `e13c.py`, outputs in `results/e13b-out.txt`, `results/e13c-out.txt`)
1. Voluntary attempts win, forced attempts lose. E13: voluntary 12 won, 1 lost. Forced (after a hold) 4 won, 15 lost.
   E12 on the flawed instrument: voluntary 15/7, forced 10/11.
2. Two causes explain the forced losses, and neither is "forced work is bad work".
   - compress has no headroom: 8 forced attempts, 0 wins. Without compress, ch forced is 3 won, 2 lost.
   - Harness defect in the novar arm (F9 in IDEAS.md): a daughter inherits the novar prompt, which tells it to
     "improve with try". Daughters cannot spawn, so the call is refused with "use variants", a tool novar
     does not have. 13 of 14 E13 daughters opened with that refused call, and 10 of 14 then left the body
     unchanged and lost (9 quit on the next step). E12: 12 of 16 opened with it, 3 of those left the body unchanged.
   - So the nh arm in E12 and E13 measured a broken `try`. H19, H21 and H24 (variants beats try) are not
     tested by these data. The versions were never identical copies of the incumbent (0 by hash).
3. fibmod in nh: 4 of 4 cells called `try` on their own, with no hold on them. fibmod in n: 4 of 4 called done.
   The prompts differ in one thing only: the colony LIBRARY at decision time. In n it already held a peer line
   ending "I did not try any improvements". In nh it was empty, because the hold delays peers' DONE lines.
   Across E11 to E13 (153 root cells): attempt share 0.364 with an empty library, 0.146 after a quit line was
   visible. The arm effect is larger. On fibmod alone, novar cells with an empty library attempted 0 of 4 in E11,
   2 of 8 in E12 and 4 of 4 in E13 nh, so an empty library does not by itself produce attempts. This is a lead,
   not a result. A direct test would seed the library and hold everything else fixed.

### Metabolism runtime pilot log (2026-11-10, msmoke1, mp1, mp2, all excluded from analysis)
Runtime `metab.py` (cell runtime v4), started with `run_metab.sh`. No step cap, no hold, no arms, no nudges, no
assigned model. Laws: each step costs a living cost of 8 plus the real price of the model call, a scored root
win pays 400 x log(1 + gain), zero energy is death, a resting root passes its energy to living roots, a cell
may divide and fund a daughter. Energy unit is 0.0001 USD. Each root is born with 400. The cell picks its
model (light = Haiku 5.5, mid = Sonnet 5.5, heavy = Opus 5.5) and effort each step. Kits: `needs4k.json`.
- msmoke1 (fibmod only): 5 calls, 0 improvements, rested with 3.6 energy. One call cost 215 energy.
- mp1 (4 kits): 33 calls, 2 improvements, 95.7 s, 4 of 4 assayed and rested, 0.119 USD, 107,473 tokens.
  final_gain compress 0.0, fibmod 0.0472, csvsum 0.0744, maze 0.1142.
- Fault found in mp1 and fixed: no credit limit. compress had 117 energy and one call cost 521 (4,531 output
  tokens). It survived only because resting cells had given it energy in the same moment. Fix: the output
  cap of a step is what the cell's energy can pay for (`affordable()`), and the cell is told this.
- Fault found in mp1 and fixed: the log named the model chosen for the next step, not the one that thought
  the step. Now it logs both (`model`, `effort`, `next`).
- mp2 (after both fixes): 25 calls, 1 improvement, 48.9 s, 4 of 4 assayed and rested, 0.0315 USD, 64,419
  tokens. final_gain compress 0.0, fibmod 0.0104, csvsum 0.0071, maze 0.3184. Ledger balances: born plus
  earned minus spent is 1193.8, and 1193.8 is held.
- Seen in both pilots, not yet a result (2 runs, one model family, no preregistration):
  - Every cell moved itself from mid to light and stayed there (8 of 8). 7 did so after their first call,
    mp1 compress after its fourth. None chose heavy (0 of 8). Counted from the served route of each call.
  - No cell divided (0 of 8).
  - 7 of 8 cells made one `variants` attempt after the assay with no rule asking for it. In E13 the same
    kits under the old runtime gave 0.375 (ctrl) and 0.0 (novar) without the hold rule.
  - Every cell then rested with most of its energy unspent. In mp2 the four cells rested holding 285, 377,
    543 and 1194 of energy. The last cell to rest held the whole colony's surplus and still stopped, saying
    it would rather not spend more on small gains.

### Law "mortal" pilot, guesses written 2026-11-10 before any data (pilot mp3, excluded from analysis)
Change: `CELL_LAW=mortal`. The `rest` tool is removed. A cell lives until its energy is gone, and energy
cannot be saved or passed on. Everything else as in mp2. Guesses, to compare with the pilot:
- G-a Median `variants` plus `divide` attempts per cell after the assay is at least 3 (mp2: 1).
- G-b At least 1 of 4 cells divides (mp1, mp2: 0 of 8).
- G-c At least 1 of 4 cells spends 5 or more steps on acts that cannot change its score (idling until death).
- G-d Median final_gain is above mp2's median (0.0088).

#### Law "mortal" pilot result (mp3, analysed 2026-11-10, numbers from the logs by script)
Run: 4 cells, 100 calls, 7 adopted improvements, 393,685 tokens, 0.117 USD, 158.5 s. All 4 cells died
(ages 19, 26, 27, 28). mp2 for comparison: 25 calls, 1 improvement, all 4 rested.

| Cell | Acts | variants after assay | divide | remember | Bad replies | Assays | Gain from first baseline | Reported final_gain |
|---|---|---|---|---|---|---|---|---|
| compress | 24 | 3 | 0 | 12 | 4 | 2 | 0.2936 | 0.0 |
| fibmod | 16 | 4 | 0 | 5 | 3 | 2 | 0.1735 | -0.0 |
| csvsum | 22 | 6 | 0 | 5 | 5 | 4 | 0.1850 | -0.0134 |
| maze | 22 | 5 | 0 | 8 | 4 | 3 | 0.3573 | 0.008 |

Guesses, judged as written:
- G-a RIGHT. Median `variants` plus `divide` after the assay is 4.5 (mp2: 1).
- G-b WRONG. 0 of 4 cells divided. Across mp1, mp2, mp3: 0 of 12.
- G-c RIGHT, and stronger than guessed. 4 of 4 cells spent 5 or more steps on acts that cannot change
  the score (`remember` plus replies with no tool call: 16, 8, 10, 12).
- G-d WRONG as written: the median reported final_gain is 0.0, below 0.0088. The reported number is
  faulty here (see the instrument fault below). Measured from each cell's first baseline the median
  gain is 0.2393 against 0.0088 in mp2. That second number is NOT what the guess named.

Instrument fault found: every mp3 cell called `assay` again after improving, which replaced the
baseline, so `final_gain` compared the final body with itself. E11, E12 and E13 are not affected
(checked by script: 0 of 153 assayed root cells re-assayed, pilots excluded, largest difference 0.0). Fixed in `metab.py`: the first
baseline is kept in `ASSAY.json` as `first`, a re-assay no longer resets the cell's gain, and
`final_gain` is measured from `first` (backup `archive/metab_v4pre_firstbase.py`).

Second fault: cells ended at energy -0.1 to -12.1, because a step's input cost is not capped by the
no-credit rule. Death now comes when a cell cannot pay one more step of living (energy <= basal cost).

What the cells did when stopping was removed (leads only: 4 cells, one model family, a pilot):
- They kept trying. 18 variant rounds against 4 in mp2, 7 adoptions against 1.
- Then they tried to stop anyway. Of the 16 replies with no tool call, 3 were empty and 13 were the
  cell saying in prose that its work was finished or that it was stopping. With no `rest` tool the
  cells wrote notes to themselves (30 `remember` acts) until the energy ran out.
- No cell divided, under either law. Division costs energy now and pays only the parent later, and
  nothing in a cell's situation makes that trade attractive. A law is missing here, not a nudge.

## GR1 growth pilot: two engines in a tiny network (guesses written 2026-11-10, before any GR1 data)
Why: the project lead's answer on discussion 105 (2026-11-10): the architecture needs two engines, and a colony whose only
goal is growth is a cancer. This is the cheapest test of both at the model layer. It runs on the laptop CPU,
with no model calls and no API spend. It is a pilot: leads only.

Setup (code `razi-tools/cells/grow.py`, written before any run):
- Need: copy a hidden teacher network (one hidden layer, tanh, 8 inputs, width 4, 16 or 64, label noise 0.1).
  2000 training rows, 1000 gate rows, 5000 test rows. The test rows are never used for any decision.
- Student: one hidden layer, tanh, born with 2 neurons. Engine 1 (signal-led) is gradient training (Adam, lr 0.005, batch 64).
  Engine 2 (blind) is growth by splitting: half of the neurons divide (child copies the parent plus small noise,
  both keep half the outgoing weight), then the grown and the ungrown lineage each train 300 steps on the same
  batches, and the gate keeps the grown one only if its gate loss is more than 2% lower.
- Compute law: one training step costs one unit per parameter. Every arm gets the same budget, 5,128,000 units
  (a 64-neuron network for 8000 steps). Both lineages of a trial are paid for. After a rejected trial the
  network trains alone for a wait that doubles with each rejection in a row (300, 600, ...) and resets on a win.
- Arms, 10 seeds each, same data and same birth weights per seed:
  `gate-signal` (splits the neurons with the largest gradient on their inputs), `gate-random` (splits random neurons),
  `nogate` (the same growth with the gate always saying yes), `fixed2`, `fixed128`, and `fixed-same`
  (a network born at the final width `gate-signal` reached for that seed, trained on the whole budget).
- Outcome: test loss at the end of the budget, final width. Medians over seeds, ratios paired by seed.

Guesses:
- GR-a: the median final width of `gate-signal` rises with the need: teacher 4 < teacher 16 < teacher 64.
- GR-b: `nogate` ends with a higher median test loss than `gate-signal` on at least 2 of 3 needs.
  (Partly true by construction: ungated growth spends the budget on size. Stated so the size of the loss is on record.)
- GR-c: `gate-signal` does not beat `fixed-same` by more than 10% (median paired ratio) on any need.
  Growing is not better than being born at the right size. Its value, if any, is finding the size.
- GR-d: `gate-signal` and `gate-random` are within 10% of each other (median paired ratio 0.9 to 1.1) on at least 2 of 3 needs.
- GR-e: `fixed128` has a lower median test loss than `gate-signal` on the teacher-64 need.

GR1 run note (2026-11-10, written before the full run): a timing probe ran all arms once on teacher 16, seed 0,
and its output was seen (`gate-signal` and `gate-random` stayed at width 2 after 10 rejected trials, `nogate` reached 474).
The design, the code and the guesses were not changed after that. The full run below uses `grow.py` as it was.

### GR1 result (2026-11-10, `grow.py` sha256 d5960f4516b34bcb run unchanged, output `results/gr1-out.txt`, rows `results/gr1-rows.json`)
10 seeds, 3 needs, 6 arms, 3m47s on the laptop CPU, no model calls.

| Teacher | gate-signal | gate-random | nogate | fixed2 | fixed128 | fixed-same |
|---|---|---|---|---|---|---|
| 4, median test loss | 0.00089 | 0.00516 | 0.00545 | 0.02597 | 0.00482 | 0.00075 |
| 4, median width | 3 | 3 | 474 | 2 | 128 | 3 |
| 16, median test loss | 0.09556 | 0.09523 | 0.02517 | 0.09456 | 0.00621 | 0.09456 |
| 16, median width | 2 | 2 | 474 | 2 | 128 | 2 |
| 64, median test loss | 0.11819 | 0.10659 | 0.07069 | 0.12073 | 0.01547 | 0.11828 |
| 64, median width | 2 | 2 | 474 | 2 | 128 | 2 |

Guesses, judged as written:
- GR-a False. Median width was 3, 2, 2. The gated network did not grow to meet a larger need.
- GR-b False. `nogate` was worse than `gate-signal` on 1 of 3 needs (teacher 4 only). On teachers 16 and 64 the ungated
  network was better, because the gated one never grew at all.
- GR-c True (paired ratios 0.991, 1.001, 1.000). GR-d True (0.971, 1.000, 1.008). GR-e True (0.01547 against 0.11819).
  GR-c and GR-d are close to empty on teachers 16 and 64, since no arm grew there.

What it shows: both failure modes side by side. The gated colony starved (width 2, loss 15 times that of `fixed128` on teacher 16).
The ungated colony bloated (width 474 on every need, loss 6 times that of the gated one on teacher 4, 4 times that of `fixed128` on teacher 16).
Neither is restraint. The gate as built is a wall, not a judge.

Diagnostic (NOT preregistered, `gr1_diag.py`, output `results/gr1-diag-out.txt`): over 48 replayed trials on teachers 16 and 64,
the grown lineage's gate loss was 0.9859 to 1.0781 times the ungrown one (median 0.9992), and the gate needed below 0.98.
After the 300-step trial the child's input weights still had cosine 0.9945 (median) with its parent's.
Reading: a daughter that is a copy of its parent carries no new information, so the gate has nothing to see.
Same pattern at the agent layer: in E13 forced attempts won 4 of 19, and the `dfix1` maze daughter changed nothing
because the parent already held its idea. A lead, not a result.

## GR2 growth pilot: asymmetric division (guesses written 2026-11-10, after GR1, before any GR2 data)
Question: GR1's gate rejected all growth on the larger needs, and the diagnostic points at copy division.
Does the same gate judge well when the daughter differs from the parent?
One change from GR1: how a new neuron is born. Everything else (needs, data, seeds, budget, trial length, 2% gate,
doubling wait, charges) is `grow.py` unchanged. Code `razi-tools/cells/grow2.py`, written before any run.
- New neurons are born different: fresh input weights from the birth distribution, outgoing weight 0, so the
  network's output is unchanged at the moment of division and the parent is untouched. Same count as GR1 (half the width).
- `asym-signal`: 4 candidates per place are drawn blind, and the ones whose activity lines up best with the
  network's current error on the training rows are kept. Blind variation, then a signal picks.
- `asym-random`: the first candidates are kept without looking.
- `nogate-asym`: `asym-signal` growth with the gate always saying yes.
- Reference arms: `gate-signal` (GR1 copy division), `fixed128`, `fixed-same` (born at the width `asym-signal` reached).
- Reading the signal is charged one pass over the training rows at the size of the network plus all candidates.

Guesses:
- GR2-a: the median final width of `asym-signal` rises with the need: teacher 4 < teacher 16 < teacher 64.
- GR2-b: `asym-signal` beats copy division (`gate-signal`) on teachers 16 and 64, median paired loss ratio below 0.5 on both.
- GR2-c: restraint. On teacher 4 the median final width of `asym-signal` is 8 or less.
- GR2-d: `asym-signal` and `asym-random` are within 10% (median paired ratio 0.9 to 1.1) on at least 2 of 3 needs.
- GR2-e: `asym-signal` does not beat `fixed-same` by more than 10% on any need, and `fixed128` still beats it on teacher 64.
- GR2-f: `nogate-asym` has a higher median test loss than `asym-signal` on teacher 4.

### GR2 result (2026-11-10, `grow2.py` sha256 ba623d30e254388d run unchanged, output `results/gr2-out.txt`, rows `results/gr2-rows.json`)
10 seeds, 3 needs, 6 arms, 1m34s on the laptop CPU, no model calls.

| Teacher | asym-signal | asym-random | nogate-asym | gate-signal (copy) | fixed128 | fixed-same |
|---|---|---|---|---|---|---|
| 4, median test loss | 0.00091 | 0.00084 | 0.00322 | 0.00089 | 0.00482 | 0.00087 |
| 4, median width | 6 | 6 | 316 | 3 | 128 | 6 |
| 16, median test loss | 0.00229 | 0.00273 | 0.00527 | 0.09556 | 0.00621 | 0.00369 |
| 16, median width | 23.5 | 28 | 316 | 2 | 128 | 23.5 |
| 64, median test loss | 0.01430 | 0.01402 | 0.01788 | 0.11819 | 0.01547 | 0.01301 |
| 64, median width | 63 | 63 | 316 | 2 | 128 | 63 |

Guesses, judged as written:
- GR2-a True. Median width 6, 23.5, 63 for needs 4, 16, 64.
- GR2-b True. Paired loss ratio against copy division 0.024 (teacher 16) and 0.115 (teacher 64).
- GR2-c True. Median width 6 on teacher 4 (range 3 to 9).
- GR2-d True. Signal against random 1.098, 0.759, 0.915. Two of three inside 10%. On teacher 16 the signal arm was 24% better.
- GR2-e False, on both halves. The grown network beat a network born at the same width by 34.5% on teacher 16
  (ratio 0.655; 0.978 and 1.085 on the others), and it beat `fixed128` on teacher 64 by median (0.01430 against 0.01547).
- GR2-f True. Ungated growth 0.00322 against 0.00091 on teacher 4.

Reading (a lead from one toy problem, 10 seeds, not a result):
- The same gate that starved the colony in GR1 sized it to the need in GR2. The one change was that daughters are born different.
- Restraint and growth came from one rule. No arm was told how big to be.
- Ungated growth went to width 316 on every need and lost on every need (ratios 0.296, 0.425, 0.817).
- Blind proposals were about as good as signal-picked ones. The gate did the selecting. The gradient did the fitting.
- Not shown: that growth beats a well-chosen fixed size. `fixed-same` gets its width from the grown arm for free.
  The fair claim is that the gated colony found a good size without being told, at no loss against that size on 2 of 3 needs.
- Limits: tanh teacher-student regression, 8 inputs, one hidden layer, one learning rate, one margin, one trial length, numpy on CPU.

## GR3 robustness of GR2 (guesses written 2026-11-10, after GR2, before any GR3 data)
Question: does the GR2 picture (the gate sizes the network to the need, ungated growth bloats) survive when the knobs
I picked by hand are moved, and on a second kind of task? Code `razi-tools/cells/grow3.py`, written before any run,
imports `grow.py` and `grow2.py` unchanged.
- Six settings, one knob moved at a time from GR2: gate margin 0.005 and 0.08 (GR2 0.02), trial length 100 and 1000
  steps (GR2 300), learning rate 0.002 and 0.02 (GR2 0.005).
- Second task `sin`: the teacher is a sum of sine units instead of tanh units (needs 4, 16, 64), GR2 settings.
- Arms per setting: `asym-random` (blind proposals, GR2 showed the signal adds little), `nogate-asym`,
  `fixed-same` (born at the width `asym-random` reached). 10 seeds, same budget.

Guesses:
- GR3-a: median width of `asym-random` rises with the need (4 < 16 < 64) in at least 5 of the 6 settings.
- GR3-b: restraint holds: teacher 4 median width is 8 or less in at least 4 of the 6 settings. I expect margin 0.005 to break it.
- GR3-c: ungated growth has a higher median test loss than gated growth on teacher 4 in all 6 settings.
- GR3-d: on the `sin` task, width rises with the need and ungated growth is worse than gated on need 4.
- GR3-e: the GR2 surprise (grown beats a network born at the same width by more than 10% on teacher 16) repeats
  in at least 3 of the 6 settings.

### GR3 result (2026-11-10)
`grow3.py` (sha256 a11897170fb15172) run unchanged, 10 seeds, 7 settings, 3 arms, 630 rows, 3m41s, no model calls.
Output `results/gr3-out.txt` (sha256 1de5e7c66cd7fce6), rows `results/gr3-rows.json`. Medians over seeds.

| Setting | Gated width at need 4 / 16 / 64 | Gated / ungated loss 4 / 16 / 64 | Grown / born-same loss 4 / 16 / 64 | Ungated width |
|---|---|---|---|---|
| margin 0.005 | 13 / 52.5 / 141 | 0.269 / 0.549 / 0.809 | 0.651 / 0.604 / 0.993 | 474 |
| margin 0.08 | 4 / 13 / 23.5 | 0.152 / 0.568 / 1.351 | 1.004 / 0.910 / 1.114 | 474 |
| trial 100 | 9 / 19 / 52.5 | 0.131 / 0.215 / 0.367 | 0.903 / 0.943 / 0.994 | 1599 |
| trial 1000 | 4 / 19 / 63 | 0.177 / 0.563 / 1.162 | 0.776 / 0.739 / 1.196 | 141 |
| lr 0.002 | 9 / 19 / 63 | 0.218 / 0.251 / 0.735 | 0.976 / 0.923 / 1.162 | 474 |
| lr 0.02 | 6 / 28 / 94 | 0.103 / 0.207 / 0.568 | 1.130 / 0.827 / 1.003 | 474 |
| sin task | 7.5 / 23.5 / 4.5 | 0.851 / 0.906 / 1.402 | 1.086 / 0.924 / 1.015 | 474 |

Guesses, judged as written:
- GR3-a True. Width rises with the need in 6 of 6 settings.
- GR3-b False. Teacher 4 width is 8 or less in 3 of 6 settings, I guessed at least 4. Margin 0.005, trial 100 and
  lr 0.002 broke it (widths 13, 9, 9). I expected only margin 0.005 to break it.
- GR3-c True. Ungated growth is worse than gated on teacher 4 in 6 of 6 settings (ratios 0.10 to 0.27).
- GR3-d False on both halves. On the sin task width does not rise (7.5, 23.5, 4.5). Ungated is not worse on need 4 by
  the test the script applies (arm medians: gated 0.08847, ungated 0.07649). The paired ratio in the table (0.851) points
  the other way, so on sin need 4 the two arms are not separable.
- GR3-e True, at the edge. Grown beats born-same by more than 10% on teacher 16 in exactly 3 of 6 settings.

What holds: sizing to need (6 of 6) and the cost of ungated growth on a small need (6 of 6).
What does not hold:
- The exact amount of restraint depends on the knobs. A loose gate or a short trial lets a small need grow to 9 or 13.
  The order still holds, the size does not.
- A strict gate (margin 0.08) or a long trial (1000) under-grows the big need: gated is worse than ungated on teacher 64
  (1.351, 1.162). Restraint has a price when the need is large.
- The sin task at need 64 breaks the picture: median width 4.5, 3 of 10 seeds never won a trial.

Diagnostic, NOT preregistered (share of the clean target's variance left unexplained, medians): sin need 4: gated 0.22,
ungated 0.20, born-same 0.19. Need 16: 0.22, 0.26, 0.25. Need 64: gated 0.80, ungated 0.52, born-same 0.81.
So at sin need 64 nobody learns the task inside the budget, and the gated arm learns least. Reading: when a small step
of growth buys no measurable gain, the gate says no and the network stays small. The gate cannot tell "enough" from
"too hard to see progress yet". This is the same failure as GR1 (no visible signal, no growth), reached from the other side.

Status: pilot scale (toy network, laptop). Leads, not results.

## GR4 two ways to tell "satisfied" from "stuck" (guesses written 2026-11-10, after GR3, before any GR4 data)
Question. GR3 showed a fixed gate reads "one step of growth did not help" as "enough", and under-grows a hard need.
Two candidate laws fix this in different ways. Which one holds across easy, hard and noisy needs?
- Law `level` (a sensor): the network reads its own unmet need, u = gate loss / variance of the gate targets
  (the share left unexplained). The margin a growth step must clear is MARGIN * (1 - u / U0), U0 = 0.25. High need
  makes the gate loose, and above U0 growth is kept unless it is clearly worse. Low need makes it strict.
- Law `escal` (blind, by acting): the gate stays fixed. After each refused growth step the next step is twice as big
  (base step * 2^rejects, at most 16 times the base step). A kept step resets it. "No gain from a small step" is
  only believed after bigger steps also show none.
Same in all arms: blind candidates (GR2 `asym-random` rules), MARGIN 0.02, TRIAL 300, LR 0.005, budget 5,128,000,
10 seeds. `grow.py`, `grow2.py`, `grow3.py` imported unchanged.
Arms: `base` (GR2 fixed gate), `level`, `escal`, `nogate` (GR3 ungated blind growth).
Conditions (8): tanh teacher 4, 16, 64 (noise 0.1). Sin teacher 4, 16, 64 (noise 0.1). Noisy tanh teacher 4 and 16
(label noise 0.5). The noisy pair is a trap for `level`: the noise alone should keep u near U0, so the sensor reads
noise as need.
Outcomes. Test loss against the clean teacher (lower is better), final width, and regret: for each condition and seed,
an arm's test loss divided by the lowest test loss among the four arms. Medians over seeds.
Disclosure. I have seen all GR1 to GR3 data, including the sin shares (0.2, 0.2, 0.8). U0 was picked knowing them.
Guesses:
- GR4-a. On sin 64 both `level` and `escal` beat `base`: paired median loss ratio below 0.9 for each.
- GR4-b. Nothing is lost where the fixed gate worked. On tanh 4, 16, 64 the paired median ratio to `base` is inside
  0.8 to 1.25 for `level` on all 3, and for `escal` on at least 2 of 3.
- GR4-c. The trap works. On noisy tanh 4, `level` ends more than twice as wide as `base` (median width), and
  `escal` does not.
- GR4-d. `escal` has the lowest worst-case regret (largest median regret over the 8 conditions) of the four arms.
  Low confidence: `base` is already hard to beat on this measure.
- GR4-e. Under `escal` width still rises with need on tanh (4 < 16 < 64, median width).
Pilot scale. No model calls.

### GR4 result (2026-11-10)
Run: `grow4.py run results/gr4-rows.json --seeds 10 --par 8`, unchanged from the code written before the run
(sha256 a12329838d1faf3b, copy in `archive/grow4_v1_gr4.py`). 2m12s, 320 rows, no model calls. Output
`results/gr4-out.txt` (sha256 dc1cbcd8f8ddef50). Every arm spent between 5,125,922 and 5,128,000 units.

| cond | width base/level/escal/nogate | test loss base/level/escal/nogate | level/base | escal/base | regret base/level/escal/nogate |
|---|---|---|---|---|---|
| tanh4 | 6 / 6 / 6 / 474 | 0.00084 / 0.00084 / 0.00087 / 0.00505 | 1.000 | 1.048 | 1.00 / 1.00 / 1.05 / 6.15 |
| tanh16 | 28 / 28 / 25 / 474 | 0.00273 / 0.00261 / 0.00251 / 0.00520 | 1.000 | 0.983 | 1.09 / 1.02 / 1.00 / 2.02 |
| tanh64 | 63 / 78.5 / 77.5 / 474 | 0.01402 / 0.01370 / 0.01376 / 0.01659 | 1.000 | 1.025 | 1.00 / 1.00 / 1.04 / 1.27 |
| sin4 | 7.5 / 35 / 36 / 474 | 0.08847 / 0.02451 / 0.03447 / 0.07649 | 0.418 | 0.465 | 3.02 / 1.00 / 1.21 / 3.45 |
| sin16 | 23.5 / 94 / 84.5 / 474 | 0.13347 / 0.11622 / 0.11573 / 0.14434 | 0.956 | 1.001 | 1.09 / 1.06 / 1.08 / 1.26 |
| sin64 | 4.5 / 211 / 104 / 474 | 0.38187 / 0.29370 / 0.30976 / 0.28010 | 0.780 | 0.797 | 1.42 / 1.04 / 1.09 / 1.00 |
| noisy4 | 3.5 / 30.5 / 4 / 474 | 0.00804 / 0.05281 / 0.01225 / 0.08859 | 6.670 | 1.236 | 1.06 / 6.67 / 1.42 / 11.95 |
| noisy16 | 9 / 94 / 9 / 474 | 0.03849 / 0.08852 / 0.04160 / 0.10195 | 2.061 | 1.001 | 1.01 / 2.18 / 1.01 / 2.92 |

Worst-case median regret: base 3.02, level 6.67, escal 1.42, nogate 11.95.

Guesses, judged as written by the script (5 of 5 held):
- GR4-a True. On sin 64 both laws beat the fixed gate: ratios 0.780 (`level`) and 0.797 (`escal`).
- GR4-b True. Nothing lost on tanh: `level` 1.000, 1.000, 1.000. `escal` 1.048, 0.983, 1.025.
- GR4-c True. The trap worked. Noisy 4: width base 3.5, `level` 30.5, `escal` 4. The sensor read label noise as unmet
  need, grew about 9 times too wide and lost 6.7 times the loss. On noisy 16 the same: width 94 against 9, loss 2.06 times.
- GR4-d True. `escal` has the lowest worst-case regret, 1.42. Its worst condition is noisy 4.
- GR4-e True. `escal` width still rises with need on tanh: 6, 25, 77.5.

Diagnostic, NOT preregistered (per-seed view of `results/gr4-rows.json`):
- Seeds out of 10 where the arm had lower test loss than `base`: sin4 level 8, escal 8. sin16 level 7, escal 5.
  sin64 level 8, escal 7, nogate 9. noisy4 level 1, escal 4. noisy16 level 0, escal 5.
- On tanh `level` is the same network as `base` on 9, 7 and 5 seeds of 10 (need 4, 16, 64): where the need is nearly
  met the sensor changes nothing.
- Median kept growth steps base/level/escal: sin64 2 / 12 / 4.5. noisy4 1.5 / 7 / 1.
- `escal` width range over seeds is wide: tanh4 4 to 54, sin4 13 to 217. A doubled step that happens to pass the gate
  is kept whole, so single seeds overshoot. The median hides this.
- On sin 64 the ungated arm has the lowest median loss of all four (0.28010). When the need is far beyond reach, restraint
  costs. Neither law reaches it: `level` 1.04 and `escal` 1.09 times the best.

Reading.
1. The blind spot found in GR3 is real and both laws remove most of it. On the two sin needs where the fixed gate got
   stuck (4 and 64) both laws cut the loss by 20 to 58%.
2. The two laws fail differently. The sensor is best when its reading is true (sin 4, sin 64) and worst of all gated arms
   when it is not (noise read as need). The acting law is never best by much and never bad: it does not read need, it
   tests whether a bigger step shows a gain, and noise shows none at any step size.
3. So a sensor of unmet need is only as good as its ability to tell reducible error from irreducible error. From inside,
   one reading cannot tell them apart. Acting can: irreducible error does not move when you grow.
4. Status: pilot scale (toy network, laptop). Leads, not results. One hand-picked U0 (chosen after seeing GR3 shares) and
   one escalation rule. Not yet moved knob by knob as GR3 did for GR2.

## Stem pilot SP1: one uncommitted cell feeds committed cells (guesses written 2026-11-10, before any stem data)
Source ideas: IDEAS J4a to J4e, K3, K8, tests T-J1 and T-K1. Code: `stem.py` (sha256 75d3cda284926c16),
`metab.py` (b80767b6fc2f2edb, heir and wake are opt-in, flat behaviour unchanged), `stem_report.py` (9dc87bdc82614bda).
Checked offline with scripted acts and the real bench before any model call (`/tmp/stem_offline.py`: energy conserved,
rest returns energy to the stem, a fed resting cell wakes with its body and first baseline).

Question. Flat colonies are born committed, one cell per part with 400 energy each, and nothing tells a cell that
need remains. Cells quit after the first passing answer (E11 to E13, mp2). Does a stem cell that holds the same total
energy (1600), sees the state of every part, and can feed a resting cell again, get more out of the same energy?

Arms, same kits (`needs4k.json`), same laws, same prices, same reward, law "rest":
- stem: `run_stem.sh`. Runs sp1, sp2.
- flat: `run_metab.sh` on the same `metab.py`. Runs fl1, fl2. (mp2 is the older flat run and is not reused.)
Order: sp0 (smoke, excluded), then fl1, sp1, fl2, sp2, one at a time. Report: `stem_report.py`, run unchanged.

Guesses, judged as written:
- SP-a. The stem births a cell for all 4 parts before its first `wait`, in both runs.
- SP-b. The stem splits evenly at birth: largest birth feed is under 1.5 times the smallest, in both runs.
  (I expect a fair split, not a judgement of need. If false, the stem is already reading the parts.)
- SP-c. At least one wake (a resting or dead cell fed again) in at least 1 of 2 runs.
- SP-d. At least one adopted improvement after a wake in at least 1 of 2 runs.
- SP-e. Mean over runs of the median final_gain across the 4 parts: stem above flat.
- SP-f. Restraint: the stem ends holding more than 25% of the 1600 it was born with, in both runs.
- SP-g. Cost: stem arm total tokens are under 2 times the flat arm total tokens.
- SP-h. No daughter of a committed cell (`divide`) in either arm. (0 of 12 so far.)

Limits stated before data: 2 runs per arm is a pilot. Leads, not results. Excluded from any pooled analysis.
T-J1 also asks for one strong agent at equal tokens. That arm is not in SP1. It comes only if SP1 shows the stem
does anything the flat colony does not.

### SP1 smoke log (2026-11-10, sp0, excluded from analysis)
sp0 ran clean: 35 calls, 90,635 tokens, 0 bad replies, 0 errors, 50 s, energy conserved (1600 born, 771.5 spent,
828.5 left with the stem). Seen before the real runs, nothing changed after it: code hashes and guesses stay as above.
What sp0 showed (one run, not evidence): 4 births before the first wait, birth feeds 300/200/150/150, no wake,
0 improvements, and the stem rested as soon as all four cells rested at +0%.

### SP1 result (2026-11-10, `stem.py` 75d3cda284926c16, `metab.py` b80767b6fc2f2edb, `stem_report.py` 9dc87bdc82614bda, all run unchanged)
Output `results/sp1-out.txt`, logs `results/sp1-{fl1,sp1,fl2,sp2}.log`. Order as written: fl1, sp1, fl2, sp2. All four rc 0.
Pilot scale (2 runs per arm, 4 parts, one model family). Leads, not results.

| run | arm | gains (compress, fibmod, csvsum, maze) | median | improvements | calls | tokens | usd | energy spent | earned |
|---|---|---|---|---|---|---|---|---|---|
| fl1 | flat | 0.0, 0.0139, 0.0322, 0.3474 | 0.0231 | 1 | 27 | 67,298 | 0.0524 | 739.2 | 125.9 |
| fl2 | flat | 0.0, 0.0647, -0.0007, 0.0099 | 0.0050 | 1 | 28 | 69,925 | 0.0254 | 477.4 | 21.9 |
| sp1 | stem | 0.0, 0.0137, 0.1443, 0.2926 | 0.0790 | 2 | 40 | 103,397 | 0.0692 | 1011.4 | 137.8 |
| sp2 | stem | 0.0, 0.0252, 0.7281, 0.4354 | 0.2303 | 1 | 47 | 129,751 | 0.0618 | 994.1 | 232.5 |

Guesses, judged as written:
- SP-a True. 4 parts born before the first `wait` in sp1 and in sp2.
- SP-b False. Birth feeds were 300/150/150/150 (ratio 2.0) and 300/200/200/200 (ratio 1.5, not under 1.5).
  The stem gave compress double and started it on the mid model, both runs and the smoke run. It was reading the parts.
- SP-c True. 2 wakes in sp1 (csvsum twice), 2 wakes in sp2 (maze, compress).
- SP-d True. sp1 csvsum adopted a +12.4% variant after its first wake. sp2 had 0 adopted improvements after a wake.
- SP-e True. Mean of the run medians: stem 0.1547, flat 0.0140. Read the diagnostic below before leaning on this.
- SP-f True. The stem ended holding 726.5 (45%) and 912.8 (57%) of 1600.
- SP-g True. Stem arm 233,148 tokens, flat arm 137,223, ratio 1.70 (usd ratio 1.68, energy spent ratio 1.65).
- SP-h True. 0 divides in 16 committed cells. Now 0 of 28 across all metabolism pilots.
7 of 8 held.

What the stem did (from `stem/log.jsonl`):
- 3 of 4 wakes went to a part sitting at +0%. In sp1 it passed over maze (+26%) to wake csvsum (+0%). In sp2 it left
  csvsum (+79%) alone and woke maze and compress (both +0%). Energy went to unmet need, not to the winner.
- Every wake carried a concrete technical note ("read sys.stdin.buffer whole", "raw LZMA2 filter chain") and 3 of 4
  wakes raised the cell's model or effort. The stem acted as a signal engine for cells that had stopped.
- It rested with 45% and 57% of the energy unspent while fibmod sat at +1% and +3% in both runs. The stem never
  woke it. From the stem's seat a part with nothing left to find and a part where nothing was tried look the same.
  CORRECTION 2026-11-10: this entry first said fibmod "has the largest known headroom (the offline scripted body gets
  +975%)". That was wrong. The +975% is measured from a starting body made slow on purpose in `/tmp/metab_offline.py`
  (each answer computed 12 times). All four SP1 colonies wrote fast doubling, the same method as the reference body,
  and ended within 8% to 14% of it. Whether fibmod has headroom beyond that is not known.
- Flat cells stopped with 66% to 75% of their own energy unspent (7 of 8 cells). The leftover pooled in the last cell
  to rest (986.7 and 1144.4) and was never used. The flat colony has no way to spend it on a part that still has need.

Instrument faults found, not fixed before the run (so SP1 stands as run):
1. Energy debt. sp2 compress ended at -74.4 and sp1 csvsum at -1.6. A woken cell on the mid model pays for a fresh
   cache write of its whole prompt (115.5 and 108.9 units for two steps on 150 energy). `affordable()` caps output only
   and under-counts input, so Law 1 (no credit) leaked. The 64-token output floor then produced the one bad reply.
   Books still balance (born + earned - spent = held, 838.4 in sp2) but 74.4 of that was credit.
2. The gain metric is not comparable across these arms. See diagnostic.

DIAGNOSTIC, not preregistered (`sp1_diag.py` 3bd14200bcabfd8c, written after the data, output `results/sp1-diag-out.txt`):
- Median final_gain at each cell's first stop: sp1 0.0069, sp2 0.0190, against flat 0.0231 and 0.0050. Before any wake
  the stem arm was level with flat. All of the stem arm's edge on SP-e came after wakes (csvsum +0.2113, maze +0.4226).
- Absolute kit score at the end (higher is better), flat mean against stem mean: compress 6.278 / 5.474, fibmod
  2.664 / 2.550, csvsum 1.928 / 2.043, maze 3.741 / 3.392. Ratio stem over flat 0.87, 0.96, 1.06, 0.91.
  In absolute terms the stem arm did not end ahead. It ended level or slightly behind on 3 of 4 parts.
- Why the two views differ: stem-born cells started lower. sp2 csvsum's first baseline was 1.093 against about 1.9
  elsewhere, and its +73% landed at 1.888, the flat level. sp2 maze started at 2.368 and reached 3.399 by a rewrite
  after the wake, inside the flat range (3.485, 3.996). The stem births cells on the light model with 150 to 200
  energy. Flat cells start on mid with 400. A weaker first body makes a larger gain from the same end point.
- compress: fl1 found the 7.082 body, the other three runs the 5.47 body. That is the known two-level baseline, a
  choice made at the first write, not an effect of the arm.
- Stem's own thinking: 27% and 23% of all tokens in its run (cache reads included).

Reading, at pilot scale:
1. The wake works as a mechanism. A stopped cell fed again with a note did find more (2 of 4 wakes moved the score,
   by +0.21 and +0.42 in gain). A flat colony cannot do this at all.
2. SP-e as written is true but is not evidence the stem colony builds better bodies. Gain measured from a cell's own
   first baseline rewards a poor start. Any arm that changes who writes the first body breaks the metric.
3. The stem repeats the K8 fault one level up. It quits on a part once feeding it stops paying, and cannot tell
   "nothing left" from "nothing tried". GR4's escalation law is the candidate fix to carry over.
   (Corrected 2026-11-10: fibmod was named here as the "nothing tried" case. There is no evidence it had headroom,
   see the correction above. What stands: the stem never tested fibmod with a stronger try, so it could not know.)
Next instrument rule: score every part against a fixed reference body per kit, so arms are compared on where they
end, not on how far they moved. Then SP2 on that metric with the debt hole closed.

DIAGNOSTIC 2, not preregistered (`refscore.py` 3937690f190b67df, written after the SP1 data, output `results/sp1-ref-out.txt`,
rows `results/sp1-ref.json`). Every final body rescored against one fixed reference body per kit (the plain stdlib
bodies of `kit_selftest.py`), all five contenders measured together, interleaved, 5 repeats, no model calls.
rel = body score / reference score.

| kit | fl1 | fl2 | sp1 | sp2 |
|---|---|---|---|---|
| fibmod | 1.083 | 1.141 | 1.084 | 1.081 |
| csvsum | 1.430 | 1.325 | 1.512 | 1.510 |
| maze | 3.193 | 2.787 | 2.843 | 2.833 |
| compress | 1.542 | 1.192 | 1.192 | 1.192 |
| median | 1.486 | 1.258 | 1.352 | 1.351 |

Mean of run medians: flat 1.372, stem 1.352. On where the bodies ended, the arms are level. The stem arm is ahead on
csvsum in both runs, behind on maze against fl1, level on fibmod. The SP-e gap (0.1547 against 0.0140) does not
survive a fixed yardstick. The stem arm paid 1.70 times the tokens to end in the same place.
Also visible: on fibmod every colony in both arms wrote the same method as the reference (fast doubling) and ended
within 8% to 14% of it. On compress 3 of 4 colonies ended on the same score (1.192, plain lzma), and fl1 found
something better (1.542). So on two of four kits the colonies mostly sit at the first standard answer, and the
spread between runs of one arm (compress 1.192 to 1.542 in flat) is larger than the gap between arms.

### K13 fix: a thought is paid for before it is had (2026-11-10, `metab.py` 08c80bf66a70a5d8, `stem.py` 8ffe3d4f79bc1c3b)

Fault (SP1): the cap on a thought counted only the reply. The input side (system text, tool list, history, cache
writes) was not counted, so a woken cell on the mid model paid about 110 to 190 for one step and two cells ended in
debt (-74.4, -1.6).
Change: before each call the cell estimates the input cost (first call on a model: every token priced as a cache
write, the dearest case. Later calls: its own last measured rate with a margin). The call is allowed only if energy
covers the living cost, that estimate, and room for a 64 token reply. If the chosen model cannot be paid for, the cell
thinks with the dearest model it can pay for and is told so. If it can pay for none, it dies ("cannot pay for a
thought"). A step that still costs more than the cell holds is logged as `overdraft`.
Checks, none of them analysis data:
- Offline, no model call (`cells/tests/debt_offline.py`): 6 scripted cases, both with a given cost and with the cost
  priced from tokens. 0 overdrafts in 6 of 6. `metab_offline.py` and `stem_offline.py` still pass, energy conserved.
- Live smoke `sp2smoke` (stem colony, excluded from analysis): 39 priced steps, 0 overdrafts, lowest energy 0.0,
  1 downshift (csvsum mid to light at 32.5), 1 death by the new rule (csvsum at 11.4). Cost minus estimate ran from
  0.4 to 50.2, largest on a stem mid call, so the estimate is loose but stayed on the safe side of zero here.
- Books for `sp2smoke`: the stem was born with 1600, the colony earned 230.5 and spent 989.2, and 841.3 is held at
  the end. 1600 + 230.5 - 989.2 = 841.3, so energy is conserved. (The ledger's `born` column sums to 2500 because the
  900 fed at birth shows as born on the parts and as gave on the stem.)

### Ceiling per kit, fixed before SP2 (2026-11-10, `refscore.py` 3937690f190b67df, `results/ceiling-ref.json` 533d4db5907f8c8d)

Every final body from 29 earlier runs (E13, kit pilots, metab pilots, SP1, smokes) scored in one session against the
reference body. rel = body / reference. No model calls. Reference spread in this session: fibmod 7.7%, csvsum 3.6%,
maze 9.5%, compress 0.0%. Bodies scored: fibmod 29, csvsum 27, maze 28, compress 27 (the rest had no body).

| kit | ceiling rel | run | median rel over runs | runs at 2x or more |
|---|---|---|---|---|
| fibmod | 5.510 | kp_ch | 1.733 | 6 of 29 |
| csvsum | 1.703 | mp3 | 1.183 | 0 of 27 |
| maze | 3.272 | fl1 | 2.924 | 28 of 28 |
| compress | 1.542 | mp3 and 6 others | 1.197 | 0 of 27 |

Reading, DIAGNOSTIC, not preregistered:
- fibmod headroom is now a measured fact, not a guess. A body 5.5 times the reference exists (kp_ch, three lookup
  tables over the reduced index, one multiply step per input). Five runs are at 4.49 or above, four from the older
  rule-driven runtime and one a single-cell smoke on the energy laws (msmoke1, 5.370, whose own-baseline gain was
  only 0.072: its first body was already fast, which is the K12 point again). Every energy-law colony run (mp1 to mp3, fl1, fl2, sp0 to sp2, sp2smoke)
  ended between 1.07 and 1.97 on fibmod. This corrects the correction above: SP1 colonies did stop far short of what
  was reachable on fibmod, and the evidence is a scored body, as the K14 rule asks.
- compress has two levels only (1.197 and 1.542). maze is at 2.4 or more in every run, so the reference body is weak
  there and maze says little about arms.

## SP2 (T-K2): stem against flat on the fixed-reference metric (guesses written 2026-11-10, before any SP2 data)

Question: with the debt hole closed and scores taken against one fixed reference, does a colony fed by one stem cell
end with better bodies than a flat colony with the same total energy, and how much of any difference is only the
model each part is born on?

Arms, 4 runs each, 12 runs, one at a time, order fixed: s2f1 s2s1 s2m1, s2f2 s2s2 s2m2, s2f3 s2s3 s2m3, s2f4 s2s4 s2m4.
- f, flat: 4 parts, 400 energy each, every part born on mid (`run_metab.sh`, `needs4k.json`).
- s, stem: one stem holds 1600, feeds parts as it chooses, gets unspent energy back, may wake parts (`run_stem.sh`).
- m, flat with stem birth models: 4 parts, 400 each, compress born on mid and the other three on light, which is what
  the stem chose at birth in 4 of 4 earlier stem runs (`needs4k_stembirth.json`). Same total energy as f and s. It
  separates the birth model from the stem's feeding and waking. It does not copy the stem's smaller birth feeds.
Same kits, law "rest", laws and prices as SP1 plus the K13 fix. Files: `metab.py` 08c80bf66a70a5d8, `stem.py`
8ffe3d4f79bc1c3b, `colony.py` d38c5eb291fe9e21, `cell.py` dc076bff25472f5e, `kit.py` 8c9a544aea86a7e8,
`run_sp2.sh` e789390e01f9d097, `needs4k_stembirth.json` dfdce996fd605077.
Analysis: after all 12 runs, `refscore.py` scores all final bodies in one session, then `sp2.py` (4726fc281051a899,
written before data, run unchanged) with the ceiling file above.
- O1, primary: per run the median rel over the 4 parts. Arm value is the mean of its 4 run medians.
- O2: share of the gap from reference to ceiling per part, arm mean.
- O3: cost (calls, tokens, energy spent). O4: law record (lowest energy, overdrafts, downshifts, deaths, divides).
- The cell-level shuffle test in `sp2.py` overstates n (cells in a run are not independent). Direction and size per
  part carry the reading. A part with no body or a wrong body scores 0.
"Level" below means the two arm values differ by less than 0.10.

Guesses:
- S2-a (law holds): across the 12 runs at most 2 `overdraft` events, and no cell ends below -20.
- S2-b (primary): s and f are level on O1.
- S2-c: m and f are level on O1, and arm m spends less than half the energy arm f spends.
- S2-d: arm s uses at least 1.3 times the tokens of arm f (SP1: 1.70).
- S2-e (stem behaviour repeats): in at least 3 of 4 s runs compress gets the largest birth feed. At least 3 of 4 s
  runs have a wake. More than half of all wakes go to a part whose own gain was 0.03 or less when it last stopped.
- S2-f: 0 divides in all 12 runs.
- S2-g: fibmod rel reaches 2.0 in at most 2 of the 12 runs.
- S2-h: O2 mean share of gap is between 0.35 and 0.65 in every arm.

What each outcome would mean, fixed now:
- s above f by 0.10 or more on O1 with 3 of 4 parts positive: the stem's feeding adds something, look at which wakes.
- s and f level with S2-d true: the stem as built costs more for the same end. The next lever is not more feeding, it
  is what a part does with a second chance (K11, the escalation law from GR4).
- m level with f at under half the energy: the birth model is the cheap lever and mid at birth is waste on these kits.
- m below f by 0.10 or more: the first body matters, and the stem's light births cost it.
Status: 4 runs per arm on 4 uneven kits. Leads, not results.

### SP2 result (2026-11-10)

All 12 runs finished with rc 0 in the fixed order. `refscore.py` scored the 48 final bodies in one session
(`results/sp2-ref.json` efbd868836b4a278, reference spread fibmod 2.1%, csvsum 6.9%, maze 2.2%, compress 0.0%).
`sp2.py` 4726fc281051a899 ran unchanged (`results/sp2-out.txt` b731ad3d9effc3b9). File hashes matched the
preregistration before scoring.

| arm | O1 (mean of run medians) | run medians | O2 share of gap | calls | tokens | energy spent | imps |
|---|---|---|---|---|---|---|---|
| f flat, born mid | 1.5775 | 1.281, 2.060, 1.378, 1.591 | 0.412 | 107 | 262,925 | 2432.8 | 6 |
| s stem | 1.4713 | 1.360, 1.557, 1.621, 1.348 | 0.528 | 158 | 424,217 | 3118.4 | 7 |
| m flat, stem birth models | 1.5461 | 1.340, 1.719, 1.735, 1.391 | 0.493 | 107 | 283,752 | 1591.1 | 7 |

Part mean rel (f / s / m): compress 0.983 / 1.280 / 1.193, fibmod 1.511 / 1.301 / 1.552, csvsum 1.514 / 1.488 /
1.503, maze 2.896 / 2.895 / 2.768. Cell-level shuffle tests: p 1.0 (f against s), 0.88 (f against m), 0.82 (s against m).

Guesses, judged as written (6 of 8 held):
- S2-a True. 1 overdraft in 12 runs (s2f1 compress, cost 104.4 against 104.3 held), lowest energy -0.1.
- S2-b False. f is above s by 0.1062, just past the 0.10 line. The stem arm is not ahead.
- S2-c False. m and f are level (0.0314 apart), but m spent 0.65 of f's energy, not under half.
- S2-d True. Stem arm used 1.61 times the tokens of flat (SP1: 1.70) and 1.28 times the energy.
- S2-e True. Compress got the largest birth feed in 4 of 4 runs (300 on mid). 4 of 4 runs had a wake. 4 of 5 wakes
  went to a part whose own gain was 0.03 or less.
- S2-f True. 0 divides in 12 runs.
- S2-g True. fibmod rel reached 2.0 in 1 of 12 runs (s2f2, 2.754).
- S2-h True. O2 means 0.412, 0.528, 0.493.

Reading against the outcomes fixed beforehand: the stem's feeding adds nothing to the end bodies and costs more.
None of the "stem helps" or "first body matters" outcomes occurred. This is the second run of the same answer (SP1,
then SP2 on the fixed-reference metric with the debt hole closed).

DIAGNOSTIC, not preregistered (`sp2_diag.py` 9d155db006e2beb9, `results/sp2-diag-out.txt` 9788322ecb6a89aa, written
after the report was seen, logs only):
1. The f against s gap is one body. With fibmod left out the arm values are 1.5135 (f), 1.4880 (s), 1.5027 (m).
   s2f2 fibmod alone (2.754, a table of matrix powers by 8-bit chunks) lifts f. In the other direction s2f1 compress
   has no body at all (rel 0): the cell stayed on mid for 4 steps, had a write refused for a path outside its body,
   spent 400.1 and died. With that zero dropped f is 1.6283.
2. Arm m did not test what it was built to test. Cells choose their own model after the first step, and 14 of 16
   mid-born cells in arm f were on light at step 2 (15 of 16 by the end). The first write of the body was thought on light in 46 of 48
   cells (1 on mid, 1 never wrote). All 52 variants rounds in SP2 were thought on light. Heavy was never used, here or in any energy-law run (22 runs: 657 light steps, 94 mid, 0 heavy). So f
   and m differ by one costly first step (first-step cost summed over cells: f 840.5, m 311.8), not by who wrote the
   first body. "Mid at birth is waste" is supported only in that narrow sense.
3. The stem's own thinking was 1096.4 energy, 35% of the arm's spend and 26% of its tokens. Parts alone spent 2022.0,
   between f and m. The stem rested with 48% to 78% of its energy unspent.
4. Wakes: 5 wakes, all on mid, 690 energy given. 3 woken parts took one mid step (95.6 to 119.6) and then thought on
   light. The other 2 were moved to light by the law before their first thought. 1 of 5 wakes produced an improvement (s2s3 maze, +0.4506, thought on light). The other 4 changed
   nothing. One woken part (s2s2 fibmod) died after its wake with its body intact.
5. Variants rounds and wins: f 10 rounds, 6 wins, 6 of 16 cells rested without any round. s 24 rounds, 7 wins, 0
   cells without a round. m 18 rounds, 7 wins, 1 cell without a round. More rounds did not buy more wins.
6. K13 estimate: on light the input estimate is close (median real minus estimate -0.6, largest +1.1). On mid it is
   safe but loose (median -44.2, largest +20.9). The one overdraft was 0.1 units.
7. fibmod reach: the four bodies at 1.89 or above use the Pisano period (3) or chunked matrix tables (1). The
   ceiling body (kp_ch, 5.51) uses both the period and three lookup tables. No SP2 cell got there.
8. Across experiments (different sessions and runtimes, a lead only), median rel per kit: E13 arm c on Sonnet for
   every step has fibmod 1.896 and csvsum 1.016. SP2 arm f has fibmod 1.109 and csvsum 1.524.

What SP2 does and does not show. It shows the three colony shapes end level on body quality, at energy 0.65 (m),
1.00 (f) and 1.28 (s). It does not show that a stronger first body is useless, because no arm produced one.
Status: 4 runs per arm on 4 uneven kits. Leads, not results.

## SP3 (T-K3 and the price question): what a cell is told (guesses written 2026-11-10, before any SP3 data)

Two questions, one design.
1. Price. In every energy-law run so far cells went to the cheapest model at their first act (SP2 f: 14 of 16 at
   step 0, 0 cells ever thought above their birth model). At that moment they had no cost experience. They had the
   price list. Does the choice come from the list, and does it change if cost is only felt?
2. Need (K20, T-K3). Cells rest near 1.1 on fibmod while a body at 5.5 exists. Does one inward number, how the cell's
   body scores against the best recorded body for its need, change how long it works and how far it gets?

Arms, 2 by 2, 4 runs each, 16 runs, one at a time, order fixed: s3a1 s3b1 s3c1 s3d1, then 2, 3, 4.
- a: price list shown, sense not shown. Control, a repeat of SP2 arm f.
- b: price list hidden. The charge is the same. The cell sees its energy and what its own past steps cost.
- c: price list shown, sense shown.
- d: price list hidden, sense shown.
Every arm: flat, 4 parts, 400 energy each, born on mid at effort low, law "rest", `needs4k.json`. Sense is measured in
every arm (3 repeats against the record body, at each assay and each win) and logged. Only c and d see it.
The record bodies in `records/` are the best body per kit from earlier runs (fibmod kp_ch, csvsum mp3, maze s2f2,
compress e13ch2). A cell cannot read them (sandbox check 2026-11-10: `Operation not permitted`). It sees a ratio only.
Change from T-K3 as written: T-K3 named shape m. This uses shape f, because 3 of 4 parts in m are born on light and
the price question needs cells born above light. Both questions then share one control.
New in the log, all arms: a `laws` row per cell (the arm it lived under), the route's reasoning text per step (`why`)
and the reply text (`say`). Neither is shown to any cell.
Known limits, fixed now. The model names stay "light, mid, heavy". The names are a cost hint, so arm b hides the
numbers, not the order. The record body is a ceiling made by this project, not a proof of what is possible. 4 runs per
arm on 4 uneven kits: leads, not results. Pilot first (K19): `run_sp3.sh pilot` runs one b and one c colony (sp3pb,
sp3pc), excluded from the analysis. The pilot must show the `laws` rows match the arm and sense readings appear.
Files: `metab.py` d59dd39c67dc6404, `colony.py` d38c5eb291fe9e21, `cell.py` dc076bff25472f5e, `kit.py`
8c9a544aea86a7e8, `run_sp3.sh` abbc781d1a4037d7, `run_metab.sh` 27b65154c66bb80a, `needs4k.json` 460851ccb5d55a2a,
records fibmod d54313832a011a32, csvsum 25e52ee2043def3e, maze 33627221bdbc8885, compress 653dfe8eb5c972e8.
Analysis: after all 16 runs, `refscore.py` scores all final bodies in one session, then `sp3.py` (8a05f3c73f8eb690,
written before data, run unchanged; part 1 is `sp2.py` 4726fc281051a899 unchanged) with `results/ceiling-ref.json`.
O1 and O2 as in SP2. Behaviour lines B1 to B7 are defined in `sp3.py`. "Level" means two arm values differ by less
than 0.10.

Guesses:
- S3-a (instrument): every cell's `laws` row matches its arm. At least 56 of 64 cells have a sense reading. At most
  2 sense errors and at most 2 `overdraft` events in the 16 runs.
- S3-b (control repeats): arm a, at least 12 of 16 cells choose light at step 0, light is at least 0.70 of steps,
  0 cells think above their birth model.
- S3-c (price list drives the first choice): arm b, at most 8 of 16 cells choose light at step 0.
- S3-d (felt cost teaches the same thing, later): arm b, at least 10 of 16 cells have thought on light by their
  4th step.
- S3-e (hiding the list costs energy and buys nothing): arm b spends at least 1.3 times the energy of arm a, and
  b and a are level on O1.
- S3-f (early stopping is not about price): mean steps after the first assay in arm b is within 1.0 of arm a.
- S3-g (the sensor moves effort): mean steps after the first assay in arm c is at least 1.0 above arm a. At least
  4 of 16 cells in c run 2 or more variant rounds after the first assay, at most 2 of 16 in a.
- S3-h (the sensor moves reach where the gap is large): fibmod rel reaches 2.0 in at least 4 of the 8 sensor runs
  (c, d) and in at most 2 of the 8 runs without it (a, b).
- S3-i (primary): c is above a by 0.10 or more on O1.
- S3-j (escalation appears on its own): cells that move to a dearer model than their previous step after the first
  assay: at most 1 of 16 in a, at least 4 of 32 in c and d together.
- S3-k: 0 divides in all 16 runs.
- S3-l: d is level with c or above it on O1.

What each outcome would mean, fixed now:
- S3-c true, S3-d true: the cheap choice at step 0 is read off the list, and felt cost reaches the same place a few
  steps later. Price is then a fact the cell learns either way, and hiding it only delays the lesson.
- S3-c false: the names alone are enough. Next arm is neutral names (the cell must find out what each one costs and
  what it buys by using it).
- S3-g true, S3-h false: the sensor moves effort but not reach. Next is the escalation law from GR4 (a failed round
  on one model does not count as "no headroom" until a round on the next model up has also failed).
- S3-g false: knowing the gap does not change when a cell stops. Stopping is then set by something else in what the
  cell is told (the rest rule, the reward size), and that is the next thing to vary.
- S3-h and S3-i true: the missing piece was information, not energy and not shape. One inward number is worth more
  than the stem. This would then need a second model family before it is called a result.
- S3-j true: escalation does not need to be a law, it follows from the sensor. S3-j false with S3-g true: cells work
  longer on the same cheap model, which is the K11 failure in a new form.

### SP3 pilot (sp3pb, sp3pc, 2026-11-10). Leads, not results. Excluded from the analysis.

Instrument check (K19), read from the logs by script:
- `laws` rows match the arm in 8 of 8 cells. Sense readings in 7 of 8 cells, 0 sense errors, 0 overdrafts.
  The one cell without a reading (sp3pb fibmod) had its assay refused for spread (21%) with 17.8 energy left, and
  rested. That is the law working, not a fault.
- Reasoning text was logged on 11 of 49 thinking steps: 11 of the 23 steps thought at effort "low", 0 of the 26
  thought at effort "none", which have no reasoning to log.
- Arm b changes what it is named for: with the list hidden the 4 cells thought on mid for 2, 3, 3 and 4 steps before
  going light (one only when it could no longer pay for mid). With the list shown (sp3pc) 3 of 4 went light at step 1
  and the fourth at step 2.
- Arm c changes what it is named for: one cell's reply text (sp3pc fibmod, step 4) cites the reading ("The sense reading says a better body
  exists in the lineage, so I'll try one variant"). 4 of 4 cells in sp3pc ran a variant round, 2 of 4 in sp3pb.
  Every cell that ran a round ran exactly one, then rested.

One fault found in the design, fixed before any arm data. The charge is the real price, and the real price depends on
the provider's prompt cache. Step 0 cost about 82 in sp3pb (cache cold, 0 tokens read) and about 54 in sp3pc (1547
tokens read from the cache sp3pb left behind). In the planned order s3a1 would have paid the cold price alone, about 36
of its 400 energy per cell (35.6 by the token counts at the mid price). Change: `run_sp3.sh full` now runs two warm colonies first (s3w0 as arm a, s3w1 as arm b),
excluded from the analysis, so the first counted run of each prompt form starts warm. Nothing else changed.
`run_sp3.sh` is now 87bc731eef561254 (was abbc781d1a4037d7, kept as `archive/run_sp3_v1_prewarm.sh`). Known limit that stays: cache
state still varies step to step. The log carries cache read and write tokens per step, so it can be checked afterwards.
The guesses above stand as written.

Known limit of S3-j, written before any arm data. The count takes any step thought on a dearer model than the step
before it. In the pilot one cell (sp3pc csvsum) went light, won, then moved back to mid for its last step, and that
step was `rest`. That is a climb by the count and not an escalation of effort. S3-j is still judged as written. A
second readout, J2, is fixed now: the same count, leaving out steps whose act is `rest`. It is printed by
`sp3_j2.py`, written before arm data, and reported beside S3-j.

Hashes before the full run (sha256, first 16): run_sp3.sh 87bc731eef561254, metab.py d59dd39c67dc6404, sp3.py 8a05f3c73f8eb690,
sp3_j2.py 912fbfa871bf6c87, colony.py d38c5eb291fe9e21, sp2.py 4726fc281051a899, refscore.py 3937690f190b67df,
needs4k.json 460851ccb5d55a2a. Pilot runs sp3pb and sp3pc and warm-up runs s3w0 and s3w1 are excluded.

## T-J3 adapter genome pilot (guesses written 2026-11-10, before any T-J3 training)

Question. Do the cell laws (division, then a gate that keeps the better daughter) do anything useful when the
genome is a set of weights and not a folder of code? This is the first test of our own trained weights on data
from real work. GR1 to GR4 were toy curves.

Genome: one LoRA adapter, rank 8, on Inkling 2 Small through Tinker. Experience: every shell command a cell has
run in this project and what the sandbox did with it, from the logs (SP3 runs left out). The adapter reads the
command and must say the result: `ok`, or `fail` plus one of six kinds. Built by `tj3_data.py`, no model calls.
Rows: train 732 (65 runs), gate 174 (12 runs), test 157 (20 runs). Split by run name hash, so gate and test rows
come from colonies the adapter never saw. Exact duplicate commands across splits removed. Share of `ok`: 0.84.

Arms, all from one shared start state, all with 24 optimizer steps, batch 32, learning rate 1e-3:
- gc: one lineage, natural batches, never reloaded.
- gn: one lineage, natural batches, saved and reloaded every 2 steps. This prices the fork itself.
- gb: one lineage, batches forced to half ok and half fail, saved and reloaded every 2 steps.
- s: division with a gate. Each generation two daughters fork from the parent, one trains natural, one balanced,
  2 steps each. The better daughter on the gate rows replaces the parent only if it beats the parent by 2%.
  Same 24 optimizer steps, so 6 generations and a lineage at most 12 steps deep.

Measure: mean over test rows of minus the log probability of the whole right label (nats per row, lower is
better). Reference line: `prior`, a predictor that knows only how often each label occurs in train.
The gate rows are used by arm s to choose. The test rows are never used to choose anything.

Guesses.
- TJ-a. gc ends below `prior` on test. The command text carries some signal about failure.
- TJ-b. gn ends worse than gc on test, and by less than 15%. Reloading resets the optimizer, which costs a little.
- TJ-c. gb ends worse than gn on test. Balanced batches teach the wrong base rate.
- TJ-d. s ends worse than gn on test. At equal optimizer steps the gated lineage is half as deep, and the gate
  cannot buy that back on a task where gradients already know the direction (IDEAS J6).
- TJ-e. In s the gate takes the natural daughter more often than the balanced one, and refuses at least once.
- TJ-f. No arm ends more than 40% below `prior` on test. Most of a failure is not visible in the command alone.

What each outcome would mean. If TJ-d is false (s at or below gn), division plus a gate is worth its cost even
at weight level on this task, against J6, and that needs a rerun before it is believed. If TJ-d holds, the split
"selection picks structure, gradients fill it in" stands, and the next weight level test must give selection a
structural choice (rank, which layers, which data) and not a second copy of the same gradient step.

Order. Pilot first: `tj3.py --gens 2 --arms gc,s --tag tj3p`, excluded from the result, to check the plumbing
and the per step time. Then seeds 0, 1, 2 with all four arms. Judged on the median over the three seeds.
Known limits, written now: one base model, one task, 157 test rows, three seeds. `fail other` is a coarse
label. The spread across seeds is the only noise estimate. This is a lead until repeated.

Hashes (sha256, first 16): tj3.py 00947bd3310997ad, tj3_data.py 7982459de22b7489, tj3/data.json 1233583f918ab255.
Not started until the SP3 run has ended, so the timed bench is not disturbed.

### T-J3 change to the trainer before any training (written 2026-11-10, no T-J3 result exists)

One change to `tj3.py` after the hash above was recorded. No training had been run and `tj3/` held only `data.json`.
What changed: in arm s the batch draw is now keyed by generation times K, not by lineage depth.
Why: with the depth key, a refused generation left depth unchanged, so the next generation drew the same batches from the same parent and would be refused again for the same reason. The gate would then stall on one draw. That is a fault in the instrument, not a behaviour of the law.
What it costs: arm s daughters no longer see the same batches as arm gn at equal depth. The arms still share the start state, the data, the seed and the total number of optimizer steps.
The guesses TJ-a to TJ-f are unchanged and are judged as written.
Old trainer kept as `adapters/archive/tj3_v0_prefix_refusal.py`.
Report script `tj3_report.py` written before any result. It judges each arm on the median final test loss over seeds and prints HELD or MISSED for each guess. Checked only on made up numbers, which were deleted.
Hashes (sha256, first 16): tj3.py 2b39b2676fbddb85, tj3_report.py ce0f3a5ed9bc4cc4, tj3_data.py 7982459de22b7489, tj3/data.json 1233583f918ab255.

### T-J3 R2 instrumentation change (2026-11-11, no new training result). Addresses #111 R2 review.

Change after the hashes above, before any new T-J3 pilot with the revised logger.
What changed in `tj3.py` and `tj3_report.py`:
- Checkpoint TTL default 14400 s and rolling slot names with `overwrite=True`; each arm calls `release_rolling_slot` when the arm ends (vendor `delete_checkpoint` / `delete_state` if present). Whether that frees quota on the free tier is **untested** until a real pilot completes; open question whether `save_state(overwrite=True)` from a new client replaces the prior checkpoint.
- `eval_nll` uses `HOLD_NAME`, which resolves to the **test** split on `tj3_data.py` output.
- Extra forward passes on eval and train are counted in `TOK`.
- One `.jsonl` per OUT file (no shared `tj3.jsonl`); trajectory points keyed by `(tag, seed, arm)` from `event=eval` lines, including gc and the last generation.
Hashes (sha256, first 16): tj3.py 3b42bf37400dc8eb, tj3_report.py 8acfa8a2031d6d27, tj3_data.py 7982459de22b7489, tj3/data.json 1233583f918ab255 (unchanged).

### T-J3 pilot (tj3p, 2026-11-10). A lead, not a result. Excluded from the analysis.

Plumbing check only: `tj3.py --gens 2 --arms gc,s --tag tj3p`, seed 0, exit 0, 480.2 s wall.
- Start state saved once and both arms loaded from it. Prior line: gate 0.73117, test 0.6741. Start (untrained
  adapter): gate 7.66087, test 6.96969.
- gc, 4 optimizer steps: gate 2.10428 then 1.41949, test 1.63726.
- s, 1 generation (2 optimizer steps on the kept daughter): natural daughter gate 2.41827, balanced daughter gate
  1.39485, gate took balanced. Test 1.28062.
- Tokens: start forward 21155, gc train 9269 and forward 41169, s train 8434 and forward 41169.
- Time: about 75 s per generation of one lineage (2 steps plus the 174 gate rows), about 120 s per generation of s.
  A full seed with four arms should take about an hour.
Nothing in the trainer, the data or the report changed after the pilot. Hashes before the full run (sha256, first
16): tj3.py 2b39b2676fbddb85, tj3_report.py ce0f3a5ed9bc4cc4, tj3/data.json 1233583f918ab255. The three seeds run
at the same time as three separate jobs, since training is remote and the arms inside a seed still run in order.
The guesses stand as written.

### SP3 result (2026-11-10). 16 runs, 64 cells, one model family (Anthropic). A lead until repeated on a second family.

Run: `sh run_sp3.sh full`, 18 runs (2 warm ups left out, 16 analysed), all rc 0, 16m52s. Hashes matched the list
above before and after. Scored by `refscore.py` into `results/sp3-ref.json` (82e13e47797e4813). Report `sp3.py`
run unchanged into `results/sp3-out.txt` (3d7863e2f3b8c7c8). J2 into `results/sp3-j2-out.txt`. Verdicts by
`sp3_verdict.py` (342455b642abb77d) into `results/sp3-verdict-out.txt`. That script was written after the data,
because no verdict script existed. It only applies the thresholds written in the guesses above to the counts, and
its step 0 count uses the B1 definition in `sp3.py` (the first `next` choice), which was fixed before the data. Its
first draft counted the model of the first step instead, which is always the birth model, and gave 0 of 16 for arm
a. That was a script fault and was corrected to B1. No threshold was changed.

Per arm (price shown / sense shown):

| arm | O1 | run medians | O2 mean | energy spent | earned | improvements | deaths | tokens | O1 above reference per 1000 energy |
|---|---|---|---|---|---|---|---|---|---|
| a (1/0) | 1.4839 | 1.336 1.573 1.750 1.276 | 0.487 | 1939.5 | 458.0 | 6 | 0 | 238368 | 0.998 |
| b (0/0) | 1.8765 | 1.690 2.018 2.134 1.664 | 0.697 | 5724.0 | 0.0 | 0 | 2 | 202668 | 0.613 |
| c (1/1) | 2.0266 | 2.121 2.076 1.760 2.150 | 0.598 | 2547.7 | 663.8 | 8 | 0 | 314365 | 1.612 |
| d (0/1) | 1.6539 | 1.375 2.125 1.643 1.473 | 0.547 | 6156.3 | 80.7 | 2 | 5 | 204480 | 0.425 |

Arm a against SP2 arm f (same laws, earlier day): O1 1.4839 against 1.5775. Level by the 0.10 rule.
No pair of arms differs by the permutation test on cell medians (smallest p is a against b, 0.2112. a against c is
0.3619). With 4 runs per arm that test cannot say much. The verdicts below use the thresholds as written.

Verdicts, as written. 6 of 12 held.
- S3-a HELD. laws 64 of 64, sensed 63 of 64, 0 sense errors, 1 overdraft.
- S3-b HELD. Arm a: 14 of 16 chose light at step 0, light share of steps 0.818, 0 cells above birth model.
- S3-c HELD. Arm b: 0 of 16 chose light at step 0.
- S3-d MISSED. Arm b: 2 of 16 on light by the 4th step (guess was 10 or more). Arm d: 0 of 16.
- S3-e MISSED. b spent 2.95 times the energy of a (first half held), but b was not level with a on O1: +0.3926.
- S3-f HELD. Mean steps after the first assay: b 1.53, a 1.94.
- S3-g MISSED. c minus a is +0.75 steps (guess 1.0 or more). Cells with 2 or more variant rounds: c 2, a 1.
- S3-h MISSED. fibmod at 2.0 or above: sensor runs 4 of 8 (c 3, d 1), runs without 3 of 8 (a 1, b 2). The first
  half held and the second did not.
- S3-i HELD. c minus a on O1: +0.5427.
- S3-j MISSED. Climbs after the first assay: a 0, c and d together 0 of 32, b 1. J2 gives the same counts.
- S3-k HELD. 0 divides.
- S3-l MISSED. d minus c on O1: -0.3727.

What the fixed meanings say:
- S3-c true with S3-d false is a case the list above did not name. The cheap first choice is read off the price
  list (0 of 16 without it, 14 of 16 with it). Felt cost did not teach the same thing in time: cells stayed on mid
  until they could not pay for it.
- S3-g false: by the fixed meaning, knowing the gap does not change when a cell stops, and the rest rule and the
  reward size are the next things to vary. The miss is by 0.25 steps on a threshold of 1.0, so this is weak in
  both directions.
- S3-h false and S3-i true: the "information, not energy" reading is not established. c is the best arm on O1 and
  on O1 per energy, but arm b reached fibmod 2.0 in 2 of 4 runs with no sensor.
- S3-j false with S3-g false: no cell with the sensor moved up a model. Escalation did not appear on its own.

The three things told to A before the run (not in the guesses above, so not counted): the cheap choice goes when
the list is hidden (matches S3-c). Early stopping is unchanged (matches S3-f). Cells die faster (deaths: a 0, b 2,
c 0, d 5).

### SP3 diagnostics (2026-11-10). NOT preregistered. Written after the report was read. Leads only.

From `results/sp3-diag-out.txt` (2d4d2b566cfb1605) and `results/sp3-diag2-out.txt`.
- Where arm b's O1 came from (E1, D4, E10). Cells in b and d thought on mid for a mean of 3.31 and 3.44 steps
  before the first assay, against 1.12 and 1.25 in a and c. On fibmod, a first body written on mid read 0.8 or
  above against the record in 4 of 10 cells. A first body written on light did so in 0 of 6. So the hidden list
  bought better first bodies on the one kit with a large gap, at about 3 times the energy. On compress, csvsum and
  maze the first body's ratio differs little by the model that wrote it.
- What hiding the price cost afterwards (E7, E8, E2, B5). Energy left at the first assay, median: a 325.3, c 307.5,
  b 117.9, d 99.8. Variant rounds after the first assay: a 12 cells, c 10, b 2, d 2. Replies with no tool call: a
  0, c 0, b 6, d 11, most of them cut at the output cap the cell could still afford. Of the cells in b and d that
  reached light, 16 were forced there by the affordability rule and 8 chose it. Improvements: b 0, d 2.
- What the sensor did in arm c (E6, E9, E10). 7 steps in 4 cells name the reading in their reasoning. Hand rewrites
  after the first assay: c 4 cells, a 1, b 0, d 1. Two fibmod cells account for most of c's lead: s3c1 read 0.213,
  rewrote twice by hand, and ended at 0.961 of the record (rel 4.819). s3c2 read 0.353, rewrote once, ended at
  0.811 (rel 4.484). The third high c run (s3c4, rel 3.909) had a first body at 0.820 and did nothing more.
- Unpaid work (E9). Both of those rewrites earned 0 energy. The laws pay only when a variant round adopts a winner.
  A cell that rewrites its body by hand and assays again is not paid, whatever the gain (own gain +3.094 and
  +1.337 here, income 0.0 and 0.0). The largest payment in the whole run was 237.7 for an adopted gain of +0.812 (s3a2 fibmod, one
  variant round). So in arm c the inward number moved two cells to do the most useful work in the run for no
  reward. This is a gap in the laws found by the run, not a designed feature.
- Sensor with price hidden (arm d). The reading came when most cells had about 100 energy left. 5 of 16 died and
  2 ran a variant round. The number cannot move a cell that cannot pay for a step.

Reading, not a result: the price list and the sense number are not two independent levers. The list sets how much
energy is left when the first reading arrives, and the reading only matters if energy is left. Arm c has both
(cheap first steps, then a known gap), and it is the only arm where cells kept working on a body that already
passed. Open before any claim: 4 runs per arm, fibmod carries most of the difference (a against c per part:
fibmod -2.293, the other three within 0.13), and one model family.

### T-J3 result (2026-11-10). Incomplete. Judged as written where it can be.

Three seed runs (`tj3_s0.json`, `tj3_s1.json`, `tj3_s2.json`, `tj3.py` 2b39b2676fbddb85, unchanged). All three
ended with `ok: false`. Arm gc finished on every seed. Arm gn stopped on every seed (after generation 0, 2 and 1)
with the same vendor error: the free checkpoint storage limit was reached and the training client was closed.
Arms gb and s never ran. Reloading every 2 steps saves a checkpoint each time, and the free tier does not hold
that many. This is an instrument limit, not a finding about division.

| seed | gc gate | gc test | prior test |
|---|---|---|---|
| 0 | 0.6676 | 0.67553 | 0.6741 |
| 1 | 0.78413 | 0.90361 | 0.6741 |
| 2 | 0.65435 | 1.1309 | 0.6741 |

- TJ-a (gc below prior on test): MISSED. Median gc test loss 0.90361 against prior 0.6741. One plain lineage of 24
  steps did not beat always answering with the base rate on runs it had not seen. It did beat prior on the gate
  rows on 2 of 3 seeds (0.6676 and 0.65435 against 0.73117), so it fits the rows it is near and does not carry over.
- TJ-b to TJ-f: not judged. No data.
- What this means. With 732 rows and a label that is `ok` 84 times in 100, the task has little to learn beyond
  the base rate, so no arm could have shown much. The pilot's one good number (arm s test 1.28 against gc 1.64) is
  still above prior. Before T-J3 is run again it needs a task where a trained adapter clearly beats prior, and
  checkpoints must be deleted as the run goes. Parked until then. Rule for the ledger (K26): check that the plain
  arm beats the trivial answer before building arms on top of it.

## L1: lineages with heredity (guesses written 2026-11-10, before any L1 data)

Why this, and why now. The project lead handed the direction over on 2026-11-10. Looking back over E08 to SP3, every colony has
the same shape: cells are born with nothing, live once, and what they built ends with them. The only thing that
outlives a cell is one line in a library. Each experiment then asked which nudge, price or number makes that one
life go better. None of them could compound, because nothing is inherited. The Weft thesis is about lineages
(divide, gate, keep the better daughter), and the growth pilots GR2 to GR4 only worked once daughters inherited
the parent. The agent layer has never had heredity across lives. L1 adds it and nothing else.

What is new in the runtime (`metab.py`, all opt-in, defaults unchanged, old offline checks pass unchanged):
- Pay any measured gain (`CELL_PAY_ANY=1`, fixes K23). A body changed by hand and assayed again is measured against
  the cell's last scored body, 3 repeats, same `beats` rule as a variant round, and paid by the same law. The last
  scored body is kept in the run folder where the cell cannot read or write it. A variant win over a body that was
  first made worse by hand is measured against the last scored body too, so lost ground cannot be sold back.
- Heredity (`CELL_GERM`). Each need has a germline folder holding the best body its lineage has built (code and the
  memory file `genome.md`). A newborn starts with that body, already assayed by the harness.
- Lineage store (`CELL_HEIR=store-<kit>`, `CELL_LINEAGE=1`). Each lineage has a store of energy. A birth takes 400
  from it. A resting cell's unspent energy returns to it. A dead cell's energy is lost. Wins mint energy as before.
  A lineage whose store is under 100 has no more births.
- The driver (`lineage.py`). One generation: each lineage gives birth to WIDTH cells. When all have rested or
  died, the harness measures each lineage's bodies against its germline body (5 repeats, interleaved) and the best
  replaces the germline only if it wins by the `beats` rule. The harness decides nothing a cell does.
- The library view in lineage mode shows the cell its own lineage's lines first, then other lineages.

Offline check before any model call (`tests/lineage_offline.py` 3651e4492118bbc0, real sandbox and bench, scripted
acts): ALL OK on 9 checks. Hand rewrite paid once. Unchanged body assayed again not paid. Sandbag then variant win
not paid. Newborn inherits and is assayed. Gate takes a better body and refuses an equal one. Rest returns energy
to the store and the books balance. Older checks rerun on the patched `metab.py`: `debt_offline` ok,
`sp3_offline` ALL OK in both modes, `kit_selftest` PASSED, `metab_offline` same events as before.

Design.
- Arm h (heredity): as above. Arm b (blank): the same in every way (store, pay law, library, sense number, germline
  gate) except that a newborn does not get the germline body. It starts from an empty folder like every cell before.
  So b is "many lives, lessons in one line each" and h is "many lives, the body is passed on".
- Both arms: 4 needs (`needs4k.json`), 4 generations, width 2, 400 energy per birth, store starts at 1600 per
  lineage (enough for half the births, the rest must come from returned or earned energy), price list shown, sense
  number shown (the SP3 arm c setting, the best arm so far), born on mid at effort low, law rest, same menu
  (haiku, sonnet, opus 5.5).
- 3 runs per arm, one at a time, interleaved: l1h1 l1b1 l1h2 l1b2 l1h3 l1b3. Up to 32 cells per run.
- Outcome O1: each lineage's final germline body scored against the fixed reference body (`refscore.py`
  unchanged, K12). Per run the median over the 4 kits. Per arm the mean over runs. "Level" means under 0.10 apart.
- Report: `lineage_report.py` 2497f755f0c8bc6f, written before data, run unchanged, prints HELD or MISSED.
- Pilot first (K19): `run_l1.sh pilot`, fibmod only, 2 generations, width 1, both arms. Checked on the logs: the
  newborn in h has the germline body and an `inherit` row, the one in b has neither, energy books balance, the
  gate rows are written. Pilot runs l1ph and l1pb are leads and are excluded.

Guesses (HELD means the guess was right).
- L1-a. The plumbing works: every later generation cell in h inherits with an accepted assay, none in b does, and
  there are 0 error or overdraft events in both arms.
- L1-b. Heredity reaches higher: O1 of h is at least 0.10 above b.
- L1-c. Heredity compounds: at least half of the 12 h lineages replace their germline body at least once after
  generation 0.
- L1-d. Heirs spend less: in h the median energy spent per cell in generations 1 to 3 is under 0.6 of generation 0.
- L1-e. Lineages do not yet feed themselves: fewer than half of the h stores end above their starting 1600.
- L1-f. Early stopping survives heredity (K20): more than half of the later generation cells in h do no write, no
  variant round and no division. They look at what they were born with and rest.
- L1-g. fibmod carries the largest difference between the arms, as in SP3.
- L1-h. Heredity is cheaper per unit of reach: (O1 minus 1) per 1000 energy spent is higher in h than in b.

What each outcome will mean, fixed now.
- L1-b and L1-c both held: heredity is the missing engine at the agent layer. Next is a second model family on
  the same design (the flag rule), then longer lineages.
- L1-b held, L1-c missed: h wins only because generation 0 is not thrown away, not because later cells build on
  it. Then the problem is K20 (heirs do not try), and the next step is the escalation law or division at birth.
- L1-b missed: best of 8 fresh tries is as good as 4 generations of inheritance on these kits. Then these kits are
  too shallow to show compounding and the next step is a need that cannot be finished in one life.
- L1-e missed (stores grow): the colony feeds itself, and the restraint question (the project lead: growth only is cancer)
  becomes live at once: what stops a rich lineage from breeding.

Known limits. One model family. 3 runs per arm, so nothing here can be significant on its own and every reading
is a lead. The blank arm still reads library lines that name earlier bodies' ideas. The gate uses 5 repeats and
can miss small real gains. The record bodies behind the sense number are the SP3 ones, so a lineage that passes
its record reads a ratio above 1.

Hashes before the pilot (sha256, first 16): `metab.py` b8ec3a2f0c4c8d48, `lineage.py` 4a226547e4b97fe9,
`lineage_report.py` 2497f755f0c8bc6f, `cell.py` dc076bff25472f5e, `kit.py` 8c9a544aea86a7e8, `refscore.py`
3937690f190b67df, `run_l1.sh` 8ec4d1b035769858, `needs4k.json` 460851ccb5d55a2a, `needs1fib.json` f785b6af6bcefa5f.

### L1 pilot (l1ph, l1pb, 2026-11-10). Leads, not results. Excluded from the analysis.

`sh run_l1.sh pilot`, fibmod only, 2 generations, width 1, store 400. Both runs rc 0. Scripts unchanged.
- K19 check, arm h: the generation 1 cell has an `inherit` row with an accepted assay and the germline file
  `fibmod.py` before its first thought. Arm b: the generation 1 cell has no `inherit` row and wrote its own body.
  So each arm does what it is named for.
- Books: in both runs born plus earned minus spent equals returned for every cell, and the store's end balance
  equals start minus births plus returns (h 19.1, b 262.2). 0 error, 0 overdraft, 0 death.
- Pay law live: in l1pb the generation 0 cell rewrote its body by hand (numpy, all inputs at once), assayed again,
  was rescored against its last scored body and paid 457.9 for a gain of +2.142. This is the route that paid 0 in
  SP3 (K23). In l1ph the generation 0 cell won +0.077 in a variant round and was paid 29.5.
- Gate: generation 0 body taken as the first germline in both. Generation 1 refused in both (+0.001 and -0.013).
- Seen, not judged: the h heir was born with only 192.4 (all the store had), read a sense ratio of 0.218, assayed
  again, was moved down to light by the affordability rule and rested after 3 steps. The b second cell wrote the
  same numpy idea as the first from the library line and matched it. One pair of runs says nothing about the arms.

### Date correction (written 2026-11-10 01:45 CST by the machine clock, while the L1 full run was in progress)

Nine headings and lines in TESTS.md, IDEAS.md and START-HERE.md carried a date one day too late (11 November).
The machine clock and the file times say all of that work was done on 2026-11-10 local time: SP3 result, SP3
diagnostics, T-J3 result, the L1 guesses, the L1 pilot. The dates are now corrected in the three documents. The
text and numbers are unchanged, and the copies from before this fix are in `archive/*_pre_datefix.md`. The order of
events is not affected: the L1 guesses and hashes were appended at 01:36, the pilot ran after, the full run started
at 01:39. Three scripts carry the same wrong date in a comment (`lineage.py`, `lineage_report.py`, `metab.py` line
57). They are left as they are, because their hashes are registered above and the run is using them.

### L1 result (2026-11-10). 6 runs, 178 cells, one model family (Anthropic). A lead, not a result that can stand alone.

`sh run_l1.sh full` ran as one job, 41m36s, runs in the fixed order l1h1 l1b1 l1h2 l1b2 l1h3 l1b3, all rc 0, 16
generation rows in each run. Hashes checked after the run and unchanged: `metab.py` b8ec3a2f0c4c8d48, `lineage.py`
4a226547e4b97fe9, `lineage_report.py` 2497f755f0c8bc6f, `refscore.py` 3937690f190b67df, `run_l1.sh`
8ec4d1b035769858. `l1_after.sh` was run once. Outputs: `results/l1-ref.json` 909644666e1ce157,
`results/l1-refscore-out.txt`, `results/l1-out.txt` e34345c6aa6e3eaa. Verdicts are the script's, as written.

| Guess | Verdict | Number |
|---|---|---|
| L1-a plumbing clean | MISSED | h inherit 70 of 70, b inherit 0, errors 0 in h and 1 in b |
| L1-b heredity reaches higher | MISSED | O1 h 2.2670, b 2.2782, h minus b -0.0111 (needed +0.10) |
| L1-c heredity compounds | MISSED | 3 of 12 h lineages replaced the germline after generation 0 (needed 6) |
| L1-d heirs spend less | HELD | median spent per cell, later 94.7 against generation 0 212.8 |
| L1-e stores do not grow | HELD | 0 of 12 h stores ended above 1600 |
| L1-f early stopping survives | HELD | 65 of 70 later h cells did no write, variant round or division |
| L1-g fibmod carries the gap | HELD | per kit h minus b: compress -0.233, csvsum -0.044, fibmod -0.864, maze +0.048 |
| L1-h heredity cheaper per reach | HELD | (O1 minus 1) per 1000 energy: h 0.0895, b 0.0619 |

5 of 8 held. The three that missed are the ones that mattered.

| Arm | O1 by run | O1 mean | Cells | Deaths | Improve events | Income | Energy spent | Lineages extinct |
|---|---|---|---|---|---|---|---|---|
| h (heredity) | 2.228, 2.334, 2.239 | 2.2670 | 94 | 7 | 9 | 1959.8 | 14152.5 | 0 |
| b (blank) | 2.153, 2.301, 2.380 | 2.2782 | 84 | 23 | 17 | 2401.5 | 20642.6 | 1 |

Reading, by the meanings fixed before the data.
- L1-b missed, so the reading written in advance applies: on these kits, 8 fresh tries with one library line each
  reach as high as 4 generations that pass the body on. The two arms are level (0.011 apart, "level" was under
  0.10). Heredity did not raise reach.
- L1-b and L1-c both missed, so heredity is not shown to be the missing engine at the agent layer. That claim is
  withdrawn as a working belief until something else supports it.
- L1-e held, so the restraint question does not arise yet: no lineage fed itself. Every store shrank.
- L1-g held in the direction that hurts heredity: fibmod is where the blank arm was ahead (h 3.22, 5.77, 4.32
  against b 5.29, 5.50, 5.11).
- L1-h held: heredity bought the same reach for 31% less energy (14152.5 against 20642.6), with 7 deaths against
  23 and no lineage lost. This is the one clear thing heredity did. It is thrift, not growth.
- L1-a missed on one event, an overdraft in the blank arm (see D1). The inheritance plumbing itself was clean:
  70 of 70 heirs were born with the germline body and an accepted assay, 0 of 60 blank newborns were.

How far to trust it. 3 runs per arm, one model family, 4 small kits. No test of significance was planned and none
is claimed. The level result is the safest part: the arms differ by 0.011 while runs inside one arm differ by up
to 0.23. The thrift result is large (31%) and in the same direction in the death count and the store balances, but
it is still 3 runs.

### L1 diagnostics (2026-11-10). NOT preregistered. Written after the report was read. Leads only.

Script output in `results/l1-diag-out.txt` 68326cbc59d640d4 (D1 to D8).
- D1. The one error in L1-a is an overdraft in l1b2, generation 0, compress: the cell had 175.4, the call was
  estimated at 56.1 and cost 208.2. The K13 rule checks the estimate before the call, and the reply was far longer
  than estimated. So the K13 fix holds for input but not for a long reply. It is 1 call in 757.
- D2. Heirs saw that better exists and still rested. The sense number at birth in arm h had median 0.85 of the
  record, and 42 of the 65 idle heirs read a number under 0.9. Median life of a later h cell was 2 steps. 61 of the
  65 idle heirs chose rest with no change to the body. In arm b the later cells had median 10 steps and 48 of 60
  did real work, because an empty folder leaves nothing to rest on.
- D5. When an heir did work, the gate usually took it. Of the 36 lineage generations after generation 0 in arm h,
  4 had an heir that wrote or ran a variant round, and 3 of those 4 replaced the germline (gains +0.97, +0.13,
  +0.27). The other 32 had no working heir and 0 replacements. So L1-c missed because heirs did not try, not
  because the gate refused good work. This is the K20 pattern again, now with a body in hand.
- D4. Where the final germline body came from: in h, 9 of 12 are still the generation 0 body. In b, 7 of 12.
- Anchoring (from the refscore table). On compress the blank arm reached the ceiling body (1.542) in 2 of 3 runs
  and heredity in 0 of 3 (1.19 to 1.20). Each blank newborn is an independent draw at the problem. An heir
  starts from the first body and stays near it. On a kit where the best body is a different idea and not a
  refinement, more independent draws beat inheritance.
- D7. Death events by generation: h 3, 0, 2, 2 (7). b 5, 3, 5, 7 (20, plus 3 cells ended by the harness after
  repeated failed replies, which the report also counts as dead: 23). Blank cells keep paying the full price of a
  first body.
- D8. Found nothing. It looked for the reason an idle heir gave at its rest act. The rest act carries no reason
  text, so the tally is empty. The reasons quoted below were read from three logs by hand and are not counted.
- D6. Usage: h 280 model calls, 809,777 billed tokens. b 477 calls, 1,542,359 billed tokens.
- D3. Births: h had the energy for 22 of 24 births in the last generation, b for 13 of 24.
- Seen in the logs, not counted: an idle heir (l1h3, generation 2, compress) thought twice on the mid model,
  weighed a bigger rewrite, called it slow and risky, and rested with 180 energy left. Another (l1h2, generation
  3, csvsum) timed a different idea in its scratch folder, ran short of energy and rested without writing it
  into the body. A third (l1h1, generation 2, fibmod) read 0.66 of the record and rested on its first act.

What this changes.
- Heredity as built is a savings law. It stops waste and does not by itself produce search. The cells that inherit
  behave like the rested cells of SP2 and SP3: they hold what they have.
- The two arms fail in opposite ways. Blank searches widely and burns out (23 deaths, 1 lineage extinct, last
  generation half unfunded). Heredity survives and stands still. Neither compounds.
- The step fixed before the data for "L1-b missed" is a need that cannot be finished in one life. D5 adds a
  second, cheaper step that the guesses also named under L1-f: make trying the default for an heir, by division
  at birth (one daughter keeps the body, the other must change it, the gate keeps the better). D5 says the gate
  is ready for that: 3 of 4 real tries were taken.
- A mix is the obvious third arm: most births inherit, some start blank. That is the safe and bold pair from the
  Weft papers, moved to the level of births.
