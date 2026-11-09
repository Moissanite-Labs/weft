#!/usr/bin/env python3
"""
Binary Combinator Packet (BCP) Graph Serializer (Codebase C3 — Interface I5)
============================================================================
Canonical binary format for serializing, hashing, and restoring Interaction
Combinator graphs (`FlatCombinatorVM`).

Header layout (12 bytes, little-endian `<4sBBHI`):
  - `magic`:   4 bytes (`b"WEFT"`, `0x57454654`)
  - `version`: uint8 (`2`; version `1` is decoded, never written)
  - `flags`:   uint8 (`0` = canonical active-node snapshot)
  - `count`:   uint16 (number of serialized non-FREE nodes)
  - `capacity`: uint32 (VM node array capacity)

Node record layout (20 bytes per non-FREE node, little-endian `<IBBhiii`):
  - `slot`:    uint32 (node slot index, strictly ascending)
  - `tag`:     uint8  (`ERA=0, CON=1, DUP=2, VLV=3, FRC=4, SUP=5`)
  - `peers`:   uint8  (version 2: peer-port byte; version 1: reserved, zero)
  - `aux_tag`: int16  (combinator label / superposition index)
  - `p0`:      int32  (principal port: peer slot, or -1 if open)
  - `p1`:      int32  (left auxiliary port: peer slot, or -1)
  - `p2`:      int32  (right auxiliary port: peer slot, or -1)

Version 2 peer-port byte: bits `2i..2i+1` hold which port of node `p_i` the
wire reaches (0, 1 or 2), or `3` when port i is open (`p_i == -1`). Bits 6-7
are zero. With it, every wire is stored as a pair of ports, so two different
nets can no longer share one encoding (#52). Records are 20 bytes in both
versions.

Both directions also check topology: ports beyond a node's arity are open, and
every wire is reciprocal between two distinct ports of live nodes.

Version 1 stored only the peer slot. It is decoded by inferring each peer port,
and rejected where that is ambiguous (two wires between the same two nodes) or
the wiring is not a well-formed graph.

Provenance:
  Extracted and completed from `weft/design/craft.md:455-512` and `PROGRAM.md`
  Phase 4 ("an execution record that actually includes the graph").
"""

from __future__ import annotations

import hashlib
import struct
from typing import TYPE_CHECKING, Iterable, List, Tuple

if TYPE_CHECKING:
    from .ic_vm import FlatCombinatorVM

BCP_MAGIC = b"WEFT"
BCP_VERSION = 2
BCP_DECODABLE_VERSIONS = (1, 2)
HEADER_STRUCT = struct.Struct("<4sBBHI")
NODE_STRUCT = struct.Struct("<IBBhiii")
# A tiny packet may declare a huge sparse arena. Bound that allocation before
# constructing NumPy arrays; callers can choose another explicit node limit.
DEFAULT_MAX_BCP_CAPACITY = 1_048_576
# Ports beyond a node's arity must be open. ERA 0, CON 1, DUP 2, VLV 3, FRC 4, SUP 5.
NODE_ARITY = {0: 0, 1: 2, 2: 2, 3: 1, 4: 1, 5: 2}
NODE_TAGS = frozenset(NODE_ARITY)
OPEN_PEER = 3


def pack_peer_ports(peers) -> int:
    byte = 0
    for i, j in enumerate(peers):
        byte |= (OPEN_PEER if j == -1 else int(j)) << (2 * i)
    return byte


def unpack_peer_ports(byte: int) -> List[int]:
    if byte >> 6:
        raise ValueError("BCP peer-port byte bits 6-7 must be zero")
    out = []
    for i in range(3):
        j = (byte >> (2 * i)) & 3
        out.append(-1 if j == OPEN_PEER else j)
    return out


def _validate_records(records: list, capacity: int) -> None:
    """Validate the storage domain: header bounds, slot order, tags, port ranges."""
    if not 0 <= capacity <= 0xFFFFFFFF:
        raise ValueError("BCP capacity must fit uint32")
    if len(records) > min(capacity, 0xFFFF):
        raise ValueError("BCP node count exceeds capacity or uint16")
    previous_slot = -1
    for slot, tag, _peers, _label, *ports in records:
        if not previous_slot < slot < capacity:
            raise ValueError("BCP slots must be unique, ascending and below capacity")
        if tag not in NODE_TAGS:
            raise ValueError(f"Invalid BCP node tag: {tag}")
        if any(port < -1 or port >= capacity for port in ports):
            raise ValueError("BCP port must be -1 or an in-arena slot")
        previous_slot = slot


def _infer_v1_peer_ports(records: list) -> List[List[int]]:
    """Recover peer ports for version 1 records, or raise if that is ambiguous."""
    rows = {slot: (tag, ports) for slot, tag, _r, _l, *ports in records}
    out = []
    for slot, tag, reserved, _label, *ports in records:
        if reserved != 0:
            raise ValueError("BCP V1 node reserved byte must be zero")
        arity = NODE_ARITY[tag]
        peers = []
        for i, m in enumerate(ports):
            if m == -1:
                peers.append(-1)
                continue
            if i > arity or m not in rows:
                raise ValueError(f"BCP V1 node {slot} port {i} is not a well-formed wire")
            m_tag, m_ports = rows[m]
            candidates = [j for j in range(NODE_ARITY[m_tag] + 1)
                          if m_ports[j] == slot and (m, j) != (slot, i)]
            if len(candidates) != 1:
                raise ValueError(f"BCP V1 node {slot} port {i}: peer port is ambiguous or missing")
            peers.append(candidates[0])
        out.append(peers)
    return out


def validate_port_graph(nodes: Iterable[Tuple[int, int, List[int], List[int]]], capacity: int) -> None:
    """Check `(slot, tag, ports, peer_ports)` rows form a well-formed port graph."""
    rows = {slot: (tag, ports, peers) for slot, tag, ports, peers in nodes}
    for slot, (tag, ports, peers) in rows.items():
        arity = NODE_ARITY.get(tag)
        if arity is None:
            raise ValueError(f"node {slot}: unknown tag {tag}")
        for i in range(3):
            m, j = int(ports[i]), int(peers[i])
            if m == -1 or j == -1:
                if (m, j) != (-1, -1):
                    raise ValueError(f"node {slot} port {i}: half-open port")
                continue
            if i > arity:
                raise ValueError(f"node {slot} port {i}: wired beyond arity {arity}")
            if not 0 <= m < capacity or m not in rows:
                raise ValueError(f"node {slot} port {i}: wired to a free or out-of-range slot {m}")
            if not 0 <= j <= NODE_ARITY[rows[m][0]]:
                raise ValueError(f"node {slot} port {i}: peer port {j} beyond arity of node {m}")
            if (m, j) == (slot, i):
                raise ValueError(f"node {slot} port {i}: wired to itself")
            if (int(rows[m][1][j]), int(rows[m][2][j])) != (slot, i):
                raise ValueError(f"node {slot} port {i}: wire to ({m}, {j}) is not reciprocal")


def serialize_graph_bcp(vm: "FlatCombinatorVM") -> bytes:
    """Serialize all non-FREE nodes of `vm` in ascending slot order (version 2)."""
    active_indices = [
        idx for idx in range(vm.capacity) if int(vm.tags[idx]) != int(vm.FREE)
    ]
    records = [
        (idx, int(vm.tags[idx]), pack_peer_ports(int(j) for j in vm.peer_ports[idx]),
         int(vm.aux_tags[idx]), *(int(port) for port in vm.ports[idx]))
        for idx in active_indices
    ]
    _validate_records(records, int(vm.capacity))
    validate_port_graph(
        ((r[0], r[1], list(r[4:]), unpack_peer_ports(r[2])) for r in records), int(vm.capacity)
    )
    buf = bytearray(HEADER_STRUCT.size + len(active_indices) * NODE_STRUCT.size)
    HEADER_STRUCT.pack_into(
        buf, 0, BCP_MAGIC, BCP_VERSION, 0, len(active_indices), int(vm.capacity)
    )
    offset = HEADER_STRUCT.size
    for record in records:
        NODE_STRUCT.pack_into(buf, offset, *record)
        offset += NODE_STRUCT.size
    return bytes(buf)


def deserialize_graph_bcp(
    blob: bytes, *, max_capacity: int = DEFAULT_MAX_BCP_CAPACITY
) -> "FlatCombinatorVM":
    """Restore a graph with its exact capacity, under an explicit allocation limit.

    Accepts version 2, and version 1 where peer ports can be inferred. Storage,
    arity and reciprocal wiring are all checked before the arena is allocated.
    A snapshot holds the graph only, not a reduction count or trace; because
    allocation takes the lowest free slot, the graph alone fixes later steps.
    """
    from .ic_vm import FlatCombinatorVM

    if len(blob) < HEADER_STRUCT.size:
        raise ValueError("BCP packet shorter than 12-byte header")
    magic, version, flags, count, capacity = HEADER_STRUCT.unpack_from(blob, 0)
    if magic != BCP_MAGIC:
        raise ValueError(f"Invalid BCP magic: {magic!r}")
    if version not in BCP_DECODABLE_VERSIONS:
        raise ValueError(f"Unsupported BCP version: {version}")
    if flags != 0:
        raise ValueError("BCP flags must be zero")
    if not isinstance(max_capacity, int) or max_capacity < 0:
        raise ValueError("BCP max_capacity must be a nonnegative integer")
    if capacity > max_capacity:
        raise ValueError(f"BCP capacity {capacity} exceeds decode limit {max_capacity}")
    expected_len = HEADER_STRUCT.size + count * NODE_STRUCT.size
    if len(blob) != expected_len:
        raise ValueError(f"BCP length mismatch: got {len(blob)}, expected {expected_len}")

    records = list(NODE_STRUCT.iter_unpack(blob[HEADER_STRUCT.size:]))
    _validate_records(records, capacity)
    if version == 1:
        peer_rows = _infer_v1_peer_ports(records)
    else:
        peer_rows = [unpack_peer_ports(r[2]) for r in records]
    rows: List[Tuple[int, int, List[int], List[int]]] = [
        (r[0], r[1], list(r[4:]), peers) for r, peers in zip(records, peer_rows)
    ]
    validate_port_graph(rows, capacity)
    # Every record is valid; this is the only arena allocation.
    vm = FlatCombinatorVM(capacity=capacity)
    for (slot, tag, _p, aux_tag, *_ports), (_s, _t, ports, peers) in zip(records, rows):
        vm.tags[slot] = tag
        vm.aux_tags[slot] = aux_tag
        vm.ports[slot, :] = ports
        vm.peer_ports[slot, :] = peers
    return vm


def graph_state_sha256(vm: "FlatCombinatorVM") -> str:
    """Return `0x`-prefixed SHA-256 digest of the canonical BCP graph serialization."""
    return "0x" + hashlib.sha256(serialize_graph_bcp(vm)).hexdigest()
