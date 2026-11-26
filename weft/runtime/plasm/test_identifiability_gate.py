#!/usr/bin/env python3
"""Unit, tamper, and v1.1 boundary-closure tests for `weft/runtime/plasm/identifiability_gate.py`."""

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
    fiat_shamir_probe_seed,
    quantize_fixed_radix_q,
    sample_haar_orthogonal_probe,
    verify_farkas_identifiability_certificate,
    verify_haar_probe_refresh_receipt,
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


class TestV11FixedRadixQuantizer(unittest.TestCase):
    """v1.1: fixed-radix 10^-6 boundary quantizer with a required conservative `direction`."""

    def test_quantize_directions_are_conservative(self) -> None:
        exact = Fraction.from_float(0.1234565)
        # A cost quantizes UP: never below the exact float value.
        up = quantize_fixed_radix_q(0.1234565, direction="up")
        self.assertEqual(up, Fraction(123457, 10**6))
        self.assertGreater(up, exact)
        # A budget quantizes DOWN: never above the exact float value.
        down = quantize_fixed_radix_q(0.1234565, direction="down")
        self.assertEqual(down, Fraction(123456, 10**6))
        self.assertLess(down, exact)
        # "nearest" stays within half a tick of the exact value.
        nearest = quantize_fixed_radix_q(0.1234565, direction="nearest")
        self.assertLessEqual(abs(nearest - exact), Fraction(1, 2 * 10**6))
        self.assertEqual(10**6 % nearest.denominator, 0)
        # Exact inputs pass through unchanged; quantized floats keep denominator dividing 10^6.
        self.assertEqual(quantize_fixed_radix_q(Fraction(3, 7), direction="up"), Fraction(3, 7))
        self.assertEqual(quantize_fixed_radix_q(5, direction="down"), Fraction(5, 1))
        self.assertEqual(quantize_fixed_radix_q("2/3", direction="nearest"), Fraction(2, 3))
        for d in ("up", "down", "nearest"):
            q = quantize_fixed_radix_q(0.1, direction=d)
            self.assertEqual(10**6 % q.denominator, 0)
        # Validation: bad direction, bool, non-finite.
        with self.assertRaises(ValueError):
            quantize_fixed_radix_q(0.5, direction="sideways")
        with self.assertRaises(ValueError):
            quantize_fixed_radix_q(True, direction="up")
        with self.assertRaises(ValueError):
            quantize_fixed_radix_q(float("nan"), direction="up")
        with self.assertRaises(ValueError):
            quantize_fixed_radix_q(float("inf"), direction="down")

    def test_fixed_radix_1e6_caps_denominator_at_20_bits_over_2500_steps(self) -> None:
        acc = Fraction(0, 1)
        for k in range(1, 2501):
            val = 0.0137 + 0.0001 * float(np.sin(k))
            acc += quantize_fixed_radix_q(val, direction="up")
        # 1_000_000.bit_length() == 20: the accumulator denominator NEVER exceeds
        # 20 bits, by construction, even after 2,500 steps.
        self.assertEqual(FIXED_RADIX_DENOM.bit_length(), 20)
        self.assertLessEqual(acc.denominator.bit_length(), 20)
        self.assertEqual(FIXED_RADIX_DENOM % acc.denominator, 0)

    def test_mpdi_receipt_keeps_exact_conversion_not_1e6_rounding(self) -> None:
        # The certificate path must NOT silently quantize to 1e-6 (review item 3):
        # a float delta_dominant is recorded via the exact `_to_q` conversion.
        rec = evaluate_multi_probe_divergence_gate(
            delta_dominant=0.1234565,
            delta_opposing_probes=[1.0],
            probe_scales=[1.0],
        )
        expected = Fraction.from_float(0.1234565).limit_denominator(10**9)
        self.assertEqual(rec.delta_dominant_q, f"{expected.numerator}/{expected.denominator}")
        self.assertNotEqual(rec.delta_dominant_q, "123456/1000000")
        self.assertNotEqual(rec.delta_dominant_q, "123457/1000000")
        self.assertTrue(verify_multi_probe_divergence_receipt(rec)["ok"])


class TestV11FiatShamirHaarProbeRefresh(unittest.TestCase):
    """v1.1: Fiat-Shamir Haar orthogonal probe refresh over the unobserved joint null space."""

    def _obs_and_null(self) -> tuple:
        rng = np.random.default_rng(20261113)
        periph_dim, out_dim = 32, 6
        x_dom = rng.standard_normal((12, periph_dim))
        x_tail = rng.standard_normal((8, periph_dim))
        obs = np.vstack([x_dom, x_tail])  # 20 x 32 -> 12-D unobserved null space
        _, _, vh = np.linalg.svd(obs, full_matrices=True)
        null_basis = vh[20:, :]  # (12, 32), orthogonal to BOTH probe families
        return obs, x_dom, x_tail, null_basis, out_dim

    def test_fiat_shamir_seed_depends_on_verifier_nonce(self) -> None:
        delta = np.random.default_rng(1).standard_normal((32, 6))
        s1, h1 = fiat_shamir_probe_seed(2026, 0, delta, verifier_nonce=b"\x01" * 32)
        s2, h2 = fiat_shamir_probe_seed(2026, 0, delta, verifier_nonce=b"\x02" * 32)
        s1b, h1b = fiat_shamir_probe_seed(2026, 0, delta, verifier_nonce=b"\x01" * 32)
        self.assertNotEqual(h1, h2)
        self.assertNotEqual(s1, s2)
        self.assertEqual((s1, h1), (s1b, h1b))  # deterministic for a fixed nonce
        with self.assertRaises(TypeError):
            fiat_shamir_probe_seed(2026, 0, delta, verifier_nonce="not-bytes")

    def test_haar_refresh_vetoes_joint_nullspace_attacks_both_modes(self) -> None:
        obs, x_dom, x_tail, null_basis, out_dim = self._obs_and_null()
        rng = np.random.default_rng(4242)
        nonce = bytes(range(32))
        for sub_k, expected_post in ((None, 0), (4, 8)):
            vetoed = 0
            for idx in range(25):
                coeff = rng.standard_normal((12, out_dim))
                attack = null_basis.T @ coeff
                attack = attack * (4.0 / (np.linalg.norm(attack) + 1e-12))
                # The attack is invisible (< 1e-12) to both static probe families.
                self.assertLess(float(np.linalg.norm(x_dom @ attack)), 1e-12)
                self.assertLess(float(np.linalg.norm(x_tail @ attack)), 1e-12)
                rec = evaluate_haar_refreshed_mpdi_gate(
                    observed_peripheral_probes=obs,
                    candidate_peripheral_delta=attack,
                    delta_dominant=-0.15,
                    static_tail_delta=float(np.linalg.norm(x_tail @ attack)),
                    static_tail_scale=0.25,
                    haar_scale=0.50,
                    verifier_nonce=nonce,
                    colony_seed=42,
                    epoch=idx,
                    max_haar_rows=sub_k,
                )
                self.assertTrue(verify_haar_probe_refresh_receipt(rec, expected_verifier_nonce=nonce)["ok"])
                self.assertEqual(rec.prior_unobserved_nullity, 12)
                self.assertEqual(rec.post_refresh_nullity, expected_post)
                self.assertTrue(rec.mpdi_receipt.scalar_gate_would_commit)
                self.assertFalse(rec.mpdi_receipt.mpdi_gate_commits)
                if rec.mpdi_receipt.masked_regression_caught:
                    vetoed += 1
                # Tamper checks: nullity accounting and the verifier nonce.
                bad = replace(rec, post_refresh_nullity=99)
                self.assertFalse(verify_haar_probe_refresh_receipt(bad)["ok"])
                wrong = verify_haar_probe_refresh_receipt(rec, expected_verifier_nonce=b"\xff" * 32)
                self.assertEqual(wrong, {"ok": False, "reason": "verifier_nonce_mismatch"})
            self.assertEqual(vetoed, 25)

    def test_mezzadri_haar_probe_orthonormality_and_complement_orthogonality(self) -> None:
        obs = np.random.default_rng(7).standard_normal((14, 24))
        q_haar, meta = sample_haar_orthogonal_probe(obs, challenge_seed=999)
        self.assertEqual(meta["prior_unobserved_nullity"], 10)
        self.assertEqual(meta["post_refresh_nullity"], 0)
        self.assertEqual(q_haar.shape, (10, 24))
        np.testing.assert_allclose(q_haar @ q_haar.T, np.eye(10), atol=1e-12)
        np.testing.assert_allclose(obs @ q_haar.T, np.zeros((14, 10)), atol=1e-12)

    def test_full_complement_mode_is_a_deterministic_projection(self) -> None:
        # Review item 1: in full-complement mode the probe energy is identical
        # across challenge seeds and equals the plain null-space projection norm
        # ("randomisation in name only"); sub-sampled mode is seed-dependent.
        obs, _, _, null_basis, out_dim = self._obs_and_null()
        rng = np.random.default_rng(99)
        delta = null_basis.T @ rng.standard_normal((12, out_dim))
        delta = delta * (4.0 / (np.linalg.norm(delta) + 1e-12))
        null_proj_norm = float(np.linalg.norm(null_basis @ delta))
        nonce = b"\x07" * 32
        full_energies, sub4_energies = [], []
        for s in range(8):
            rec_full = evaluate_haar_refreshed_mpdi_gate(
                observed_peripheral_probes=obs,
                candidate_peripheral_delta=delta,
                delta_dominant=-0.15,
                static_tail_delta=0.0,
                static_tail_scale=0.25,
                haar_scale=0.50,
                verifier_nonce=nonce,
                colony_seed=2026,
                epoch=s,
                max_haar_rows=None,
            )
            rec_sub4 = evaluate_haar_refreshed_mpdi_gate(
                observed_peripheral_probes=obs,
                candidate_peripheral_delta=delta,
                delta_dominant=-0.15,
                static_tail_delta=0.0,
                static_tail_scale=0.25,
                haar_scale=0.50,
                verifier_nonce=nonce,
                colony_seed=2026,
                epoch=s,
                max_haar_rows=4,
            )
            full_energies.append(float(Fraction(rec_full.haar_probe_energy_q)))
            sub4_energies.append(float(Fraction(rec_sub4.haar_probe_energy_q)))
        full_spread = max(full_energies) - min(full_energies)
        sub4_spread = max(sub4_energies) - min(sub4_energies)
        # Quantized UP, so each energy is within one 10^-6 tick of the projection norm.
        self.assertLessEqual(full_spread, 1e-6)
        for e in full_energies:
            self.assertGreaterEqual(e, null_proj_norm - 1e-12)
            self.assertLessEqual(e - null_proj_norm, 1e-6)
        self.assertGreater(sub4_spread, 1e-9)

    def test_haar_gate_passes_generic_updates_at_half_static_scale(self) -> None:
        # Review item 1: 100/100 attack vetoes alone do not distinguish the gate
        # from one that rejects everything; generic updates at half the 0.25
        # static scale must pass in both modes. This is not a zero-false-veto
        # claim: over the whole statically accepted range the benchmark measures
        # 7/100 (full-complement) and 4/100 (sub-4) false vetoes.
        obs, _, x_tail, _, out_dim = self._obs_and_null()
        rng = np.random.default_rng(31337)
        nonce = b"\x11" * 32
        for sub_k in (None, 4):
            false_vetoed = 0
            for idx in range(25):
                g = rng.standard_normal((32, out_dim))
                g = g * (0.125 / (np.linalg.norm(x_tail @ g) + 1e-12))
                rec = evaluate_haar_refreshed_mpdi_gate(
                    observed_peripheral_probes=obs,
                    candidate_peripheral_delta=g,
                    delta_dominant=-0.15,
                    static_tail_delta=float(np.linalg.norm(x_tail @ g)),
                    static_tail_scale=0.25,
                    haar_scale=0.50,
                    verifier_nonce=nonce,
                    colony_seed=2026,
                    epoch=idx,
                    max_haar_rows=sub_k,
                )
                self.assertTrue(verify_haar_probe_refresh_receipt(rec)["ok"])
                if rec.mpdi_receipt.masked_regression_caught:
                    false_vetoed += 1
            self.assertEqual(false_vetoed, 0)

    def test_fixed_public_nonce_is_grindable_fresh_nonce_is_not(self) -> None:
        # Review item 2: with a public/fixed nonce a rank-1 null-space attacker
        # can grind the sub-sampled (sub-4) challenge; with a fresh verifier
        # nonce per submission (drawn after commitment, unknown beforehand) the
        # per-submission success rate collapses. Not cryptographic either way.
        obs, _, x_tail, null_basis, out_dim = self._obs_and_null()
        grind_rng = np.random.default_rng(777001)
        nonce_rng = np.random.default_rng(777002)
        fixed_public_nonce = b"\x00" * 32

        def _rank1_attack() -> np.ndarray:
            a = grind_rng.standard_normal(12)
            b = grind_rng.standard_normal(out_dim)
            atk = np.outer(null_basis.T @ a, b)
            return atk * (2.0 / (np.linalg.norm(atk) + 1e-12))

        def _passes(attack: np.ndarray, nonce: bytes, sub_k) -> bool:
            rec = evaluate_haar_refreshed_mpdi_gate(
                observed_peripheral_probes=obs,
                candidate_peripheral_delta=attack,
                delta_dominant=-0.15,
                static_tail_delta=float(np.linalg.norm(x_tail @ attack)),
                static_tail_scale=0.25,
                haar_scale=0.50,
                verifier_nonce=nonce,
                colony_seed=2026,
                epoch=0,
                max_haar_rows=sub_k,
            )
            return bool(rec.mpdi_receipt.mpdi_gate_commits)

        # (a) fixed public nonce: grinding finds a passing attack well within the cap.
        tries = None
        for t in range(1, 5001):
            if _passes(_rank1_attack(), fixed_public_nonce, 4):
                tries = t
                break
        self.assertIsNotNone(tries)
        self.assertLessEqual(tries, 5000)

        # (b) fresh verifier nonce per submission: one shot per nonce.
        successes = 0
        for _ in range(25):
            fresh = nonce_rng.bytes(32)
            if _passes(_rank1_attack(), fresh, 4):
                successes += 1
        self.assertLessEqual(successes, 3)


if __name__ == "__main__":
    unittest.main()
