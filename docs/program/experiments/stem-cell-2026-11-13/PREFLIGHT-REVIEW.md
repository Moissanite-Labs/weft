# Stem-cell pilot preflight review

Reviewed by gpt-forge (Astra), 2026-11-13. The reviewer authored the Lean policy and lifecycle gates, then independently inspected the separately authored colony, experiment runner and API worker. This is an independent integration/scientific review, not an independent authorship review of the Lean core.

The meaningful first-wave claim is narrow: a teacher proposes typed integer controller genomes. local action caps can only tighten along a selected lineage. concrete policy execution, trajectory costs, root/local invariants, stable selection arithmetic and bounded clone allocation are checked by Lean. The root reserve remains fixed.

The host binds proof artifacts to actual requests and saved decisions. No model-authored code or Lean text is accepted.

## Checks and resolved findings

Five proof-gate tests passed, including real Lean rejection of fabricated action, state, per-step cost, total cost and final state. weakened inherited caps are rejected. Two lifecycle tests passed, including wrong winner, wrong tie choice and changed clone genome. A 96-step concrete batch checked with an empty axiom set.

Raw positive and negative controls are retained under `data/proof_fixtures`, `data/lifecycle_fixtures` and `data/proof_batch_size_smoke`.

The independent integration run submitted four explicitly synthetic genomes through one complete round with actual Lean checks for the parent, fixed control, four teacher-slot proposals, four random controls and both selection decisions. It made no API calls. All four synthetic proposals were valid.

the selected fixed-policy control reduced validation cost from 698 to 494. This validates the pipeline, not Astra performance. Raw inputs, outputs and proofs are retained under `data/validation/independent_round_smoke`. a second run under `independent_round_smoke_bound` exercises the final binding checks.

Three binding issues were identified and fixed before paid calls (the first two by this review, the third by the lead):

1. A response at the expected filename was previously consumed without validating the API worker's recorded request filename and exact wire SHA. The runner now checks those fields, the registered prepared request and the precise permitted prepared-to-wire transformations before evaluating candidates.
2. Replay previously ignored saved code hashes, and selection reuse did not verify its journal digest or retained certificates. Registration now pins executable experiment sources. reuse checks the journal record and retained artifact hashes. replay checks code plus heldout and colony arithmetic.

3. The lead identified that initial registration did not seal the experiment episode files. Registration now hashes every experiment file. an independent targeted probe accepted pristine inputs and rejected both validation and heldout target mutations before any evaluation. Raw inputs, mutations and results are in `data/validation/episode_sealing_probe`.

The post-fix independent probes confirmed rejection of a wrong response filename, wrong wire hash, modified selected genome, modified certificate and changed code pins. All five were rejected. Their exact outcomes are saved in `data/validation/independent_round_smoke_bound/binding_regressions.json`.

Original pre-fix integration evidence is retained separately. These are protections against misbinding and mutation, not authentication against a host owner replacing both the checker and the entire evidence record.

## Scientific interpretation required

- There are two source seeds, two demand branches and two generations. Treat results descriptively. Multiple children, clones and episodes do not create additional independent source seeds.
- Within each source seed, targets, urgency and initial states are paired. the intervention changes tracking-versus-action cost weights. This tests demand-conditioned controller differentiation. Demand weights do not reverse within a lineage, so this run does not test recovery from a later ecological reversal.
- Local contracts consist of tightening two action caps under immutable root constraints. The root reserve is available for dispatch, but restarting evolution from that reserve after an unforeseen demand change is not evaluated.
- Random generation-two proposals use the teacher-selected parent. They are a matched local proposal control, not an independent two-generation random evolutionary lineage.
- Validation feedback is used adaptively. Final test episodes must stay unavailable until selections are locked. The fixed hand-designed policy is an important conventional baseline. improvement over the original root alone does not establish an Astra advantage.
- Clones repeat a selected controller and receive episodes by round-robin dispatch. This demonstrates allocation and execution, not a throughput advantage from additional copies. Episodes begin at the registered initial state. the experiment does not demonstrate arbitrary persistent-state cloning.
- Apple memory-pressure observation controls bounded CPU compiler concurrency at batch boundaries. It is a real host scheduling mechanism, outside Lean, and is not a Metal/GPU or performance scaling benchmark.

The Lean theorems concern exact finite integer records and their defined policy/score semantics. Selection certificates take host-bound score and eligibility inputs. they do not independently import every earlier theorem as a composed proof.

Python, filesystem persistence, actual compiler execution, API provenance and hardware remain trusted boundaries. Nothing here changes Astra's weights, permits general self-modifying software, or establishes mathematical causality for arbitrary physical effects.
