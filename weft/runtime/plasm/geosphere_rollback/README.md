# Weft-Geosphere `16 B` $\Pi_{t_0}$ Holonomy Rollback & `Spec8 × Lean 4.36.0` Micro-Prover Bridge

Pure Python standard-library runtime extension under `weft/runtime/plasm/geosphere_rollback/` generalizing C1 Plasm's speculative A/B lineage rollback and core-freezing plasticity to **`16 B` $SU(2)$ holonomy checkpoints** and **parallel `8`-branch `Spec8 × Lean 4.36.0` speculative theorem verification**.

## Components

- [`pi16_spec8_lean_bridge.py`](pi16_spec8_lean_bridge.py):
  - **`16 B` $\Pi_{t_0}$ holonomy checkpoint & rollback (`pack_pi_t0_16b`, `unpack_pi_t0_16b`, `Spec8HolonomyEngine.rollback_16b`):** Packs each $SU(2)$ quaternion spinor into an exact little-endian `float4` (`16 B`; `128 B` per `8`-spinor head; `12,288 B` across `12` layers × `8` heads × `8` spinors), validates tight dyadic unit-norm spinor bounds (`|‖q‖² - 1| <= 1/1024`), element-wise FP32 finiteness, and strict list/tuple/int/real typing across both spinors and $S_{\text{prefix}}$, enforces atomic check-then-assign SHA-256 restoration (`0.0` drift against an independent pre-perturbation reference copy), and leaves engine state untouched on any validation or SHA mismatch failure.
  - **`Spec8` Woodbury (`4-IMMA` / `6,400 B` SMEM) state machine:** Strict shape/int8/finiteness-validated causal multi-step `causal_woodbury_s_pred(arena, b_sel, tau)`, atomic rank-`win_len` FP32 `S_prefix` commit, and SFU-free rational Cayley $SU(2)$ replay with Newton-Raphson unit-norm polish.
  - **`R12` + `R13b` `Lean 4.36.0` sandbox oracle (`Lean4R12SandboxOracle`):** Resolves elan proxy binaries (`<elan>/bin/lean`) pre-scrub to their direct toolchain executable (`<prefix>/bin/lean`) via `--print-prefix`, wraps all subprocess invocations (`--print-prefix`, `--version`, and `--stdin`) into typed `WeftHolonomyError` failures (`LEAN_VERSION_BAD` / `LEAN_EXEC_ERROR`), and runs all kernel checks inside an allowlist-scrubbed environment (`scrubbed_r12_lean_env`, dropping `LEAN_PATH`, `LEAN_*`, `ELAN_*`, `LAKE_*`, `LD_*`, `DYLD_*`), ensuring live execution succeeds even under `env -i PATH="$HOME/.elan/bin:/usr/bin:/bin" HOME=/nonexistent LEAN_PATH=/tmp/poison`. Applies an `18`-rule comment/Char-literal-aware static trust-escape pre-filter (`static_r13b_prefilter`) and enforces `#print axioms` purity (`propext`, `Quot.sound` only — zero `sorryAx`, zero `Classical.choice`, zero `native_decide`, zero warnings) across `8` parallel branches. Operators may optionally pin a local Lean 4 executable via the privileged `WEFT_LEAN_BIN` (or `ALETHEIA_LEAN_BIN`) environment variable.
- [`test_pi16_spec8_lean_bridge.py`](test_pi16_spec8_lean_bridge.py): Pure-stdlib `unittest` suite covering Woodbury causal parity (`< 1e-5`), strict unit-spinor/finiteness/type/overflow/check-then-assign rollback-atomicity guards, `12L` KV-cache compression math, all `18` `R13b` static rules, `#print axioms` parsing, `R12` hostile `LEAN_PATH` & elan-proxy pre-scrub resolution, mock-oracle subprocess & `OSError`/`TimeoutExpired` error paths, and live `Lean 4.36.0` `7/7` pure-`Init` verification (gracefully skipping only the live-`lean` test when `lean` is absent in CI while running the full deterministic + mock-oracle suite with zero failures).

## `16 B` $\Pi_{t_0}$ Rollback vs `12L, d=512` FP16 KV-Cache Compression

| Horizon $T$ | `12L, d=512` FP16 KV Cache | `Weft` `16 B` Spinor | `Weft` Full `12L × 8H × 8S` Holonomy | Compression (vs `16 B` Spinor) | Compression (vs Full `12L`) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `512` | `12,582,912 B` (`12.0 MiB`) | `16 B` | `12,288 B` | `786,432×` | `1,024×` |
| `2,048` | `50,331,648 B` (`48.0 MiB`) | `16 B` | `12,288 B` | `3,145,728×` | `4,096×` |
| `8,192` | `201,326,592 B` (`192.0 MiB`) | `16 B` | `12,288 B` | **`12,582,912×`** | **`16,384×`** |

## Live `Lean 4.36.0` `7/7` Pure-`Init` Spec8 Synthesis Results

Verified locally against `Lean (version 4.36.0, x86_64-unknown-linux-gnu, commit 611c117bfaf7b7ae1cfcf246ce6fba31e8f509e9, Release)` (including under `env -i PATH="$HOME/.elan/bin:/usr/bin:/bin" HOME=/nonexistent LEAN_PATH=/tmp/poison`) across `64` parallel candidate branches (`Step 0` all-reject + `7` pure-`Init` goals × `8` branches):

- **Step 0 (All-Reject Adversarial Round):** `8/8` branches rejected (`R13b` static blocks + live `R13B_FORBIDDEN_AXIOM: Classical.choice` catch on `by grind`), triggering `16 B` $\Pi_{t_0}$ rollback from `pre_rollback_u_drift = 0.411955` back to `0.0` spinor drift and `0.0` $S_{\text{prefix}}$ drift against the pre-perturbation state (`bit_exact_sha_restored = true`).
- **Steps 1–7 (Live Pure-`Init` Goals):** `7/7` solved (`G1_nat_add_comm_assoc`, `G2_int_diff_sq_identity`, `G3_cayley2x2_unit_norm_homog`, `G4_cayley_su2_unit_norm_homog`, `G5_cayley2x2_beltrami_commutator`, `G6_weft_crow_cancellation_witness`, `G7_a16_hamming_even_xor_cancel`) with only constructive axioms (`[]` or `[propext, Quot.sound]`), `0` `Classical.choice`, `0` `sorryAx`, and `0` `native_decide`.

## Scope and Evidence Boundary

- **Directly certified by this module and its tests:** `16 B` $\Pi_{t_0}$ holonomy serialization/deserialization and atomic check-then-assign rollback, exact `12L, d=512` FP16 KV-cache compression arithmetic, `Spec8` causal Woodbury `s_pred` and rank-`win_len` commit parity (`< 1e-5`), `R12` allowlist-scrubbed subprocess isolation, `R13b` `18`-rule static filtering and `#print axioms` verification, deterministic `3`-mode `-I` preflight replay, and local live `Lean 4.36.0` `7/7` pure-`Init` synthesis.
- **Outside the scope of this PR:** External GPU hardware training/evaluation benchmarks and GPU microbenchmark latencies are intentionally omitted here and will only be linked once self-contained, rehashable receipt artifacts ship in-tree or in `Moissanite-Labs/weft-loom`. Ubuntu CI runners do not install `lean`, so CI runs the full deterministic, `R12`/`R13b`, and mock-oracle suite while skipping only the live-`lean` test.

## Verification

```bash
# Run through the repository's C1 plasm unittest discovery (also executed in CI)
python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'

# Deterministic preflight receipt (bit-identical across -I -B, -I -O -B, -I -B -W error)
python3 -I -B weft/runtime/plasm/geosphere_rollback/pi16_spec8_lean_bridge.py --mode deterministic

# Standalone unit suite (runs live Lean 4.36.0 when installed; skips live-lean cleanly in CI)
python3 -I -B weft/runtime/plasm/geosphere_rollback/test_pi16_spec8_lean_bridge.py

# Live Lean 4.36.0 7/7 pure-Init synthesis under env -i with poisoned LEAN_PATH & HOME=/nonexistent
env -i PATH="$HOME/.elan/bin:/usr/bin:/bin" HOME=/nonexistent LEAN_PATH=/tmp/poison \
  python3 -I -B weft/runtime/plasm/geosphere_rollback/pi16_spec8_lean_bridge.py --mode live-lean --no-timings
```
