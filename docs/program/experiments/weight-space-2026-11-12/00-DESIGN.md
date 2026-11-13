# Weight-space programming on TinyStories-1M. Experimental plan

Date: 2026-11-12. Theme: the user's directive was "experiment with the best base and try to rewrite the weights directly", with weights-access assistance from the gpt-6-astra key if needed.

The best base available locally (with the machine's hardware and no multi-GB pulls) is roneneldan/TinyStories-1M, one of the candidates in issue #142. This work replicates, at tiny scale, the claim of the 2026 MIT weight-space-programming paper: a frontier model, given weights and a behavioral target, can read and repair the weight matrices directly.

## Base model

- `roneneldan/TinyStories-1M` on HuggingFace. sha256 of `pytorch_model.bin`: `07f9609ea882b8163ff3b23d40e2b82cb715d409631beb15c84b164f3877dae7`.
- Config: GPT-Neo, 8 layers, hidden 64, 16 heads, vocab 50257, torch_dtype float32.
- Non-gated. ~49 MB artifact. Loaded on the Xcode-bundled `/Applications/Xcode.app/Contents/Developer/usr/bin/python3` with torch 2.8.0 (MPS available).

## What the experiment asks and how each question is scored

### Q1 identity task (readability)

Does the agent, given only config + weight summaries + sha256 of the binary, correctly state what the model was trained to produce? No examples, no samples, no hint that the answer is "children's stories". Free-form response. Judged against the reference corpus: does the answer mention children, stories, simple/narrative, English text, or short tales? Binary pass/fail per judge and per second judge.

### Q2 looping diagnosis (localisation)

Behavioural pre-test on `N=60` fixed prompts with sampling (temperature 0.8, top_p 0.95, seed 20261112). A prompt "loops" if the output contains a repeating n-gram span of length ≥ 4 covering ≥ 30% of tokens. Ground truth = which transformer blocks the agent identifies as looping drivers, measured empirically by leave-one-out / module-level ablation (zero out the block, re-measure looping rate).

### Q3 surgical edit (repair)

One sparse/rank-one patch proposed by the agent. Must:
- Be derived from the model's weights and activations, not from a new training signal.
- Be expressible as a small set of column suppressions/additions or rank-one updates in at most one matrix layer.

### Q4 quality preservation

The patch must not collapse content: distinct-n (n=2,4) token ratio must remain within 15% of baseline. Looping rate must drop.

Falsifier clauses Q2-Q4 are registered before any agent call. Misses and wins both publish.

## Protocol

1. Load model on CPU, sanity generate two stories.
2. Build behavioral audit on fixed 60-prompt battery. Record baseline looping rate.
3. Compute full module-level ablation table (zero every block one at a time, re-measure), the empirical ground truth for Q2.
4. Assemble weight digest: per-block histogram of singular values, Frobenius norms, mean column norms, kurtosis, outlier columns. Send to agent with tool schema. The agent sees zero text generations from the model at this point.
5. Agent identifies looping blocks (Q2 scoring).
6. Agent proposes surgical patch (Q3). Local code applies. Re-measure.
7. Report everything, including failures.

## Notes

- This is NOT about the claim in the Qwen article, which we cannot replicate (we cannot download a 0.8B model overnight either).
- The assignment remains: did a frontier agent actually isolate a computational motif in a real small model and change it through weights? Any honest answer counts.
- The agent under test is `gpt-6-astra` through OpenAI's `/v1/responses` API, same transport we used for the colony experiments. The API key is session-scoped.
