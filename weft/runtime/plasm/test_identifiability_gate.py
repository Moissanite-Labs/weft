#!/usr/bin/env python3
"""Unit, boundary-closure, and tamper tests for `weft/runtime/plasm/identifiability_gate.py` (v1.1)."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import unittest

import numpy as np

from weft.runtime.plasm.identifiability_gate import (
    FIXED_RADIX_DENOM,
    certify_probe_world_identifiability,
    certify_shift_robust_corridors_helly,
    evaluate_haar_refreshed_mpdi_gate,
    evaluate_multi_probe_divergence_gate,
    quantize_fixed_radix_q,
    sample_haar_orthogonal_probe,
    verify_farkas_identifiability_certificate,
    verify_haar_probe_refresh_receipt,
    verify_multi_probe_divergence_receipt,
)


class TestWeftAsmaCrossPollinationV11(unittest.TestCase):
    def test_fixed_radix_1e6_caps_denominator_at_20_bits_over_2500_steps(self) -> None:
        acc = Fraction(0, 1)
        for k in range(1, 2501):
            val = 0.0137 + 0.0001 * float(np.sin(k))
            acc += quantize_fixed_radix_q(val, denom=FIXED_RADIX_DENOM, min_positive_tick=True)
        # 1_000_000.bit_length() == 20: denominator NEVER exceeds 20 bits even after 2,500 steps!
        self.assertLessEqual(acc.denominator.bit_length(), 20)
        self.assertEqual(FIXED_RADIX_DENOM % acc.denominator, 0)

        # Sub-micro-unit positive float `1e-18` with `min_positive_tick=True` charges 1/1_000_000 (blocks Zeno!)
        self.assertEqual(quantize_fixed_radix_q(1e-18, min_positive_tick=True), Fraction(1, 1_000_000))

    def test_fiat_shamir_haar_probe_refresh_closes_12d_joint_nullspace(self) -> None:
        rng = np.random.default_rng(20261113)
        periph_dim, out_dim = 32, 6
        x_dom = rng.standard_normal((12, periph_dim))
        x_tail = rng.standard_normal((8, periph_dim))
        obs = np.vstack([x_dom, x_tail])  # 20 x 32 -> 12-D unobserved null space!

        _, _, vh = np.linalg.svd(obs, full_matrices=True)
        null_12 = vh[20:, :]  # (12, 32), invisible to BOTH x_dom and x_tail!

        # Test 50 omniscient double-null-space attacks across both full-complement (`max_haar_rows=None`)
        # and sub-sampled (`max_haar_rows=4 < 12`) Fiat-Shamir modes!
        for sub_k in (None, 4):
            vetoed = 0
            for idx in range(25):
                coeff = rng.standard_normal((12, out_dim))
                attack = null_12.T @ coeff
                attack = attack * (4.0 / (np.linalg.norm(attack) + 1e-12))

                # Confirm attack is completely invisible (< 1e-13) to static x_dom and x_tail!
                self.assertLess(float(np.linalg.norm(x_dom @ attack)), 1e-12)
                self.assertLess(float(np.linalg.norm(x_tail @ attack)), 1e-12)

                rec = evaluate_haar_refreshed_mpdi_gate(
                    observed_peripheral_probes=obs,
                    candidate_peripheral_delta=attack,
                    delta_dominant=-0.15,
                    static_tail_delta=float(np.linalg.norm(x_tail @ attack)),
                    static_tail_scale=0.25,
                    haar_scale=0.50,
                    colony_seed=42,
                    epoch=idx,
                    max_haar_rows=sub_k,
                )
                self.assertTrue(verify_haar_probe_refresh_receipt(rec)["ok"])
                if sub_k is None:
                    self.assertEqual(rec.prior_unobserved_nullity, 12)
                    self.assertEqual(rec.post_refresh_nullity, 0)
                else:
                    self.assertEqual(rec.post_refresh_nullity, 8)
                self.assertTrue(rec.mpdi_receipt.scalar_gate_would_commit)
                self.assertFalse(rec.mpdi_receipt.mpdi_gate_commits)
                if rec.mpdi_receipt.masked_regression_caught:
                    vetoed += 1

                # Tamper check on receipt nullity accounting
                bad = replace(rec, post_refresh_nullity=99)
                self.assertFalse(verify_haar_probe_refresh_receipt(bad)["ok"])

            self.assertEqual(vetoed, 25)

    def test_mezzadri_haar_probe_orthonormality_and_exact_complement_orthogonality(self) -> None:
        obs = np.random.default_rng(7).standard_normal((14, 24))
        q_haar, meta = sample_haar_orthogonal_probe(obs, challenge_seed=999)
        self.assertEqual(meta["prior_unobserved_nullity"], 10)
        self.assertEqual(meta["post_refresh_nullity"], 0)
        self.assertEqual(q_haar.shape, (10, 24))
        np.testing.assert_allclose(q_haar @ q_haar.T, np.eye(10), atol=1e-12)
        np.testing.assert_allclose(obs @ q_haar.T, np.zeros((14, 10)), atol=1e-12)

    def test_mpdi_and_farkas_and_helly_regressions_preserved(self) -> None:
        rec = evaluate_multi_probe_divergence_gate(
            delta_dominant=-1.0,
            delta_opposing_probes=[16.0],
            probe_scales=[4.0],
            dominant_weight=25.0,
        )
        self.assertTrue(verify_multi_probe_divergence_receipt(rec)["ok"])
        self.assertTrue(rec.masked_regression_caught)

        c_2d = certify_probe_world_identifiability(
            [Fraction(4, 5), Fraction(18, 25)],
            [Fraction(19, 25), Fraction(4, 5)],
            max_bias=Fraction(1, 20),
            target_eps=Fraction(1, 60),
        )
        self.assertTrue(verify_farkas_identifiability_certificate(c_2d)["ok"])
        self.assertEqual(c_2d.eps_star_q, "3/100")

        res = certify_shift_robust_corridors_helly(
            row_base_fisher=[0.9, 0.9, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1],
            row_shift_slopes=[0.0, 0.0, 0.6, -0.6, 0.6, 0.1, -0.1, 0.0],
            plasmid_demands=[2, 2],
            core_rows=2,
            fisher_cap=Fraction(1, 2),
            max_shift_beta=Fraction(1, 1),
        )
        self.assertEqual(res["uniform_mitosis_deficit"], 1)


class TestHellyMidSegmentBottleneck(unittest.TestCase):
    def test_true_min_shift_flow_catches_mid_segment_bottleneck(self) -> None:
        # Rows r0,r1 eligible on [-10, 3] and [-10, 7]; r2,r3 eligible on [4, 10] and [8, 10].
        # Every Helly knot reports flow 2 (demand 2). In the open segment (3, 4) only r1
        # remains eligible, so the true worst-case flow is 1. Knot-only sweeps miss this.
        res = certify_shift_robust_corridors_helly(
            row_base_fisher=[Fraction(0), Fraction(0), Fraction(3, 5), Fraction(3, 5)],
            row_shift_slopes=[Fraction(1, 6), Fraction(1, 14), Fraction(-1, 40), Fraction(-1, 80)],
            plasmid_demands=[2],
            core_rows=0,
            fisher_cap=Fraction(1, 2),
            max_shift_beta=Fraction(10, 1),
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
