"""Unit tests for causal synaptic routing, crushing quorum, and Farkas mitosis gates."""
from __future__ import annotations

from fractions import Fraction
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from causal_synaptic_gate import (  # noqa: E402
    certify_two_channel_mitosis_farkas,
    check_crushing_quorum_transition,
    normalize_shard_midranks,
    route_causal_synaptic_flow,
)


class TestCausalSynapticGate(unittest.TestCase):
    def test_parent_gated_routing_blocks_orphan_secondary_hop_and_certifies_cut(self) -> None:
        receptors = [(0, True), (1, True), (2, False), (3, True)]
        cert = route_causal_synaptic_flow(
            num_rungs=2,
            intact_receptors=receptors,
            primary_matches=[(1, 0), (2, 2)],
            secondary_hops=[(1, 1), (2, 3)],
            conserved_parent_rungs={1},
        )
        self.assertTrue(cert.primal_dual_verified)
        self.assertEqual(cert.max_flow, 2)
        self.assertEqual(cert.blocked_secondary_hops, 1)

    def test_crushing_quorum_detects_sticky_mirage(self) -> None:
        mirage = check_crushing_quorum_transition(2, 5, 2, quorum_req=9, aura_drain=3)
        self.assertTrue(mirage["sticky_would_admit"])
        self.assertTrue(mirage["crushed_by_gate_slam"])
        safe = check_crushing_quorum_transition(9, 0, 0, quorum_req=9, aura_drain=3)
        self.assertTrue(safe["turn_end_quorum_holds"])

    def test_floating_drift_impossibility_and_two_channel_farkas_cure(self) -> None:
        for k in range(1, 21):
            p = Fraction(k, 20)
            q_drift = (19 * p) / (18 * p + 1)
            q_c25 = (11 * p + Fraction(1, 4) * (1 - p)) / (10 * p + 1)
            self.assertLess(abs(q_drift - q_c25) / 2, Fraction(1, 60))
        cert = certify_two_channel_mitosis_farkas(Fraction(1, 20), Fraction(11, 1), Fraction(1, 4))
        self.assertEqual(cert["rs_invariant_eps_star"], Fraction(19, 240))
        self.assertTrue(cert["certified_above_ceiling"])

    def test_shard_midrank_normalization_is_affine_offset_invariant(self) -> None:
        raw = {"a": [0.1, 0.4, 0.9], "b": [10.2, 10.5, 11.0]}
        shifted = {"a": [-4.9, -4.6, -4.1], "b": [100.2, 100.5, 101.0]}
        self.assertEqual(normalize_shard_midranks(raw), normalize_shard_midranks(shifted))


if __name__ == "__main__":
    unittest.main()
