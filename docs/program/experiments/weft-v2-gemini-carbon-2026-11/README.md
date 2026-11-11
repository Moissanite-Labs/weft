# External Design Proposal & C11/Python Conformance Suite (`weft-v2-gemini-carbon-2026-11`)

**AI-Assistance Disclosure (`CONTRIBUTING.md`):** This directory was substantially written and executed by an AI tool (Gemini task-mode agent) in an isolated Linux x86_64 container without GitHub or live model-API access. Every claim below separates what was executed in that container from what remains unexecuted or open in [`Moissanite-Labs/weft`](https://github.com/Moissanite-Labs/weft).

**Mandate:** *No token. No sale. Nothing on-chain.*

## Scope & What This Bundle Is (and Is Not)

- **Reusable runtime contribution:** `weft_v2_invariants.h` and `test_weft_v2_c11.c` implement a C11-vs-Python differential conformance harness testing three specific numerical repairs for `weft/runtime/invariants/`: (1) Zeno-safe monotone budget deduction via `nextafterf`, (2) Laplace-scaled Neumaier `binary64` Frobenius accumulation with pre-cast `double` radius comparison, and (3) frozen-bitmask (`locked_mask`) tamper rejection.
- **Synthetic design simulations (`E1`–`E5`):** `weft_v2_engine.py` runs five toy-scale 10-seed NumPy simulations motivating experiments for [`Moissanite-Labs/weft#111`](https://github.com/Moissanite-Labs/weft/issues/111). **They do not close, settle, or substitute for `F1`–`F9` or `R1`–`R5` on the real colony archives or `Tinker` harness.**
- **JSON output with hashes (`certificates.json`):** Plain JSON recording seeded synthetic simulation summaries, SHA-256 normal-form hashes (`E4`), and pinned host toolchain metadata. It is **not** a cryptographic audit ledger and carries no project ruling status.
- **Toy formalization (`WeftInvariants.lean`):** Four small lemmas over `Int` and `Nat` (`omega` / `decide`). It models paper integer inequalities only. It says nothing about IEEE-754 floating-point hardware, `weft_v2_invariants.h`, or `weft_v2_engine.py`. `lean` was not installed on the Linux generation host. Type-checking was run externally on Apple M-series during PR #128 triage.

## Pinned Execution Environment & Cross-Platform Tolerance

`c11_conformance_report.json` and `certificates.json` were generated on:

- **CPU / Arch:** `Intel(R) Xeon(R) Platinum 8481C` (`x86_64`, `2` logical cores)
- **OS:** `Linux-6.12.105+-x86_64-with-glibc2.36`
- **C Compiler & Flags:** `gcc (Debian 12.2.0-14+deb12u1) 12.2.0` with `-O3 -ffp-contract=off -std=c11 -Wall -Wextra -Werror`
- **Python / NumPy / BLAS:** Python `3.11.2`, NumPy `2.1.3` (`blas=scipy-openblas (0.3.27), lapack=scipy-openblas (0.3.27)`)

### Observed Metrics & Cross-Machine Drift Boundaries

1. **C11-vs-Python Frobenius Distance Agreement (`c11_conformance_report.json`):**
   - Enforced specification: `2,048 / 2,048` verdict, status, and `float32` budget matches, with `binary64` distance agreement within explicit tolerance `|dist_c11 - dist_py| <= 1.0e-9`.
   - Observed on the pinned Intel Xeon Linux host above: `max_distance_abs_error_c11_vs_py = 0.000e+00`, throughput `5589.87` `65,536`-float arenas/s (`0.3663` Gweights/s).
   - Observed on Apple M-series (`Apple clang 21 -O3`, Python `3.13`, NumPy `2.5.4` without `-ffp-contract=off`): `max_distance_abs_error_c11_vs_py = 7.105e-15` (`2^-47`, 1 `binary64` ULP at `[64, 128)` from ARM64 FMA contraction), well within the `1.0e-9` tolerance. Throughput is hardware-dependent.
2. **LAPACK Nullspace Sensitivity in `E5` (`certificates.json`):**
   - `E5`'s `raw_dense_nullmodem` baseline fits a `512 x 512` orthogonal Procrustes map using `N_cal = 256 < 512` calibration anchors (`256`-dimensional zero singular subspace). Because `np.linalg.svd` selects an implementation-dependent orthonormal basis on the zero-singular-value subspace, mean cosine measures `0.6245` on x86_64 `scipy-openblas 0.3.27` vs. `0.626` on Apple M-series `Accelerate`. Treat `E5` numbers to two significant digits (`~0.62`–`0.63`) across BLAS backends.

## Contents

| File | Role & Evidence Boundary |
| :--- | :--- |
| `weft_v2_invariants.h` | Zero-dependency ISO C11 header implementing `nextafterf` monotone budget deduction, Laplace-scaled Neumaier `binary64` Frobenius norm, and `locked_mask` tamper checks. |
| `test_weft_v2_c11.c` | C11 differential conformance runner (`-O3 -ffp-contract=off -std=c11 -Wall -Wextra -Werror`) testing 2,048 binary vectors within `1e-9` distance tolerance and 100,000-step sub-ULP budget stress. |
| `WeftInvariants.lean` | Toy `Int`/`Nat` formalization (`omega`/`decide`) of four paper arithmetic lemmas. It does not model IEEE-754 floats or C/Python code. |
| `weft_v2_engine.py` | Reproducible runner generating the 2,048 binary vectors for `test_weft_v2_c11.c` and running synthetic 10-seed NumPy simulations `E1`–`E5`. |
| `plot_figures.py` | Matplotlib script plotting synthetic simulation outputs from `certificates.json`. |
| `c11_conformance_report.json` | Output of `test_weft_v2_c11.c` with pinned `execution_environment` metadata and `1e-9` tolerance specification. |
| `certificates.json` | Seeded simulation and local C11 conformance JSON output (with SHA-256 hashes and pinned toolchain metadata). |
| `weft_v2_whitepaper.tex` | Draft design-proposal LaTeX source with an explicit `#111` target map (`open` / `partial` / `closed`) and evidence boundaries. |
| `fig1_mitosis_benchmarks.pdf`, `fig2_continuum_plasm.pdf`, `fig3_colony_cascade.pdf`, `fig4_invariants_latent.pdf` | Plots of `certificates.json`, written by `plot_figures.py`. |
| `weft_v2_whitepaper.pdf` | PDF built from `weft_v2_whitepaper.tex` and those four figures. The received monograph, which claimed the suite closes `#111`, remains in commit `dcc1fa4`. |
| `SHA256SUMS` | SHA-256 digests of the suite files. `PROVENANCE.md` is not in the list. |

## Reproduction Commands

```bash
# 1. Compile C11 conformance binary cleanly
gcc -O3 -ffp-contract=off -std=c11 -Wall -Wextra -Werror test_weft_v2_c11.c -lm -o /tmp/test_weft_v2_c11 && rm -f /tmp/test_weft_v2_c11

# 2. Run 2,048-vector C11-vs-Python differential check + 10-seed synthetic simulations
python3 weft_v2_engine.py

# 3. Check file digests (note: running step 2 on a different machine updates execution_environment and timings)
sha256sum -c SHA256SUMS
```
