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

import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from weft.runtime.invariants import compute_royalty_split, verify_tension_bound

from .keccak256 import keccak256_hex

ZERO_ADDRESS: str = "0x" + "0" * 40
ZERO_BYTES32: str = "0x" + "0" * 64

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


def _is_zero_address(addr: object) -> bool:
    if type(addr) is not str:
        return True
    stripped = addr.strip()
    return stripped == "" or stripped.lower() == ZERO_ADDRESS


def _is_zero_hash(value: object) -> bool:
    if type(value) is not str:
        return True
    stripped = value.strip()
    return stripped == "" or stripped.lower() == ZERO_BYTES32


def _require_non_negative_int(value: object, error_message: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(error_message)
    return value


def _require_finite_non_negative_tension(tension: object) -> float:
    if type(tension) not in (int, float):
        raise ValueError("ASL_ERROR: INVALID_TENSION_TELEMETRY")
    try:
        t_val = float(tension)
    except OverflowError as exc:
        raise ValueError("ASL_ERROR: INVALID_TENSION_TELEMETRY") from exc
    if not math.isfinite(t_val) or t_val < 0.0:
        raise ValueError("ASL_ERROR: INVALID_TENSION_TELEMETRY")
    return t_val


def validate_rpc_endpoint(rpc_url: str, *, allow_remote: bool = False) -> str:
    if type(rpc_url) is not str:
        raise TypeError("rpc_url must be a str")
    if type(allow_remote) is not bool:
        raise TypeError("allow_remote must be a bool")
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
        if _is_zero_address(self.governor_core):
            raise ValueError("ASL_ERROR: INVALID_GOVERNOR_ADDRESS")
        if type(self.enforce_independent_adjudicator) is not bool:
            raise TypeError("enforce_independent_adjudicator must be a bool")
        if type(self.max_lineage_depth) is not int or self.max_lineage_depth < 1:
            raise ValueError("ASL_ERROR: INVALID_MAX_LINEAGE_DEPTH")
        _require_non_negative_int(
            self.critical_fraction_penalty, "ASL_ERROR: INVALID_PENALTY"
        )
        _require_non_negative_int(
            self.total_supply, "ASL_ERROR: INVALID_TOTAL_SUPPLY"
        )
        self.balances[self.governor_core] = self.total_supply

    def allocate_metabolic_seed(self, caller: str, recipient: str, amount: int) -> None:
        if caller != self.governor_core:
            raise PermissionError("ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED")
        if _is_zero_address(recipient):
            raise ValueError("ASL_ERROR: MINT_TO_ZERO_ADDRESS")
        _require_non_negative_int(amount, "ASL_ERROR: INVALID_AMOUNT")
        self.total_supply += amount
        self.balances[recipient] = self.balances.get(recipient, 0) + amount

    def set_harness_authorization(self, caller: str, harness: str, authorized: bool) -> None:
        if caller != self.governor_core:
            raise PermissionError("ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED")
        if _is_zero_address(harness):
            raise ValueError("ASL_ERROR: INVALID_HARNESS_ADDRESS")
        if type(authorized) is not bool:
            raise TypeError("authorized must be a bool")
        self.authorized_harnesses[harness] = authorized

    def register_genotype(self, creator: str, weight_hash: str, genotype_root: str) -> None:
        if _is_zero_address(creator):
            raise ValueError("ASL_ERROR: INVALID_CREATOR_ADDRESS")
        if _is_zero_hash(weight_hash):
            raise ValueError("ASL_ERROR: INVALID_WEIGHT_HASH")
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
        if _is_zero_address(splicer):
            raise ValueError("ASL_ERROR: INVALID_SPLICER_ADDRESS")
        if _is_zero_hash(child_hash) or _is_zero_hash(parent_hash):
            raise ValueError("ASL_ERROR: INVALID_WEIGHT_HASH")
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
                break
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
        if _is_zero_address(swarm):
            raise ValueError("ASL_ERROR: INVALID_SWARM_ADDRESS")
        if _is_zero_address(creator):
            raise ValueError("ASL_ERROR: INVALID_CREATOR_ADDRESS")
        if _is_zero_hash(weight_hash):
            raise ValueError("ASL_ERROR: INVALID_WEIGHT_HASH")
        _require_non_negative_int(value, "ASL_ERROR: INVALID_AMOUNT")
        if self.balances.get(swarm, 0) < value:
            raise ValueError("ASL_ERROR: SWARM_METABOLICALLY_STARVED")
        split = compute_royalty_split(value)
        creator_share, burn_share = split["weaver_wei"], split["upstream_wei"]
        self.balances[swarm] = self.balances.get(swarm, 0) - value
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
        if _is_zero_address(reporting_harness):
            raise ValueError("ASL_ERROR: INVALID_HARNESS_ADDRESS")
        if _is_zero_address(rogue_swarm):
            raise ValueError("ASL_ERROR: INVALID_SWARM_ADDRESS")
        if _is_zero_hash(weight_hash):
            raise ValueError("ASL_ERROR: INVALID_WEIGHT_HASH")
        t_val = _require_finite_non_negative_tension(tension_telemetry)
        if not verify_tension_bound(t_val)["excision_triggered"]:
            raise ValueError("ASL_ERROR: NORMAL_OPERATIONAL_HOMEOSTASIS_NO_INTERVENTION_REQUIRED")
        dispute_id = len(self.disputes) + 1
        rec = StructuralDisputeRecord(
            dispute_id=dispute_id,
            reporting_harness=reporting_harness,
            rogue_swarm=rogue_swarm,
            corrupted_weight_hash=weight_hash,
            tension_telemetry=t_val,
        )
        self.disputes[dispute_id] = rec
        self.event_log.append(
            {
                "event": "TensionAlertLog",
                "topic0": EVENT_TOPIC_HASHES["TensionAlertLog"],
                "disputeId": dispute_id,
                "harness": reporting_harness,
                "tension": t_val,
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
        if type(confirm_malicious) is not bool:
            raise TypeError("confirm_malicious must be a bool")
        if type(dispute_id) is not int or dispute_id not in self.disputes:
            raise ValueError("ASL_ERROR: DISPUTE_NONEXISTENT")
        dispute = self.disputes[dispute_id]
        if dispute.adjudicated:
            raise ValueError("ASL_ERROR: DISPUTE_ALREADY_ADJUDICATED")
        if self.enforce_independent_adjudicator and caller == dispute.reporting_harness:
            raise PermissionError("ASL_ERROR: REPORTER_CANNOT_SELF_ADJUDICATE")

        if confirm_malicious:
            creator = self.get_creator(dispute.corrupted_weight_hash)
            recipient = creator if creator else dispute.reporting_harness
            if self.balances.get(dispute.rogue_swarm, 0) < self.critical_fraction_penalty:
                raise ValueError("ASL_ERROR: INSUFFICIENT_SLASHING_BALANCE")
            # Commit all state mutations only after every revert condition passes (#44).
            self.balances[dispute.rogue_swarm] = (
                self.balances.get(dispute.rogue_swarm, 0) - self.critical_fraction_penalty
            )
            self.balances[recipient] = self.balances.get(recipient, 0) + self.critical_fraction_penalty
            dispute.adjudicated = True
            dispute.confirmed_malicious = True
            dispute.recipient = recipient
            self.event_log.append(
                {
                    "event": "DisputeAdjudicated",
                    "topic0": EVENT_TOPIC_HASHES["DisputeAdjudicated"],
                    "disputeId": dispute_id,
                    "confirmedMalicious": True,
                    "enforcementAction": recipient,
                }
            )
            return recipient

        dispute.adjudicated = True
        dispute.confirmed_malicious = False
        dispute.recipient = None
        self.event_log.append(
            {
                "event": "DisputeAdjudicated",
                "topic0": EVENT_TOPIC_HASHES["DisputeAdjudicated"],
                "disputeId": dispute_id,
                "confirmedMalicious": False,
                "enforcementAction": ZERO_ADDRESS,
            }
        )
        return None
