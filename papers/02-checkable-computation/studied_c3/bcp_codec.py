#!/usr/bin/env python3
"""
Binary Combinator Packet (BCP) Graph Serializer (Codebase C3 — Interface I5)
============================================================================
Canonical binary format for serializing, hashing, and restoring Interaction
Combinator graphs (`FlatCombinatorVM`).

Header layout (12 bytes, little-endian `<4sBBHI`):
  - `magic`:   4 bytes (`b"WEFT"`, `0x57454654`)
  - `version`: uint8 (`1`)
  - `flags`:   uint8 (`0` = canonical active-node snapshot)
  - `count`:   uint16 (number of serialized non-FREE nodes)
  - `capacity`: uint32 (VM node array capacity)

Node record layout (20 bytes per non-FREE node, little-endian `<IBBhiii`):
  - `slot`:    uint32 (deterministic node slot index)
  - `tag`:     uint8  (`ERA=0, CON=1, DUP=2, VLV=3, FRC=4, SUP=5`)
  - `reserved`: uint8 (`0`)
  - `aux_tag`: int16  (combinator label / superposition index)
  - `p0`:      int32  (principal port target)
  - `p1`:      int32  (left auxiliary port target)
  - `p2`:      int32  (right auxiliary port target)

Provenance:
  Extracted and completed from `weft/design/craft.md:455-512` and `PROGRAM.md`
  Phase 4 ("an execution record that actually includes the graph").
"""

from __future__ import annotations

import hashlib
import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ic_vm import FlatCombinatorVM

BCP_MAGIC = b"WEFT"
BCP_VERSION = 1
HEADER_STRUCT = struct.Struct("<4sBBHI")
NODE_STRUCT = struct.Struct("<IBBhiii")
# A tiny packet may declare a huge sparse arena. Bound that allocation before
# constructing NumPy arrays; callers can choose another explicit node limit.
DEFAULT_MAX_BCP_CAPACITY = 1_048_576
NODE_TAGS = frozenset(range(6))


def _validate_records(records: list, capacity: int) -> None:
    """Validate the V1 storage domain, not interaction-net topology/semantics."""
    if not 0 <= capacity <= 0xFFFFFFFF:
        raise ValueError("BCP capacity must fit uint32")
    if len(records) > min(capacity, 0xFFFF):
        raise ValueError("BCP node count exceeds capacity or uint16")
    previous_slot = -1
    for slot, tag, reserved, _label, *ports in records:
        if not previous_slot < slot < capacity:
            raise ValueError("BCP slots must be unique, ascending and below capacity")
        if tag not in NODE_TAGS:
            raise ValueError(f"Invalid BCP node tag: {tag}")
        if reserved != 0:
            raise ValueError("BCP node reserved byte must be zero")
        if any(port < -1 or port >= capacity for port in ports):
            raise ValueError("BCP port must be -1 or an in-arena slot")
        previous_slot = slot


def serialize_graph_bcp(vm: "FlatCombinatorVM") -> bytes:
    """Serialize all non-FREE nodes of `vm` in ascending slot order into a BCP packet."""
    active_indices = [
        idx for idx in range(vm.capacity) if int(vm.tags[idx]) != int(vm.FREE)
    ]
    records = [
        (idx, int(vm.tags[idx]), 0, int(vm.aux_tags[idx]),
         *(int(port) for port in vm.ports[idx]))
        for idx in active_indices
    ]
    _validate_records(records, int(vm.capacity))
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
    """Restore exact graph storage capacity, with an explicit allocation limit.

    V1 snapshots do not include allocator history or execution continuation.
    Port ranges are checked; peer-port identity and topology are not encoded.
    """
    from .ic_vm import FlatCombinatorVM

    if len(blob) < HEADER_STRUCT.size:
        raise ValueError("BCP packet shorter than 12-byte header")
    magic, version, flags, count, capacity = HEADER_STRUCT.unpack_from(blob, 0)
    if magic != BCP_MAGIC:
        raise ValueError(f"Invalid BCP magic: {magic!r}")
    if version != BCP_VERSION:
        raise ValueError(f"Unsupported BCP version: {version}")
    if flags != 0:
        raise ValueError("BCP V1 flags must be zero")
    if not isinstance(max_capacity, int) or max_capacity < 0:
        raise ValueError("BCP max_capacity must be a nonnegative integer")
    if capacity > max_capacity:
        raise ValueError(f"BCP capacity {capacity} exceeds decode limit {max_capacity}")
    expected_len = HEADER_STRUCT.size + count * NODE_STRUCT.size
    if len(blob) != expected_len:
        raise ValueError(f"BCP length mismatch: got {len(blob)}, expected {expected_len}")

    records = list(NODE_STRUCT.iter_unpack(blob[HEADER_STRUCT.size:]))
    _validate_records(records, capacity)
    # Validate every record before the only arena allocation.
    vm = FlatCombinatorVM(capacity=capacity)
    for slot, tag, _reserved, aux_tag, p0, p1, p2 in records:
        vm.tags[slot] = tag
        vm.aux_tags[slot] = aux_tag
        vm.ports[slot, 0] = p0
        vm.ports[slot, 1] = p1
        vm.ports[slot, 2] = p2
    vm.next_alloc = records[-1][0] + 1 if records else 0
    return vm


def graph_state_sha256(vm: "FlatCombinatorVM") -> str:
    """Return `0x`-prefixed SHA-256 digest of the canonical BCP graph serialization."""
    return "0x" + hashlib.sha256(serialize_graph_bcp(vm)).hexdigest()
