#!/usr/bin/env python3
"""
Weft Flat-Array Interaction Combinator VM (Codebase C3 — Interface I5)
======================================================================

Storage (version 2, port-indexed)
---------------------------------
Each node has three port slots. A wire joins two *ports*, not two nodes, so
for every port the VM stores both the peer node (`ports[n, i]`) and which port
of that node the wire reaches (`peer_ports[n, i]`). An open port, a free wire
end on the boundary of the net, is `-1` in both arrays. Version 1 stored only
the peer node. Two different nets could then share one representation (#52),
and rules mis-wired loops through the active pair (#66). Paper 2 studied the
version 1 reducer; that copy is frozen under papers/02-checkable-computation/.

Arity (ports beyond it must stay open): ERA 0, CON 2, DUP 2, SUP 2, VLV 1, FRC 1.

Rules
-----
`interact(a, b)` accepts only an **active pair**: two distinct live nodes whose
principal ports (port 0) are wired to each other. Anything else raises
`ValueError` before the net, allocator or trace change.

1. Pure Lafont interaction combinators (`ERA = 0`, `CON = 1`, `DUP = 2`):
   - Same kind and label (`CON-CON`, `DUP(L)-DUP(L)`) annihilate, joining aux
     port i of one node to aux port i of the other.
   - Different kinds or labels (`CON-DUP`, `DUP(L)-DUP(M)`) commute: two copies
     of each node cross over.
   - `ERA-ERA` vanishes; `ERA` against a binary node leaves two `ERA` nodes on
     its aux wires.
   - Every rule removes the pair's ports and contracts the paths through them,
     so a wire that loops back into the pair is rewired correctly.
   - Confluence of this implementation has not been established by its tests.
2. Weft extensions (`VLV = 3`, `FRC = 4`, `SUP = 5`):
   - `VLV` (metabolic valve) gates the reduction with the C2 tension bound and a
     positive budget. When it passes, `VLV` vanishes and its peer takes the
     valve's output wire (port 1). When it fails, `VLV` becomes `FRC` with its
     principal port open, and a new `ERA` is wired to the peer's principal
     port, forming an active pair that erases the peer.
   - `SUP(L)` annihilates with `SUP(L)` or `DUP(L)` and commutes otherwise.
   - `FRC` has no rule.

Allocation always takes the lowest free slot, so where new nodes go depends
only on the current graph. A BCP snapshot therefore fixes every later step,
and a record replays from its initial graph (see `replay_execution`).

Execution record
----------------
The initial graph is snapshotted at the first reduction (or by an explicit
`snapshot_initial_graph()`). From then on the graph is sealed: the only way to
change it is `interact`, so every change appears in the step log.
`trace_commitment_sha256` hashes
`initial_graph_bcp || step_log_json || final_graph_bcp` with domain separators.
It binds bytes and steps under SHA-256's collision resistance;
`verify_execution_record` replays the steps to check they follow the rules.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

from weft.runtime.invariants import TENSION_MAX, verify_tension_bound
from .bcp_codec import BCP_VERSION, NODE_ARITY, deserialize_graph_bcp, serialize_graph_bcp, validate_port_graph

Port = Tuple[int, int]

EXEC_DOMAIN = b"WEFT-IC-EXEC-V2:"


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
    ARITY = NODE_ARITY

    def __init__(self, capacity: int = 4096):
        self.capacity = int(capacity)
        self.tags = np.full(self.capacity, self.FREE, dtype=np.uint8)
        self.aux_tags = np.zeros(self.capacity, dtype=np.int16)
        self.ports = np.full((self.capacity, 3), -1, dtype=np.int32)
        self.peer_ports = np.full((self.capacity, 3), -1, dtype=np.int8)
        self.reductions = 0
        self.trace_log: List[Dict[str, Any]] = []
        self._initial_bcp: Optional[bytes] = None

    # ------------------------------------------------------------ building
    def _require_unsealed(self) -> None:
        if self._initial_bcp is not None:
            raise RuntimeError(
                "graph is sealed after the initial snapshot; only interact() may change it, "
                "so that every change is in the execution record"
            )

    def _free_slots(self, count: int) -> List[int]:
        free = np.flatnonzero(self.tags == self.FREE)
        if len(free) < count:
            raise MemoryError(f"Combinator rule requires {count} free arena slots")
        return [int(s) for s in free[:count]]

    def _place(self, idx: int, tag: int, aux_tag: int) -> None:
        self.tags[idx] = tag
        self.aux_tags[idx] = aux_tag
        self.ports[idx, :] = -1
        self.peer_ports[idx, :] = -1

    def alloc_node(self, tag: int, aux_tag: int = 0) -> int:
        """Add a node with all ports open, in the lowest free slot."""
        self._require_unsealed()
        if int(tag) not in self.ARITY:
            raise ValueError(f"unknown node tag {tag}")
        (idx,) = self._free_slots(1)
        self._place(idx, int(tag), int(aux_tag))
        return idx

    def free_node(self, idx: int) -> None:
        """Remove a node; ports wired to it become open."""
        self._require_unsealed()
        self._release(int(idx))

    def _release(self, idx: int) -> None:
        for i in range(3):
            self._open(idx, i)
        self.tags[idx] = self.FREE
        self.aux_tags[idx] = 0

    def _check_port(self, node: int, port: int) -> None:
        if not (0 <= node < self.capacity) or int(self.tags[node]) == self.FREE:
            raise ValueError(f"node {node} is not live")
        if not 0 <= port <= self.ARITY[int(self.tags[node])]:
            raise ValueError(f"port {port} is beyond the arity of node {node}")

    def _open(self, node: int, port: int) -> None:
        """Open (node, port) and the far end of its wire, if any."""
        m = int(self.ports[node, port])
        if m >= 0:
            j = int(self.peer_ports[node, port])
            self.ports[m, j] = -1
            self.peer_ports[m, j] = -1
        self.ports[node, port] = -1
        self.peer_ports[node, port] = -1

    def _link(self, p: Port, q: Port) -> None:
        (a, i), (b, j) = p, q
        self.ports[a, i], self.peer_ports[a, i] = b, j
        self.ports[b, j], self.peer_ports[b, j] = a, i

    def connect_ports(self, node_a: int, port_a: int, node_b: int, port_b: int) -> None:
        """Wire port `port_a` of `node_a` to port `port_b` of `node_b`.

        Any wire either port had before is cut, leaving its far end open.
        """
        self._require_unsealed()
        node_a, port_a, node_b, port_b = int(node_a), int(port_a), int(node_b), int(port_b)
        self._check_port(node_a, port_a)
        self._check_port(node_b, port_b)
        if (node_a, port_a) == (node_b, port_b):
            raise ValueError("a port cannot be wired to itself")
        self._open(node_a, port_a)
        self._open(node_b, port_b)
        self._link((node_a, port_a), (node_b, port_b))

    def peer(self, node: int, port: int) -> Optional[Port]:
        """The port wired to (node, port), or None if it is open."""
        m = int(self.ports[node, port])
        return None if m < 0 else (m, int(self.peer_ports[node, port]))

    # ------------------------------------------------------------ validity
    def live_nodes(self) -> List[int]:
        return [int(s) for s in np.flatnonzero(self.tags != self.FREE)]

    def check_net(self) -> None:
        """Raise ValueError unless the storage is a well-formed port graph.

        Checks tags, arity, port ranges and that every wire is reciprocal and
        joins two distinct ports of live nodes. Open ports are allowed.
        """
        validate_port_graph(
            ((s, int(self.tags[s]), self.ports[s].tolist(), self.peer_ports[s].tolist())
             for s in self.live_nodes()),
            self.capacity,
        )

    def is_active_pair(self, a: int, b: int) -> bool:
        a, b = int(a), int(b)
        if a == b or not (0 <= a < self.capacity and 0 <= b < self.capacity):
            return False
        if self.FREE in (int(self.tags[a]), int(self.tags[b])):
            return False
        return self.peer(a, 0) == (b, 0)

    def active_pairs(self) -> List[Tuple[int, int]]:
        out = []
        for a in self.live_nodes():
            p = self.peer(a, 0)
            if p is not None and p[1] == 0 and a < p[0]:
                out.append((a, p[0]))
        return out

    # ------------------------------------------------------------ records
    def snapshot_initial_graph(self) -> bytes:
        """Record the initial graph and seal it against edits outside interact()."""
        if self.reductions:
            raise RuntimeError("the initial snapshot must precede the first reduction")
        if self._initial_bcp is None:
            self._initial_bcp = serialize_graph_bcp(self)
        return self._initial_bcp

    # ------------------------------------------------------------ rewriting
    def _rewrite(self, removed_nodes: Iterable[int], through: List[Tuple[Port, Port]]) -> None:
        """Remove `removed_nodes`, joining wires along the rule's `through` links.

        Each removed port has its old wire and at most one through link. From
        every surviving port that touches a removed port, follow old wires and
        through links alternately until reaching a surviving port (the new
        wire) or an open end. Loops through the pair are contracted, and closed
        loops made only of removed ports vanish.
        """
        removed_nodes = list(removed_nodes)
        removed = {(n, i) for n in removed_nodes for i in range(3)}
        nxt: Dict[Port, Port] = {}
        for p, q in through:
            if p in nxt or q in nxt:
                raise AssertionError("a port has two through links")
            nxt[p], nxt[q] = q, p

        starts: List[Port] = []
        for r in sorted(removed):
            s = self.peer(*r)
            if s is not None and s not in removed:
                starts.append(s)
        starts += [p for p in nxt if p not in removed]

        result: Dict[Port, Optional[Port]] = {}
        limit = 2 * len(removed) + 2
        for s in starts:
            if s in result:
                continue
            if s in nxt:
                cur, via = nxt[s], "through"
            else:
                cur, via = self.peer(*s), "wire"
            hops = 0
            while cur is not None and cur in removed:
                hops += 1
                if hops > limit:
                    raise AssertionError("path contraction did not terminate")
                if via == "wire":
                    cur, via = nxt.get(cur), "through"
                else:
                    cur, via = self.peer(*cur), "wire"
            result[s] = cur
            if cur is not None:
                result[cur] = s

        for n in removed_nodes:
            self.tags[n] = self.FREE
            self.aux_tags[n] = 0
            self.ports[n, :] = -1
            self.peer_ports[n, :] = -1
        for s, t in result.items():
            if t is None:
                self.ports[s] = -1
                self.peer_ports[s] = -1
            else:
                self._link(s, t)

    def interact(
        self,
        a: int,
        b: int,
        tension: float = 22.0,
        metabolic_budget: float = 100.0,
    ) -> str:
        a, b = int(a), int(b)
        if not self.is_active_pair(a, b):
            raise ValueError(f"({a}, {b}) is not an active pair (principal ports wired together)")
        ta, tb = int(self.tags[a]), int(self.tags[b])
        la, lb = int(self.aux_tags[a]), int(self.aux_tags[b])
        if self.FRC in (ta, tb):
            raise ValueError("FRC has no interaction rule")

        annihilates = (
            (ta == tb and la == lb and ta in (self.CON, self.DUP, self.SUP))
            or ({ta, tb} == {self.DUP, self.SUP} and la == lb)
        )
        if ta == self.VLV or tb == self.VLV:
            tension = float(tension)
            metabolic_budget = float(metabolic_budget)
            if not (math.isfinite(tension) and math.isfinite(metabolic_budget)):
                raise ValueError("VLV tension and metabolic_budget must be finite")
            t_check = verify_tension_bound(tension, max_tension=TENSION_MAX)
            valve_passes = t_check["accepted"] and metabolic_budget > 0.0
            required_slots = 0 if valve_passes else 1
        elif ta == self.ERA and tb == self.ERA:
            required_slots = 0
        elif ta == self.ERA or tb == self.ERA:
            required_slots = 2
        else:
            required_slots = 0 if annihilates else 4
        # Preflight: reserve every slot the rule needs before anything changes.
        # The old pair stays live during the rule, so new nodes never reuse it.
        slots = self._free_slots(required_slots)
        if self._initial_bcp is None:
            self.snapshot_initial_graph()

        entry: Dict[str, Any] = {"a": a, "b": b}
        # 0. Weft metabolic valve (VLV = 3)
        if ta == self.VLV or tb == self.VLV:
            vlv, peer = (a, b) if ta == self.VLV else (b, a)
            if valve_passes:
                self._rewrite([vlv], [((vlv, 0), (vlv, 1))])
                op = "VLV_PASS"
            else:
                (era,) = slots
                self._place(era, self.ERA, 0)
                self.tags[vlv] = self.FRC
                self.ports[vlv, 0] = -1
                self.peer_ports[vlv, 0] = -1
                self._link((era, 0), (peer, 0))
                op = "VLV_EXCISE_TO_FRC"
            entry.update(tension=tension, metabolic_budget=metabolic_budget)

        # 1. Erasure
        elif ta == self.ERA and tb == self.ERA:
            self._rewrite([a, b], [])
            op = "ERA_ERA"
        elif ta == self.ERA or tb == self.ERA:
            era_idx, other = (a, b) if ta == self.ERA else (b, a)
            e1, e2 = slots
            self._place(e1, self.ERA, 0)
            self._place(e2, self.ERA, 0)
            self._rewrite([era_idx, other], [((other, 1), (e1, 0)), ((other, 2), (e2, 0))])
            op = f"ERA_PROPAGATE({e1},{e2})"

        # 2. Annihilation: CON-CON, DUP(L)-DUP(L), SUP(L)-SUP(L), DUP(L)-SUP(L)
        elif annihilates:
            self._rewrite([a, b], [((a, 1), (b, 1)), ((a, 2), (b, 2))])
            op = f"ANNIHILATE(tagA={ta},tagB={tb},label={la})"

        # 3. Commutation: CON-DUP, DUP(L)-DUP(M), and CON/DUP/SUP mixes
        else:
            a1, a2, b1, b2 = slots
            self._place(a1, tb, lb)
            self._place(a2, tb, lb)
            self._place(b1, ta, la)
            self._place(b2, ta, la)
            self._link((a1, 1), (b1, 1))
            self._link((a1, 2), (b2, 1))
            self._link((a2, 1), (b1, 2))
            self._link((a2, 2), (b2, 2))
            self._rewrite(
                [a, b],
                [((a, 1), (a1, 0)), ((a, 2), (a2, 0)), ((b, 1), (b1, 0)), ((b, 2), (b2, 0))],
            )
            op = f"COMMUTE({a1},{a2},{b1},{b2})"

        self.reductions += 1
        entry.update(step=self.reductions, op=op)
        self.trace_log.append(entry)
        return op

    def normalize(self, max_steps: int = 10_000, **kwargs: float) -> int:
        """Reduce the lowest active pair until none remain; return the step count."""
        steps = 0
        while steps < max_steps:
            pairs = [p for p in self.active_pairs() if self.FRC not in (int(self.tags[p[0]]), int(self.tags[p[1]]))]
            if not pairs:
                break
            self.interact(*pairs[0], **kwargs)
            steps += 1
        return steps

    def compute_execution_commitment(self) -> Dict[str, Any]:
        """
        Compute the graph-committed execution trace digest (#21, #29, PROGRAM.md Phase 4):
          `H(initial_graph_bcp || canonical_step_log_json || final_graph_bcp)`
        """
        initial_bcp = self._initial_bcp if self._initial_bcp is not None else serialize_graph_bcp(self)
        return _commitment_record(self.capacity, initial_bcp, self.trace_log, serialize_graph_bcp(self),
                                  self.reductions, len(self.live_nodes()))


def _commitment_record(capacity: int, initial_bcp: bytes, steps: List[Dict[str, Any]], final_bcp: bytes,
                       reductions: int, active_nodes: int) -> Dict[str, Any]:
    step_json = json.dumps(steps, sort_keys=True, separators=(",", ":")).encode("utf-8")
    h = hashlib.sha256()
    h.update(EXEC_DOMAIN)
    h.update(initial_bcp)
    h.update(b":STEPS:")
    h.update(step_json)
    h.update(b":FINAL:")
    h.update(final_bcp)
    return {
        "status": "PASS" if reductions > 0 else "FAIL",
        "bcp_version": BCP_VERSION,
        "capacity": capacity,
        "reductions_executed": reductions,
        "active_nodes_remaining": active_nodes,
        "initial_graph_sha256": "0x" + hashlib.sha256(initial_bcp).hexdigest(),
        "final_graph_sha256": "0x" + hashlib.sha256(final_bcp).hexdigest(),
        "bcp_byte_length": len(final_bcp),
        "trace_commitment_sha256": "0x" + h.hexdigest(),
        "steps": [dict(s) for s in steps],
    }


def replay_execution(initial_bcp: bytes, steps: List[Dict[str, Any]]) -> FlatCombinatorVM:
    """Re-run `steps` from the initial graph, checking each step's op as it goes.

    Raises ValueError if a step is not an active pair, or yields a different op.
    """
    vm = deserialize_graph_bcp(initial_bcp)
    vm.snapshot_initial_graph()
    for n, step in enumerate(steps, start=1):
        if step.get("step") != n:
            raise ValueError(f"step {n}: numbered {step.get('step')!r}")
        kwargs = {k: step[k] for k in ("tension", "metabolic_budget") if k in step}
        op = vm.interact(step["a"], step["b"], **kwargs)
        if op != step.get("op"):
            raise ValueError(f"step {n}: replay gave {op!r}, record says {step.get('op')!r}")
    return vm


def verify_execution_record(initial_bcp: bytes, record: Dict[str, Any]) -> Dict[str, Any]:
    """Check a record by replaying it from `initial_bcp`.

    PASS means: the bytes match the record's initial hash, every step is a legal
    reduction giving the recorded op, and the replayed final graph and
    commitment equal the record's. It says nothing about why the steps were
    chosen, or about any VLV inputs beyond those recorded.
    """
    reasons = []
    if "0x" + hashlib.sha256(initial_bcp).hexdigest() != record.get("initial_graph_sha256"):
        reasons.append("initial graph does not match the record's initial_graph_sha256")
    try:
        vm = replay_execution(initial_bcp, record.get("steps", []))
    except (ValueError, KeyError, TypeError, MemoryError) as exc:
        reasons.append(f"replay failed: {exc}")
    else:
        again = _commitment_record(vm.capacity, initial_bcp, vm.trace_log, serialize_graph_bcp(vm),
                                   vm.reductions, len(vm.live_nodes()))
        for key in ("final_graph_sha256", "trace_commitment_sha256"):
            if again[key] != record.get(key):
                reasons.append(f"{key} differs on replay")
    return {"status": "FAIL" if reasons else "PASS", "reasons": reasons}


def run_combinator_self_test() -> Dict[str, Any]:
    """Reduce a small net to normal form and check its record replays.

    The net exercises annihilation with a wire looped across the pair,
    commutation of a CON whose aux ports are wired to each other, and erasure.
    It is built in full before the snapshot; every change after that is a
    reduction of an active pair.
    """
    vm = FlatCombinatorVM(capacity=64)
    # Allocation order sets the reduction order: normalize() takes the lowest
    # active pair, so c2-c3 annihilates first and leaves c1's aux ports looped.
    c2, c3 = vm.alloc_node(vm.CON), vm.alloc_node(vm.CON)
    c1, d1 = vm.alloc_node(vm.CON), vm.alloc_node(vm.DUP, aux_tag=1)
    e0, d2 = vm.alloc_node(vm.ERA), vm.alloc_node(vm.DUP, aux_tag=2)
    vm.connect_ports(c1, 0, d1, 0)
    vm.connect_ports(c2, 0, c3, 0)
    vm.connect_ports(e0, 0, d2, 0)
    vm.connect_ports(c1, 1, c2, 1)
    vm.connect_ports(c1, 2, c3, 1)
    vm.connect_ports(c2, 2, c3, 2)  # loops across the c2-c3 pair
    vm.connect_ports(d1, 1, d2, 1)
    # d1.2 and d2.2 stay open: the net's interface.
    vm.check_net()
    initial = vm.snapshot_initial_graph()
    vm.normalize()
    vm.check_net()
    record = vm.compute_execution_commitment()
    record["replay"] = verify_execution_record(initial, record)["status"]
    if record["replay"] != "PASS":
        record["status"] = "FAIL"
    return record


run_ic_verification = run_combinator_self_test
