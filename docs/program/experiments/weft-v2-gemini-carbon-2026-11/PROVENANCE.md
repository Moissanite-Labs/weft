# Provenance: Weft v2 reference suite (external, unreviewed)

Received 2026-11-11 from a Gemini carbon export at
`/Users/kethuda/Documents/exo/weft/work/carb0n/` (`weft_v2_whitepaper.pdf` and
`weft_v2_reference_suite/`). The model had no GitHub access, so the files come
in here by hand. Nothing in this directory has been reviewed or accepted as
project evidence yet. Commit `dcc1fa4` is that export, plus this note.

## What was re-run on 2026-11-11 (Apple M-series, Apple clang 21, Python 3.13, numpy 2.5.4)

- `sha256sum -c SHA256SUMS`: the nine entries then in the file were OK. The PDF was not in the list.
- `python3 weft_v2_engine.py`: completes in about 20 s, exit 0, regenerates
  the conformance report and certificates.
- `lean WeftInvariants.lean`: no errors. The Lean development is four small
  theorems over `Int`/`Nat` models with `omega`/`decide` proofs. It checks, but
  it formalizes paper arithmetic, not the C code or the Python engine.
- `gcc -O3 -std=c11 -Wall -Wextra -Werror test_weft_v2_c11.c`: compiles clean,
  and the engine's C11-vs-Python differential audit passes.

## What did not reproduce

On the export at `dcc1fa4`:

- The export called `max_distance_abs_error_c11_vs_py = 0.0` bit-exact parity.
  This machine reports `7.105e-15`. That is one binary64 unit in the last place
  for values between 64 and 128, so the claim is wrong as stated, not just different.
- Throughput figures (arenas/s) are machine-dependent and do reproduce in
  shape but not in size.
- E5's raw-dense cosine fidelity differs in the fourth decimal
  (`0.6245` committed vs. `0.626` here). The run is seeded, so this drift
  suggests a library-version difference, not pure hardware noise.

## Revision after that re-run

The nine hashed sources were rewritten from the local carbone review bundle.
They no longer say this suite closes
[issue #111](https://github.com/Moissanite-Labs/weft/issues/111).
`certificates.json` records the Linux container that produced the numbers, and
it says it is not a project ruling. The C11 report states a `1e-9` tolerance
instead of bit-exact parity.

`plot_figures.py` used to read a container path that is not in this repo. It
now reads `certificates.json` beside the script. The four `fig*.pdf` files are
that script's output from the committed certificates, drawn on this machine
(Apple M1 Max, Python 3.14, matplotlib 3.11.2, NumPy 2.5.4). The committed
`weft_v2_whitepaper.pdf` was built from the revised `.tex` and those figures
with tectonic. The received PDF, which said the findings were proven, remains
in `dcc1fa4`.

`SHA256SUMS` matches this revision, including the PDF and the four figures.
`PROVENANCE.md` is not in that list. The engine was not re-run for this
revision, so the certificate numbers are still the Linux container's numbers.

## What this work is not

- It does not close, verify, or answer anything in issue #111. The experiments
  are toy-scale NumPy simulations. R1 and R5 still need a held-out audit of the
  archived runs by someone other than the agent that built the cells.
- The Lean file checks integer arithmetic. It does not check the C header or
  IEEE-754 hardware.
- The PDF and `.tex` are an unreviewed design draft, not a publication.

## How to treat it

Read it as a design proposal. The conformance harness is the piece worth
comparing with `weft/runtime/invariants/`. Do not cite any number in this
directory as a project result. The C gate repair that came out of this review
is a separate change against `weft/runtime/invariants/`. Do not grow this
directory into the runtime tree.
