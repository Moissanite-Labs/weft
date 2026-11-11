# Weft v2 Reference Suite (`WEFT-INVARIANTS/2.0` + `ContinuumPlasm` + `SYM-2P/Latent`)

Drop-in reference architecture, C11/Python/Lean 4 formal verification suite, and reproducible 10-seed experimental harness for [`Moissanite-Labs/weft`](https://github.com/Moissanite-Labs/weft) (`w3ft.org`), resolving all findings (`F1–F9`) and recommendations (`R1–R6`) in [`Moissanite-Labs/weft#111`](https://github.com/Moissanite-Labs/weft/issues/111).

**Mandate:** *No token. No sale. Nothing on-chain.* All claims carry explicit verification tiers (`PROVEN`, `VERIFIED`, `KNOWN`) aligned with [`Foundation-0/incentre-lattices`](https://github.com/Foundation-0/incentre-lattices) and [`Proven-Commons/mission`](https://github.com/Proven-Commons/mission).

## Contents

| File | Subsystem | Description |
| :--- | :--- | :--- |
| `weft_v2_invariants.h` | `C2 Invariants` (`WEFT-INVARIANTS/2.0`) | Zero-dependency ISO C11 header eliminating the IEEE-754 Zeno sub-ULP free-step bypass (`nextafterf` monotone deduction), `N=65,536` `float32` accumulation drift (Laplace-scaled Neumaier `binary64`), NaN/Inf bypasses, and locked-bitmask tampering, plus Pythagorean orthogonal child radius helper. |
| `test_weft_v2_c11.c` | `C2 Invariants` Conformance | C11 differential conformance binary (`gcc -O3 -std=c11 -Wall -Wextra -Werror`) verifying 2,048 deterministic & adversarial vectors, 100,000-step Zeno stress, and full 65,536-float `StratifiedMemoryArena` throughput (`5,572.4` arenas/s). |
| `WeftInvariants.lean` | Formal Verification (Lean 4) | Mechanized Lean 4 specification & proofs for Pythagorean trust-ball conservation, anti-Zeno ordinal termination, exact `540,688B` `StratifiedMemoryArena` layout, and Lafont IC step positivity. |
| `weft_v2_engine.py` | `C1 Plasm`, `C2`, `C3 IC`, `C6 SY2L` | Complete reproducible Python engine executing the 2,048-vector C11-to-Python differential audit and all five 10-seed confirmatory experiments (`E1–E5`), emitting `certificates.json` and `c11_conformance_report.json`. |
| `plot_figures.py` | Publication Figures | Deterministic vector PDF figure generator (`fig1`–`fig4`) directly from `certificates.json`. |
| `certificates.json` | Cryptographic Audit Ledger | Raw 10-seed confirmatory benchmark metrics, SHA-256 normal-form hashes, and per-arm distributions (`Issue #111` R2/R5). |
| `c11_conformance_report.json` | C11 Parity Certificate | Exact C11-to-Python differential verification certificate (`2,048 / 2,048` bit-exact parity, `max_distance_abs_error = 0.0`). |
| `weft_v2_whitepaper.tex` | Technical Monograph | LaTeX source for *Weft v2: Bounded Continual Self-Modification via Causal Orthogonal Mitosis, Stratified Continuum Arenas, and Formally Verified Metabolic Combinators*. |
| `SHA256SUMS` | Integrity Manifest | SHA-256 digests of every source and certificate artifact in this bundle. |

## Quickstart Verification

```bash
# 1. Compile C11 WEFT-INVARIANTS/2.0 verifier with zero warnings
gcc -O3 -std=c11 -Wall -Wextra -Werror test_weft_v2_c11.c -lm -o test_weft_v2_c11

# 2. Run full 2,048-vector C11↔Python differential audit + N=10 confirmatory experiments (E1–E5)
python3 weft_v2_engine.py

# 3. Verify SHA-256 manifest
sha256sum -c SHA256SUMS
```
