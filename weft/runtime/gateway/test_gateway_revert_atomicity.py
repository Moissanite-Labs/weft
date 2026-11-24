#!/usr/bin/env python3
"""Revert-atomicity and fail-closed state-invariant tests for LedgerTriadSimulator (Refs #44).

Verifies the mechanical revert repair separated from policy questions in #44:
  - Failed transactions leave all modeled state and event logs completely unchanged
    (matching EVM revert semantics).
  - Dispute adjudication validates balance, dispute existence, and boolean types
    before committing state or emitting DisputeAdjudicated events.
  - Non-finite, negative, boolean, or overflowing inputs fail closed across all
    state-mutating entry points without corrupting balances, supply, or logs.
  - Policy behavior explicitly held separate by #44 (85/15 integer rounding for
    amount 1 and direct-registration lookup precedence) remains unchanged.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from typing import Any, Callable, Tuple, Type

_REPO_ROOT = str(Path(__file__).resolve().parents[3])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from weft.runtime.gateway.gateway import (
    EVENT_TOPIC_HASHES,
    ZERO_ADDRESS,
    ZERO_BYTES32,
    LedgerTriadSimulator,
    validate_rpc_endpoint,
)


def _snapshot(sim: LedgerTriadSimulator) -> Tuple[Any, ...]:
    return (
        sim.total_supply,
        copy.deepcopy(sim.balances),
        copy.deepcopy(sim.authorized_harnesses),
        copy.deepcopy(sim.registries),
        copy.deepcopy(sim.lineage_dag),
        copy.deepcopy(sim.disputes),
        copy.deepcopy(sim.event_log),
    )


class TestGatewayRevertAtomicity(unittest.TestCase):
    def _assert_reverts_atomically(
        self,
        sim: LedgerTriadSimulator,
        exc_type: Type[BaseException],
        expected_substr: str,
        fn: Callable[[], Any],
    ) -> None:
        before = _snapshot(sim)
        with self.assertRaises(exc_type) as ctx:
            fn()
        self.assertIn(expected_substr, str(ctx.exception))
        self.assertEqual(_snapshot(sim), before)

    def test_adjudicate_insufficient_balance_reverts_atomically_and_allows_retry(self) -> None:
        """Issue #44 headline bug: insufficient slash balance must leave dispute unadjudicated."""
        sim = LedgerTriadSimulator()
        sim.register_genotype("0xCreatorA", "0xW1", "0xGen0")
        # Fund just 1 wei below critical_fraction_penalty to pin the exact boundary.
        sim.allocate_metabolic_seed(
            sim.governor_core, "0xRogue", sim.critical_fraction_penalty - 1
        )
        dispute_id = sim.report_tension_fracture("0xHarness1", "0xRogue", "0xW1", 92.5)

        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INSUFFICIENT_SLASHING_BALANCE",
            lambda: sim.adjudicate_tension_dispute(sim.governor_core, dispute_id, True),
        )
        self.assertFalse(sim.disputes[dispute_id].adjudicated)
        self.assertIsNone(sim.disputes[dispute_id].confirmed_malicious)
        self.assertIsNone(sim.disputes[dispute_id].recipient)

        # Top up by 1 wei so balance == critical_fraction_penalty; retry must now succeed.
        sim.allocate_metabolic_seed(sim.governor_core, "0xRogue", 1)
        recipient = sim.adjudicate_tension_dispute(sim.governor_core, dispute_id, True)
        self.assertEqual(recipient, "0xCreatorA")
        self.assertTrue(sim.disputes[dispute_id].adjudicated)
        self.assertTrue(sim.disputes[dispute_id].confirmed_malicious)
        self.assertEqual(sim.disputes[dispute_id].recipient, "0xCreatorA")
        self.assertEqual(sim.balances["0xRogue"], 0)
        self.assertEqual(sim.balances["0xCreatorA"], sim.critical_fraction_penalty)
        self.assertEqual(
            sim.event_log[-1],
            {
                "event": "DisputeAdjudicated",
                "topic0": EVENT_TOPIC_HASHES["DisputeAdjudicated"],
                "disputeId": dispute_id,
                "confirmedMalicious": True,
                "enforcementAction": "0xCreatorA",
            },
        )

        # Second adjudication on the same dispute must revert atomically.
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "DISPUTE_ALREADY_ADJUDICATED",
            lambda: sim.adjudicate_tension_dispute(sim.governor_core, dispute_id, False),
        )

    def test_adjudicate_dismissal_zero_penalty_and_reject_paths_atomic(self) -> None:
        sim = LedgerTriadSimulator()
        d1 = sim.report_tension_fracture("0xHarness1", "0xUnfundedRogue", "0xUnknownW", 88.0)

        # Reject non-governor caller, malformed confirm_malicious, nonexistent/bool dispute_id.
        self._assert_reverts_atomically(
            sim,
            PermissionError,
            "ONLY_TECHNICAL_WEAVER_ALLOWED",
            lambda: sim.adjudicate_tension_dispute("0xNotGovernor", d1, False),
        )
        for bad_flag in ("false", 1, 0, None):
            self._assert_reverts_atomically(
                sim,
                TypeError,
                "confirm_malicious must be a bool",
                lambda flag=bad_flag: sim.adjudicate_tension_dispute(sim.governor_core, d1, flag),  # type: ignore[arg-type]
            )
        for bad_id in (999, True, "1", 1.0):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "DISPUTE_NONEXISTENT",
                lambda did=bad_id: sim.adjudicate_tension_dispute(sim.governor_core, did, False),  # type: ignore[arg-type]
            )

        # Dismissal (confirm_malicious=False) succeeds even with 0 rogue balance and logs ZERO_ADDRESS.
        res = sim.adjudicate_tension_dispute(sim.governor_core, d1, False)
        self.assertIsNone(res)
        self.assertTrue(sim.disputes[d1].adjudicated)
        self.assertFalse(sim.disputes[d1].confirmed_malicious)
        self.assertIsNone(sim.disputes[d1].recipient)
        self.assertEqual(
            sim.event_log[-1],
            {
                "event": "DisputeAdjudicated",
                "topic0": EVENT_TOPIC_HASHES["DisputeAdjudicated"],
                "disputeId": d1,
                "confirmedMalicious": False,
                "enforcementAction": ZERO_ADDRESS,
            },
        )

        # Fallback payee routes to reporting_harness when weight has no registered creator.
        sim.allocate_metabolic_seed(sim.governor_core, "0xRogue2", sim.critical_fraction_penalty)
        d2 = sim.report_tension_fracture("0xHarness2", "0xRogue2", "0xUnregisteredW", 91.0)
        self.assertEqual(
            sim.adjudicate_tension_dispute(sim.governor_core, d2, True),
            "0xHarness2",
        )

        # Self-adjudication blocked when enforce_independent_adjudicator=True, permitted when False.
        d3 = sim.report_tension_fracture(sim.governor_core, "0xRogue3", "0xW3", 95.0)
        self._assert_reverts_atomically(
            sim,
            PermissionError,
            "REPORTER_CANNOT_SELF_ADJUDICATE",
            lambda: sim.adjudicate_tension_dispute(sim.governor_core, d3, False),
        )
        sim_non_indep = LedgerTriadSimulator(
            enforce_independent_adjudicator=False,
            critical_fraction_penalty=0,
        )
        d4 = sim_non_indep.report_tension_fracture(
            sim_non_indep.governor_core, "0xUnfundedSwarm", "0xW4", 90.0
        )
        self.assertEqual(
            sim_non_indep.adjudicate_tension_dispute(sim_non_indep.governor_core, d4, True),
            sim_non_indep.governor_core,
        )
        self.assertEqual(sim_non_indep.balances["0xUnfundedSwarm"], 0)

    def test_report_tension_fracture_rejects_nonfinite_negative_and_zero_inputs(self) -> None:
        sim = LedgerTriadSimulator()
        for bad_tension in (
            float("nan"),
            float("inf"),
            float("-inf"),
            -0.01,
            -100.0,
            True,
            False,
            "90.0",
            None,
            10**400,
        ):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_TENSION_TELEMETRY",
                lambda t=bad_tension: sim.report_tension_fracture("0xHarness1", "0xRogue", "0xW1", t),  # type: ignore[arg-type]
            )

        # Exact 0.0 and 85.0 pass telemetry validation and fail the homeostasis threshold.
        for safe_tension in (0.0, 85.0):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "NORMAL_OPERATIONAL_HOMEOSTASIS",
                lambda t=safe_tension: sim.report_tension_fracture("0xHarness1", "0xRogue", "0xW1", t),
            )

        # Zero / blank / non-string addresses and hashes fail closed.
        for bad_addr in ("", "   ", ZERO_ADDRESS, ZERO_ADDRESS.upper(), None, 123):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_HARNESS_ADDRESS",
                lambda a=bad_addr: sim.report_tension_fracture(a, "0xRogue", "0xW1", 90.0),  # type: ignore[arg-type]
            )
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_SWARM_ADDRESS",
                lambda a=bad_addr: sim.report_tension_fracture("0xHarness1", a, "0xW1", 90.0),  # type: ignore[arg-type]
            )
        for bad_hash in ("", "   ", ZERO_BYTES32, ZERO_BYTES32.upper(), None, 123):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_WEIGHT_HASH",
                lambda h=bad_hash: sim.report_tension_fracture("0xHarness1", "0xRogue", h, 90.0),  # type: ignore[arg-type]
            )

        # Exact integer tension > 85 is accepted.
        did = sim.report_tension_fracture("0xHarness1", "0xRogue", "0xW1", 86)
        self.assertEqual(did, 1)
        self.assertEqual(sim.disputes[1].tension_telemetry, 86.0)

    def test_mint_auth_provenance_splicing_and_excision_fail_closed_atomically(self) -> None:
        sim = LedgerTriadSimulator()

        # allocate_metabolic_seed
        self._assert_reverts_atomically(
            sim,
            PermissionError,
            "ONLY_TECHNICAL_WEAVER_ALLOWED",
            lambda: sim.allocate_metabolic_seed("0xOther", "0xSwarm1", 10),
        )
        for bad_addr in ("", ZERO_ADDRESS, None):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "MINT_TO_ZERO_ADDRESS",
                lambda a=bad_addr: sim.allocate_metabolic_seed(sim.governor_core, a, 10),  # type: ignore[arg-type]
            )
        for bad_amt in (-1, True, 1.5, "10"):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_AMOUNT",
                lambda v=bad_amt: sim.allocate_metabolic_seed(sim.governor_core, "0xSwarm1", v),  # type: ignore[arg-type]
            )
        # Exact 0 mint boundary succeeds without error.
        supply_before = sim.total_supply
        sim.allocate_metabolic_seed(sim.governor_core, "0xSwarm1", 0)
        self.assertEqual(sim.total_supply, supply_before)
        self.assertEqual(sim.balances["0xSwarm1"], 0)

        # set_harness_authorization
        self._assert_reverts_atomically(
            sim,
            PermissionError,
            "ONLY_TECHNICAL_WEAVER_ALLOWED",
            lambda: sim.set_harness_authorization("0xOther", "0xHarness1", True),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_HARNESS_ADDRESS",
            lambda: sim.set_harness_authorization(sim.governor_core, ZERO_ADDRESS, True),
        )
        for bad_bool in (1, "true", None):
            self._assert_reverts_atomically(
                sim,
                TypeError,
                "authorized must be a bool",
                lambda b=bad_bool: sim.set_harness_authorization(sim.governor_core, "0xHarness1", b),  # type: ignore[arg-type]
            )
        sim.set_harness_authorization(sim.governor_core, "0xHarness1", True)

        # register_genotype
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_CREATOR_ADDRESS",
            lambda: sim.register_genotype(ZERO_ADDRESS, "0xRoot", "0xGen0"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_WEIGHT_HASH",
            lambda: sim.register_genotype("0xCreatorA", ZERO_BYTES32, "0xGen0"),
        )
        sim.register_genotype("0xCreatorA", "0xRoot", "0xGen0")
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "GENOTYPE_ALREADY_REGISTERED",
            lambda: sim.register_genotype("0xCreatorB", "0xRoot", "0xGen0"),
        )

        # record_cross_splicing
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_SPLICER_ADDRESS",
            lambda: sim.record_cross_splicing(ZERO_ADDRESS, "0xChild1", "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_WEIGHT_HASH",
            lambda: sim.record_cross_splicing("0xSplicer", ZERO_BYTES32, "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_WEIGHT_HASH",
            lambda: sim.record_cross_splicing("0xSplicer", "0xChild1", ZERO_BYTES32),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "SELF_SPLICE_FORBIDDEN",
            lambda: sim.record_cross_splicing("0xSplicer", "0xRoot", "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "PARENT_GENOTYPE_NONEXISTENT",
            lambda: sim.record_cross_splicing("0xSplicer", "0xChild1", "0xMissingParent"),
        )
        sim.record_cross_splicing("0xSplicer", "0xChild1", "0xRoot")
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "CHILD_LINEAGE_ALREADY_RECORDED",
            lambda: sim.record_cross_splicing("0xSplicer", "0xChild1", "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "LINEAGE_CYCLE_DETECTED",
            lambda: sim.record_cross_splicing("0xSplicer", "0xRoot", "0xChild1"),
        )

        # execute_excision_valve
        self._assert_reverts_atomically(
            sim,
            PermissionError,
            "UNAUTHORIZED_HARNESS_NODE",
            lambda: sim.execute_excision_valve("0xOther", "0xSwarm1", "0xCreatorA", 10, "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_SWARM_ADDRESS",
            lambda: sim.execute_excision_valve("0xHarness1", ZERO_ADDRESS, "0xCreatorA", 10, "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_CREATOR_ADDRESS",
            lambda: sim.execute_excision_valve("0xHarness1", "0xSwarm1", ZERO_ADDRESS, 10, "0xRoot"),
        )
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "INVALID_WEIGHT_HASH",
            lambda: sim.execute_excision_valve("0xHarness1", "0xSwarm1", "0xCreatorA", 10, ZERO_BYTES32),
        )
        for bad_val in (-1, True, 1.5, "10"):
            self._assert_reverts_atomically(
                sim,
                ValueError,
                "INVALID_AMOUNT",
                lambda v=bad_val: sim.execute_excision_valve("0xHarness1", "0xSwarm1", "0xCreatorA", v, "0xRoot"),  # type: ignore[arg-type]
            )
        # Value == 0 on unfunded swarm succeeds cleanly (no KeyError).
        self.assertEqual(
            sim.execute_excision_valve("0xHarness1", "0xNeverFunded", "0xCreatorA", 0, "0xRoot"),
            (0, 0),
        )
        self.assertEqual(sim.balances["0xNeverFunded"], 0)

        sim.allocate_metabolic_seed(sim.governor_core, "0xSwarm1", 100)
        self._assert_reverts_atomically(
            sim,
            ValueError,
            "SWARM_METABOLICALLY_STARVED",
            lambda: sim.execute_excision_valve("0xHarness1", "0xSwarm1", "0xCreatorA", 101, "0xRoot"),
        )
        # Governor core is authorized directly; exact full-balance excision succeeds.
        c_share, b_share = sim.execute_excision_valve(
            sim.governor_core, "0xSwarm1", "0xCreatorA", 100, "0xRoot"
        )
        self.assertEqual((c_share, b_share), (85, 15))
        self.assertEqual(sim.balances["0xSwarm1"], 0)

    def test_constructor_and_rpc_endpoint_fail_closed_guards(self) -> None:
        with self.assertRaises(ValueError):
            LedgerTriadSimulator(governor_core=ZERO_ADDRESS)
        with self.assertRaises(TypeError):
            LedgerTriadSimulator(enforce_independent_adjudicator="true")  # type: ignore[arg-type]
        for bad_depth in (0, -1, True):
            with self.assertRaises(ValueError):
                LedgerTriadSimulator(max_lineage_depth=bad_depth)  # type: ignore[arg-type]
        for bad_penalty in (-1, True):
            with self.assertRaises(ValueError):
                LedgerTriadSimulator(critical_fraction_penalty=bad_penalty)  # type: ignore[arg-type]
        for bad_supply in (-1, True):
            with self.assertRaises(ValueError):
                LedgerTriadSimulator(total_supply=bad_supply)  # type: ignore[arg-type]

        # Exact minimal valid boundary constructor values succeed.
        minimal = LedgerTriadSimulator(
            max_lineage_depth=1, critical_fraction_penalty=0, total_supply=0
        )
        self.assertEqual(minimal.balances[minimal.governor_core], 0)

        # RPC endpoint strict type and localhost checks.
        with self.assertRaises(TypeError):
            validate_rpc_endpoint(123)  # type: ignore[arg-type]
        for bad_allow in ("false", 1, None):
            with self.assertRaises(TypeError):
                validate_rpc_endpoint("http://127.0.0.1:8545", allow_remote=bad_allow)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validate_rpc_endpoint("ftp://127.0.0.1:8545")
        self.assertEqual(
            validate_rpc_endpoint("https://rpc.example.org", allow_remote=True),
            "https://rpc.example.org",
        )

    def test_issue44_policy_boundaries_remain_untouched(self) -> None:
        """Pin #44 scope separation: economic rounding and lineage-vs-direct priority are unchanged."""
        sim = LedgerTriadSimulator()
        sim.allocate_metabolic_seed(sim.governor_core, "0xSwarm1", 1)
        sim.register_genotype("0xCreatorA", "0xRoot", "0xGen0")
        sim.record_cross_splicing("0xSplicer", "0xChild", "0xRoot")
        sim.register_genotype("0xCreatorB", "0xChild", "0xGenB")
        self.assertEqual(sim.get_creator("0xChild"), "0xCreatorB")
        self.assertEqual(
            sim.execute_excision_valve(sim.governor_core, "0xSwarm1", "0xCreatorA", 1, "0xRoot"),
            (1, 0),
        )


if __name__ == "__main__":
    unittest.main()
