#!/usr/bin/env python3
"""Regression tests for scaled Frobenius norm parity and Zeno budget floor in invariants.py."""

import math
import unittest

from weft.runtime.invariants.invariants import (
    _frobenius_norm,
    _torch_frobenius_norm_f64,
    verify_weight_update_safety,
    verify_weight_update_safety_ex,
)


class TestInvariantsOverflowAndZeno(unittest.TestCase):
    def test_unmasked_large_magnitude_no_overflow_parity_with_masked(self) -> None:
        base = [0.0, 0.0]
        cand = [1e200, 0.0]
        res_unmasked = verify_weight_update_safety_ex(base, cand, 2e200, 10.0, 1.0)
        res_masked = verify_weight_update_safety_ex(
            base, cand, 2e200, 10.0, 1.0, locked_mask=[0, 0]
        )
        self.assertEqual(res_unmasked, (True, 1e200, 9.0, "ok"))
        self.assertEqual(res_unmasked, res_masked)

        ok, dist, rem, reason = verify_weight_update_safety_ex(
            [0.0, 0.0], [3e200, 4e200], 6e200, 10.0, 1.0
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")
        self.assertEqual(rem, 9.0)
        self.assertTrue(math.isclose(dist, 5e200, rel_tol=1e-14))

        ok_rej, dist_rej, rem_rej, reason_rej = verify_weight_update_safety_ex(
            [0.0, 0.0], [3e200, 4e200], 4.9e200, 10.0, 1.0
        )
        self.assertFalse(ok_rej)
        self.assertEqual(reason_rej, "baseline_distance_exceeded")
        self.assertEqual(rem_rej, 10.0)
        self.assertTrue(math.isclose(dist_rej, 5e200, rel_tol=1e-14))

        ok_big, dist_big, rem_big, reason_big = verify_weight_update_safety_ex(
            [0.0, 0.0], [1e308, 1e308], 1.5e308, 10.0, 1.0
        )
        self.assertTrue(ok_big)
        self.assertEqual(reason_big, "ok")
        self.assertEqual(rem_big, 9.0)
        self.assertTrue(math.isclose(dist_big, math.sqrt(2.0) * 1e308, rel_tol=1e-14))

        ok_ovf, dist_ovf, rem_ovf, reason_ovf = verify_weight_update_safety_ex(
            [0.0, 0.0], [1.5e308, 1.5e308], 1.79e308, 10.0, 1.0
        )
        self.assertFalse(ok_ovf)
        self.assertTrue(math.isinf(dist_ovf))
        self.assertEqual(rem_ovf, 10.0)
        self.assertEqual(reason_ovf, "non_finite_weights")

        ok_diff_ovf, dist_diff_ovf, rem_diff_ovf, reason_diff_ovf = verify_weight_update_safety_ex(
            [-1e308, -1e308], [1e308, 1e308], 1.79e308, 10.0, 1.0
        )
        self.assertFalse(ok_diff_ovf)
        self.assertTrue(math.isinf(dist_diff_ovf))
        self.assertEqual(rem_diff_ovf, 10.0)
        self.assertEqual(reason_diff_ovf, "non_finite_weights")

    def test_unmasked_small_magnitude_blocks_underflow_radius_bypass(self) -> None:
        base = [0.0, 0.0]
        cand = [1e-200, 0.0]
        res_unmasked = verify_weight_update_safety_ex(base, cand, 1e-201, 10.0, 1.0)
        res_masked = verify_weight_update_safety_ex(
            base, cand, 1e-201, 10.0, 1.0, locked_mask=[0, 0]
        )
        self.assertFalse(res_unmasked[0])
        self.assertEqual(res_unmasked[3], "baseline_distance_exceeded")
        self.assertEqual(res_unmasked[2], 10.0)
        self.assertTrue(math.isclose(res_unmasked[1], 1e-200, rel_tol=1e-14))
        self.assertEqual(res_unmasked, res_masked)

        ok, dist, rem, reason = verify_weight_update_safety_ex(
            [0.0, 0.0], [3e-200, 4e-200], 6e-200, 10.0, 1.0
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")
        self.assertEqual(rem, 9.0)
        self.assertTrue(math.isclose(dist, 5e-200, rel_tol=1e-14))

    def test_unmasked_neumaier_precision_matches_masked_n65536(self) -> None:
        n = 65536
        base = [0.0] * n
        cand = [1e-4] * n
        cand[0] = 100.0
        ok_u, dist_u, rem_u, reason_u = verify_weight_update_safety_ex(
            base, cand, 120.0, 10.0, 1.0
        )
        ok_m, dist_m, rem_m, reason_m = verify_weight_update_safety_ex(
            base, cand, 120.0, 10.0, 1.0, locked_mask=[0] * n
        )
        self.assertTrue(ok_u)
        self.assertEqual((ok_u, dist_u, rem_u, reason_u), (ok_m, dist_m, rem_m, reason_m))
        self.assertTrue(math.isclose(dist_u, math.hypot(*cand), rel_tol=1e-14))

    def test_wrapper_compared_sizes_no_overflow_or_nan(self) -> None:
        res_same = verify_weight_update_safety(
            [0.0, 0.0], [1e200, 0.0], [1e200, 0.0], 10.0, 1.0, 2e200
        )
        self.assertTrue(res_same["accepted"])
        self.assertEqual(res_same["reason"], "ok")
        self.assertEqual(res_same["compared_sizes"], 0.0)
        self.assertEqual(res_same["baseline_distance"], 1e200)
        self.assertEqual(res_same["remaining_budget"], 9.0)

        res_step = verify_weight_update_safety(
            [0.0, 0.0], [0.0, 0.0], [1e200, 0.0], 10.0, 1.0, 2e200
        )
        self.assertTrue(res_step["accepted"])
        self.assertEqual(res_step["compared_sizes"], 1e200)
        self.assertEqual(res_step["baseline_distance"], 1e200)

        res_tiny = verify_weight_update_safety(
            [0.0, 0.0], [0.0, 0.0], [1e-200, 0.0], 10.0, 1.0, 1e-201
        )
        self.assertFalse(res_tiny["accepted"])
        self.assertEqual(res_tiny["reason"], "baseline_distance_exceeded")
        self.assertTrue(math.isclose(res_tiny["compared_sizes"], 1e-200, rel_tol=1e-14))

        self.assertEqual(_frobenius_norm([]), 0.0)
        self.assertTrue(math.isnan(_frobenius_norm([float("nan"), 1.0])))
        self.assertTrue(math.isnan(_frobenius_norm([float("inf"), float("nan")])))
        self.assertTrue(math.isinf(_frobenius_norm([float("inf"), 1.0])))

    def test_zeno_sub_ulp_budget_monotone_decrease(self) -> None:
        ok, dist, rem, reason = verify_weight_update_safety_ex(
            [0.0], [0.0], 120.0, 1e16, 0.1
        )
        self.assertTrue(ok)
        self.assertEqual(dist, 0.0)
        self.assertEqual(reason, "ok")
        self.assertLess(rem, 1e16)
        self.assertEqual(rem, math.nextafter(1e16, -math.inf))

        budget = 100.0
        sub_ulp_cost = 1e-16
        for _ in range(1000):
            prev = budget
            ok_s, _, budget, reason_s = verify_weight_update_safety_ex(
                [1.0, 2.0], [1.1, 2.1], 120.0, prev, sub_ulp_cost
            )
            self.assertTrue(ok_s)
            self.assertEqual(reason_s, "ok")
            self.assertLess(budget, prev)
            self.assertEqual(budget, math.nextafter(prev, -math.inf))

        wrap = verify_weight_update_safety(
            [0.0], [0.0], [0.0], 1e16, 0.1, 120.0
        )
        self.assertTrue(wrap["accepted"])
        self.assertEqual(wrap["remaining_budget"], math.nextafter(1e16, -math.inf))

        ok_ex, _, rem_ex, _ = verify_weight_update_safety_ex(
            [0.0], [0.0], 120.0, 1.0, 1.0
        )
        self.assertTrue(ok_ex)
        self.assertEqual(rem_ex, 0.0)

        min_sub = math.nextafter(0.0, 1.0)
        ok_sub, _, rem_sub, _ = verify_weight_update_safety_ex(
            [0.0], [0.0], 120.0, min_sub, min_sub
        )
        self.assertTrue(ok_sub)
        self.assertEqual(rem_sub, 0.0)

    def test_torch_fast_path_scaled_norm_and_zeno_parity(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")

        b_zero = torch.tensor([0.0, 0.0], dtype=torch.float64)
        c_big = torch.tensor([1e200, 0.0], dtype=torch.float64)
        ok, dist, rem, reason = verify_weight_update_safety_ex(
            b_zero, c_big, 2e200, 10.0, 1.0
        )
        self.assertEqual((ok, dist, rem, reason), (True, 1e200, 9.0, "ok"))

        c_pyth = torch.tensor([3e200, 4e200], dtype=torch.float64)
        ok_p, dist_p, rem_p, reason_p = verify_weight_update_safety_ex(
            b_zero, c_pyth, 6e200, 10.0, 1.0
        )
        self.assertTrue(ok_p)
        self.assertEqual(reason_p, "ok")
        self.assertEqual(rem_p, 9.0)
        self.assertTrue(math.isclose(dist_p, 5e200, rel_tol=1e-14))

        c_ovf = torch.tensor([1.5e308, 1.5e308], dtype=torch.float64)
        ok_o, dist_o, rem_o, reason_o = verify_weight_update_safety_ex(
            b_zero, c_ovf, 1.79e308, 10.0, 1.0
        )
        self.assertFalse(ok_o)
        self.assertTrue(math.isinf(dist_o))
        self.assertEqual(rem_o, 10.0)
        self.assertEqual(reason_o, "non_finite_weights")

        ok_do, dist_do, rem_do, reason_do = verify_weight_update_safety_ex(
            torch.tensor([-1e308], dtype=torch.float64),
            torch.tensor([1e308], dtype=torch.float64),
            1.79e308,
            10.0,
            1.0,
        )
        self.assertFalse(ok_do)
        self.assertTrue(math.isinf(dist_do))
        self.assertEqual(rem_do, 10.0)
        self.assertEqual(reason_do, "non_finite_weights")

        c_tiny = torch.tensor([1e-200, 0.0], dtype=torch.float64)
        ok_t, dist_t, rem_t, reason_t = verify_weight_update_safety_ex(
            b_zero, c_tiny, 1e-201, 10.0, 1.0
        )
        self.assertFalse(ok_t)
        self.assertEqual(reason_t, "baseline_distance_exceeded")
        self.assertEqual(rem_t, 10.0)
        self.assertTrue(math.isclose(dist_t, 1e-200, rel_tol=1e-14))

        ok_z0, dist_z0, rem_z0, reason_z0 = verify_weight_update_safety_ex(
            b_zero, b_zero, 120.0, 1e16, 0.1
        )
        self.assertTrue(ok_z0)
        self.assertEqual(dist_z0, 0.0)
        self.assertEqual(reason_z0, "ok")
        self.assertEqual(rem_z0, math.nextafter(1e16, -math.inf))

        budget = 100.0
        for _ in range(100):
            prev = budget
            ok_s, _, budget, _ = verify_weight_update_safety_ex(
                b_zero, b_zero, 120.0, prev, 1e-16
            )
            self.assertTrue(ok_s)
            self.assertLess(budget, prev)
            self.assertEqual(budget, math.nextafter(prev, -math.inf))

        res_wrap = verify_weight_update_safety(
            b_zero, c_big, c_big, 10.0, 1.0, 2e200
        )
        self.assertTrue(res_wrap["accepted"])
        self.assertEqual(res_wrap["compared_sizes"], 0.0)
        self.assertEqual(res_wrap["baseline_distance"], 1e200)

        self.assertEqual(
            _torch_frobenius_norm_f64(torch.tensor([], dtype=torch.float64)), 0.0
        )
        self.assertTrue(
            math.isnan(
                _torch_frobenius_norm_f64(
                    torch.tensor([float("nan"), 1.0], dtype=torch.float64)
                )
            )
        )
        self.assertTrue(
            math.isnan(
                _torch_frobenius_norm_f64(
                    torch.tensor([float("inf"), float("nan")], dtype=torch.float64)
                )
            )
        )
        self.assertTrue(
            math.isinf(
                _torch_frobenius_norm_f64(
                    torch.tensor([float("inf"), 1.0], dtype=torch.float64)
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
