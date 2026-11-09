#!/usr/bin/env python3
"""Differential test: the C3 reducer against Paper 2's reference semantics.

The oracle is `papers/02-checkable-computation/reference.py`, a port-indexed
model written independently of the VM. Paper 2 found the version 1 reducer
disagreed with it on loops through the active pair (#66) and on nets whose
storage was ambiguous (#52). Here random closed nets, including self-loops and
multiple wires between two agents, are reduced step for step in both, in a
random order of active pairs, and must stay identical under the slot mapping.
"""

import importlib.util
import random
import re
import sys
import unittest
from pathlib import Path

from weft.runtime.ic import FlatCombinatorVM, serialize_graph_bcp, deserialize_graph_bcp, verify_execution_record

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "papers" / "02-checkable-computation" / "reference.py"


def load_reference():
    spec = importlib.util.spec_from_file_location("weft_paper2_reference", REFERENCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look the module up while it loads
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(REFERENCE.exists(), "Paper 2 reference semantics not present")
class TestAgainstReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = load_reference()

    def to_vm(self, net):
        vm = FlatCombinatorVM(capacity=4096)
        slot = {a: vm.alloc_node(net.kind[a], aux_tag=net.label[a]) for a in sorted(net.kind)}
        for (a, i), (b, j) in net.wire.items():
            if (a, i) < (b, j):
                vm.connect_ports(slot[a], i, slot[b], j)
        return vm, slot

    def assert_same(self, net, vm, slot):
        self.assertEqual(sorted(slot[a] for a in net.kind), vm.live_nodes())
        for a in net.kind:
            self.assertEqual(int(vm.tags[slot[a]]), net.kind[a])
            self.assertEqual(int(vm.aux_tags[slot[a]]), net.label[a])
        for (a, i), (b, j) in net.wire.items():
            self.assertEqual(vm.peer(slot[a], i), (slot[b], j), f"wire ({a},{i})-({b},{j})")
        vm.check_net()

    def run_differential(self, net, rng, max_steps=40):
        vm, slot = self.to_vm(net)
        initial = vm.snapshot_initial_graph()
        for _ in range(max_steps):
            pairs = net.active_pairs()
            if not pairs:
                break
            a, b = rng.choice(pairs)
            if rng.random() < 0.5:
                a, b = b, a
            before = set(net.kind)
            net.reduce(a, b)
            op = vm.interact(slot[a], slot[b])
            new_agents = sorted(set(net.kind) - before)
            new_slots = [int(x) for x in re.findall(r"\d+", op.split("(", 1)[1])] if op.startswith(("COMMUTE", "ERA_PROP")) else []
            self.assertEqual(len(new_agents), len(new_slots), op)
            del slot[a], slot[b]
            slot.update(zip(new_agents, new_slots))
            self.assert_same(net, vm, slot)
        record = vm.compute_execution_commitment()
        self.assertEqual(verify_execution_record(initial, record)["status"], "PASS")
        final = serialize_graph_bcp(vm)
        self.assertEqual(serialize_graph_bcp(deserialize_graph_bcp(final)), final)
        return vm.reductions

    def test_loop_back_corpus(self):
        """The six loop-back cases from #66, built directly."""
        R = self.ref
        cases = []
        # ERA-DUP, DUP aux ports looped together
        n = R.Net(); e, d = n.add(R.ERA), n.add(R.DUP, 1)
        n.link((e, 0), (d, 0)); n.link((d, 1), (d, 2)); cases.append(n)
        # CON-DUP, CON aux looped
        n = R.Net(); c, d = n.add(R.CON), n.add(R.DUP, 1); x = n.add(R.ERA); y = n.add(R.ERA)
        n.link((c, 0), (d, 0)); n.link((c, 1), (c, 2)); n.link((d, 1), (x, 0)); n.link((d, 2), (y, 0)); cases.append(n)
        # CON-DUP, one aux wire across the pair
        n = R.Net(); c, d = n.add(R.CON), n.add(R.DUP, 1); x = n.add(R.ERA); y = n.add(R.ERA)
        n.link((c, 0), (d, 0)); n.link((c, 1), (d, 2)); n.link((c, 2), (x, 0)); n.link((d, 1), (y, 0)); cases.append(n)
        # CON-CON loops on both, parallel and crossed across
        for wiring in ([((0, 1), (0, 2)), ((1, 1), (1, 2))], [((0, 1), (1, 1)), ((0, 2), (1, 2))],
                       [((0, 1), (1, 2)), ((0, 2), (1, 1))]):
            n = R.Net(); a, b = n.add(R.CON), n.add(R.CON); n.link((a, 0), (b, 0))
            for p, q in wiring:
                n.link(p, q)
            cases.append(n)
        for i, net in enumerate(cases):
            with self.subTest(case=i):
                net.check()
                self.run_differential(net, random.Random(i))

    def test_random_nets_with_loops_and_multi_edges(self):
        rng = random.Random(20261109)
        steps = 0
        for trial in range(300):
            net = self.ref.random_closed_net(rng, rng.randint(2, 14), simple=False,
                                             kinds=(self.ref.CON, self.ref.DUP, self.ref.ERA, self.ref.SUP),
                                             weights=(4, 4, 2, 1))
            with self.subTest(trial=trial):
                steps += self.run_differential(net, random.Random(trial))
        self.assertGreater(steps, 1000)


if __name__ == "__main__":
    unittest.main()
