#!/usr/bin/env python3
"""Native lineage selection. Preregistered before the run. No API calls.

Question
  The published plasm cycle always prefers alpha, because beta is a worse
  copy of the same residual. Paper 1 section 7 asks for two update rules
  whose ranking changes with the data. This run is that test.

Rules, fixed before looking at outcomes
  Two streams. Each has its own periphery target, one unit of Frobenius
  distance from the saved baseline, core rows identical to the baseline.
  Alpha steps along stream 0's residual. Beta steps along stream 1's residual.
  The step is scaled to Frobenius length eta after the core rows are zeroed.
  Gaussian noise at 5 percent of the gradient is added before that scaling.
  The winner is the lower error on the scored stream. Ties go to alpha.
  Novelty weight is 0.
  A commit requires the live Python gate
  (weft/runtime/invariants/invariants.py verify_weight_update_safety_ex)
  and a winner error no higher than the parent. The loser is not offered
  to the gate. That matches plasm.py. There is no watermark and no
  shared-memory arena in this run.

Predictions
  P1. Single stream 0 or 1, eta 0.25, R 120, 8 generations, 10 seeds:
      the chosen lineage matches the scored stream on at least 80 percent
      of generations, and the mean held-error ratio ends below 0.5.
  P2. Same, R 0.20: zero commits, held-error ratio stays 1.
      One step is longer than the radius.
  P3. Switch from stream 0 to stream 1 at generation 5, eta 0.25, R 120:
      held error falls inside phase A and again inside phase B.
  P4. Same switch, R 0.45: phase B commits fewer generations than phase A.
      The baseline anchor, not the last commit, is what the gate measures.

The process exits 1 if the match counts, the R 0.20 rejection, the phase
falls, or the phase-B commit contrast fail. The 0.5 error line in P1 is
recorded in predictions and is not an exit check.

Not claimed
  This is not the razi-cells harness, not the carbone operator spec, and
  not a closure of issue 111. The C11 header is not on this path.
"""

from __future__ import annotations

import importlib.util
import json
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = ROOT / "weft/runtime/invariants/invariants.py"
OUT_PATH = Path(__file__).resolve().parent / "results.json"

DIM = 256
CORE_ROWS = DIM // 4
N_ROWS = 32
SEEDS = [20261111 + i for i in range(10)]
GENS = 8
ETA = 0.25
SWITCH_AT = 5
STEP_COST = 2.5
BUDGET0 = 100.0
NOISE_FRAC = 0.05


def load_gate():
    spec = importlib.util.spec_from_file_location("weft_invariants_live", GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {GATE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify_weight_update_safety_ex


def unit_periphery(rng: np.random.Generator) -> np.ndarray:
    delta = rng.normal(size=(DIM, DIM))
    delta[:CORE_ROWS] = 0.0
    return delta / np.linalg.norm(delta)


def residual_grad(x: np.ndarray, w: np.ndarray, y: np.ndarray) -> np.ndarray:
    resid = y - x @ w
    return (x.T @ resid) / float(x.shape[0])


def scaled_step(rng: np.random.Generator, grad: np.ndarray) -> np.ndarray:
    noisy = grad + rng.normal(scale=NOISE_FRAC, size=grad.shape) * (
        np.linalg.norm(grad) + 1e-12
    )
    noisy[:CORE_ROWS] = 0.0
    norm = np.linalg.norm(noisy)
    if norm < 1e-15:
        return np.zeros_like(grad)
    return noisy * (ETA / norm)


def run_seed(gate, seed: int, scored_fn, radius: float) -> dict:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(N_ROWS, DIM)) * 0.25
    w0 = rng.normal(size=(DIM, DIM)) * 0.02
    d0 = unit_periphery(rng)
    d1 = unit_periphery(rng)
    y0 = x @ (w0 + d0)
    y1 = x @ (w0 + d1)
    targets = (y0, y1)

    w = w0.copy()
    budget = BUDGET0
    held_dist = 0.0
    rows = []
    for gen in range(1, GENS + 1):
        stream = scored_fn(gen)
        y = targets[stream]
        parent = float(np.linalg.norm(x @ w - y))
        g0 = residual_grad(x, w, y0)
        g1 = residual_grad(x, w, y1)
        cand = (
            w + scaled_step(rng, g0),
            w + scaled_step(rng, g1),
        )
        err = [
            float(np.linalg.norm(x @ cand[0] - y)),
            float(np.linalg.norm(x @ cand[1] - y)),
        ]
        winner = 0 if err[0] <= err[1] else 1
        accepted, dist, remaining, reason = gate(
            w0, cand[winner], radius, budget, STEP_COST
        )
        core = float(np.linalg.norm(cand[winner][:CORE_ROWS] - w0[:CORE_ROWS]))
        commit = bool(accepted and err[winner] <= parent and core == 0.0)
        if commit:
            w = cand[winner]
            budget = float(remaining)
            held = err[winner]
            held_dist = float(np.linalg.norm(w - w0))
        else:
            held = parent
        rows.append(
            {
                "generation": gen,
                "stream": stream,
                "winner": winner,
                "match": winner == stream,
                "parent_error": parent,
                "err_alpha": err[0],
                "err_beta": err[1],
                "winner_error": err[winner],
                "held_error": held,
                "committed": commit,
                "distance": None if dist == float("inf") else dist,
                "held_distance": held_dist,
                "gate_reason": reason,
                "core_drift": core,
                "budget": budget,
            }
        )
    return {
        "seed": seed,
        "direction_dot": float(np.sum(d0 * d1)),
        "rows": rows,
    }


def summarize(runs: list[dict], label: str) -> dict:
    rows = [r for run in runs for r in run["rows"]]
    commits = [r for r in rows if r["committed"]]
    start = [run["rows"][0]["parent_error"] for run in runs]
    end = [run["rows"][-1]["held_error"] for run in runs]
    ratios = [e / s for s, e in zip(start, end)]
    dists = [r["distance"] for r in rows if r["distance"] is not None]
    gaps = [
        abs(r["err_alpha"] - r["err_beta"]) / r["parent_error"]
        for r in rows
        if r["parent_error"] > 0.0
    ]
    by_gen = []
    for gen in range(1, GENS + 1):
        group = [r for r in rows if r["generation"] == gen]
        by_gen.append(sum(1 for r in group if r["committed"]))
    return {
        "label": label,
        "generations": len(rows),
        "match_rate": sum(r["match"] for r in rows) / len(rows),
        "commits": len(commits),
        "commits_by_generation": by_gen,
        "mean_held_ratio": float(np.mean(ratios)),
        "max_held_ratio": float(np.max(ratios)),
        "min_held_ratio": float(np.min(ratios)),
        "mean_error_gap": float(np.mean(gaps)),
        "mean_direction_dot": float(np.mean([run["direction_dot"] for run in runs])),
        "max_distance": None if not dists else float(np.max(dists)),
        "gate_reasons": sorted({r["gate_reason"] for r in rows}),
    }


def phase_summary(runs: list[dict], label: str) -> dict:
    a_commits = 0
    b_commits = 0
    a_fall = 0
    b_fall = 0
    a_ratios = []
    b_ratios = []
    held_end_a = []
    for run in runs:
        rows = run["rows"]
        a = rows[: SWITCH_AT - 1]
        b = rows[SWITCH_AT - 1 :]
        a_commits += sum(r["committed"] for r in a)
        b_commits += sum(r["committed"] for r in b)
        a_fall += int(a[-1]["held_error"] < a[0]["parent_error"])
        b_fall += int(b[-1]["held_error"] < b[0]["parent_error"])
        a_ratios.append(a[-1]["held_error"] / a[0]["parent_error"])
        b_ratios.append(b[-1]["held_error"] / b[0]["parent_error"])
        held_end_a.append(a[-1]["held_distance"])
    return {
        "label": label,
        "phase_a_commits": a_commits,
        "phase_b_commits": b_commits,
        "phase_a_seeds_error_fell": a_fall,
        "phase_b_seeds_error_fell": b_fall,
        "seeds": len(runs),
        "mean_phase_a_ratio": float(np.mean(a_ratios)),
        "mean_phase_b_ratio": float(np.mean(b_ratios)),
        "mean_held_distance_end_a": float(np.mean(held_end_a)),
    }


def main() -> None:
    gate = load_gate()
    conditions = {
        "p1_stream0_r120": lambda g: 0,
        "p1_stream1_r120": lambda g: 1,
        "p2_stream0_r020": lambda g: 0,
        "p3_switch_r120": lambda g: 0 if g < SWITCH_AT else 1,
        "p4_switch_r045": lambda g: 0 if g < SWITCH_AT else 1,
    }
    radii = {
        "p1_stream0_r120": 120.0,
        "p1_stream1_r120": 120.0,
        "p2_stream0_r020": 0.20,
        "p3_switch_r120": 120.0,
        "p4_switch_r045": 0.45,
    }
    out_runs = {}
    summary = {}
    for name, scored in conditions.items():
        runs = [run_seed(gate, seed, scored, radii[name]) for seed in SEEDS]
        out_runs[name] = runs
        if name.startswith("p3") or name.startswith("p4"):
            summary[name] = phase_summary(runs, name)
            summary[name].update(summarize(runs, name))
        else:
            summary[name] = summarize(runs, name)

    p1 = summary["p1_stream0_r120"]
    p1b = summary["p1_stream1_r120"]
    p2 = summary["p2_stream0_r020"]
    p3 = summary["p3_switch_r120"]
    p4 = summary["p4_switch_r045"]
    verdict = {
        "p1_stream0_match": p1["match_rate"] >= 0.8,
        "p1_stream0_error_below_half": p1["mean_held_ratio"] < 0.5,
        "p1_stream1_match": p1b["match_rate"] >= 0.8,
        "p1_stream1_error_below_half": p1b["mean_held_ratio"] < 0.5,
        "p2_no_commit": p2["commits"] == 0 and abs(p2["mean_held_ratio"] - 1.0) < 1e-12,
        "p3_both_phases_fall": (
            p3["phase_a_seeds_error_fell"] == len(SEEDS)
            and p3["phase_b_seeds_error_fell"] == len(SEEDS)
        ),
        "p4_anchor_blocks_switch": p4["phase_b_commits"] < p4["phase_a_commits"],
    }
    payload = {
        "instrument": "numpy lineage loop calling the live Python gate",
        "gate": "weft/runtime/invariants/invariants.py:verify_weight_update_safety_ex",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "dim": DIM,
        "core_rows": CORE_ROWS,
        "rows": N_ROWS,
        "eta": ETA,
        "seeds": SEEDS,
        "generations": GENS,
        "switch_at": SWITCH_AT,
        "novelty": 0.0,
        "predictions": verdict,
        "summary": summary,
        "runs": out_runs,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"predictions": verdict, "summary": summary}, indent=2))
    required = [
        verdict["p1_stream0_match"],
        verdict["p1_stream1_match"],
        verdict["p2_no_commit"],
        verdict["p3_both_phases_fall"],
        verdict["p4_anchor_blocks_switch"],
    ]
    if not all(required):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
