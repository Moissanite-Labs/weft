#!/usr/bin/env python3
"""
Syntactic Weft // Master Self-Test & Corpus Integrity Suite
Exercises:
  1. Stratified Apple Silicon Unified Memory Plasm (POSIX shm + PyTorch MPS)
  2. Lafont Interaction Combinator VM (CON/DUP/ERA reduction + cryptographic trace)
  3. Aywa WebGPU & Moissanite-Labs 19-Repository Telemetry Bridge
  4. Full 53-file Markdown Corpus + 4 Browser Transcripts + 5 Sandbox Widgets Audit
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WEFT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "aywa")))

import torch

from weft_plasm import R_INVARIANT, run_plasm_cycle, verify_weight_update_safety, weight_frobenius_size
from weft_ic_vm import run_ic_verification
from weft_daemon import read_darwin_hardware_metrics
from github_harvester import harvest_moissanite_telemetry

def run_weight_safety_checks():
    """Observable safety invariants for baseline-distance and metabolic budget."""
    cases = []

    # 1) Matching Frobenius sizes after a large move: compared-sizes is 0, baseline distance is 200.
    baseline = torch.tensor([100.0, 0.0])
    current = torch.tensor([-100.0, 0.0])
    candidate = current.clone()
    compared = abs(weight_frobenius_size(candidate) - weight_frobenius_size(current))
    baseline_distance = float(torch.norm(candidate - baseline).item())
    trap = verify_weight_update_safety(
        baseline, current, candidate, remaining_budget=50.0, update_cost=1.0, max_baseline_distance=500.0
    )
    compared_sizes_would_pass = compared == 0.0
    cases.append({
        "name": "baseline_distance_with_matching_sizes",
        "compared_sizes": compared,
        "baseline_distance": baseline_distance,
        "compared_sizes_trap_would_hide_move": compared_sizes_would_pass and baseline_distance == 200.0,
        "uses_baseline_distance_not_compared_sizes": trap["baseline_distance"] == 200.0 and trap["compared_sizes"] == 0.0,
        "status": "PASS"
        if (compared_sizes_would_pass and baseline_distance == 200.0 and trap["baseline_distance"] == 200.0)
        else "FAIL",
    })

    # 2) Reject not-a-number weight state.
    nan_candidate = torch.tensor([float("nan"), 1.0])
    nan_res = verify_weight_update_safety(
        baseline, current, nan_candidate, remaining_budget=10.0, update_cost=1.0
    )
    cases.append({
        "name": "reject_nan_candidate",
        "accepted": nan_res["accepted"],
        "status": "PASS" if not nan_res["accepted"] else "FAIL",
    })

    # 3) Remaining budget 1 must not accept an update costing 2.5 (no success with budget -1.5).
    underflow = verify_weight_update_safety(
        baseline, current, candidate, remaining_budget=1.0, update_cost=2.5, max_baseline_distance=500.0
    )
    cases.append({
        "name": "reject_negative_remaining_budget",
        "accepted": underflow["accepted"],
        "remaining_budget": underflow.get("remaining_budget"),
        "status": "PASS"
        if (not underflow["accepted"] and underflow.get("remaining_budget") == -1.5)
        else "FAIL",
    })

    # 4) Budget must be finite and positive before any update is accepted.
    exhausted = verify_weight_update_safety(
        baseline, current, candidate, remaining_budget=0.0, update_cost=0.5, max_baseline_distance=500.0
    )
    nonfinite = verify_weight_update_safety(
        baseline, current, candidate, remaining_budget=float("inf"), update_cost=0.5, max_baseline_distance=500.0
    )
    precondition_ok = not exhausted["accepted"] and not nonfinite["accepted"]
    cases.append({
        "name": "remaining_budget_precondition",
        "exhausted_accepted": exhausted["accepted"],
        "nonfinite_accepted": nonfinite["accepted"],
        "status": "PASS" if precondition_ok else "FAIL",
    })

    # Guardrail: within R_INVARIANT, legitimate updates still dispatch.
    small_step = torch.tensor([95.0, 10.0])
    within = verify_weight_update_safety(
        baseline, baseline, small_step, remaining_budget=25.0, update_cost=2.0, max_baseline_distance=R_INVARIANT
    )
    cases.append({
        "name": "accept_invariant_safe_update",
        "accepted": within["accepted"],
        "status": "PASS" if within["accepted"] else "FAIL",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in cases) else "FAIL"
    return {"status": status, "cases": cases}


def run_pages_seed_selftest():
    aywa_dir = os.path.abspath(os.path.join(HERE, "..", "aywa"))
    module_path = os.path.join(aywa_dir, "site_selftest.py")
    if not os.path.isfile(module_path):
        return {"status": "FAIL", "error": f"missing site selftest module: {module_path}"}
    spec = importlib.util.spec_from_file_location("weft_site_selftest", module_path)
    if spec is None or spec.loader is None:
        return {"status": "FAIL", "error": "could not load site_selftest module spec"}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_site_selftest()


def main():
    safety_res = run_weight_safety_checks()
    plasm_res = run_plasm_cycle(cycles=3)
    ic_res = run_ic_verification()
    # Write harvester output to a throwaway directory so a test run never
    # rewrites tracked files (moissanite_telemetry.json/.bin, telemetry.jsonl).
    with tempfile.TemporaryDirectory(prefix="weft-selftest-") as scratch:
        moiss_res = harvest_moissanite_telemetry(scratch)
    hw_res = read_darwin_hardware_metrics()

    try:
        pages_res = run_pages_seed_selftest()
    except Exception as exc:
        pages_res = {"status": "FAIL", "error": str(exc)}

    overall = all(
        x == "PASS"
        for x in [
            safety_res["status"],
            plasm_res["status"],
            ic_res["status"],
            pages_res["status"],
        ]
    )
    summary = {
        "overall_status": "PASS" if overall else "FAIL",
        "weight_safety_checks": safety_res,
        "plasm_substrate": plasm_res,
        "interaction_combinator_vm": ic_res,
        "moissanite_telemetry": {
            "active_nodes": moiss_res["active_nodes"],
            "org_tension": moiss_res["org_tension"],
            "gini_index": moiss_res["gini_index"],
            "binary_frame_bytes": moiss_res["binary_frame_bytes"],
            "darwin_hardware": hw_res,
        },
        "corpus_audit": "moved to Moissanite-Labs/weft-corpus (scripts/check_corpus.py)",
        "pages_seed": pages_res,
    }
    print(json.dumps(summary, indent=2))
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
