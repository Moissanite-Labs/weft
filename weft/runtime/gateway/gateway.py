#!/usr/bin/env python3
"""
Weft Off-Chain Gateway & Local Ledger Simulator (Codebase C5 — Interface I5)
============================================================================
Bridges the bare-metal / Python runtime (`C1`, `C2`, `C6`) to the three-contract
provenance and metabolic ledger triad (`C4`: `ProvenanceRegistry.sol`,
`WeftTokenTissue.sol`, `TensionGovernor.sol`).

Fixes Issue #20 & #30:
  - Computes real Ethereum ABI event topic hashes via `keccak256` (`keccak256.py`),
    replacing the transcript's fabricated `0x8f3e...` prefix in `weft/more.md`.
  - Enforces localhost-only default RPC endpoints (`http://127.0.0.1:8545`) unless
    `allow_remote=True` is explicitly provided.
  - Reads signing keys exclusively from environment variables (`WEFT_GATEWAY_PRIVATE_KEY`),
    never from hardcoded source literals.
  - Provides a deterministic in-process triad state machine (`LedgerTriadSimulator`)
    matching the Solidity contracts for offline CI verification.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from weft.runtime.invariants import compute_royalty_split, verify_tension_bound

from .keccak256 import keccak256_hex

EVENT_SIGNATURES: Dict[str, str] = {
    "ProvenanceRegistered": "ProvenanceRegistered(bytes32,address,bytes32)",
    "LineageSpliced": "LineageSpliced(bytes32,bytes32,address)",
    "CapitalExcision": "CapitalExcision(address,address,uint256,bytes32)",
    "TensionAlertLog": "TensionAlertLog(uint256,address,uint256,bytes32)",
    "DisputeAdjudicated": "DisputeAdjudicated(uint256,bool,address)",
    "Transfer": "Transfer(address,address,uint256)",
}

EVENT_TOPIC_HASHES: Dict[str, str] = {
    name: keccak256_hex(sig) for name, sig in EVENT_SIGNATURES.items()
}


def validate_rpc_endpoint(rpc_url: str, *, allow_remote: bool = False) -> str:
    parsed = urlparse(rpc_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported RPC scheme: {parsed.scheme}")
    host = (parsed.hostname or "").lower()
    if not allow_remote and host not in ("127.0.0.1", "localhost", "::1"):
        raise PermissionError(
            f"Remote RPC endpoint '{rpc_url}' refused without allow_remote=True (#20/#30)"
        )
    return rpc_url


def load_gateway_private_key(env_var: str = "WEFT_GATEWAY_PRIVATE_KEY") -> Optional[str]:
    val = os.environ.get(env_var, "").strip()
    return val if val else None


@dataclass
class StructuralDisputeRecord:
    dispute_id: int
    reporting_harness: str
    rogue_swarm: str
    corrupted_weight_hash: str
    tension_telemetry: float
    adjudicated: bool = False
    confirmed_malicious: Optional[bool] = None
    recipient: Optional[str] = None


@dataclass
class LedgerTriadSimulator:
    """
    Deterministic reference model of `ProvenanceRegistry.sol`, `WeftTokenTissue.sol`,
    and `TensionGovernor.sol` for offline conformance testing (#20, #30).
    """

    governor_core: str = "0x1111111111111111111111111111111111111111"
    enforce_independent_adjudicator: bool = True
    max_lineage_depth: int = 12
    critical_fraction_penalty: int = 500 * 10**18
    total_supply: int = field(default=21_000_000 * 10**18)
    balances: Dict[str, int] = field(default_factory=dict)
    authorized_harnesses: Dict[str, bool] = field(default_factory=dict)
    registries: Dict[str, str] = field(default_factory=dict)
    lineage_dag: Dict[str, str] = field(default_factory=dict)
    disputes: Dict[int, StructuralDisputeRecord] = field(default_factory=dict)
    event_log: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.balances[self.governor_core] = self.total_supply

    def allocate_metabolic_seed(self, caller: str, recipient: str, amount: int) -> None:
        if caller != self.governor_core:
            raise PermissionError("ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED")
        self.total_supply += amount
        self.balances[recipient] = self.balances.get(recipient, 0) + amount

    def set_harness_authorization(self, caller: str, harness: str, authorized: bool) -> None:
        if caller != self.governor_core:
            raise PermissionError("ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED")
        self.authorized_harnesses[harness] = authorized

    def register_genotype(self, creator: str, weight_hash: str, genotype_root: str) -> None:
        if weight_hash in self.registries:
            raise ValueError("ASL_ERROR: GENOTYPE_ALREADY_REGISTERED")
        self.registries[weight_hash] = creator
        self.event_log.append(
            {
                "event": "ProvenanceRegistered",
                "topic0": EVENT_TOPIC_HASHES["ProvenanceRegistered"],
                "weightHash": weight_hash,
                "creator": creator,
                "baseGenotypeRoot": genotype_root,
            }
        )

    def record_cross_splicing(self, splicer: str, child_hash: str, parent_hash: str) -> None:
        if child_hash == parent_hash:
            raise ValueError("ASL_ERROR: SELF_SPLICE_FORBIDDEN")
        if parent_hash not in self.registries and parent_hash not in self.lineage_dag:
            raise ValueError("ASL_ERROR: PARENT_GENOTYPE_NONEXISTENT")
        if child_hash in self.lineage_dag:
            raise ValueError("ASL_ERROR: CHILD_LINEAGE_ALREADY_RECORDED")

        cursor: Optional[str] = parent_hash
        depth = 1
        while cursor:
            if cursor == child_hash:
                raise ValueError("ASL_ERROR: LINEAGE_CYCLE_DETECTED")
            if depth >= self.max_lineage_depth:
                raise ValueError("ASL_ERROR: MAX_LINEAGE_DEPTH_EXCEEDED")
            cursor = self.lineage_dag.get(cursor)
            depth += 1

        self.lineage_dag[child_hash] = parent_hash
        self.event_log.append(
            {
                "event": "LineageSpliced",
                "topic0": EVENT_TOPIC_HASHES["LineageSpliced"],
                "childHash": child_hash,
                "parentHash": parent_hash,
                "splicer": splicer,
            }
        )

    def get_creator(self, weight_hash: str) -> Optional[str]:
        cursor: Optional[str] = weight_hash
        for _ in range(self.max_lineage_depth):
            if not cursor:
                return None
            if cursor in self.registries:
                return self.registries[cursor]
            cursor = self.lineage_dag.get(cursor)
        return None

    def execute_excision_valve(
        self,
        caller: str,
        swarm: str,
        creator: str,
        value: int,
        weight_hash: str,
    ) -> Tuple[int, int]:
        if caller != self.governor_core and not self.authorized_harnesses.get(caller, False):
            raise PermissionError("ASL_ERROR: UNAUTHORIZED_HARNESS_NODE")
        if self.balances.get(swarm, 0) < value:
            raise ValueError("ASL_ERROR: SWARM_METABOLICALLY_STARVED")
        split = compute_royalty_split(value)
        creator_share, burn_share = split["weaver_wei"], split["upstream_wei"]
        self.balances[swarm] -= value
        self.balances[creator] = self.balances.get(creator, 0) + creator_share
        self.total_supply -= burn_share
        self.event_log.append(
            {
                "event": "CapitalExcision",
                "topic0": EVENT_TOPIC_HASHES["CapitalExcision"],
                "swarm": swarm,
                "creator": creator,
                "value": value,
                "weightHash": weight_hash,
                "creatorShare": creator_share,
                "burnShare": burn_share,
            }
        )
        return creator_share, burn_share

    def report_tension_fracture(
        self,
        reporting_harness: str,
        rogue_swarm: str,
        weight_hash: str,
        tension_telemetry: float,
    ) -> int:
        if not verify_tension_bound(tension_telemetry)["excision_triggered"]:
            raise ValueError("ASL_ERROR: NORMAL_OPERATIONAL_HOMEOSTASIS_NO_INTERVENTION_REQUIRED")
        dispute_id = len(self.disputes) + 1
        rec = StructuralDisputeRecord(
            dispute_id=dispute_id,
            reporting_harness=reporting_harness,
            rogue_swarm=rogue_swarm,
            corrupted_weight_hash=weight_hash,
            tension_telemetry=tension_telemetry,
        )
        self.disputes[dispute_id] = rec
        self.event_log.append(
            {
                "event": "TensionAlertLog",
                "topic0": EVENT_TOPIC_HASHES["TensionAlertLog"],
                "disputeId": dispute_id,
                "harness": reporting_harness,
                "tension": tension_telemetry,
                "weightHash": weight_hash,
            }
        )
        return dispute_id

    def adjudicate_tension_dispute(
        self,
        caller: str,
        dispute_id: int,
        confirm_malicious: bool,
    ) -> Optional[str]:
        if caller != self.governor_core:
            raise PermissionError("ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED")
        dispute = self.disputes[dispute_id]
        if dispute.adjudicated:
            raise ValueError("ASL_ERROR: DISPUTE_ALREADY_ADJUDICATED")
        if self.enforce_independent_adjudicator and caller == dispute.reporting_harness:
            raise PermissionError("ASL_ERROR: REPORTER_CANNOT_SELF_ADJUDICATE")

        dispute.adjudicated = True
        dispute.confirmed_malicious = confirm_malicious
        if confirm_malicious:
            creator = self.get_creator(dispute.corrupted_weight_hash)
            recipient = creator if creator else dispute.reporting_harness
            if self.balances.get(dispute.rogue_swarm, 0) < self.critical_fraction_penalty:
                raise ValueError("ASL_ERROR: INSUFFICIENT_SLASHING_BALANCE")
            self.balances[dispute.rogue_swarm] -= self.critical_fraction_penalty
            self.balances[recipient] = self.balances.get(recipient, 0) + self.critical_fraction_penalty
            dispute.recipient = recipient
            return recipient
        return None
