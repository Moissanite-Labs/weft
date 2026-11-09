"""Storage and failure contracts for C3: BCP version 2 and failed reductions (#43, #52)."""

import copy
import math
import struct
import unittest
from unittest.mock import patch

import numpy as np

from weft.runtime.ic import FlatCombinatorVM, deserialize_graph_bcp, serialize_graph_bcp

OPEN = 0b111111  # all three ports open


def peers(p0=3, p1=3, p2=3):
    return p0 | (p1 << 2) | (p2 << 4)


def packet(capacity, records=(), *, flags=0, version=2):
    """Build wire fixtures independently of the serializer under test.

    A record is (slot, tag, peer_byte, label, p0, p1, p2).
    """
    header = struct.pack("<4sBBHI", b"WEFT", version, flags, len(records), capacity)
    return header + b"".join(struct.pack("<IBBhiii", *record) for record in records)


class TestBCPStorageContract(unittest.TestCase):
    def test_small_empty_full_and_sparse_arenas_roundtrip_exactly(self):
        fixtures = [
            packet(0),
            packet(1),
            packet(1, [(0, 0, OPEN, 0, -1, -1, -1)]),
            # CON.0 - DUP(7).0, everything else open
            packet(2, [(0, 1, peers(0), 0, 1, -1, -1), (1, 2, peers(0), 7, 0, -1, -1)]),
            # sparse slots, extreme labels, CON.1 - SUP.2
            packet(5, [(1, 1, peers(3, 2), -32768, -1, 4, -1), (4, 5, peers(3, 3, 1), 32767, -1, -1, 1)]),
            # a self-loop: CON aux 1 - aux 2
            packet(1, [(0, 1, peers(3, 2, 1), 0, -1, 0, 0)]),
        ]
        for blob in fixtures:
            with self.subTest(blob=blob.hex()):
                restored = deserialize_graph_bcp(blob)
                self.assertEqual(restored.capacity, struct.unpack_from("<I", blob, 8)[0])
                self.assertEqual(serialize_graph_bcp(restored), blob)

    def test_malformed_packets_are_rejected_before_arena_allocation(self):
        node = (0, 1, OPEN, 0, -1, -1, -1)
        fixtures = {
            "short_header": b"WEFT",
            "bad_magic": b"NOPE" + packet(2)[4:],
            "bad_version": b"WEFT\x03" + packet(2)[5:],
            "flags": packet(2, [node], flags=1),
            "count_exceeds_capacity": packet(0, [node]),
            "oversized_arena": packet(0xFFFFFFFF),
            "duplicate_slot": packet(2, [node, node]),
            "unordered_slots": packet(2, [(1, *node[1:]), node]),
            "slot_out_of_bounds": packet(2, [(2, *node[1:])]),
            "unknown_tag": packet(2, [(0, 6, *node[2:])]),
            "free_tag": packet(2, [(0, 255, *node[2:])]),
            "peer_byte_high_bits": packet(2, [(0, 1, OPEN | 0x40, 0, -1, -1, -1)]),
            "negative_port": packet(2, [(0, 1, OPEN, 0, -2, -1, -1)]),
            "port_at_capacity": packet(2, [(0, 1, peers(0), 0, 2, -1, -1)]),
            "half_open_port": packet(2, [(0, 1, peers(0), 0, -1, -1, -1)]),
            "wired_to_free_slot": packet(2, [(0, 1, peers(0), 0, 1, -1, -1)]),
            "not_reciprocal": packet(2, [(0, 1, peers(0), 0, 1, -1, -1), (1, 1, OPEN, 0, -1, -1, -1)]),
            "wrong_peer_port": packet(2, [(0, 1, peers(1), 0, 1, -1, -1), (1, 1, peers(0), 0, 0, -1, -1)]),
            "wired_to_itself": packet(1, [(0, 1, peers(3, 1), 0, -1, 0, -1)]),
            "beyond_arity": packet(2, [(0, 0, peers(3, 0), 0, -1, 1, -1), (1, 1, peers(1), 0, 0, -1, -1)]),
            "v1_reserved_byte": packet(2, [(0, 1, 1, 0, -1, -1, -1)], version=1),
            "v1_ambiguous_double_wire": packet(
                2, [(0, 1, 0, 0, -1, 1, 1), (1, 1, 0, 0, -1, 0, 0)], version=1),
            "truncated_record": packet(2, [node])[:-1],
            "extra_bytes": packet(2, [node]) + b"\0",
        }
        for name, blob in fixtures.items():
            with self.subTest(name=name), patch("weft.runtime.ic.ic_vm.FlatCombinatorVM") as arena:
                with self.assertRaises(ValueError):
                    deserialize_graph_bcp(blob)
                arena.assert_not_called()

    def test_version_1_decodes_where_peer_ports_are_unambiguous(self):
        # CON aux 2 points back at the CON itself, but no other port of it answers.
        v1 = packet(3, [(0, 1, 0, 0, 1, 2, 0), (1, 2, 0, 4, 0, -1, -1), (2, 0, 0, 0, 0, -1, -1)], version=1)
        with self.assertRaises(ValueError):
            deserialize_graph_bcp(v1)
        v1 = packet(3, [(0, 1, 0, 0, 1, 2, -1), (1, 2, 0, 4, 0, -1, -1), (2, 0, 0, 0, 0, -1, -1)], version=1)
        vm = deserialize_graph_bcp(v1)
        self.assertEqual(vm.peer(0, 1), (2, 0))
        self.assertEqual(vm.peer(1, 0), (0, 0))
        reencoded = serialize_graph_bcp(vm)
        self.assertEqual(reencoded[4], 2)
        self.assertEqual(serialize_graph_bcp(deserialize_graph_bcp(reencoded)), reencoded)
        # A self-loop is unambiguous in v1: the other aux port of the same node.
        vm = deserialize_graph_bcp(packet(1, [(0, 1, 0, 0, -1, 0, 0)], version=1))
        self.assertEqual(vm.peer(0, 1), (0, 2))

    def test_decode_resource_limit_is_explicit_and_configurable(self):
        blob = packet(4)
        with self.assertRaisesRegex(ValueError, "capacity"):
            deserialize_graph_bcp(blob, max_capacity=3)
        self.assertEqual(deserialize_graph_bcp(blob, max_capacity=4).capacity, 4)

    def test_serializer_rejects_malformed_storage(self):
        vm = FlatCombinatorVM(capacity=2)
        a = vm.alloc_node(vm.CON)
        vm.ports[a, 1] = 2
        vm.peer_ports[a, 1] = 0
        with self.assertRaisesRegex(ValueError, "port"):
            serialize_graph_bcp(vm)
        vm.ports[a, 1] = 1
        with self.assertRaisesRegex(ValueError, "free"):
            serialize_graph_bcp(vm)

    def test_serializer_rejects_unrepresentable_active_count(self):
        vm = FlatCombinatorVM(capacity=65536)
        vm.tags[:] = vm.CON
        with self.assertRaisesRegex(ValueError, "count"):
            serialize_graph_bcp(vm)


class TestReductionFailureContract(unittest.TestCase):
    @staticmethod
    def state(vm):
        return (
            vm.tags.copy(), vm.aux_tags.copy(), vm.ports.copy(), vm.peer_ports.copy(),
            vm.reductions, copy.deepcopy(vm.trace_log), vm._initial_bcp,
        )

    def assert_state_equal(self, vm, before):
        after = self.state(vm)
        for expected, actual in zip(before[:4], after[:4]):
            np.testing.assert_array_equal(actual, expected)
        self.assertEqual(after[4:], before[4:])

    def test_all_allocating_rules_preserve_state_on_exhaustion(self):
        cases = [
            (FlatCombinatorVM.CON, FlatCombinatorVM.DUP, 5, 22.0, 100.0),
            (FlatCombinatorVM.ERA, FlatCombinatorVM.CON, 3, 22.0, 100.0),
            (FlatCombinatorVM.VLV, FlatCombinatorVM.CON, 2, 92.5, 100.0),
            (FlatCombinatorVM.VLV, FlatCombinatorVM.CON, 2, 22.0, 0.0),
        ]
        for ta, tb, capacity, tension, budget in cases:
            for snapshot_first in (False, True):
                with self.subTest(tags=(ta, tb), capacity=capacity, budget=budget, snapshot=snapshot_first):
                    vm = FlatCombinatorVM(capacity=capacity)
                    a, b = vm.alloc_node(ta), vm.alloc_node(tb)
                    vm.connect_ports(a, 0, b, 0)
                    if snapshot_first:
                        vm.snapshot_initial_graph()
                    before = self.state(vm)
                    with self.assertRaises(MemoryError):
                        vm.interact(a, b, tension=tension, metabolic_budget=budget)
                    self.assert_state_equal(vm, before)

    def test_exact_available_capacity_commits_one_transition(self):
        vm = FlatCombinatorVM(capacity=6)
        a, b = vm.alloc_node(vm.CON), vm.alloc_node(vm.DUP)
        vm.connect_ports(a, 0, b, 0)
        self.assertTrue(vm.interact(a, b).startswith("COMMUTE"))
        self.assertEqual(vm.reductions, 1)
        self.assertEqual(len(vm.trace_log), 1)
        self.assertEqual(int(np.count_nonzero(vm.tags != vm.FREE)), 4)
        self.assertEqual(serialize_graph_bcp(deserialize_graph_bcp(serialize_graph_bcp(vm))), serialize_graph_bcp(vm))

    def test_exhaustion_preserves_an_existing_execution_history(self):
        vm = FlatCombinatorVM(capacity=6)
        first, second = vm.alloc_node(vm.CON), vm.alloc_node(vm.CON)
        vm.connect_ports(first, 0, second, 0)
        a, b = vm.alloc_node(vm.CON), vm.alloc_node(vm.DUP)
        vm.connect_ports(a, 0, b, 0)
        vm.alloc_node(vm.CON)
        vm.alloc_node(vm.CON)
        vm.interact(first, second)  # frees two slots; commutation needs four
        before = self.state(vm)
        with self.assertRaises(MemoryError):
            vm.interact(a, b)
        self.assert_state_equal(vm, before)

    def test_nonfinite_valve_inputs_are_rejected_without_a_transition(self):
        for field in ("tension", "metabolic_budget"):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(field=field, value=value):
                    vm = FlatCombinatorVM(capacity=4)
                    a, b = vm.alloc_node(vm.VLV), vm.alloc_node(vm.CON)
                    vm.connect_ports(a, 0, b, 0)
                    before = self.state(vm)
                    with self.assertRaises(ValueError):
                        vm.interact(a, b, **{field: value})
                    self.assert_state_equal(vm, before)

    def test_finite_valve_budget_and_tension_boundary_preserve_current_policy(self):
        for tension, budget, expected in (
            (85.0, 0.001, "VLV_PASS"),
            (85.000001, 1.0, "VLV_EXCISE_TO_FRC"),
            (22.0, 0.0, "VLV_EXCISE_TO_FRC"),
            (22.0, -1.0, "VLV_EXCISE_TO_FRC"),
        ):
            with self.subTest(tension=tension, budget=budget):
                vm = FlatCombinatorVM(capacity=3)
                a, b = vm.alloc_node(vm.VLV), vm.alloc_node(vm.CON)
                vm.connect_ports(a, 0, b, 0)
                self.assertEqual(vm.interact(a, b, tension=tension, metabolic_budget=budget), expected)
                self.assertEqual(vm.trace_log[-1]["tension"], tension)
                self.assertEqual(vm.trace_log[-1]["metabolic_budget"], budget)


if __name__ == "__main__":
    unittest.main()
