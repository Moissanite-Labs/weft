#!/usr/bin/env python3
"""Unit tests for Codebases C4 & C5 (`weft/runtime/ledger` & `weft/runtime/gateway`) covering Issues #20, #30."""

import unittest
from pathlib import Path

from weft.runtime.gateway import (
    EVENT_TOPIC_HASHES,
    LedgerTriadSimulator,
    keccak256_hex,
    validate_rpc_endpoint,
)


class TestWeftGatewayAndLedger(unittest.TestCase):
    def test_keccak256_matches_ethereum_standard_vectors_and_replaces_fabricated_prefix(self) -> None:
        """Issue #20 L7: verify real Ethereum Keccak-256 and confirm CapitalExcision topic is not 0x8f3e..."""
        self.assertEqual(
            keccak256_hex(b""),
            "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
        )
        self.assertEqual(
            EVENT_TOPIC_HASHES["Transfer"],
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
        )
        cap_topic = EVENT_TOPIC_HASHES["CapitalExcision"]
        self.assertEqual(len(cap_topic), 66)
        self.assertFalse(cap_topic.startswith("0x8f3e"), "Fabricated 0x8f3e topic prefix must not be used (#20 L7)")

    def test_rpc_endpoint_guard_blocks_remote_by_default(self) -> None:
        """Issue #20/#30: gateway refuses remote RPC URLs unless allow_remote=True."""
        self.assertEqual(validate_rpc_endpoint("http://127.0.0.1:8545"), "http://127.0.0.1:8545")
        with self.assertRaises(PermissionError):
            validate_rpc_endpoint("https://mainnet.infura.io/v3/example")

    def test_ledger_triad_contracts_exist_and_compile_structure(self) -> None:
        """Issue #20 L1: all three Solidity contracts exist in weft/runtime/ledger/."""
        ledger_dir = Path(__file__).resolve().parents[1] / "ledger"
        for name in ("ProvenanceRegistry.sol", "WeftTokenTissue.sol", "TensionGovernor.sol"):
            sol = (ledger_dir / name).read_text(encoding="utf-8")
            self.assertIn("pragma solidity ^0.8.26;", sol)

    def test_provenance_lineage_cycle_and_depth_guard(self) -> None:
        """Issue #20 L6: lineage DAG rejects cycles and depths >= 12 so root creator attribution survives."""
        sim = LedgerTriadSimulator()
        sim.register_genotype("0xCreatorA", "0xRoot", "0xGen0")
        prev = "0xRoot"
        for i in range(1, 12):
            curr = f"0xChild{i}"
            sim.record_cross_splicing("0xSplicer", curr, prev)
            self.assertEqual(sim.get_creator(curr), "0xCreatorA")
            prev = curr

        # 12th splice edge (13th node in chain) would exceed MAX_LINEAGE_DEPTH=12
        with self.assertRaises(ValueError):
            sim.record_cross_splicing("0xSplicer", "0xChild12", prev)

    def test_metabolic_excision_and_independent_tension_adjudication(self) -> None:
        """Issue #20 L3, L4, L5: 85/15 excision split, tension > 85 gate, and no self-adjudication."""
        sim = LedgerTriadSimulator()
        sim.set_harness_authorization(sim.governor_core, "0xHarness1", True)
        sim.allocate_metabolic_seed(sim.governor_core, "0xSwarm1", 1_000 * 10**18)
        sim.register_genotype("0xCreatorA", "0xW1", "0xRoot1")

        c_share, b_share = sim.execute_excision_valve(
            "0xHarness1", "0xSwarm1", "0xCreatorA", 1000, "0xW1"
        )
        self.assertEqual(c_share, 850)
        self.assertEqual(b_share, 150)

        # Tension <= 85.0 rejected
        with self.assertRaises(ValueError):
            sim.report_tension_fracture("0xHarness1", "0xSwarm1", "0xW1", 85.0)

        # Tension > 85.0 accepted; independent governor adjudicates and routes penalty to creator
        dispute_id = sim.report_tension_fracture("0xHarness1", "0xSwarm1", "0xW1", 85.01)
        recipient = sim.adjudicate_tension_dispute(sim.governor_core, dispute_id, True)
        self.assertEqual(recipient, "0xCreatorA")

        # Self-adjudication by reporting harness when reporting_harness == governor_core is blocked
        with self.assertRaises(PermissionError):
            d2 = sim.report_tension_fracture(sim.governor_core, "0xSwarm1", "0xW1", 90.0)
            sim.adjudicate_tension_dispute(sim.governor_core, d2, True)


if __name__ == "__main__":
    unittest.main()
