"""Causal non-stuttering synaptic routing, crushing-gate quorum, and floating-drift Farkas gates."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Mapping, Sequence, Set, Tuple


@dataclass(frozen=True)
class CertifiedSynapticFlow:
    max_flow: int
    cut_capacity: int
    source_side_nodes: Tuple[int, ...]
    blocked_secondary_hops: int
    primal_dual_verified: bool


def route_causal_synaptic_flow(
    num_rungs: int,
    intact_receptors: Sequence[Tuple[int, bool]],
    primary_matches: Sequence[Tuple[int, int]],
    secondary_hops: Sequence[Tuple[int, int]],
    conserved_parent_rungs: Set[int],
) -> CertifiedSynapticFlow:
    intact_ids = {idx for idx, is_intact in intact_receptors if is_intact}
    num_left = len(primary_matches) + len(secondary_hops)
    receptor_count = len(intact_receptors)
    sink = num_left + receptor_count + 1
    adj: List[List[List[int]]] = [[] for _ in range(sink + 1)]
    orig_edges: List[Tuple[int, int, int]] = []

    def add_edge(u: int, v: int, cap: int) -> None:
        orig_edges.append((u, v, cap))
        adj[u].append([v, cap, len(adj[v])])
        adj[v].append([u, 0, len(adj[u]) - 1])

    for i in range(num_left):
        add_edge(0, 1 + i, 1)
    for r_idx in range(receptor_count):
        if r_idx in intact_ids:
            add_edge(1 + num_left + r_idx, sink, 1)
    for i, (rung_k, r_idx) in enumerate(primary_matches):
        if 1 <= rung_k <= num_rungs and r_idx in intact_ids:
            add_edge(1 + i, 1 + num_left + r_idx, 1)

    blocked = 0
    offset = len(primary_matches)
    for j, (rung_k, r_idx) in enumerate(secondary_hops):
        if rung_k not in conserved_parent_rungs:
            if r_idx in intact_ids:
                blocked += 1
            continue
        if r_idx in intact_ids:
            add_edge(1 + offset + j, 1 + num_left + r_idx, 1)

    flow = 0
    while True:
        level = [-1] * (sink + 1)
        level[0] = 0
        q = deque([0])
        while q:
            u = q.popleft()
            for v, cap, _ in adj[u]:
                if cap > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    q.append(v)
        if level[sink] < 0:
            break
        it = [0] * (sink + 1)

        def dfs(u: int, pushed: int) -> int:
            if pushed == 0 or u == sink:
                return pushed
            while it[u] < len(adj[u]):
                idx = it[u]
                v, cap, rev = adj[u][idx]
                if cap > 0 and level[v] == level[u] + 1:
                    tr = dfs(v, min(pushed, cap))
                    if tr > 0:
                        adj[u][idx][1] -= tr
                        adj[v][rev][1] += tr
                        return tr
                it[u] += 1
            return 0

        while True:
            p = dfs(0, 10**9)
            if p == 0:
                break
            flow += p

    s_cut: Set[int] = {0}
    rq = deque([0])
    while rq:
        u = rq.popleft()
        for v, cap, _ in adj[u]:
            if cap > 0 and v not in s_cut:
                s_cut.add(v)
                rq.append(v)

    cut_cap = sum(cap for u, v, cap in orig_edges if u in s_cut and v not in s_cut)
    return CertifiedSynapticFlow(
        max_flow=flow,
        cut_capacity=cut_cap,
        source_side_nodes=tuple(sorted(s_cut)),
        blocked_secondary_hops=blocked,
        primal_dual_verified=(flow == cut_cap and sink not in s_cut),
    )


def check_crushing_quorum_transition(
    locked_scaffolds: int,
    mobile_scaffolds: int,
    transient_workers: int,
    quorum_req: int,
    aura_drain: int,
) -> Dict[str, object]:
    pre_quorum = (locked_scaffolds + mobile_scaffolds + transient_workers) >= quorum_req
    post_mobile = max(0, mobile_scaffolds - aura_drain)
    post_quorum = (locked_scaffolds + post_mobile) >= quorum_req
    return {
        "pre_transition_quorum": pre_quorum,
        "sticky_would_admit": pre_quorum,
        "turn_end_quorum_holds": pre_quorum and post_quorum,
        "crushed_by_gate_slam": pre_quorum and not post_quorum,
        "required_locked_floor": max(0, quorum_req - post_mobile),
    }


def certify_two_channel_mitosis_farkas(
    p_seed: Fraction,
    r_drift: Fraction,
    c_mitosis: Fraction,
    noise_ceiling: Fraction = Fraction(1, 60),
) -> Dict[str, object]:
    if not (Fraction(0, 1) <= p_seed < Fraction(1, 1)):
        raise ValueError("p_seed must lie in [0, 1)")
    denom = r_drift * p_seed + (1 - p_seed)
    q_val = (r_drift * p_seed + c_mitosis * (1 - p_seed)) / denom
    u_val = (c_mitosis * (1 - p_seed)) / denom
    eps_star = u_val / 2
    return {
        "q_channel": q_val,
        "u_channel": u_val,
        "rs_invariant_eps_star": eps_star,
        "certified_above_ceiling": eps_star > noise_ceiling,
        "farkas_dual_witness": (Fraction(0, 1), Fraction(1, 1)),
    }


def normalize_shard_midranks(shard_scores: Mapping[str, Sequence[float]]) -> Dict[str, List[float]]:
    out: Dict[str, List[float]] = {}
    for shard_id, scores in shard_scores.items():
        n = len(scores)
        if n == 0:
            out[shard_id] = []
            continue
        indexed = sorted(enumerate(scores), key=lambda x: x[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and indexed[j + 1][1] == indexed[i][1]:
                j += 1
            mid_pct = (((i + 1 + j + 1) / 2.0) - 0.5) / n
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = mid_pct
            i = j + 1
        out[shard_id] = ranks
    return out
