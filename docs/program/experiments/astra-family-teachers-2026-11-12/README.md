# Astra family teacher experiment

This experiment tests persistent numerical edits to small policy cells and transfer to related siblings. The first family experiment is complete. Follow-up experiments are in progress. The completed inversion calibration passed its registered gate. It does not establish family-policy improvement or editing of pretrained language models.

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

Until `data/results.json` and `data/manifest.json` exist, that command must fail. Numeric family replay verifies the recorded artifact manifest and the computation modules. It does not prove original API transport identity.

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
| data/experiments, data/config.json | Source families, sealed evaluation samples and configuration |
| data/requests | Teacher packets and observable returned responses |
| data/candidates | Parsed patches and validation decisions as rounds advance |
| data/scramble_private | Shuffle mappings hidden from teachers, retained for audit |
| data/transport_failures | Normalized transport-error records |
| data/calibration | Calibration source, request, response and result |
| data/results.json, data/manifest.json | Final family outcomes and replay record, when complete |

API token usage is retained when returned by the service. Coding-agent token usage is unavailable to this harness. Credentials and internal reasoning traces are excluded. Observable answer text, usage counters and normalized errors remain in the public research record. RUN-LOG.md records checkpoints and completed checks.

## First family results

The weight-visible arm reduced active-context movement error by 19.107%, 21.860% and 20.768% across the three source seeds. Two of three met both the improvement and retention criteria on fresh IID observations. None met retention on the shifted distribution. Behavior-only met the primary criterion on zero seeds, and scrambled weights met it on one.

The weight-visible packets also supplied truthful hidden activations. This comparison cannot attribute the advantage to numerical weights alone. Follow-up factorial and conditional experiments are testing that distinction separately. See RESULTS.md for per-seed results, controls and family transfer.

The 22 archived API responses include calibration. Estimated API cost is $6.2913975 using the recorded token rates, not an invoice. The earlier TLS transport failure is archived separately.
