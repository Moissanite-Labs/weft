# Experiment run log

The study is in progress. This checkpoint reports the completed calibration only. Family held-out outcomes have not been inspected for this note.

| Checkpoint | Record |
| --- | --- |
| 1fa0cfa | Initial protocol and source evidence committed before teacher calls |
| ab90c53 | Amendment A, harness, calibration registration, source data and prepared requests pushed before successful teacher responses |
| Transport failure | An initial HTTPS request failed TLS certificate verification before any successful model response. The normalized failure is archived under data/transport_failures. The client then used certifi's certificate bundle. |
| Calibration | One completed Astra response, followed by local evaluation against registered held-out observations |

Calibration results from `data/calibration/result.json`:

| Measure | IID, 2,048 observations | Shifted, 2,048 observations |
| --- | --- | --- |
| Inverse-ground-truth accuracy | 100% | 99.853515625% |
| Inversion of source predictions | 100% | 100% |
| Agreement with row-swap oracle classes | 100% | 100% |
| Frozen first layer unchanged | true | true |

The response negated both output logits. It did not duplicate the analytic row-swap oracle's numerical logits, and exact logit equality was not required. This is a successful simple inversion edit under the registered limits. Family transfer and broader weight understanding remain separate questions.

The reference environment is Python 3.14.6, NumPy 2.5.4 and certifi 2026.10.23. The registration checkpoint passed 19 offline unit tests. Calibration replay recomputes the archived result without a key. See README.md for portable commands.

API response token accounting is captured in response artifacts. Coding-agent tokens are unavailable. The captured response contains observable message text and accounting, excluding internal reasoning items. Credentials are not recorded.

## First family proposals

All nine first-round responses and candidate evaluations are archived. Every proposal was valid. The saved validation decisions are:

| Arm | Valid proposals | Accepted by validation gates |
| --- | --- | --- |
| weights_behavior | 3/3 | 3/3 |
| behavior_only | 3/3 | 2/3 |
| scrambled_weights | 3/3 | 2/3 |

These are validation decisions, with family held-out outcomes still sealed. Later weight-visible and behavior-only rounds remain in progress. A preliminary statement that the first two scrambled proposals were rejected was corrected after the second was scored. The archived second scrambled proposal was accepted.
