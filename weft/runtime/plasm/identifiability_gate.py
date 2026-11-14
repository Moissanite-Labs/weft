#!/usr/bin/env python3
"""
Asma -> Weft Cross-Pollination: Multi-Probe Divergence Gate, Exact Farkas
Probe Identifiability, & Helly-Swept Shift-Robust Synaptic Corridors
(`weft/runtime/plasm/identifiability_gate.py`)
=========================================================================
Cross-pollinates three mathematical primitives proven in `Foundation-0/project-asma`
(Theorems P01 & P02; PR #78 & PR #80) directly into `Moissanite-Labs/weft`:

  1. Multi-Probe Divergence Index (`MPDI`) Gate (from Asma Monograph 01 / P02):
     Eliminates Weft's "Scalar Loss Blind Spot" (identical to falling serum CA-125
     masking 28.1:1 oligosecretory serosal progression). When a candidate HGT plasmid
     or mitotic step improves dominant niche loss (`delta_dom < 0`) while silently
     degrading low-amplitude tail/OOD anchor loss (`delta_tail > 0`), scalar loss
     `w_dom * delta_dom + w_tail * delta_tail < 0` falsely commits the regression.
     `evaluate_multi_probe_divergence_gate` computes an exact `Fraction` divergence
     certificate and blocks false-reassurance commits fail-closed.

  2. Exact Rational Farkas Probe-Identifiability & Probe Mitosis (from Asma P02 / PR #78):
     Applies the exact closed-form rational LP/Farkas dual (`L1_norm(lambda) <= 1/2`)
     to certify whether Weft's evaluation probes separate genuine skill adaptation
     from bounded affine covariate bias `abs(b) <= B_0` at noise tolerance `eps_target`,
     triggering orthogonal probe expansion when `eps_star <= eps_target`.

  3. Helly-Swept Shift-Robust Synaptic Corridor Routing (from Asma P01):
     Extends `synaptic_flow.allocate_disjoint_synaptic_corridors` from a single static
     Fisher snapshot to a continuous covariate-shift interval `b in [-beta, +beta]`:
     sweeps exact rational 1-D Helly interval endpoints AND every open segment between
     consecutive knots to certify collision-free corridors (or exact worst-case flow
     and min-cut mitosis deficit) across the entire shift range. Knot-only sweeps are
     not enough: eligible rows can vanish strictly inside an open segment, so the
     worst-case flow is reported over knots AND segments.

License: Apache-2.0. Mandate: No token. No sale. Nothing on-chain.
Disclosure: AI-assisted research & execution via Gemini task agent per CONTRIBUTING.md.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

RationalInput = Union[int, float, str, Fraction]


def _to_q(val: RationalInput) -> Fraction:
    if isinstance(val, Fraction):
        return val
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, str):
        return Fraction(val)
    if isinstance(val, float):
        return Fraction.from_float(val).limit_denominator(10**9)
    raise TypeError(f"Unsupported rational input: {type(val)!r}")


def _q_str(val: Fraction) -> str:
    return f"{val.numerator}/{val.denominator}"


def _canon_sha256(payload: Dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "certificate_sha256"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# -----------------------------------------------------------------------------
# 1. Multi-Probe Divergence Index (MPDI) Gate (Asma Shedding Blind-Spot Fix)
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class MultiProbeDivergenceReceipt:
    dominant_weight_q: str
    tail_weight_q: str
    exact_masking_ratio_q: str
    delta_dominant_q: str
    delta_opposing_probes_q: Tuple[str, ...]
    probe_scales_q: Tuple[str, ...]
    probe_weights_q: Tuple[str, ...]
    scalar_weighted_delta_q: str
    mpdi_score_q: str
    alert_threshold_q: str
    scalar_gate_would_commit: bool
    mpdi_gate_commits: bool
    masked_regression_caught: bool
    certificate_sha256: str


def evaluate_multi_probe_divergence_gate(
    *,
    delta_dominant: RationalInput,
    delta_opposing_probes: Sequence[RationalInput],
    probe_scales: Sequence[RationalInput],
    probe_weights: Optional[Sequence[RationalInput]] = None,
    dominant_weight: RationalInput = Fraction(25, 1),
    tail_weight: RationalInput = Fraction(1, 1),
    alert_threshold: RationalInput = Fraction(1, 1),
) -> MultiProbeDivergenceReceipt:
    """
    Certifies whether a candidate colony/plasmid update exhibits hidden sub-mode
    divergence masked by a high-weight dominant niche loss (`scalar_weighted_delta < 0`
    while opposing OOD/safety/curvature probes degrade above `alert_threshold`).
    """
    if len(delta_opposing_probes) == 0 or len(delta_opposing_probes) != len(probe_scales):
        raise ValueError("delta_opposing_probes and probe_scales must be non-empty and equal length")

    w_dom = _to_q(dominant_weight)
    w_tail = _to_q(tail_weight)
    if w_dom <= 0 or w_tail <= 0:
        raise ValueError("dominant_weight and tail_weight must be strictly positive")

    d_dom = _to_q(delta_dominant)
    d_opp = [_to_q(x) for x in delta_opposing_probes]
    scales = [_to_q(s) for s in probe_scales]
    if any(s <= 0 for s in scales):
        raise ValueError("All probe_scales must be strictly positive")

    if probe_weights is None:
        n_p = len(d_opp)
        p_weights = [Fraction(1, n_p) for _ in range(n_p)]
    else:
        p_weights = [_to_q(w) for w in probe_weights]
        if len(p_weights) != len(d_opp) or any(w < 0 for w in p_weights):
            raise ValueError("Invalid probe_weights")

    thresh = _to_q(alert_threshold)
    # Scalar loss change combines dominant loss and first opposing tail loss
    scalar_delta = w_dom * d_dom + w_tail * d_opp[0]
    scalar_commits = bool(scalar_delta < 0)

    # Exact rational piecewise-linear gating factor: active whenever dominant probe improves (`d_dom < 0`)
    # or even if stagnant, weighting normalized positive regressions across all opposing probes:
    dom_drive = Fraction(1, 1) if d_dom < 0 else Fraction(1, 2)
    opposing_sum = sum(
        pw * max(Fraction(0, 1), dp / sc)
        for pw, dp, sc in zip(p_weights, d_opp, scales)
    )
    mpdi_q = dom_drive * opposing_sum

    # Commit ONLY if scalar loss improves AND no opposing probe divergence alert is triggered
    mpdi_commits = bool(scalar_commits and (mpdi_q < thresh))
    masked_caught = bool(scalar_commits and not mpdi_commits)

    raw_dict = {
        "dominant_weight_q": _q_str(w_dom),
        "tail_weight_q": _q_str(w_tail),
        "exact_masking_ratio_q": _q_str(w_dom / w_tail),
        "delta_dominant_q": _q_str(d_dom),
        "delta_opposing_probes_q": tuple(_q_str(x) for x in d_opp),
        "probe_scales_q": tuple(_q_str(s) for s in scales),
        "probe_weights_q": tuple(_q_str(w) for w in p_weights),
        "scalar_weighted_delta_q": _q_str(scalar_delta),
        "mpdi_score_q": _q_str(mpdi_q),
        "alert_threshold_q": _q_str(thresh),
        "scalar_gate_would_commit": scalar_commits,
        "mpdi_gate_commits": mpdi_commits,
        "masked_regression_caught": masked_caught,
    }
    digest = _canon_sha256(raw_dict)
    return MultiProbeDivergenceReceipt(**raw_dict, certificate_sha256=digest)


def verify_multi_probe_divergence_receipt(rec: MultiProbeDivergenceReceipt) -> Dict[str, Any]:
    body = asdict(rec)
    if _canon_sha256(body) != rec.certificate_sha256:
        return {"ok": False, "reason": "certificate_sha256_mismatch"}
    recomputed = evaluate_multi_probe_divergence_gate(
        delta_dominant=Fraction(rec.delta_dominant_q),
        delta_opposing_probes=[Fraction(x) for x in rec.delta_opposing_probes_q],
        probe_scales=[Fraction(s) for s in rec.probe_scales_q],
        probe_weights=[Fraction(w) for w in rec.probe_weights_q],
        dominant_weight=Fraction(rec.dominant_weight_q),
        tail_weight=Fraction(rec.tail_weight_q),
        alert_threshold=Fraction(rec.alert_threshold_q),
    )
    if recomputed != rec:
        return {"ok": False, "reason": "semantic_recomputation_mismatch"}
    return {"ok": True, "reason": "verified"}


# -----------------------------------------------------------------------------
# 2. Exact Rational Farkas Probe-Identifiability & Probe Mitosis (Asma P02)
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FarkasIdentifiabilityCertificate:
    probe_deltas_q: Tuple[str, ...]
    max_bias_q: str
    target_eps_q: str
    eps_star_q: str
    farkas_dual_q: Tuple[str, ...]
    identifiable_at_target: bool
    requires_probe_mitosis: bool
    certificate_sha256: str


def certify_probe_world_identifiability(
    world1_outputs: Sequence[RationalInput],
    world2_outputs: Sequence[RationalInput],
    *,
    max_bias: RationalInput = Fraction(1, 20),
    target_eps: RationalInput = Fraction(1, 60),
) -> FarkasIdentifiabilityCertificate:
    """
    Computes the exact rational separation radius `eps_star` and explicit Farkas LP
    dual vector `lambda` (`L1_norm(lambda) <= 1/2`) between two model/skill hypotheses
    under bounded affine shift `abs(b) <= max_bias` and residual error `abs(e_i) <= eps`.
    """
    if len(world1_outputs) == 0 or len(world1_outputs) != len(world2_outputs):
        raise ValueError("world1_outputs and world2_outputs must be non-empty and equal length")

    deltas = [_to_q(a) - _to_q(b) for a, b in zip(world1_outputs, world2_outputs)]
    b0 = _to_q(max_bias)
    t_eps = _to_q(target_eps)
    if b0 < 0 or t_eps < 0:
        raise ValueError("max_bias and target_eps must be non-negative")

    B = Fraction(2, 1) * b0
    d_min = min(deltas)
    d_max = max(deltas)
    i_min = deltas.index(d_min)
    i_max = deltas.index(d_max)
    mid_shift = -(d_min + d_max) / Fraction(2, 1)

    m = len(deltas)
    dual = [Fraction(0, 1)] * m
    if -B <= mid_shift <= B:
        eps_star = (d_max - d_min) / Fraction(4, 1)
        if i_max != i_min:
            dual[i_max] = Fraction(1, 4)
            dual[i_min] = Fraction(-1, 4)
    elif mid_shift < -B:
        eps_star = max(Fraction(0, 1), (d_max - B) / Fraction(2, 1))
        if eps_star > 0:
            dual[i_max] = Fraction(1, 2)
    else:
        eps_star = max(Fraction(0, 1), (-d_min - B) / Fraction(2, 1))
        if eps_star > 0:
            dual[i_min] = Fraction(-1, 2)

    identifiable = bool(eps_star > t_eps)
    raw = {
        "probe_deltas_q": tuple(_q_str(d) for d in deltas),
        "max_bias_q": _q_str(b0),
        "target_eps_q": _q_str(t_eps),
        "eps_star_q": _q_str(eps_star),
        "farkas_dual_q": tuple(_q_str(x) for x in dual),
        "identifiable_at_target": identifiable,
        "requires_probe_mitosis": not identifiable,
    }
    return FarkasIdentifiabilityCertificate(**raw, certificate_sha256=_canon_sha256(raw))


def verify_farkas_identifiability_certificate(cert: FarkasIdentifiabilityCertificate) -> Dict[str, Any]:
    body = asdict(cert)
    if _canon_sha256(body) != cert.certificate_sha256:
        return {"ok": False, "reason": "certificate_sha256_mismatch"}
    deltas = [Fraction(d) for d in cert.probe_deltas_q]
    dual = [Fraction(x) for x in cert.farkas_dual_q]
    if len(deltas) != len(dual) or len(deltas) == 0:
        return {"ok": False, "reason": "dimension_mismatch"}
    if sum(abs(x) for x in dual) > Fraction(1, 2):
        return {"ok": False, "reason": "dual_l1_norm_exceeds_half"}
    B = Fraction(2, 1) * Fraction(cert.max_bias_q)
    dual_val = max(Fraction(0, 1), sum(u * d for u, d in zip(dual, deltas)) - B * abs(sum(dual)))
    eps_star = Fraction(cert.eps_star_q)
    # Also check primal upper bound `min_{db in [-B, B]} max_i |delta_i + db| / 2`
    d_min, d_max = min(deltas), max(deltas)
    db_opt = max(-B, min(B, -(d_min + d_max) / Fraction(2, 1)))
    primal_val = max(abs(d + db_opt) for d in deltas) / Fraction(2, 1)
    if dual_val != eps_star or primal_val != eps_star:
        return {"ok": False, "reason": "strong_duality_gap"}
    t_eps = Fraction(cert.target_eps_q)
    if bool(eps_star > t_eps) != cert.identifiable_at_target:
        return {"ok": False, "reason": "identifiable_flag_mismatch"}
    if cert.requires_probe_mitosis != (not cert.identifiable_at_target):
        return {"ok": False, "reason": "mitosis_flag_mismatch"}
    return {"ok": True, "reason": "verified"}


# -----------------------------------------------------------------------------
# 3. Helly-Swept Shift-Robust Synaptic Corridor Routing (Asma P01 -> Weft)
# -----------------------------------------------------------------------------

class _DinicUnit:
    def __init__(self, n: int) -> None:
        self.n = n
        self.adj: List[List[List[int]]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        self.adj[u].append([v, len(self.adj[v]), cap, 0])
        self.adj[v].append([u, len(self.adj[u]) - 1, 0, 0])

    def max_flow(self, s: int, t: int) -> Tuple[int, List[int]]:
        flow = 0
        while True:
            lvl = [-1] * self.n
            lvl[s] = 0
            q = deque([s])
            while q:
                u = q.popleft()
                for v, _, cap, fl in self.adj[u]:
                    if cap - fl > 0 and lvl[v] < 0:
                        lvl[v] = lvl[u] + 1
                        q.append(v)
            if lvl[t] < 0:
                break
            it = [0] * self.n

            def dfs(u: int, pushed: int) -> int:
                if pushed == 0 or u == t:
                    return pushed
                while it[u] < len(self.adj[u]):
                    e = self.adj[u][it[u]]
                    v, rev, cap, fl = e
                    if cap - fl > 0 and lvl[v] == lvl[u] + 1:
                        tr = dfs(v, min(pushed, cap - fl))
                        if tr > 0:
                            e[3] += tr
                            self.adj[v][rev][3] -= tr
                            return tr
                    it[u] += 1
                return 0

            while True:
                p = dfs(s, 10**9)
                if p == 0:
                    break
                flow += p

        seen = [False] * self.n
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for v, _, cap, fl in self.adj[u]:
                if cap - fl > 0 and not seen[v]:
                    seen[v] = True
                    q.append(v)
        return flow, [i for i, f in enumerate(seen) if f]


def certify_shift_robust_corridors_helly(
    row_base_fisher: Sequence[RationalInput],
    row_shift_slopes: Sequence[RationalInput],
    *,
    plasmid_demands: Sequence[int],
    core_rows: int,
    fisher_cap: RationalInput,
    max_shift_beta: RationalInput,
) -> Dict[str, Any]:
    """
    sweeps exact rational 1-D Helly interval endpoints across covariate shift
    `b in [-max_shift_beta, +max_shift_beta]`, where peripheral row `r`'s Fisher
    sensitivity evolves affinely as `F_r(b) = base_r + slope_r * b <= fisher_cap`.

    Returns:
      - `uniformly_safe_corridors` payload (`uniform_shift_safe_flow`, assignments): rows safe across
        ALL `b in [-beta, +beta]` simultaneously
      - `helly_knot_witnesses`: exact flow and min-cut at each knot endpoint
      - `segment_witnesses`: exact flow inside every open interval between consecutive knots.
        Eligible-row eligibility inside `(k_i, k_{i+1})` is `{lo <= k_i AND hi >= k_{i+1}}`;
        max-flow is monotone in the edge set, so each segment flow is at most both endpoint knot
        flows. `true_min_shift_flow` is the minimum over knots and segments and is the honest
        worst-case flow over the whole shift range. `min_pointwise_knot_flow` is kept for
        compatibility and reports the knot-only minimum (not a lower bound on the shift range).
    """
    n_rows = len(row_base_fisher)
    if n_rows != len(row_shift_slopes) or core_rows < 0 or core_rows >= n_rows:
        raise ValueError("Invalid row dimensions or core_rows")

    base_q = [_to_q(x) for x in row_base_fisher]
    slope_q = [_to_q(x) for x in row_shift_slopes]
    f_cap = _to_q(fisher_cap)
    beta = _to_q(max_shift_beta)
    total_demand = sum(int(d) for d in plasmid_demands)

    # Compute exact feasible shift interval `I_r = [lo_r, hi_r] subset [-beta, +beta]` for each peripheral row
    row_intervals: Dict[int, Optional[Tuple[Fraction, Fraction]]] = {}
    knots = {-beta, beta}
    uniformly_safe_rows: List[int] = []

    for r in range(core_rows, n_rows):
        b0, sl = base_q[r], slope_q[r]
        if sl == 0:
            iv = (-beta, beta) if b0 <= f_cap else None
        elif sl > 0:
            ub = min(beta, (f_cap - b0) / sl)
            iv = (-beta, ub) if -beta <= ub else None
        else:
            lb = max(-beta, (f_cap - b0) / sl)
            iv = (lb, beta) if lb <= beta else None
        row_intervals[r] = iv
        if iv is not None:
            knots.add(iv[0])
            knots.add(iv[1])
            if iv == (-beta, beta):
                uniformly_safe_rows.append(r)

    def _solve_at_rows(eligible_rows: Sequence[int]) -> Tuple[int, List[int]]:
        k_p = len(plasmid_demands)
        n_periph = n_rows - core_rows
        src = 0
        p_base = 1
        rin_base = 1 + k_p
        rout_base = 1 + k_p + n_periph
        sink = 1 + k_p + 2 * n_periph
        g = _DinicUnit(sink + 1)
        elig_set = set(eligible_rows)
        for p_idx, dem in enumerate(plasmid_demands):
            g.add_edge(src, p_base + p_idx, int(dem))
            for r in elig_set:
                off = r - core_rows
                g.add_edge(p_base + p_idx, rin_base + off, 1)
        for off in range(n_periph):
            r = core_rows + off
            if r in elig_set:
                g.add_edge(rin_base + off, rout_base + off, 1)
                g.add_edge(rout_base + off, sink, 1)
        return g.max_flow(src, sink)

    static_b0_rows = [
        r for r, iv in row_intervals.items()
        if iv is not None and iv[0] <= Fraction(0, 1) <= iv[1]
    ]
    static_flow, _ = _solve_at_rows(static_b0_rows)
    uniform_flow, uniform_cut = _solve_at_rows(uniformly_safe_rows)

    knot_records: List[Dict[str, Any]] = []
    min_knot_flow = total_demand + 1
    sorted_knots = sorted(knots)
    for bk in sorted_knots:
        elig = [r for r, iv in row_intervals.items() if iv is not None and iv[0] <= bk <= iv[1]]
        fl, s_side = _solve_at_rows(elig)
        min_knot_flow = min(min_knot_flow, fl)
        knot_records.append({
            "shift_b_q": _q_str(bk),
            "eligible_peripheral_rows": elig,
            "max_flow": fl,
            "deficit": max(0, total_demand - fl),
            "source_minimal_cut": s_side,
        })

    # Exact worst case over the continuum: eligible rows inside (k_i, k_{i+1}) vanish to
    # {lo <= k_i AND hi >= k_{i+1}}. Knot-only sweeps miss these mid-segment bottlenecks.
    segment_records: List[Dict[str, Any]] = []
    true_min_flow = min_knot_flow
    for k_i, k_j in zip(sorted_knots, sorted_knots[1:]):
        elig = [
            r for r, iv in row_intervals.items()
            if iv is not None and iv[0] <= k_i and iv[1] >= k_j
        ]
        fl, s_side = _solve_at_rows(elig)
        true_min_flow = min(true_min_flow, fl)
        segment_records.append({
            "open_interval_q": [_q_str(k_i), _q_str(k_j)],
            "eligible_peripheral_rows": elig,
            "max_flow": fl,
            "deficit": max(0, total_demand - fl),
            "source_minimal_cut": s_side,
        })

    # Assign disjoint corridors from `uniformly_safe_rows` (guaranteed zero collision for ALL b in [-beta, +beta])
    assignments: List[List[int]] = []
    cursor = 0
    for dem in plasmid_demands:
        take = uniformly_safe_rows[cursor : cursor + int(dem)]
        assignments.append(take)
        cursor += len(take)

    payload: Dict[str, Any] = {
        "total_demand": total_demand,
        "core_rows": core_rows,
        "static_b0_flow": static_flow,
        "static_b0_false_safety": bool(static_flow >= total_demand and uniform_flow < total_demand),
        "uniform_shift_safe_flow": uniform_flow,
        "uniform_mitosis_deficit": max(0, total_demand - uniform_flow),
        "min_pointwise_knot_flow": min_knot_flow,
        "true_min_shift_flow": true_min_flow,
        "uniform_corridor_assignments": assignments,
        "helly_knot_witnesses": knot_records,
        "segment_witnesses": segment_records,
    }
    payload["certificate_sha256"] = _canon_sha256(payload)
    return payload
