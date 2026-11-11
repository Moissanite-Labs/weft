#!/usr/bin/env python3
"""Experiments for Paper 1, "Models as cells".

Every number in the paper comes from this script, which imports the tested
modules in weft/runtime (C1 plasm, C2 invariants). Run from the repository root:

    python3 papers/01-models-as-cells/experiments.py           # write results.json and figures/
    python3 papers/01-models-as-cells/experiments.py --check   # CI: recompute, compare, write nothing
    python3 papers/01-models-as-cells/experiments.py --device mps # write results-mps-m1.json

Default device is CPU and deterministic: each run seeds torch, and the Plasm cycle is forced
onto the CPU so CI results do not depend on whether Apple MPS is available.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

import weft.runtime.plasm.plasm as plasm  # noqa: E402
from weft.runtime.invariants import (  # noqa: E402
    R_INVARIANT,
    TENSION_MAX,
    load_conformance_vectors,
    verify_weight_update_safety_ex,
)

plasm.select_compute_device = lambda: torch.device("cpu")  # default deterministic CPU runs

SEEDS = list(range(10))
GENERATIONS = 12
DIM = 256


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def probe_environment(device_name: str) -> dict:
    env = {
        "commit": git_commit(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "machine": platform.machine(),
        "system": platform.system(),
        "device": device_name,
    }
    if device_name == "mps":
        brand = None
        for cmd in (["sysctl", "-n", "machdep.cpu.brand_string"], ["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"]):
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
                if out:
                    brand = out
                    break
            except Exception:
                pass
        if brand:
            env["chip"] = brand

        try:
            sw_ver = subprocess.check_output(["sw_vers", "-productVersion"], stderr=subprocess.DEVNULL).decode().strip()
            sw_build = subprocess.check_output(["sw_vers", "-buildVersion"], stderr=subprocess.DEVNULL).decode().strip()
            if sw_ver:
                env["os_version"] = sw_ver
            if sw_build:
                env["os_build"] = sw_build
        except Exception:
            pass

        env["mps_available"] = bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
        env["mps_built"] = bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_built())
    return env


# --- E1: equal sizes do not mean a small move --------------------------------
def e1_compared_sizes(device: torch.device = torch.device("cpu")) -> dict:
    """W' = cos(t) W + sin(t) Q with <W, Q>_F = 0 and ||Q|| = ||W||.

    Then ||W'|| = ||W|| for every t, while ||W' - W|| = 2 sin(t/2) ||W||.
    A check on |‖W'‖ - ‖W‖| passes every t; the baseline-distance gate does not.
    """
    dtype = torch.float32 if device.type == "mps" else torch.float64
    g = torch.Generator(device="cpu").manual_seed(7)
    w = (torch.randn(DIM, DIM, generator=g, dtype=dtype) * 0.05).to(device)
    q = torch.randn(DIM, DIM, generator=g, dtype=dtype).to(device)
    q = q - (torch.sum(q * w) / torch.sum(w * w)) * w  # orthogonal to W in the Frobenius inner product
    q = q / torch.linalg.norm(q) * torch.linalg.norm(w)
    norm_w = float(torch.linalg.norm(w).item())
    radius = 0.25 * norm_w
    rows = []
    for k in range(0, 37):
        t = math.pi * k / 36
        cand = math.cos(t) * w + math.sin(t) * q
        size_change = abs(float(torch.linalg.norm(cand).item()) - norm_w)
        ok, dist, _, reason = verify_weight_update_safety_ex(w, cand, radius, 10.0, 1.0)
        rows.append({
            "theta_deg": round(math.degrees(t), 1),
            "size_change": size_change,
            "distance": dist,
            "closed_form_distance": 2 * math.sin(t / 2) * norm_w,
            "weak_check_accepts": size_change <= radius,
            "gate_accepts": ok,
            "gate_reason": reason,
        })
    weak_wrong = [r for r in rows if r["weak_check_accepts"] and not r["gate_accepts"]]
    return {
        "baseline_norm": norm_w,
        "radius": radius,
        "max_size_change": max(r["size_change"] for r in rows),
        "max_closed_form_error": max(abs(r["distance"] - r["closed_form_distance"]) for r in rows),
        "weak_accepts": sum(r["weak_check_accepts"] for r in rows),
        "gate_accepts": sum(r["gate_accepts"] for r in rows),
        "cases": len(rows),
        "weak_accepts_beyond_radius": len(weak_wrong),
        "first_rejected_theta_deg": min(r["theta_deg"] for r in rows if not r["gate_accepts"]),
        "rows": rows,
    }


# --- E2: the Plasm cycle ------------------------------------------------------
def e2_plasm_cycles(device: torch.device = torch.device("cpu")) -> dict:
    plasm.select_compute_device = lambda: device
    runs = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        t0 = time.perf_counter()
        res = plasm.run_weft_plasm_cycle(generations=GENERATIONS, shm_name=f"weft_wp1_{os.getpid()}_{seed}")
        if device.type == "mps":
            torch.mps.synchronize()
        elapsed = (time.perf_counter() - t0) * 1000
        gens = res["generations"]
        committed = []
        for g in gens:
            took = g["invariant_safe"] and g["watermark_retained"] and g["winner_target_error"] <= g["parent_target_error"] and g["tension"] <= TENSION_MAX
            committed.append(bool(took))
        runs.append({
            "seed": seed,
            "status": res["status"],
            "initial_error": res["initial_target_error"],
            "final_error": res["final_target_error"],
            "error_by_generation": [g["winner_target_error"] for g in gens],
            "drift_by_generation": [g["frobenius_drift"] for g in gens],
            "tension_by_generation": [g["tension"] for g in gens],
            "winners": [g["winner"] for g in gens],
            "commits": sum(committed),
            "max_core_row_drift": max(g["core_row_drift"] for g in gens),
            "min_watermark_alignment": min(g["watermark_alignment"] for g in gens),
            "max_watermark_response_drift": max(g["watermark_l2_drift"] for g in gens),
            "final_budget": gens[-1]["remaining_budget"],
            "elapsed_ms": elapsed,
            "final_weights_sha256": res["final_weights_sha256"],
        })
    errs = [r["final_error"] / r["initial_error"] for r in runs]
    winners = [w for r in runs for w in r["winners"]]
    return {
        "seeds": SEEDS,
        "generations": GENERATIONS,
        "arena_bytes": plasm.ARENA_BYTE_SIZE,
        "core_rows_frozen": DIM // 4,
        "r_invariant": R_INVARIANT,
        "tension_max": TENSION_MAX,
        "drift_cap_from_tension": (TENSION_MAX - 20.0) / 2.5,
        "all_pass": all(r["status"] == "PASS" for r in runs),
        "error_ratio_mean": sum(errs) / len(errs),
        "error_ratio_min": min(errs),
        "error_ratio_max": max(errs),
        "max_core_row_drift": max(r["max_core_row_drift"] for r in runs),
        "min_watermark_alignment": min(r["min_watermark_alignment"] for r in runs),
        "max_watermark_response_drift": max(r["max_watermark_response_drift"] for r in runs),
        "max_drift": max(max(r["drift_by_generation"]) for r in runs),
        "commits_total": sum(r["commits"] for r in runs),
        "proposals_total": len(runs) * GENERATIONS,
        "alpha_wins": winners.count("ALPHA"),
        "beta_wins": winners.count("BETA"),
        "elapsed_ms_median": sorted(r["elapsed_ms"] for r in runs)[len(runs) // 2],
        "runs": runs,
    }


# --- E5: the gate inside the loop --------------------------------------------
def e5_radius_sweep(device: torch.device = torch.device("cpu")) -> dict:
    """Run the same cycle with smaller radii so the gate actually binds.

    run_weft_plasm_cycle reads the module-level R_INVARIANT at call time, so the
    sweep sets it for each run and restores it afterwards.
    """
    plasm.select_compute_device = lambda: device
    original = plasm.R_INVARIANT
    rows = []
    try:
        for r in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, R_INVARIANT]:
            plasm.R_INVARIANT = r
            commits, ratios, reported, max_dist, reasons = [], [], [], [], {}
            for seed in SEEDS:
                torch.manual_seed(seed)
                res = plasm.run_weft_plasm_cycle(generations=GENERATIONS, shm_name=f"weft_wp1r_{os.getpid()}_{seed}")
                gens = res["generations"]
                committed_drifts = [g["frobenius_drift"] for g in gens if g["invariant_safe"]]
                commits.append(len(committed_drifts))
                # Error of the weights actually held after the last generation.
                last = gens[-1]
                held = last["winner_target_error"] if last["invariant_safe"] else last["parent_target_error"]
                # Since the #63 fix the library reports the held error itself.
                if res["final_target_error"] != held:
                    raise AssertionError(f"library final_target_error {res['final_target_error']} != held {held}")
                ratios.append(held / res["initial_target_error"])
                # What the library reported before the #63 fix: the last *candidate's*
                # error, committed or not. Kept so §5.4's measurement of the defect
                # still reproduces.
                reported.append(last["winner_target_error"] / res["initial_target_error"])
                max_dist.append(max(committed_drifts) if committed_drifts else 0.0)
                for g in gens:
                    reasons[g["gate_reason"]] = reasons.get(g["gate_reason"], 0) + 1
            rows.append({
                "radius": r,
                "commits_mean": sum(commits) / len(commits),
                "error_ratio_mean": sum(ratios) / len(ratios),
                "library_reported_error_ratio_mean": sum(reported) / len(reported),
                "max_committed_distance": max(max_dist),
                "gate_reasons": reasons,
            })
    finally:
        plasm.R_INVARIANT = original
    return {"generations": GENERATIONS, "seeds": len(SEEDS), "rows": rows}


# --- E3: watermark threat model ----------------------------------------------
def e3_watermark(device: torch.device = torch.device("cpu")) -> dict:
    torch.manual_seed(11)
    g = torch.Generator(device="cpu").manual_seed(11)
    w0 = (torch.randn(DIM, DIM, generator=g, dtype=torch.float32) * 0.05).to(device)
    core = DIM // 4
    wm, trig, target, init_align = plasm.embed_weight_watermark(w0, core_rows=core)
    base = wm.clone()
    noise = torch.randn(DIM, DIM, generator=g, dtype=torch.float32).to(device)
    noise = noise / torch.linalg.norm(noise)
    periphery = torch.ones(DIM, DIM, device=device)
    periphery[:core, :] = 0.0
    sweep = []
    for scale in [0.0, 0.5, 1, 2, 4, 6, 8, 12, 16, 24, 32]:
        row = {"scale": scale}
        for name, m in (("masked", periphery), ("unmasked", torch.ones(DIM, DIM, device=device))):
            cand = base + scale * (m * noise) / max(float(torch.linalg.norm(m * noise).item()), 1e-12)
            r = plasm.verify_watermark_retention(base, cand, trig, target)
            row[name] = {"retained": r["retained"], "cosine": r["cosine_alignment"], "response_drift": r["response_l2_drift"], "reason": r["reason"]}
        sweep.append(row)
    # Threat 1: targeted rank-1 overwrite of the trigger response.
    adv = torch.randn(DIM, generator=g, dtype=torch.float32).to(device)
    adv = adv / torch.linalg.norm(adv) * 3.0
    resp = torch.mv(base.t(), trig)
    overwritten = base + torch.outer(trig, adv - resp)
    over = plasm.verify_watermark_retention(base, overwritten, trig, target)
    gate = verify_weight_update_safety_ex(base, overwritten, R_INVARIANT, 100.0, 2.5)
    first_unmasked_fail = next((r["scale"] for r in sweep if not r["unmasked"]["retained"]), None)
    return {
        "initial_alignment": init_align,
        "masked_all_retained": all(r["masked"]["retained"] for r in sweep),
        "masked_max_response_drift": max(r["masked"]["response_drift"] for r in sweep),
        "first_unmasked_failure_scale": first_unmasked_fail,
        "rank1_overwrite": {"detected": not over["retained"], "cosine": over["cosine_alignment"], "reason": over["reason"],
                            "distance": gate[1], "gate_accepts_at_R_invariant": gate[0]},
        "sweep": sweep,
    }


# --- E4: cross-language conformance -----------------------------------------
def e4_conformance(device: torch.device = torch.device("cpu")) -> dict:
    v = load_conformance_vectors()
    agree = 0
    for vec in v["weight_update_vectors"]:
        dec = lambda x: float(x) if isinstance(x, str) else x  # noqa: E731
        if device.type == "mps":
            b = torch.tensor([dec(x) for x in vec["baseline"]], dtype=torch.float32, device=device)
            c = torch.tensor([dec(x) for x in vec["candidate"]], dtype=torch.float32, device=device)
            ok, dist, rem, reason = verify_weight_update_safety_ex(
                b, c, vec["r_invariant"], vec["budget"], vec["cost"], vec.get("locked_mask")
            )
        else:
            ok, dist, rem, reason = verify_weight_update_safety_ex(
                [dec(x) for x in vec["baseline"]], [dec(x) for x in vec["candidate"]],
                vec["r_invariant"], vec["budget"], vec["cost"], vec.get("locked_mask")
            )
        agree += ok == vec["expected_accepted"] and reason == vec["expected_reason"]
    return {"weight_update_vectors": len(v["weight_update_vectors"]), "python_agrees": agree,
            "tension_vectors": len(v["tension_vectors"]), "royalty_vectors": len(v["royalty_vectors"]),
            "implementations": ["Python (invariants.py)", "C11 (weft_invariants.h)", "JavaScript (site/assets/js/invariant-gate.js)"]}


# --- Figures -----------------------------------------------------------------
def figures(e1: dict, e2: dict, e3: dict, e5: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid = "#0a1a3d", "#586780", "#e4e9f0"
    cyan, violet, red = "#163168", "#b8862b", "#6b7a94"  # navy, gold, slate (names kept for diff size)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": muted, "axes.labelcolor": ink,
        "xtick.color": muted, "ytick.color": muted, "axes.grid": True, "grid.color": grid, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "path", "figure.dpi": 100,
        "svg.hashsalt": "weft-paper-1",
    })

    # Figure 1
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    th = [r["theta_deg"] for r in e1["rows"]]
    ax.plot(th, [r["distance"] for r in e1["rows"]], color=cyan, lw=2, label="distance from baseline ‖W′ − W₀‖")
    ax.plot(th, [r["size_change"] for r in e1["rows"]], color=violet, lw=2, ls="--", label="size change |‖W′‖ − ‖W₀‖|")
    ax.axhline(e1["radius"], color=red, lw=1, ls=":", label=f"radius R = {e1['radius']:.2f}")
    ax.set_xlabel("angle θ of the norm-preserving move (degrees)")
    ax.set_ylabel("Frobenius norm")
    ax.set_xlim(0, 180)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig1-compared-sizes.svg", metadata={"Date": None})
    plt.close(fig)

    # Figure 2
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
    gens = list(range(1, e2["generations"] + 1))
    for r in e2["runs"]:
        a1.plot(gens, [e / r["initial_error"] for e in r["error_by_generation"]], color=cyan, alpha=0.35, lw=1)
        a2.plot(gens, r["drift_by_generation"], color=violet, alpha=0.35, lw=1)
    a1.set_xlabel("generation"); a1.set_ylabel("target error / initial")
    a1.set_ylim(0, 1.05)
    a2.axhline(e2["drift_cap_from_tension"], color=red, lw=1, ls=":", label=f"tension cap ({e2['drift_cap_from_tension']:.0f})")
    a2.set_xlabel("generation"); a2.set_ylabel("‖W − W₀‖ (candidate)")
    a2.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig2-plasm-cycles.svg", metadata={"Date": None})
    plt.close(fig)

    # Figure 3
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.8))
    sc = [r["scale"] for r in e3["sweep"]]
    for key, color, label in (("masked", cyan, "core frozen"), ("unmasked", violet, "no mask")):
        a1.plot(sc, [r[key]["cosine"] for r in e3["sweep"]], color=color, lw=2, marker="o", ms=3, label=label)
        a2.plot(sc, [r[key]["response_drift"] for r in e3["sweep"]], color=color, lw=2, marker="o", ms=3, label=label)
    a1.axhline(0.85, color=red, lw=1, ls=":", label="threshold")
    a2.axhline(0.35, color=red, lw=1, ls=":", label="threshold")
    a1.set_xlabel("perturbation size ‖ΔW‖"); a1.set_ylabel("cosine alignment")
    a1.set_ylim(0.6, 1.02)
    a2.set_xlabel("perturbation size ‖ΔW‖"); a2.set_ylabel("trigger-response drift")
    a1.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig3-watermark.svg", metadata={"Date": None})
    plt.close(fig)

    # Figure 4
    fig, a1 = plt.subplots(figsize=(6.2, 2.8))
    rows = [r for r in e5["rows"] if r["radius"] < 100]
    xs = [r["radius"] for r in rows]
    a1.plot(xs, [r["error_ratio_mean"] for r in rows], color=cyan, lw=2, marker="o", ms=3, label="final error / initial")
    a1.set_xlabel("radius R")
    a1.set_ylabel("final error / initial", color=cyan)
    a1.set_ylim(0, 1.05)
    a2 = a1.twinx()
    a2.plot(xs, [r["commits_mean"] for r in rows], color=violet, lw=2, ls="--", marker="s", ms=3, label="committed updates (of 12)")
    a2.set_ylabel("committed updates", color=violet)
    a2.set_ylim(0, 12.5)
    a2.grid(False)
    a2.spines["right"].set_visible(True)
    lines = a1.get_lines() + a2.get_lines()
    a1.legend(lines, [l.get_label() for l in lines], frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig4-radius-sweep.svg", metadata={"Date": None})
    plt.close(fig)


VOLATILE = {"environment", "elapsed_ms", "elapsed_ms_median", "final_weights_sha256"}


def compare(a, b, path="") -> list[str]:
    """Differences between recomputed and committed results, ignoring timing and environment.

    Floats may differ in the last digits across CPUs, so numbers are compared with a tolerance.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k in VOLATILE:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present on one side only")
            else:
                out += compare(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in compare(x, y, f"{path}[{i}]")]
    if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return [] if a == b else [f"{path}: {a!r} != {b!r}"]
    if math.isclose(a, b, rel_tol=1e-4, abs_tol=1e-5):
        return []
    return [f"{path}: {a} != {b}"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Experiments for Paper 1, 'Models as cells'.")
    parser.add_argument("--check", action="store_true", help="CI: recompute, compare against baseline, write nothing")
    parser.add_argument("--check-mps", action="store_true", help="Recompute on MPS, compare against results-mps-m1.json, write nothing")
    parser.add_argument("--device", choices=["cpu", "mps"], default="cpu", help="Compute device (default: cpu)")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path (default: results.json for cpu, results-mps-m1.json for mps)")
    parser.add_argument("--figures", action="store_true", help="Force generating SVG figures")
    args = parser.parse_args()

    if args.check_mps:
        args.device = "mps"
        args.check = True

    if args.device == "mps" and not (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()):
        sys.exit("Error: PyTorch MPS backend is not available on this machine.")

    device = torch.device(args.device)
    target_out = args.out or (HERE / ("results-mps-m1.json" if args.device == "mps" else "results.json"))

    e1 = e1_compared_sizes(device)
    e2 = e2_plasm_cycles(device)
    e3 = e3_watermark(device)
    e4 = e4_conformance(device)
    e5 = e5_radius_sweep(device)

    if not args.check and (args.figures or (args.device == "cpu" and args.out is None)):
        figures(e1, e2, e3, e5)

    out = {
        "schema": "weft-paper-1-results/1",
        "environment": probe_environment(args.device),
        "e1_compared_sizes": e1,
        "e2_plasm_cycles": e2,
        "e3_watermark": e3,
        "e4_conformance": e4,
        "e5_radius_sweep": e5,
    }

    if args.check:
        if not target_out.exists():
            sys.exit(f"Baseline file {target_out} not found")
        committed = json.loads(target_out.read_text(encoding="utf-8"))
        diffs = compare(json.loads(json.dumps(out)), committed)
        for d in diffs[:50]:
            print(f"DIFF {d}", file=sys.stderr)
        print(json.dumps({"status": "FAIL" if diffs else "PASS", "differences": len(diffs)}))
        raise SystemExit(1 if diffs else 0)

    target_out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    summary = {
        "device": args.device,
        "out": str(target_out),
        "E1": {k: e1[k] for k in ("cases", "weak_accepts", "gate_accepts", "weak_accepts_beyond_radius", "max_size_change", "first_rejected_theta_deg")},
        "E2": {k: e2[k] for k in ("all_pass", "error_ratio_mean", "error_ratio_min", "error_ratio_max", "max_core_row_drift", "min_watermark_alignment", "max_drift", "commits_total", "proposals_total", "alpha_wins", "beta_wins", "elapsed_ms_median")},
        "E3": {k: e3[k] for k in ("masked_all_retained", "masked_max_response_drift", "first_unmasked_failure_scale", "rank1_overwrite")},
        "E4": e4,
        "E5": [{k: r[k] for k in ("radius", "commits_mean", "error_ratio_mean", "library_reported_error_ratio_mean", "max_committed_distance")} for r in e5["rows"]],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
