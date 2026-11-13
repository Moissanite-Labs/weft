# PREREG-WS1. Weight-space programming on TinyStories-1M, registered before any agent call

Date: 2026-11-12. Owner confirmed this arm: try one of the models identified in issue #142 as the base, attempt direct weight editing, and let the OpenAI key assist the work if needed.

## Registered clauses

- H1: with only config + weight statistics in context (no text examples from the model), the agent replies with at minimum one of: children, stories, narratives, English, simple. Free-form. Two independent judges agree. Falsified otherwise.
- H2: the agent names the top-2 transformer blocks (by weight-based criteria only) that drive repeating n-gram generation at looping prompt states as measured by our module-level ablation. Hits measured against ablation ground truth. Falsified if none of the two matches.
- H3: a sparse or rank-one patch the agent proposes (≤ 1e-3 of total parameters modified) reduces the looping rate on our 60-prompt battery by at least 33% absolute vs baseline without dropping distinct-2 ratio by more than 15%. Falsified otherwise.
- H4 (control): an ablation-marker baseline (our own ablation study, zeros on the ground-truth blocks, no agent) reduces looping similarly or better than H3's patch. Falsified if the agent beats the control, i.e., it did real work the control could not.

## Battery

60 fixed prompts written by hand, children-story policy (short openings, e.g., "A little dog named Max wanted to ..."). All 60 follow the same template family to stay in-distribution for our corpus.

## Budgeted calls

Approximately 8 agent round-trips for identification, 2 for patch proposals, full battery re-measure locally. Under $10 expected.

## Stop rule

If H1 or H2 fail decisively (e.g., the agent guesses a completely unrelated architecture or gets zero overlap with ablation), stop and report as a miss. No retry with a different framing. The first answer is the answer under this preregistration.
