"""
synaptic_flow.py — Unit-Capacity Dinic Synaptic Routing, Certified Min-Cut Mitosis
Triggers, and Exact `fractions.Fraction` Dual Certificates for `weft.runtime.plasm`.

Ports exact-frontier combinatorial optimization and fail-closed verification primitives
from `ahrazzle/soko` (PRs #18, #26, #29, #34, #35, #37) directly into Codebase C1
(`weft/runtime/plasm`), honoring Interfaces I3 (`weft/runtime/invariants`), I4
(`StratifiedMemoryArena` 540,688-byte layout & `core_rows = dim // 4` freeze contract),
and Issue #51 (explicit candidate-vs-committed state separation & deterministic replay).

Key guarantees:
  1. Vertex-Split Unit-Capacity Dinic Routing (`u_in -> u_out` capacity 1): Eliminates
     multi-plasmid "Hall-stacking" slot collisions while strictly excluding frozen core
     rows (`0 .. core_rows - 1`) and any caller-supplied `locked_mask` indices.
  2. Dual Residual Min-Cut Certificates (`source_minimal` & `sink_minimal`): Emits
     independently verifiable max-flow == min-cut obstruction witnesses quantifying the
     exact slot deficit `deficit = total_demand - max_flow` needed for Orthogonal Mitosis.
  3. Zero-Drift Orthogonal Mitosis Expansion (`expand_weights_orthogonal_mitosis`):
     Appends exact-deficit zero-initialized peripheral channels with `core_row_drift == 0.0`.
  4. Exact-Rational `fractions.Fraction` Cost-Partitioned & Farkas Dual Certificates:
     Verifies strict budget monotonicity (blocking negative-cost minting and IEEE-754
     Zeno sub-ULP stagnation in exact Q), additive multi-skill drift bounds, and Farkas
     infeasibility witnesses with zero floating-point rounding optimism in the TCB.

License: Apache-2.0
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union

import numpy as np


# =============================================================================
# 1. Tensor / Array Interop Helpers (Seamless `numpy.ndarray` & `torch.Tensor`)
# =============================================================================

def _is_torch_tensor(x: Any) -> bool:
    return hasattr(x, "detach") and hasattr(x, "cpu") and hasattr(x, "numpy")


def _to_numpy_f64(x: Any) -> np.ndarray:
    if _is_torch_tensor(x):
        return x.detach().cpu().numpy().astype(np.float64, copy=True)
    return np.asarray(x, dtype=np.float64)


def _restore_like(arr: np.ndarray, template: Any) -> Any:
    if _is_torch_tensor(template):
        import torch  # Imported lazily only when caller supplied a torch.Tensor
        return torch.as_tensor(arr, dtype=template.dtype, device=template.device).clone()
    if isinstance(template, np.ndarray):
        return arr.astype(template.dtype, copy=False)
    return arr


# Input bounds. Every builder and verifier rejects inputs above these before
# allocating anything proportional to them.
MAX_NEURONS = 1 << 20
MAX_PLASMIDS = 1 << 16
MAX_NETWORK_EDGES = 1 << 24
MAX_RATIONAL_TERMS = 1 << 16
MAX_RATIONAL_CHARS = 4096
MAX_DEMAND = 1 << 40
_CANONICAL_Q_RE = re.compile(r"-?(0|[1-9][0-9]*)/[1-9][0-9]*")


def _is_int(x: Any) -> bool:
    """True for Python and numpy integers, never for bool."""
    return isinstance(x, (int, np.integer)) and not isinstance(x, (bool, np.bool_))


def _require_int(x: Any, name: str, *, lo: Optional[int] = None, hi: Optional[int] = None) -> int:
    if not _is_int(x):
        raise ValueError(f"{name} must be an integer, got {type(x).__name__} {x!r}.")
    v = int(x)
    if lo is not None and v < lo:
        raise ValueError(f"{name}={v} is below {lo}.")
    if hi is not None and v > hi:
        raise ValueError(f"{name}={v} is above {hi}.")
    return v


def _exact_fraction(value: Union[int, float, str, Fraction], *, upward_digits: Optional[int] = None) -> Fraction:
    """
    Converts `value` into an exact signed `fractions.Fraction` without float rounding
    optimism. Rejects `bool`, `None`, `NaN`, `Inf`, a zero denominator and any other type
    with `ValueError`. Used for Farkas matrix and right-hand-side entries, which may be
    negative.
    """
    if isinstance(value, (bool, np.bool_)):
        raise ValueError("Boolean values are not valid rational quantities.")
    if isinstance(value, Fraction):
        q = value
    elif _is_int(value):
        q = Fraction(int(value))
    elif isinstance(value, str):
        if len(value) > MAX_RATIONAL_CHARS:
            raise ValueError("Rational string is too long.")
        try:
            q = Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"Invalid rational string {value!r}: {exc}") from None
    elif isinstance(value, (float, np.floating)):
        fv = float(value)
        if not math.isfinite(fv):
            raise ValueError(f"Non-finite float {fv!r} cannot be converted to Fraction.")
        # Exact IEEE-754 binary float value in Q (never string-rounded!)
        q = Fraction.from_float(fv)
        if upward_digits is not None:
            scale = 10 ** int(upward_digits)
            q = Fraction(math.ceil(q * scale), scale)
    else:
        raise ValueError(f"Unsupported numeric type for Fraction conversion: {type(value)!r}")
    return q


def _exact_nonneg_fraction(value: Union[int, float, str, Fraction], *, upward_digits: Optional[int] = None) -> Fraction:
    """
    Converts `value` into an exact `fractions.Fraction` without float rounding optimism.
    Rejects `bool`, `NaN`, `Inf`, and negative numbers fail-closed with `ValueError`.
    """
    q = _exact_fraction(value, upward_digits=upward_digits)
    if q < 0:
        raise ValueError(f"Negative quantity {q} rejected; expected a non-negative rational.")
    return q


def _parse_canonical_q(value: Any) -> Optional[Fraction]:
    """Parses a certificate's canonical `num/den` string. Returns None if it is not one."""
    if not isinstance(value, str) or len(value) > MAX_RATIONAL_CHARS:
        return None
    if not _CANONICAL_Q_RE.fullmatch(value):
        return None
    q = Fraction(value)
    if f"{q.numerator}/{q.denominator}" != value:
        return None
    return q


# =============================================================================
# 2. Unit-Capacity Dinic Synaptic Router & Certified Residual Min-Cuts
# =============================================================================

@dataclass
class _ResidualEdge:
    to: int
    rev: int
    cap: int
    flow: int = 0


@dataclass(frozen=True)
class MinCutMitosisCertificate:
    """
    Immutable, independently checkable certificate of a synaptic slot-routing solve
    and its exact max-flow / min-cut mitosis trigger status.
    """
    total_neurons: int
    core_rows_frozen: int
    frozen_indices: Tuple[int, ...]
    eligible_indices: Tuple[int, ...]
    plasmid_demands: Tuple[int, ...]
    total_demand: int
    max_flow: int
    deficit: int
    requires_mitosis: bool
    assignments: Tuple[Tuple[int, ...], ...]
    source_minimal_cut: Tuple[int, ...]
    sink_minimal_cut: Tuple[int, ...]
    cut_capacity_source_minimal: int
    cut_capacity_sink_minimal: int
    network_vertex_count: int
    network_edges: Tuple[Tuple[int, int, int], ...]  # (u, v, cap) of original directed graph
    sha256_digest: str


_MIN_CUT_FIELDS: Tuple[str, ...] = (
    "total_neurons",
    "core_rows_frozen",
    "frozen_indices",
    "eligible_indices",
    "plasmid_demands",
    "total_demand",
    "max_flow",
    "deficit",
    "requires_mitosis",
    "assignments",
    "source_minimal_cut",
    "sink_minimal_cut",
    "cut_capacity_source_minimal",
    "cut_capacity_sink_minimal",
    "network_vertex_count",
    "network_edges",
)


class DinicSynapticFlowKernel:
    """
    Deterministic integer Dinic max-flow kernel with forward (`source_minimal`) and
    reverse (`sink_minimal`) residual min-cut extraction.
    """

    def __init__(self, n_vertices: int) -> None:
        n_vertices = _require_int(n_vertices, "n_vertices", hi=2 * MAX_NEURONS + MAX_PLASMIDS + 2)
        if n_vertices < 2:
            raise ValueError("Flow network requires at least source and sink vertices.")
        self.n = int(n_vertices)
        self.adj: List[List[_ResidualEdge]] = [[] for _ in range(self.n)]
        self.original_edges: List[Tuple[int, int, int]] = []

    def add_edge(self, u: int, v: int, cap: int) -> None:
        u = _require_int(u, "edge tail")
        v = _require_int(v, "edge head")
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError(f"Edge ({u}, {v}) out of vertex bounds [0, {self.n}).")
        c = _require_int(cap, "edge capacity")
        if c < 0:
            raise ValueError(f"Edge capacity must be non-negative, got {cap}.")
        fwd = _ResidualEdge(to=v, rev=len(self.adj[v]), cap=c, flow=0)
        bwd = _ResidualEdge(to=u, rev=len(self.adj[u]), cap=0, flow=0)
        self.adj[u].append(fwd)
        self.adj[v].append(bwd)
        if c > 0:
            self.original_edges.append((u, v, c))

    def _bfs_levels(self, source: int, sink: int) -> List[int]:
        level = [-1] * self.n
        level[source] = 0
        q = deque([source])
        while q:
            u = q.popleft()
            for e in self.adj[u]:
                if e.cap - e.flow > 0 and level[e.to] < 0:
                    level[e.to] = level[u] + 1
                    q.append(e.to)
        return level

    def _augment_once(self, source: int, sink: int, level: List[int], ptr: List[int]) -> int:
        """
        Finds one augmenting path in the level graph and pushes its bottleneck.
        Iterative, so path length is bounded by memory rather than the recursion limit.
        """
        path: List[_ResidualEdge] = []
        u = source
        while True:
            if u == sink:
                pushed = min(e.cap - e.flow for e in path)
                for e in path:
                    e.flow += pushed
                    self.adj[e.to][e.rev].flow -= pushed
                return pushed
            advanced = False
            adj_u = self.adj[u]
            while ptr[u] < len(adj_u):
                e = adj_u[ptr[u]]
                if level[e.to] == level[u] + 1 and e.cap - e.flow > 0:
                    path.append(e)
                    u = e.to
                    advanced = True
                    break
                ptr[u] += 1
            if advanced:
                continue
            if not path:
                return 0
            # Dead end: retreat one edge and skip it from the parent.
            level[u] = -1
            last = path.pop()
            u = self.adj[last.to][last.rev].to
            ptr[u] += 1

    def solve_max_flow(self, source: int, sink: int) -> int:
        if source == sink:
            raise ValueError("Source and sink must be distinct vertices.")
        total_flow = 0
        while True:
            level = self._bfs_levels(source, sink)
            if level[sink] < 0:
                break
            ptr = [0] * self.n
            while True:
                pushed = self._augment_once(source, sink, level, ptr)
                if pushed == 0:
                    break
                total_flow += pushed
        return total_flow

    def extract_residual_min_cut(self, source: int, sink: int, mode: str = "source_minimal") -> Tuple[int, ...]:
        """
        Extracts a canonical minimum s-t cut S (with `source in S`, `sink not in S`):
          - `source_minimal`: unique inclusion-minimal s-t min-cut (reachable from `source` in G_f).
          - `sink_minimal`: unique inclusion-maximal s-t min-cut (complement of vertices reaching
            `sink` in the reverse residual graph G_f^R).
        """
        if mode == "source_minimal":
            visited = {source}
            q = deque([source])
            while q:
                u = q.popleft()
                for e in self.adj[u]:
                    if e.cap - e.flow > 0 and e.to not in visited:
                        visited.add(e.to)
                        q.append(e.to)
            return tuple(sorted(visited))

        if mode == "sink_minimal":
            can_reach_sink = {sink}
            q = deque([sink])
            while q:
                v = q.popleft()
                for back_e in self.adj[v]:
                    u = back_e.to
                    fwd_e = self.adj[u][back_e.rev]
                    if fwd_e.cap - fwd_e.flow > 0 and u not in can_reach_sink:
                        can_reach_sink.add(u)
                        q.append(u)
            return tuple(sorted(i for i in range(self.n) if i not in can_reach_sink))

        raise ValueError(f"Unsupported cut selection mode {mode!r}; expected 'source_minimal' or 'sink_minimal'.")


def compute_cut_capacity(edges: Iterable[Tuple[int, int, int]], s_cut: Set[int]) -> int:
    cap_sum = 0
    for u, v, cap in edges:
        if u in s_cut and v not in s_cut:
            cap_sum += int(cap)
    return cap_sum


def _digest_min_cut_payload(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


MIN_CUT_DIGEST_SCHEMA = "WEFT-PLASM-MINCUT/2"


def _min_cut_digest_body(fields: Mapping[str, Any]) -> Dict[str, Any]:
    """Every certificate field except the digest itself, so no field can change unsealed."""
    def _tuples(x: Any) -> Any:
        if isinstance(x, (tuple, list)):
            return [_tuples(i) for i in x]
        if _is_int(x):
            return int(x)
        return x

    body = {k: _tuples(fields[k]) for k in _MIN_CUT_FIELDS}
    body["schema"] = MIN_CUT_DIGEST_SCHEMA
    return body


def min_cut_certificate_digest(cert: "MinCutMitosisCertificate") -> str:
    """SHA-256 over every field of `cert` except `sha256_digest`."""
    return _digest_min_cut_payload(_min_cut_digest_body({k: getattr(cert, k) for k in _MIN_CUT_FIELDS}))


def allocate_disjoint_synaptic_corridors(
    fisher_sensitivity: Any,
    plasmid_demands: Sequence[int],
    *,
    core_rows: Optional[int] = None,
    locked_mask: Optional[Any] = None,
    max_fisher_threshold: Optional[float] = None,
    allowed_corridors: Optional[Sequence[Sequence[int]]] = None,
) -> MinCutMitosisCertificate:
    """
    Routes `K = len(plasmid_demands)` horizontal skill plasmids across `M = len(fisher_sensitivity)`
    channels using a vertex-split (`j_in -> j_out` capacity 1) Dinic network.

    Strictly enforces `weft.runtime.plasm` core-freezing (`0 .. core_rows - 1` where
    `core_rows` defaults to `M // 4` matching `compute_plasticity_mask`) and `locked_mask != 0`.
    """
    try:
        scores = _to_numpy_f64(fisher_sensitivity).ravel()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"fisher_sensitivity must be numeric: {exc}") from None
    if scores.size == 0 or not np.all(np.isfinite(scores)):
        raise ValueError("fisher_sensitivity must be a non-empty finite 1-D sequence.")
    M = int(scores.size)
    if M > MAX_NEURONS:
        raise ValueError(f"fisher_sensitivity has {M} entries; the limit is {MAX_NEURONS}.")

    c_rows = (M // 4) if core_rows is None else _require_int(core_rows, "core_rows")
    if c_rows < 0 or c_rows > M:
        raise ValueError(f"core_rows={c_rows} out of bounds for M={M}.")

    if isinstance(plasmid_demands, (str, bytes, Mapping)) or not isinstance(plasmid_demands, Sequence):
        raise ValueError("plasmid_demands must be a sequence of non-negative integers.")
    if len(plasmid_demands) > MAX_PLASMIDS:
        raise ValueError(f"{len(plasmid_demands)} plasmids exceeds the limit of {MAX_PLASMIDS}.")
    demands = tuple(_require_int(d, "plasmid demand", lo=0, hi=MAX_DEMAND) for d in plasmid_demands)

    if max_fisher_threshold is not None:
        if isinstance(max_fisher_threshold, (bool, np.bool_)) or not isinstance(max_fisher_threshold, (int, float, np.integer, np.floating)):
            raise ValueError("max_fisher_threshold must be a finite number.")
        if not math.isfinite(float(max_fisher_threshold)):
            raise ValueError("max_fisher_threshold must be a finite number.")
    if allowed_corridors is not None:
        if len(allowed_corridors) != len(demands):
            raise ValueError(
                f"allowed_corridors has {len(allowed_corridors)} entries for {len(demands)} plasmids."
            )
        corridors_checked: List[Tuple[int, ...]] = []
        for k, row in enumerate(allowed_corridors):
            if isinstance(row, (str, bytes, Mapping)):
                raise ValueError(f"allowed_corridors[{k}] must be a sequence of neuron indices.")
            corridors_checked.append(
                tuple(_require_int(j, f"allowed_corridors[{k}] entry", lo=0, hi=M - 1) for j in row)
            )
        allowed_corridors = corridors_checked

    frozen_set: Set[int] = set(range(c_rows))
    if locked_mask is not None:
        mask_arr = np.asarray(_to_numpy_f64(locked_mask)).ravel()
        if mask_arr.size != M:
            raise ValueError(f"locked_mask length {mask_arr.size} != M={M}.")
        for idx in range(M):
            if mask_arr[idx] != 0.0:
                frozen_set.add(idx)

    eligible: List[int] = []
    for idx in range(M):
        if idx in frozen_set:
            continue
        if max_fisher_threshold is not None and float(scores[idx]) > float(max_fisher_threshold):
            continue
        eligible.append(idx)

    # Canonical tie-broken ordering: quietest Fisher sensitivity first, then neuron index
    eligible.sort(key=lambda idx: (float(scores[idx]), idx))
    eligible_set = set(eligible)

    K = len(demands)
    if K * len(eligible) + 2 * len(eligible) + K > MAX_NETWORK_EDGES:
        raise ValueError("Routing network would exceed MAX_NETWORK_EDGES.")
    src = 0
    snk = 1 + K + 2 * M
    kernel = DinicSynapticFlowKernel(snk + 1)

    for k, dem in enumerate(demands):
        if dem > 0:
            kernel.add_edge(src, 1 + k, dem)

    # Split each eligible plastic neuron j into j_in -> j_out with unit capacity 1
    for j in eligible:
        vin = 1 + K + j
        vout = 1 + K + M + j
        kernel.add_edge(vin, vout, 1)
        kernel.add_edge(vout, snk, 1)

    for k in range(K):
        if allowed_corridors is not None:
            cand_js = sorted({j for j in allowed_corridors[k] if j in eligible_set})
            # Sort in ascending Fisher sensitivity order so augmenting paths prefer quietest slots
            cand_js.sort(key=lambda idx: (float(scores[idx]), idx))
        else:
            cand_js = eligible
        for j in cand_js:
            kernel.add_edge(1 + k, 1 + K + j, 1)

    max_flow = kernel.solve_max_flow(src, snk) if sum(demands) > 0 else 0
    s_min = kernel.extract_residual_min_cut(src, snk, "source_minimal")
    t_min = kernel.extract_residual_min_cut(src, snk, "sink_minimal")

    cap_s = compute_cut_capacity(kernel.original_edges, set(s_min))
    cap_t = compute_cut_capacity(kernel.original_edges, set(t_min))

    assigned_lists: List[Tuple[int, ...]] = []
    for k in range(K):
        slots_k: List[int] = []
        for e in kernel.adj[1 + k]:
            if e.cap == 1 and e.flow == 1 and (1 + K) <= e.to < (1 + K + M):
                slots_k.append(e.to - (1 + K))
        assigned_lists.append(tuple(sorted(slots_k)))

    total_demand = int(sum(demands))
    deficit = max(0, total_demand - max_flow)
    frozen_tuple = tuple(sorted(frozen_set))
    eligible_tuple = tuple(sorted(eligible))
    edges_tuple = tuple(kernel.original_edges)

    digest = _digest_min_cut_payload(_min_cut_digest_body({
        "total_neurons": M,
        "core_rows_frozen": c_rows,
        "frozen_indices": frozen_tuple,
        "eligible_indices": eligible_tuple,
        "plasmid_demands": demands,
        "total_demand": total_demand,
        "max_flow": max_flow,
        "deficit": deficit,
        "requires_mitosis": deficit > 0,
        "assignments": tuple(assigned_lists),
        "source_minimal_cut": s_min,
        "sink_minimal_cut": t_min,
        "cut_capacity_source_minimal": cap_s,
        "cut_capacity_sink_minimal": cap_t,
        "network_vertex_count": snk + 1,
        "network_edges": edges_tuple,
    }))

    return MinCutMitosisCertificate(
        total_neurons=M,
        core_rows_frozen=c_rows,
        frozen_indices=frozen_tuple,
        eligible_indices=eligible_tuple,
        plasmid_demands=demands,
        total_demand=total_demand,
        max_flow=max_flow,
        deficit=deficit,
        requires_mitosis=(deficit > 0),
        assignments=tuple(assigned_lists),
        source_minimal_cut=s_min,
        sink_minimal_cut=t_min,
        cut_capacity_source_minimal=cap_s,
        cut_capacity_sink_minimal=cap_t,
        network_vertex_count=snk + 1,
        network_edges=edges_tuple,
        sha256_digest=digest,
    )


def _int_seq(x: Any, *, lo: int, hi: int, limit: int) -> Optional[Tuple[int, ...]]:
    """A tuple of ints in [lo, hi] from a list or tuple, or None if anything is off."""
    if not isinstance(x, (tuple, list)) or len(x) > limit:
        return None
    out = []
    for v in x:
        if not _is_int(v) or not (lo <= int(v) <= hi):
            return None
        out.append(int(v))
    return tuple(out)


def verify_min_cut_mitosis_certificate(cert: MinCutMitosisCertificate) -> Dict[str, Any]:
    """
    Independent fail-closed verifier for `MinCutMitosisCertificate` (`cut_certificate.py` analog).

    Trusts nothing the certificate states about optimality. It checks that
    `network_edges` is exactly the vertex-split network the builder would emit for
    the recorded demands and eligible slots (non-negative capacities, in-range
    vertices, unit split, an edge to the sink for each slot), rebuilds the s-t flow
    the assignments describe, and recomputes both residual min cuts from that flow.
    A flow whose value equals a cut's capacity is maximum, so `max_flow`, `deficit`
    and `requires_mitosis` follow from the network rather than from the peer.
    Malformed input returns a reason; it never raises.
    """
    if not isinstance(cert, MinCutMitosisCertificate):
        return {"ok": False, "reason": "not_a_min_cut_certificate"}

    # 0. Types and bounds, before anything is allocated from peer-supplied sizes.
    if not _is_int(cert.total_neurons) or not (1 <= int(cert.total_neurons) <= MAX_NEURONS):
        return {"ok": False, "reason": "invalid_vertex_layout"}
    M = int(cert.total_neurons)
    if not _is_int(cert.core_rows_frozen) or not (0 <= int(cert.core_rows_frozen) <= M):
        return {"ok": False, "reason": "core_rows_out_of_range"}
    c_rows = int(cert.core_rows_frozen)
    demands = _int_seq(cert.plasmid_demands, lo=0, hi=MAX_DEMAND, limit=MAX_PLASMIDS)
    if demands is None:
        if isinstance(cert.plasmid_demands, (tuple, list)) and any(
            _is_int(d) and int(d) < 0 for d in cert.plasmid_demands
        ):
            return {"ok": False, "reason": "negative_demand"}
        return {"ok": False, "reason": "malformed_plasmid_demands"}
    K = len(demands)
    for name in ("total_demand", "max_flow", "deficit", "cut_capacity_source_minimal",
                 "cut_capacity_sink_minimal", "network_vertex_count"):
        if not _is_int(getattr(cert, name)):
            return {"ok": False, "reason": f"malformed_{name}"}
    if not isinstance(cert.requires_mitosis, bool):
        return {"ok": False, "reason": "malformed_requires_mitosis"}
    if not isinstance(cert.sha256_digest, str):
        return {"ok": False, "reason": "malformed_sha256_digest"}

    src = 0
    snk = int(cert.network_vertex_count) - 1
    if snk != 1 + K + 2 * M:
        return {"ok": False, "reason": "invalid_vertex_layout"}
    if cert.total_demand != sum(demands):
        return {"ok": False, "reason": "demand_sum_mismatch"}
    if cert.max_flow < 0 or cert.max_flow > cert.total_demand:
        return {"ok": False, "reason": "invalid_max_flow_bounds"}
    expected_deficit = cert.total_demand - cert.max_flow
    if cert.deficit != expected_deficit or cert.requires_mitosis != (expected_deficit > 0):
        return {"ok": False, "reason": "mitosis_deficit_mismatch"}

    frozen = _int_seq(cert.frozen_indices, lo=0, hi=M - 1, limit=M)
    eligible = _int_seq(cert.eligible_indices, lo=0, hi=M - 1, limit=M)
    if frozen is None or eligible is None or len(set(frozen)) != len(frozen) or len(set(eligible)) != len(eligible):
        return {"ok": False, "reason": "malformed_index_sets"}
    frozen_set = set(frozen)
    eligible_set = set(eligible)
    if frozen_set & eligible_set:
        return {"ok": False, "reason": "frozen_core_in_eligible_pool"}
    if any(j not in frozen_set for j in range(c_rows)):
        return {"ok": False, "reason": "core_rows_missing_from_frozen_set"}

    s_cut = _int_seq(cert.source_minimal_cut, lo=0, hi=snk, limit=snk + 1)
    t_cut = _int_seq(cert.sink_minimal_cut, lo=0, hi=snk, limit=snk + 1)
    if s_cut is None or t_cut is None:
        return {"ok": False, "reason": "malformed_cut"}
    s_set = set(s_cut)
    t_set = set(t_cut)
    if src not in s_set or snk in s_set or src not in t_set or snk in t_set:
        return {"ok": False, "reason": "invalid_cut_endpoints"}
    if not s_set.issubset(t_set):
        return {"ok": False, "reason": "source_minimal_not_subset_of_sink_minimal"}

    # 1. The network must be exactly the vertex-split routing network.
    if not isinstance(cert.network_edges, (tuple, list)) or len(cert.network_edges) > MAX_NETWORK_EDGES:
        return {"ok": False, "reason": "malformed_network_edges"}
    cap: Dict[Tuple[int, int], int] = {}
    for edge in cert.network_edges:
        if not isinstance(edge, (tuple, list)) or len(edge) != 3 or not all(_is_int(x) for x in edge):
            return {"ok": False, "reason": "malformed_network_edges"}
        u, v, c = (int(x) for x in edge)
        if not (0 <= u <= snk and 0 <= v <= snk) or u == v:
            return {"ok": False, "reason": "edge_vertex_out_of_range"}
        if c < 0:
            return {"ok": False, "reason": "negative_edge_capacity"}
        if c == 0:
            return {"ok": False, "reason": "zero_capacity_edge"}
        if (u, v) in cap:
            return {"ok": False, "reason": "duplicate_network_edge"}
        cap[(u, v)] = c

    def vin(j: int) -> int:
        return 1 + K + j

    def vout(j: int) -> int:
        return 1 + K + M + j

    expected_fixed: Dict[Tuple[int, int], int] = {}
    for k, d in enumerate(demands):
        if d > 0:
            expected_fixed[(src, 1 + k)] = d
    for j in eligible:
        expected_fixed[(vin(j), vout(j))] = 1
        expected_fixed[(vout(j), snk)] = 1
    for key, c in expected_fixed.items():
        if cap.get(key) != c:
            return {"ok": False, "reason": "network_missing_required_edge"}
    for (u, v), c in cap.items():
        if (u, v) in expected_fixed:
            continue
        is_corridor = 1 <= u <= K and vin(0) <= v < vin(M) and (v - vin(0)) in eligible_set and c == 1
        if not is_corridor:
            return {"ok": False, "reason": "unexpected_network_edge"}

    # 2. Assignments must be an integral s-t flow on that network.
    if not isinstance(cert.assignments, (tuple, list)) or len(cert.assignments) != K:
        return {"ok": False, "reason": "assignment_count_mismatch"}
    flow: Dict[Tuple[int, int], int] = {}
    seen_slots: Set[int] = set()
    routed_total = 0
    for k, slots in enumerate(cert.assignments):
        slots_t = _int_seq(slots, lo=-(1 << 62), hi=1 << 62, limit=M)
        if slots_t is None:
            return {"ok": False, "reason": "malformed_assignments"}
        if len(slots_t) > demands[k]:
            return {"ok": False, "reason": "plasmid_assignment_exceeds_demand"}
        for j in slots_t:
            if j in frozen_set or j not in eligible_set:
                return {"ok": False, "reason": "slot_violates_frozen_or_eligible_mask"}
            if j in seen_slots:
                return {"ok": False, "reason": "hall_stacking_slot_collision"}
            if cap.get((1 + k, vin(j)), 0) < 1:
                return {"ok": False, "reason": "missing_network_corridor_edge"}
            seen_slots.add(j)
            routed_total += 1
            for e in ((1 + k, vin(j)), (vin(j), vout(j)), (vout(j), snk)):
                flow[e] = flow.get(e, 0) + 1
        if slots_t:
            flow[(src, 1 + k)] = len(slots_t)

    if routed_total != cert.max_flow:
        return {"ok": False, "reason": "assignment_total_does_not_equal_max_flow"}

    # 3. Recompute both residual min cuts from that flow. If the flow's value equals
    #    a cut's capacity, the flow is maximum and the cut is minimum.
    out_res: List[List[int]] = [[] for _ in range(snk + 1)]
    in_res: List[List[int]] = [[] for _ in range(snk + 1)]
    for (u, v), c in cap.items():
        f = flow.get((u, v), 0)
        if f < c:  # forward residual u -> v
            out_res[u].append(v)
            in_res[v].append(u)
        if f > 0:  # backward residual v -> u
            out_res[v].append(u)
            in_res[u].append(v)

    reach = {src}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in out_res[u]:
            if v not in reach:
                reach.add(v)
                q.append(v)
    if snk in reach:
        return {"ok": False, "reason": "max_flow_not_maximum"}
    co_reach = {snk}
    q = deque([snk])
    while q:
        v = q.popleft()
        for u in in_res[v]:
            if u not in co_reach:
                co_reach.add(u)
                q.append(u)
    s_expected = reach
    t_expected = set(range(snk + 1)) - co_reach

    cap_s = compute_cut_capacity(((u, v, c) for (u, v), c in cap.items()), s_expected)
    cap_t = compute_cut_capacity(((u, v, c) for (u, v), c in cap.items()), t_expected)
    if cap_s != routed_total or cap_t != routed_total:
        return {"ok": False, "reason": "cut_capacity_does_not_match_max_flow"}
    if s_set != s_expected or t_set != t_expected:
        return {"ok": False, "reason": "cut_not_residual_min_cut"}
    if cap_s != cert.cut_capacity_source_minimal or cap_t != cert.cut_capacity_sink_minimal:
        return {"ok": False, "reason": "recorded_cut_capacity_mismatch"}

    # 4. Canonical SHA-256 over every field, network_edges included.
    try:
        expected_digest = min_cut_certificate_digest(cert)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "malformed_certificate"}
    if cert.sha256_digest != expected_digest:
        return {"ok": False, "reason": "sha256_digest_mismatch"}

    return {
        "ok": True,
        "reason": "verified",
        "max_flow": int(cert.max_flow),
        "deficit": int(cert.deficit),
        "requires_mitosis": cert.requires_mitosis,
    }


def expand_weights_orthogonal_mitosis(
    weights: Any,
    deficit_rows: int,
    deficit_cols: int = 0,
    *,
    core_rows: Optional[int] = None,
) -> Tuple[Any, Dict[str, Any]]:
    """
    Expands a 2-D weight matrix `weights` (`shape = (rows, cols)`) by appending exact-deficit
    zero-initialized peripheral rows (`deficit_rows`) and/or columns (`deficit_cols`),
    guaranteeing `core_row_drift == 0.0` on `weights[:core_rows]` and `0.0` Frobenius norm change.
    """
    w_np = _to_numpy_f64(weights)
    if w_np.ndim != 2:
        raise ValueError(f"Expected 2-D weight matrix, got shape {w_np.shape}.")
    r_add = _require_int(deficit_rows, "deficit_rows", hi=MAX_NEURONS)
    c_add = _require_int(deficit_cols, "deficit_cols", hi=MAX_NEURONS)
    if r_add < 0 or c_add < 0:
        raise ValueError("Mitosis deficits must be non-negative.")

    orig_r, orig_c = w_np.shape
    c_rows = (orig_r // 4) if core_rows is None else _require_int(core_rows, "core_rows")
    if c_rows < 0 or c_rows > orig_r:
        raise ValueError(f"core_rows={c_rows} out of bounds for {orig_r} rows.")
    expanded = np.zeros((orig_r + r_add, orig_c + c_add), dtype=np.float64)
    expanded[:orig_r, :orig_c] = w_np

    core_drift = float(np.linalg.norm(expanded[:c_rows, :orig_c] - w_np[:c_rows, :orig_c]))
    restored = _restore_like(expanded, weights)
    return restored, {
        "original_shape": (orig_r, orig_c),
        "expanded_shape": (orig_r + r_add, orig_c + c_add),
        "core_rows_protected": c_rows,
        "core_row_drift": core_drift,
        "added_frobenius_norm": 0.0,
    }


# =============================================================================
# 3. Exact `fractions.Fraction` Cost-Partitioned & Farkas Dual Certificates
# =============================================================================

@dataclass(frozen=True)
class FractionDualCertificate:
    """
    Zero-float-TCB certificate for metabolic budget debits, additive cost-partitioned
    subspace drift bounds, and Farkas linear infeasibility witnesses (`A x <= b` UNSAT).
    All quantities are stored as canonical `"num/den"` strings so serialization is 100% lossless.
    """
    initial_budget_q: str
    step_costs_q: Tuple[str, ...]
    remaining_budget_q: str
    quotient_weights_q: Tuple[str, ...]
    quotient_drifts_q: Tuple[str, ...]
    partitioned_drift_q: str
    drift_cap_q: str
    farkas_matrix_q: Optional[Tuple[Tuple[str, ...], ...]]
    farkas_rhs_q: Optional[Tuple[str, ...]]
    farkas_multipliers_q: Optional[Tuple[str, ...]]
    sha256_digest: str


def _fmt_q(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


def _digest_fraction_cert(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def certify_cost_partitioned_dual(
    initial_budget: Union[int, float, str, Fraction],
    step_costs: Sequence[Union[int, float, str, Fraction]],
    quotient_drifts: Sequence[Union[int, float, str, Fraction]],
    drift_cap: Union[int, float, str, Fraction],
    *,
    quotient_weights: Optional[Sequence[Union[int, float, str, Fraction]]] = None,
    farkas_system: Optional[Tuple[Sequence[Sequence[Union[int, float, str, Fraction]]], Sequence[Union[int, float, str, Fraction]], Sequence[Union[int, float, str, Fraction]]]] = None,
) -> FractionDualCertificate:
    """
    Constructs and validates an exact `fractions.Fraction` certificate:
      - Converts any float inputs via exact IEEE-754 `Fraction.from_float` (no string rounding!).
      - Enforces `initial_budget > 0`, every `step_cost > 0` (preventing both negative-cost
        budget minting and zero-cost Zeno stagnation in exact Q!), and `remaining_budget >= 0`.
      - Enforces exact unit-partition weights `alpha_m >= 0`, `sum_m alpha_m == 1`, and
        additive cost-partitioned bound `sum_m alpha_m * drift_m <= drift_cap`.
      - Optionally certifies Farkas Lemma infeasibility (`lambda >= 0`, `lambda^T A == 0`,
        `lambda^T b < 0`) for infeasible linear constraint systems `A x <= b`.
    """
    for name, seq in (("step_costs", step_costs), ("quotient_drifts", quotient_drifts)):
        if isinstance(seq, (str, bytes, Mapping)) or not isinstance(seq, (Sequence, np.ndarray)):
            raise ValueError(f"{name} must be a sequence.")
        if len(seq) > MAX_RATIONAL_TERMS:
            raise ValueError(f"{name} exceeds MAX_RATIONAL_TERMS.")
    b0 = _exact_nonneg_fraction(initial_budget)
    if b0 <= Fraction(0, 1):
        raise ValueError(f"initial_budget must be strictly positive, got {b0}.")

    costs_q: List[Fraction] = []
    rem = b0
    for c in step_costs:
        cq = _exact_fraction(c)
        if cq <= Fraction(0, 1):
            raise ValueError(f"Each step_cost must be strictly positive (got {cq}); negative/zero costs forbidden.")
        rem = rem - cq
        if rem < Fraction(0, 1):
            raise ValueError(f"Metabolic budget exhausted: remaining {rem} < 0.")
        costs_q.append(cq)

    if len(quotient_drifts) == 0:
        raise ValueError("quotient_drifts must be non-empty.")
    drifts_q = [_exact_fraction(d) for d in quotient_drifts]
    if any(d < Fraction(0, 1) for d in drifts_q):
        raise ValueError("quotient_drifts must be non-negative.")

    M_q = len(drifts_q)
    if quotient_weights is None:
        weights_q = [Fraction(1, M_q) for _ in range(M_q)]
    else:
        if len(quotient_weights) != M_q:
            raise ValueError("quotient_weights length must match quotient_drifts.")
        weights_q = [_exact_fraction(w) for w in quotient_weights]
        if any(w < Fraction(0, 1) for w in weights_q) or sum(weights_q) != Fraction(1, 1):
            raise ValueError("quotient_weights must be non-negative and sum identically to 1.")

    cap_q = _exact_nonneg_fraction(drift_cap)
    part_drift = sum((w * d for w, d in zip(weights_q, drifts_q)), Fraction(0, 1))
    if part_drift > cap_q:
        raise ValueError(f"Cost-partitioned drift {part_drift} exceeds drift_cap {cap_q}.")

    f_mat_s: Optional[Tuple[Tuple[str, ...], ...]] = None
    f_rhs_s: Optional[Tuple[str, ...]] = None
    f_mul_s: Optional[Tuple[str, ...]] = None

    if farkas_system is not None:
        try:
            A_raw, b_raw, lam_raw = farkas_system
        except (TypeError, ValueError):
            raise ValueError("farkas_system must be a triple (A, b, lambda).") from None
        for name, part in (("A", A_raw), ("b", b_raw), ("lambda", lam_raw)):
            if isinstance(part, (str, bytes, Mapping)) or not isinstance(part, (Sequence, np.ndarray)):
                raise ValueError(f"Farkas {name} must be a sequence.")
            if len(part) > MAX_RATIONAL_TERMS:
                raise ValueError(f"Farkas {name} exceeds MAX_RATIONAL_TERMS.")
        rows_raw = []
        for row in A_raw:
            if isinstance(row, (str, bytes, Mapping)) or not isinstance(row, (Sequence, np.ndarray)):
                raise ValueError("farkas_dimension_mismatch: every Farkas row must be a sequence.")
            rows_raw.append(row)
        if sum(len(r) for r in rows_raw) > MAX_RATIONAL_TERMS:
            raise ValueError("Farkas matrix exceeds MAX_RATIONAL_TERMS.")
        # A and b carry signed entries; only the multipliers must be non-negative.
        A_q = [[_exact_fraction(val) for val in row] for row in rows_raw]
        b_q = [_exact_fraction(val) for val in b_raw]
        lam_q = [_exact_fraction(val) for val in lam_raw]
        if len(A_q) == 0 or len(A_q) != len(b_q) or len(lam_q) != len(A_q):
            raise ValueError("farkas_dimension_mismatch: Malformed Farkas system dimensions.")
        n_cols = len(A_q[0])
        if n_cols == 0 or any(len(row) != n_cols for row in A_q):
            raise ValueError("farkas_dimension_mismatch: the Farkas matrix must be rectangular with at least one column.")
        if any(l < Fraction(0, 1) for l in lam_q):
            raise ValueError("Farkas dual multipliers lambda must be >= 0.")
        for col in range(n_cols):
            col_dot = sum((lam_q[row] * A_q[row][col] for row in range(len(A_q))), Fraction(0, 1))
            if col_dot != Fraction(0, 1):
                raise ValueError(f"Farkas stationarity violated on column {col}: {col_dot} != 0.")
        rhs_dot = sum((lam_q[row] * b_q[row] for row in range(len(A_q))), Fraction(0, 1))
        if rhs_dot >= Fraction(0, 1):
            raise ValueError(f"Farkas witness fails strict negativity: lambda^T b = {rhs_dot} >= 0.")

        f_mat_s = tuple(tuple(_fmt_q(v) for v in row) for row in A_q)
        f_rhs_s = tuple(_fmt_q(v) for v in b_q)
        f_mul_s = tuple(_fmt_q(v) for v in lam_q)

    init_s = _fmt_q(b0)
    costs_s = tuple(_fmt_q(c) for c in costs_q)
    rem_s = _fmt_q(rem)
    weights_s = tuple(_fmt_q(w) for w in weights_q)
    drifts_s = tuple(_fmt_q(d) for d in drifts_q)
    part_s = _fmt_q(part_drift)
    cap_s = _fmt_q(cap_q)

    digest = _digest_fraction_cert({
        "initial_budget_q": init_s,
        "step_costs_q": costs_s,
        "remaining_budget_q": rem_s,
        "quotient_weights_q": weights_s,
        "quotient_drifts_q": drifts_s,
        "partitioned_drift_q": part_s,
        "drift_cap_q": cap_s,
        "farkas_matrix_q": f_mat_s,
        "farkas_rhs_q": f_rhs_s,
        "farkas_multipliers_q": f_mul_s,
    })

    return FractionDualCertificate(
        initial_budget_q=init_s,
        step_costs_q=costs_s,
        remaining_budget_q=rem_s,
        quotient_weights_q=weights_s,
        quotient_drifts_q=drifts_s,
        partitioned_drift_q=part_s,
        drift_cap_q=cap_s,
        farkas_matrix_q=f_mat_s,
        farkas_rhs_q=f_rhs_s,
        farkas_multipliers_q=f_mul_s,
        sha256_digest=digest,
    )


def fraction_dual_certificate_digest(cert: "FractionDualCertificate") -> str:
    """SHA-256 over every field of `cert` except `sha256_digest`."""
    return _digest_fraction_cert({
        "initial_budget_q": cert.initial_budget_q,
        "step_costs_q": cert.step_costs_q,
        "remaining_budget_q": cert.remaining_budget_q,
        "quotient_weights_q": cert.quotient_weights_q,
        "quotient_drifts_q": cert.quotient_drifts_q,
        "partitioned_drift_q": cert.partitioned_drift_q,
        "drift_cap_q": cert.drift_cap_q,
        "farkas_matrix_q": cert.farkas_matrix_q,
        "farkas_rhs_q": cert.farkas_rhs_q,
        "farkas_multipliers_q": cert.farkas_multipliers_q,
    })


def _q_list(x: Any) -> Optional[List[Fraction]]:
    if not isinstance(x, (tuple, list)) or len(x) > MAX_RATIONAL_TERMS:
        return None
    out = []
    for v in x:
        q = _parse_canonical_q(v)
        if q is None:
            return None
        out.append(q)
    return out


def verify_fraction_dual_certificate(cert: FractionDualCertificate) -> Dict[str, Any]:
    """
    Standalone pure-`Fraction` verifier (zero floating-point operations in the TCB!).
    Every quantity must be a canonical `num/den` string. Malformed input returns a
    reason; it never raises.
    """
    if not isinstance(cert, FractionDualCertificate):
        return {"ok": False, "reason": "not_a_fraction_dual_certificate"}
    b0 = _parse_canonical_q(cert.initial_budget_q)
    costs = _q_list(cert.step_costs_q)
    rem_claimed = _parse_canonical_q(cert.remaining_budget_q)
    weights = _q_list(cert.quotient_weights_q)
    drifts = _q_list(cert.quotient_drifts_q)
    part_claimed = _parse_canonical_q(cert.partitioned_drift_q)
    cap = _parse_canonical_q(cert.drift_cap_q)
    if any(x is None for x in (b0, costs, rem_claimed, weights, drifts, part_claimed, cap)):
        return {"ok": False, "reason": "malformed_rational_string"}
    if not isinstance(cert.sha256_digest, str):
        return {"ok": False, "reason": "malformed_sha256_digest"}
    if b0 <= Fraction(0, 1):
        return {"ok": False, "reason": "non_positive_initial_budget"}

    rem = b0
    for c in costs:
        if c <= Fraction(0, 1):
            return {"ok": False, "reason": "non_positive_step_cost"}
        prev = rem
        rem = rem - c
        if not (rem < prev):
            return {"ok": False, "reason": "non_monotone_budget_step"}
        if rem < Fraction(0, 1):
            return {"ok": False, "reason": "budget_underflow"}
    if rem != rem_claimed:
        return {"ok": False, "reason": "remaining_budget_mismatch"}

    if len(weights) == 0 or len(weights) != len(drifts):
        return {"ok": False, "reason": "quotient_dimension_mismatch"}
    if any(w < Fraction(0, 1) for w in weights) or sum(weights, Fraction(0, 1)) != Fraction(1, 1):
        return {"ok": False, "reason": "invalid_partition_of_unity"}
    if any(d < Fraction(0, 1) for d in drifts):
        return {"ok": False, "reason": "negative_quotient_drift"}

    part = sum((w * d for w, d in zip(weights, drifts)), Fraction(0, 1))
    if part != part_claimed or part > cap:
        return {"ok": False, "reason": "partitioned_drift_violation"}

    farkas_verified = False
    if (
        cert.farkas_matrix_q is not None
        or cert.farkas_rhs_q is not None
        or cert.farkas_multipliers_q is not None
    ):
        if (
            cert.farkas_matrix_q is None
            or cert.farkas_rhs_q is None
            or cert.farkas_multipliers_q is None
        ):
            return {"ok": False, "reason": "incomplete_farkas_tuple"}
        if not isinstance(cert.farkas_matrix_q, (tuple, list)) or len(cert.farkas_matrix_q) > MAX_RATIONAL_TERMS:
            return {"ok": False, "reason": "malformed_farkas_rational"}
        A_q = []
        for row in cert.farkas_matrix_q:
            row_q = _q_list(row)
            if row_q is None:
                return {"ok": False, "reason": "malformed_farkas_rational"}
            A_q.append(row_q)
        b_q = _q_list(cert.farkas_rhs_q)
        lam_q = _q_list(cert.farkas_multipliers_q)
        if b_q is None or lam_q is None:
            return {"ok": False, "reason": "malformed_farkas_rational"}
        if len(A_q) == 0 or len(A_q) != len(b_q) or len(lam_q) != len(A_q):
            return {"ok": False, "reason": "farkas_dimension_mismatch"}
        n_cols = len(A_q[0])
        if n_cols == 0 or any(len(row) != n_cols for row in A_q):
            return {"ok": False, "reason": "farkas_dimension_mismatch"}
        if any(l < Fraction(0, 1) for l in lam_q):
            return {"ok": False, "reason": "negative_farkas_multiplier"}
        for col in range(n_cols):
            if sum((lam_q[r] * A_q[r][col] for r in range(len(A_q))), Fraction(0, 1)) != Fraction(0, 1):
                return {"ok": False, "reason": "farkas_stationarity_failed"}
        if sum((lam_q[r] * b_q[r] for r in range(len(A_q))), Fraction(0, 1)) >= Fraction(0, 1):
            return {"ok": False, "reason": "farkas_rhs_not_negative"}
        farkas_verified = True

    try:
        expected_digest = fraction_dual_certificate_digest(cert)
    except (TypeError, ValueError):
        return {"ok": False, "reason": "malformed_certificate"}
    if cert.sha256_digest != expected_digest:
        return {"ok": False, "reason": "sha256_digest_mismatch"}

    return {
        "ok": True,
        "reason": "verified",
        "remaining_budget_q": cert.remaining_budget_q,
        "partitioned_drift_q": cert.partitioned_drift_q,
        "farkas_witness_verified": farkas_verified,
    }


def pack_certificate_lock_record(
    min_cut_cert: MinCutMitosisCertificate,
    dual_cert: FractionDualCertificate,
    *,
    lock_capacity_bytes: int = 12288,
) -> bytes:
    """
    Packs a deterministic UTF-8 JSON audit record into a fixed-length byte buffer sized for
    `StratifiedMemoryArena.cryptographic_lock` (`12,288` bytes). Note per `weft/runtime/plasm`
    I4 contract: this stores an offline-verifiable audit receipt, not an OS memory lock.
    Refuses (ValueError) a certificate that either verifier rejects.
    """
    mc_verdict = verify_min_cut_mitosis_certificate(min_cut_cert)
    if not mc_verdict["ok"]:
        raise ValueError(f"Min-cut certificate rejected: {mc_verdict['reason']}.")
    dc_verdict = verify_fraction_dual_certificate(dual_cert)
    if not dc_verdict["ok"]:
        raise ValueError(f"Fraction dual certificate rejected: {dc_verdict['reason']}.")
    lock_capacity_bytes = _require_int(lock_capacity_bytes, "lock_capacity_bytes", lo=1, hi=1 << 24)
    record = json.dumps(
        {
            "schema": "WEFT-PLASM-SOKO-LOCK/1.0",
            "min_cut_sha256": min_cut_cert.sha256_digest,
            "dual_sha256": dual_cert.sha256_digest,
            "max_flow": min_cut_cert.max_flow,
            "deficit": min_cut_cert.deficit,
            "remaining_budget_q": dual_cert.remaining_budget_q,
            "partitioned_drift_q": dual_cert.partitioned_drift_q,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(record) > lock_capacity_bytes:
        raise ValueError(f"Serialized lock receipt ({len(record)} B) exceeds capacity ({lock_capacity_bytes} B).")
    buf = bytearray(lock_capacity_bytes)
    buf[: len(record)] = record
    return bytes(buf)


# =============================================================================
# 4. Peripheral Permutation Gauge Canonizer & Issue #51 Reproducible Cycle Report
# =============================================================================

def canonicalize_peripheral_gauge(
    w_in: Any,
    w_out: Any,
    *,
    bias_in: Optional[Any] = None,
    core_rows: Optional[int] = None,
    probe_seed: int = 314159,
) -> Tuple[Any, Any, Optional[Any], Tuple[int, ...]]:
    """
    Collapses `(M - core_rows)! -> 1` peripheral hidden-channel permutation symmetry on a
    2-layer interface `y = w_out @ phi(w_in @ x + bias_in)` while holding frozen core rows
    `0 .. core_rows - 1` strictly fixed in place (`core_row_drift == 0.0` for watermarks!).
    """
    wi = _to_numpy_f64(w_in).copy()
    wo = _to_numpy_f64(w_out).copy()
    if wi.ndim != 2 or wo.ndim != 2:
        raise ValueError("w_in and w_out must be 2-D.")
    bi = _to_numpy_f64(bias_in).ravel().copy() if bias_in is not None else None

    M, d_in = wi.shape
    if M > MAX_NEURONS:
        raise ValueError(f"w_in has {M} rows; the limit is {MAX_NEURONS}.")
    if wo.shape[1] != M:
        raise ValueError(f"w_out columns ({wo.shape[1]}) must equal w_in rows ({M}).")
    if bi is not None and bi.size != M:
        raise ValueError(f"bias_in has {bi.size} entries; expected {M}.")
    for name, arr in (("w_in", wi), ("w_out", wo), ("bias_in", bi)):
        if arr is not None and not np.all(np.isfinite(arr)):
            raise ValueError(f"{name} must be finite.")
    c_rows = (M // 4) if core_rows is None else _require_int(core_rows, "core_rows")
    if c_rows < 0 or c_rows > M:
        raise ValueError(f"Invalid core_rows={c_rows} for M={M}.")
    seed = _require_int(probe_seed, "probe_seed", lo=0)

    rng = np.random.default_rng(seed)
    X_probe = rng.normal(0.0, 1.0, size=(64, d_in))
    anchor = rng.normal(0.0, 1.0, size=64)

    # Smooth GELU probe signature, computed one unit at a time from a fresh copy of
    # that unit's parameters, so equal units get bit-identical keys wherever they sit.
    P = M - c_rows
    keys = np.empty(P, dtype=np.float64)
    for p_idx in range(P):
        j = c_rows + p_idx
        row = np.array(wi[j, :], dtype=np.float64, copy=True)
        pre = X_probe @ row
        if bi is not None:
            pre = pre + bi[j]
        act = pre * (1.0 / (1.0 + np.exp(-1.702 * np.clip(pre, -20.0, 20.0))))
        keys[p_idx] = float(anchor @ act + 1e-3 * np.sum(act ** 2))

    # Ties on the probe key (identical incoming rows and biases) are broken by the
    # unit's exact parameters, outgoing column included, so the canonical form does
    # not depend on input order.
    tie_cols = [wi[c_rows:, c] for c in range(d_in)]
    if bi is not None:
        tie_cols.append(bi[c_rows:])
    tie_cols.extend(wo[r, c_rows:] for r in range(wo.shape[0]))
    periph_perm = np.lexsort(tuple(reversed(tie_cols)) + (keys,)) + c_rows
    full_order = np.concatenate([np.arange(c_rows, dtype=int), periph_perm]).astype(int)

    wi_c = wi[full_order, :]
    wo_c = wo[:, full_order]
    bi_c = bi[full_order] if bi is not None else None

    return (
        _restore_like(wi_c, w_in),
        _restore_like(wo_c, w_out),
        _restore_like(bi_c, bias_in) if bi_c is not None else None,
        tuple(int(idx) for idx in full_order),
    )


def build_reproducible_plasm_report(
    *,
    seed: int,
    backend: str,
    effective_config: Mapping[str, Any],
    iterations_requested: int,
    proposed_candidate_metrics: Optional[Mapping[str, Any]],
    committed: bool,
    committed_state_metrics: Mapping[str, Any],
    min_cut_cert: Optional[MinCutMitosisCertificate] = None,
    dual_cert: Optional[FractionDualCertificate] = None,
) -> Dict[str, Any]:
    """
    Builds an Issue #51-compliant Plasm execution report that strictly separates:
      1. `effective_config` (parameters actually executed, never unforwarded CLI echoes),
      2. `proposed_candidate` (may be None on 0-iteration runs or rejected on failed gates),
      3. `committed_state` (unchanged baseline metrics whenever `committed == False`),
      4. `backend` (explicit `'cpu'` or `'mps'`, never conflated).
    """
    if backend not in ("cpu", "mps", "cuda"):
        raise ValueError(f"Explicit execution backend required ('cpu', 'mps', 'cuda'), got {backend!r}.")
    if not isinstance(committed, bool):
        raise ValueError(f"committed must be a bool, got {type(committed).__name__} {committed!r}.")
    seed = _require_int(seed, "seed")
    iters = _require_int(iterations_requested, "iterations_requested")
    if iters < 0:
        raise ValueError("iterations_requested must be >= 0.")
    if not isinstance(effective_config, Mapping) or not isinstance(committed_state_metrics, Mapping):
        raise ValueError("effective_config and committed_state_metrics must be mappings.")
    if proposed_candidate_metrics is not None and not isinstance(proposed_candidate_metrics, Mapping):
        raise ValueError("proposed_candidate_metrics must be a mapping or None.")
    if min_cut_cert is not None and not isinstance(min_cut_cert, MinCutMitosisCertificate):
        raise ValueError("min_cut_cert must be a MinCutMitosisCertificate or None.")
    if dual_cert is not None and not isinstance(dual_cert, FractionDualCertificate):
        raise ValueError("dual_cert must be a FractionDualCertificate or None.")
    if iters == 0 and committed:
        raise ValueError("Zero-iteration run cannot claim committed=True.")

    report = {
        "schema": "WEFT-PLASM-REPORT/2.0",
        "seed": seed,
        "backend": backend,
        "iterations_executed": iters,
        "zero_iteration_noop": (iters == 0),
        "effective_config": dict(effective_config),
        "committed": committed,
        "proposed_candidate": dict(proposed_candidate_metrics) if proposed_candidate_metrics is not None else None,
        "committed_state": dict(committed_state_metrics),
        "min_cut_certificate_sha256": min_cut_cert.sha256_digest if min_cut_cert is not None else None,
        "fraction_dual_certificate_sha256": dual_cert.sha256_digest if dual_cert is not None else None,
    }
    try:
        report["report_sha256"] = _digest_fraction_cert(report)
    except ValueError:
        raise ValueError("Report contains NaN or Infinity; reports must be strict JSON.") from None
    except TypeError as exc:
        raise ValueError(f"Report contains a value that is not JSON: {exc}") from None
    return report


__all__ = [
    "DinicSynapticFlowKernel",
    "FractionDualCertificate",
    "MinCutMitosisCertificate",
    "allocate_disjoint_synaptic_corridors",
    "build_reproducible_plasm_report",
    "canonicalize_peripheral_gauge",
    "certify_cost_partitioned_dual",
    "compute_cut_capacity",
    "expand_weights_orthogonal_mitosis",
    "fraction_dual_certificate_digest",
    "min_cut_certificate_digest",
    "pack_certificate_lock_record",
    "verify_fraction_dual_certificate",
    "verify_min_cut_mitosis_certificate",
]
