# Preregistration: Experiment E16 — Endogenous Recurrent Markov-Blanket Cells Without External Target Supervision

Date: 2026-11-11
Status: Preregistered and committed prior to running `run_e16.py` or collecting benchmark data. The sections through "Preregistered Predictions" are the original text. Execution deviations and later runner amendments are listed under "Amendments" at the end and are not part of the preregistration.
Interfaces exercised: C1 (`weft/runtime/plasm`), C2 (`weft/runtime/invariants`), I1 (`weft/runtime/telemetry/frame64`).
Runner: `docs/program/experiments/endogenous-cells-e16-2026-11/run_e16.py`

## Motivation

Every adaptive cell experiment in the repository to date (`papers/01-models-as-cells`, `E14`, `E15`, `native-lineage-2026-11`) scores candidates against an external ground-truth matrix output `Y* = X W*`. In addition, issue #75 notes that `plasm.py:329` defines tension as `20.0 + 2.5 * ||W - W0||_F`, which is open-loop and can never enter the `< 15.0` low-tension regime in `weft/runtime/invariants` (`HOMEOSTATIC_TENSION_MIN = 15.0`).

Experiment E16 tests whether cells built strictly from single weight matrices `W_i` (`[32, 32]`, top `8` core rows frozen with the deterministic Weft watermark and gated by `C2` `verify_weight_update_safety_ex` and `verify_tension_bound`) can sustain themselves in a precarious chemical ring environment with **zero external `Y*` target supervision** and **zero harness-held symbolic belief variables**.

## Causal Architecture and Environment

- **Cell state**: Each of `n_cells = 64` cells owns one matrix `W_i` (`32 x 32`, `core_rows = 8` frozen, `r_invariant = 12.0`), one recurrent activation vector `h_i(t)` in `[-1, 1]^32` (reset to `0` at birth), scalar metabolic energy `E_i(t)` (birth `24.0`, setpoint `30.0`, basal drain `0.32`/tick, death at `E_i <= 0`), and scalar toxin load `D_i(t)` (decay `0.85`/tick).
- **Two-microstep recurrent forward pass**: At each tick `t` (`24` ticks per generation, `40` generations), sensor vector `z_i(t)` (`32` floats: static concentration, ego-corrupted spatial gradient, carrier phase `phi(t)`, probe echo `f_i(t)`, efference copy `a_move(t-1)`, neighbor signal, visceral energy/toxin channels, and recurrent slice `h_i(t-1)`) passes through `u_i = tanh(W_i^T z_i(t))` followed by `h_i(t) = tanh(W_i^T (0.5 * z_i(t) + 0.5 * u_i))`. Motor/action heads (`move`, `probe`, `ingest`, `signal_amp`, `signal_valence`) are direct nonlinear readouts of fixed indices of `h_i(t)`.
- **Ambiguous nutrient/toxin patches (requiring both active probing and recurrent memory)**:
  - Each generation places `4` nutrient (`V = +1`) and `4` toxin (`V = -1`) patches on the periodic ring `[0, 1)`. Static concentration `C(x)` and spatial gradient `dC/dx` are unsigned and identical for food and poison.
  - At tick `t - 1`, an observable global Rademacher carrier `phi(t - 1)` in `{-1, +1}` is broadcast. If a cell pays `c_probe = 0.03` ATP to emit `a_probe(t - 1)`, it receives fluorescence `f_i(t) = phi(t - 1) * V_local * a_probe(t - 1)` at tick `t`, when `phi(t - 1)` is no longer present in environmental inputs. Decoding `V_local` therefore requires both active probing at `t - 1` and retaining `phi(t - 1)` in `h_i(t - 1)`.
- **Ego-motion reafference**: Locomotion `a_move(t - 1)` adds sensory slip `2.2 * a_move(t - 1)` onto the observed chemical gradient receptor at tick `t`.
- **Endogenous visceral tension (#75 closure test)**:
  `tension_i = clamp(5.0 + 50.0 * max(0, 1 - E_i / 30.0) + 25.0 * D_i, 0.0, 100.0)`.
  Low tension (`< 15.0`) cools mutation scale (`* 0.90`); homeostatic tension (`[15.0, 35.0]`) holds scale steady; high allostatic tension (`> 35.0`) expands mutation scale (`* 1.15`); `tension > 85.0` triggers `C2` excision/apoptosis.
- **Receptor inversion shock at generation 20**: Halfway through the 40-generation run (`gen >= 20`), the sign of the spatial gradient and probe-echo channels is inverted (`* -1.0`) to compare Baldwinian germline priors (daughters inherit `W_germ` near `W0` with wiped newborn state and fresh plasticity) against Lamarckian adult soma inheritance (daughters copy adult `W` directly).
- **Telemetry**: Each generation encodes colony state into a `64-byte` IEEE-754 binary32 frame via `weft.runtime.telemetry.frame64.pack_frame64` and verifies unpacking.

## Fixed Protocol and Arms

- **Seeds**: 10 seeds, `20261131` through `20261140`.
- **8 Arms (`80` total 40-generation colony runs)**:
  1. `full_endogenous`: Intact recurrent cells, endogenous visceral tension, paid signaling (`c_sig = 0.05`), efference copy intact, Baldwinian germline inheritance.
  2. `blind_drift`: Random zero-order mutations without energy-based survivor selection (null baseline).
  3. `open_loop_tension_75`: Replaces visceral tension with `plasm.py`'s open-loop distance formula `20.0 + 2.5 * ||W - W0||_F` (#75).
  4. `memory_lesion`: Zeroes recurrent feedback `h_i(t - 1)` in `z_i(t)`.
  5. `probe_lesion`: Clamps epistemic probe `a_probe = 0.0`.
  6. `reafference_lesion`: Zeroes proprioceptive efference copy `a_move(t - 1)` in `z_i(t)`.
  7. `free_signaling`: Sets metabolic signaling cost `c_sig = 0.0` (cheap-talk control).
  8. `lamarckian_soma`: Daughters copy adult parent `W` directly with low mutation scale instead of resetting soma around evolving germline priors `W_germ`.

## Preregistered Predictions

1. **P1 (Endogenous survival without external `Y*` and reachable `< 15` tension band)**:
   - `P1a`: `full_endogenous` achieves strictly higher mean colony net energy in the second half pre-shock window (`generations 10..19`) and across all `40` generations than `blind_drift`.
   - `P1b`: `open_loop_tension_75` records `0` cell-generations in the `< 15.0` tension band, whereas `full_endogenous` visits all three `I3` tension regimes (`< 15.0`, `[15.0, 35.0]`, and `> 35.0`) and achieves higher mean colony energy than `open_loop_tension_75`.
2. **P2 (Necessity of recurrent memory and active epistemic probing for food/toxin discrimination)**:
   - `full_endogenous` achieves a strictly higher nutrient-to-toxin ingestion selectivity `(nutrient_ingested - toxin_ingested) / (nutrient_ingested + toxin_ingested + 1e-6)` and higher mean colony energy than both `memory_lesion` (`P2a`) and `probe_lesion` (`P2b`).
3. **P3 (Corollary discharge under ego-motion sensory slip)**:
   - `full_endogenous` achieves strictly higher mean colony energy and higher patch-residence accuracy than `reafference_lesion`.
4. **P4 (Metabolically paid signaling suppresses cheap-talk saturation)**:
   - Mean emitted signal amplitude `mean(a_sig)` is strictly lower (more metabolically sparse) in `full_endogenous` (`c_sig = 0.05`) than in `free_signaling` (`c_sig = 0.0`), while signal-to-valence correlation `|corr(emitted_valence, local_patch_valence)|` on active emissions is higher in `full_endogenous` than in `free_signaling`.
5. **P5 (Post-shock adaptation and strict C1/C2/I1 conformance)**:
   - `P5a`: Following the generation-20 receptor inversion shock (`generations 20..39`), `full_endogenous` (Baldwinian germline) achieves higher post-shock recovery energy (`gen 30..39` minus `gen 20..22`) than `lamarckian_soma`.
   - `P5b`: Across all `80` colony runs, `max_core_drift == 0.0`, `min_watermark_cosine >= 0.999999`, `max_committed_distance <= 12.0` (`C2` gate enforced on every weight commit), and `100%` of emitted `I1` `frame64` telemetry packets pass byte-level `unpack_frame64` validation.

## Amendments (made after data collection, not preregistered)

Dated 2026-11-12, after reviews of head `048db94d`. The original preregistration text above is unchanged.

### Execution deviations in the 2026-11-11 M1 record

These are the protocol differences that generated `results.json`. They were present in `run_e16.py` at `048db94d`.

1. Low-tension cooling is `* 0.88` with clamps `[0.015, 0.30]`. This document says `* 0.90` and does not mention the clamps.
2. The M1 P5b check was `max_committed_distance <= R_BALL + 1e-5`. This document says `<= 12.0`. The observed maximum was `12.00000286`, on `blind_drift`. `torch.linalg.matrix_norm` in the audit and `torch.linalg.norm` in the gate (`invariants.py:86`) disagree at that ulp, so a literal `<= 12.0` check on the audit would fail.
3. Commit `864e7fd` (2026-11-11 09:38:19 -0600) holds only this file. `run_e16.py` arrived in `048db94d` four minutes later, so the executable thresholds were not frozen in the preregistration commit.
4. This document names `pack_frame64` and `unpack_frame64`, which are not in the module. The runner uses `encode_frame_64b_bytes` and `decode_frame_64b_bytes`.
5. The tension cite `plasm.py:329` is stale. The open-loop assignment is `plasm.py:433`, `tension = 20.0 + drift * 2.5`.
6. The same motivation paragraph lists E15 and `native-lineage-2026-11` as repository experiments. Both remain open pull requests (`#134`, `#131`).
7. The second microstep is defined here as `h_i(t) = tanh(W_i^T (0.5 * z_i(t) + 0.5 * u_i))`. The runner keeps `z` and overwrites only slots `17:32` with `u_hid[:, 2:17]` (`run_e16.py` at the two-microstep block; originally lines 211-214 in `048db94d`).
8. The probe echo is defined here with the valence probed at `t-1`. The runner rebuilds `signed_field` at the current patch positions and multiplies that field into the echo.
9. The M1 runner projected each somatic bout onto the `R = 12` ball and assigned `W` directly. `verify_weight_update_safety_ex` ran at reproduction only. This document says the gate is enforced on every weight commit.

### Runner amendments on 2026-11-12

These changes are in the current `run_e16.py`. They do not rewrite the M1 file.

1. The runner pins one CPU thread (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `torch.set_num_threads(1)`) and calls `torch.use_deterministic_algorithms(True)`.
2. Every somatic candidate is projected with the same flattened Frobenius norm the gate uses, then passed through `verify_weight_update_safety_ex`. A rejecting gate leaves `W` and the unused budget unchanged. A unit test covers a far-out candidate and a zero-budget candidate. The P5b distance check is now `<= 12.0`.
3. Each generation packs an I1 frame through `pack_uniform_frame_64b` and counts a packet only when the decoded floats equal the packed float32 values. Energy CV, mean energy, toxin, sigma, and polarity stay beside the frame.
4. Signal amplitude is averaged over live cells. The half-colony comment was corrected: every cell proposes a somatic candidate each bout.
5. `WEFT_E16_RESULTS` may point the output path away from the committed M1 `results.json`.
