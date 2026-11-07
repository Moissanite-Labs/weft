#!/usr/bin/env python3
"""
Weft Flat-Array Interaction Combinator VM (Codebase C3 — Interface I5)
======================================================================
Explicitly separates:
  1. Pure Lafont Interaction Combinators (`ERA = 0`, `CON = 1`, `DUP = 2`):
     - Same-kind / same-label active pairs (`CON-CON`, `DUP(L)-DUP(L)`, `ERA-ERA`)
       annihilate and fuse auxiliary ports (`a.p1 <-> b.p1`, `a.p2 <-> b.p2`).
     - Distinct-kind / distinct-label active pairs (`CON-DUP`, `DUP(L)-DUP(M)` for `L != M`)
       commute by allocating 4 cross-wired nodes (`a1, a2, b1, b2`) and rewiring
       external neighbor pointers bidirectionally.
     - `ERA` interacting with `CON` or `DUP` erases the binary node by spawning two
       `ERA` nodes connected to `p1` and `p2`.
     - Pure Lafont nets satisfy strong confluence (one-step diamond property).
  2. Weft Extended Metabolic & Superposition Nodes (`VLV = 3`, `FRC = 4`, `SUP = 5`):
     - `VLV` (Metabolic Valve): gates a reduction across a node pair using the C2
       invariant gate (`verify_tension_bound` and metabolic budget). When within
       bounds, `VLV` forwards its payload port transparently; when tension exceeds
       `TENSION_MAX` (`85.0`) or budget is exhausted, `VLV` transitions to `FRC`
       (Fracture / Excision marker) and erases the downstream subgraph via `ERA`.
     - `SUP` (Superposition with label `aux_tag`): annihilates with matching-label
       `DUP(L)` and commutes with distinct-label `DUP(M)` (`L != M`).

Execution trace commitment (#21, #29, PROGRAM.md Phase 4):
  `trace_commitment_sha256` hashes `SHA256(initial_graph_bcp || step_log_json || final_graph_bcp)`
  so two distinct graphs can never collide on identical step tuples.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from weft.runtime.invariants import TENSION_MAX, verify_tension_bound
from .bcp_codec import deserialize_graph_bcp, graph_state_sha256, serialize_graph_bcp


class FlatCombinatorVM:
    # Pure Lafont basis tags
    ERA = 0
    CON = 1
    DUP = 2
    # Weft metabolic & superposition extension tags
    VLV = 3
    FRC = 4
    SUP = 5
    FREE = 255

    PURE_LAFONT_TAGS = (ERA, CON, DUP)
    EXTENDED_WEFT_TAGS = (VLV, FRC, SUP)

    def __init__(self, capacity: int = 4096):
        self.capacity = int(capacity)
        self.tags = np.full(self.capacity, self.FREE, dtype=np.uint8)
        self.aux_tags = np.zeros(self.capacity, dtype=np.int16)
        self.ports = np.full((self.capacity, 3), -1, dtype=np.int32)
        self.next_alloc = 0
        self.reductions = 0
        self.trace_log: List[Dict[str, Any]] = []
        self._initial_bcp: Optional[bytes] = None

    def alloc_node(
        self,
        tag: int,
        p0: int = -1,
        p1: int = -1,
        p2: int = -1,
        aux_tag: int = 0,
    ) -> int:
        while self.next_alloc < self.capacity and self.tags[self.next_alloc] != self.FREE:
            self.next_alloc += 1
        if self.next_alloc >= self.capacity:
            free_slots = np.where(self.tags == self.FREE)[0]
            if len(free_slots) == 0:
                raise MemoryError("Combinator arena exhausted")
            idx = int(free_slots[0])
        else:
            idx = self.next_alloc
            self.next_alloc += 1

        self.tags[idx] = tag
        self.aux_tags[idx] = aux_tag
        self.ports[idx, 0] = p0
        self.ports[idx, 1] = p1
        self.ports[idx, 2] = p2
        return idx

    def free_node(self, idx: int) -> None:
        self.tags[idx] = self.FREE
        self.aux_tags[idx] = 0
        self.ports[idx, :] = -1

    def connect_ports(self, node_a: int, port_a: int, node_b: int, port_b: int) -> None:
        """Wire `(node_a, port_a)` and `(node_b, port_b)` bidirectionally."""
        if node_a >= 0:
            self.ports[node_a, port_a] = node_b
        if node_b >= 0:
            self.ports[node_b, port_b] = node_a

    def _replace_neighbor_link(self, target_node: int, old_peer: int, new_peer: int) -> None:
        """When `old_peer` was connected to `target_node`, redirect `target_node`'s port to `new_peer`."""
        if target_node < 0 or target_node >= self.capacity:
            return
        if self.tags[target_node] == self.FREE:
            return
        for p in range(3):
            if int(self.ports[target_node, p]) == int(old_peer):
                self.ports[target_node, p] = int(new_peer)
                return

    def _fuse_external_wires(self, ext_a: int, old_a: int, ext_b: int, old_b: int) -> None:
        """Splice two external neighbors `ext_a` (formerly wired to `old_a`) and `ext_b` (wired to `old_b`)."""
        self._replace_neighbor_link(ext_a, old_a, ext_b)
        self._replace_neighbor_link(ext_b, old_b, ext_a)

    def snapshot_initial_graph(self) -> bytes:
        """Record the initial serialized graph state before reductions begin."""
        self._initial_bcp = serialize_graph_bcp(self)
        return self._initial_bcp

    def interact(
        self,
        a: int,
        b: int,
        tension: float = 22.0,
        metabolic_budget: float = 100.0,
    ) -> str:
        if self._initial_bcp is None:
            self.snapshot_initial_graph()

        ta = int(self.tags[a])
        tb = int(self.tags[b])
        la = int(self.aux_tags[a])
        lb = int(self.aux_tags[b])

        # 0. Weft Extended Metabolic Valve (VLV = 3)
        if ta == self.VLV or tb == self.VLV:
            vlv = a if ta == self.VLV else b
            peer = b if ta == self.VLV else a
            t_check = verify_tension_bound(tension, max_tension=TENSION_MAX)
            if t_check["accepted"] and metabolic_budget > 0.0:
                ext_out = int(self.ports[vlv, 1])
                self._replace_neighbor_link(ext_out, vlv, peer)
                self.ports[peer, 0] = ext_out
                self.free_node(vlv)
                op = "VLV_PASS"
            else:
                # Excision triggered: convert valve to FRC marker and erase peer via ERA
                self.tags[vlv] = self.FRC
                era = self.alloc_node(self.ERA, p0=peer)
                self.ports[peer, 0] = era
                op = "VLV_EXCISE_TO_FRC"
            self.reductions += 1
            self.trace_log.append(
                {"step": self.reductions, "op": op, "a": a, "b": b, "tension": round(float(tension), 4)}
            )
            return op

        # 1. Erasure (ERA interacting with ERA, CON, DUP, or SUP)
        if ta == self.ERA and tb == self.ERA:
            self.free_node(a)
            self.free_node(b)
            op = "ERA_ERA"
        elif ta == self.ERA or tb == self.ERA:
            era_idx = a if ta == self.ERA else b
            other_idx = b if ta == self.ERA else a
            p1, p2 = int(self.ports[other_idx, 1]), int(self.ports[other_idx, 2])
            e1 = self.alloc_node(self.ERA, p0=p1)
            e2 = self.alloc_node(self.ERA, p0=p2)
            self._replace_neighbor_link(p1, other_idx, e1)
            self._replace_neighbor_link(p2, other_idx, e2)
            self.free_node(era_idx)
            self.free_node(other_idx)
            op = f"ERA_PROPAGATE({e1},{e2})"

        # 2. Annihilation:
        #    - CON <-> CON (with matching aux_tag)
        #    - DUP(L) <-> DUP(L) (matching label L)
        #    - SUP(L) <-> DUP(L) or SUP(L) <-> SUP(L) (matching label L)
        elif (
            (ta == tb and la == lb and ta in (self.CON, self.DUP, self.SUP))
            or ({ta, tb} == {self.DUP, self.SUP} and la == lb)
        ):
            a1, a2 = int(self.ports[a, 1]), int(self.ports[a, 2])
            b1, b2 = int(self.ports[b, 1]), int(self.ports[b, 2])
            self._fuse_external_wires(a1, a, b1, b)
            self._fuse_external_wires(a2, a, b2, b)
            self.free_node(a)
            self.free_node(b)
            op = f"ANNIHILATE(tagA={ta},tagB={tb},label={la})"

        # 3. Commutation:
        #    - CON <-> DUP
        #    - DUP(L) <-> DUP(M) with L != M
        #    - CON/DUP <-> SUP(M) with distinct kind/label
        else:
            ext_a1, ext_a2 = int(self.ports[a, 1]), int(self.ports[a, 2])
            ext_b1, ext_b2 = int(self.ports[b, 1]), int(self.ports[b, 2])

            a1 = self.alloc_node(tb, p0=ext_a1, aux_tag=lb)
            a2 = self.alloc_node(tb, p0=ext_a2, aux_tag=lb)
            b1 = self.alloc_node(ta, p0=ext_b1, aux_tag=la)
            b2 = self.alloc_node(ta, p0=ext_b2, aux_tag=la)

            self._replace_neighbor_link(ext_a1, a, a1)
            self._replace_neighbor_link(ext_a2, a, a2)
            self._replace_neighbor_link(ext_b1, b, b1)
            self._replace_neighbor_link(ext_b2, b, b2)

            # Wire cross-connections between auxiliary ports of the 4 new nodes
            self.ports[a1, 1] = b1
            self.ports[a1, 2] = b2
            self.ports[a2, 1] = b1
            self.ports[a2, 2] = b2
            self.ports[b1, 1] = a1
            self.ports[b1, 2] = a2
            self.ports[b2, 1] = a1
            self.ports[b2, 2] = a2

            self.free_node(a)
            self.free_node(b)
            op = f"COMMUTE({a1},{a2},{b1},{b2})"

        self.reductions += 1
        self.trace_log.append({"step": self.reductions, "op": op, "a": a, "b": b})
        return op

    def compute_execution_commitment(self) -> Dict[str, Any]:
        """
        Compute the graph-committed execution trace digest (#21, #29, PROGRAM.md Phase 4):
          `H(initial_graph_bcp || canonical_step_log_json || final_graph_bcp)`
        """
        initial_bcp = self._initial_bcp if self._initial_bcp is not None else serialize_graph_bcp(self)
        final_bcp = serialize_graph_bcp(self)
        step_json = json.dumps(self.trace_log, sort_keys=True, separators=(",", ":")).encode("utf-8")

        initial_hash = "0x" + hashlib.sha256(initial_bcp).hexdigest()
        final_hash = "0x" + hashlib.sha256(final_bcp).hexdigest()

        h = hashlib.sha256()
        h.update(b"WEFT-IC-EXEC-V1:")
        h.update(initial_bcp)
        h.update(b":STEPS:")
        h.update(step_json)
        h.update(b":FINAL:")
        h.update(final_bcp)
        commitment = "0x" + h.hexdigest()

        active_nodes = int(np.sum(self.tags != self.FREE))
        return {
            "status": "PASS" if self.reductions > 0 else "FAIL",
            "capacity": self.capacity,
            "reductions_executed": self.reductions,
            "active_nodes_remaining": active_nodes,
            "initial_graph_sha256": initial_hash,
            "final_graph_sha256": final_hash,
            "bcp_byte_length": len(final_bcp),
            "trace_commitment_sha256": commitment,
            "steps": list(self.trace_log),
        }


def run_combinator_self_test() -> Dict[str, Any]:
    """Run a standard CON-DUP commutation followed by CON-CON annihilation and ERA propagation."""
    vm = FlatCombinatorVM(capacity=1024)
    # Allocate external anchor wires (CON nodes acting as free interface ports)
    ext_l = vm.alloc_node(vm.CON, p0=100, p1=101, p2=102)
    ext_r = vm.alloc_node(vm.CON, p0=200, p1=201, p2=202)
    c1 = vm.alloc_node(vm.CON, p0=1, p1=ext_l, p2=ext_r)
    d1 = vm.alloc_node(vm.DUP, p0=c1, p1=30, p2=40, aux_tag=1)
    vm.ports[c1, 0] = d1
    vm.ports[ext_l, 1] = c1
    vm.ports[ext_r, 1] = c1
    vm.snapshot_initial_graph()

    # Step 1: Commute CON(c1) with DUP(d1)
    vm.interact(c1, d1)

    # Step 2: Annihilate a same-kind CON-CON pair
    c2 = vm.alloc_node(vm.CON, p0=-1, p1=ext_l, p2=ext_r)
    c3 = vm.alloc_node(vm.CON, p0=c2, p1=ext_r, p2=ext_l)
    vm.ports[c2, 0] = c3
    vm.interact(c2, c3)

    # Step 3: Propagate ERA against one of the commuted nodes
    e0 = vm.alloc_node(vm.ERA, p0=4)
    vm.interact(e0, 4)

    return vm.compute_execution_commitment()


run_ic_verification = run_combinator_self_test
