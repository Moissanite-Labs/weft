#!/usr/bin/env python3
"""
Independent Clean-Room Verifier for Paper 3 / Experiment E15
(`papers/03-certified-morphogenesis/verify_e15.py`)
Imports nothing from `weft/` or `scripts/`; checks canonical SHA-256, exact aggregate
counts across all 12 seeds, zero frozen-core drift, rational budget non-negativity,
and boundary audit invariants. Fails closed (exit 1) on any tamper.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict


def verify_e15_dict(rep: Dict[str, Any]) -> bool:
    body = {k: v for k, v in rep.items() if k != "certificate_sha256"}
    got_sha = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if got_sha != rep.get("certificate_sha256"):
        return False
    if int(rep.get("n_seeds", 0)) != 12 or len(rep.get("per_seed_records", [])) != 12:
        return False

    sm = rep.get("summary_by_regime", {})
    m3 = sm.get("M3_full_dual_morphogenesis", {})
    if int(m3.get("passes_of_12", -1)) != 12:
        return False
    if int(m3.get("total_poison_committed_of_120", -1)) != 0:
        return False
    if int(m3.get("total_poison_vetoed_of_120", -1)) != 120:
        return False
    if float(m3.get("max_core_drift", 1.0)) != 0.0:
        return False

    # Cross-check per-seed records against summary totals!
    re_passes_m3 = 0
    re_vetoes_m3 = 0
    for srec in rep["per_seed_records"]:
        r3 = srec["regimes"]["M3_full_dual_morphogenesis"]
        if r3["core_drift"] != 0.0 or r3["final_dim"] != 24:
            return False
        if not r3["dual_certificate_passed"] or Fraction(r3["remaining_budget_q"]) < 0 or Fraction(r3["partitioned_drift_q"]) > Fraction(3, 4):
            return False
        if r3["passed_joint_gate"]:
            re_passes_m3 += 1
        re_vetoes_m3 += int(r3["poison_vetoed"])

    if re_passes_m3 != int(m3["passes_of_12"]) or re_vetoes_m3 != int(m3["total_poison_vetoed_of_120"]):
        return False

    # Verify boundary audit honesty flags
    ba = rep.get("boundary_audits", {}).get("unprobed_subspace_audit", {})
    if int(ba.get("unobserved_nullity_dim", 0)) <= 0 or ba.get("mpdi_detects_unprobed_nullspace") is not False:
        return False

    return True


def main() -> int:
    p = Path(__file__).resolve().parent / "e15_certificate.json"
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
    rep = json.loads(p.read_text(encoding="utf-8"))
    if not verify_e15_dict(rep):
        print("FAIL: E15 certificate verification failed", file=sys.stderr)
        return 1
    print(f"OK: E15 certificate verified ({rep['certificate_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
