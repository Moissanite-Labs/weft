#!/usr/bin/env python3
"""
Self-consistency checker for the recorded dual morphogenesis benchmark run
(`papers/evidence/dual-morphogenesis/verify_certificate.py`).
Imports nothing from `weft/` or `scripts/`; pure standard library, any Python
3.10+. Checks the canonical SHA-256 over the file's own body, that the 12
per-seed rows add up to the summary, and that the recorded invariants hold
(zero frozen-core drift, poison accounting, budget non-negativity, drift cap,
boundary-audit accounting identities — including the v1.1 Haar probe refresh,
grinding and rational bit-length audits — and that `passed_joint_gate` follows
from the recorded fields). Exits 1 if any of these checks fail.

This is internal consistency of the JSON only. It does NOT assert any
particular headline outcome (how many regimes pass, how many poisons are
committed or vetoed, how many attacks the Haar probe vetoes, how many grind
tries succeeded): those are results, not invariants. It is not tamper
evidence and not an independent re-derivation: the digest recipe is public,
so an edited file with a recomputed `certificate_sha256` passes. Re-deriving
the results needs `scripts/dual_morphogenesis_benchmark.py --check` in a
pinned environment (and `--check` is not portable across platforms/libm).
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict

REGIMES = (
    "M0_fixed_scalar",
    "M1_synaptic_only",
    "M2_sensory_mpdi_fixed_dim",
    "M3_full_dual_morphogenesis",
)
MPDI_REGIMES = ("M2_sensory_mpdi_fixed_dim", "M3_full_dual_morphogenesis")

REGIME_KEYS = (
    "mode", "final_dim", "core_drift", "mean_shifted_ood_r2", "min_wave_shifted_ood_r2",
    "mean_shunted_ood_r2", "wave_r2s", "max_ood_tail_ratio", "poison_offered",
    "poison_committed", "poison_vetoed", "poison_improves_dominant_count",
    "clean_gate_commits", "clean_gate_vetoes", "probe_mitosis_events",
    "probe_identifiable_waves", "synaptic_mitosis_events", "synaptic_rows_added",
    "dual_certificate_passed", "fraction_dual_sha256", "partitioned_drift_q",
    "remaining_budget_q", "passed_joint_gate",
)


def verify_report_dict(rep: Dict[str, Any]) -> bool:
    body = {k: v for k, v in rep.items() if k != "certificate_sha256"}
    got_sha = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if got_sha != rep.get("certificate_sha256"):
        return False

    n_seeds = int(rep.get("n_seeds", 0))
    n_waves = int(rep.get("n_waves", 0))
    seeds = rep.get("per_seed_records", [])
    if n_seeds != 12 or len(seeds) != n_seeds or n_waves != 5:
        return False
    if any(int(s.get("seed", -1)) != i for i, s in enumerate(seeds)):
        return False

    # Provenance block exists and is shaped right (values are not asserted: the
    # commit may legitimately be "unknown" outside a git checkout).
    prov = rep.get("provenance")
    if not isinstance(prov, dict) or not {
        "git_commit", "python_version", "numpy_version", "platform", "command"
    }.issubset(prov.keys()):
        return False
    pdf_fields = rep.get("platform_dependent_fields")
    if not isinstance(pdf_fields, list) or not pdf_fields or "certificate_sha256" not in pdf_fields:
        return False

    sm = rep.get("summary_by_regime", {})
    if set(sm.keys()) != set(REGIMES):
        return False

    for m in REGIMES:
        rows = [s["regimes"][m] for s in seeds if m in s.get("regimes", {})]
        if len(rows) != n_seeds:
            return False
        s = sm[m]
        # Per-seed rows must add up to the summary.
        if int(s["passes_of_12"]) != sum(1 for r in rows if r["passed_joint_gate"]):
            return False
        if int(s["total_poison_committed_of_120"]) != sum(int(r["poison_committed"]) for r in rows):
            return False
        if int(s["total_poison_vetoed_of_120"]) != sum(int(r["poison_vetoed"]) for r in rows):
            return False
        if int(s["total_poison_improves_dominant_of_120"]) != sum(int(r["poison_improves_dominant_count"]) for r in rows):
            return False
        if abs(float(s["mean_shifted_ood_r2"]) - sum(float(r["mean_shifted_ood_r2"]) for r in rows) / n_seeds) > 1e-3:
            return False
        if abs(float(s["mean_min_wave_r2"]) - sum(float(r["min_wave_shifted_ood_r2"]) for r in rows) / n_seeds) > 1e-3:
            return False
        if abs(float(s["mean_shunted_ood_r2"]) - sum(float(r["mean_shunted_ood_r2"]) for r in rows) / n_seeds) > 1e-3:
            return False
        if abs(float(s["mean_max_ood_tail_ratio"]) - sum(float(r["max_ood_tail_ratio"]) for r in rows) / n_seeds) > 1e-3:
            return False
        if float(s["max_core_drift"]) != max(float(r["core_drift"]) for r in rows):
            return False
        if any(int(r["final_dim"]) != int(s["final_dim"]) for r in rows):
            return False

        for r in rows:
            # Structural invariants of each per-seed regime record.
            if any(k not in r for k in REGIME_KEYS):
                return False
            if r["mode"] != m:
                return False
            if float(r["core_drift"]) != 0.0:
                return False
            if int(r["poison_offered"]) != 2 * n_waves:
                return False
            if int(r["poison_committed"]) + int(r["poison_vetoed"]) != int(r["poison_offered"]):
                return False
            if not 0 <= int(r["poison_improves_dominant_count"]) <= int(r["poison_offered"]):
                return False
            if len(r["wave_r2s"]) != n_waves:
                return False
            if float(r["min_wave_shifted_ood_r2"]) != min(float(x) for x in r["wave_r2s"]):
                return False
            if abs(float(r["mean_shifted_ood_r2"]) - sum(float(x) for x in r["wave_r2s"]) / n_waves) > 2e-6:
                return False
            if not 0 <= int(r["probe_mitosis_events"]) <= n_waves:
                return False
            if not 0 <= int(r["probe_identifiable_waves"]) <= n_waves:
                return False
            if int(r["synaptic_rows_added"]) != 4 * int(r["synaptic_mitosis_events"]):
                return False
            # The clean plasmid goes through the gate exactly once per wave in the
            # MPDI regimes, and never in the scalar regimes.
            expected_clean = n_waves if m in MPDI_REGIMES else 0
            if int(r["clean_gate_commits"]) + int(r["clean_gate_vetoes"]) != expected_clean:
                return False
            # The fraction dual either passed with in-cap drift and non-negative
            # budget, or failed closed with all certificate fields null.
            if r["dual_certificate_passed"]:
                if Fraction(r["remaining_budget_q"]) < 0 or Fraction(r["partitioned_drift_q"]) > Fraction(3, 4):
                    return False
                if not isinstance(r["fraction_dual_sha256"], str):
                    return False
            else:
                if r["fraction_dual_sha256"] is not None or r["partitioned_drift_q"] is not None or r["remaining_budget_q"] is not None:
                    return False
            # passed_joint_gate must follow from the recorded fields (it is evaluated
            # on the rounded values that are recorded).
            recomputed = bool(
                float(r["core_drift"]) == 0.0
                and float(r["mean_shifted_ood_r2"]) >= 0.80
                and float(r["min_wave_shifted_ood_r2"]) >= 0.72
                and float(r["max_ood_tail_ratio"]) <= 1.0
                and int(r["poison_committed"]) == 0
                and bool(r["dual_certificate_passed"])
            )
            if bool(r["passed_joint_gate"]) != recomputed:
                return False

    # Boundary audit identities (mathematical/accounting invariants, not headline outcomes).
    ba = rep.get("boundary_audits", {})
    us = ba.get("unprobed_subspace_audit", {})
    if int(us.get("unobserved_nullity_dim", -1)) != int(us.get("peripheral_dim", 0)) - int(us.get("joint_probe_rank", -1)):
        return False
    if int(us.get("unobserved_nullity_dim", 0)) <= 0:
        return False
    if not 1 <= int(us.get("joint_probe_rank", 0)) <= min(int(us.get("n_dom_samples", 0)) + int(us.get("n_tail_samples", 0)), int(us.get("peripheral_dim", 0))):
        return False
    if us.get("mpdi_detects_unprobed_nullspace") is not False:
        return False
    if float(us.get("invisible_attack_dom_delta", 1.0)) > 1e-9 or float(us.get("invisible_attack_tail_delta", 1.0)) > 1e-9:
        return False

    # v1.1 Haar probe refresh audit: stated N, counts within [0, N], nullity accounting.
    ha = ba.get("haar_probe_refresh_audit", {})
    n_trials = int(ha.get("n_trials", 0))
    if n_trials != 100:
        return False
    if len(ha.get("verifier_nonce_hex", "")) != 64:
        return False
    prior_nullity = int(ha.get("prior_unobserved_nullity_dim", -1))
    if prior_nullity != int(ha.get("peripheral_dim", 0)) - int(ha.get("joint_probe_rank", -1)) or prior_nullity <= 0:
        return False
    sub4_rows = int(ha.get("sub4_haar_rows", 0))
    if not 1 <= sub4_rows < prior_nullity:
        return False
    if int(ha.get("haar_full_post_refresh_nullity", -1)) != 0:
        return False
    if int(ha.get("haar_sub4_post_refresh_nullity", -1)) != prior_nullity - sub4_rows:
        return False
    for key in (
        "static_mpdi_attack_vetoed_of_100",
        "haar_full_complement_attack_vetoed_of_100",
        "haar_sub4_attack_vetoed_of_100",
        "static_mpdi_false_vetoed_of_100",
        "haar_full_complement_false_vetoed_of_100",
        "haar_sub4_false_vetoed_of_100",
    ):
        if not 0 <= int(ha.get(key, -1)) <= n_trials:
            return False
    n_seed_probes = int(ha.get("n_seed_probes", 0))
    if n_seed_probes < 2:
        return False
    full_spread = float(ha.get("full_complement_energy_seed_spread", -1.0))
    sub4_spread = float(ha.get("sub4_energy_seed_spread", -1.0))
    if full_spread < 0.0 or sub4_spread < 0.0:
        return False
    if bool(ha.get("full_complement_is_deterministic_projection", False)):
        # If full-complement mode is a deterministic projection, the measured
        # spread must be within one 10^-6 quantization tick and the energy must
        # match the plain null-space projection norm.
        if full_spread > 1e-6 or ha.get("full_complement_energy_matches_null_projection") is not True:
            return False
    else:
        if full_spread <= 1e-6 and ha.get("full_complement_energy_matches_null_projection") is True:
            return False

    # v1.1 grinding audit: stated N and cap, tries within the cap, rates consistent.
    gr = ba.get("grinding_audit", {})
    max_tries = int(gr.get("max_grind_tries", 0))
    if max_tries < 1:
        return False
    if len(gr.get("fixed_public_nonce_hex", "")) != 64:
        return False
    for key in ("sub4_fixed_public_nonce_tries_to_success", "full_fixed_public_nonce_tries_to_success"):
        v = gr.get(key)
        if v is not None and not 1 <= int(v) <= max_tries:
            return False
    n_fresh = int(gr.get("n_fresh_nonce_submissions", 0))
    if n_fresh != 100:
        return False
    for mode in ("sub4", "full"):
        succ = int(gr.get(f"{mode}_fresh_nonce_attack_successes_of_100", -1))
        if not 0 <= succ <= n_fresh:
            return False
        if abs(float(gr.get(f"{mode}_fresh_nonce_per_submission_success_rate", -1.0)) - succ / n_fresh) > 1e-12:
            return False

    # v1.1 rational bit-length audit. The fixed-radix accumulator has a
    # denominator dividing 10^6 < 2^20 forever (BY CONSTRUCTION); the
    # discrepancy is bounded by n_steps ticks of 10^-6 (direction="up").
    bl = ba.get("rational_bitlength_audit", {})
    if int(bl.get("fixed_radix_denom_bits_by_construction", -1)) != (10**6).bit_length():
        return False
    if not 1 <= int(bl.get("fixed_radix_1e6_250_steps_bits", 0)) <= 20:
        return False
    if not 1 <= int(bl.get("fixed_radix_1e6_2500_steps_bits", 0)) <= 20:
        return False
    if int(bl.get("raw_ieee754_dyadic_250_steps_bits", 0)) < 1 or int(bl.get("stern_brocot_250_steps_bits", 0)) < 1:
        return False
    if float(bl.get("max_250_step_discrepancy", 1.0)) > 250 * 1e-6 + 1e-9:
        return False
    if float(bl.get("max_2500_step_discrepancy", 1.0)) > 2500 * 1e-6 + 1e-9:
        return False

    # Measured per-seed denominator bit-lengths must agree with the per-seed
    # records (recomputed here in pure stdlib; platform-independent).
    da = ba.get("certificate_denominator_audit", {})
    dual_passed = 0
    max_cert_bits = 0
    max_drift_bits = 0
    for s in seeds:
        for r in s["regimes"].values():
            if r["dual_certificate_passed"]:
                dual_passed += 1
                max_cert_bits = max(
                    max_cert_bits,
                    Fraction(r["remaining_budget_q"]).denominator.bit_length(),
                    Fraction(r["partitioned_drift_q"]).denominator.bit_length(),
                )
            for x in r["wave_r2s"]:
                d = Fraction.from_float(max(0.0, 1.0 - float(x)))
                max_drift_bits = max(max_drift_bits, d.denominator.bit_length())
    if int(da.get("dual_certificates_passed_count", -1)) != dual_passed:
        return False
    if int(da.get("max_certificate_q_denom_bits", -1)) != max_cert_bits:
        return False
    if int(da.get("exact_drift_input_denom_bits_from_recorded_wave_r2_max", -1)) != max_drift_bits:
        return False

    return True


def main() -> int:
    p = Path(__file__).resolve().parent / "certificate.json"
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
    rep = json.loads(p.read_text(encoding="utf-8"))
    if not verify_report_dict(rep):
        print("FAIL: dual morphogenesis certificate verification failed", file=sys.stderr)
        return 1
    print(f"OK: dual morphogenesis certificate self-consistent ({rep['certificate_sha256']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
