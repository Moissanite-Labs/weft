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


def serialize_graph_bcp(vm: "FlatCombinatorVM") -> bytes:
    """Serialize all non-FREE nodes of `vm` in ascending slot order into a BCP packet."""
    active_indices = [
        idx for idx in range(vm.capacity) if int(vm.tags[idx]) != int(vm.FREE)
    ]
    buf = bytearray(HEADER_STRUCT.size + len(active_indices) * NODE_STRUCT.size)
    HEADER_STRUCT.pack_into(
        buf, 0, BCP_MAGIC, BCP_VERSION, 0, len(active_indices), int(vm.capacity)
    )
    offset = HEADER_STRUCT.size
    for idx in active_indices:
        NODE_STRUCT.pack_into(
            buf,
            offset,
            int(idx),
            int(vm.tags[idx]),
            0,
            int(vm.aux_tags[idx]),
            int(vm.ports[idx, 0]),
            int(vm.ports[idx, 1]),
            int(vm.ports[idx, 2]),
        )
        offset += NODE_STRUCT.size
    return bytes(buf)


def deserialize_graph_bcp(blob: bytes) -> "FlatCombinatorVM":
    """Reconstruct a `FlatCombinatorVM` state from a canonical BCP packet."""
    from .ic_vm import FlatCombinatorVM

    if len(blob) < HEADER_STRUCT.size:
        raise ValueError("BCP packet shorter than 12-byte header")
    magic, version, _flags, count, capacity = HEADER_STRUCT.unpack_from(blob, 0)
    if magic != BCP_MAGIC:
        raise ValueError(f"Invalid BCP magic: {magic!r}")
    if version != BCP_VERSION:
        raise ValueError(f"Unsupported BCP version: {version}")
    expected_len = HEADER_STRUCT.size + count * NODE_STRUCT.size
    if len(blob) != expected_len:
        raise ValueError(f"BCP length mismatch: got {len(blob)}, expected {expected_len}")

    vm = FlatCombinatorVM(capacity=max(int(capacity), count + 16))
    offset = HEADER_STRUCT.size
    max_slot = -1
    for _ in range(count):
        slot, tag, _res, aux_tag, p0, p1, p2 = NODE_STRUCT.unpack_from(blob, offset)
        offset += NODE_STRUCT.size
        if slot >= vm.capacity:
            raise ValueError(f"Node slot {slot} exceeds VM capacity {vm.capacity}")
        vm.tags[slot] = tag
        vm.aux_tags[slot] = aux_tag
        vm.ports[slot, 0] = p0
        vm.ports[slot, 1] = p1
        vm.ports[slot, 2] = p2
        if int(slot) > max_slot:
            max_slot = int(slot)
    vm.next_alloc = max_slot + 1
    return vm


def graph_state_sha256(vm: "FlatCombinatorVM") -> str:
    """Return `0x`-prefixed SHA-256 digest of the canonical BCP graph serialization."""
    return "0x" + hashlib.sha256(serialize_graph_bcp(vm)).hexdigest()
