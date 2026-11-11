#!/usr/bin/env python3
"""
Experiment E16 Runner: Endogenous Recurrent Markov-Blanket Cells
================================================================
Tests ground-up sensorimotor survival, recurrent memory + active epistemic probing,
corollary-discharge reafference cancellation, metabolically paid signaling,
endogenous visceral tension (closing the #75 unreachable <15 band), and Baldwinian
germline vs. Lamarckian soma inheritance — with ZERO external Y* target oracle
and ZERO harness-held symbolic belief variables.

Writes `results.json` in this directory and exits 0 if all C1/C2/I1 invariants hold.
"""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from weft.runtime.invariants import (  # noqa: E402
    TENSION_MAX,
    verify_tension_bound,
    verify_weight_update_safety_ex,
)
from weft.runtime.plasm import DEFAULT_SEED_PHRASE, embed_weight_watermark  # noqa: E402
from weft.runtime.telemetry.frame64 import (  # noqa: E402
    compute_gini,
    decode_frame_64b_bytes,
    encode_frame_64b_bytes,
    pack_uniform_frame_64b,
)

SEEDS = list(range(20261131, 20261141))
N_CELLS = 64
DIM = 32
CORE_ROWS = 8
R_BALL = 12.0
GENERATIONS = 40
BOUTS_PER_GEN = 3
TICKS_PER_BOUT = 8  # 3 * 8 = 24 causal ticks per generation
SHOCK_GEN = 20

ARMS = [
    "full_endogenous",
    "blind_drift",
    "open_loop_tension_75",
    "memory_lesion",
    "probe_lesion",
    "reafference_lesion",
    "free_signaling",
    "lamarckian_soma",
]


def probe_host() -> Dict[str, Any]:
    chip = "unknown"
    for cmd in (["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"], ["sysctl", "-n", "machdep.cpu.brand_string"]):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            if out:
                chip = out
                break
        except Exception:
            pass
    return {
        "chip": chip,
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
    }


def ring_delta(x_cell: torch.Tensor, x_patch: torch.Tensor) -> torch.Tensor:
    """Signed shortest displacement on periodic ring [0, 1): shape (n_cells, n_patches)."""
    raw = x_patch.unsqueeze(0) - x_cell.unsqueeze(1)
    return torch.remainder(raw + 0.5, 1.0) - 0.5


def run_single_colony(seed: int, arm: str) -> Dict[str, Any]:
    g_rng = torch.Generator(device="cpu").manual_seed(seed)
    torch.manual_seed(seed)

    # 1. Embed C1 provenance watermark in frozen top CORE_ROWS of W0
    w_proto = torch.randn(DIM, DIM, generator=g_rng, dtype=torch.float32) * 0.08
    w_wm, trigger_vec, target_id, _ = embed_weight_watermark(
        w_proto, DEFAULT_SEED_PHRASE, core_rows=CORE_ROWS
    )

    W0 = torch.randn(N_CELLS, DIM, DIM, generator=g_rng, dtype=torch.float32) * 0.08
    W0[:, :CORE_ROWS, :] = w_wm[:CORE_ROWS, :].unsqueeze(0)
    W_germ = W0.clone()
    W = W0.clone()

    plasticity_mask = torch.ones(N_CELLS, DIM, DIM, dtype=torch.float32)
    plasticity_mask[:, :CORE_ROWS, :] = 0.0

    germline_budget = torch.full((N_CELLS,), 200.0, dtype=torch.float32)

    # Spatial positions on periodic ring [0, 1)
    pos = torch.linspace(0.0, 1.0 - 1.0 / N_CELLS, N_CELLS, dtype=torch.float32)

    gen_energies: List[float] = []
    tension_low_count = 0
    tension_homeo_count = 0
    tension_high_count = 0
    excisions_total = 0
    gate_commits = 0
    frame64_valid_count = 0

    total_nutrient_ingested = 0.0
    total_toxin_ingested = 0.0
    total_patch_hits = 0
    total_cell_ticks = 0
    signal_amp_accum: List[float] = []
    sig_val_samples: List[float] = []
    true_val_samples: List[float] = []

    max_core_drift = 0.0
    min_wm_cosine = 1.0
    max_committed_dist = 0.0

    t_start = time.perf_counter()

    for gen in range(GENERATIONS):
        polarity = -1.0 if gen >= SHOCK_GEN else 1.0

        # Place 4 nutrient (+1) and 4 toxin (-1) patches on the ring
        patch_pos = torch.rand(8, generator=g_rng, dtype=torch.float32)
        patch_val = torch.tensor([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0], dtype=torch.float32)
        patch_sigma = 0.045

        # Newborn visceral and recurrent state at start of generation
        energy = torch.full((N_CELLS,), 24.0, dtype=torch.float32)
        toxin = torch.zeros(N_CELLS, dtype=torch.float32)
        h_state = torch.zeros(N_CELLS, DIM, dtype=torch.float32)
        last_move = torch.zeros(N_CELLS, dtype=torch.float32)
        last_probe = torch.zeros(N_CELLS, dtype=torch.float32)
        phi_prev = 1.0

        init_sigma = 0.025 if arm == "lamarckian_soma" else 0.14
        sigma = torch.full((N_CELLS,), init_sigma, dtype=torch.float32)

        # Stigmergic signal ring (16 spatial bins around [0, 1))
        stigmergy_bins = torch.zeros(16, dtype=torch.float32)

        for bout in range(BOUTS_PER_GEN):
            # Online somatic A/B candidate generation: half colony tests candidate mutation
            # evaluated purely by visceral energy delta over this bout (zero external Y*).
            w_parent_bout = W.clone()
            e_before_bout = energy.clone()

            u_m = torch.randn(N_CELLS, DIM, 4, generator=g_rng, dtype=torch.float32)
            v_m = torch.randn(N_CELLS, 4, DIM, generator=g_rng, dtype=torch.float32)
            raw_step = torch.bmm(u_m, v_m) * (sigma.view(N_CELLS, 1, 1) * 0.25)
            w_cand = W + plasticity_mask * raw_step
            dist_cand = torch.linalg.matrix_norm(w_cand - W0, ord="fro", dim=(1, 2))
            proj = torch.clamp(R_BALL / (dist_cand + 1e-8), max=1.0).view(N_CELLS, 1, 1)
            W = W0 + (w_cand - W0) * proj
            W[:, :CORE_ROWS, :] = w_wm[:CORE_ROWS, :].unsqueeze(0)

            for _tick in range(TICKS_PER_BOUT):
                # Slowly drift patches so static memorization of coordinates fails
                patch_pos = torch.remainder(patch_pos + 0.003, 1.0)
                phi_curr = 1.0 if float(torch.rand(1, generator=g_rng).item()) > 0.5 else -1.0

                dx = ring_delta(pos, patch_pos)  # (N_CELLS, 8)
                gauss = torch.exp(-0.5 * (dx / patch_sigma) ** 2)
                # Static concentration and gradient are unsigned (identical for food & poison)
                conc = gauss.sum(dim=1)
                grad_true = (gauss * (dx / (patch_sigma ** 2))).sum(dim=1) * 0.08
                signed_field = (gauss * patch_val.unsqueeze(0)).sum(dim=1)

                # Ego-motion sensory slip corrupts observed gradient
                grad_obs = polarity * grad_true + 2.2 * last_move
                probe_echo = polarity * phi_prev * signed_field * last_probe

                bin_idx = torch.clamp((pos * 16.0).long(), 0, 15)
                neighbor_sig = stigmergy_bins[bin_idx]

                # Assemble 32-float input vector z (rows 0..7 reserved for frozen core)
                z = torch.zeros(N_CELLS, DIM, dtype=torch.float32)
                z[:, 8] = conc
                z[:, 9] = torch.clamp(grad_obs, -4.0, 4.0)
                z[:, 10] = phi_curr
                z[:, 11] = probe_echo
                z[:, 12] = 0.0 if arm == "reafference_lesion" else last_move
                z[:, 13] = neighbor_sig
                z[:, 14] = (energy - 30.0) / 30.0
                z[:, 15] = toxin
                z[:, 16] = 1.0
                if arm != "memory_lesion":
                    z[:, 17:32] = h_state[:, 17:32]

                # Two-microstep recurrent forward pass using ONLY single matrix W_i
                u_hid = torch.tanh(torch.bmm(W.transpose(1, 2), z.unsqueeze(2)).squeeze(2))
                z2 = z.clone()
                z2[:, 17:32] = u_hid[:, 2:17]
                h_next = torch.tanh(torch.bmm(W.transpose(1, 2), z2.unsqueeze(2)).squeeze(2))
                h_state = h_next

                # Action readouts from fixed channels of h_state
                a_move = h_state[:, 0] * 0.035  # step size on ring
                a_probe = torch.zeros(N_CELLS) if arm == "probe_lesion" else torch.sigmoid(2.0 * h_state[:, 1])
                a_ingest = torch.sigmoid(2.5 * h_state[:, 2] - 0.5)
                a_sig_amp = torch.sigmoid(2.0 * h_state[:, 3] - 1.0)
                a_sig_val = h_state[:, 4]

                # Metabolic costs & environmental causality
                alive = (energy > 0.0).float()
                move_norm = h_state[:, 0]  # normalized [-1, 1] motor drive
                sig_cost = 0.0 if arm == "free_signaling" else 0.05

                intake = a_ingest * signed_field * 1.9
                nutr_gain = torch.clamp(intake, min=0.0)
                tox_hit = torch.clamp(-intake, min=0.0)

                energy_delta = (
                    nutr_gain
                    - 1.35 * tox_hit
                    - 0.32
                    - 0.04 * (move_norm ** 2)
                    - 0.03 * a_probe
                    - sig_cost * a_sig_amp
                )
                energy = torch.clamp(energy + alive * energy_delta, min=0.0, max=80.0)
                toxin = 0.85 * toxin + alive * tox_hit

                # Update stigmergic bins with emitted signals
                stigmergy_bins = 0.70 * stigmergy_bins
                weighted_sig = alive * a_sig_amp * a_sig_val
                stigmergy_bins.scatter_add_(0, bin_idx, weighted_sig * 0.25)
                stigmergy_bins = torch.clamp(stigmergy_bins, -2.0, 2.0)

                # Update positions and reafference history
                pos = torch.remainder(pos + alive * a_move, 1.0)
                last_move = alive * move_norm
                last_probe = alive * a_probe
                phi_prev = phi_curr

                # Telemetry accumulation
                total_nutrient_ingested += float((alive * nutr_gain).sum().item())
                total_toxin_ingested += float((alive * tox_hit).sum().item())
                total_patch_hits += int(((alive > 0) & (signed_field > 0.35)).sum().item())
                total_cell_ticks += int(alive.sum().item())
                signal_amp_accum.append(float(a_sig_amp.mean().item()))

                active_emit = (alive > 0) & (a_sig_amp > 0.25) & (conc > 0.25)
                if bool(active_emit.any().item()):
                    sig_val_samples.extend(a_sig_val[active_emit].tolist())
                    true_val_samples.extend(torch.sign(signed_field[active_emit]).tolist())

            # End of bout: visceral retention vs reversion + tension regulation
            de_bout = energy - e_before_bout
            if arm != "blind_drift":
                revert_mask = de_bout < -2.6  # revert somatic moves that worsened visceral drain beyond basal
                W[revert_mask] = w_parent_bout[revert_mask]

            if arm == "open_loop_tension_75":
                drift_norms = torch.linalg.matrix_norm(W - W0, ord="fro", dim=(1, 2))
                tensions = 20.0 + 2.5 * drift_norms
            else:
                tensions = torch.clamp(
                    5.0 + 50.0 * torch.clamp(1.0 - energy / 30.0, min=0.0) + 25.0 * toxin,
                    min=0.0,
                    max=100.0,
                )

            low_m = tensions < 15.0
            homeo_m = (tensions >= 15.0) & (tensions <= 35.0)
            high_m = tensions > 35.0
            sigma[low_m] = torch.clamp(sigma[low_m] * 0.88, min=0.015)
            sigma[high_m] = torch.clamp(sigma[high_m] * 1.15, max=0.30)

        # End-of-generation C2 tension audit & telemetry
        for i in range(N_CELLS):
            t_res = verify_tension_bound(float(tensions[i].item()), TENSION_MAX)
            t_val = float(tensions[i].item())
            if t_val < 15.0:
                tension_low_count += 1
            elif t_res["homeostatic"]:
                tension_homeo_count += 1
            else:
                tension_high_count += 1
            if t_res["excision_triggered"]:
                excisions_total += 1
                energy[i] = 0.0

        mean_e = float(energy.mean().item())
        gen_energies.append(mean_e)

        # Pack and verify I1 64-byte telemetry frame
        elapsed_rel = round(float(time.perf_counter() - t_start), 4)
        frame_vals = [
            float((energy > 0).sum().item()),
            float(tensions.mean().item()),
            elapsed_rel,
            float(energy.std().item() / (mean_e + 1e-6)),
            mean_e,
            float(toxin.mean().item()),
            float(sigma.mean().item()),
            float(polarity),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        ]
        packed = encode_frame_64b_bytes(frame_vals)
        unpacked = decode_frame_64b_bytes(packed)
        if len(packed) == 64 and len(unpacked) == 16:
            frame64_valid_count += 1

        # Inter-generational reproduction with spatial viscosity and C2 gate
        if arm == "blind_drift":
            u_d = torch.randn(N_CELLS, DIM, 4, generator=g_rng, dtype=torch.float32)
            v_d = torch.randn(N_CELLS, 4, DIM, generator=g_rng, dtype=torch.float32)
            cand_all = W + plasticity_mask * (torch.bmm(u_d, v_d) * 0.03)
            for i in range(N_CELLS):
                ok, dist, rem, _ = verify_weight_update_safety_ex(
                    W0[i], cand_all[i], R_BALL, float(germline_budget[i].item()), 0.5
                )
                if ok:
                    W[i] = cand_all[i]
                    W[i, :CORE_ROWS, :] = w_wm[:CORE_ROWS, :]
                    germline_budget[i] = rem
                    gate_commits += 1
        else:
            # Top 25% energy cells serve as spatial germline/soma parents
            k_top = N_CELLS // 4
            _, top_idx = torch.topk(energy, k_top, largest=True)
            parent_choices = top_idx[torch.randint(0, k_top, (N_CELLS,), generator=g_rng)]

            next_W = W.clone()
            next_Wgerm = W_germ.clone()
            next_pos = pos.clone()

            # Rank bottom 50% (plus dead/excised cells) for replacement
            _, replace_order = torch.argsort(energy), None
            replace_indices = torch.argsort(energy)[: N_CELLS // 2]

            for idx_t in replace_indices:
                child = int(idx_t.item())
                parent = int(parent_choices[child].item())
                mut_noise = plasticity_mask[child] * (
                    torch.randn(DIM, DIM, generator=g_rng, dtype=torch.float32) * 0.015
                )
                if arm == "lamarckian_soma":
                    cand_child = W[parent].clone() + mut_noise * 0.5
                else:
                    # Baldwinian Weismann assimilation: germline moves partially toward successful adult W,
                    # while newborn soma resets to germline prior with fresh developmental plasticity.
                    cand_child = (
                        W0[parent]
                        + 0.65 * (W_germ[parent] - W0[parent])
                        + 0.35 * (W[parent] - W0[parent])
                        + mut_noise
                    )
                cand_child[:CORE_ROWS, :] = w_wm[:CORE_ROWS, :]

                # Baseline W0 of lineage shifts with parent's frozen watermarked W0; verify against W0[parent]
                ok, dist, rem, _ = verify_weight_update_safety_ex(
                    W0[parent], cand_child, R_BALL, float(germline_budget[child].item()), 0.5
                )
                if ok:
                    W0[child] = W0[parent].clone()
                    next_Wgerm[child] = cand_child
                    next_W[child] = cand_child.clone()
                    germline_budget[child] = rem
                    # Viscous spatial budding near parent
                    bud_jitter = float(torch.randn(1, generator=g_rng).item()) * 0.03
                    next_pos[child] = float((pos[parent].item() + bud_jitter) % 1.0)
                    gate_commits += 1

            W_germ = next_Wgerm
            W = next_W
            pos = next_pos

        # Check C1/C2 invariants at end of every generation
        c_drift = float(
            torch.max(
                torch.linalg.matrix_norm(W[:, :CORE_ROWS, :] - W0[:, :CORE_ROWS, :], ord="fro", dim=(1, 2))
            ).item()
        )
        max_core_drift = max(max_core_drift, c_drift)

        resps = torch.matmul(W.transpose(1, 2), trigger_vec)
        cos_sims = torch.nn.functional.cosine_similarity(resps, target_id.unsqueeze(0), dim=1)
        min_wm_cosine = min(min_wm_cosine, float(cos_sims.min().item()))

        m_dist = float(
            torch.max(torch.linalg.matrix_norm(W - W0, ord="fro", dim=(1, 2))).item()
        )
        max_committed_dist = max(max_committed_dist, m_dist)

    selectivity = (total_nutrient_ingested - total_toxin_ingested) / (
        total_nutrient_ingested + total_toxin_ingested + 1e-6
    )
    patch_residence = total_patch_hits / max(1, total_cell_ticks)

    sig_corr = 0.0
    if len(sig_val_samples) >= 8:
        s_arr = np.asarray(sig_val_samples, dtype=np.float64)
        v_arr = np.asarray(true_val_samples, dtype=np.float64)
        if np.std(s_arr) > 1e-8 and np.std(v_arr) > 1e-8:
            sig_corr = float(abs(np.corrcoef(s_arr, v_arr)[0, 1]))

    pre_shock_late = float(np.mean(gen_energies[10:20]))
    shock_dip = float(np.mean(gen_energies[20:23]))
    post_shock_late = float(np.mean(gen_energies[30:40]))

    return {
        "seed": seed,
        "arm": arm,
        "mean_energy_all_40": float(np.mean(gen_energies)),
        "mean_energy_pre_shock_10_19": pre_shock_late,
        "mean_energy_shock_20_22": shock_dip,
        "mean_energy_post_shock_30_39": post_shock_late,
        "post_shock_recovery_delta": post_shock_late - shock_dip,
        "nutrient_selectivity": float(selectivity),
        "nutrient_ingested": round(total_nutrient_ingested, 4),
        "toxin_ingested": round(total_toxin_ingested, 4),
        "patch_residence_rate": float(patch_residence),
        "mean_signal_amplitude": float(np.mean(signal_amp_accum)),
        "abs_signal_valence_corr": sig_corr,
        "tension_low_lt15": tension_low_count,
        "tension_homeo_15_35": tension_homeo_count,
        "tension_high_gt35": tension_high_count,
        "excisions_total": excisions_total,
        "gate_commits": gate_commits,
        "frame64_valid_packets": frame64_valid_count,
        "max_core_drift": max_core_drift,
        "min_watermark_cosine": min_wm_cosine,
        "max_committed_distance": max_committed_dist,
    }


def summarize_arm(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    keys_mean = [
        "mean_energy_all_40",
        "mean_energy_pre_shock_10_19",
        "mean_energy_shock_20_22",
        "mean_energy_post_shock_30_39",
        "post_shock_recovery_delta",
        "nutrient_selectivity",
        "patch_residence_rate",
        "mean_signal_amplitude",
        "abs_signal_valence_corr",
    ]
    out: Dict[str, Any] = {f"{k}_mean": float(np.mean([r[k] for r in runs])) for k in keys_mean}
    out["tension_low_lt15_total"] = int(sum(r["tension_low_lt15"] for r in runs))
    out["tension_homeo_15_35_total"] = int(sum(r["tension_homeo_15_35"] for r in runs))
    out["tension_high_gt35_total"] = int(sum(r["tension_high_gt35"] for r in runs))
    out["excisions_total"] = int(sum(r["excisions_total"] for r in runs))
    out["frame64_valid_packets_total"] = int(sum(r["frame64_valid_packets"] for r in runs))
    out["max_core_drift"] = float(max(r["max_core_drift"] for r in runs))
    out["min_watermark_cosine"] = float(min(r["min_watermark_cosine"] for r in runs))
    out["max_committed_distance"] = float(max(r["max_committed_distance"] for r in runs))
    return out


def main() -> int:
    host = probe_host()
    t0 = time.perf_counter()
    raw: Dict[str, List[Dict[str, Any]]] = {a: [] for a in ARMS}

    for seed in SEEDS:
        ts = time.perf_counter()
        for arm in ARMS:
            raw[arm].append(run_single_colony(seed, arm))
        print(f"Seed {seed} (8 arms) complete in {(time.perf_counter() - ts):.2f}s", flush=True)

    summary = {a: summarize_arm(raw[a]) for a in ARMS}
    fe = summary["full_endogenous"]
    bd = summary["blind_drift"]
    ol = summary["open_loop_tension_75"]
    ml = summary["memory_lesion"]
    pl = summary["probe_lesion"]
    rl = summary["reafference_lesion"]
    fs = summary["free_signaling"]
    ls = summary["lamarckian_soma"]

    p1a = (
        fe["mean_energy_pre_shock_10_19_mean"] > bd["mean_energy_pre_shock_10_19_mean"]
        and fe["mean_energy_all_40_mean"] > bd["mean_energy_all_40_mean"]
    )
    p1b = (
        ol["tension_low_lt15_total"] == 0
        and fe["tension_low_lt15_total"] > 0
        and fe["tension_homeo_15_35_total"] > 0
        and fe["tension_high_gt35_total"] > 0
        and fe["mean_energy_all_40_mean"] > ol["mean_energy_all_40_mean"]
    )
    p2a = (
        fe["nutrient_selectivity_mean"] > ml["nutrient_selectivity_mean"]
        and fe["mean_energy_all_40_mean"] > ml["mean_energy_all_40_mean"]
    )
    p2b = (
        fe["nutrient_selectivity_mean"] > pl["nutrient_selectivity_mean"]
        and fe["mean_energy_all_40_mean"] > pl["mean_energy_all_40_mean"]
    )
    p3 = (
        fe["mean_energy_all_40_mean"] > rl["mean_energy_all_40_mean"]
        and fe["patch_residence_rate_mean"] > rl["patch_residence_rate_mean"]
    )
    p4 = (
        fe["mean_signal_amplitude_mean"] < fs["mean_signal_amplitude_mean"]
        and fe["abs_signal_valence_corr_mean"] > fs["abs_signal_valence_corr_mean"]
    )
    p5a = fe["post_shock_recovery_delta_mean"] > ls["post_shock_recovery_delta_mean"]
    p5b = all(
        s["max_core_drift"] == 0.0
        and s["min_watermark_cosine"] >= 0.999999
        and s["max_committed_distance"] <= R_BALL + 1e-5
        and s["frame64_valid_packets_total"] == len(SEEDS) * GENERATIONS
        for s in summary.values()
    )

    predictions = {
        "P1a_endogenous_beats_blind_drift": {
            "held": bool(p1a),
            "full_energy_10_19": fe["mean_energy_pre_shock_10_19_mean"],
            "blind_energy_10_19": bd["mean_energy_pre_shock_10_19_mean"],
            "full_energy_all_40": fe["mean_energy_all_40_mean"],
            "blind_energy_all_40": bd["mean_energy_all_40_mean"],
        },
        "P1b_visceral_tension_reaches_all_bands_vs_issue75": {
            "held": bool(p1b),
            "open_loop_lt15": ol["tension_low_lt15_total"],
            "full_lt15": fe["tension_low_lt15_total"],
            "full_homeo_15_35": fe["tension_homeo_15_35_total"],
            "full_gt35": fe["tension_high_gt35_total"],
            "full_energy": fe["mean_energy_all_40_mean"],
            "open_loop_energy": ol["mean_energy_all_40_mean"],
        },
        "P2a_memory_lesion_degrades_selectivity_and_energy": {
            "held": bool(p2a),
            "full_selectivity": fe["nutrient_selectivity_mean"],
            "memory_lesion_selectivity": ml["nutrient_selectivity_mean"],
            "full_energy": fe["mean_energy_all_40_mean"],
            "memory_lesion_energy": ml["mean_energy_all_40_mean"],
        },
        "P2b_probe_lesion_degrades_selectivity_and_energy": {
            "held": bool(p2b),
            "full_selectivity": fe["nutrient_selectivity_mean"],
            "probe_lesion_selectivity": pl["nutrient_selectivity_mean"],
            "full_energy": fe["mean_energy_all_40_mean"],
            "probe_lesion_energy": pl["mean_energy_all_40_mean"],
        },
        "P3_reafference_lesion_degrades_energy_and_residence": {
            "held": bool(p3),
            "full_energy": fe["mean_energy_all_40_mean"],
            "reafference_lesion_energy": rl["mean_energy_all_40_mean"],
            "full_residence": fe["patch_residence_rate_mean"],
            "reafference_lesion_residence": rl["patch_residence_rate_mean"],
        },
        "P4_paid_signaling_sparser_and_more_correlated_than_free": {
            "held": bool(p4),
            "paid_mean_amp": fe["mean_signal_amplitude_mean"],
            "free_mean_amp": fs["mean_signal_amplitude_mean"],
            "paid_abs_corr": fe["abs_signal_valence_corr_mean"],
            "free_abs_corr": fs["abs_signal_valence_corr_mean"],
        },
        "P5a_baldwinian_post_shock_recovery_vs_lamarckian": {
            "held": bool(p5a),
            "baldwinian_recovery_delta": fe["post_shock_recovery_delta_mean"],
            "lamarckian_recovery_delta": ls["post_shock_recovery_delta_mean"],
            "baldwinian_post_30_39": fe["mean_energy_post_shock_30_39_mean"],
            "lamarckian_post_30_39": ls["mean_energy_post_shock_30_39_mean"],
        },
        "P5b_invariants_and_frame64_all_80_runs": {
            "held": bool(p5b),
            "max_core_drift": max(s["max_core_drift"] for s in summary.values()),
            "min_watermark_cosine": min(s["min_watermark_cosine"] for s in summary.values()),
            "max_committed_distance": max(s["max_committed_distance"] for s in summary.values()),
            "frame64_valid_packets_per_arm": min(s["frame64_valid_packets_total"] for s in summary.values()),
        },
    }

    out = {
        "experiment": "E16",
        "environment": host,
        "protocol": {
            "seeds": SEEDS,
            "n_cells": N_CELLS,
            "dim": DIM,
            "core_rows": CORE_ROWS,
            "r_invariant": R_BALL,
            "generations": GENERATIONS,
            "bouts_per_gen": BOUTS_PER_GEN,
            "ticks_per_bout": TICKS_PER_BOUT,
            "shock_generation": SHOCK_GEN,
            "arms": ARMS,
        },
        "predictions": predictions,
        "summary": summary,
        "elapsed_seconds_total": round(time.perf_counter() - t0, 2),
        "runs": raw,
    }

    out_path = HERE / "results.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\n=== E16 Prediction Verdicts ===")
    for k, v in predictions.items():
        print(f"  {k}: {'HELD' if v['held'] else 'FAILED'} -> {v}")

    return 0 if p5b else 1


if __name__ == "__main__":
    raise SystemExit(main())
