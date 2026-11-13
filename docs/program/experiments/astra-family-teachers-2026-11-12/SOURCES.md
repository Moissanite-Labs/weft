# Evidence for Weft weight editing experiments

Research support: gpt-forge, model gpt-6.1-sol. Checked 2026-11-12. Source inspection only. No model experiments were reproduced here.

The four supplied articles trace to the authors' [November 2 research blog](https://rikiyat.github.io/blog/weight-space-programming/), rather than four independent demonstrations. It reports these distinct conditions:

| Task | Scale and access | Result and boundary |
| --- | --- | --- |
| Identify games | 17,253 weights as text. No tools | Four game identities recovered |
| Identify generated shapes | 23,824 weights. No forward passes | Shape identities recovered. Filled shapes misread as outlines |
| Identify training language | 7.16M parameter character models, middle blocks only. Python | Three corpora identified. Copying heads matched measurements |
| Repair car policy | 171,664 weights, scene and recorded failure. One reply | 3.5% edited. 1,024/1,024 successes |
| Write MinAtar policies | 600→32→32→6. Text weights, rules and source | No tools or feedback. Outperformed 100M-step PPO |
| Write Go policy | 1,480,274 weights. Python. 0–50 feedback calls | Generated numerical program. Strength depended on feedback and opponent size |
| Identify sycophancy | Paired Gemma 270M | Weight-only identification failed. Attention probes helped |
| Improve math | Qwen 0.8B. Python plus 10/25/50 feedback calls | 50-call edit raised MATH-500 7.9→48.1%. Loop repair, not demonstrated new math skill |
| Improve non-looping math | Gemma 270M | No established improvement |

The report prohibits gradient training. These conditions distinguish literal text edits from programs that calculate tensor replacements and from feedback-guided search. They do not demonstrate autonomous modification of Astra's own weights.

The [released edit manifest](https://raw.githubusercontent.com/RikiyaT/lm_understand-logs/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/edit/manifest.json) identifies only layers 15 and 19 MLP down-projection matrices, each shape 1024×3584. Each targets 64 columns. Of 131,072 addressed slots, 130,188 bfloat16 entries differ in bits. Rounding explains the difference. 

Relative changes across the two complete matrices are about 10.6% and 8.1%. Small edit counts do not imply small functional effects.

The [agent's final submission](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/final_answer.md) reports dose-response, isolated-layer and norm-matched random controls. On held-out practice examples it reports 579 rescues and five regressions. 576 rescues had originally been truncated. 

This directly supports diagnosing a failure mode. These are practice results, separate from benchmark evaluation.

A [separate baseline investigator](https://github.com/RikiyaT/lm_understand-logs/issues/4) reports that sampling and thinking settings materially change the untouched model's score. That is a reason to run matched configurations, not a reason to subtract unlike scores. 

The [released checkpoint](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming) also permits rebuilding and testing the artifact independently.

## Proposed Weft controls

These are experiment recommendations, not claims demonstrated by the cited work.

1. Freeze the colony-family model and evaluation seeds. Give teacher cells copies. Save every proposed patch before evaluation. Hash the initial model, patch and resulting model.
2. Split teacher-visible training situations, development situations and a final unseen ecology. Count all feedback samples, episodes and tokens, rather than calling a batch one inexpensive pass.
3. Compare unchanged, teacher-edited, norm-matched random, shuffled-target, simple hand-coded and gradient-trained variants. Match resource budgets when comparing efficiency. Keep a separately labeled zero-feedback teacher arm.
4. Test causal specificity: individual edited layers, sign reversal, dose response and removal of the teacher patch. For model families, compare patch transfer to a related seed and an unrelated family.
5. Separate repairing a known obstacle from teaching a missing skill. Include a deliberately damaged policy with a known causal defect and an intact policy that lacks the desired capability.
6. Measure colony survival, resource use, task success, diversity and failures outside the teacher's target. Report per-seed changes and uncertainty, including regressions and rejected edits.
7. To test whether the teacher uses weights, include a task-description-only arm and hidden neuron permutations that preserve the original function. Also test action/channel remappings. Familiar game rules can support writing a policy without interpreting the inherited policy.
8. Keep direct finite tensor patches, generated programs that write tensors, gradient updates and prompt-only assistance as separate conditions. A teacher suggesting a learning-rate change is a training controller, not evidence of direct weight understanding.

The first useful Weft claim would be narrow: teacher cells make persistent, reproducible improvements to frozen family policies under unseen ecological conditions, beyond equal-budget controls. General weight understanding, capability transfer and recursive self-improvement need their own tests.
