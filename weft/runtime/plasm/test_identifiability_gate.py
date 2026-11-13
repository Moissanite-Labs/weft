#!/usr/bin/env python3
"""Unit and tamper tests for `weft/runtime/plasm/identifiability_gate.py`."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import unittest

from weft.runtime.plasm.identifiability_gate import (
    certify_probe_world_identifiability,
    certify_shift_robust_corridors_helly,
    evaluate_multi_probe_divergence_gate,
    verify_farkas_identifiability_certificate,
    verify_multi_probe_divergence_receipt,
)


class TestWeftAsmaCrossPollination(unittest.TestCase):
    def test_mpdi_blocks_masked_tail_regression_across_20_cases(self) -> None:
        scalar_false_commits = 0
        mpdi_false_commits = 0
        for idx in range(20):
            # Dominant niche improves by -1.0, while rare OOD/safety probe degrades by +12..+24
            # Under 25:1 dominant weighting, scalar delta = -25 + (12..24) < 0 (FALSE REASSURANCE!)
            tail_deg = Fraction(12 + (idx % 13), 1)
            rec = evaluate_multi_probe_divergence_gate(
                delta_dominant=Fraction(-1, 1),
                delta_opposing_probes=[tail_deg, Fraction(3, 1)],
                probe_scales=[Fraction(4, 1), Fraction(2, 1)],
                dominant_weight=Fraction(25, 1),
                tail_weight=Fraction(1, 1),
                alert_threshold=Fraction(1, 1),
            )
            self.assertTrue(verify_multi_probe_divergence_receipt(rec)["ok"])
            if rec.scalar_gate_would_commit:
                scalar_false_commits += 1
            if rec.mpdi_gate_commits:
                mpdi_false_commits += 1

            # Tamper check: flipping mpdi_gate_commits even after re-hashing fails semantic verification!
            tampered = replace(rec, mpdi_gate_commits=True)
            self.assertFalse(verify_multi_probe_divergence_receipt(tampered)["ok"])

        self.assertEqual(scalar_false_commits, 20)
        self.assertEqual(mpdi_false_commits, 0)

    def test_mpdi_allows_genuinely_healthy_updates(self) -> None:
        rec = evaluate_multi_probe_divergence_gate(
            delta_dominant=Fraction(-2, 1),
            delta_opposing_probes=[Fraction(-1, 2), Fraction(1, 10)],
            probe_scales=[Fraction(2, 1), Fraction(1, 1)],
            alert_threshold=Fraction(1, 1),
        )
        self.assertTrue(rec.scalar_gate_would_commit)
        self.assertTrue(rec.mpdi_gate_commits)
        self.assertFalse(rec.masked_regression_caught)
        self.assertTrue(verify_multi_probe_divergence_receipt(rec)["ok"])

    def test_farkas_probe_identifiability_triggers_and_resolves_probe_mitosis(self) -> None:
        # Single scalar probe with |delta| = 1/25 <= 2*max_bias (1/10) has eps* == 0 -> triggers probe mitosis!
        c_1d = certify_probe_world_identifiability(
            [Fraction(4, 5)], [Fraction(19, 25)], max_bias=Fraction(1, 20), target_eps=Fraction(1, 60)
        )
        self.assertTrue(verify_farkas_identifiability_certificate(c_1d)["ok"])
        self.assertEqual(c_1d.eps_star_q, "0/1")
        self.assertTrue(c_1d.requires_probe_mitosis)

        # Adding an anti-correlated probe point cancels shared bias and lifts eps* = 3/100 > 1/60!
        c_2d = certify_probe_world_identifiability(
            [Fraction(4, 5), Fraction(18, 25)],
            [Fraction(19, 25), Fraction(4, 5)],
            max_bias=Fraction(1, 20),
            target_eps=Fraction(1, 60),
        )
        self.assertTrue(verify_farkas_identifiability_certificate(c_2d)["ok"])
        self.assertFalse(c_2d.requires_probe_mitosis)
        self.assertEqual(c_2d.eps_star_q, "3/100")

        # Tamper check on Farkas dual norm / value
        bad = replace(c_2d, eps_star_q="9/10")
        self.assertFalse(verify_farkas_identifiability_certificate(bad)["ok"])

    def test_helly_shift_robust_corridors_catch_mid_shift_fisher_collisions(self) -> None:
        # 8 total rows: 2 frozen core (0,1), 6 peripheral (2..7); 2 plasmids demanding 2 rows each (total=4)
        # At b=0, all 6 peripheral rows have Fisher=0.2 <= 0.5 cap (`static_b0_flow == 4`, looks safe!).
        # Under shift `b in [-1, +1]`, rows 2,3,4 spike (`0.2 + 0.6*b > 0.5` at b=+1), leaving only 3 safe rows!
        res = certify_shift_robust_corridors_helly(
            row_base_fisher=[0.9, 0.9, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1],
            row_shift_slopes=[0.0, 0.0, 0.6, -0.6, 0.6, 0.1, -0.1, 0.0],
            plasmid_demands=[2, 2],
            core_rows=2,
            fisher_cap=Fraction(1, 2),
            max_shift_beta=Fraction(1, 1),
        )
        self.assertEqual(res["static_b0_flow"], 4)
        self.assertTrue(res["static_b0_false_safety"])
        self.assertEqual(res["uniform_shift_safe_flow"], 3)
        self.assertEqual(res["uniform_mitosis_deficit"], 1)

    def test_helly_true_min_shift_flow_catches_mid_segment_bottleneck(self) -> None:
        # Rows: r0 and r1 are shift-prefix rows eligible on [-10, 3] and [-10, 7];
        # r2 and r3 are shift-suffix rows eligible on [4, 10] and [8, 10].
        # At every Helly knot the flow is 2 (demand 2). In the open segment (3, 4)
        # only row r1 remains eligible, so the true worst-case flow is 1.
        beta = Fraction(10, 1)
        res = certify_shift_robust_corridors_helly(
            row_base_fisher=[Fraction(0), Fraction(0), Fraction(3, 5), Fraction(3, 5)],
            row_shift_slopes=[Fraction(1, 6), Fraction(1, 14), Fraction(-1, 40), Fraction(-1, 80)],
            plasmid_demands=[2],
            core_rows=0,
            fisher_cap=Fraction(1, 2),
            max_shift_beta=beta,
        )
        self.assertEqual(res["min_pointwise_knot_flow"], 2)
        self.assertEqual(res["true_min_shift_flow"], 1)
        self.assertEqual(res["static_b0_flow"], 2)
        midpoint = next(
            s for s in res["segment_witnesses"] if s["open_interval_q"] == ["3/1", "4/1"]
        )
        self.assertEqual(midpoint["eligible_peripheral_rows"], [1])
        self.assertEqual(midpoint["max_flow"], 1)
        self.assertEqual(midpoint["deficit"], 1)


if __name__ == "__main__":
    unittest.main()
