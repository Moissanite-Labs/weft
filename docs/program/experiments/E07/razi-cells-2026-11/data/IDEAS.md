# Cell experiments: ideas log

## From A (2026-11-09, verbatim intent)
- A1 Agency: let cells freely build tooling around themselves.
- A2 Meta-mitosis: give cells the mitosis framework itself; let them run, adapt and iterate the mitosis process.
- A3 Formal: hardcode mitosis as mathematical causality (Lean, Bend).
- A4 Proven stack: make the whole architecture provably correct end to end (Bend).
Tooling now: Lean 4.35.0 + lake in ~/.elan/bin. Bend, HVM, cargo absent.

## From razi
- R1 Proof-carrying wins (A3 made concrete): a win is kept only with a certificate.
  Easy tier: differential test vs a reference on random inputs. Hard tier: a Lean proof that the
  new function equals the spec function. Measure: how often a cheap model can write the proof.
- R2 Lean as the NEED: needs that are theorems. Fitness = `lake build` passes and no `sorry`.
  A perfectly honest assay: no timing noise, no fake wins. Mitosis = two proof tactics.
- R3 Mitosis as a law, not code (A3/A4): write the selection rule in Lean
  (keep daughter iff lower CI bound of gain > 0; parent stays baseline) and prove
  "fitness is monotone across generations". Then generate the Python check from that spec.
- R4 Meta-cells (A2): a cell whose body is a copy of cell.py and whose fitness is
  wins per 100 calls of a small child colony. Guardrail: the assay and sandbox stay outside its body.
- R5 Tool commons (A1): cells may publish a tool to a shared shelf; other cells may import it.
  Watch which tools spread (cultural evolution) and whether reuse lifts wins per 100 calls.
- R6 Adversary cells: one cell writes the code, a sibling writes inputs that break it.
  The assay grows from the attacker's finds. Tests whether fake wins appear without one.
- R7 Bend/HVM sanity: Bend is for parallel evaluation, not proofs. Real path: install via cargo
  and use it to run the fitness assays on many cores; proofs stay in Lean.

## Order
1. Finish B5/B6 model runs (in TESTS.md).
2. R2 (cheapest: Lean is installed, assay is binary).
3. R1 differential tier, then Lean tier.
4. R5, R4, R6. R3 after R2 shows models can write Lean at all.

## E: embeddings (A, 2026-11-09, shaped by razi)
Core move: embed every code variant a cell writes. A colony's history becomes a path through vector space, and mitosis becomes a step in that space.
- E1 Split distance vs gain. Measure cosine distance between daughters A and B at each split. Question: do wider splits find bigger wins, or do they mostly fail? Gives an optimal split width.
- E2 Novelty floor. Reject a split whose daughters sit closer than a threshold, so every A/B is a real experiment, not two near-copies. Compare wins/100 calls with and without it.
- E3 Surrogate fitness. kNN over embedded past variants and their scores predicts a new variant's score before the bench runs. Skip variants predicted to lose. Cuts bench time, the serial bottleneck. Runs local on the M1 GPU.
- E4 Retrieved loser lessons. Embed LIBRARY entries and give each cell only the top k nearest to its current code, not the whole file. Test none / all / top-k.
- E5 Model fingerprints. Plot where each model's variants land for the same NEED. Do Fable, Astra, hy4, argon occupy separate regions? Does a mixed colony cover more area and win more?
- E6 Convergence map. Across colonies, do winners for one NEED collapse to one point (one best answer, like bz2 for compress) or several basins?
Prereq: cell.py must save every variant's full code (logs now keep only "<N chars>"). Embedder: local ollama nomic-embed-text, no key, no network after pull.

- 2026-11-09: cell.py now archives every write/variant to <cell>/variants.jsonl (backup cell_v3d.py). embed.py (razi-tools/cells) runs E1+E5 via local ollama nomic-embed-text (768-d), self-tested. b7 started before the patch, so b8 is the first run with code captured.

## F: embedding causality (2026-11-09, from A's "embedding -> vector -> mathematical causality")
E1-E6 are correlational: they observe where code lands and how that relates to fitness. F intervenes.
- F1 steering direction: d = centroid(winners) - centroid(losers) per need. Generate k candidates, keep the one whose projection on d is highest vs a random pick. Randomized A/B on the pick rule. If projection-picked wins more, the direction is causal, not just descriptive.
- F2 do-test: ask the model to rewrite a variant "toward" a nearest-winner exemplar vs "away". Fitness delta by arm.
- F3 Lean link (R-series): state "split adopted only if gain > noise floor" as a theorem over the logged numbers; the embedding space is the measured state, the proof checks the selection rule held.
- Embedding A/B: embed.py takes EMBED_MODEL=nomic-embed-text | openai:text-embedding-3-small | openai:text-embedding-3-large. Cached per model. Synthetic check: all three keep the same ordering; spreads differ in scale (nomic 0.20, 3-small 0.38, 3-large 0.31-0.35). Real comparison waits for b8 code.

## W. Weft link (2026-11-09, after reading Moissanite-Labs/weft @5dc2838 and weft-corpus @393e13e)

razi-cells is the agent level twin of Weft C1 (Models as Cells). Same loop, different substrate:
Weft mutates a 256x256 weight matrix; razi-cells mutates code files through an LLM.

| Weft (C1/C2, Paper 1) | razi-cells today | Gap or transfer |
|---|---|---|
| frozen core rows + watermark | HIDDEN files (NEED, ASSAY, log), read-only to the cell | equal role; add a watermark analogue: reference outputs held by the harness |
| saved baseline W0, gate on distance from W0 | `beats` compares to the current incumbent only | Paper 1 Prop 3: per-step bounds compound. Add a baseline-anchored check: every winner must still pass a differential test against generation-0 output |
| budget b >= c, only commits spend | MAX_CALLS caps all calls, not commits | log spend per commit as well as per call |
| alpha (cautious) / beta (exploratory) lineages; beta never won (Paper 1 E2) | `variants` (2 to 6) and `try` daughters; `try` rarely used, only Astra split | same finding at two levels: selection is plumbing unless lineage merit depends on data. Our `variants` does exercise real selection (b10: 15 kept wins) |
| hippocampal novelty term (0.05 weight) | H9 embedding novelty floor, F1 centroid steering | F1 is the agent level test of Weft's novelty term; E07 card asks the same question |
| tension = function of distance (not measured) | measured noise (spread over 5 repeats) | our noise is an independent signal; offer it as "measured tension" (Paper 1 next step 4) |
| reporting defect #63: reported candidate, not held | `improve` events log only held winners | already correct; keep a test for it |
| C3 interaction combinators + SHA-256 execution records | Bend/HVM installed (HVM is an IC runtime) | A4/R7 meet C3. Cheap step: hash-chain log.jsonl so each cell's lineage is a replayable committed record |
| Milestone I.3: Lean proof of the gate | F3 / R3 Lean theorem | write the Lean proof of Prop 3 (ball invariant) as the first R2 Lean need |
| MPS results not measured | this M1 Max is Apple Silicon | reproduce Paper 1 here, then E2/E4 on MPS (job j_aeee9a) |

Proposed experiments:
- W1. Reproduce Paper 1 on arm64 CPU (`experiments.py --check`), then E2/E4 on MPS. Contribution to Paper 1 §7.6.
- W2. Baseline-anchored gate for cells: winners must match generation-0 reference output. Measures how often today's `beats` admits a semantically drifted winner.
- W3. Committed cell lineage: SHA-256 chain over log.jsonl and winner files. Replay check like Paper 2's 60/60.
- W4. Data-dependent lineages: force alpha (small edit) vs beta (rewrite) daughters each split; record which wins per task. Agent level answer to Paper 1 §6 "Selection".
- W5. Write razi-cells up as a Weft paper candidate ("Agents as Cells") using Paper 1's evidence style. Publication needs A.
