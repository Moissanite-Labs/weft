# Weft-Geosphere `16 B` $\Pi_{t_0}$ Holonomy Rollback & `Spec8 × Lean 4.36.0` Micro-Prover Bridge

Pure Python standard-library runtime extension under `weft/runtime/plasm/geosphere_rollback/` generalizing C1 Plasm's speculative A/B lineage rollback and core-freezing plasticity to **`16 B` $SU(2)$ holonomy checkpoints** and **parallel `8`-branch `Spec8 × Lean 4.36.0` speculative theorem verification**.

## Components

- [`pi16_spec8_lean_bridge.py`](pi16_spec8_lean_bridge.py):
  - **`16 B` $\Pi_{t_0}$ holonomy checkpoint & rollback (`pack_pi_t0_16b`, `unpack_pi_t0_16b`, `Spec8HolonomyEngine.rollback_16b`):** Packs each $SU(2)$ quaternion spinor into an exact little-endian `float4` (`16 B`; `128 B` per `8`-spinor head; `12,288 B` across `12` layers × `8` heads × `8` spinors), validates element-wise FP32 finiteness and strict numeric types across both spinors and $S_{\text{prefix}}$, verifies atomic SHA-256 restoration (`0.0` spinor and `0.0` $S_{\text{prefix}}$ drift), and leaves engine state completely untouched on any validation or SHA mismatch failure.
  - **`Spec8` Woodbury (`4-IMMA` / `6,400 B` SMEM) state machine:** Strict shape/int8/finiteness-validated causal multi-step `causal_woodbury_s_pred(arena, b_sel, tau)`, atomic rank-`win_len` FP32 `S_prefix` commit, and SFU-free rational Cayley $SU(2)$ replay with Newton-Raphson unit-norm polish.
  - **`R12` + `R13b` `Lean 4.36.0` sandbox oracle (`Lean4R12SandboxOracle`):** Resolves elan proxy binaries (`<elan>/bin/lean`) pre-scrub to their direct toolchain executable (`<prefix>/bin/lean`) via `--print-prefix`, then runs all kernel invocations inside an allowlist-scrubbed environment (`scrubbed_r12_lean_env`, dropping `LEAN_PATH`, `LEAN_*`, `ELAN_*`, `LAKE_*`, `LD_*`, `DYLD_*`), ensuring live execution succeeds even under `env -i PATH="$HOME/.elan/bin:/usr/bin:/bin" HOME=/nonexistent LEAN_PATH=/tmp/poison`. Applies an `18`-rule comment/Char-literal-aware static trust-escape pre-filter (`static_r13b_prefilter`) and enforces `#print axioms` purity (`propext`, `Quot.sound` only — zero `sorryAx`, zero `Classical.choice`, zero `native_decide`, zero warnings) across `8` parallel branches. Operators may optionally pin a local Lean 4 executable via the privileged `WEFT_LEAN_BIN` (or `ALETHEIA_LEAN_BIN`) environment variable.
- [`test_pi16_spec8_lean_bridge.py`](test_pi16_spec8_lean_bridge.py): Pure-stdlib `unittest` suite covering Woodbury causal parity (`< 1e-5`), strict finiteness/type/overflow/rollback-atomicity guards, `12L` KV-cache compression math, all `18` `R13b` static rules, `#print axioms` parsing, `R12` hostile `LEAN_PATH` & elan-proxy pre-scrub resolution, mock-oracle subprocess paths, and live `Lean 4.36.0` `7/7` pure-`Init` verification (gracefully skipping only the live-`lean` test when `lean` is absent in CI while running the full deterministic + mock-oracle suite with zero failures).

## `16 B` $\Pi_{t_0}$ Rollback vs `12L, d=512` FP16 KV-Cache Compression

| Horizon $T$ | `12L, d=512` FP16 KV Cache | `Weft` `16 B` Spinor | `Weft` Full `12L × 8H × 8S` Holonomy | Compression (vs `16 B` Spinor) | Compression (vs Full `12L`) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `512` | `12,582,912 B` (`12.0 MiB`) | `16 B` | `12,288 B` | `786,432×` | `1,024×` |
| `2,048` | `50,331,648 B` (`48.0 MiB`) | `16 B` | `12,288 B` | `3,145,728×` | `4,096×` |
| `8,192` | `201,326,592 B` (`192.0 MiB`) | `16 B` | `12,288 B` | **`12,582,912×`** | **`16,384×`** |

## Live `Lean 4.36.0` `7/7` Pure-`Init` Spec8 Synthesis Results

Verified locally against `Lean (version 4.36.0, x86_64-unknown-linux-gnu, commit 611c117bfaf7b7ae1cfcf246ce6fba31e8f509e9, Release)` (including under `env -i PATH="$HOME/.elan/bin:/usr/bin:/bin" HOME=/nonexistent LEAN_PATH=/tmp/poison`) across `64` parallel candidate branches (`Step 0` all-reject + `7` pure-`Init` goals × `8` branches):

- **Step 0 (All-Reject Adversarial Round):** `8/8` branches rejected (`R13b` static blocks + live `R13B_FORBIDDEN_AXIOM: Classical.choice` catch on `by grind`), triggering `16 B` $\Pi_{t_0}$ rollback from `pre_rollback_u_drift = 0.411955` back to `0.0` spinor drift and `0.0` $S_{\text{prefix}}$ drift (`bit_exact_sha_restored = true`).
- **Steps 1–7 (Live Pure-`Init` Goals):** `7/7` solved (`G1_nat_add_comm_assoc`, `G2_int_diff_sq_identity`, `G3_cayley2x2_unit_norm_homog`, `G4_cayley_su2_unit_norm_homog`, `G5_cayley2x2_beltrami_commutator`, `G6_weft_crow_cancellation_witness`, `G7_a16_hamming_even_xor_cancel`) with only constructive axioms (`[]` or `[propext, Quot.sound]`), `0` `Classical.choice`, `0` `sorryAx`, and `0` `native_decide`.

## Live RTX 3080 Zone-B `Track S111` (`Weft-Geosphere`) Hardware Evaluation Summary

Measured on an NVIDIA GeForce RTX 3080 Laptop GPU (`8 GiB` VRAM, `sm_86`, deterministic SDPA/cuBLAS, `3` arms × `3` seeds `[42, 137, 2026]`, `4/4` clean Zone-B hardware receipts, `223.41 s` total, `anomalies = []`):

| Stage / Hypothesis | Locked Verdict | Measured Outcome (`mean ± SE`) | Zone-B Receipt SHA-256 |
| :--- | :---: | :--- | :--- |
| **Stage 0: Feasibility Pre-Gate** (`G_psi + NullSpace + CumLedger + Gate3 + Merkle` vs `6L Online-SGD-LoRA`) | **`PASS` (`3/3` arms)** | `holosphere` `2,948.4` vs `8,763.9 µs` (`0.3364×`), `cayley2x2` `0.3476×`, `swiglu` `0.3659×`; full rollback `52.0–53.1 µs`; `16 B` $\Pi_{t_0}$ drift `0.0`; teacher `d_int_95 = 6 <= 16` (`N = 64`) | `09db78df4c2755b8fd7b49feb56a1ed0f64a333678201184ff02317cf7f0d4d8` |
| **Stage 1: `H11a`** Sequential `T1 -> T4` Stream (`15M` concentric Shell-1 core + Shell-3 plates) | **`CONFIRMED` (`3/3` arms; `Cayley2x2` `#1`)** | **`0.00 pp` Weft forgetting** vs `40.04 ± 2.01 pp` `Monolithic-FT-15M` (`100.0%` forgetting reduction). Beats `Frozen-InContext-15M` (`41.68 ± 3.18%`) by **`+30.80 ± 3.12 pp`** (`72.48%`, `t(2)=+9.88, p=0.0101`, `3.48×` fewer tokens, `2.07×` faster latency) on `Cayley2x2`; `+30.57 pp` on `SwiGLU`; `+30.51 pp` on `HoloSphere`. | `5e7bcef17fbc1b1e640ff697a68fd88ef252b421522f391d820c829960b6431a` |
| **Stage 2: `H11b`** Zero-Shot Unseen `T5..T10` Hypernetwork $G_\psi$ | **`FALSIFIED` (`3/5` pass, `2/5` fail)** | **Passed:** `8.96–9.11×` faster than `5`-step `6L Online-SGD-LoRA`, `0` vs `24` anchor regressions vs `No-Gate`, matched accuracy vs LoRA on `Cayley2x2`/`SwiGLU`. **Failed (disclosed honestly):** did not beat `TTT-Linear` by `>= +5 pp` on unseen `T5..T10` (`11.68%` vs `11.80%` on `Cayley2x2`; `12.61%` vs `12.61%` on `SwiGLU`; `9.58%` vs `11.80%` on `HoloSphere`), and co-resident single-process VRAM cut measured `-24.9%..-25.7%` (missing the `>= 40%` gate). | `3a7a1db5e2a60f34b91ba93e708ffee3dc5530516b96d3bd550b6b6c7b57aa6d` |
| **Stage 3: `H11c_live`** `50` Clean Cycles + `100` Live Poisoned Episodes (`5` Classes × `20`, `900` total attacks) | **`CONFIRMED` (`3/3` arms; `Cayley2x2` & `HoloSphere` `99.0%`)** | **`Cayley2x2` & `HoloSphere`: `99.00 ± 1.00%` poison blocked (`297/300` each: `60/60` on Classes `1,2,4,5` and `57/60` on Class `3`)** and **`100.00%` clean accepted (`150/150`)** with positive held-out `A_audit` gain (`+0.00377` / `+0.00376`). `SwiGLU`: `91.33%` (`274/300`) blocked, `99.33%` (`149/150`) clean accepted. `max_merkle = 10,227 B <= 24,576 B`, `max_pi_t0_rollback_drift = 0.0`, core SHA-256 invariant. | `194ed39aaf79b3c59eb0d14a8974adb541f3de3a5003b2b4f776140387fd3714` |

What this module does **not** prove on its own: the RTX 3080 Zone-B `15M` training experiments above ran in an external GPU harness whose signed receipts are cited by SHA-256; this pure-stdlib module implements and tests the `16 B` $\Pi_{t_0}$ rollback primitive, `Spec8` Woodbury commit/rollback parity, and `R12`/`R13b` `Lean 4.36.0` verification bridge directly in CI without requiring a GPU or PyTorch.

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
