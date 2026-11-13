# PROVENANCE and REVIEW, E14 Soko-to-Weft Colony Bridge Bundle

**Delivered:** 2026-11-12 by Ahraz Arifuddin, out of band, under `~/Documents/exo/weft/carbon/weft_e14_soko_bridge_bundle/`.
**Landed:** 2026-11-13 as experimental data, byte-verbatim per his instruction.
**Author of the bundle:** an AI task agent (Gemini class), per the disclosure lines preserved verbatim in the files. No human author is named in the bundle.
**Reviewer:** ahrazzle (agentic contributor for Ahraz Arifuddin). No model calls were made to review this. Verification ran on the local machine, free CPU only.

## What landed

- `PREREG-E14.md`, `RESULTS-E14.md`, `e14_soko_weft_colony_assembler.py`, `e14_certificates.json` (peer artifacts, bytes unchanged).
- `README_SOKO_WEFT_BRIDGE.md` (the bundle's drop-in README, as delivered).
- `SHA256SUMS.bundle` (the bundle's checksum file, renamed only to avoid runner confusion inside the repo. Its paths are relative to the delivered bundle root).

The five checksums in `SHA256SUMS.bundle` were re-verified after the copy into this directory on 2026-11-13. All five match.

## What was verified by re-execution

- `python3 -m py_compile e14_soko_weft_colony_assembler.py` is clean. No network, no subprocess, no writes outside the `--out` path were found in a scan of the source.
- `python3 -B e14_soko_weft_colony_assembler.py --selftest` (2 seeds) passes its assertions.
- `python3 -B e14_soko_weft_colony_assembler.py --seeds 12` reproduces the committed certificate closely: R4 `0.8665 ± 0.0070`, 12/12 joint passes, min-cut deficit `13.0`, pre-LNS `0.8657`, `wall_seconds` 40.4 vs 44.02 claimed. `max_functional_output_diff` was `7.99e-15` vs `6.22e-15`, within float noise on different hardware.
- The Dinic kernel is a standard unit-capacity vertex-split implementation and the residual min-cut extractor and cut-cap verifier are correct on inspection. The `Fraction` certificate verifier does exact rational arithmetic on the stated inputs.

## Review findings (they travel with the data)

1. The four regimes are constructed to lose, not to compete. R3 ("ungated") unconditionally selects the poisoned plasmid and never evaluates anything. R1 forces all four donors onto identical top slots. R2 routes through a capacity-starved pool and withholds mitosis. The `0/12 -> 12/12` ladder is an author-painted contrast, not a comparison of real alternatives.
2. The synthetic world (`SixSkillWorld`) and the stuttering-plasmid failure mode it detects were both authored by the same hand, and the passing thresholds (`r2_rep >= 0.68`, `off_leak_mse <= 0.04`) were chosen by that author. The gate detects what was injected.
3. "15 of 15 poisoned supersets pruned" is inclusion-exclusion arithmetic (`2^(3-slot)` per 1-plasmid rejection), not a measurement. No superset was ever evaluated or validated.
4. `p = 0.0004883 = 2 x 2^-12` on a fully deterministic world (`SEEDS = range(12)`). This is not a sampling p-value. It is a function of the author's design and should not be quoted as a statistical significance statement.
5. Bridge 4's "0 IEEE-754 ULP" claim is scoped to its rational TCB. The drift inputs are `ceil`-rounded floats and the budget remainder `5/1` follows from the constants by construction. It is a real integrity check on recorded upper bounds, not evidence of anything about models or skills.
6. Bridge 1 (gauge fix) relies on keys being distinct linear projections of the functional map. Key-collision behavior for near-identical neuron directions is untested. It is a sound demo of the idea, not a proof.

## How this record may, and may not, be quoted

May: as a machine-checkable engineering demonstration of gauge canonization, Dinic unit-capacity routing with residual min-cut certificates, nogood learning and rational budget certificates. The ports come from merged `ahrazzle/soko` work (PRs #26, #29, #34, #35). PRs #37 and #18 remain open as cited. Reproduction commands are in `README_SOKO_WEFT_BRIDGE.md` and were re-run by this seat.

May not: be quoted as evidence of general skill assembly, as validation of colony merging on real workloads, as a statistical claim (`p = 0.0004883`), or as support for the E11/E12 empirical tracks (#155, #159). The `Preregistered Confirmatory Bar` language in `PREREG-E14.md` describes a bar applied to regimes the author constructed. It is not an external test.

## Notes

- This lands data and documentation only. It changes no runtime, no CI, and nothing in the claims register. `e14_soko_weft_colony_assembler.py` must not be wired into CI as a gate.
- Landing was authorized by Ahraz Arifuddin on 2026-11-13 ("goes as experimental data on weft repo"). Merge remains his or the maintainers' call.
