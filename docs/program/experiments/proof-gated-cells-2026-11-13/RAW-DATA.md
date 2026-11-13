# Scientific raw-data access and capture

This index makes the scientific evidence retrievable from the repository. The folder uses the UTC date November 13, 2026. The user began this work on November 12 in local time. No API calls or credentials are required to retrieve the archived evidence.

RAW-DATA-INDEX.json records byte lengths, SHA-256 hashes, exact source commits and remote links. The audit checked repository reachability and file bytes. It did not rerun model calls or floating-point experiments.

From this directory, verify all indexed evidence without regenerating it:

```sh
python3 verify_raw_archive.py --fetch
```

The optional fetch retrieves the two public pull-request refs and the preserved history branch. Omit `--fetch` when their objects are already available locally. The script checks 140 repository files and the newly supplied local attachment. It makes no model API calls.

## Earlier teacher experiments

All 96 original paid response files are tracked at [the audited teacher-study head](https://github.com/Moissanite-Labs/weft/tree/cc3d02523c6d6ff6156c78ea34637d63fd1ca0d6/docs/program/experiments/astra-family-teachers-2026-11-12). Requests, candidate patches, rejection decisions, measurements and reviews remain part of that record.

Response artifacts retain observable answers and token accounting, excluding internal reasoning items and credentials.

The 37 large generated files removed from the current tree remain in [the original remote history](https://github.com/Moissanite-Labs/weft/tree/record/astra-teachers-prereg-history-20261112). That branch points to commit `d85940c0d078b54f40f4742b33c286c521164567`.

The audit read all 37 objects and verified all byte lengths and SHA-256 hashes, totaling 52,076,501 bytes. These include source experiments, numerical results, the calibration experiment and fidelity oracles.

The [restoration script](https://github.com/Moissanite-Labs/weft/blob/cc3d02523c6d6ff6156c78ea34637d63fd1ca0d6/docs/program/experiments/astra-family-teachers-2026-11-12/restore_generated.py) retrieves the original bytes and checks the recorded hashes. From a checkout of the teacher branch:

```sh
cd docs/program/experiments/astra-family-teachers-2026-11-12
python3 restore_generated.py
```

This is restoration from preserved git objects, rather than regeneration from seeds. The original macOS arm64 numerical results have documented Linux x86_64 replay limits. Hash verification proves byte identity, without establishing cross-platform numerical reproducibility.

## Earlier supplied-harness review

The separate [Flex harness review archive](https://github.com/Moissanite-Labs/weft/pull/151) contains the supplied source, portable reproduction script, recorded observations, sanitized selftest output and scientific/runtime reviews. Its exact file hashes and source URLs are listed in the index.

The offline probes used mocked transport and synthetic files. They made no API calls and did not repair the supplied harness.

## New supplied Lean harness

The new attachment is preserved verbatim as inputs/supplied-lean-harness.py.txt, with its digest in inputs/SHA256SUMS and the index. It is a data attachment. This archival step inspected the text for credential patterns and personal absolute paths and did not import or execute it. Placeholder key examples are source text, without actual credentials.

HARNESS-REVIEW.md separately evaluates its claims and trust boundaries.

## New proof-gated prototype capture

Every proposed transition belongs in the record, including invalid requests and rejected proofs. The prototype must retain the exact transition request, proof source, verifier input, compiler stdout and stderr, exit status, accepted proof artifact, before/after state hashes and chained event record.

Preserve fixed fixtures, adversarial examples, test results and verifier/toolchain identities alongside successful examples.

The new local work makes no model API calls, so there are no new API prompts or paid model responses. Proof requests and supplied proof text are the relevant inputs. Do not label an absent model call as a missing response.

Compiler acceptance establishes the formal statement checked under the recorded assumptions and toolchain. It does not establish that an external physical action occurred, that a specification captures every intended property, or that arbitrary runtime effects have been formalized. Capture any bridge between the mathematical state and runtime execution as its own explicit assumption or checked interface.

Credentials, internal model reasoning, sensitive personal paths and unrelated private data are outside the archive. Scientific inputs, observable outputs, errors and rejected cases remain available. The final prototype manifest should hash every new fixture, proof request, compiler log and proof artifact after capture, so reviewers can verify the exact evidence without relying on a local machine.

## New prototype artifact policy

The repository includes authored source, all captured fixtures, JSON-RPC transport records, accepted and rejected transition records, generated proof source, compiler stdout/stderr and exit statuses, test output and replay results. MANIFEST.json records the final bytes and SHA-256 of this package.

Derived Python caches, Lean object files and transient writer lock files are excluded. They are not authored scientific input.

The supplied-harness control log normalizes compiler-command metadata from machine-specific executable and temporary-directory paths to `lake` and `<scratch>/Empty.lean`. Compiler stdout, stderr and exit statuses are unchanged. No transition, proof source, measurement or rejection decision was removed by that normalization.
