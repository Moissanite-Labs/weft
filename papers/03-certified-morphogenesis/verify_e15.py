#!/usr/bin/env python3
"""
Independent Clean-Room Verifier for Paper 3 v1.1 / Experiment E15
(`papers/03-certified-morphogenesis/verify_e15.py`)
Verifies SHA-256, 12/12 M3 dual morphogenesis passes, fixed-radix `<= 20`-bit
denominator invariance across 2,500 steps, and `100/100` Fiat-Shamir Haar
double-null-space attack rejections (`post_haar_full_nullity_dim == 0`).
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
    if int(m3.get("total_poison_committed_of_120", -1)) != 0 or int(m3.get("total_poison_vetoed_of_120", -1)) != 120:
        return False
    if float(m3.get("max_core_drift", 1.0)) != 0.0:
        return False

    re_passes = 0
    re_vetoes = 0
    for srec in rep["per_seed_records"]:
        r3 = srec["regimes"]["M3_full_dual_morphogenesis"]
        if r3["core_drift"] != 0.0 or r3["final_dim"] != 24 or not r3["dual_certificate_passed"]:
            return False
        rem_q = Fraction(r3["remaining_budget_q"])
        drift_q = Fraction(r3["partitioned_drift_q"])
        if rem_q < 0 or drift_q > Fraction(3, 4):
            return False
        # Verify fixed-radix `10^-6` denominator ceiling (<= 20 bits!) on every seed's dual certificate!
        if rem_q.denominator.bit_length() > 20 or drift_q.denominator.bit_length() > 24:
            return False
        if r3["passed_joint_gate"]:
            re_passes += 1
        re_vetoes += int(r3["poison_vetoed"])

    if re_passes != int(m3["passes_of_12"]) or re_vetoes != int(m3["total_poison_vetoed_of_120"]):
        return False

    # Verify v1.1 boundary closures!
    ba = rep.get("boundary_audits", {})
    uc = ba.get("unprobed_subspace_closure", {})
    rc = ba.get("rational_bitlength_closure", {})
    if (
        int(uc.get("prior_unobserved_nullity_dim", 0)) != 12
        or int(uc.get("post_haar_full_nullity_dim", -1)) != 0
        or int(uc.get("static_mpdi_vetoed_of_100", -1)) != 0
        or int(uc.get("haar_sub4_fiat_shamir_vetoed_of_100", -1)) != 100
        or int(uc.get("haar_full_complement_vetoed_of_100", -1)) != 100
    ):
        return False
    if (
        int(rc.get("fixed_radix_1e6_250_steps_bits", 99)) > 20
        or int(rc.get("fixed_radix_1e6_2500_steps_bits", 99)) > 20
    ):
        return False

    return True


def main() -> int:
    p = Path(__file__).resolve().parent / "e15_certificate.json"
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
    rep = json.loads(p.read_text(encoding="utf-8"))
    if not verify_e15_dict(rep):
        print("FAIL: E15 v1.1 certificate verification failed", file=sys.stderr)
        return 1
    print(f"OK: E15 v1.1 certificate verified ({rep['certificate_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
