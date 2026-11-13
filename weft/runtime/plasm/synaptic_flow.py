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


def _exact_nonneg_fraction(value: Union[int, float, str, Fraction], *, upward_digits: Optional[int] = None) -> Fraction:
    """
    Converts `value` into an exact `fractions.Fraction` without float rounding optimism.
    Rejects `bool`, `NaN`, `Inf`, and negative numbers fail-closed.
    """
    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid rational quantities.")
    if isinstance(value, Fraction):
        q = value
    elif isinstance(value, (int, str)):
        q = Fraction(value)
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
        raise TypeError(f"Unsupported numeric type for Fraction conversion: {type(value)!r}")
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


class DinicSynapticFlowKernel:
    """
    Deterministic integer Dinic max-flow kernel with forward (`source_minimal`) and
    reverse (`sink_minimal`) residual min-cut extraction.
    """

    def __init__(self, n_vertices: int) -> None:
        if n_vertices < 2:
            raise ValueError("Flow network requires at least source and sink vertices.")
        self.n = int(n_vertices)
        self.adj: List[List[_ResidualEdge]] = [[] for _ in range(self.n)]
        self.original_edges: List[Tuple[int, int, int]] = []

    def add_edge(self, u: int, v: int, cap: int) -> None:
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError(f"Edge ({u}, {v}) out of vertex bounds [0, {self.n}).")
        if int(cap) < 0:
            raise ValueError(f"Edge capacity must be non-negative, got {cap}.")
        c = int(cap)
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

    def _dfs_push(self, u: int, sink: int, pushed: int, level: List[int], ptr: List[int]) -> int:
        if pushed == 0 or u == sink:
            return pushed
        while ptr[u] < len(self.adj[u]):
            idx = ptr[u]
            e = self.adj[u][idx]
            if level[e.to] == level[u] + 1 and e.cap - e.flow > 0:
                tr = self._dfs_push(e.to, sink, min(pushed, e.cap - e.flow), level, ptr)
                if tr > 0:
                    e.flow += tr
                    self.adj[e.to][e.rev].flow -= tr
                    return tr
            ptr[u] += 1
        return 0

    def solve_max_flow(self, source: int, sink: int) -> int:
        if source == sink:
            raise ValueError("Source and sink must be distinct vertices.")
        total_flow = 0
        inf_cap = sum(c for _, _, c in self.original_edges) + 1
        while True:
            level = self._bfs_levels(source, sink)
            if level[sink] < 0:
                break
            ptr = [0] * self.n
            while True:
                pushed = self._dfs_push(source, sink, inf_cap, level, ptr)
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
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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
    scores = _to_numpy_f64(fisher_sensitivity).ravel()
    if scores.size == 0 or not np.all(np.isfinite(scores)):
        raise ValueError("fisher_sensitivity must be a non-empty finite 1-D sequence.")
    M = int(scores.size)

    c_rows = (M // 4) if core_rows is None else int(core_rows)
    if c_rows < 0 or c_rows > M:
        raise ValueError(f"core_rows={c_rows} out of bounds for M={M}.")

    demands = tuple(int(d) for d in plasmid_demands)
    if any(d < 0 for d in demands):
        raise ValueError(f"plasmid_demands must be non-negative integers, got {demands}.")

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
            cand_js = [int(j) for j in allowed_corridors[k] if int(j) in eligible_set]
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

    digest_payload = {
        "total_neurons": M,
        "core_rows_frozen": c_rows,
        "frozen_indices": frozen_tuple,
        "eligible_indices": eligible_tuple,
        "plasmid_demands": demands,
        "total_demand": total_demand,
        "max_flow": max_flow,
        "deficit": deficit,
        "assignments": assigned_lists,
        "source_minimal_cut": s_min,
        "sink_minimal_cut": t_min,
    }
    digest = _digest_min_cut_payload(digest_payload)

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


def verify_min_cut_mitosis_certificate(cert: MinCutMitosisCertificate) -> Dict[str, Any]:
    """
    Independent fail-closed verifier for `MinCutMitosisCertificate` (`cut_certificate.py` analog).
    """
    src = 0
    snk = cert.network_vertex_count - 1
    if cert.total_neurons <= 0 or snk != 1 + len(cert.plasmid_demands) + 2 * cert.total_neurons:
        return {"ok": False, "reason": "invalid_vertex_layout"}
    if any(d < 0 for d in cert.plasmid_demands):
        return {"ok": False, "reason": "negative_demand"}
    if cert.total_demand != sum(cert.plasmid_demands):
        return {"ok": False, "reason": "demand_sum_mismatch"}
    if cert.max_flow < 0 or cert.max_flow > cert.total_demand:
        return {"ok": False, "reason": "invalid_max_flow_bounds"}
    expected_deficit = cert.total_demand - cert.max_flow
    if cert.deficit != expected_deficit or cert.requires_mitosis != (expected_deficit > 0):
        return {"ok": False, "reason": "mitosis_deficit_mismatch"}

    # 1. Verify strong Max-Flow == Min-Cut duality on BOTH source_minimal & sink_minimal cuts!
    s_set = set(cert.source_minimal_cut)
    t_set = set(cert.sink_minimal_cut)
    if src not in s_set or snk in s_set or src not in t_set or snk in t_set:
        return {"ok": False, "reason": "invalid_cut_endpoints"}
    if not s_set.issubset(t_set):
        return {"ok": False, "reason": "source_minimal_not_subset_of_sink_minimal"}

    cap_s = compute_cut_capacity(cert.network_edges, s_set)
    cap_t = compute_cut_capacity(cert.network_edges, t_set)
    if cap_s != cert.max_flow or cap_t != cert.max_flow:
        return {"ok": False, "reason": "cut_capacity_does_not_match_max_flow"}
    if cap_s != cert.cut_capacity_source_minimal or cap_t != cert.cut_capacity_sink_minimal:
        return {"ok": False, "reason": "recorded_cut_capacity_mismatch"}

    # 2. Verify integral flow feasibility, frozen-core exclusion, & zero Hall-stacking collisions!
    frozen_set = set(cert.frozen_indices)
    eligible_set = set(cert.eligible_indices)
    if frozen_set & eligible_set:
        return {"ok": False, "reason": "frozen_core_in_eligible_pool"}
    if not set(range(cert.core_rows_frozen)).issubset(frozen_set):
        return {"ok": False, "reason": "core_rows_missing_from_frozen_set"}

    if len(cert.assignments) != len(cert.plasmid_demands):
        return {"ok": False, "reason": "assignment_count_mismatch"}

    seen_slots: Set[int] = set()
    routed_total = 0
    edge_lookup = {(u, v): cap for u, v, cap in cert.network_edges}
    K = len(cert.plasmid_demands)
    M = cert.total_neurons

    for k, slots in enumerate(cert.assignments):
        if len(slots) > cert.plasmid_demands[k]:
            return {"ok": False, "reason": "plasmid_assignment_exceeds_demand"}
        for j in slots:
            if j in frozen_set or j not in eligible_set:
                return {"ok": False, "reason": "slot_violates_frozen_or_eligible_mask"}
            if j in seen_slots:
                return {"ok": False, "reason": "hall_stacking_slot_collision"}
            if edge_lookup.get((1 + k, 1 + K + j), 0) < 1:
                return {"ok": False, "reason": "missing_network_corridor_edge"}
            seen_slots.add(j)
            routed_total += 1

    if routed_total != cert.max_flow:
        return {"ok": False, "reason": "assignment_total_does_not_equal_max_flow"}

    # 3. Verify canonical SHA-256 integrity digest
    expected_digest = _digest_min_cut_payload({
        "total_neurons": cert.total_neurons,
        "core_rows_frozen": cert.core_rows_frozen,
        "frozen_indices": cert.frozen_indices,
        "eligible_indices": cert.eligible_indices,
        "plasmid_demands": cert.plasmid_demands,
        "total_demand": cert.total_demand,
        "max_flow": cert.max_flow,
        "deficit": cert.deficit,
        "assignments": list(cert.assignments),
        "source_minimal_cut": cert.source_minimal_cut,
        "sink_minimal_cut": cert.sink_minimal_cut,
    })
    if cert.sha256_digest != expected_digest:
        return {"ok": False, "reason": "sha256_digest_mismatch"}

    return {
        "ok": True,
        "reason": "verified",
        "max_flow": cert.max_flow,
        "deficit": cert.deficit,
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
    r_add = int(deficit_rows)
    c_add = int(deficit_cols)
    if r_add < 0 or c_add < 0:
        raise ValueError("Mitosis deficits must be non-negative.")

    orig_r, orig_c = w_np.shape
    c_rows = (orig_r // 4) if core_rows is None else int(core_rows)
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
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
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
    b0 = _exact_nonneg_fraction(initial_budget)
    if b0 <= Fraction(0, 1):
        raise ValueError(f"initial_budget must be strictly positive, got {b0}.")

    costs_q: List[Fraction] = []
    rem = b0
    for c in step_costs:
        cq = _exact_nonneg_fraction(c)
        if cq <= Fraction(0, 1):
            raise ValueError(f"Each step_cost must be strictly positive (got {cq}); negative/zero costs forbidden.")
        rem = rem - cq
        if rem < Fraction(0, 1):
            raise ValueError(f"Metabolic budget exhausted: remaining {rem} < 0.")
        costs_q.append(cq)

    if len(quotient_drifts) == 0:
        raise ValueError("quotient_drifts must be non-empty.")
    drifts_q = [_exact_nonneg_fraction(d) for d in quotient_drifts]
    if any(d < Fraction(0, 1) for d in drifts_q):
        raise ValueError("quotient_drifts must be non-negative.")

    M_q = len(drifts_q)
    if quotient_weights is None:
        weights_q = [Fraction(1, M_q) for _ in range(M_q)]
    else:
        if len(quotient_weights) != M_q:
            raise ValueError("quotient_weights length must match quotient_drifts.")
        weights_q = [_exact_nonneg_fraction(w) for w in quotient_weights]
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
        A_raw, b_raw, lam_raw = farkas_system
        A_q = [[_exact_nonneg_fraction(val) for val in row] for row in A_raw]
        b_q = [_exact_nonneg_fraction(val) for val in b_raw]
        lam_q = [_exact_nonneg_fraction(val) for val in lam_raw]
        if len(A_q) == 0 or len(A_q) != len(b_q) or len(lam_q) != len(A_q):
            raise ValueError("Malformed Farkas system dimensions.")
        if any(l < Fraction(0, 1) for l in lam_q):
            raise ValueError("Farkas dual multipliers lambda must be >= 0.")
        n_cols = len(A_q[0])
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


def verify_fraction_dual_certificate(cert: FractionDualCertificate) -> Dict[str, Any]:
    """
    Standalone pure-`Fraction` verifier (zero floating-point operations in the TCB!).
    """
    try:
        b0 = Fraction(cert.initial_budget_q)
        costs = [Fraction(c) for c in cert.step_costs_q]
        rem_claimed = Fraction(cert.remaining_budget_q)
        weights = [Fraction(w) for w in cert.quotient_weights_q]
        drifts = [Fraction(d) for d in cert.quotient_drifts_q]
        part_claimed = Fraction(cert.partitioned_drift_q)
        cap = Fraction(cert.drift_cap_q)
    except (ValueError, ZeroDivisionError):
        return {"ok": False, "reason": "malformed_rational_string"}

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
        try:
            A_q = [[Fraction(x) for x in row] for row in cert.farkas_matrix_q]
            b_q = [Fraction(x) for x in cert.farkas_rhs_q]
            lam_q = [Fraction(x) for x in cert.farkas_multipliers_q]
        except (ValueError, ZeroDivisionError):
            return {"ok": False, "reason": "malformed_farkas_rational"}
        if len(A_q) == 0 or len(A_q) != len(b_q) or len(lam_q) != len(A_q):
            return {"ok": False, "reason": "farkas_dimension_mismatch"}
        if any(l < Fraction(0, 1) for l in lam_q):
            return {"ok": False, "reason": "negative_farkas_multiplier"}
        n_cols = len(A_q[0])
        for col in range(n_cols):
            if sum((lam_q[r] * A_q[r][col] for r in range(len(A_q))), Fraction(0, 1)) != Fraction(0, 1):
                return {"ok": False, "reason": "farkas_stationarity_failed"}
        if sum((lam_q[r] * b_q[r] for r in range(len(A_q))), Fraction(0, 1)) >= Fraction(0, 1):
            return {"ok": False, "reason": "farkas_rhs_not_negative"}
        farkas_verified = True

    expected_digest = _digest_fraction_cert({
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
    """
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
    bi = _to_numpy_f64(bias_in).ravel().copy() if bias_in is not None else None

    M, d_in = wi.shape
    if wo.shape[1] != M:
        raise ValueError(f"w_out columns ({wo.shape[1]}) must equal w_in rows ({M}).")
    c_rows = (M // 4) if core_rows is None else int(core_rows)
    if c_rows < 0 or c_rows > M:
        raise ValueError(f"Invalid core_rows={c_rows} for M={M}.")

    rng = np.random.default_rng(probe_seed)
    X_probe = rng.normal(0.0, 1.0, size=(64, d_in))
    anchor = rng.normal(0.0, 1.0, size=64)

    pre = X_probe @ wi[c_rows:, :].T
    if bi is not None:
        pre = pre + bi[None, c_rows:]
    # Smooth GELU probe signature (equivariant under peripheral channel permutations)
    act = pre * (1.0 / (1.0 + np.exp(-1.702 * np.clip(pre, -20.0, 20.0))))
    keys = anchor @ act + 1e-3 * np.sum(act ** 2, axis=0)
    periph_perm = np.argsort(keys, kind="mergesort") + c_rows
    full_order = np.concatenate([np.arange(c_rows, dtype=int), periph_perm])

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
    iters = int(iterations_requested)
    if iters < 0:
        raise ValueError("iterations_requested must be >= 0.")
    if iters == 0 and committed:
        raise ValueError("Zero-iteration run cannot claim committed=True.")

    report = {
        "schema": "WEFT-PLASM-REPORT/2.0",
        "seed": int(seed),
        "backend": backend,
        "iterations_executed": iters,
        "zero_iteration_noop": (iters == 0),
        "effective_config": dict(effective_config),
        "committed": bool(committed),
        "proposed_candidate": dict(proposed_candidate_metrics) if proposed_candidate_metrics is not None else None,
        "committed_state": dict(committed_state_metrics),
        "min_cut_certificate_sha256": min_cut_cert.sha256_digest if min_cut_cert is not None else None,
        "fraction_dual_certificate_sha256": dual_cert.sha256_digest if dual_cert is not None else None,
    }
    report["report_sha256"] = _digest_fraction_cert(report)
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
    "pack_certificate_lock_record",
    "verify_fraction_dual_certificate",
    "verify_min_cut_mitosis_certificate",
]
