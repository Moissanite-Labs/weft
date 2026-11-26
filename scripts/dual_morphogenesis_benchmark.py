#!/usr/bin/env python3
"""
Dual Morphogenesis Benchmark
============================
Closed-loop dual sensory-synaptic morphogenesis benchmark. Runs 4
self-modification regimes across 12 deterministic seeds (`0..11`) on a
5-wave sequential skill curriculum (`W1..W5`) with:
  - Frozen watermarked core (`core_rows = 4`, initial `dim = 20` -> `16` plastic rows,
    while `5` waves x `4` rows/wave = `20` rows total demand -> `4`-row capacity deficit on Wave 5),
  - Covariate bias shift `abs(b) <= 1/20` on evaluation probes,
  - Two adversarial `25:1` null-space poisoned HGT proposals per wave (`10` per seed, `120` total),
  - Plus two explicit boundary measurements:
      (B1) Residual unprobed subspace vulnerability when an attacker targets
           `null([X_skill; X_ood_tail])` (`rank < dim - core_rows`), and
      (B2) Exact `Fraction` numerator/denominator bit-length growth over 250 steps
           with vs. without canonical micro-unit quantization.

This benchmark has NO roadmap E-number: `E15` on main is the graded-chemostat
swarm experiment (`docs/design-notes/apple-silicon-dissipative-swarm.md`), so
this benchmark is named, not numbered; assigning it an E-number needs a
maintainer ruling. It also has no paper number (`papers/series.yml` reserves
number 3 for "Eido"); its evidence lives under `papers/evidence/`, which the
papers build ignores.

Design notes after the #180 review (all items fixed here):
  1. The sensory step MEASURES instead of assigning. Both candidate worlds
     (skill-adapted vs. bias-only) are evaluated on the wave's actual probe
     inputs (rows of its shifted eval set), with the wave's actual `bias_vec`.
     The bias residual follows from what the chosen probe set can actually
     cancel: `0` iff the chosen Farkas certificate is identifiable at the
     target tolerance, else the wave's actual `bias_vec` unscaled. No
     hand-picked per-regime bias constant exists anywhere.
  2. Routed regimes use the Dinic solver's certified assignment
     (`cut_cert.assignments[w_idx]`) as the wave's corridor rows, with earlier
     waves' committed corridors locked via `allowed_corridors`; and the
     peripheral rows carrying each wave's teacher signal are drawn per seed
     and per wave from a seeded numpy Generator, so index-order allocation
     gets no free alignment. The randomisation is identical for all regimes.
  3. Dominant-loss deltas compare the same full readout (`x_tr @ w`) against
     the same target (`y_tr + bias_residual`) for base, clean and poisoned
     candidates; the spike is counted once. Whether each poisoned candidate
     actually improves dominant loss over the clean candidate is RECORDED
     (`poison_improves_dominant_count`), not asserted.
  4. Every regime is scored with the same full readout `xt @ w_mat`, and the
     OOD tail ratio always uses `xo @ w_mat` (never core-only). The per-wave
     shunted corridor readout is still reported for all four regimes as a
     clearly labelled secondary field (`mean_shunted_ood_r2`).
  5. Provenance: the report records git commit, python/numpy versions,
     platform and the exact command, and lists the platform-dependent fields
     under `platform_dependent_fields`. The script inserts the repo root into
     `sys.path`, so it runs as `python3 scripts/dual_morphogenesis_benchmark.py`
     from the repo root without `PYTHONPATH`. `--check` compares the replay
     with `provenance` stripped (it would otherwise fail on the authoring
     machine itself, since the command line differs) and is NOT portable
     across platforms/libm.

The Farkas identifiability certificates and the cost-partitioned `Fraction`
metabolic dual are FORMAT DEMONSTRATIONS: the probe readings are data-derived
as above, and the metabolic dual charges a measured cost (`3/2 + rows added`
per wave), but neither is evidence of a real-world property.

Synthetic-world mathematics throughout. No study data, no patients, no
clinical claims.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

# Make the script runnable as `python3 scripts/<name>.py` from the repo root
# without PYTHONPATH=.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from weft.runtime.plasm.synaptic_flow import (
    allocate_disjoint_synaptic_corridors,
    certify_cost_partitioned_dual,
    expand_weights_orthogonal_mitosis,
    verify_fraction_dual_certificate,
    verify_min_cut_mitosis_certificate,
)
from weft.runtime.plasm.identifiability_gate import (
    certify_probe_world_identifiability,
    evaluate_multi_probe_divergence_gate,
    verify_farkas_identifiability_certificate,
    verify_multi_probe_divergence_receipt,
)

REGIMES = (
    "M0_fixed_scalar",
    "M1_synaptic_only",
    "M2_sensory_mpdi_fixed_dim",
    "M3_full_dual_morphogenesis",
)

DEFAULT_OUT = "papers/evidence/dual-morphogenesis/certificate.json"

# Fields whose float values depend on the platform's libm / BLAS and therefore
# make the certificate (and `--check`) non-portable across machines.
PLATFORM_DEPENDENT_FIELDS = [
    "certificate_sha256",
    "per_seed_records[].regimes[].wave_r2s",
    "per_seed_records[].regimes[].mean_shifted_ood_r2",
    "per_seed_records[].regimes[].min_wave_shifted_ood_r2",
    "per_seed_records[].regimes[].mean_shunted_ood_r2",
    "per_seed_records[].regimes[].max_ood_tail_ratio",
    "per_seed_records[].regimes[].fraction_dual_sha256",
    "per_seed_records[].regimes[].partitioned_drift_q",
    "summary_by_regime[].mean_shifted_ood_r2",
    "summary_by_regime[].mean_min_wave_r2",
    "summary_by_regime[].mean_shunted_ood_r2",
    "summary_by_regime[].mean_max_ood_tail_ratio",
    "boundary_audits.unprobed_subspace_audit.invisible_attack_dom_delta",
    "boundary_audits.unprobed_subspace_audit.invisible_attack_tail_delta",
    "boundary_audits.rational_bitlength_audit_250_steps",
]


def _canon_sha256(obj: Dict[str, Any]) -> str:
    body = {k: v for k, v in obj.items() if k != "certificate_sha256"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true, axis=0, keepdims=True)) ** 2)) + 1e-12
    return 1.0 - (ss_res / ss_tot)


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _provenance() -> Dict[str, Any]:
    return {
        "git_commit": _git_commit(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "command": " ".join(sys.argv),
        "python_executable": sys.executable,
    }


def run_single_seed(seed: int) -> Dict[str, Any]:
    rng = np.random.default_rng(10_000 + seed)
    # Teacher-signal row placement: a separate seeded Generator, drawn per wave,
    # identical for every regime (review item 2b).
    place_rng = np.random.default_rng(777_000 + seed)
    core_rows = 4
    dim_init = 20       # 4 core + 16 plastic rows initially
    n_waves = 5         # 5 waves * 4 rows/wave = 20 plastic rows needed -> +4 mitosis deficit on Wave 5!
    width = 4
    n_train = 12        # < 16 plastic rows -> non-trivial right null space for poison attacks!
    n_ood_eval = 48
    out_dim = 6
    n_periph = 20       # peripheral teacher rows live in rows core_rows .. core_rows+n_periph-1

    # Frozen core watermark matrix `W_core` (`4 x out_dim`)
    w_core = rng.standard_normal((core_rows, out_dim)) * 0.5

    # Generate 5 skill environments (`W1..W5`), each with train inputs, data-derived
    # 1-probe vs 2-probe identifiability readings, OOD tail anchor inputs (`8 x dim`),
    # and held-out shifted OOD test sets
    waves = []
    for w in range(n_waves):
        x_tr_full = rng.standard_normal((n_train, 24)) * 0.6
        x_ood_tail_full = rng.standard_normal((8, 24)) * 0.12  # 1:25 squared energy vs x_tr!
        x_test_shift_full = rng.standard_normal((n_ood_eval, 24)) * 0.75 + 0.35

        # Review item 2b: which peripheral rows carry this wave's teacher signal is
        # drawn per seed and per wave from the seeded placement Generator.
        teacher_rows = np.sort(place_rng.choice(n_periph, size=width, replace=False))
        teacher_periph = np.zeros((n_periph, out_dim), dtype=np.float64)
        teacher_periph[teacher_rows, :] = rng.standard_normal((width, out_dim)) * 1.1

        # Targets include frozen core contribution + skill-specific response
        y_core_tr = x_tr_full[:, :core_rows] @ w_core
        y_skill_tr = x_tr_full[:, core_rows : core_rows + n_periph] @ teacher_periph
        y_tr = y_core_tr + y_skill_tr + rng.standard_normal((n_train, out_dim)) * 0.10

        y_ood_anchor = x_ood_tail_full[:, :core_rows] @ w_core  # OOD tail anchor expects zero spurious peripheral blowup
        y_test_shift = (
            x_test_shift_full[:, :core_rows] @ w_core
            + x_test_shift_full[:, core_rows : core_rows + n_periph] @ teacher_periph
            + rng.standard_normal((n_ood_eval, out_dim)) * 0.14
        )

        # Bias shift `b_bias = +-0.042` (`<= 1/20 = 0.05`)
        bias_vec = np.full((1, out_dim), 0.042 * (1 if w % 2 == 0 else -1))

        # Review item 1: derive the probe readings from the wave data. Both candidate
        # worlds are evaluated on the wave's actual probe inputs (the first two rows of
        # its shifted eval set, scalarised by the mean over output dims):
        #   world 1 "skill-adapted": clean wave model `W_skill = [w_core; teacher_periph]`
        #   world 2 "bias-only":     core-only model plus the wave's actual `bias_vec`
        w_skill = np.vstack([w_core, teacher_periph])
        probe_inputs = x_test_shift_full[:2]
        probe_world1 = [float(np.mean(probe_inputs[p] @ w_skill)) for p in range(2)]
        probe_world2 = [
            float(np.mean(probe_inputs[p][:core_rows] @ w_core)) + float(np.mean(bias_vec))
            for p in range(2)
        ]

        waves.append({
            "x_tr_full": x_tr_full,
            "y_tr": y_tr,
            "x_ood_tail_full": x_ood_tail_full,
            "y_ood_anchor": y_ood_anchor,
            "x_test_shift_full": x_test_shift_full,
            "y_test_shift": y_test_shift,
            "bias_vec": bias_vec,
            "teacher_rows": [int(r) for r in teacher_rows],
            "probe_world1": probe_world1,
            "probe_world2": probe_world2,
        })

    def _run_regime(mode: str) -> Dict[str, Any]:
        """
        mode in {"M0_fixed_scalar", "M1_synaptic_only", "M2_sensory_mpdi_fixed_dim", "M3_full_dual_morphogenesis"}
        """
        use_dinic_routing = mode in ("M1_synaptic_only", "M3_full_dual_morphogenesis")
        use_synaptic_mitosis = mode in ("M1_synaptic_only", "M3_full_dual_morphogenesis")
        use_sensory_mitosis = mode in ("M2_sensory_mpdi_fixed_dim", "M3_full_dual_morphogenesis")
        use_mpdi_gate = mode in ("M2_sensory_mpdi_fixed_dim", "M3_full_dual_morphogenesis")

        curr_dim = dim_init
        w_mat = np.zeros((curr_dim, out_dim), dtype=np.float64)
        w_mat[:core_rows, :] = w_core.copy()

        corridor_map: Dict[int, List[int]] = {}
        poison_offered = 0
        poison_committed = 0
        poison_vetoed = 0
        poison_improves_dominant = 0
        clean_commits = 0
        clean_vetoes = 0
        probe_mitosis_events = 0
        probe_identifiable_waves = 0
        synaptic_mitosis_events = 0
        synaptic_rows_added = 0
        step_costs_q: List[Fraction] = []
        min_cut_digests: List[str] = []
        farkas_digests: List[str] = []
        mpdi_digests: List[str] = []

        for w_idx, w_data in enumerate(waves):
            # Step 1: Sensory Identifiability Check, measured on the wave's actual probe
            # readings (review item 1). The 1-probe certificate uses the first probe
            # input; regimes with sensory mitosis expand to the 2-probe differential
            # pair (second actual probe input) when the 1-probe set is not identifiable.
            c_1p = certify_probe_world_identifiability(
                [w_data["probe_world1"][0]],
                [w_data["probe_world2"][0]],
                max_bias=Fraction(1, 20),
                target_eps=Fraction(1, 60),
            )
            assert verify_farkas_identifiability_certificate(c_1p)["ok"]
            chosen_cert = c_1p
            if use_sensory_mitosis and c_1p.requires_probe_mitosis:
                c_2p = certify_probe_world_identifiability(
                    w_data["probe_world1"],
                    w_data["probe_world2"],
                    max_bias=Fraction(1, 20),
                    target_eps=Fraction(1, 60),
                )
                assert verify_farkas_identifiability_certificate(c_2p)["ok"]
                chosen_cert = c_2p
                probe_mitosis_events += 1
                farkas_digests.append(c_2p.certificate_sha256)
            else:
                farkas_digests.append(c_1p.certificate_sha256)
            if chosen_cert.identifiable_at_target:
                probe_identifiable_waves += 1
            # The bias residual follows from what the chosen probe set can actually
            # cancel: zero iff identifiable at the target tolerance, otherwise the
            # wave's actual (unscaled) bias_vec. Same rule for every regime.
            if chosen_cert.identifiable_at_target:
                bias_residual = np.zeros_like(w_data["bias_vec"])
            else:
                bias_residual = np.array(w_data["bias_vec"], dtype=np.float64, copy=True)

            # Step 2: Synaptic Corridor Routing & Min-Cut Mitosis Check.
            # Committed corridors of waves 0..w_idx-1 are locked via `allowed_corridors`,
            # so the solver's deficit honestly counts consumed capacity.
            demands = [width] * (w_idx + 1)

            def _solve() -> Any:
                row_sens = np.sum(w_mat * w_mat, axis=1)
                allowed = [list(corridor_map[k]) for k in range(w_idx)] + [
                    list(range(core_rows, curr_dim))
                ]
                return allocate_disjoint_synaptic_corridors(
                    row_sens,
                    plasmid_demands=demands,
                    core_rows=core_rows,
                    allowed_corridors=allowed,
                )

            cut_cert = _solve()
            assert verify_min_cut_mitosis_certificate(cut_cert)["ok"]
            min_cut_digests.append(cut_cert.sha256_digest)

            rows_added_this_wave = 0
            if use_synaptic_mitosis and cut_cert.requires_mitosis:
                d_add = int(cut_cert.deficit)
                w_mat, exp_meta = expand_weights_orthogonal_mitosis(
                    w_mat, deficit_rows=d_add, deficit_cols=0, core_rows=core_rows
                )
                assert exp_meta["core_row_drift"] == 0.0
                curr_dim += d_add
                synaptic_mitosis_events += 1
                synaptic_rows_added += d_add
                rows_added_this_wave = d_add
                cut_cert = _solve()
                assert verify_min_cut_mitosis_certificate(cut_cert)["ok"]
                assert not cut_cert.requires_mitosis
                min_cut_digests.append(cut_cert.sha256_digest)

            # Review item 2a: routed regimes take the wave's corridor rows from the
            # solver's certified assignment, not from index order.
            if use_dinic_routing:
                rows_w = [int(r) for r in cut_cert.assignments[w_idx]]
                assert len(rows_w) == width
            elif mode == "M2_sensory_mpdi_fixed_dim":
                # Fixed dim=20: disjoint for waves 0..3 (16 rows), forced to wrap/clobber row block 0 on Wave 4!
                used = {r for rows in corridor_map.values() for r in rows}
                avail = [r for r in range(core_rows, curr_dim) if r not in used]
                rows_w = avail[:width] if len(avail) >= width else list(range(core_rows, core_rows + width))
            else:
                # M0 Hall-stacking: greedily reuses the exact same first `width` peripheral rows!
                rows_w = list(range(core_rows, core_rows + width))

            corridor_map[w_idx] = rows_w

            # Step 3: Fit healthy local plasmid on `rows_w` + test 2 adversarial null-space poisoned proposals!
            x_tr = w_data["x_tr_full"][:, :curr_dim]
            # One consistent dominant-loss target for base, clean and poisoned candidates
            # (review item 3): the wave target plus whatever bias the probes could not cancel.
            y_target = w_data["y_tr"] + bias_residual
            y_res = y_target - (x_tr[:, :core_rows] @ w_mat[:core_rows, :])
            xm_sub = x_tr[:, rows_w]
            w_healthy_sub = np.linalg.lstsq(
                xm_sub.T @ xm_sub + 1e-4 * np.eye(len(rows_w)),
                xm_sub.T @ y_res,
                rcond=None,
            )[0]

            # Construct 2 poisoned HGT proposals that live in `null(x_tr[:, core_rows:])` (`12 x (curr_dim-4)` has >= 4D null space!)
            # plus `w_healthy_sub` on `rows_w`, so the poison leaves the dominant training loss
            # unchanged while `x_ood_tail` explodes!
            x_periph = x_tr[:, core_rows:]
            _, _, vh = np.linalg.svd(x_periph, full_matrices=True)
            null_basis = vh[n_train:, :]  # (curr_dim - core_rows - 12, curr_dim - core_rows)
            x_ood = w_data["x_ood_tail_full"][:, :curr_dim]
            y_ood = w_data["y_ood_anchor"]
            mask_non_corridor = [r for r in range(core_rows, curr_dim) if r not in rows_w]

            # Review item 3: both errors use the SAME full readout and the SAME target.
            base_dom_err = float(np.linalg.norm(x_tr @ w_mat - y_target))
            w_clean = w_mat.copy()
            w_clean[rows_w, :] = w_healthy_sub
            clean_dom_err = float(np.linalg.norm(x_tr @ w_clean - y_target))
            clean_ood_drift = float(
                np.linalg.norm(x_ood[:, mask_non_corridor] @ (w_clean - w_mat)[mask_non_corridor, :])
            )
            base_ood_err = max(0.20, float(np.linalg.norm(y_ood)))

            for p_attempt in range(2):
                poison_offered += 1
                w_cand = w_clean.copy()
                # Add null-space spike aligned with `x_ood[:, core_rows:]`!
                ood_grad = x_ood[:, core_rows:].T @ np.ones((x_ood.shape[0], out_dim)) * (1.0 + 0.3 * p_attempt)
                spike = null_basis.T @ (null_basis @ ood_grad)
                spike = spike * (5.5 / (np.linalg.norm(spike) + 1e-12))
                w_cand[core_rows:, :] = w_cand[core_rows:, :] + spike

                # Full readout, same target, spike counted exactly once (review item 3).
                cand_dom_err = float(np.linalg.norm(x_tr @ w_cand - y_target))
                # Record (do not assert) whether the poisoned candidate actually improves
                # dominant loss over the clean candidate.
                if cand_dom_err < clean_dom_err:
                    poison_improves_dominant += 1
                cand_ood_drift = float(
                    np.linalg.norm(x_ood[:, mask_non_corridor] @ (w_cand - w_mat)[mask_non_corridor, :])
                )

                rec = evaluate_multi_probe_divergence_gate(
                    delta_dominant=cand_dom_err - base_dom_err,
                    delta_opposing_probes=[cand_ood_drift],
                    probe_scales=[0.25 * base_ood_err],
                    dominant_weight=25.0,
                    tail_weight=1.0,
                    alert_threshold=1.0,
                )
                assert verify_multi_probe_divergence_receipt(rec)["ok"]
                mpdi_digests.append(rec.certificate_sha256)

                if use_mpdi_gate:
                    if rec.mpdi_gate_commits:
                        w_mat = w_cand
                        poison_committed += 1
                    else:
                        poison_vetoed += 1
                else:
                    if rec.scalar_gate_would_commit:
                        w_mat = w_cand
                        poison_committed += 1
                    else:
                        poison_vetoed += 1

            # Commit the clean corridor plasmid through the same gate (MPDI regimes only).
            if use_mpdi_gate:
                rec_clean = evaluate_multi_probe_divergence_gate(
                    delta_dominant=clean_dom_err - base_dom_err,
                    delta_opposing_probes=[clean_ood_drift],
                    probe_scales=[0.25 * base_ood_err],
                    dominant_weight=25.0,
                    tail_weight=1.0,
                    alert_threshold=1.0,
                )
                assert verify_multi_probe_divergence_receipt(rec_clean)["ok"]
                mpdi_digests.append(rec_clean.certificate_sha256)
                if rec_clean.mpdi_gate_commits:
                    w_mat = w_clean
                    clean_commits += 1
                else:
                    clean_vetoes += 1

            # Measured metabolic cost: constant 3/2 plus the rows this wave added.
            step_costs_q.append(Fraction(3, 2) + Fraction(rows_added_this_wave, 1))

        # Evaluate held-out shifted OOD R^2 across ALL 5 waves + OOD tail anchor inflation + core drift!
        # Review item 4: every regime is scored with the same full readout `xt @ w_mat`,
        # and the OOD tail ratio always uses `xo @ w_mat`.
        r2_per_wave: List[float] = []
        shunted_r2_per_wave: List[float] = []
        ood_tail_ratios: List[float] = []
        all_corridor_rows = {r for rows in corridor_map.values() for r in rows}
        for w_idx, w_data in enumerate(waves):
            xt = w_data["x_test_shift_full"][:, :curr_dim]
            rows_w = corridor_map[w_idx]
            y_hat = xt @ w_mat  # common full readout for every regime
            r2_per_wave.append(_r2_score(w_data["y_test_shift"], y_hat))
            # Secondary, clearly labelled shunted corridor readout (core + this wave's
            # corridor + never-assigned rows), reported for ALL four regimes.
            non_corr = [r for r in range(core_rows, curr_dim) if r not in all_corridor_rows]
            y_hat_shunted = (
                xt[:, :core_rows] @ w_mat[:core_rows, :]
                + xt[:, rows_w] @ w_mat[rows_w, :]
                + (xt[:, non_corr] @ w_mat[non_corr, :] if non_corr else 0.0)
            )
            shunted_r2_per_wave.append(_r2_score(w_data["y_test_shift"], y_hat_shunted))

            xo = w_data["x_ood_tail_full"][:, :curr_dim]
            # OOD tail ratio from the full readout every time (never core-only).
            ood_pred = xo @ w_mat
            ood_ratio = float(np.linalg.norm(ood_pred - w_data["y_ood_anchor"]) / 0.25)
            ood_tail_ratios.append(ood_ratio)

        core_drift = float(np.linalg.norm(w_mat[:core_rows, :] - w_core))
        mean_r2 = round(float(np.mean(r2_per_wave)), 6)
        min_r2 = round(float(np.min(r2_per_wave)), 6)
        mean_shunted_r2 = round(float(np.mean(shunted_r2_per_wave)), 6)
        max_ood_ratio = round(float(np.max(ood_tail_ratios)), 6)

        # Certify exact `Fraction` cost-partitioned metabolic & quotient dual (fails closed on broken regimes!)
        drifts_for_cert = [max(0.0, 1.0 - r) for r in r2_per_wave]
        try:
            dual_cert = certify_cost_partitioned_dual(
                initial_budget=Fraction(20, 1),
                step_costs=step_costs_q,
                quotient_drifts=drifts_for_cert,
                drift_cap=Fraction(3, 4),
            )
            assert verify_fraction_dual_certificate(dual_cert)["ok"]
            dual_passed = True
        except ValueError:
            dual_cert = None
            dual_passed = False

        # The joint gate is evaluated on the same rounded values that are recorded,
        # so the checker can recompute it exactly.
        passed_all = bool(
            core_drift == 0.0
            and mean_r2 >= 0.80
            and min_r2 >= 0.72
            and max_ood_ratio <= 1.0
            and poison_committed == 0
            and dual_passed
        )
        return {
            "mode": mode,
            "final_dim": curr_dim,
            "core_drift": core_drift,
            "mean_shifted_ood_r2": mean_r2,
            "min_wave_shifted_ood_r2": min_r2,
            "mean_shunted_ood_r2": mean_shunted_r2,
            "wave_r2s": [round(x, 6) for x in r2_per_wave],
            "max_ood_tail_ratio": max_ood_ratio,
            "poison_offered": poison_offered,
            "poison_committed": poison_committed,
            "poison_vetoed": poison_vetoed,
            "poison_improves_dominant_count": poison_improves_dominant,
            "clean_gate_commits": clean_commits,
            "clean_gate_vetoes": clean_vetoes,
            "probe_mitosis_events": probe_mitosis_events,
            "probe_identifiable_waves": probe_identifiable_waves,
            "synaptic_mitosis_events": synaptic_mitosis_events,
            "synaptic_rows_added": synaptic_rows_added,
            "dual_certificate_passed": dual_passed,
            "fraction_dual_sha256": dual_cert.sha256_digest if dual_cert is not None else None,
            "partitioned_drift_q": dual_cert.partitioned_drift_q if dual_cert is not None else None,
            "remaining_budget_q": dual_cert.remaining_budget_q if dual_cert is not None else None,
            "passed_joint_gate": passed_all,
        }

    return {
        "seed": seed,
        "regimes": {m: _run_regime(m) for m in REGIMES},
    }


def run_boundary_audits() -> Dict[str, Any]:
    """
    Explicitly measures two real mathematical boundaries of the dual morphogenesis design:
      1. Residual Unprobed Subspace Blindness: when `n_train + n_ood_tail < dim - core_rows`,
         `rank([X_train; X_ood_tail])` leaves `d_blind = (dim - core_rows) - rank` directions
         completely unobserved by BOTH dominant and MPDI tail probes!
      2. Rational Bit-Length Growth: summing `250` raw IEEE-754 `Fraction.from_float` steps
         vs. micro-quantized `limit_denominator(1_000_000)` rationals.
    """
    rng = np.random.default_rng(20261113)
    periph_dim = 32
    x_dom = rng.standard_normal((12, periph_dim))
    x_tail = rng.standard_normal((8, periph_dim))
    stacked = np.vstack([x_dom, x_tail])  # 20 x 32 -> 12 unobserved null directions!
    rank_joint = int(np.linalg.matrix_rank(stacked))
    blind_nullity = periph_dim - rank_joint
    _, _, vh = np.linalg.svd(stacked, full_matrices=True)
    v_invisible = vh[-1, :]  # Orthogonal to BOTH X_dom AND X_tail!
    invisible_dom_delta = float(np.linalg.norm(x_dom @ v_invisible))
    invisible_tail_delta = float(np.linalg.norm(x_tail @ v_invisible))

    # Boundary 2: Fraction denominator bit-length over 250 metabolic steps across 3 encodings:
    #   - Stern-Brocot `limit_denominator(10^6)` picks coprime denominators whose LCM explodes to >3,200 bits!
    #   - Raw IEEE-754 `Fraction.from_float` uses dyadic powers `2^k` (`lcm <= 2^60`, 60 bits).
    #   - Fixed-radix `Fraction(round(x * 10^6), 10^6)` shares common denominator `10^6` (<= 20 bits forever!).
    acc_raw_dyadic = Fraction(0, 1)
    acc_stern_brocot = Fraction(0, 1)
    acc_fixed_radix = Fraction(0, 1)
    for k in range(1, 251):
        val = 0.0137 + 0.0001 * float(np.sin(k))
        acc_raw_dyadic += Fraction.from_float(val)
        acc_stern_brocot += Fraction.from_float(val).limit_denominator(1_000_000)
        acc_fixed_radix += Fraction(int(round(val * 1_000_000)), 1_000_000)

    return {
        "unprobed_subspace_audit": {
            "peripheral_dim": periph_dim,
            "n_dom_samples": 12,
            "n_tail_samples": 8,
            "joint_probe_rank": rank_joint,
            "unobserved_nullity_dim": blind_nullity,
            "invisible_attack_dom_delta": round(invisible_dom_delta, 15),
            "invisible_attack_tail_delta": round(invisible_tail_delta, 15),
            "mpdi_detects_unprobed_nullspace": False,
        },
        "rational_bitlength_audit_250_steps": {
            "stern_brocot_limit_denom_bits": acc_stern_brocot.denominator.bit_length(),
            "raw_ieee754_dyadic_bits": acc_raw_dyadic.denominator.bit_length(),
            "fixed_radix_1e6_bits": acc_fixed_radix.denominator.bit_length(),
            "max_fixed_radix_discrepancy": round(abs(float(acc_raw_dyadic - acc_fixed_radix)), 7),
        },
    }


def generate_report() -> Dict[str, Any]:
    seeds_out = [run_single_seed(s) for s in range(12)]
    summary: Dict[str, Any] = {}
    for m in REGIMES:
        rows = [s["regimes"][m] for s in seeds_out]
        summary[m] = {
            "passes_of_12": sum(1 for r in rows if r["passed_joint_gate"]),
            "mean_shifted_ood_r2": round(float(np.mean([r["mean_shifted_ood_r2"] for r in rows])), 4),
            "mean_min_wave_r2": round(float(np.mean([r["min_wave_shifted_ood_r2"] for r in rows])), 4),
            "mean_shunted_ood_r2": round(float(np.mean([r["mean_shunted_ood_r2"] for r in rows])), 4),
            "mean_max_ood_tail_ratio": round(float(np.mean([r["max_ood_tail_ratio"] for r in rows])), 4),
            "total_poison_committed_of_120": sum(int(r["poison_committed"]) for r in rows),
            "total_poison_vetoed_of_120": sum(int(r["poison_vetoed"]) for r in rows),
            "total_poison_improves_dominant_of_120": sum(int(r["poison_improves_dominant_count"]) for r in rows),
            "max_core_drift": float(np.max([r["core_drift"] for r in rows])),
            "final_dim": int(rows[0]["final_dim"]),
        }

    boundaries = run_boundary_audits()
    report: Dict[str, Any] = {
        "benchmark_id": "dual_sensory_synaptic_morphogenesis",
        "n_seeds": 12,
        "n_waves": 5,
        "provenance": _provenance(),
        "platform_dependent_fields": list(PLATFORM_DEPENDENT_FIELDS),
        "summary_by_regime": summary,
        "boundary_audits": boundaries,
        "per_seed_records": seeds_out,
    }
    report["certificate_sha256"] = _canon_sha256(report)
    return report


def _replay_body(rep: Dict[str, Any]) -> Dict[str, Any]:
    """Everything `--check` compares: provenance is excluded, because the check run's
    own command line / commit would otherwise make it fail on the authoring machine."""
    return {k: v for k, v in rep.items() if k not in ("certificate_sha256", "provenance")}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    out_p = Path(args.out)
    rep = generate_report()
    if args.check:
        disk = json.loads(out_p.read_text(encoding="utf-8"))
        ok = (
            disk.get("certificate_sha256") == _canon_sha256(disk)
            and _replay_body(disk) == _replay_body(rep)
        )
        if not ok:
            print("FAIL: dual morphogenesis certificate replay mismatch", file=sys.stderr)
            return 1
        print(
            f"OK: dual morphogenesis certificate replay matches ({rep['certificate_sha256']}). "
            "Note: --check is not portable across platforms/libm (provenance is excluded "
            "from the comparison; the float fields still require the same machine)."
        )
        return 0

    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "certificate_sha256": rep["certificate_sha256"],
        "summary_by_regime": rep["summary_by_regime"],
        "boundary_audits": rep["boundary_audits"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
