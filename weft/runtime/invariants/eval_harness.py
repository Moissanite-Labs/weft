#!/usr/bin/env python3
"""Fixed evaluation harness for the weight-update safety gate (#223).

Runs the gate from `invariants.py` over the shared conformance vectors
under varied bounds and budgets, and runs one adaptive sequence where each
accepted update moves the baseline and spends budget. Records accept or
reject, distance to baseline, and cost for every run.

Run from the repository root:

    python3 weft/runtime/invariants/eval_harness.py            # write eval_results.json
    python3 weft/runtime/invariants/eval_harness.py --check    # CI: recompute, compare, write nothing

Standard library only. No torch, no network. The seed, the radius factors,
the budgets, and the sequence deltas are fixed here, so a fresh run on a
clean clone reproduces the committed table. Cross-implementation agreement
(Python, C11, JavaScript) stays with `test_invariants.py`; this harness
checks the gate's behaviour under varied bounds and budgets, not the ports.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from weft.runtime.invariants import (  # noqa: E402
    R_INVARIANT,
    load_conformance_vectors,
    verify_weight_update_safety_ex,
)

SCHEMA = "weft-invariant-gate-eval/1"
SEED = 7
RADIUS_FACTORS = (0.5, 1.0, 2.0)
BUDGETS = (5.0, 10.0, 25.0)
SEQ_STEPS = 12
SEQ_START_BUDGET = 10.0
SEQ_COST = 1.0
SEQ_RADIUS = R_INVARIANT
SEQ_BASELINE = (1.0, 2.0, 3.0, 4.0)
SEQ_DELTA_RANGE = 80.0
RESULTS_PATH = HERE / "eval_results.json"


def decode(value):
    """Shared vectors encode non-finite numbers as strings ("NaN", "Inf")."""
    return float(value) if isinstance(value, str) else value


def encode(value):
    """Keep the results file strict JSON: non-finite floats become strings."""
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else "Inf"
    return value


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def probe_environment() -> dict:
    return {
        "commit": git_commit(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "system": platform.system(),
    }


def run_grid(vectors):
    """Every weight-update vector under each radius factor and budget."""
    rows = []
    for vec in vectors["weight_update_vectors"]:
        baseline = [decode(x) for x in vec["baseline"]]
        candidate = [decode(x) for x in vec["candidate"]]
        cost = decode(vec["cost"])
        for factor in RADIUS_FACTORS:
            radius = decode(vec["r_invariant"]) * factor
            for budget in BUDGETS:
                accepted, dist, remaining, reason = verify_weight_update_safety_ex(
                    baseline, candidate, radius, budget, cost, vec.get("locked_mask")
                )
                rows.append({
                    "vector": vec["name"],
                    "radius_factor": factor,
                    "radius": encode(radius),
                    "budget": budget,
                    "accepted": accepted,
                    "reason": reason,
                    "distance": encode(dist),
                    "cost": encode(cost),
                    "remaining_budget": encode(remaining),
                })
    return rows


def run_sequence():
    """One adaptive run: accepts move the baseline and spend budget.

    The deltas come from a fixed seed, so the run is the same on every
    machine. A reject leaves the baseline and the budget untouched.
    """
    rng = random.Random(SEED)
    baseline = list(SEQ_BASELINE)
    budget = SEQ_START_BUDGET
    rows = []
    for step in range(1, SEQ_STEPS + 1):
        delta = [rng.uniform(-SEQ_DELTA_RANGE, SEQ_DELTA_RANGE) for _ in baseline]
        candidate = [b + d for b, d in zip(baseline, delta)]
        accepted, dist, remaining, reason = verify_weight_update_safety_ex(
            baseline, candidate, SEQ_RADIUS, budget, SEQ_COST
        )
        rows.append({
            "step": step,
            "delta": [round(d, 6) for d in delta],
            "accepted": accepted,
            "reason": reason,
            "distance": encode(dist),
            "cost": SEQ_COST,
            "remaining_budget": encode(remaining),
        })
        if accepted:
            baseline = candidate
            budget = remaining
    return rows


def summarize(rows):
    reasons = {}
    for row in rows:
        reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
    return {
        "runs": len(rows),
        "accepts": sum(1 for r in rows if r["accepted"]),
        "rejects": sum(1 for r in rows if not r["accepted"]),
        "reasons": dict(sorted(reasons.items())),
    }


def run_eval():
    vectors = load_conformance_vectors()
    grid = run_grid(vectors)
    sequence = run_sequence()
    return {
        "schema": SCHEMA,
        "environment": probe_environment(),
        "config": {
            "seed": SEED,
            "radius_factors": list(RADIUS_FACTORS),
            "budgets": list(BUDGETS),
            "sequence_steps": SEQ_STEPS,
            "sequence_start_budget": SEQ_START_BUDGET,
            "sequence_cost": SEQ_COST,
            "sequence_radius": SEQ_RADIUS,
            "sequence_baseline": list(SEQ_BASELINE),
            "sequence_delta_range": SEQ_DELTA_RANGE,
            "weight_update_vectors": len(vectors["weight_update_vectors"]),
        },
        "grid": grid,
        "sequence": sequence,
        "summary": {
            "grid": summarize(grid),
            "sequence": summarize(sequence),
        },
    }


VOLATILE = {"environment"}


def compare(a, b, path=""):
    """Differences between recomputed and committed results.

    Floats may differ in the last digits across machines, so numbers are
    compared with a tolerance. Non-finite values are stored as the strings
    "NaN" and "Inf" and compared exactly.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            if key in VOLATILE:
                continue
            if key not in a or key not in b:
                out.append(f"{path}/{key}: present on one side only")
            else:
                out += compare(a[key], b[key], f"{path}/{key}")
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
    parser = argparse.ArgumentParser(description="Fixed evaluation harness for the weight-update safety gate.")
    parser.add_argument("--check", action="store_true", help="Recompute, compare against the committed table, write nothing")
    parser.add_argument("--table", type=Path, default=RESULTS_PATH, help="Results table path (default: eval_results.json)")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path (default: --table)")
    args = parser.parse_args()

    result = run_eval()

    if args.check:
        if not args.table.exists():
            sys.exit(f"Baseline file {args.table} not found")
        committed = json.loads(args.table.read_text(encoding="utf-8"))
        diffs = compare(json.loads(json.dumps(result)), committed)
        for d in diffs[:50]:
            print(f"DIFF {d}", file=sys.stderr)
        print(json.dumps({"status": "FAIL" if diffs else "PASS", "differences": len(diffs)}))
        raise SystemExit(1 if diffs else 0)

    out = args.out or args.table
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(out),
        "grid": result["summary"]["grid"],
        "sequence": result["summary"]["sequence"],
    }, indent=2))


if __name__ == "__main__":
    main()
