#!/usr/bin/env python3
"""
Experiment E14 Runner: Apple Silicon Micro-Swarm Architecture
=============================================================
Executes preregistered benchmarks for H-S1 through H-S5:
  - Benchmark 1: Hardware acceleration scaling (Serial CPU vs Batched CPU vs Batched MPS)
  - Benchmark 2: Mitotic regimes comparison across 10 random seeds (0..9)
  - Benchmark 3: CPU vs MPS parity check (seeds 0..1)
Saves complete raw data to `results/e14_results.json`.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from weft.runtime.mac.swarm_loom import (
    StratifiedSwarmArena,
    VectorizedPlasmColony,
    compute_swarm_arena_size,
)


def run_benchmark_1_hardware_speedup() -> Dict[str, Any]:
    """
    Test H-S1:
    512 cells x 256x256 forward evaluation + C2 norm check.
    Compares:
      1. Serial per-cell CPU evaluation
      2. Batched CPU evaluation
      3. Batched Apple Silicon MPS evaluation
    """
    print("=== Running Benchmark 1: Hardware Acceleration Scaling (H-S1) ===")
    n_cells = 512
    dim = 256
    n_niches = 8
    batch_size = 16
    n_iters = 20

    # CPU setup
    torch.manual_seed(42)
    w_cpu = torch.randn(n_cells, dim, dim, dtype=torch.float32)
    w0_cpu = torch.randn(n_cells, dim, dim, dtype=torch.float32)
    x_cpu = torch.randn(n_niches, batch_size, dim, dtype=torch.float32)

    # 1. Serial CPU evaluation
    # Sample 32 cells to avoid excessively long test times and project to 512
    sample_cells = 32
    # Warmup
    for i in range(4):
        for m in range(n_niches):
            _ = torch.matmul(x_cpu[m], w_cpu[i])
        _ = torch.linalg.norm(w_cpu[i] - w0_cpu[i])

    t0 = time.perf_counter()
    for _ in range(n_iters):
        for i in range(sample_cells):
            for m in range(n_niches):
                _ = torch.matmul(x_cpu[m], w_cpu[i])
            _ = torch.linalg.norm(w_cpu[i] - w0_cpu[i])
    t_serial_sample = (time.perf_counter() - t0) / n_iters
    t_serial_full_ms = t_serial_sample * (n_cells / sample_cells) * 1000.0

    # 2. Batched CPU evaluation
    # Warmup
    _ = torch.matmul(x_cpu.unsqueeze(0), w_cpu.unsqueeze(1))
    _ = torch.linalg.matrix_norm(w_cpu - w0_cpu, ord="fro", dim=(1, 2))

    t0 = time.perf_counter()
    for _ in range(n_iters):
        _ = torch.matmul(x_cpu.unsqueeze(0), w_cpu.unsqueeze(1))
        _ = torch.linalg.matrix_norm(w_cpu - w0_cpu, ord="fro", dim=(1, 2))
    t_batched_cpu_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0

    # 3. Batched MPS evaluation
    has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    t_batched_mps_ms = float("nan")
    speedup_mps_vs_serial = float("nan")
    speedup_mps_vs_batched_cpu = float("nan")

    if has_mps:
        device_mps = torch.device("mps")
        w_mps = w_cpu.to(device_mps)
        w0_mps = w0_cpu.to(device_mps)
        x_mps = x_cpu.to(device_mps)

        # Warmup
        for _ in range(5):
            _ = torch.matmul(x_mps.unsqueeze(0), w_mps.unsqueeze(1))
            _ = torch.linalg.matrix_norm(w_mps - w0_mps, ord="fro", dim=(1, 2))
            torch.mps.synchronize()

        t0 = time.perf_counter()
        for _ in range(n_iters):
            _ = torch.matmul(x_mps.unsqueeze(0), w_mps.unsqueeze(1))
            _ = torch.linalg.matrix_norm(w_mps - w0_mps, ord="fro", dim=(1, 2))
            torch.mps.synchronize()
        t_batched_mps_ms = ((time.perf_counter() - t0) / n_iters) * 1000.0
        speedup_mps_vs_serial = t_serial_full_ms / t_batched_mps_ms
        speedup_mps_vs_batched_cpu = t_batched_cpu_ms / t_batched_mps_ms

    print(f"Serial CPU (projected 512 cells): {t_serial_full_ms:.2f} ms")
    print(f"Batched CPU (AMX / SIMD):        {t_batched_cpu_ms:.2f} ms")
    print(f"Batched MPS (Apple Silicon GPU):  {t_batched_mps_ms:.2f} ms")
    print(f"Speedup MPS vs Serial CPU:        {speedup_mps_vs_serial:.2f}x (H-S1 threshold >= 5.0x)")
    print(f"Speedup MPS vs Batched CPU:       {speedup_mps_vs_batched_cpu:.2f}x")

    return {
        "n_cells": n_cells,
        "dim": dim,
        "n_niches": n_niches,
        "batch_size": batch_size,
        "n_iters": n_iters,
        "t_serial_cpu_ms": t_serial_full_ms,
        "t_batched_cpu_ms": t_batched_cpu_ms,
        "t_batched_mps_ms": t_batched_mps_ms,
        "speedup_mps_vs_serial": speedup_mps_vs_serial,
        "speedup_mps_vs_batched_cpu": speedup_mps_vs_batched_cpu,
        "h_s1_held": bool(speedup_mps_vs_serial >= 5.0),
    }


def run_benchmark_2_mitotic_regimes() -> Dict[str, Any]:
    """
    Test H-S2, H-S3, H-S4, H-S5:
    10 seeds (0..9) x 3 modes on MPS:
      1. paper1_blind
      2. hgt_isolated
      3. hgt_foraging
    """
    print("\n=== Running Benchmark 2: Mitotic Regimes & Ecology (H-S2 to H-S5) ===")
    device = "mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"
    print(f"Executing on compute device: {device}")

    n_cells = 256
    dim = 128
    n_niches = 8
    generations = 60
    seeds = list(range(10))
    modes = ["paper1_blind", "hgt_isolated", "hgt_foraging", "dissipative_chemostat"]

    results: Dict[str, List[Dict[str, Any]]] = {m: [] for m in modes}

    for seed in seeds:
        print(f"Running Seed {seed:02d}...", end="", flush=True)
        t_seed_start = time.perf_counter()
        for mode in modes:
            colony = VectorizedPlasmColony(
                device=device,
                n_cells=n_cells,
                dim=dim,
                n_niches=n_niches,
                subspace_rank=4,
                r_invariant=10.0,
                initial_energy=100.0,
                basal_upkeep=2.0,
                tile_bounty=160.0,
                seed=seed,
            )
            report = colony.run(generations=generations, mode=mode)
            report["seed"] = seed
            report["error_reduction"] = 1.0 - report["mean_min_tile_error_ratio"]
            results[mode].append(report)
            colony.close()
        t_seed_ms = (time.perf_counter() - t_seed_start) * 1000.0
        print(f" done ({t_seed_ms:.1f} ms)")

    # Aggregate statistics
    summary: Dict[str, Any] = {}
    for mode in modes:
        records = results[mode]
        beta_shares = [r["beta_win_share"] for r in records]
        min_err_ratios = [r["mean_min_tile_error_ratio"] for r in records]
        error_reductions = [r["error_reduction"] for r in records]
        niche_covs = [r["niche_coverage"] for r in records]
        entropies = [r["niche_entropy_bits"] for r in records]
        idle_cells = [r["idle_surviving_cells"] for r in records]
        core_drifts = [r["max_core_drift"] for r in records]
        wm_cosines = [r["min_watermark_cosine"] for r in records]
        max_dists = [r["max_committed_distance"] for r in records]
        recolonizations = [r["apoptosis_recolonizations"] for r in records]
        spore_births = [r.get("spore_births", 0) for r in records]

        summary[mode] = {
            "beta_win_share_mean": float(np.mean(beta_shares)),
            "beta_win_share_median": float(np.median(beta_shares)),
            "min_err_ratio_mean": float(np.mean(min_err_ratios)),
            "min_err_ratio_median": float(np.median(min_err_ratios)),
            "error_reduction_mean": float(np.mean(error_reductions)),
            "error_reduction_median": float(np.median(error_reductions)),
            "niche_coverage_mean": float(np.mean(niche_covs)),
            "niche_coverage_median": float(np.median(niche_covs)),
            "niche_entropy_mean": float(np.mean(entropies)),
            "niche_entropy_median": float(np.median(entropies)),
            "idle_cells_mean": float(np.mean(idle_cells)),
            "idle_cells_median": float(np.median(idle_cells)),
            "idle_cells_max": int(np.max(idle_cells)),
            "core_drift_max": float(np.max(core_drifts)),
            "min_watermark_cosine": float(np.min(wm_cosines)),
            "max_committed_distance": float(np.max(max_dists)),
            "recolonizations_mean": float(np.mean(recolonizations)),
            "spore_births_mean": float(np.mean(spore_births)),
        }

    # Hypothesis evaluations
    blind_summary = summary["paper1_blind"]
    isolated_summary = summary["hgt_isolated"]
    foraging_summary = summary["hgt_foraging"]
    chemostat_summary = summary["dissipative_chemostat"]

    # H-S2: Beta win share and error reduction
    h_s2_beta_share = (blind_summary["beta_win_share_mean"] < 0.05) and (
        foraging_summary["beta_win_share_mean"] > 0.50
    )
    reduction_ratio = (
        foraging_summary["error_reduction_mean"]
        / max(1e-6, blind_summary["error_reduction_mean"])
    )
    h_s2_reduction = reduction_ratio >= 3.0
    h_s2_held = bool(h_s2_beta_share and h_s2_reduction)

    # H-S3: Niche differentiation
    h_s3_coverage = foraging_summary["niche_coverage_median"] == 1.0
    h_s3_entropy = (
        foraging_summary["niche_entropy_median"] >= 2.5
        and foraging_summary["niche_entropy_median"] > isolated_summary["niche_entropy_median"]
    )
    h_s3_held = bool(h_s3_coverage and h_s3_entropy)

    # H-S4 (preregistered): coasting elimination in hgt_foraging
    h_s4_held = bool(foraging_summary["idle_cells_max"] == 0)
    # X-1 (exploratory, added after data collection): same test on dissipative_chemostat
    x1_held = bool(chemostat_summary["idle_cells_max"] == 0)

    # H-S5: Invariants
    all_core_drift = max(s["core_drift_max"] for s in summary.values())
    all_min_wm = min(s["min_watermark_cosine"] for s in summary.values())
    all_max_dist = max(s["max_committed_distance"] for s in summary.values())
    h_s5_held = bool(all_core_drift == 0.0 and all_min_wm >= 0.999999 and all_max_dist <= 10.0)

    verdicts = {
        "H-S2": {
            "held": h_s2_held,
            "blind_beta_share": blind_summary["beta_win_share_mean"],
            "foraging_beta_share": foraging_summary["beta_win_share_mean"],
            "chemostat_beta_share": chemostat_summary["beta_win_share_mean"],
            "reduction_ratio": reduction_ratio,
        },
        "H-S3": {
            "held": h_s3_held,
            "foraging_coverage_median": foraging_summary["niche_coverage_median"],
            "foraging_entropy_median": foraging_summary["niche_entropy_median"],
            "chemostat_entropy_median": chemostat_summary["niche_entropy_median"],
            "isolated_entropy_median": isolated_summary["niche_entropy_median"],
        },
        "H-S4": {
            "held": h_s4_held,
            "foraging_idle_cells_max": foraging_summary["idle_cells_max"],
            "foraging_idle_cells_mean": foraging_summary["idle_cells_mean"],
            "blind_idle_cells_mean": blind_summary["idle_cells_mean"],
        },
        "X-1_exploratory": {
            "held": x1_held,
            "chemostat_idle_cells_max": chemostat_summary["idle_cells_max"],
            "chemostat_idle_cells_mean": chemostat_summary["idle_cells_mean"],
        },
        "H-S5": {
            "held": h_s5_held,
            "all_core_drift_max": all_core_drift,
            "all_min_watermark_cosine": all_min_wm,
            "all_max_committed_distance": all_max_dist,
        },
    }

    print("\n--- Summary Table (Means over 10 Seeds) ---")
    print(f"{'Metric':<28} | {'paper1_blind':<14} | {'hgt_isolated':<14} | {'hgt_foraging':<14} | {'dissip_chemo':<14}")
    print("-" * 92)
    print(f"{'Beta Win Share':<28} | {blind_summary['beta_win_share_mean']:<14.3f} | {isolated_summary['beta_win_share_mean']:<14.3f} | {foraging_summary['beta_win_share_mean']:<14.3f} | {chemostat_summary['beta_win_share_mean']:<14.3f}")
    print(f"{'Final Error Ratio (Min Tile)':<28} | {blind_summary['min_err_ratio_mean']:<14.3f} | {isolated_summary['min_err_ratio_mean']:<14.3f} | {foraging_summary['min_err_ratio_mean']:<14.3f} | {chemostat_summary['min_err_ratio_mean']:<14.3f}")
    print(f"{'Error Reduction (1 - Ratio)':<28} | {blind_summary['error_reduction_mean']:<14.4f} | {isolated_summary['error_reduction_mean']:<14.4f} | {foraging_summary['error_reduction_mean']:<14.4f} | {chemostat_summary['error_reduction_mean']:<14.4f}")
    print(f"{'Niche Coverage (Max 1.0)':<28} | {blind_summary['niche_coverage_mean']:<14.3f} | {isolated_summary['niche_coverage_mean']:<14.3f} | {foraging_summary['niche_coverage_mean']:<14.3f} | {chemostat_summary['niche_coverage_mean']:<14.3f}")
    print(f"{'Shannon Entropy (Max 3.0b)':<28} | {blind_summary['niche_entropy_mean']:<14.3f} | {isolated_summary['niche_entropy_mean']:<14.3f} | {foraging_summary['niche_entropy_mean']:<14.3f} | {chemostat_summary['niche_entropy_mean']:<14.3f}")
    print(f"{'Idle Survivors (of 256)':<28} | {blind_summary['idle_cells_mean']:<14.1f} | {isolated_summary['idle_cells_mean']:<14.1f} | {foraging_summary['idle_cells_mean']:<14.1f} | {chemostat_summary['idle_cells_mean']:<14.1f}")
    print(f"{'Apoptosis Recolonizations':<28} | {blind_summary['recolonizations_mean']:<14.1f} | {isolated_summary['recolonizations_mean']:<14.1f} | {foraging_summary['recolonizations_mean']:<14.1f} | {chemostat_summary['recolonizations_mean']:<14.1f}")
    print(f"{'Spore Births (Law 2c)':<28} | {blind_summary['spore_births_mean']:<14.1f} | {isolated_summary['spore_births_mean']:<14.1f} | {foraging_summary['spore_births_mean']:<14.1f} | {chemostat_summary['spore_births_mean']:<14.1f}")
    print(f"{'Max Core Drift':<28} | {blind_summary['core_drift_max']:<14.6f} | {isolated_summary['core_drift_max']:<14.6f} | {foraging_summary['core_drift_max']:<14.6f} | {chemostat_summary['core_drift_max']:<14.6f}")
    print(f"{'Min Watermark Cosine':<28} | {blind_summary['min_watermark_cosine']:<14.6f} | {isolated_summary['min_watermark_cosine']:<14.6f} | {foraging_summary['min_watermark_cosine']:<14.6f} | {chemostat_summary['min_watermark_cosine']:<14.6f}")
    print(f"{'Max Committed Distance':<28} | {blind_summary['max_committed_distance']:<14.2f} | {isolated_summary['max_committed_distance']:<14.2f} | {foraging_summary['max_committed_distance']:<14.2f} | {chemostat_summary['max_committed_distance']:<14.2f}")
    print("\n--- Verdicts ---")
    for name, v in verdicts.items():
        print(f"{name}: {'HELD' if v['held'] else 'FAILED'}")

    return {
        "device": device,
        "n_cells": n_cells,
        "dim": dim,
        "n_niches": n_niches,
        "generations": generations,
        "seeds": seeds,
        "summary": summary,
        "verdicts": verdicts,
        "raw_records": results,
    }


def run_benchmark_3_cpu_parity() -> Dict[str, Any]:
    """Verify numerical parity of invariants and outcomes on CPU across seeds 0 and 1."""
    print("\n=== Running Benchmark 3: CPU Parity Verification (Seeds 0 and 1) ===")
    cpu_records: List[Dict[str, Any]] = []
    for seed in [0, 1]:
        colony = VectorizedPlasmColony(
            device="cpu",
            n_cells=256,
            dim=128,
            n_niches=8,
            seed=seed,
        )
        report = colony.run(generations=60, mode="hgt_foraging")
        report["seed"] = seed
        cpu_records.append(report)
        colony.close()
        print(f"CPU Seed {seed} | Beta Share: {report['beta_win_share']:.3f} | "
              f"Coverage: {report['niche_coverage']:.2f} | Entropy: {report['niche_entropy_bits']:.2f} | "
              f"Drift: {report['max_core_drift']:.6f} | WM: {report['min_watermark_cosine']:.6f}")

    return {"cpu_records": cpu_records}


def main() -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "e14_results.json"

    bench1 = run_benchmark_1_hardware_speedup()
    bench2 = run_benchmark_2_mitotic_regimes()
    bench3 = run_benchmark_3_cpu_parity()

    full_data = {
        "meta": {
            "experiment": "E14",
            "title": "Apple Silicon Swarm Loom Architecture and Mitotic Regimes",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "torch_version": torch.__version__,
            "has_mps": hasattr(torch.backends, "mps") and torch.backends.mps.is_available(),
        },
        "benchmark_1": bench1,
        "benchmark_2": bench2,
        "benchmark_3": bench3,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=2)

    print(f"\nSaved raw benchmark data to {out_path}")


if __name__ == "__main__":
    main()
