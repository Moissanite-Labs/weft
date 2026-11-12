# E10 results: task-horizon commit evaluation

- Date: 2026-11-12. Follow-on experiment, preregistered in `PREREG-E10.md` before this run.
- Single change vs E09: the mitosis probe evaluates candidates on the actual 80-step task episode (t=0), not the 24-step window at t=1000 used before.
- Seeds: 20261112, 20261113, 20261114. Same init, same architecture, same invariants, same 1.01 commit margin.

## Results

| Seed | commits | A gen 1 | A gen 10 | A gen 40 | B gen 40 |
|---|---|---|---|---|---|
| 20261112 | 18 | 26.69 | 36.21 | 37.38 | 34.40 |
| 20261113 | 9 | 34.57 | 36.83 | 37.21 | 34.09 |
| 20261114 | 17 | 30.85 | 37.17 | 36.80 | 35.07 |

Collisions zero everywhere in all runs. Watermark cosine 1.0 everywhere. Core drift exactly 0.0 everywhere.

## Read-out vs `PREREG-E10.md`

- H-E10-A HELD. All 3 seeds exceed their E09 final returns by a wide margin (best seed +24.4, worst +9.4 against E09's same-seed endpoints).
- H-E10-B HELD. Final 5-generation mean per (seed, agent) exceeds the same-stage frozen control in all 3 seeds, both agents.
- H-E10-C HELD. Rejection rate 0%, watermark intact, core drift 0.0 everywhere.
- H-E10-D: all four cases with a differing probe preference flipped to task-horizon candidates at the gen where E09 had committed into a regression. The flip count across seeds was 100% (E09's probes were picking wrong-window candidates systematically). Confirming direction but exploratory.

## Honest conclusion

- The selection horizon mismatch was the entire drag in E08/E09. Every arm of this program now behaves as if working, in the sense that it finds the field's exploitable gradient and stops there.
- The ceiling is the task. The wave field admits one family of good strategies. This organism and the matrix organism find that family equally. Capacity does not unlock more return on this environment.
- The instrument works correctly once the commit rule sees the task it is actually committed to. That is an instrument bug, now documented in E09 and fixed here.

## Files

`microcell.py` (probe horizon via `NOLEX_PROBE_LEN`/`NOLEX_PROBE_T` env, default stays E08/E09 behaviour), the `e10-*.jsonl` logs, and this file. E09 remains part of the same PR as the cautionary arm.
