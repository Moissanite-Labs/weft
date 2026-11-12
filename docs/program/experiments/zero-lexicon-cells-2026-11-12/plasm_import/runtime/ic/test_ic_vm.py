#!/usr/bin/env python3
"""Unit tests for Codebase C3 (`weft/runtime/ic`) covering Issues #21 and #29."""

import unittest

from weft.runtime.ic import (
    FlatCombinatorVM,
    deserialize_graph_bcp,
    graph_state_sha256,
    run_combinator_self_test,
    serialize_graph_bcp,
)


class TestWeftICVM(unittest.TestCase):
    def test_pure_lafont_annihilation_rewires_neighbors(self) -> None:
        """Issue #21: CON-CON annihilation must splice external neighbor wires bidirectionally."""
        vm = FlatCombinatorVM(capacity=64)
        left_anchor = vm.alloc_node(vm.CON, p0=0, p1=-1, p2=-1)
        right_anchor = vm.alloc_node(vm.CON, p0=1, p1=-1, p2=-1)
        c_a = vm.alloc_node(vm.CON)
        c_b = vm.alloc_node(vm.CON)
        vm.connect_ports(c_a, 0, c_b, 0)
        vm.connect_ports(c_a, 1, left_anchor, 1)
        vm.connect_ports(c_b, 1, right_anchor, 1)
        vm.snapshot_initial_graph()

        op = vm.interact(c_a, c_b)
        self.assertIn("ANNIHILATE", op)
        # left_anchor.port[1] and right_anchor.port[1] are now directly wired to each other
        self.assertEqual(int(vm.ports[left_anchor, 1]), right_anchor)
        self.assertEqual(int(vm.ports[right_anchor, 1]), left_anchor)

    def test_dup_label_annihilation_vs_commutation(self) -> None:
        """Issue #21: DUP(L)-DUP(L) annihilates when labels match and commutes when L != M."""
        vm1 = FlatCombinatorVM(capacity=64)
        d1 = vm1.alloc_node(vm1.DUP, aux_tag=7)
        d2 = vm1.alloc_node(vm1.DUP, aux_tag=7)
        vm1.connect_ports(d1, 0, d2, 0)
        self.assertIn("ANNIHILATE", vm1.interact(d1, d2))

        vm2 = FlatCombinatorVM(capacity=64)
        d3 = vm2.alloc_node(vm2.DUP, aux_tag=7)
        d4 = vm2.alloc_node(vm2.DUP, aux_tag=9)
        vm2.connect_ports(d3, 0, d4, 0)
        self.assertIn("COMMUTE", vm2.interact(d3, d4))

    def test_extended_metabolic_valve_pass_and_excise(self) -> None:
        """Issue #21: VLV node passes under homeostatic tension and excises to FRC when tension > 85.0."""
        vm_ok = FlatCombinatorVM(capacity=64)
        anchor = vm_ok.alloc_node(vm_ok.CON)
        vlv = vm_ok.alloc_node(vm_ok.VLV)
        peer = vm_ok.alloc_node(vm_ok.CON)
        vm_ok.connect_ports(vlv, 0, peer, 0)
        vm_ok.connect_ports(vlv, 1, anchor, 1)
        op_ok = vm_ok.interact(vlv, peer, tension=24.0, metabolic_budget=50.0)
        self.assertEqual(op_ok, "VLV_PASS")
        self.assertEqual(int(vm_ok.ports[peer, 0]), anchor)

        vm_hi = FlatCombinatorVM(capacity=64)
        vlv_hi = vm_hi.alloc_node(vm_hi.VLV)
        peer_hi = vm_hi.alloc_node(vm_hi.CON)
        vm_hi.connect_ports(vlv_hi, 0, peer_hi, 0)
        op_hi = vm_hi.interact(vlv_hi, peer_hi, tension=92.5, metabolic_budget=50.0)
        self.assertEqual(op_hi, "VLV_EXCISE_TO_FRC")
        self.assertEqual(int(vm_hi.tags[vlv_hi]), vm_hi.FRC)

    def test_bcp_roundtrip_and_graph_committed_execution_hash(self) -> None:
        """
        Issues #21 & #29 falsifier:
        1. BCP serialization round-trips the full graph state byte-for-byte.
        2. Two distinct graphs undergoing identical `(op, a, b)` step tuples MUST
           produce different `trace_commitment_sha256` digests because the graph
           state itself is included in the commitment.
        """
        vm_a = FlatCombinatorVM(capacity=64)
        a0 = vm_a.alloc_node(vm_a.CON, p0=1, p1=10, p2=20)
        a1 = vm_a.alloc_node(vm_a.CON, p0=a0, p1=30, p2=40)
        vm_a.snapshot_initial_graph()
        blob_a = serialize_graph_bcp(vm_a)
        restored_a = deserialize_graph_bcp(blob_a)
        self.assertEqual(serialize_graph_bcp(restored_a), blob_a)
        self.assertEqual(graph_state_sha256(restored_a), graph_state_sha256(vm_a))

        # Graph B has the same node indices (0, 1) and tags (CON, CON), so interact(0, 1)
        # produces the exact same step log [{"step": 1, "op": "ANNIHILATE...", "a": 0, "b": 1}],
        # but different auxiliary port wiring (p1=99, p2=88).
        vm_b = FlatCombinatorVM(capacity=64)
        b0 = vm_b.alloc_node(vm_b.CON, p0=1, p1=99, p2=88)
        b1 = vm_b.alloc_node(vm_b.CON, p0=b0, p1=77, p2=66)
        vm_b.snapshot_initial_graph()

        vm_a.interact(a0, a1)
        vm_b.interact(b0, b1)

        rec_a = vm_a.compute_execution_commitment()
        rec_b = vm_b.compute_execution_commitment()
        self.assertEqual(rec_a["steps"], rec_b["steps"])
        self.assertNotEqual(rec_a["initial_graph_sha256"], rec_b["initial_graph_sha256"])
        self.assertNotEqual(rec_a["trace_commitment_sha256"], rec_b["trace_commitment_sha256"])

    def test_self_test_entrypoint(self) -> None:
        res = run_combinator_self_test()
        self.assertEqual(res["reductions_executed"], 3)
        self.assertTrue(res["trace_commitment_sha256"].startswith("0x"))


if __name__ == "__main__":
    unittest.main()
