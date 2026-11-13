# Astra family teacher experiment

This experiment tests persistent numerical edits to small policy cells and transfer to related siblings. All four studies are complete, with 96 archived paid responses. The completed inversion calibration passed its registered gate. It does not establish family-policy improvement or editing of pretrained language models.

The reference environment uses Python 3.14.6, NumPy 2.5.4 and certifi 2026.10.23. Run these commands from the repository root:

```sh
python3 -m venv .venv-astra
.venv-astra/bin/python -m pip install numpy==2.5.4 certifi==2026.10.23
cd docs/program/experiments/astra-family-teachers-2026-11-12
```

Activate the environment or use its absolute Python path for the following commands. NumPy is needed offline. certifi is needed only for optional API requests.

```sh
source ../../../../.venv-astra/bin/activate
python -m unittest -v test_lab.py test_runner.py test_calibration.py
python calibration.py replay --out data/calibration
```

Calibration replay uses archived artifacts and requires no API key or network access. It verifies exact recomputation of the saved result, including request and code fingerprints. To regenerate source data separately:

```sh
python calibration.py prepare --out /tmp/weft-calibration-rebuild
python run_experiment.py prepare --out /tmp/weft-family-rebuild
```

Preparation generates checkpoints and request files without contacting a teacher. Avoid replacing the registered artifacts. Family replay becomes available after all proposals are fixed and the operator records final results:

```sh
python run_experiment.py replay --out data
```

Large generated files are kept out of the tree: the phase results files, the source experiment files for phases one to three, the calibration experiment and the phase-four oracles. GENERATED-SHA256SUMS lists each one with its sha256 and size. Restore the exact bytes before any replay:

```sh
python restore_generated.py
```

The script copies each file out of commit d85940c0d078b54f40f4742b33c286c521164567, the original archive head kept on branch `record/astra-teachers-prereg-history-20261112`, fetching that branch when needed, and checks every sha256. Without it, replay stops with a missing-file error. Unit tests do not need these files. Regenerating them from seeds is not equivalent: trained source cells depend on the floating-point platform, and on Linux x86_64 with NumPy 2.5.4 the regenerated experiments differ from the archived macOS arm64 files.

After restoring, the archive includes `data/results.json` and `data/manifest.json`. Numeric family replay verifies the recorded artifact manifest and the computation modules. It does not prove original API transport identity.

For a separately authorized paid reproduction, the optional worker accepts a key at a hidden prompt and request paths on subsequent lines:

```sh
python teacher_api.py --max-calls 22 --max-output-tokens 6000
```

The 22-request total includes calibration and all family arms. Calibration consumes one request, leaving at most 21 family requests. This is a study-wide limit across workers. The worker's generic default is 18, so use the explicit amended cap and track total calls. Do not resubmit archived requests merely to replay results. See PROTOCOL.md and CALIBRATION.md for the submission and evaluation rules.

| Artifact | Content |
| --- | --- |
| PROTOCOL.md, CALIBRATION.md | Registered rules and amendment |
| SOURCES.md, LAB-DESIGN.md, independent_review.md | Evidence, design and independent review |
| lab.py, run_experiment.py | Family policy construction, selection and replay |
| calibration.py, teacher_api.py | Separate inversion calibration and optional API transport |
| test_*.py | Offline regression checks |
| data/experiments, data/config.json | Source families and sealed evaluation samples (restored, see GENERATED-SHA256SUMS) and configuration |
| data/requests | Teacher packets and observable returned responses |
| data/candidates | Parsed patches and validation decisions as rounds advance |
| data/scramble_private | Shuffle mappings hidden from teachers, retained for audit |
| data/transport_failures | Normalized transport-error records |
| data/calibration | Calibration source, request, response and result |
| data/results.json, data/manifest.json | Final family outcomes (restored) and replay record |
| GENERATED-SHA256SUMS, restore_generated.py | sha256 record of files kept out of the tree, and their exact restore |

API token usage is retained when returned by the service. Coding-agent token usage is unavailable to this harness. Credentials and internal reasoning traces are excluded. Observable answer text, usage counters and normalized errors remain in the public research record. RUN-LOG.md records checkpoints and completed checks.

## First family results

The weight-visible arm reduced active-context movement error by 19.107%, 21.860% and 20.768% across the three source seeds. Two of three met both the improvement and retention criteria on fresh IID observations. None met retention on the shifted distribution. Behavior-only met the primary criterion on zero seeds, and scrambled weights met it on one.

The weight-visible packets also supplied truthful hidden activations. This comparison cannot attribute the advantage to numerical weights alone. The completed factorial and conditional follow-ups test that distinction separately. See RESULTS.md for per-seed results, controls and family transfer.

The 22 archived API responses include calibration. Estimated API cost is $6.2913975 using the recorded token rates, not an invoice. The earlier TLS transport failure is archived separately.

## Completed archive

Read RESULTS-BRIEF.md for the four-study findings and API-USAGE.json for the per-response token ledger. Phase-specific reports are phase2_factorial/RESULTS.md, phase3_conditional/RESULTS.md and phase4_fidelity/RESULTS.md. CROSS-STUDY.md compares the peer NC1 archive with these experiments.

## Next experiment

Proposed future work should optimize the weaker conditional direction with an explicit retention margin. Compare teacher-guided hidden-feature edits against a deterministic constrained optimizer under matched validation opportunities, using new families and arena seeds. Preserve the current misses and keep these held-out sets out of further tuning.

## Review status and registration limits

Phase one was reviewed in review 5884649320 on PR #146, which recomputed its headline numbers. Phases two, three and four each need their own review of their responses and replays. Their results here have not been independently reviewed.

Phase-one round 1 prompts were committed before any family response. The phase-one round 2 and round 3 prompts, and the phase-two round 2 prompts, were committed in the same commits as their responses. They depend on earlier feedback, and each harness rebuilds them and rejects a mismatch, but they were not committed before their own calls. PROTOCOL.md records this as Deviation D2, the scramble seed correction as D1 and the phase-three packet limits as D3.

The archived phase-one, phase-two and phase-three replays matched on the reference macOS arm64 machine. On Linux x86_64 with the same NumPy version they do not reproduce: phases one and two finish with different results, and phase three stops at its request-binding check because the floating-point training diagnostics in its requests differ. Calibration replay and phase-four replay match there.
