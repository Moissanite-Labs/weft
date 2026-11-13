# Weight-space programming experiments (2026-11-12)

Exploratory record. Nothing in this directory is a registered arm of the program. Everything is labeled. Reviewers decide what, if anything, graduates.

Line of enquiry: can a strong teacher (gpt-6-astra) read a small model's raw weights, propose a direct numerical edit, and have that edit matter in controlled measurements, with no training allowed?

## Headline arithmetic (by files in this directory)

- Toy MLP classifier (`weight-space-sandbox.py`, `toy-classifier.pt/json`): teacher proposed `fc2.weight.flip(0)` and `fc2.bias.flip(0)`. Applied: accuracy 0.9805 to 0.0195 on identical inputs. Same-distribution, no held-out split. The one clean feedback-free tensor edit verified so far.
- TinyStories-1M row-scale edits (`measure_edit2.py`): h.6 q_proj row 30 *0.25 mixed outcomes (4 of 8 loop prompts improved). h.2 q_proj row 0 *-1 shifted global behavior, did not improve looping. Did not produce a reliable fix.
- Reading verification: teacher identified rows 18 and 30 as conspicuous in h.6 q_proj. Independent check confirms these are the two largest-norm rows (2.46 and 2.80).
- Ablations (`ablation-*.json`): scaling q_proj of layers 2 and 6 jointly had no monotonic effect on distinct-2 or loop score. Zeroing block 0 nearly wipes the model. Blocks 4/5/6 show largest weights. Structural signal only, not proof of causal role.
- NC1 negative-control suite. Prereg `PREREG-NC1.md`. Results `RESULTS-NC1.md` with raw responses in `nc1-responses.json` and `nc1-goodstats-full.txt`.
  - Pure noise: no confabulation.
  - False stats block (row 17 norm 15.3, row 48 norm 2.2): teacher caught the contradiction using real cell values (norm lower bound 2.46 against 2.2) and refused to edit.
  - True stats: agreement confirmed quantitatively, including an F-norm identity. Heuristic shrink of the five highest-norm rows proposed, labeled unproven.
  - Repeat call: verdict stable, reasoning re-derived, not memorized.
- Instrument misses, preserved in place. Aliasing bug printed identical pre/post row norms in the first measurement script.
  An argmin/argmax typo displayed a healthy checkpoint as 0-accuracy. A 1500-token output cap truncated one answer mid-part-(b) (re-run at 3200).
- WS3 purpose-built organism (`organism_train2.py`, `train-proper.py`, `organism-final.txt`, `PREREG-WS3.md`). Selection-only training reached scratch score 11.8 vs 2.1 at init over 40 generations. The planned teacher-flip-on-organism arm was never run. Scratch build, not a registered artifact.

## Files of note

- `probes.txt`: 24 evaluation prompts. Loop subset indices 0, 5, 6, 9, 11, 12, 18, 20.
- `stats.jsonl`: per-tensor norms, max/min/mean/std for all TinyStories-1M matrices.
- `h{2,3,4,5,6,7}-*-matrix.txt`: raw matrix dumps given to the teacher.
- `ablation-*.json`, `ablation-log.txt`: layer-zeroing ablation deltas.
- `base-""$(date +%Y%m%d-%H%M%S)"".json`: duplicate baseline produced by a shell-quoting bug. Retained verbatim, not edited.

## Reproduction

- `python3 organism_train2.py` and `python3 train-proper.py`: numpy-only torus organism (seconds, local CPU).
- `/Applications/Xcode.app/Contents/Developer/usr/bin/python3 measure_edit2.py`: before/after edit comparison on the loop prompts.
- `python3 weight-space-sandbox.py`: trains the toy classifier. Note the printed "accuracy" line uses argmin and is meaningless. The checkpoint is fine, see `RESULTS-NC1.md`.
- `OPENAI_API_KEY=... python3 nc1_run.py`: re-runs the four NC1 calls.
- TinyStories numbers require `transformers` and `torch`. The local runs here used Xcode's python.

## Secrets

Scanned: no credentials, keys, or tokens in this directory. The API key used this session was passed inline via environment and was never written to files.

This PR is the record. An earlier message to A claimed this workspace had been synced to a PR branch as `docs/program/experiments/weight-space-2026-11-12`. That was false. This is the actual sync.

Credit: experiments and measurements by this seat. Edit candidates and toy-flip insight proposed by gpt-6-astra.
