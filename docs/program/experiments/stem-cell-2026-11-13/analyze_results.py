#!/usr/bin/env python3
"""Descriptive extraction only; does not select candidates or invoke a model."""
import argparse
import json
from pathlib import Path


def analyze(root):
    results = json.loads((root / "results.json").read_text())
    rows = results["results"]
    comparisons = []
    for seed in results["config"]["seeds"]:
        for branch in results["config"]["branches"]:
            matched = {r["controller"]: r for r in rows if r["seed"] == seed and r["selected_for_demand"] == branch and r["evaluated_demand"] == branch}
            costs = {label: record["test"]["total_cost"] for label, record in matched.items()}
            comparisons.append({"seed": seed, "demand": branch, "heldout_costs": costs,
                                "teacher_improvement_over_root_percent": 100 * (costs["root_stem"] - costs["teacher_final"]) / costs["root_stem"],
                                "teacher_genome": matched["teacher_final"]["genome"]})
    selections = [json.loads(p.read_text()) for p in sorted((root / "selections").glob("*.json"))]
    responses = [json.loads(p.read_text()) for p in sorted((root / "requests").glob("*.response.json"))]
    usage = {"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0, "reasoning_output_tokens": 0}
    for record in responses:
        item = record.get("response", {}).get("usage") or {}
        usage["input_tokens"] += item.get("input_tokens", 0)
        usage["output_tokens"] += item.get("output_tokens", 0)
        usage["cached_input_tokens"] += (item.get("input_tokens_details") or {}).get("cached_tokens", 0)
        usage["reasoning_output_tokens"] += (item.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
    proof_dirs = [root / name for name in ("proofs", "control_proofs", "lifecycle_proofs", "heldout_proofs", "colony_proofs", "allocation_proofs")]
    proofs = []
    for directory in proof_dirs:
        proofs += [json.loads(p.read_text()) for p in directory.rglob("verification.json")]
    teacher_children = [child for selection in selections for child in selection["children"]]
    return {
        "scope": "Descriptive two-seed pilot; fixed demand within each lineage; no population inference, demand-reversal recovery, throughput or GPU gain established.",
        "comparisons": comparisons,
        "crossover_teacher_costs": [{"seed": r["seed"], "selected_for": r["selected_for_demand"], "evaluated_on": r["evaluated_demand"], "cost": r["test"]["total_cost"]} for r in rows if r["controller"] == "teacher_final"],
        "opportunities": len(selections),
        "returned_teacher_children": len(teacher_children),
        "eligible_teacher_children": sum(bool(c.get("eligible")) for c in teacher_children),
        "duplicate_teacher_children": sum(c.get("duplicate_of") is not None for c in teacher_children),
        "selections_changed": sum(r["selected_index"] is not None for r in selections),
        "selection_history": [{"seed": r["seed"], "branch": r["branch"], "generation": r["generation"], "selected_index": r["selected_index"], "parent_cost": r["unchanged_parent"]["validation"]["total_cost"], "selected_cost": r["selected_validation"]["total_cost"], "genome": r["selected_genome"]} for r in selections],
        "colonies": [{"seed": c["seed"], "copy_counts": c["allocation"]["copy_counts"], "total_cells": len(c["allocation"]["cells"]), "root_preserved": c["allocation"]["cells"][0]["genome"] == results["config"]["root_stem"]} for c in results["colonies"]],
        "api_responses": len(responses), "usage": usage,
        "proof_records": len(proofs), "accepted_proofs": sum(p.get("accepted") is True for p in proofs),
        "proofs_with_empty_axioms": sum(p.get("axioms") == [] for p in proofs),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("data"))
    args = parser.parse_args()
    result = analyze(args.out)
    (args.out / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
