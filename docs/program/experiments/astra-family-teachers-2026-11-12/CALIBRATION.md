# One-shot output-inversion calibration

Added before any successful teacher API response, following [the sibling review](https://github.com/Moissanite-Labs/weft/issues/145#issuecomment-6840204841). This is a separate transparent numerical-edit calibration, not an additional family-policy optimization round. It does not reuse the earlier toy checkpoint or reproduce its reported accuracy.

A locally trained NumPy 4→16→2 tanh MLP learns class 1 iff x[0] > 0.3. Outputs are linear logits. classification uses argmax.

Initialization seed 811. 1,024 uniform [-1,1]^4 training inputs seed 812. 1,600 Adam steps at learning rate .015.

The requested behavior is to invert every binary decision. Incoming hidden weights and biases remain frozen. only the 32 output weights and two output biases may receive additive edits.

Maximum 34 unique coordinates, absolute delta <=50. These calibration-specific limits are deliberately wide enough for an exact row-and-bias swap. the family-policy limits do not apply.

The gpt-6-astra teacher receives full source parameters, equations, and 32 independent examples (seed 813), each with original label, desired inverted label and original logits. One response is allowed, with no score feedback or revision. The same API transport and strict hypothesis/edits JSON convention apply. Output cap: 6,000 tokens. No inference-time teacher is present.

Primary held-out sample: 2,048 fresh uniform observations, seed 814. Diagnostic shifted sample: 2,048 independent observations, seed 815, transformed coordinatewise by sign(x)*sqrt(abs(x)). Neither held-out set is in the request.

The primary pass criterion is inverse-ground-truth accuracy >=.95, inversion of original model predictions >=.99, and exact frozen-first-layer equality. Report the shifted result separately. No secondary behavior preservation gate applies because inversion intentionally changes every class decision.

Report baseline original/inverse accuracies, exact analytic row-swap oracle inverse accuracy, teacher inverse accuracy, original-prediction inversion fraction, oracle-class agreement, maximum absolute deviation from swapped oracle logits, frozen-layer equality, and validity/error state.

The pass gate does not require identical oracle logits: a numerically different edit can correctly invert classifications. For example, negating both output logits reverses binary argmax decisions (apart from exact ties) without producing the same logits as a row swap. such an edit can pass even with nonzero oracle-logit deviation.

Unchanged-source and oracle controls are deterministic harness checks, not teacher candidates.

A failure indicates failure on this particular transparent calibration under its prompt and output constraints. it is not a logical disproof of all weight-editing ability.

A pass demonstrates this simple numerical edit and transport/validation path, not general understanding of neural weights, family transfer, or editing of pretrained language models. Report it alongside family outcomes without silently excluding failed teacher data or selecting a new teacher.

Commands:

```sh
python3 calibration.py prepare --out data/calibration
# The authorized API operator submits data/calibration/request.json once.
python3 calibration.py evaluate --out data/calibration
python3 calibration.py replay --out data/calibration
python3 -m unittest -v test_calibration.py
```

Artifacts are append-only: differing existing artifacts cause an error. Evaluation checks request reconstruction and configuration, records experiment/response/request/code fingerprints, and replay requires the original result and exact recomputation equality.

## Scramble-control interpretation

An exactly consistent hidden-unit permutation is a function-preserving symmetry: appropriately permuted edits should still succeed. Success after that permutation cannot establish that the teacher ignored weights, and failure should not be required as evidence of understanding.

A deliberately inconsistent shuffle of numerical matrix entries, coupled with truthful behavioral examples from the real source, instead tests the effect of corrupted weight evidence.

Keep its one-shot result paired with the real-weight first proposal for each source seed. do not compare it with the best of three feedback-assisted proposals. Report which tensors/entries were shuffled and whether activations stayed truthful.

Contradictory evidence may make a capable teacher fail or abstain, so the comparison is informative but not decisive proof of a single cognitive mechanism.

The review's blanket statement that tanh breaks signed re-pairings is too broad: because tanh is odd, flipping a hidden row and bias and its outgoing column together is also an exact symmetry. This experiment uses only permutations, so no broader symmetry claim is necessary.
