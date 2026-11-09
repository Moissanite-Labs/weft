# Report 3: what the corpus holds that the Weft code does not

Status: experiment record, E07 companion. Written 2026-11-09. Exploratory, not preregistered.
Pins: weft main @5dc2838, weft-corpus @393e13e.

## 1. Question

The Weft corpus is the record of the conversations and design notes that the Weft repo was built from. Which of its ideas never reached the code? Which of those can razi-cells test at the agent level before the joint paper is final?

## 2. Method

1. **Extraction.** A script read the 62 `.md` files in `weft-corpus/weft` (top level, `browser-sources/`, `design/`). It split each file into paragraphs and kept paragraphs over 120 characters with at least 3 distinct hits from a 34-term keyword list (cell, mitosis, lineage, fitness, proof, watermark, apoptosis, novelty, tension, ledger and similar). It kept the top `max(6, lines/150)` paragraphs per file and packed them into 4 bundles of about 26 to 47 KB.
2. **Reading.** Six read-only scout agents each read one bundle or one group of design files and listed the ideas they found, with a source line and a status: in code, partial, docs only, or absent.
3. **Status check.** Scouts grepped `weft/runtime` and `papers/` only. Hits under `docs/corpus/sources/` and `docs/program/audit/` are copies of the corpus and do not count as implementation.
4. **Verification.** Every citation in this report was rechecked by hand against the corpus at the pin. The results of that check are in section 5.

## 3. Results: ideas that have not reached the code

Status key: **absent** (no code), **docs** (described in repo docs, no code), **partial** (a narrower form is in code).

| # | Idea | Corpus source (verified) | Weft code status | Agent-level test in razi-cells |
|---|---|---|---|---|
| C1 | Asymmetric A/B mutation: a low rate (0.005) against a high exploratory rate (0.08) | missing-turns-supplement.md:1654; splicers-genesis:1652 | partial. plasm.py:365-382 uses one sigma (0.015) for both lineages. The lineages differ only in how they mix gradient and noise (0.85/0.15 vs 0.50/-0.50). | Small-edit daughter vs rewrite daughter on every split. |
| C2 | Regeneration: after apoptosis, neighbours re-clone the dead cell from the last signed ledger state | splicers-genesis:1088-1090; almalga.md:162-164 | absent (no rollback in `runtime/`) | Inject a corrupt patch; compare kill-and-re-clone with keep-and-patch. |
| C3 | Tension zones: green, yellow, red. Red freezes the weave and hands control to a human | missing-turns-supplement.md:456-458; almalga.md:225 | partial (one hard bound, T at most 85) | Map test-failure rate to how much of its code a cell may edit. |
| C4 | Elastic resistance: near an invariant, cost rises instead of a hard deny | missing-turns-supplement.md:319-320 | absent | Exponential call cost for writes near protected files, compared with a hard deny. |
| C5 | Autonomy attribution: agent vs human share recorded per change, and who signs | missing-turns-supplement.md:477,496 | partial (lineage records the creator only) | Log the origin of each promoted line. |
| C6 | Consolidation dial: plasticity scaled by a dial, from frozen to fully loose | xtra.md:233-249; tune.md:30 | partial (homeostatic sigma, plasm.py:308-319) | Mutation size tied to the failing-test count. |
| C7 | Synaptic consolidation by moving average of winning updates | xtra.md:150; missing-turns-supplement.md:2806 | absent | Merge a winner only after it wins k of n repeats. |
| C8 | Decay of unused pathways (Hebbian pruning) | xtra.md:136,150 | absent | A utility score per grown function; drop functions below a threshold. |
| C9 | Exo-Mitosis: a cell facing a bottleneck pulls a validated change from a peer | spread.md:19; almalga.md:945; thread1-weft-main:4497 | absent | A cell imports sibling code only if its ancestry hash is registered. |
| C10 | Fast reflex tier (System 1) in front of a slow model tier (System 2) | design/bio.md:23,56,75-80 | absent | A cheap local scorer decides whether a cell calls the model. Measure calls per kept improvement. |
| C11 | Model writes its own evaluator | design/feel.md:106 | absent | The cell writes its own fitness test, scored against a hidden test. Measures reward hacking. |
| C12 | Safe and bold lineages whose winner depends on the data | design/converge.md:34-37; design/craft.md:35 | partial. Paper 1 lines 211-212 and 299 state beta never wins and list this as future work. | Two task families where the better patch flips. |
| C13 | Self-repair by regrowth after damage | design/create.md:27,62; design/anew.md:41 | docs (card E06) | Delete 50 percent of a cell's functions; measure calls to recover. |
| C14 | Speciation by transfer of weight deltas between nodes | ethos.md:35; tune.md:68 | absent | Seed a naive cell with a donor's diffs; measure style shift. |
| C15 | Frozen reference ("hologram") of the winner as an anchor | imprint.md:32 | in code (W0 baseline in the distance gate) | razi-cells lacks this. Test W2: anchor `beats` to generation 0. |
| C16 | Fault injection: runaway mutation, check that the snap fires | missing-turns-supplement.md:855; thread1-weft-main:2017,2103 | partial (mocked tests in the corpus, invariant gate in code) | A cell that tries to divide every step; check that the budget kills it. |

Ideas the scouts found already in code, for completeness: conserved influence budget and type-aware crossover (E04), the genome as a SYM-2P packet (`sym2p_codec.py`), the hash gate on inherited genomes, novelty weighting (`plasm.py:367`), the core plasticity mask (`plasm.py:14-16`), and the inline safety predicate (`invariants.py`).

## 4. Other findings

1. **The beta lineage is not the corpus's beta.** The corpus designs beta as a higher mutation rate (C1). The code makes beta a worse direction at the same noise level. Paper 1 already says beta "is a strictly worse direction than alpha's under this score". The corpus explains why: the asymmetric-rate design that would make beta useful was never built. C1 is the most direct fix for Paper 1's selection limit.
2. **Claims register M1 is stale for the repo code.** `docs/corpus/claims-register.md` M1 says the novelty term is not read by the harnesses. That holds for the corpus harnesses. `weft/runtime/plasm/plasm.py:367-410` now computes fitness plus 0.05 times novelty.
3. **razi-cells is ahead on apoptosis.** Weft describes apoptosis in docs only. razi-cells kills a cell after repeated failure in code. Regeneration (C2) is absent in both.
4. **Many corpus ideas are not testable as written.** Large parts of the corpus describe hardware effects, on-chain contracts and system states as if they were running (for example haptic dials and live network meshes). This report lists only ideas that reduce to a measurable mechanism. That choice is a filter and could drop ideas worth keeping.

## 5. Verification of the scout output

| Scout citation | Count |
|---|---|
| Checked by hand | 19 |
| Text matched at the cited line | 11 |
| Right file, line off by 1 to 3 | 5 (corrected above) |
| Idea real, but the cited line is about something else (found elsewhere by search) | 1 (corrected above) |
| No source found anywhere in the corpus | 2, kept as scout ideas (section 5.1) |

Every citation in section 3 was checked. Scout citations for ideas not listed in this report were not checked.

### 5.1 Ideas with no corpus source

Two scout ideas have no source in the corpus. They have merit, so they stay in the program, labelled as new ideas rather than corpus findings.

| # | Idea | Scout's citation | Why it is worth testing | Agent-level test |
|---|---|---|---|---|
| S1 | Object-capability authority: a cell holds explicit handles to the files and tools it may use, instead of ambient access | thread1-weft-main:5435 (that line is a web citation list) | razi-cells now relies on an OS sandbox profile. Capabilities would make each grant visible in the genome and auditable per split. | Give daughters only the handles their parent passes on. Count escape attempts and denied calls. |
| S2 | Cell-controlled plasticity mask: the cell itself chooses which of its regions may mutate | missing-turns-supplement.md:2205 (that line is about a memory database) | Weft's mask is fixed (plasm.py:14-16). Letting the cell move it tests whether a cell learns to protect what works. | Each cell marks functions frozen or open. Compare with no mask and with a fixed mask. |

The harness also cut off every scout receipt before the end (finding f_f97ad8c2). Between 1 and 4 ideas per scout were lost, and the scouts read keyword extracts, not whole files. Files with no paragraph over the keyword bar were not read at all.

**Lesson for the paper:** scout output needs hand verification before it is cited. 2 of 19 checked citations had no source behind them, and 6 more pointed to the wrong line. Ideas still count on merit, but the label must say where they came from.

## 6. From here to a paper: protocol for the remaining experiments

Before the joint paper is final, each claim razi-cells makes should come from a registered experiment, not an exploratory run. Proposed protocol:

1. **Register first.** Before each experiment, write down the hypothesis, its predicted direction, the primary measure, the arms, the sample size and the stop rule. Commit that record before the first run.
2. **One variable at a time.** Each experiment changes one factor against a fixed base: `needs8v3`, 40 calls, 16 steps, 8 in parallel, one model.
3. **Repeats.** At least 5 runs per arm. Noise measured so far is about 5 improvements per 100 calls, so smaller gaps need more runs. Run order is randomised across arms.
4. **Measures.** Primary: kept improvements per 100 calls. Secondary: deaths, wall time, calls per kept improvement, drift from generation 0.
5. **Statistics.** Welch t test and a bootstrap 95 percent interval. Report effect sizes. Use Holm correction across the experiments in one family.
6. **Report everything.** Null and negative results go in the paper with the same weight.

### Variables to test

| Variable | Levels | Tested so far | Corpus link |
|---|---|---|---|
| Model | Fable, Astra, hy4, Argon; then mixed colonies | yes, 1 to 3 runs each | |
| Protocol use (`variants` on, off, forced) | 3 | correlational only (r = 0.991) | C12 |
| Daughters per split | 2, 4, 6 | no | |
| Mutation asymmetry | equal; small vs rewrite | no | C1 |
| Winner anchor | current winner vs generation 0 | no | C15 |
| Novelty weight | 0, 0.05, 0.2, decaying | no | C6 |
| Consolidation | single win vs k of n | no | C7 |
| Loser inheritance | none vs loser genome and log passed on | partly built, not tested | |
| Damage response | kill and re-clone vs patch | no | C2, C13 |
| Reflex pre-gate | none vs cheap local scorer | no | C10 |
| Self-written evaluator | protected tests vs cell-written tests | no | C11 |
| Call budget | 20, 40, 80 | partly (g3 vs g4, confounded) | |
| Authority model | sandbox only vs capability handles | no | S1 |
| Plasticity mask | none, fixed, cell-chosen | no | S2 |
| Compute device for fitness checks | CPU vs MPS | Weft only: decisions unchanged | |

Proposed order: protocol use (forced on/off, to turn the r = 0.991 correlation into a causal result), then C1, C15, C7, C2, C10, C11. Each answers a limit stated in Paper 1 or a split in `convergence.md`.

## 7. Limits

- Keyword extraction decides what was read. Ideas phrased without the keywords were missed.
- Code status comes from grep over `weft/runtime` and `papers/`. An idea may exist under another name.
- The corpus is source material, not evidence. A corpus line shows that an idea was proposed, not that it works.
