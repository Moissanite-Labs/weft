"""
Unit, adversarial, and planted-mutation regression tests for `synaptic_flow.py`.

Run directly via standard Weft CI discovery:
  python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
"""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

import numpy as np

# Support both `python -m unittest discover -s weft/runtime/plasm -p 'test_*.py'`
# from repo root AND standalone direct execution.
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

try:
    from weft.runtime.plasm.synaptic_flow import (
        DinicSynapticFlowKernel,
        allocate_disjoint_synaptic_corridors,
        build_reproducible_plasm_report,
        canonicalize_peripheral_gauge,
        certify_cost_partitioned_dual,
        compute_cut_capacity,
        expand_weights_orthogonal_mitosis,
        pack_certificate_lock_record,
        verify_fraction_dual_certificate,
        verify_min_cut_mitosis_certificate,
    )
except ImportError:
    from synaptic_flow import (  # type: ignore
        DinicSynapticFlowKernel,
        allocate_disjoint_synaptic_corridors,
        build_reproducible_plasm_report,
        canonicalize_peripheral_gauge,
        certify_cost_partitioned_dual,
        compute_cut_capacity,
        expand_weights_orthogonal_mitosis,
        pack_certificate_lock_record,
        verify_fraction_dual_certificate,
        verify_min_cut_mitosis_certificate,
    )


class TestDinicSynapticRoutingAndMinCutMitosis(unittest.TestCase):
    def test_disjoint_routing_eliminates_hall_stacking_and_protects_core(self) -> None:
        # M = 32 channels -> default core_rows = 32 // 4 = 8 frozen rows (0..7)
        # Even if core rows 0..7 have 0.0 Fisher score, router MUST exclude them!
        fisher = np.linspace(0.0, 3.1, 32)
        cert = allocate_disjoint_synaptic_corridors(fisher, plasmid_demands=[4, 4, 4])
        verdict = verify_min_cut_mitosis_certificate(cert)
        self.assertTrue(verdict["ok"], verdict)
        self.assertEqual(cert.core_rows_frozen, 8)
        self.assertEqual(cert.max_flow, 12)
        self.assertEqual(cert.deficit, 0)
        self.assertFalse(cert.requires_mitosis)

        # Verify 0 overlap across plasmids and 0 intersection with core rows 0..7
        all_slots = [j for grp in cert.assignments for j in grp]
        self.assertEqual(len(all_slots), 12)
        self.assertEqual(len(set(all_slots)), 12)
        self.assertTrue(all(j >= 8 for j in all_slots))
        # Quietest 12 peripheral channels are exactly 8..19
        self.assertEqual(sorted(all_slots), list(range(8, 20)))

    def test_saturated_capacity_emits_verified_min_cut_and_exact_mitosis_deficit(self) -> None:
        # M = 24 (core_rows = 6 -> 18 peripheral channels), threshold restricts eligible to 10 channels
        fisher = np.arange(24, dtype=np.float64)
        # Eligible peripheral indices: 6..15 (10 channels); demand = 5 + 5 + 5 = 15 -> deficit = 5!
        cert = allocate_disjoint_synaptic_corridors(
            fisher,
            plasmid_demands=[5, 5, 5],
            max_fisher_threshold=15.0,
        )
        verdict = verify_min_cut_mitosis_certificate(cert)
        self.assertTrue(verdict["ok"], verdict)
        self.assertEqual(cert.max_flow, 10)
        self.assertEqual(cert.deficit, 5)
        self.assertTrue(cert.requires_mitosis)
        self.assertEqual(cert.cut_capacity_source_minimal, 10)
        self.assertEqual(cert.cut_capacity_sink_minimal, 10)
        self.assertTrue(set(cert.source_minimal_cut).issubset(set(cert.sink_minimal_cut)))

        # Trigger exact-deficit orthogonal mitosis (+5 rows) and re-route: deficit drops to 0!
        w_orig = np.random.default_rng(42).normal(size=(24, 16))
        w_exp, meta = expand_weights_orthogonal_mitosis(w_orig, deficit_rows=cert.deficit, core_rows=6)
        self.assertEqual(w_exp.shape, (29, 16))
        self.assertEqual(meta["core_row_drift"], 0.0)
        self.assertEqual(float(np.linalg.norm(w_exp[:24] - w_orig)), 0.0)

        fisher_after = np.concatenate([fisher, np.zeros(cert.deficit)])
        cert_after = allocate_disjoint_synaptic_corridors(
            fisher_after,
            plasmid_demands=[5, 5, 5],
            core_rows=6,
            max_fisher_threshold=15.0,
        )
        self.assertTrue(verify_min_cut_mitosis_certificate(cert_after)["ok"])
        self.assertEqual(cert_after.max_flow, 15)
        self.assertEqual(cert_after.deficit, 0)
        self.assertFalse(cert_after.requires_mitosis)

    def test_source_minimal_strictly_smaller_than_sink_minimal_on_two_stage_bottleneck(self) -> None:
        # Graph: 0 -> 1 (cap 3) -> 2 (cap 3) -> 3 (cap 3): residual zero-slack middle vertex 1..2
        # source_minimal = {0}, sink_minimal = {0, 1, 2}, both have exact min-cut capacity 3!
        net = DinicSynapticFlowKernel(4)
        net.add_edge(0, 1, 3)
        net.add_edge(1, 2, 3)
        net.add_edge(2, 3, 3)
        flow = net.solve_max_flow(0, 3)
        self.assertEqual(flow, 3)
        s_min = net.extract_residual_min_cut(0, 3, "source_minimal")
        t_min = net.extract_residual_min_cut(0, 3, "sink_minimal")
        self.assertEqual(s_min, (0,))
        self.assertEqual(t_min, (0, 1, 2))
        self.assertEqual(compute_cut_capacity(net.original_edges, set(s_min)), 3)
        self.assertEqual(compute_cut_capacity(net.original_edges, set(t_min)), 3)

    def test_planted_mutations_on_min_cut_certificate_fail_closed(self) -> None:
        fisher = np.linspace(0.1, 2.0, 20)
        base = allocate_disjoint_synaptic_corridors(fisher, plasmid_demands=[3, 3], core_rows=5)
        self.assertTrue(verify_min_cut_mitosis_certificate(base)["ok"])

        mutations = [
            replace(base, max_flow=base.max_flow - 1),
            replace(base, deficit=base.deficit + 1),
            replace(base, requires_mitosis=True),
            replace(base, source_minimal_cut=tuple(x for x in base.source_minimal_cut if x != 0)),
            replace(base, sink_minimal_cut=base.sink_minimal_cut + (base.network_vertex_count - 1,)),
            # Hall-stacking duplicate slot across plasmid 0 and plasmid 1
            replace(base, assignments=(base.assignments[0], (base.assignments[0][0],) + base.assignments[1][1:])),
            # Frozen core row 0 leaked into assignment
            replace(base, assignments=((0,) + base.assignments[0][1:], base.assignments[1])),
            # Tampered SHA-256 digest
            replace(base, sha256_digest="0" * 64),
        ]
        for idx, mutated in enumerate(mutations):
            res = verify_min_cut_mitosis_certificate(mutated)
            self.assertFalse(res["ok"], f"Planted mutation {idx} was not rejected!")


class TestExactFractionDualCertificates(unittest.TestCase):
    def test_exact_rational_cost_partitioning_and_farkas_witness(self) -> None:
        # Infeasible primal system: x_0 >= 2 (-x_0 <= -2) AND x_0 <= 1 (x_0 <= 1) -> 0 <= -1!
        # Exact Farkas witness: lambda = [1, 1] >= 0 -> lambda^T A = [-1 + 1] = [0], lambda^T b = -1 < 0.
        A = [[-1], [1]]
        b = [-2, 1]
        lam = [1, 1]

        cert = certify_cost_partitioned_dual(
            initial_budget=Fraction(10, 1),
            step_costs=[Fraction(5, 4), Fraction(7, 4), 2.5],
            quotient_drifts=[Fraction(1, 10), Fraction(2, 10), Fraction(3, 10)],
            drift_cap=Fraction(1, 4),
            quotient_weights=[Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)],
            farkas_system=(A, b, lam),
        )
        verdict = verify_fraction_dual_certificate(cert)
        self.assertTrue(verdict["ok"], verdict)
        self.assertTrue(verdict["farkas_witness_verified"])
        self.assertEqual(cert.remaining_budget_q, "9/2")  # 10 - (1.25 + 1.75 + 2.5) = 4.5
        # 1/2 * 1/10 + 1/4 * 2/10 + 1/4 * 3/10 = 2/40 + 2/40 + 3/40 = 7/40 <= 10/40
        self.assertEqual(cert.partitioned_drift_q, "7/40")

    def test_blocks_negative_cost_minting_and_zeno_sub_ulp_stagnation_in_exact_q(self) -> None:
        with self.assertRaises(ValueError):
            certify_cost_partitioned_dual(10.0, [-1000.0], [0.01], 0.1)
        with self.assertRaises(ValueError):
            certify_cost_partitioned_dual(10.0, [0.0], [0.01], 0.1)

        # Sub-half-ULP float32 step cost (`3e-6` against `100.0`) stagnates in naive float32
        # (`np.float32(100.0) - np.float32(3e-6) == 100.0`), yet strictly decreases in exact Q!
        sub_ulp = float(np.float32(3.0e-6))
        cert = certify_cost_partitioned_dual(100.0, [sub_ulp] * 25, [0.02, 0.04], 0.10)
        verdict = verify_fraction_dual_certificate(cert)
        self.assertTrue(verdict["ok"], verdict)
        self.assertLess(Fraction(cert.remaining_budget_q), Fraction(100, 1))

    def test_planted_mutations_on_fraction_dual_certificate_fail_closed(self) -> None:
        base = certify_cost_partitioned_dual(
            initial_budget="5/1",
            step_costs=["1/2", "1/2"],
            quotient_drifts=["1/20", "3/20"],
            drift_cap="1/5",
        )
        self.assertTrue(verify_fraction_dual_certificate(base)["ok"])

        tampered_cases = [
            replace(base, step_costs_q=("-1/2", "3/2")),
            replace(base, remaining_budget_q="5/1"),
            replace(base, quotient_weights_q=("3/5", "3/5")),
            replace(base, partitioned_drift_q="1/100"),
            replace(base, drift_cap_q="1/20"),
            replace(base, sha256_digest="f" * 64),
        ]
        for idx, tc in enumerate(tampered_cases):
            self.assertFalse(verify_fraction_dual_certificate(tc)["ok"], f"Tampered case {idx} passed!")

    def test_cryptographic_lock_buffer_packing(self) -> None:
        fisher = np.linspace(0.1, 1.0, 16)
        mc = allocate_disjoint_synaptic_corridors(fisher, [2, 2])
        dc = certify_cost_partitioned_dual(10, [1, 1], [Fraction(1, 20)], Fraction(1, 10))
        buf = pack_certificate_lock_record(mc, dc)
        self.assertEqual(len(buf), 12288)
        raw_json = buf.rstrip(bytes([0])).decode("utf-8")
        parsed = json.loads(raw_json)
        self.assertEqual(parsed["min_cut_sha256"], mc.sha256_digest)
        self.assertEqual(parsed["dual_sha256"], dc.sha256_digest)


class TestPeripheralGaugeCanonizationAndIssue51Report(unittest.TestCase):
    def test_peripheral_gauge_canonization_recovers_scrambled_weights_with_zero_core_drift(self) -> None:
        rng = np.random.default_rng(20261112)
        M, d_in, d_out, core_rows = 32, 12, 6, 8
        w_in = rng.normal(size=(M, d_in))
        b_in = rng.normal(size=M)
        w_out = rng.normal(size=(d_out, M))

        # Scramble ONLY peripheral channels 8..31 while keeping frozen core 0..7 intact
        periph_perm = rng.permutation(M - core_rows) + core_rows
        full_perm = np.concatenate([np.arange(core_rows), periph_perm])
        w_in_s = w_in[full_perm, :]
        b_in_s = b_in[full_perm]
        w_out_s = w_out[:, full_perm]

        wi_1, wo_1, bi_1, _ = canonicalize_peripheral_gauge(w_in, w_out, bias_in=b_in, core_rows=core_rows)
        wi_2, wo_2, bi_2, _ = canonicalize_peripheral_gauge(w_in_s, w_out_s, bias_in=b_in_s, core_rows=core_rows)

        # Core rows 0..7 untouched bit-for-bit
        np.testing.assert_array_equal(wi_1[:core_rows], w_in[:core_rows])
        # Exact canonical recovery of scrambled peripheral gauge
        np.testing.assert_allclose(wi_1, wi_2, atol=1e-12)
        np.testing.assert_allclose(wo_1, wo_2, atol=1e-12)
        np.testing.assert_allclose(bi_1, bi_2, atol=1e-12)

        # Functional isometry check on test inputs
        X = rng.normal(size=(20, d_in))
        gelu_fn = lambda z: z / (1.0 + np.exp(-1.702 * z))
        y_orig = gelu_fn(X @ w_in.T + b_in) @ w_out.T
        y_canon = gelu_fn(X @ wi_1.T + bi_1) @ wo_1.T
        np.testing.assert_allclose(y_orig, y_canon, atol=1e-13)

    def test_issue_51_reproducible_report_separates_rejected_candidate_from_committed_state(self) -> None:
        rep_noop = build_reproducible_plasm_report(
            seed=7,
            backend="cpu",
            effective_config={"dim": 64, "r_invariant": 120.0},
            iterations_requested=0,
            proposed_candidate_metrics=None,
            committed=False,
            committed_state_metrics={"mse": 0.42},
        )
        self.assertTrue(rep_noop["zero_iteration_noop"])
        self.assertFalse(rep_noop["committed"])

        with self.assertRaises(ValueError):
            build_reproducible_plasm_report(
                seed=7,
                backend="cpu",
                effective_config={"dim": 64},
                iterations_requested=0,
                proposed_candidate_metrics={"mse": 0.1},
                committed=True,
                committed_state_metrics={"mse": 0.1},
            )

        # Determinism check: identical inputs -> identical report_sha256
        rep_a = build_reproducible_plasm_report(
            seed=11,
            backend="cpu",
            effective_config={"dim": 64},
            iterations_requested=4,
            proposed_candidate_metrics={"mse": 0.19, "rejected_reason": "watermark_drift"},
            committed=False,
            committed_state_metrics={"mse": 0.42},
        )
        rep_b = build_reproducible_plasm_report(
            seed=11,
            backend="cpu",
            effective_config={"dim": 64},
            iterations_requested=4,
            proposed_candidate_metrics={"mse": 0.19, "rejected_reason": "watermark_drift"},
            committed=False,
            committed_state_metrics={"mse": 0.42},
        )
        self.assertEqual(rep_a["report_sha256"], rep_b["report_sha256"])
        self.assertNotEqual(rep_a["proposed_candidate"]["mse"], rep_a["committed_state"]["mse"])

    def test_optional_torch_tensor_roundtrip_if_installed(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("PyTorch not installed in current test environment")
        w_t = torch.ones((16, 8), dtype=torch.float32)
        w_exp, meta = expand_weights_orthogonal_mitosis(w_t, deficit_rows=4, core_rows=4)
        self.assertIsInstance(w_exp, torch.Tensor)
        self.assertEqual(tuple(w_exp.shape), (20, 8))
        self.assertEqual(meta["core_row_drift"], 0.0)


if __name__ == "__main__":
    unittest.main()