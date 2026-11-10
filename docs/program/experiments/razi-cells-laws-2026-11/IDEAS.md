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

## E: embeddings (project lead, 2026-11-09, shaped by razi)
Core move: embed every code variant a cell writes. A colony's history becomes a path through vector space, and mitosis becomes a step in that space.
- E1 Split distance vs gain. Measure cosine distance between daughters A and B at each split. Question: do wider splits find bigger wins, or do they mostly fail? Gives an optimal split width.
- E2 Novelty floor. Reject a split whose daughters sit closer than a threshold, so every A/B is a real experiment, not two near-copies. Compare wins/100 calls with and without it.
- E3 Surrogate fitness. kNN over embedded past variants and their scores predicts a new variant's score before the bench runs. Skip variants predicted to lose. Cuts bench time, the serial bottleneck. Runs local on the M1 GPU.
- E4 Retrieved loser lessons. Embed LIBRARY entries and give each cell only the top k nearest to its current code, not the whole file. Test none / all / top-k.
- E5 Model fingerprints. Plot where each model's variants land for the same NEED. Do Fable, Astra, hy4, argon occupy separate regions? Does a mixed colony cover more area and win more?
- E6 Convergence map. Across colonies, do winners for one NEED collapse to one point (one best answer, like bz2 for compress) or several basins?
Prereq: cell.py must save every variant's full code (logs now keep only "<N chars>"). Embedder: local ollama nomic-embed-text, no key, no network after pull.

- 2026-11-09: cell.py now archives every write/variant to <cell>/variants.jsonl (backup cell_v3d.py). embed.py (razi-tools/cells) runs E1+E5 via local ollama nomic-embed-text (768-d), self-tested. b7 started before the patch, so b8 is the first run with code captured.

## F: embedding causality (2026-11-09, from the project lead's "embedding -> vector -> mathematical causality")
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

### W1 result (2026-11-09): Paper 1 on Apple MPS
- E2 (12 gen x 10 seeds) and radius sweep (7 R values) on CPU, MPS, and a second CPU run. Repo untouched.
- CPU is bit-deterministic (two runs identical). MPS is not bit-equal: 3602/11063 values differ, max abs diff 0.0117, all 10 final weight hashes differ.
- Zero differing commit decisions out of 120 E2 + 840 sweep generations. All 120 ALPHA wins on both. Held error ratio 0.2781 CPU vs 0.2771 MPS. Core drift 0.0, watermark cosine 1.0 on both.
- MPS slower at this size: ~115 ms vs ~61 ms median per run.
- Likely cause (read, not tested): torch.randn_like on device, so MPS draws a different noise stream.
- Files: ~/Work/weft-repro/{mps_e2e4.py,mps_results.json,mps_summary.md}.

## G. Google AI Mode conversation (project lead, 2026-11-10)
Source text saved in `sources/aimode-2026-11-10-google.txt` (the project lead's chat with Google AI Mode, which read Report 1).
Treat it as outside advice. Each item below is marked checked or unchecked.

Ideas worth testing:
- G1 Deterministic fitness. Score Bend programs by interaction count (ITRS) instead of wall time.
  Checked here: `bend run-c -s` gave ITRS 6029296 on 3 of 3 runs of one program, and 81 on 2 of 2 runs of another.
  `run-rs` gave 6553583 on 2 of 2 runs of the first program, so the count depends on the runtime. Pin one runtime.
  If it holds, the noise gate, the 5 repeats, the machine-wide bench lock and the stderr-179 class of
  artifact all go away for these tasks. Limit: ITRS counts work, not time, so parallel speedup is invisible.
- G2 Harness-owned validation kit. The harness, not the cell, holds the correctness cases.
  This closes the weakness Report 1 section 3.4 admits (6 of 8 tasks trust the cell's own check).
- G3 Lambda calculus evaluator as the NEED. The claimed reason: an evaluator can later run the next
  generation of variants, so gains can compound. Kit cases: identity, a Church-numeral stress term,
  and a variable-capture term that a naive substitution gets wrong.
- G4 Seed = one read-only type file (the Term type), nothing else. Checked: a Var/Lam/App type with a
  recursive function compiles and runs in Bend 0.2.38.
- G5 A/B: pure Lean arm against Bend arm. Same task, same kit.
- G6 Carryover threat. One cell's benchmark can leave the CPU hot or the cache dirty for the next cell.
  The bench lock does not stop this. Unchecked. Test: alternate a heavy and a light job, compare the light job's times.

Claims in the conversation that are wrong or unsupported:
- "Lean proves the generated Bend code satisfies the spec." No Lean semantics for Bend exists in our stack.
  What Lean can do today is check a log (F3) or check Lean code. So G5 is Lean-only against Bend-only, both judged by the kit.
- `pthread_setaffinity_np` for core pinning. Checked: 0 hits in the macOS SDK pthread headers. Not available here.
- "M1 Pro, 8 performance cores". This machine reports 8 P cores and 2 E cores and is an M1 Max (the v1 report had the wrong name).
- "Bend removes OS timing noise" is true only for the ITRS count, not for wall time.

Open risk for all of G: models may not write valid Bend (little training data). The first pilot must measure that alone.

## H. Beyond text, and what the failures taught (2026-11-10)
A, 2026-11-10: the bar for a flagged result is significance "to civilization", not to the industry. Explore
every angle judged valuable, including what failures teach. Repo work is not a priority now.

### H1. Failure ledger (each failure read as a finding, with its status)
- F1 Cells that own their fitness test drift it. E11/E12: cells built unsolvable mazes, and 5 of 62 changed
  the input after the assay. No sign of intent, the edits look like tidying. Status: observed, not yet
  tested as a hypothesis. Test: count post-assay benchmark edits per model on the old cell-owned protocol.
- F2 Cells stop at the first passing answer. E11: novar cells called `done` at steps 3 to 5. Status:
  replicated once (E11, E12), one model.
- F3 Asking does nothing, a rule does. E09: a prompt nudge toward `try` had no effect. E12: refusing `done`
  until an attempt raised O5 from 0.062 to 0.938 in novar. Status: two experiments, different models
  (Argon, Sonnet 5.5), so not yet a clean comparison. Test: nudge and hold on the same model, same kits.
- F4 More cells did not mean more progress. g4 had half the wins per 100 calls of g3. Status: one pair of
  runs, old instrument. Untested since.
- F5 The direction of the `variants` effect depends on the model. E08 (Argon) and E10 (Fable 5.2) favoured
  novar, E10 (Fable 5.1) and E11 (Sonnet 5.5) favoured ctrl. Status: open. E13 gives a valid Sonnet point.
- F6 An instrument that reads text can be scored by noise. "OMP: Warning #179" scored 179.0. Status: fixed,
  and the reason kits exist.
- F7 hy4 made 0 improvements in b7. Looked 2026-11-10 (script over b7 logs): 124 acts = 77 sh, 25 no reply,
  8 assay, 7 write, 7 done, and 0 `variants`, 0 `try`. So hy4 never used the gated improvement path at all.
  It explored by shell (in primes it tried to hand-build a C extension, and one compile failed). The 0 is "never attempted", not "cannot
  improve". Same shape as F2. Test: hy4 with hold on the kits. 25 of 124 acts had no reply, cause not checked.
- F8 Interaction counts differ by runtime (run-c 6029296, run-rs 6553583, same result). Status: checked.
  Pin one runtime before using counts as fitness.
- F9 Daughters were told to do what they cannot do. A daughter inherited the parent prompt and tool list. In the
  novar arm that prompt says "improve with try", and a daughter's `try` is refused with "use variants", a tool
  novar does not have. Script over lineage logs: E13 nh 13 of 14 daughters opened with the refused call and 10
  left the body unchanged and lost. E12 nh 12 of 16 opened with it and 3 left the body unchanged. So the nh
  arm of E12 and E13 measured a broken `try`, and H19, H21, H24 are untested. Status: fixed 2026-11-10 in
  `cell.py` (daughters get no `try` tool, their own step 3 text and nudge). Backup `archive/cell_v9pre_daughterfix.py`.
  Lesson: a refusal that names an exit the agent does not have ends the work. Every refusal must name a legal move.

### H2. Directions beyond text (order of attack)
- H2a Non-text fitness: interaction count in HVM as the score (G1). Deterministic, no noise gate, no lock.
  First pilot only asks whether models can write valid Bend at all.
- H2b Non-text inheritance: pass losers forward as vectors that steer the next attempt (extends E and F).
- H2c Weight genomes at agent scale: small local models on this machine, genome is a weight delta, a split
  branches the delta. Direct bridge to Weft Paper 1. Needs a local model and a training loop, so it is the
  largest build.
- H2d Does selection follow the same laws on both sides? Compare acceptance rate, share of bold wins and
  gate binding between Weft (weights) and razi-cells (code) on matched budgets.

### H3. Flag rule for A
Flag separately from routine reports when a result (1) replicates on a valid instrument, (2) holds on at
least two model families, (3) would change how someone outside builds or reasons about these systems.
Nothing meets it as of 2026-11-10. Closest candidate: F2 plus F3.

## I. Inward design: metabolism (project lead, 2026-11-10: behaviour should emerge from causality)
Built as `metab.py`. The harness keeps the bench, the sandbox and four constants. Everything else is the
cell's choice, read from its own state (energy, what each step cost, what a win pays, the other cells).

### I1. What the first two pilots suggest (leads, not results)
- I1a The stop is in the model, not in the harness. With every rule removed and energy to spare, cells
  still stop after one attempt. Resting costs nothing and nothing is lost by it, so the laws as written
  do not make stopping early a bad move. A living thing that stops metabolising dies. Here a resting
  body is kept for free.
- I1b Cells treat energy as something to save, not to invest. All 8 drop to the cheapest model (7 after
  their first call) and none divides. That is rational when the only payoff they can see is small.
- I1c One free attempt after the assay appears on its own (7 of 8), where the old runtime needed the hold
  rule to get it. Possible cause: the cell can see what a win pays. Not separated from the other changes.

### I2. Next laws to test, each as its own preregistered run
- I2a Upkeep: a resting body keeps paying a small living cost from the colony, so rest is not free.
- I2b Inheritance by fitness: surplus energy flows to cells in proportion to their scored gain, not equally.
- I2c Relative fitness: the kit gets harder as the colony's best score rises (a Red Queen world), so a body
  that stands still loses ground.
- I2d Reproduction as the only store: energy above a level cannot be held, it can only fund a daughter.
- I2e Run the same laws on a second model family (Mistral Large 4, Argon) before any claim about I1a.

## J. Layers, stem cells and Inkling 2 Small (project lead, 2026-11-10, discussion 105 follow-up)
Source facts (read 2026-11-10, vendor-reported, saved in `sources/thinkingmachines-inkling-2-small-2026-11-05.txt`):
Inkling 2 Small is a mixture-of-experts model, 594B parameters total, 17B active per token, released
2026-11-05 on Tinker. Tinker prices per 1M tokens: prefill 0.30, sample 1.00, train 1.50. The post
says it reached the older model's final score in 75 training steps on one task. Tinker docs describe
LoRA fine-tuning only. No Tinker key or package on this machine yet. Correction: the earlier note
"Tinker 2: 0 hits" searched the wrong name.

The project lead's hypotheses:
- J1. The same ideas work at harness level and at model level (and later at chip level).
- J2. Cell colonies are to a single strong agent what a GPU is to a CPU: better for wide parallel work.
- J3. Modular micro-harnesses spawning adaptive swarms across model families, for problems with many data types.
- J4. Look at real stem cells independently and recreate the behaviour.

razi's reading of stem cells against our logs:
- J4a. Stemness is held by the niche (signals from neighbours), not by the cell. Ours get no signal from the colony.
- J4b. Division is asymmetric: one daughter stays uncommitted, one commits to work. Ours is a costly copy. 0 of 12 pilot cells divided.
- J4c. Stem cells rest by default and wake on demand from the tissue. Our cells also rest by default (E11 to E13, mp2). Law "mortal" removed rest; biology keeps rest and adds the wake signal.
- J4d. Every cell holds the whole genome and silences most of it. Same as the project lead's dormant if-then idea, and same as 17B active of 594B.
- J4e. Our cells are born committed (one task each), so they are not stem cells at all.
- J5. Two clocks. Base model = genome (same in every cell). Prompt, library, adapter = which genes are on. Harness level is development (fast, signal-led). Model level is evolution (slow, selection-led). Predicts the layers share laws but differ in speed and in how blind the search is.
- J6. Limit on J1: at weight level selection competes with gradient descent, which is far more efficient per trial. Likely split: selection decides structure, gradients fit inside it (Weft Paper 1 already does this).
- J7. Limit on J2: g4 doubled cells and halved wins per 100 calls (3.12 to 1.57). Width helps only if the problem splits and each piece has a cheap check.

Tests to preregister:
- T-J1 stem pilot: one uncommitted cell gets a need with several unlike parts; daughters commit to parts; rest allowed; a colony demand signal wakes resting cells. Against one strong agent at equal tokens.
- T-J2 reflex pilot (discussion 105 idea 1): inherited trigger-and-response pairs, dormant until the trigger text appears.
- T-J3 adapter genome (key and SDK in place since 2026-11-10, smoke 5 of 5; guesses in TESTS.md, code in adapters/tj3.py): cell experience becomes training data for a LoRA on Inkling 2 Small; fork, train two ways, gate keeps the better.

## K. Two engines, and what GR1 and GR2 taught (2026-11-10)
- K1. A daughter that copies its parent gives the gate nothing to judge. Seen at the model layer (GR1: 48 of 48 replayed
  trials inside 2% of the parent) and at the agent layer (E13 forced attempts 4 of 19, `dfix1` maze daughter).
  Biology's answer is asymmetric division: one daughter keeps the parent's state, the other is born different.
- K2. Blind variation plus a gate plus gradient fitting sized a network to its need (GR2). Signal-picked candidates added
  little over blind ones. So "blind" at the model layer means: the proposal does not use the error signal. The gate does.
- K3. Carry K1 up a layer: in `metab.py`, a daughter should be born with a different start (model, effort, library slice,
  or part of the need), not as a copy with the parent's idea. Test as T-K1 inside the stem pilot T-J1.
- K4. Sensor data as a signal. The cheapest honest version is the price: let energy cost per step follow real machine
  load, so cells feel load through the law they already live under instead of through a prompt line.
- K5. GR3 (2026-11-10): sizing to need and the cost of ungated growth survive every knob moved (6 of 6 each). The amount of
  restraint does not: it is set by the gate margin and trial length. And the gate has a blind spot: it reads "no visible
  gain from one step of growth" as "enough". On a hard need (sin 64) that is wrong, the network stays small and learns least.
  A fixed gate cannot tell satisfied from stuck. Biology separates the two: growth is driven by demand from the tissue
  (unmet need), and stopped by contact and resource limits, not by "the last division did not help".
- K6. So the gate needs a second input: unmet need. Candidate law: the margin a growth step must clear falls as the
  remaining error stays high, and rises as it gets low. Test as GR4 before carrying it to agents. The agent-layer twin
  is already in our logs: cells quit after the first passing answer (E11 to E13) because nothing told them need remained.
- K7. GR4 (2026-11-10): two ways to tell satisfied from stuck, both tested. A need sensor (gate loosens while the unexplained
  share is high) and escalation (after each refused step, try a step twice as big, reset on a win). Both fix the stuck case.
  The sensor is fooled by noise: it reads error that cannot be reduced as need and grows about 9 times too wide. Escalation
  is not fooled and has the lowest worst-case regret (1.42 against 3.02 fixed gate, 6.67 sensor, 11.95 no gate).
  The rule this suggests for every layer: do not ask "how much need is left" (a reading), ask "does a bigger try move it"
  (an act). A cell cannot know from one look whether a poor score is a hard task or a noisy bench. It can find out by
  escalating once and seeing whether anything moves.
- K8. Agent-layer twin of K7, for the stem pilot. Our cells quit after the first passing answer (E11 to E13) and the fix so
  far was a rule (`hold`). The emergent version: after a failed attempt the next attempt must be bigger in kind (stronger
  model, more effort, or a division), not a repeat at the same size. In `metab.py` this is already allowed and never chosen
  (heavy model 0 of 8, divide 0 of 12). The law could make it a price fact, not a rule: a repeat of a failed size earns
  less per win than an escalated one. Untested.
- K9. Open after GR4: when need is far out of reach (sin 64) no gate wins, ungated growth does. Restraint has a cost and
  the cost is highest exactly where need is highest. A combined law (sensor proposes, escalation confirms) is the obvious
  next toy test, GR5, only if the agent pilot needs it.
- K10. SP1 (2026-11-10, pilot, 2 runs per arm, TESTS.md "SP1 result"). A stem cell holding all the energy did three
  things a flat colony cannot: it gave unequal birth feeds (compress double, both runs), it sent energy back to parts
  sitting at +0% and not to the winner (3 of 4 wakes), and each wake carried a concrete technical note. 2 of 4 wakes
  moved the score. So need-directed feeding emerged without a rule for it. The stem was told the state of the parts
  and the energy law, nothing else.
- K11. The same pilot shows the K8 fault one level up. The stem rested with 45% and 57% of the energy unspent while
  fibmod sat at +1% and +3% and was never woken (corrected 2026-11-10: this first called fibmod "the part with the
  most known headroom", which rested on an offline test body made slow on purpose). "Nothing left to find" and
  "nothing tried" look the same from above. Candidate carry-over from GR4: escalation. A part that stopped at +0% after
  a cheap try is not evidence of no headroom until a stronger try (model, effort, or a note) has also failed.
- K12. Instrument lesson from SP1, a new failure-ledger entry. Gain from a cell's own first baseline rewards a poor
  start. The stem arm won on median gain (0.1547 against 0.0140) and ended level or behind on absolute kit score on
  3 of 4 parts, because stem-born cells start on the light model with less energy and write a weaker first body.
  Rule from here: every part is scored against one fixed reference body per kit. Gain stays as a within-cell measure
  only. This also touches E11 to E13 less (same birth conditions in every arm) but must be stated in any write-up.
- K13. Law 1 leak found in SP1: a woken cell on the mid model pays a full cache write of its prompt, `affordable()`
  only caps output, and two cells went into debt (-74.4, -1.6). Fix before SP2: charge the real input price before
  the call is allowed, and refuse the step if the cell cannot pay for it.
- K14. Fixed-reference rescoring of SP1 (TESTS.md "DIAGNOSTIC 2", `refscore.py`): flat 1.372, stem 1.352 as the mean
  of run medians, at 1.70 times the tokens for stem. The arms end level. The SP-e gain gap was the first-body effect
  (K12). What the stem did that stands: unequal feeding and need-directed wakes emerged without a rule. What it did
  not do: end anywhere better. Also a failure-ledger entry for me: I quoted a headroom figure from a test fixture as
  if it were a property of the task. Rule: a headroom claim needs a body that exists and was scored on the kit.
- K15. Kits need a known ceiling. Without a scored strong body per kit, "restraint" and "gave up early" cannot be
  told apart, in cells or in a stem. Before SP2: for each kit, record the best body any run has produced (scored by
  `refscore.py`) as the ceiling so far, and report every arm as a share of the gap from reference to ceiling.
- K16. Ceilings measured (TESTS.md "Ceiling per kit", 29 earlier runs rescored in one session). fibmod has a scored
  body at 5.51 times the reference (kp_ch) and five runs at 4.49 or above, yet every energy-law colony run ended
  between 1.07 and 1.97 on it. So the K14 correction went too far the other way: there was headroom on fibmod and the
  energy-law colonies did stop short of it. The rule from K14 stands and is now met (a body exists and was scored).
  Two leads follow. First, the older rule-driven runtime with a hold reached the fast body more often than the energy
  laws with free rest, so "rest is free and safe" may cost reach (ties to K11, the escalation law). Second, msmoke1
  scored 5.37 with an own-baseline gain of 0.072: its first body was already fast. Reach on these kits may depend
  more on the first body than on later improvement, which is what arm m in SP2 touches.
- T-K2 (next). SP2: stem against flat on the fixed-reference metric with the debt hole closed, and a third arm,
  flat with the same total energy but birth conditions equal to the stem's births, so the arm effect is not mixed
  with the first-body effect. Guesses before data.
- K17 (SP2, 2026-11-10). The colony shape is not the lever. Flat, stem fed, and flat with light births end level on
  the fixed-reference metric (1.51, 1.49, 1.50 with fibmod left out). The stem costs 1.28 times the energy and 1.61
  times the tokens, a third of it on its own thinking, and 4 of 5 wakes change nothing. Two runs of the same answer.
  The stem as built is an overhead, not an organ. It stays in the code and leaves the main line.
- K18 (SP2). Under the energy prices the cell is its own model chooser, and it chooses the cheapest every time.
  14 of 16 mid-born cells were on light at step 2, all 52 variants rounds were thought on light, and heavy has
  never been used in any energy-law run (22 runs: 657 light steps, 94 mid, 0 heavy). This is rational under the law: a mid step costs 50 to 100 and a +10% win
  pays 38. So the exchange rate between the price of thought and the reward for a win sets how far a colony
  reaches. Any harness lever on the birth model is overwritten by the cell at its second step.
- K19 (SP2, failure ledger). Arm m was meant to separate "who wrote the first body" from the stem's feeding. It
  could not, because birth model and first-body model are different things once cells choose. Rule: before a run,
  check on pilot logs that the arm changes the thing it is named for.
- K20 (lead). Cells stop without knowing what is possible. Every part that stayed near 1.1 on fibmod rested with
  energy left while a body at 5.5 exists in the project's own records. In GR4 the two laws that fixed the stuck
  case were a sensor of unmet need and escalation after a refusal. Neither exists at the agent layer yet.
- T-K3 (next). SP3, need sensor at the agent layer. One inward data point added to the vitals: how the cell's body
  scores against the best body the lineage has ever recorded for this need (a number, not the code). Arms on the
  cheapest shape (m): no sensor, sensor. Then, if the sensor moves effort but not reach, escalation: a round that
  fails on one model is not counted as "no headroom" until one round on the next model up has also failed.
  Guesses before data. Fixed-reference metric, ceiling shares, K19 check on a pilot first.
- K21 (SP3, lead, one model family). The cheap first choice is read off the price list and nothing else. With the
  list shown 14 of 16 cells chose light at step 0. With it hidden 0 of 16 did, and felt cost did not teach it in
  time: cells stayed on mid until the affordability rule forced them down (16 forced, 8 chose). Being charged is
  not the same as knowing the price.
- K22 (SP3, lead). The price list and the need sensor are one lever, not two. The list decides how much energy is
  left when the first reading arrives (median about 310 with the list, about 110 without), and a reading can only
  move a cell that can still pay for a step. Sensor plus list was the best arm on reach and on reach per energy.
  Sensor without list was the worst on reach per energy and had 5 deaths in 16 cells.
- K23 (SP3, failure ledger, a gap in the laws). The laws pay only for a win adopted in a variant round. A cell that
  rewrites its own body by hand and assays again is paid nothing. The two largest gains in SP3 (fibmod, +3.094 and
  +1.337 on the cell's own baseline) were made that way by cells that had read the sense number, and earned 0.
  Rule: before a run, check that every route to a better body is paid the same. Until this is fixed, income and
  improvement counts understate what sensor cells did.
- K24 (SP3, lead). A stronger first thought is worth most where the gap is large. On fibmod a first body written
  on mid was at 0.8 of the record or above in 4 of 10 cells, on light in 0 of 6. On the other three kits the model
  that wrote the first body made little difference. This is the first agent layer sign that the dearer model buys
  something, and cells with the list shown never found it out because none ever tried.
- K25 (SP3). Escalation did not appear on its own: 0 of 32 sensor cells moved up a model after the first assay.
  The sensor changed what cells did on the cheap model (hand rewrites in 4 of 16 against 1 of 16), not which model
  they used. The GR4 escalation law is still untested at the agent layer.
- T-K4 (next, in this order). 1. Pay by measured gain on any assay, so hand rewrites and variant wins are paid the
  same (fixes K23), then repeat arms a and c. 2. Repeat a and c on a second model family, which the flag rule
  needs. 3. Neutral model names with a short trial of each, so a cell can learn what the dearer model buys (K24).
  4. Escalation law (K25).
- K26 (T-J3, failure ledger). Check that the plain arm beats the trivial answer before building arms on top of
  it. In T-J3 one plain adapter lineage did not beat the base rate on unseen runs (median test loss 0.904 against
  0.674), so no arm built on it could have shown anything. The run also died on the vendor's free checkpoint
  limit: an arm that reloads every 2 steps must delete checkpoints as it goes.

## L. Heredity (2026-11-10, direction handed over by A)

- L1 (the reason). Every colony from E08 to SP3 has the same shape: born with nothing, one life, and the body
  ends with the cell. Only one library line outlives it. Each experiment asked which nudge, price or number makes
  one life go better. None could compound. The growth pilots (GR2 to GR4) only worked once daughters inherited
  the parent. The agent layer never had that across lives. So the next step is not another lever on one life. It
  is to give a need a lineage: a germline body that is passed on, a store of energy that pays for births, and a
  gate that changes the germline only on a measured win.
- L2 (pay law, built). Any measured gain over the last scored body is paid the same, by hand or by variant round.
  Ground lost by hand cannot be sold back. Fixes K23.
- L3 (what to watch). If heirs inherit a good body and rest at once, the problem is not memory, it is K20 (cells
  stop without trying). Then the next law is one that makes trying cheap for an heir: division at birth, where
  one daughter keeps the body and the other must change it, and the gate keeps the better.
- L4 (restraint). A lineage whose store grows can breed without limit. The project lead said growth only is cancer. If L1 shows
  stores growing, the next law is about what a rich lineage does with surplus: feed poorer lineages, or stop.
- T-L1 (done 2026-11-10, 5 of 8 guesses held, the three that mattered missed). Arms h (heredity) and b (blank),
  4 kits, 4 generations, width 2, 3 runs each. Result in TESTS.md.
- L5 (L1, lead). Heredity as built is a savings law, not a search law. Reach was level (h 2.267, b 2.278). Heredity
  spent 31% less energy, had 7 deaths against 23 and lost no lineage. It did not compound: 9 of 12 final germline
  bodies were still the generation 0 body.
- L6 (L1, lead, the K20 pattern with a body in hand). Heirs do not try. 65 of 70 heirs changed nothing, though
  most read a sense number under 0.9 of the record. When an heir did try, the gate took the work 3 times in 4. The
  gate is not the block. The will to try is.
- L7 (L1, lead). Inheritance anchors. On compress the blank arm found the ceiling body in 2 of 3 runs and heredity
  in 0 of 3. A fresh newborn is an independent draw. An heir stays near the first body. Where the best body is a
  different idea and not a refinement, draws beat inheritance.
- L8 (L1). The two arms fail in opposite ways: blank searches and burns out, heredity survives and stands still.
  The safe and bold pair from the Weft papers is the same split, one level down. The next law should hold both in
  one lineage.
- L9 (failure ledger). The K13 rule checks the estimated cost before a call. One call in 757 overdrew because the
  reply ran far longer than the estimate. Cap the reply to what the cell can pay, not only the estimate.
- T-L2 (next). Division at birth. Each birth is a pair: one daughter keeps the germline body untouched (safe), the
  other is born with the body and a rule that it must change it before it may rest (bold). The gate keeps the
  better. Third arm: bold daughter born blank with only the library line (an independent draw, L7). Same kits,
  same budget, against arm h from L1 as the baseline. Guesses before data.
- T-L3 (after T-L2). A need that cannot be finished in one life, so that compounding is the only way up. This is
  the step written down in advance for a missed L1-b.
