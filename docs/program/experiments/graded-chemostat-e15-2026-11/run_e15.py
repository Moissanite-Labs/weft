#!/usr/bin/env python3
"""
Experiment E15 Runner: Graded-Difficulty Chemostat, Spore Sweep, and Step Cooling
=================================================================================
Executes the preregistered protocol in `PREREGISTRATION.md`:
  - Seeds 20261121..20261130 (10 seeds), 60 generations, 256 cells, dim=128, 8 tiles
  - Graded landscape: tile_ranks=[1, 2, 4, 6, 8, 12, 16, 24],
    tile_condition_numbers=[1.0, 1.5, 2.0, 3.0, 4.5, 6.0, 9.0, 12.0]
  - 7 arms comparing E14 baselines against the graded_chemostat allocation rule + spore sweep + cooling
  - Pinned-thread (threads=1) and default multi-core vectorization benchmark (P4)
Writes `results.json` in this directory and exits 0 if invariant checks (P5) hold.
"""

from __future__ import annotations

import json
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

from weft.runtime.mac.swarm_loom import VectorizedPlasmColony  # noqa: E402

SEEDS = list(range(20261121, 20261131))
N_CELLS = 256
DIM = 128
N_NICHES = 8
GENERATIONS = 60
TILE_RANKS = [1, 2, 4, 6, 8, 12, 16, 24]
TILE_CONDS = [1.0, 1.5, 2.0, 3.0, 4.5, 6.0, 9.0, 12.0]

ARMS = [
    {"name": "hgt_foraging", "mode": "hgt_foraging", "spore_fraction": 0.0, "adaptive_step": False},
    {"name": "dissipative_chemostat", "mode": "dissipative_chemostat", "spore_fraction": 0.50, "adaptive_step": False},
    {"name": "graded_chemostat_sp000", "mode": "graded_chemostat", "spore_fraction": 0.00, "adaptive_step": False},
    {"name": "graded_chemostat_sp125", "mode": "graded_chemostat", "spore_fraction": 0.125, "adaptive_step": False},
    {"name": "graded_chemostat_sp250", "mode": "graded_chemostat", "spore_fraction": 0.25, "adaptive_step": False},
    {"name": "graded_chemostat_sp500", "mode": "graded_chemostat", "spore_fraction": 0.50, "adaptive_step": False},
    {"name": "graded_chemostat_cooled", "mode": "graded_chemostat", "spore_fraction": 0.25, "adaptive_step": True},
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
        "mps_available": bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_available()),
        "default_num_threads": int(torch.get_num_threads()),
    }


def run_vectorization_benchmark() -> Dict[str, Any]:
    """Evaluate P4 under pinned 1-thread CPU, default multi-thread CPU, and MPS if available.

    Both the serial path and the batched path touch all `n_cells` cells, so
    the timings share a working set. An earlier draft timed 32 cells on the
    serial path and extrapolated 16x, which does not match the batched
    working set of 512.
    """
    n_cells = 512
    dim = 256
    n_niches = 8
    batch_size = 16
    n_iters = 20

    orig_threads = torch.get_num_threads()
    records: Dict[str, Any] = {
        "n_cells": n_cells,
        "dim": dim,
        "n_niches": n_niches,
        "batch_size": batch_size,
        "n_iters": n_iters,
        "serial_cells": n_cells,
        "batched_cells": n_cells,
        "default_num_threads": int(orig_threads),
    }

    for label, n_threads in (("pinned_1_thread", 1), (f"multicore_{orig_threads}_threads", orig_threads)):
        torch.set_num_threads(n_threads)
        torch.manual_seed(42)
        w_cpu = torch.randn(n_cells, dim, dim, dtype=torch.float32)
        w0_cpu = torch.randn(n_cells, dim, dim, dtype=torch.float32)
        x_cpu = torch.randn(n_niches, batch_size, dim, dtype=torch.float32)

        # Warmup on the full working set.
        for i in range(4):
            for m in range(n_niches):
                _ = torch.matmul(x_cpu[m], w_cpu[i])
            _ = torch.linalg.norm(w_cpu[i] - w0_cpu[i])
        _ = torch.matmul(x_cpu.unsqueeze(0), w_cpu.unsqueeze(1))
        _ = torch.linalg.matrix_norm(w_cpu - w0_cpu, ord="fro", dim=(1, 2))

        t0 = time.perf_counter()
        for _ in range(n_iters):
            for i in range(n_cells):
                for m in range(n_niches):
                    _ = torch.matmul(x_cpu[m], w_cpu[i])
                _ = torch.linalg.norm(w_cpu[i] - w0_cpu[i])
        t_serial_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0

        t0 = time.perf_counter()
        for _ in range(n_iters):
            _ = torch.matmul(x_cpu.unsqueeze(0), w_cpu.unsqueeze(1))
            _ = torch.linalg.matrix_norm(w_cpu - w0_cpu, ord="fro", dim=(1, 2))
        t_batched_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0

        records[label] = {
            "threads": n_threads,
            "serial_cells": n_cells,
            "batched_cells": n_cells,
            "serial_cpu_ms": round(t_serial_ms, 4),
            "batched_cpu_ms": round(t_batched_ms, 4),
            "speedup_batched_vs_serial": round(t_serial_ms / t_batched_ms, 4) if t_batched_ms > 0 else None,
        }

    torch.set_num_threads(orig_threads)

    has_mps = bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
    if has_mps:
        dev = torch.device("mps")
        torch.manual_seed(42)
        w_mps = torch.randn(n_cells, dim, dim, dtype=torch.float32, device=dev)
        w0_mps = torch.randn(n_cells, dim, dim, dtype=torch.float32, device=dev)
        x_mps = torch.randn(n_niches, batch_size, dim, dtype=torch.float32, device=dev)
        for _ in range(5):
            _ = torch.matmul(x_mps.unsqueeze(0), w_mps.unsqueeze(1))
            _ = torch.linalg.matrix_norm(w_mps - w0_mps, ord="fro", dim=(1, 2))
            torch.mps.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_iters):
            _ = torch.matmul(x_mps.unsqueeze(0), w_mps.unsqueeze(1))
            _ = torch.linalg.matrix_norm(w_mps - w0_mps, ord="fro", dim=(1, 2))
            torch.mps.synchronize()
        t_mps_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0
        records["mps"] = {
            "batched_mps_ms": round(t_mps_ms, 4),
            "speedup_vs_pinned_1_thread_serial": round(
                records["pinned_1_thread"]["serial_cpu_ms"] / t_mps_ms, 4
            ),
        }
    else:
        records["mps"] = {"available": False, "note": "MPS unavailable in current execution environment"}

    return records


def summarize_arm(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    min_err_red = [1.0 - r["mean_min_tile_error_ratio"] for r in runs]
    assigned_err_red = [1.0 - r["mean_assigned_error_ratio"] for r in runs]
    worst_tile_red = [1.0 - r["worst_tile_error_ratio"] for r in runs]
    hard_tile_shares = [
        (r["tile_cell_counts"][6] + r["tile_cell_counts"][7]) / float(N_CELLS) for r in runs
    ]
    easy_tile_shares = [
        (r["tile_cell_counts"][0] + r["tile_cell_counts"][1]) / float(N_CELLS) for r in runs
    ]
    per_tile_red = np.mean(
        [[1.0 - x for x in r["per_tile_best_error_ratio"]] for r in runs], axis=0
    ).tolist()
    per_tile_counts = np.mean([r["tile_cell_counts"] for r in runs], axis=0).tolist()

    return {
        "min_tile_error_reduction_mean": float(np.mean(min_err_red)),
        "min_tile_error_reduction_std": float(np.std(min_err_red)),
        "assigned_error_reduction_mean": float(np.mean(assigned_err_red)),
        "worst_tile_error_reduction_mean": float(np.mean(worst_tile_red)),
        "worst_tile_error_reduction_std": float(np.std(worst_tile_red)),
        "hard_tiles_6_7_cell_share_mean": float(np.mean(hard_tile_shares)),
        "easy_tiles_0_1_cell_share_mean": float(np.mean(easy_tile_shares)),
        "per_tile_error_reduction_mean": [round(float(x), 6) for x in per_tile_red],
        "per_tile_cell_counts_mean": [round(float(x), 2) for x in per_tile_counts],
        "beta_win_share_mean": float(np.mean([r["beta_win_share"] for r in runs])),
        "niche_coverage_mean": float(np.mean([r["niche_coverage"] for r in runs])),
        "niche_entropy_bits_mean": float(np.mean([r["niche_entropy_bits"] for r in runs])),
        "idle_cells_mean": float(np.mean([r["idle_surviving_cells"] for r in runs])),
        "idle_cells_max": int(np.max([r["idle_surviving_cells"] for r in runs])),
        "recolonizations_mean": float(np.mean([r["apoptosis_recolonizations"] for r in runs])),
        "spore_births_mean": float(np.mean([r["spore_births"] for r in runs])),
        "mean_step_scale_final": float(np.mean([r["mean_step_scale"] for r in runs])),
        "max_core_drift": float(np.max([r["max_core_drift"] for r in runs])),
        "min_watermark_cosine": float(np.min([r["min_watermark_cosine"] for r in runs])),
        "max_committed_distance": float(np.max([r["max_committed_distance"] for r in runs])),
    }


def main() -> int:
    device = "mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"
    host = probe_host()
    print(f"Host: {host['chip']} | Device: {device} | PyTorch {host['torch']}")

    vec_bench = run_vectorization_benchmark()
    print("Vectorization benchmark:", json.dumps(vec_bench))

    raw_runs: Dict[str, List[Dict[str, Any]]] = {a["name"]: [] for a in ARMS}
    t_all = time.perf_counter()

    for seed in SEEDS:
        t_s = time.perf_counter()
        for arm in ARMS:
            colony = VectorizedPlasmColony(
                device=device,
                n_cells=N_CELLS,
                dim=DIM,
                n_niches=N_NICHES,
                subspace_rank=4,
                r_invariant=10.0,
                initial_energy=100.0,
                basal_upkeep=2.0,
                tile_bounty=160.0,
                seed=seed,
                tile_ranks=TILE_RANKS,
                tile_condition_numbers=TILE_CONDS,
                spore_fraction=arm["spore_fraction"],
                adaptive_step=arm["adaptive_step"],
            )
            rep = colony.run(generations=GENERATIONS, mode=arm["mode"])
            rep["seed"] = seed
            raw_runs[arm["name"]].append(rep)
            colony.close()
        print(f"Seed {seed} complete in {(time.perf_counter() - t_s):.2f}s", flush=True)

    summary = {arm["name"]: summarize_arm(raw_runs[arm["name"]]) for arm in ARMS}

    forag = summary["hgt_foraging"]
    dissip = summary["dissipative_chemostat"]
    sp000 = summary["graded_chemostat_sp000"]
    sp125 = summary["graded_chemostat_sp125"]
    sp250 = summary["graded_chemostat_sp250"]
    sp500 = summary["graded_chemostat_sp500"]
    cooled = summary["graded_chemostat_cooled"]

    p1a_held = sp250["hard_tiles_6_7_cell_share_mean"] > forag["hard_tiles_6_7_cell_share_mean"]
    p1b_held = (
        sp250["worst_tile_error_reduction_mean"] > forag["worst_tile_error_reduction_mean"]
        and sp250["worst_tile_error_reduction_mean"] > dissip["worst_tile_error_reduction_mean"]
    )
    p2a_held = (
        max(s["idle_cells_max"] for s in (sp000, sp125, sp250, sp500)) == 0
        and forag["idle_cells_mean"] > 0.0
    )
    best_lower_sp = max(sp125["min_tile_error_reduction_mean"], sp250["min_tile_error_reduction_mean"])
    p2b_held = (
        best_lower_sp > sp500["min_tile_error_reduction_mean"]
        and best_lower_sp >= 0.95 * forag["min_tile_error_reduction_mean"]
    )
    p3a_held = cooled["min_tile_error_reduction_mean"] >= 1.5 * sp250["min_tile_error_reduction_mean"]
    p3b_held = cooled["min_tile_error_reduction_mean"] > 0.10

    multicore_key = [k for k in vec_bench if k.startswith("multicore_")][0]
    p4_held = (
        vec_bench["pinned_1_thread"]["speedup_batched_vs_serial"] >= 5.0
        and vec_bench[multicore_key]["speedup_batched_vs_serial"] >= 5.0
    )
    p5_held = all(
        s["max_core_drift"] == 0.0
        and s["min_watermark_cosine"] >= 0.999999
        and s["max_committed_distance"] <= 10.0
        for s in summary.values()
    )

    predictions = {
        "P1a_hard_tile_allocation": {
            "held": bool(p1a_held),
            "graded_sp250_hard_share": sp250["hard_tiles_6_7_cell_share_mean"],
            "hgt_foraging_hard_share": forag["hard_tiles_6_7_cell_share_mean"],
            "dissipative_chemostat_hard_share": dissip["hard_tiles_6_7_cell_share_mean"],
        },
        "P1b_worst_tile_error_reduction": {
            "held": bool(p1b_held),
            "graded_sp250_worst_tile_reduction": sp250["worst_tile_error_reduction_mean"],
            "hgt_foraging_worst_tile_reduction": forag["worst_tile_error_reduction_mean"],
            "dissipative_chemostat_worst_tile_reduction": dissip["worst_tile_error_reduction_mean"],
        },
        "P2a_zero_coasting_across_spore_sweep": {
            "held": bool(p2a_held),
            "graded_max_idle": max(s["idle_cells_max"] for s in (sp000, sp125, sp250, sp500)),
            "hgt_foraging_mean_idle": forag["idle_cells_mean"],
        },
        "P2b_lower_spore_rate_recovers_error": {
            "held": bool(p2b_held),
            "sp125_min_tile_reduction": sp125["min_tile_error_reduction_mean"],
            "sp250_min_tile_reduction": sp250["min_tile_error_reduction_mean"],
            "sp500_min_tile_reduction": sp500["min_tile_error_reduction_mean"],
            "hgt_foraging_min_tile_reduction": forag["min_tile_error_reduction_mean"],
        },
        "P3a_cooling_1_5x_over_fixed_step": {
            "held": bool(p3a_held),
            "cooled_min_tile_reduction": cooled["min_tile_error_reduction_mean"],
            "sp250_min_tile_reduction": sp250["min_tile_error_reduction_mean"],
            "ratio": cooled["min_tile_error_reduction_mean"] / max(1e-9, sp250["min_tile_error_reduction_mean"]),
        },
        "P3b_cooling_exceeds_10pct": {
            "held": bool(p3b_held),
            "cooled_min_tile_reduction": cooled["min_tile_error_reduction_mean"],
        },
        "P4_pinned_and_multicore_batched_speedup": {
            "held": bool(p4_held),
            "pinned_1_thread_speedup": vec_bench["pinned_1_thread"]["speedup_batched_vs_serial"],
            "multicore_speedup": vec_bench[multicore_key]["speedup_batched_vs_serial"],
        },
        "P5_invariants_all_70_runs": {
            "held": bool(p5_held),
            "max_core_drift": max(s["max_core_drift"] for s in summary.values()),
            "min_watermark_cosine": min(s["min_watermark_cosine"] for s in summary.values()),
            "max_committed_distance": max(s["max_committed_distance"] for s in summary.values()),
        },
    }

    out = {
        "experiment": "E15",
        "environment": host,
        "device": device,
        "protocol": {
            "seeds": SEEDS,
            "n_cells": N_CELLS,
            "dim": DIM,
            "n_niches": N_NICHES,
            "generations": GENERATIONS,
            "tile_ranks": TILE_RANKS,
            "tile_condition_numbers": TILE_CONDS,
        },
        "vectorization_benchmark": vec_bench,
        "predictions": predictions,
        "summary": summary,
        "elapsed_seconds_total": round(time.perf_counter() - t_all, 2),
        "runs": raw_runs,
    }

    out_path = HERE / "results.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\n=== E15 Prediction Verdicts ===")
    for k, v in predictions.items():
        print(f"  {k}: {'HELD' if v['held'] else 'FAILED'} -> {v}")

    return 0 if p5_held else 1


if __name__ == "__main__":
    raise SystemExit(main())
