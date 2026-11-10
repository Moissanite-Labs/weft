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
- [~] B5 (running, pid 96800) anthropic:claude-fable-5-1 (high tier, requested)
- [~] B6 (running, pid 96801) openai:gpt-6-astra (high tier, requested, API key route)
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
