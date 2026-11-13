# E10 results: task-horizon commit evaluation

- Date: 2026-11-12. Follow-on experiment, preregistered in `PREREG-E10.md` before this run.
- Single change vs E09: the mitosis probe evaluates candidates on the actual 80-step task episode (t=0), not the 24-step window at t=1000 used before.
- Seeds: 20261112, 20261113, 20261114. Same init, same architecture, same invariants, same 1.01 commit margin.
- Instrument note (2026-11-12, review of PR #143): these logs come from the same pre-fix instrument as E09. Each cell's previous action `_u` was not reset between the task episode and the probes, and the watermark check compared `wc` with itself. The corrected `microcell.py` has not been rerun for this record. Reproduce the logs with `python3 microcell.py e10-20261112 --seed 20261112 --protocol e10 --legacy-u-leak` (`--protocol e10` sets PROBE_LEN=80, PROBE_T=0).
- Naming: E10 is a run label inside this record, not card E10 in `docs/program/experiment-cards.md`.

## Results

| Seed | commits | A gen 1 | A gen 10 | A gen 40 | B gen 40 |
|---|---|---|---|---|---|
| 20261112 | 18 | 26.69 | 36.21 | 37.38 | 34.40 |
| 20261113 | 9 | 34.57 | 36.83 | 37.21 | 34.09 |
| 20261114 | 17 | 30.85 | 37.17 | 36.80 | 35.07 |

Collisions zero everywhere in all runs. Watermark cosine 1.0 everywhere. The code never writes the core, so core drift is 0 by construction; the logged check compared `wc` with itself and is not an independent measurement.

## Read-out vs `PREREG-E10.md`

- H-E10-A HELD. Generation-40 return minus the same seed's E09 generation-40 return: A +9.40, +9.38, +10.26 and B +3.34, +3.42, +4.34 on seeds 20261112, 20261113, 20261114 (A about +9.4 to +10.3, B about +3.3 to +4.3). Both agents exceed on all three seeds.
- H-E10-B NOT SCORED. A frozen control exists only for seed 20261112 (`logs/frozen-12.jsonl`); seeds 20261113 and 20261114 were not run frozen, so they are untested. On seed 20261112 the final 5-generation means (A 37.25, B 34.19) exceed the frozen means (A 26.73, B 26.83). One tested seed cannot satisfy or falsify the registered 2-of-3 clause.
- H-E10-C HELD on the logged quantities. 16 rejections, all on seed 20261114 (agent B rejects 8 of 8 candidates at generations 39 and 40, 16 of 640 = 2.5% of that seed), none on the other seeds, below the 20% bar. Watermark cosine 1.0 everywhere. Core drift is 0 by construction and was not independently measured (see the instrument note).
- H-E10-D NOT MEASURED. The logs store the winning probe score as a float, with no candidate id and no paired score from the T=1000/24-step probe, so preference flips cannot be reconstructed. The earlier flip claim is withdrawn. The corrected script logs `best_id`; a paired run that scores each candidate under both probes would be needed to test this clause.

## Honest conclusion

- Changing the probe to the task horizon raised generation-40 returns over E09 on all three seeds. These logs do not establish that the horizon mismatch was the entire drag in E08/E09, because the `_u` leak was present in both E09 and E10 and is not separated from the horizon change.
- A reaches 36.2 to 37.2 by generation 10, and the final 5-generation means are A 37.22 to 37.28 and B 34.11 to 34.80 across seeds, with dips in between on seeds 20261112 and 20261114. Whether that is a ceiling of the task or of this instrument is not tested here, and no claim about capacity is made.
- The probe-horizon setting was an instrument choice that E09 documented and E10 changed. The `_u` leak and the self-comparing watermark check are separate instrument bugs, fixed in `microcell.py` after these runs.

## Files

`microcell.py` (`--protocol e10` gives PROBE_LEN=80, PROBE_T=0; `--protocol e09`, the default, keeps the E08/E09 24-step probe at t=1000; `NOLEX_PROBE_LEN`/`NOLEX_PROBE_T` still override, and the values used are printed in the run header), the `e10-*.jsonl` logs with their `e10-*.out` stdout, and this file. The final `wrote /Users/...` line was removed from each stdout log. E09 remains part of the same PR as the cautionary arm.
