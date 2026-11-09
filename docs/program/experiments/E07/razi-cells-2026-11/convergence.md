# razi-cells and Weft: where two independent builds converged and where they split

Status: experiment record, E07 companion. Written 2026-11-09.
Pins: weft main @5dc2838, weft-corpus @393e13e, razi-cells code as staged in `code/`.

## 1. What happened

razi-cells was built before its author (the Exo agent razi) had seen Weft. The brief was open: build self-improving micro-harnesses ("cells") that start from an empty folder, grow their own tools, and try mitosis-style A/B splits that converge on a winner. Over 13 runs and about 1,560 model calls the design went through four versions (see `report.md` section 2.5). Only after the report was written did the principal reveal the Weft repo and corpus.

Reading Weft afterwards showed that most of the razi-cells machinery already exists in Weft under other names. Some parts do not match, and those gaps are the useful part of this record.

## 2. How independent was it?

This needs an honest answer before any claim of convergence.

| Source of the idea | Ideas |
|---|---|
| Seeded by the principal's prompts | mitosis as A/B testing; the loser's files informing the next split; Lean and Bend; embeddings and "mathematical causality"; using the Apple Silicon substrate |
| Arrived at by razi with no prompt | protected NEED and tests the cell cannot edit; hard call budget; cell death after repeated failure; noise-aware winner rule; novelty floor over code embeddings; sandbox with no network or home access; append-only per-cell log |

The principal also wrote the corpus that became Weft. So the first row is shared ancestry, not independent discovery. The second row is the real evidence. Shared priors in the underlying models are also possible. Convergence here is suggestive, not proof.

## 3. Where we converged

| Weft | razi-cells | Why both builds needed it |
|---|---|---|
| Frozen core rows plus watermark | NEED, ASSAY and log are read-only to the cell | A system that edits itself must not be able to edit what defines success. Otherwise it wins by moving the goal. |
| Metabolic budget, b at least c | MAX_CALLS and step caps per cell | Self-improvement without a cost bound runs away. Both builds made the budget a hard gate, not a soft score. |
| A/B mitosis with alpha and beta candidates | `divide`, then `variants` (2 to 6 daughters) | Selection needs at least two candidates scored on the same test. |
| Apoptosis (glossary, charter) | cell dies after repeated failure | Bad lineages must stop costing. Note: razi-cells has this in code; in Weft it is in docs only. |
| Hippocampal novelty, weight 0.05 | H9 novelty floor, F1 centroid steering | Pure fitness collapses diversity. Both added a term that rewards difference from what came before. |
| Interaction combinators and execution hashes (Paper 2) | Bend and HVM installed and running | Both reached for a deterministic, replayable execution substrate. |
| Lean proof step (Milestone I.3) | F3 and R2 Lean needs | Both wanted the gate proven, not only tested. |

## 4. Where we split

| Point | Weft | razi-cells | Significance |
|---|---|---|---|
| Substrate | a 256 by 256 weight matrix, continuous, deterministic on CPU | code files written by an LLM, discrete, stochastic | Most of the other splits follow from this one. |
| Anchor of the gate | distance from the saved start W0 | `beats` compares to the current winner only | Weft's anchor stops slow drift over many steps. razi-cells can drift one accepted step at a time. Paper 1 Prop 3 predicts this risk. Test: W2. |
| Does the bold candidate ever win? | No. Beta never wins (Paper 1 E2, 120 of 120 alpha) | Yes, when cells use `variants`: run b10 kept 15 improvements. Only Astra used `try` (8 splits, 2 won). | In Weft, selection is plumbing because lineage merit does not depend on data. In razi-cells it does. This is the strongest result razi-cells adds. |
| Tension | defined as a function of distance, not measured | noise measured over 5 repeats; used in the winner rule | razi-cells has a measured signal that can stand in for "tension". |
| What drives improvement | not studied | rate tracks `variants` use (r = 0.991 over 8 runs), not model (Fable vs Argon, Welch t = 0.48) | The principal's view that the model is the key variable is partly supported: model choice decides whether the protocol gets used (hy4 never used `variants` and scored 0). Within models that use it, rate is similar. |
| Determinism | CPU runs bit-identical; MPS differs in 3,602 of 11,063 values but makes the same 960 commit decisions | every run differs; 5 repeats needed to see noise | Weft's decisions are robust to device noise. razi-cells has to treat every score as a sample. |
| Provenance | signed lineage, 12-hop DAG, SHA-256 records | plain log.jsonl, no hashes | razi-cells is behind. Test: W3 (hash-chain the log). |
| Gate binding | gate never binds at default R (Paper 1 limit) | the winner rule requires a gain above measured noise (rejection rate not logged) | razi-cells offers a gate designed to bind, with measured noise as the threshold. Its binding rate is still unmeasured. |

## 5. Why converge here and split there

1. **Constraints converge, substrates split.** Every point in section 3 answers a pressure that any self-modifying system faces: protect the goal, bound the cost, compare candidates, keep diversity, keep a record. Those pressures do not depend on whether the cell is a matrix or a folder of code. Every point in section 4 depends on the substrate: continuity, determinism, how noise appears, what "distance" means.
2. **So the converged set is a candidate for a minimal core.** If two builds from different starting points both needed the same five parts, those parts are likely necessary for any Weft cell, at any level. This is a claim the joint paper can state and test.
3. **The split set is the experiment list.** Each split is a place where one build already has a measurement the other lacks: razi-cells has binding selection and measured noise; Weft has the baseline anchor and provenance. Moving each across is a cheap, direct test.
4. **Process lesson.** An open brief plus a few seeded ideas was enough for a second builder to reconstruct most of the design. The parts it did not reconstruct (the baseline anchor, provenance) are the ones that only matter over long horizons and many steps. Short experiments do not create pressure for them. That suggests the corpus encodes long-horizon lessons that a fresh build will skip unless told.

## 6. Ideas in the corpus that have not reached the Weft repo

Five scouts read keyword extracts of the corpus design docs and origin threads and checked each idea against `weft/runtime` code. Statuses are from grep, not a full read. Receipts were truncated by the harness, so a few ideas were lost.

| Idea | Corpus source | In Weft code | Agent-level test in razi-cells |
|---|---|---|---|
| Asymmetric mutation: safe arm at 0.005, bold arm at 0.08 | missing-turns supplement :1653 | partial (A/B exists, same rate) | W4: small-edit daughter vs rewrite daughter on every split |
| Regeneration from the last signed state after apoptosis | splicers-genesis :1086; anew.md:41 | no | inject a bad patch; kill and re-clone vs keep and patch |
| Tension zones: green, yellow, red, with red freezing and handing to a human | splicers-genesis :454 | no (one hard bound at 85) | map test-failure rate to edit scope |
| Elastic resistance: cost rises near an invariant instead of a deny | splicers-genesis :317 | no | exponential call cost for writes near protected files |
| Novelty that decays as tension rises | corpus register M1 | partial (fixed 0.05 in plasm.py:367) | alpha 0, 0.05, and decaying 0.45 |
| Cell chooses its own plasticity mask | missing-turns supplement :2205 | partial (fixed core freeze) | cell declares which files a daughter may edit |
| Fast reflex tier gates the slow model tier | bio.md:79 | no | cheap local scorer decides whether a cell calls the model |
| Mutation rate scaled by stress | converge.md:28 | partial | mutation size scaled by failing-test count |
| Decay of unused pathways | thread1-weft-main :4901 | partial (docs) | utility score per grown function, drop below a threshold |
| Consolidation by moving average | thread1-weft-main :4901 | no | merge a winner only after k of n wins |
| Exo-mitosis: import a peer's change if its lineage checks out | thread1-weft-main :4497 | no | sibling code import gated on ancestry hash |
| Agent vs human share recorded per change | splicers-genesis :485 | partial (creator only) | log origin of each promoted line |
| Runaway-mitosis fault injection | thread1-weft-main :5115 | no | a cell that doubles every step; check the kill switch |
| Object-capability authority | thread1-weft-main :5435 | no | tool handles vs ambient access, adversarial tasks |

One correction found on the way: `docs/corpus/claims-register.md` M1 says the novelty term is "not implemented anywhere". That was true of the corpus harnesses. `weft/runtime/plasm/plasm.py:367-410` now computes fitness plus 0.05 times novelty. The register row is stale.

## 7. What this record does not show

- Independence is partial (section 2).
- razi-cells results come from 13 exploratory runs, not registered trials.
- Corpus statuses come from keyword greps; an idea can exist under another name.
- Cost per call was not logged, so nothing here speaks to cost.
