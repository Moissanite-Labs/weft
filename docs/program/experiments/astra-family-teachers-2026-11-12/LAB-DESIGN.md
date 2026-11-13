# Family policy editing laboratory

This laboratory tests whether a teacher can change a small controller by writing numeric weight deltas. The controller already follows goals and estimates hazards. The requested change increases avoidance in urgent, high-intensity situations while preserving its other behavior.

Capability identity: `weft.family-policy-weight-editing.v1`. Its responsibilities are bounded patch application, reproducible family transfer, retention measurement, and honest separation of selection data from final evaluation data.

The controller has eight inputs, ten tanh hidden units and three tanh outputs. Four hidden units have frozen incoming weights and biases. The other 87 parameters are editable. JSON checkpoints contain all weights and stable hidden-unit identities. The packet states the forward and target equations. It supplies no gradient or inverse solution.

Base weights are fitted locally with NumPy Adam to the old behavior. Teacher arms use no gradient updates. Four siblings inherit the trained weights, receive small independent perturbations, and permute their hidden units within the frozen and editable partitions. This creates related cells with different coordinate systems. It does not establish transfer between independently trained models.

Aligned transfer uses recorded ancestry to map each edited hidden unit. Raw transfer applies identical array coordinates. Alignment is therefore an oracle provided by family history, not an inferred correspondence. The test suite verifies that alignment preserves the exact edited function when sibling drift is removed.

Training observations, validation observations and both final test sets use different seeded draws. The shifted test draws denser obstacle and neighbor vectors. Sibling weights and final test examples are withheld from the teacher. The full benchmark and seeds are public for reproducibility. These are procedural holdouts, not a secret benchmark.

`teacher_packet(..., visibility="weights")` includes weights and hidden activations. `visibility="behavior"` removes both, retaining input/output examples, target equations and tensor shapes. This compares access to internal state as a bundle. It does not isolate weights from hidden activations.

Each patch is a data object containing unique tensor coordinates and finite numeric deltas. The validator rejects frozen coordinates, excessive deltas, duplicate coordinates and total L2 drift above two. Each proposal must be applied to the original source checkpoint. Chaining individually valid patches would defeat the total drift bound and is outside this protocol.

Controls include no edit, random deltas with the same support and norm, and local random search with the same number of validation candidate evaluations. The latter matches selection opportunities, not total compute or information. The gradient diagnostic uses 100 Adam steps and is neither compute matched nor subject to the teacher's delta bound.

The primary loss combines movement error, half the hazard error, and an additional penalty on movement in the unchanged context. The runner owns candidate acceptance and retention thresholds. Final evaluation must compare each sibling with its own unedited baseline. Thresholds and evaluation rules belong in the registered protocol before teacher calls.

`rollout` adds a shared torus with a moving resource, one hazard and several cells. Every step computes all actions before moving any cell. It records collision pair-steps, hazard cell-steps, goal progress and action energy. The teacher is absent. This result is exploratory because the static target was not optimized for closed-loop stability. There is no learned communication channel or reproduction.

## Instrument-development checks

Seven unit tests passed on 2026-11-12. They cover deterministic regeneration and JSON round trips, a competent source policy, atomic patch validation, exact aligned transfer, support/norm matching, packet isolation, and repeatable shared rollouts without mutation.

A seed-17 smoke run, performed during instrument development, measured source loss 0.008788, hazard MSE 0.001425 and unchanged-context movement MSE 0.000108 on its fresh test draw. Active-context movement MSE was 0.02119. These are setup checks, not confirmatory teacher outcomes.

The 100-step gradient diagnostic reduced active-context error to 0.01432 but raised total loss to 0.01194. Its hazard MSE rose to 0.003985 and unchanged-context movement MSE to 0.003019. The small training set can support changes that harm retention. Keep those metrics visible when judging a teacher patch.

Next action: run the registered visibility arms with all proposed patches and selection feedback saved, then evaluate heldout siblings and environments once. Any later adaptation to test results needs a new experiment version and fresh final draws.

```sh
python3 -m unittest discover -s docs/program/experiments/astra-family-teachers-2026-11-12 -p test_lab.py -v
python3 docs/program/experiments/astra-family-teachers-2026-11-12/lab.py --seed 17 --output /tmp/astra-family-lab-smoke
```
