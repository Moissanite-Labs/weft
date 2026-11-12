"""Weft Interaction Combinator VM & BCP Serializer (Codebase C3)."""
from .bcp_codec import (
    BCP_MAGIC,
    BCP_VERSION,
    deserialize_graph_bcp,
    graph_state_sha256,
    serialize_graph_bcp,
)
from .ic_vm import FlatCombinatorVM, run_combinator_self_test, run_ic_verification

__all__ = [
    "BCP_MAGIC",
    "BCP_VERSION",
    "FlatCombinatorVM",
    "deserialize_graph_bcp",
    "graph_state_sha256",
    "run_combinator_self_test",
    "run_ic_verification",
    "serialize_graph_bcp",
]
