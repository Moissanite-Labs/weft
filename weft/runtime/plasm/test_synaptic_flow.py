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
        FractionDualCertificate,
        MinCutMitosisCertificate,
        _exact_nonneg_fraction,
        fraction_dual_certificate_digest,
        min_cut_certificate_digest,
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
        FractionDualCertificate,
        MinCutMitosisCertificate,
        _exact_nonneg_fraction,
        fraction_dual_certificate_digest,
        min_cut_certificate_digest,
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


def _reseal_min_cut(cert: "MinCutMitosisCertificate") -> "MinCutMitosisCertificate":
    """What a peer can do: change fields, then recompute a valid digest."""
    return replace(cert, sha256_digest=min_cut_certificate_digest(cert))


def _reseal_dual(cert: "FractionDualCertificate") -> "FractionDualCertificate":
    return replace(cert, sha256_digest=fraction_dual_certificate_digest(cert))


class TestPeerSuppliedMinCutCertificates(unittest.TestCase):
    """Review 5907258965 items 1, 3 and 5 on #170: peer-built certificates."""

    def test_overstated_flow_into_dead_end_is_rejected(self) -> None:
        # Demand 5, a capacity-5 source edge, corridor edges into five slots that
        # have no split edge and no edge to the sink. The true max flow is 0; the
        # peer claims 5 with no deficit and assigns all five slots.
        M, K = 5, 1
        snk = 1 + K + 2 * M
        edges = ((0, 1, 5),) + tuple((1, 1 + K + j, 1) for j in range(M))
        cut = (0,)
        forged = MinCutMitosisCertificate(
            total_neurons=M, core_rows_frozen=0, frozen_indices=(), eligible_indices=tuple(range(M)),
            plasmid_demands=(5,), total_demand=5, max_flow=5, deficit=0, requires_mitosis=False,
            assignments=(tuple(range(M)),), source_minimal_cut=cut, sink_minimal_cut=cut,
            cut_capacity_source_minimal=5, cut_capacity_sink_minimal=5,
            network_vertex_count=snk + 1, network_edges=edges, sha256_digest="",
        )
        res = verify_min_cut_mitosis_certificate(_reseal_min_cut(forged))
        self.assertEqual(res, {"ok": False, "reason": "network_missing_required_edge"})

    def test_added_cycle_changes_digest_and_is_rejected(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [2], core_rows=2)
        self.assertTrue(verify_min_cut_mitosis_certificate(base)["ok"])
        cyc = replace(base, network_edges=base.network_edges + ((1, 2, 1), (2, 1, 1)))
        self.assertNotEqual(min_cut_certificate_digest(cyc), base.sha256_digest)
        self.assertFalse(verify_min_cut_mitosis_certificate(cyc)["ok"])
        self.assertFalse(verify_min_cut_mitosis_certificate(_reseal_min_cut(cyc))["ok"])

    def test_negative_capacity_edge_cannot_fake_mitosis(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [2], core_rows=2)
        self.assertEqual(base.max_flow, 2)
        forged = replace(
            base,
            network_edges=base.network_edges + ((0, 2, -2),),
            max_flow=0, deficit=2, requires_mitosis=True, assignments=((),),
            source_minimal_cut=(0,), cut_capacity_source_minimal=0,
        )
        res = verify_min_cut_mitosis_certificate(_reseal_min_cut(forged))
        self.assertFalse(res["ok"], res)
        self.assertEqual(res["reason"], "negative_edge_capacity")

    def test_wrong_cut_with_matching_capacity_is_rejected(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [2], core_rows=2)
        # Swap the sink-minimal cut for the source-minimal one. Both have capacity
        # equal to the flow, but only one is the inclusion-maximal residual cut.
        self.assertNotEqual(base.source_minimal_cut, base.sink_minimal_cut)
        forged = replace(base, sink_minimal_cut=base.source_minimal_cut,
                         cut_capacity_sink_minimal=base.cut_capacity_source_minimal)
        res = verify_min_cut_mitosis_certificate(_reseal_min_cut(forged))
        self.assertEqual(res, {"ok": False, "reason": "cut_not_residual_min_cut"})

    def test_negative_core_rows_is_rejected(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [1], core_rows=0)
        forged = _reseal_min_cut(replace(base, core_rows_frozen=-5))
        res = verify_min_cut_mitosis_certificate(forged)
        self.assertEqual(res, {"ok": False, "reason": "core_rows_out_of_range"})

    def test_huge_core_rows_rejected_before_allocation(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [1], core_rows=0)
        res = verify_min_cut_mitosis_certificate(replace(base, core_rows_frozen=10 ** 12))
        self.assertEqual(res, {"ok": False, "reason": "core_rows_out_of_range"})

    def test_malformed_peer_values_return_reasons(self) -> None:
        base = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [2], core_rows=2)
        cases = {
            "dict": {"network_vertex_count": 3},
            "none": None,
            "demands_str": replace(base, plasmid_demands=("2",)),
            "edge_2_tuple": replace(base, network_edges=((0, 1),) + base.network_edges[1:]),
            "edge_cap_nan": replace(base, network_edges=((0, 1, float("nan")),) + base.network_edges[1:]),
            "core_rows_float": replace(base, core_rows_frozen=2.0),
            "cut_none": replace(base, source_minimal_cut=None),
            "assign_none": replace(base, assignments=None),
        }
        for name, cert in cases.items():
            with self.subTest(name=name):
                try:
                    res = verify_min_cut_mitosis_certificate(cert)  # type: ignore[arg-type]
                except Exception as exc:  # pragma: no cover - the failure being tested
                    self.fail(f"{name} raised {type(exc).__name__}: {exc}")
                self.assertFalse(res["ok"])
                self.assertIsInstance(res["reason"], str)

    def test_lock_packer_refuses_rejected_certificate(self) -> None:
        mc = allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 16), [2, 2])
        dc = certify_cost_partitioned_dual(10, [1, 1], [Fraction(1, 20)], Fraction(1, 10))
        with self.assertRaises(ValueError):
            pack_certificate_lock_record(replace(mc, max_flow=mc.max_flow + 1), dc)
        with self.assertRaises(ValueError):
            pack_certificate_lock_record(mc, replace(dc, remaining_budget_q="9/1"))


class TestBuilderInputValidation(unittest.TestCase):
    """Review 5907258965 items 3 and 5: builders reject bad input with ValueError."""

    def test_fractional_demands_rejected(self) -> None:
        with self.assertRaises(ValueError):
            allocate_disjoint_synaptic_corridors(np.linspace(0.1, 1.0, 8), [1.9, 2.2])

    def test_short_allowed_corridors_rejected(self) -> None:
        with self.assertRaises(ValueError):
            allocate_disjoint_synaptic_corridors(
                np.linspace(0.1, 1.0, 8), [1, 1], core_rows=0, allowed_corridors=[[0, 1]]
            )

    def test_long_path_runs_without_recursion_limit(self) -> None:
        n = sys.getrecursionlimit() + 500
        net = DinicSynapticFlowKernel(n)
        for u in range(n - 1):
            net.add_edge(u, u + 1, 1)
        self.assertEqual(net.solve_max_flow(0, n - 1), 1)

    def test_iterative_dinic_matches_reference_on_random_graphs(self) -> None:
        rng = np.random.default_rng(170)
        for _ in range(40):
            n = int(rng.integers(4, 12))
            edges = [(int(u), int(v), int(c)) for u, v, c in zip(
                rng.integers(0, n, 30), rng.integers(0, n, 30), rng.integers(0, 6, 30)) if u != v]
            net = DinicSynapticFlowKernel(n)
            for u, v, c in edges:
                net.add_edge(u, v, c)
            got = net.solve_max_flow(0, n - 1)
            # Reference: Edmonds-Karp on a dense capacity matrix.
            capm = [[0] * n for _ in range(n)]
            for u, v, c in edges:
                capm[u][v] += c
            total = 0
            while True:
                par = [-1] * n
                par[0] = 0
                q = [0]
                while q and par[n - 1] < 0:
                    u = q.pop(0)
                    for v in range(n):
                        if par[v] < 0 and capm[u][v] > 0:
                            par[v] = u
                            q.append(v)
                if par[n - 1] < 0:
                    break
                f, v = 10 ** 9, n - 1
                while v != 0:
                    f = min(f, capm[par[v]][v])
                    v = par[v]
                v = n - 1
                while v != 0:
                    capm[par[v]][v] -= f
                    capm[v][par[v]] += f
                    v = par[v]
                total += f
            self.assertEqual(got, total)
            s_min = net.extract_residual_min_cut(0, n - 1, "source_minimal")
            self.assertEqual(compute_cut_capacity(net.original_edges, set(s_min)), total)

    def test_short_bias_and_bad_seed_rejected(self) -> None:
        rng = np.random.default_rng(5)
        w_in, w_out = rng.normal(size=(8, 3)), rng.normal(size=(2, 8))
        with self.assertRaises(ValueError):
            canonicalize_peripheral_gauge(w_in, w_out, bias_in=np.zeros(3), core_rows=2)
        with self.assertRaises(ValueError):
            canonicalize_peripheral_gauge(w_in, w_out, core_rows=2, probe_seed=1.5)
        with self.assertRaises(ValueError):
            canonicalize_peripheral_gauge(w_in, w_out, core_rows=-1)

    def test_gauge_tie_collapses_to_one_canonical_form(self) -> None:
        # Two hidden units with identical incoming rows and biases and different
        # outgoing columns implement the same map after a swap.
        rng = np.random.default_rng(9)
        M, d_in, d_out, core = 6, 3, 2, 0
        w_in = rng.normal(size=(M, d_in))
        b_in = rng.normal(size=M)
        w_out = rng.normal(size=(d_out, M))
        w_in[1] = w_in[0]
        b_in[1] = b_in[0]
        perm = np.array([1, 0, 2, 3, 4, 5])
        a = canonicalize_peripheral_gauge(w_in, w_out, bias_in=b_in, core_rows=core)
        b = canonicalize_peripheral_gauge(w_in[perm], w_out[:, perm], bias_in=b_in[perm], core_rows=core)
        np.testing.assert_array_equal(a[0], b[0])
        np.testing.assert_array_equal(a[1], b[1])
        np.testing.assert_array_equal(a[2], b[2])


class TestFarkasAndFractionHardening(unittest.TestCase):
    """Review 5907258965 items 2, 3 and 4."""

    def test_feasible_system_with_unchecked_column_is_not_certified(self) -> None:
        # x0 - x1 <= -1 and -x0 + x1 + 7 x2 <= -1 is feasible at (0, 1, -1).
        A = [[1, -1], [-1, 1, 7]]
        b = [-1, -1]
        lam = [1, 1]
        with self.assertRaises(ValueError):
            certify_cost_partitioned_dual(5, [1], [0], 1, farkas_system=(A, b, lam))
        base = certify_cost_partitioned_dual(5, [1], [0], 1, farkas_system=([[1, -1], [-1, 1]], b, lam))
        self.assertTrue(verify_fraction_dual_certificate(base)["ok"])
        forged = _reseal_dual(replace(base, farkas_matrix_q=(("1/1", "-1/1"), ("-1/1", "1/1", "7/1"))))
        res = verify_fraction_dual_certificate(forged)
        self.assertEqual(res, {"ok": False, "reason": "farkas_dimension_mismatch"})

    def test_short_row_returns_reason(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            certify_cost_partitioned_dual(5, [1], [0], 1, farkas_system=([[1, -1], [1]], [-1, -1], [1, 1]))
        self.assertIn("farkas_dimension_mismatch", str(ctx.exception))
        base = certify_cost_partitioned_dual(5, [1], [0], 1, farkas_system=([[-1], [1]], [-2, 1], [1, 1]))
        forged = _reseal_dual(replace(base, farkas_matrix_q=(("-1/1", "0/1"), ("1/1",))))
        self.assertEqual(verify_fraction_dual_certificate(forged)["reason"], "farkas_dimension_mismatch")

    def test_malformed_fraction_inputs_return_reasons(self) -> None:
        base = certify_cost_partitioned_dual(5, [1], [0], 1)
        for name, cert in {
            "none_budget": replace(base, initial_budget_q=None),
            "dict": {"initial_budget_q": "5/1"},
            "none": None,
            "non_canonical": replace(base, initial_budget_q="10/2"),
            "costs_none": replace(base, step_costs_q=None),
        }.items():
            with self.subTest(name=name):
                try:
                    res = verify_fraction_dual_certificate(cert)  # type: ignore[arg-type]
                except Exception as exc:  # pragma: no cover
                    self.fail(f"{name} raised {type(exc).__name__}: {exc}")
                self.assertFalse(res["ok"])

    def test_exact_nonneg_fraction_rejects_negatives(self) -> None:
        for v in (-5, "-1/2", -0.25, Fraction(-1, 3)):
            with self.subTest(v=v):
                with self.assertRaises(ValueError):
                    _exact_nonneg_fraction(v)
        self.assertEqual(_exact_nonneg_fraction("3/4"), Fraction(3, 4))

    def test_committed_must_be_a_real_bool(self) -> None:
        kwargs = dict(seed=1, backend="cpu", effective_config={}, iterations_requested=2,
                      proposed_candidate_metrics=None, committed_state_metrics={"mse": 0.4})
        with self.assertRaises(ValueError):
            build_reproducible_plasm_report(committed="false", **kwargs)
        self.assertIs(build_reproducible_plasm_report(committed=False, **kwargs)["committed"], False)

    def test_report_rejects_nan_and_infinity(self) -> None:
        for bad in (float("nan"), float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    build_reproducible_plasm_report(
                        seed=1, backend="cpu", effective_config={}, iterations_requested=1,
                        proposed_candidate_metrics={"mse": bad}, committed=False,
                        committed_state_metrics={"mse": 0.4},
                    )


if __name__ == "__main__":
    unittest.main()
