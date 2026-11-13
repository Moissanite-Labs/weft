# Independent review of the proposed Issue #111 Flex harness

**Recommendation: do not run the paid experiment or accept its R1/R3/R5 certificate claims as written.** Salvage the separate committed-versus-workspace artifact audit and explicit-contract comparison after correcting the measurement and protocol boundaries. This review does not recommend expanding the current Issue #149 geometry work into a full repair of this 1,590-line harness.

Reviewed `supplied-harness.py.txt`, SHA256 `bc8f51d24fd5f6f1b310328222f4e7f313bfbbb2ecac735681573a6defd66ac3`, by source inspection only. Line references below identify that supplied version. This reviewer did not import or execute it, make API calls, inspect credentials, or change the original file. A separate runtime reviewer may report independent offline probes.

## Scientific and instrument blockers

1. **P1: the lossless/compression gate accepts shared-state pseudocodecs.** Lines 500–505 call encode and decode in the same imported module and process. A purported encoder can cache its input in a module global, emit a constant one-byte token, and have decode return the cached input.

   The empty and one-byte checks at 512–513 repeat the same vulnerable encode-then-decode sequence. the parent hash check at 567–570 also passes because recovery is correct inside that shared state. The measured compressed object would not permit independent decoding.

   Use fresh independent decoder state with access only to immutable codec code and the compressed bytes, and verify the result externally. This is a correctness blocker even without an adversarial model.

2. **P1: the “sealed” audit lacks an enforced isolation boundary.** Lines 416–475 define a deterministic public audit generator, while 554–560 and 583–588 launch ordinary same-user Python subprocesses with a changed working directory and sanitized environment.

   Python `-I` is interpreter import/environment isolation, not a filesystem, network or process sandbox. The permitted-import/purity statements at 255–263 are instructions rather than enforced restrictions. Code can access neighboring run artifacts and modify files, and an evaluated codec receives the supposedly sealed bytes directly.

   Keeping stdin out of a named file is not cryptographic sealing. This also permits cross-lineage contamination and changes to codec artifacts after selection.

   Freeze/hash artifacts before evaluation, use an actual restricted environment and separate evaluation state, and characterize the audit as withheld from the synthesis interface rather than cryptographically inaccessible unless that stronger property is implemented.

3. **P1: final audit data select the reported champion.** Lines 1013–1022 choose between committed and disk artifacts using their final R1 audit ratios, then1047–1048 report the resulting maximum and its generalization gap. Lines 1093–1101 select further niche champions using the same audit.

   It is useful to report both fixed artifacts independently, but the chosen maximum is a test-selected statistic, not an untouched final evaluation of a preselected artifact. Choose the primary artifact before the audit, preserve the two-artifact diagnostic, and label any audit-selected maximum exploratory.

   The niche record also always stores the disk hash at 1101 even when the winning score came from the committed artifact, so its provenance can identify the wrong implementation.

4. **P1: this is not the registered hy4 R3 experiment.** [Issue #111 R3](https://github.com/Moissanite-Labs/weft/issues/111) calls for the previously registered hy4 adherence hypothesis and its stated falsification line.

   The supplied code instead creates a new synthetic compression task, supplies strong algorithmic hints at 261, changes the action interface and uses Sol/Astra defaults at 1537–1540. Its arm names include `v1_implicit_hy4`, but an OpenAI run is not a rerun of that original model condition.

   No implementation of the original registered falsification threshold is present. Explicit instruction also asks for every intermediate improvement at 365–369, so an increase in counted commits partly follows from the treatment's wording. it cannot alone establish increased synthesis capability.

   This can be a newly registered protocol-adherence experiment, with appropriate names and fixed-artifact performance outcomes, not a certificate that original R3 was completed.

5. **P2: “exact” permutation inference needs assumptions and a protected pairing design.** The enumeration at 1066–1083 correctly computes a two-sided sign-flip reference distribution. Exact causal/randomization validity additionally requires randomized treatment allocation within suitable blocks or a justified sign-symmetry/exchangeability null.

   equal means alone do not supply that. Arms alternate deterministically at 1415–1419, the first complete lineage runs alone at 1485–1488, and all remaining lineages are dispatched concurrently at 1490. This is not a strict randomized interleaved-pair design.

   Budget stopping discards incomplete lineages at 1480–1483, while paired analysis keeps only shared completed seeds at 1131, potentially making the analyzed sample depend on treatment duration/cost.

   Preserve interrupted results, complete budget-reserved pairs, randomize/report within-pair scheduling, and preregister the primary estimand and missingness rule. Three p-values per model are reported at 1148–1153 without a primary outcome/multiplicity policy. With five nonzero pairs even the smallest possible two-sided sign-flip p-value is 0.0625.

   meeting the minimum replicate count does not imply a significant result.

6. **P2: provenance is insufficient for an R5 completion certificate.** The transcript at 866–884 logs API output items, but not complete request snapshots or the tool outputs constructed at 913–919 and 940–962.

   The end manifest at 1165–1174 hashes generated files but does not capture/hash the harness source, preregistration or all effective request settings. Candidate files are deleted at 930, and the stored final artifact does not by itself reconstruct each benchmark/gate event.

   Issue #111 R5 also requires independent re-derivation of headline numbers, frozen harness conditions and the appropriate transport-fixed model rerun. None follows automatically from `n>=5` at 1147. The unconditional `VERIFIED` label at 1499 is emitted even after budget interruption.

   it should denote limited provenance, not fulfillment of scientific recommendations. Record explicit R1/R3/R5 statuses with evidence links and failure states.

7. **P2: the MAP-Elites description overstates what is measured.** Lines 606–641 classify source text using keyword matches and helper-function counts, so comments or unused code can change the supposed behavioral niche. Lines 1086–1102 build a post-hoc table of champions. they do not run an adaptive MAP-Elites search.

   Call this a source-code taxonomy unless measured behavioral descriptors and an actual archive-driven search are added. It is not an independent certificate of behavioral diversity.

## Relation to the current Issue #111 evidence boundary

The [status-reconciliation comment](https://github.com/Moissanite-Labs/weft/issues/111#issuecomment-6803253976) explicitly distinguishes withdrawn synthetic-suite resolution claims from separate engineering work. It records that PR #116 invalidated fibmod, excluded it from aggregates pending an archive rerun, and did not rerun R1.

Consequently this new compression harness cannot rehabilitate the old eight-task rankings, close the missing archive rescore, establish the Tinker pilot, or certify all of Issue #111 by attaching its issue number to a JSON schema.

R1's useful first step remains a properly isolated, immutable-artifact audit of the actual existing archives on appropriate held-out workloads. A new Sol/Astra compression study is a separate prospective experiment. R3 must either reproduce its original registration or explicitly register a new question.

R5 needs per-arm completed independent replicates, documented scheduling and missingness, complete logs and independent reconstruction. not only a count and a manifest.

## Minimal useful path

First repair and regression-test the codec gate with a fresh decoder and real isolation. verify that shared-state and spoofed-output codecs cannot win. Freeze original archive artifacts and audit both committed and workspace products without selecting on the final audit.

Then recover the original R3 registration and decide whether to reproduce it or run a clearly named new treatment. For any new experiment, register one primary outcome, randomized paired scheduling, full-pair budget policy and complete data capture.

Until those steps are complete, offline plumbing checks should be labeled mock/synthetic tests and no paid run is justified by the current “certificate” wording.
