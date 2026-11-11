# Provenance: Weft v2 reference suite (external, unreviewed)

Received 2026-11-11 from a Gemini carbon export at
`/Users/kethuda/Documents/exo/weft/work/carb0n/` (`weft_v2_whitepaper.pdf` and
`weft_v2_reference_suite/`). The model had no GitHub access, so the files come
in here by hand. Nothing in this directory has been reviewed or accepted as
project evidence yet. The source files are byte-identical to the export (see
`SHA256SUMS`); this file and the PR that carried them here are the only
additions.

## What was re-run on 2026-11-11 (Apple M-series, Apple clang 21, Python 3.13, numpy 2.5.4)

- `sha256sum -c SHA256SUMS`: all ten files OK.
- `python3 weft_v2_engine.py`: completes in about 20 s, exit 0, regenerates
  the conformance report and certificates.
- `lean WeftInvariants.lean`: no errors. The Lean development is four small
  theorems over `Int`/`Nat` models with `omega`/`decide` proofs. It checks, but
  it formalizes paper arithmetic, not the C code or the Python engine.
- `gcc -O3 -std=c11 -Wall -Wextra -Werror test_weft_v2_c11.c`: compiles clean,
  and the engine's C11-vs-Python differential audit passes.

## What did not reproduce

- The bundle claims `max_distance_abs_error_c11_vs_py = 0.0` (bit-exact
  parity). This machine reports `7.105e-15`. That is about one float32 ULP at
  magnitude 1, so the claim is wrong as stated, not just different.
- Throughput figures (arenas/s) are machine-dependent and do reproduce in
  shape but not in size.
- E5's raw-dense cosine fidelity differs in the fourth decimal
  (`0.6245` committed vs. `0.626` here). The run is seeded, so this drift
  suggests a library-version difference, not pure hardware noise.

## What this work is not

- It does not close, verify, or answer anything in
  [issue #111](https://github.com/Moissanite-Labs/weft/issues/111). The
  whitepaper's "Complete Resolution Ledger" maps F1–F9 and R1–R6 onto a
  self-run synthetic 10-seed suite. R1 and R5 require held-out audits over the
  existing run archives and re-derivation by someone other than the agent that
  built the system; this suite does neither. F5's "resolved" claim rests on a
  simulated equal-compute experiment, not on the program's registered test.
- The experiments are toy-scale numpy simulations. Treat `E1`–`E5` outputs as
  illustrative, not as measurements of the colony program.
- "PROVEN", "VERIFIED" and the phrase "cryptographic audit ledger" in
  `certificates.json` are the exporter's labels, not rulings by this project.
- The PDF and `.tex` are an unreviewed draft monograph, not a publication.

## How to treat it

Read it as a design proposal. The conformance harness (C11 + Python differential
test) is the most reusable piece; the engineering ideas (Zeno-safe monotone
deduction via `nextafterf`, Neumaier-compensated float64 accumulation) deserve
a real review against `weft/runtime/invariants/`. Do not cite any number in
this directory as a project result until a review says so. Open follow-ups as
separate PRs; do not let this directory grow into the runtime tree by default.
