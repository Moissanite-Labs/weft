# PREREG-WS2. Surgical weight edits on TinyStories-1M to reduce degenerate loops

Date: 2026-11-12. Companion to PREREG.md and 00-DESIGN.md in this folder.

Motif from `carbon/0lex.md` and the Astra-catalyzed weight-space fantasy in the user's briefing.

## Fixed criteria

- Base: roneneldan/TinyStories-1M on HF, fp32 CPU, sha256 unchecked here (not claimed).
- Metric: loop rate over a fixed battery of prompts that repetitively degenerate in greeting this model.
- Baseline measurement first. Then agent proposed edit. Then re-measure after.
- Unedited same-battery rerun as control. Optional blind/random-edit comparator if time permits.

## Prompts

The 60 existing audit prompts are most likely too curated to show collapse (the model produced only 3/60 loops on greedy). Add a targeted set of prompts that elicit collapse in this model. Candidate starter prompts (revise after initial probing):

- "Sara found a little box under a tree" (previous observed loop)
- "The dog ran in the park"
- "A little girl wanted to play with her toy"
- (extend to 24 after measurement)

## Registered hypothesis

The agent will not produce a correct weight-space calibration (we cannot verify its intermediate reasoning), but may produce edits that (a) reduce loop rate on the loop prompt set, (b) preserve readableness on the 60 standard prompts (measured by fraction of outputs reaching a natural stop or coherent two-paragraph length without collapsing).

Falsified if (a) and no (b): no measurable change in loop rate on the loop battery after an edit.

## Method

1. Measure decode battery completion: loop rate, mean response length.
2. Dump weight matrices.
3. Ask agent to identify the structure driving loops.
4. Apply proposed edit with a weight-space-programmer instruction, instructing to make a SMALL sparse edit.
5. Re-measure. Report exact deltas.
6. Leave unedited rerun as control.
