#!/usr/bin/env python3
"""Unit tests for Codebase C3 (`weft/runtime/ic`): rules, records and replay (#21, #29, #52, #66, #77)."""

import unittest

from weft.runtime.ic import (
    FlatCombinatorVM,
    deserialize_graph_bcp,
    graph_state_sha256,
    replay_execution,
    run_combinator_self_test,
    serialize_graph_bcp,
    verify_execution_record,
)


def pair(ta, tb, la=0, lb=0, capacity=64):
    vm = FlatCombinatorVM(capacity=capacity)
    a, b = vm.alloc_node(ta, aux_tag=la), vm.alloc_node(tb, aux_tag=lb)
    vm.connect_ports(a, 0, b, 0)
    return vm, a, b


class TestRules(unittest.TestCase):
    def test_annihilation_joins_aux_wires_port_to_port(self) -> None:
        vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.CON)
        left, right = vm.alloc_node(vm.CON), vm.alloc_node(vm.CON)
        vm.connect_ports(a, 1, left, 2)
        vm.connect_ports(b, 1, right, 1)
        self.assertIn("ANNIHILATE", vm.interact(a, b))
        self.assertEqual(vm.peer(left, 2), (right, 1))
        self.assertEqual(vm.peer(right, 1), (left, 2))
        vm.check_net()

    def test_dup_label_annihilation_vs_commutation(self) -> None:
        vm, a, b = pair(FlatCombinatorVM.DUP, FlatCombinatorVM.DUP, 7, 7)
        self.assertIn("ANNIHILATE", vm.interact(a, b))
        vm, a, b = pair(FlatCombinatorVM.DUP, FlatCombinatorVM.DUP, 7, 9)
        self.assertIn("COMMUTE", vm.interact(a, b))
        vm.check_net()

    def test_erasing_a_self_looped_dup_leaves_an_era_era_pair(self) -> None:
        """#66: the two new ERAs must be wired to each other, not to the freed DUP."""
        vm, era, dup = pair(FlatCombinatorVM.ERA, FlatCombinatorVM.DUP, 0, 1)
        vm.connect_ports(dup, 1, dup, 2)
        op = vm.interact(era, dup)
        e1, e2 = (int(x) for x in op[op.index("(") + 1:-1].split(","))
        self.assertEqual(vm.peer(e1, 0), (e2, 0))
        self.assertEqual(vm.active_pairs(), [(min(e1, e2), max(e1, e2))])
        vm.check_net()

    def test_commuting_a_self_looped_con_wires_its_copies_together(self) -> None:
        """#66: CON-DUP with the CON's aux ports looped together."""
        vm, con, dup = pair(FlatCombinatorVM.CON, FlatCombinatorVM.DUP, 0, 1)
        vm.connect_ports(con, 1, con, 2)
        op = vm.interact(con, dup)
        a1, a2, _b1, _b2 = (int(x) for x in op[op.index("(") + 1:-1].split(","))
        self.assertEqual(vm.peer(a1, 0), (a2, 0))
        vm.check_net()

    def test_multi_edges_are_kept_apart(self) -> None:
        """#52: crossed and parallel double wires are different nets and stay different."""
        def net(crossed):
            vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.CON)
            x, y = vm.alloc_node(vm.DUP, aux_tag=1), vm.alloc_node(vm.DUP, aux_tag=2)
            vm.connect_ports(x, 0, y, 0)
            vm.connect_ports(a, 1, x, 1)
            vm.connect_ports(a, 2, x, 2)
            vm.connect_ports(b, 1, y, 2 if crossed else 1)
            vm.connect_ports(b, 2, y, 1 if crossed else 2)
            return vm, a, b, x, y

        (p, pa, pb, px, py), (c, ca, cb, cx, cy) = net(False), net(True)
        self.assertNotEqual(serialize_graph_bcp(p), serialize_graph_bcp(c))
        p.interact(pa, pb)
        c.interact(ca, cb)
        self.assertEqual(p.peer(px, 1), (py, 1))
        self.assertEqual(c.peer(cx, 1), (cy, 2))

    def test_non_active_pairs_are_rejected_without_change(self) -> None:
        vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.DUP)
        c = vm.alloc_node(vm.CON)
        vm.connect_ports(c, 0, a, 1)  # principal to aux: not active
        before = serialize_graph_bcp(vm)
        for x, y in ((a, c), (c, a), (a, a), (a, 63), (b, c)):
            with self.subTest(pair=(x, y)):
                with self.assertRaises(ValueError):
                    vm.interact(x, y)
        self.assertEqual(serialize_graph_bcp(vm), before)
        self.assertEqual(vm.reductions, 0)
        self.assertIsNone(vm._initial_bcp)

    def test_frc_has_no_rule(self) -> None:
        vm, v, c = pair(FlatCombinatorVM.VLV, FlatCombinatorVM.CON)
        vm.interact(v, c, tension=92.5)
        era = vm.peer(c, 0)[0]
        self.assertEqual(int(vm.tags[era]), vm.ERA)
        self.assertEqual(int(vm.tags[v]), vm.FRC)
        self.assertIsNone(vm.peer(v, 0))
        self.assertEqual(vm.active_pairs(), [tuple(sorted((era, c)))])

    def test_valve_pass_hands_the_output_wire_to_the_peer(self) -> None:
        vm, v, c = pair(FlatCombinatorVM.VLV, FlatCombinatorVM.CON)
        anchor = vm.alloc_node(vm.CON)
        vm.connect_ports(v, 1, anchor, 1)
        self.assertEqual(vm.interact(v, c, tension=24.0, metabolic_budget=50.0), "VLV_PASS")
        self.assertEqual(vm.peer(c, 0), (anchor, 1))
        vm.check_net()

    def test_ports_beyond_arity_cannot_be_wired(self) -> None:
        vm = FlatCombinatorVM(capacity=8)
        e, c = vm.alloc_node(vm.ERA), vm.alloc_node(vm.CON)
        with self.assertRaises(ValueError):
            vm.connect_ports(e, 1, c, 1)


class TestRecords(unittest.TestCase):
    def test_graph_is_sealed_after_snapshot(self) -> None:
        vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.CON)
        vm.snapshot_initial_graph()
        for edit in (lambda: vm.alloc_node(vm.CON), lambda: vm.connect_ports(a, 1, b, 1), lambda: vm.free_node(a)):
            with self.assertRaises(RuntimeError):
                edit()

    def test_same_steps_on_different_graphs_commit_differently(self) -> None:
        """#21/#29: the commitment covers the graphs, not just the step list."""
        def run(crossed):
            vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.CON)
            vm.connect_ports(a, 1, b, 2 if crossed else 1)
            vm.interact(a, b)
            return vm.compute_execution_commitment()

        x, y = run(False), run(True)
        self.assertEqual(x["steps"], y["steps"])
        self.assertNotEqual(x["initial_graph_sha256"], y["initial_graph_sha256"])
        self.assertNotEqual(x["trace_commitment_sha256"], y["trace_commitment_sha256"])

    def test_self_test_reaches_normal_form_and_replays(self) -> None:
        res = run_combinator_self_test()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["replay"], "PASS")
        self.assertEqual(res["reductions_executed"], 6)
        self.assertTrue(res["trace_commitment_sha256"].startswith("0x"))

    def test_replay_verifier_catches_tampering(self) -> None:
        vm, a, b = pair(FlatCombinatorVM.CON, FlatCombinatorVM.DUP)
        e = vm.alloc_node(vm.ERA)
        vm.connect_ports(a, 1, e, 0)
        initial = vm.snapshot_initial_graph()
        vm.normalize()
        record = vm.compute_execution_commitment()
        self.assertEqual(verify_execution_record(initial, record)["status"], "PASS")

        bad_op = {**record, "steps": [dict(s) for s in record["steps"]]}
        bad_op["steps"][0]["op"] = "ANNIHILATE(tagA=1,tagB=2,label=0)"
        self.assertEqual(verify_execution_record(initial, bad_op)["status"], "FAIL")

        bad_pair = {**record, "steps": [dict(s) for s in record["steps"]]}
        bad_pair["steps"][0]["b"] = e
        self.assertEqual(verify_execution_record(initial, bad_pair)["status"], "FAIL")

        dropped = {**record, "steps": record["steps"][:-1]}
        self.assertEqual(verify_execution_record(initial, dropped)["status"], "FAIL")

        other = pair(FlatCombinatorVM.CON, FlatCombinatorVM.CON)[0]
        self.assertEqual(verify_execution_record(serialize_graph_bcp(other), record)["status"], "FAIL")

    def test_bcp_roundtrip_preserves_continuation(self) -> None:
        """A snapshot taken mid-run fixes every later step (lowest-free-slot allocation).

        This net never reaches normal form (the CON-DUP pair keeps copying
        itself), so both runs stop after the same 12 steps.
        """
        vm = FlatCombinatorVM(capacity=256)
        nodes = [vm.alloc_node(t, aux_tag=l) for t, l in ((1, 0), (2, 1), (1, 0), (2, 2), (0, 0), (2, 1))]
        vm.connect_ports(nodes[0], 0, nodes[1], 0)
        vm.connect_ports(nodes[2], 0, nodes[3], 0)
        vm.connect_ports(nodes[4], 0, nodes[5], 0)
        vm.connect_ports(nodes[0], 1, nodes[3], 1)
        vm.connect_ports(nodes[1], 2, nodes[2], 2)
        vm.interact(nodes[0], nodes[1])
        mid = serialize_graph_bcp(vm)
        resumed = deserialize_graph_bcp(mid)
        self.assertEqual(serialize_graph_bcp(resumed), mid)
        self.assertEqual(graph_state_sha256(resumed), graph_state_sha256(vm))
        self.assertEqual(vm.normalize(max_steps=12), 12)
        self.assertEqual(resumed.normalize(max_steps=12), 12)
        self.assertEqual(serialize_graph_bcp(resumed), serialize_graph_bcp(vm))
        self.assertEqual(replay_execution(mid, resumed.trace_log).trace_log, resumed.trace_log)


if __name__ == "__main__":
    unittest.main()
