"""Experiment E13: 3-Cell Transitive BCP Plasmid Cascades Under Composed Jacobian Null-Space Gates.

Tests multi-hop horizontal combinator-plasmid propagation (`Cell A -> Cell B -> Cell C`) across
triads of independently channel-permuted `256x256` (`65,536`-weight) sibling organisms, directly
extending E11 (PR #155), E12 (PR #159), and the Lean 4 `SymmetricNullSpace` proofs (PR #166).

Usage:
  python3 e13_transitive_cascade.py --unit       # Fast CI unit & wire-format suite (<0.2s)
  python3 e13_transitive_cascade.py --benchmark  # Full 12-seed x 3-triad x 7-arm = 252-cell run
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

ERA, CON, DUP, VLV, FRC, SUP, FREE = 0, 1, 2, 3, 4, 5, 255
NODE_ARITY = {ERA: 0, CON: 2, DUP: 2, VLV: 1, FRC: 1, SUP: 2}
BCP_MAGIC = b"WEFT"
BCP_VERSION = 2
SKETCH_MAGIC = b"WFSK"
EXEC_DOMAIN = b"WEFT-IC-EXEC-V2:"

HEADER_STRUCT = struct.Struct("<4sBBHI")
NODE_RECORD_STRUCT = struct.Struct("<IBBhiii")
SKETCH_HEADER_STRUCT = struct.Struct("<4sBBH")
MAX_SKETCH_FREQ = 6

DIM = 256
CORE_ROWS = DIM // 4
M_CILIA = DIM - CORE_ROWS
SEEDS = [20261112 + i for i in range(12)]
TRIADS: List[Tuple[int, int, int]] = [(1, 2, 3), (2, 3, 1), (3, 1, 2)]
EVO_GENS = 30
PLASMID_NODES = 8
R_RMS = 0.56

ARMS = [
    "A0_Recipient_PreCascade",
    "C1_Raw_Cascade_Permuted",
    "C2_Random_Capsule_FlagGate",
    "G1_Ungated_BCP_Cascade",
    "G2_Memoryless_SingleGate",
    "G3_Unsketched_SVD_Crowding",
    "G4_Sketched_Composed_FlagGate",
]


def pack_peer_ports(p0: int, p1: int, p2: int) -> int:
    return ((p0 & 0x3) | ((p1 & 0x3) << 2) | ((p2 & 0x3) << 4)) & 0xFF


def unpack_peer_ports(b: int) -> Tuple[int, int, int]:
    return (b & 0x3, (b >> 2) & 0x3, (b >> 4) & 0x3)


@dataclass
class ICNode:
    tag: int = FREE
    aux_tag: int = 0
    ports: List[int] = None
    peer_ports: List[int] = None

    def __post_init__(self) -> None:
        if self.ports is None:
            self.ports = [-1, -1, -1]
        if self.peer_ports is None:
            self.peer_ports = [0, 0, 0]


class MorphogeneticCombinatorVM:
    def __init__(self, capacity: int = 192, max_tension: int = 88) -> None:
        self.capacity = capacity
        self.max_tension = max_tension
        self.nodes: List[ICNode] = [ICNode() for _ in range(capacity)]
        self.steps = 0
        self.annihilations = 0
        self.commutations = 0
        self.vlv_arrests = 0

    def active_slots(self) -> List[int]:
        return [i for i, n in enumerate(self.nodes) if n.tag != FREE]

    def alloc_node(self, tag: int, aux_tag: int = 0) -> int:
        aux_c = max(-4096, min(4096, int(aux_tag)))
        for idx, node in enumerate(self.nodes):
            if node.tag == FREE:
                self.nodes[idx] = ICNode(tag=tag, aux_tag=aux_c)
                return idx
        return -1

    def disconnect(self, slot: int, port: int) -> Tuple[int, int]:
        if slot < 0 or self.nodes[slot].tag == FREE:
            return -1, 0
        ps, pp = self.nodes[slot].ports[port], self.nodes[slot].peer_ports[port]
        self.nodes[slot].ports[port], self.nodes[slot].peer_ports[port] = -1, 0
        if ps >= 0 and self.nodes[ps].tag != FREE:
            self.nodes[ps].ports[pp], self.nodes[ps].peer_ports[pp] = -1, 0
        return ps, pp

    def wire(self, sa: int, pa: int, sb: int, pb: int) -> None:
        if sa < 0 or sb < 0 or (sa == sb and pa == pb):
            return
        if self.nodes[sa].tag == FREE or self.nodes[sb].tag == FREE:
            return
        self.disconnect(sa, pa)
        self.disconnect(sb, pb)
        self.nodes[sa].ports[pa], self.nodes[sa].peer_ports[pa] = sb, pb
        self.nodes[sb].ports[pb], self.nodes[sb].peer_ports[pb] = sa, pa

    def free_node(self, slot: int) -> None:
        if 0 <= slot < self.capacity and self.nodes[slot].tag != FREE:
            for p in (0, 1, 2):
                self.disconnect(slot, p)
            self.nodes[slot] = ICNode()

    def tension(self) -> int:
        active = self.active_slots()
        redexes = sum(1 for i in active if self.nodes[i].ports[0] > i and self.nodes[i].peer_ports[0] == 0)
        return min(100, int((len(active) * 65) // max(self.capacity, 1) + redexes * 4))

    def step(self) -> bool:
        cur_t = self.tension()
        active = self.active_slots()
        for a in active:
            b = self.nodes[a].ports[0]
            if b <= a or self.nodes[a].peer_ports[0] != 0 or self.nodes[b].tag == FREE:
                continue
            ta, tb = self.nodes[a].tag, self.nodes[b].tag
            if (ta == VLV or tb == VLV) and cur_t > self.max_tension:
                self.vlv_arrests += 1
                return False
            if ta == tb:
                a1, ap1 = self.disconnect(a, 1)
                a2, ap2 = self.disconnect(a, 2)
                b1, bp1 = self.disconnect(b, 1)
                b2, bp2 = self.disconnect(b, 2)
                self.free_node(a)
                self.free_node(b)
                if a1 >= 0 and b1 >= 0:
                    self.wire(a1, ap1, b1, bp1)
                if a2 >= 0 and b2 >= 0:
                    self.wire(a2, ap2, b2, bp2)
                self.annihilations += 1
                self.steps += 1
                return True
            if ta == ERA or tb == ERA:
                es, os_ = (a, b) if ta == ERA else (b, a)
                tgts = [self.disconnect(os_, p) for p in range(1, NODE_ARITY.get(self.nodes[os_].tag, 0) + 1)]
                self.free_node(es)
                self.free_node(os_)
                for ts, tp in tgts:
                    if ts >= 0:
                        en = self.alloc_node(ERA, 0)
                        if en >= 0:
                            self.wire(en, 0, ts, tp)
                self.commutations += 1
                self.steps += 1
                return True
            if NODE_ARITY.get(ta, 0) == 2 and NODE_ARITY.get(tb, 0) == 2:
                if len(active) + 2 >= self.capacity or cur_t > self.max_tension:
                    self.vlv_arrests += 1
                    return False
                aa, ab = self.nodes[a].aux_tag, self.nodes[b].aux_tag
                a1, ap1 = self.disconnect(a, 1)
                a2, ap2 = self.disconnect(a, 2)
                b1, bp1 = self.disconnect(b, 1)
                b2, bp2 = self.disconnect(b, 2)
                self.free_node(a)
                self.free_node(b)
                nb1, nb2 = self.alloc_node(tb, (aa + ab) // 2), self.alloc_node(tb, (ab - aa) // 2)
                na1, na2 = self.alloc_node(ta, aa), self.alloc_node(ta, -aa // 2)
                if min(nb1, nb2, na1, na2) >= 0:
                    if a1 >= 0:
                        self.wire(nb1, 0, a1, ap1)
                    if a2 >= 0:
                        self.wire(nb2, 0, a2, ap2)
                    if b1 >= 0:
                        self.wire(na1, 0, b1, bp1)
                    if b2 >= 0:
                        self.wire(na2, 0, b2, bp2)
                    self.wire(nb1, 1, na1, 1)
                    self.wire(nb1, 2, na2, 1)
                    self.wire(nb2, 1, na1, 2)
                    self.wire(nb2, 2, na2, 2)
                self.commutations += 1
                self.steps += 1
                return True
            us, bs = (a, b) if NODE_ARITY.get(ta, 0) == 1 else (b, a)
            ut, ua, ba = self.nodes[us].tag, self.nodes[us].aux_tag, self.nodes[bs].aux_tag
            u1, up1 = self.disconnect(us, 1)
            b1, bp1 = self.disconnect(bs, 1)
            b2, bp2 = self.disconnect(bs, 2)
            self.free_node(us)
            self.nodes[bs].aux_tag = int(ba * 0.80) if ut == VLV else max(-4096, min(4096, ba + ua // 2))
            if u1 >= 0:
                self.wire(bs, 0, u1, up1)
            if b1 >= 0:
                uc1 = self.alloc_node(ut, ua)
                if uc1 >= 0:
                    self.wire(uc1, 0, b1, bp1)
                    self.wire(bs, 1, uc1, 1)
            if b2 >= 0:
                uc2 = self.alloc_node(ut, -ua // 2)
                if uc2 >= 0:
                    self.wire(uc2, 0, b2, bp2)
                    self.wire(bs, 2, uc2, 1)
            self.commutations += 1
            self.steps += 1
            return True
        return False

    def reduce_all(self, max_steps: int = 24) -> Dict[str, object]:
        seed_sha = hashlib.sha256(serialize_graph_bcp(self)).hexdigest()
        init_n = len(self.active_slots())
        for _ in range(max_steps):
            if not self.step():
                break
        final_sha = hashlib.sha256(serialize_graph_bcp(self)).hexdigest()
        payload = (
            f"{seed_sha}:{init_n}:{self.steps}:{self.annihilations}:"
            f"{self.commutations}:{self.vlv_arrests}:{len(self.active_slots())}:{final_sha}"
        ).encode("ascii")
        return {
            "seed_bcp_sha256": seed_sha,
            "initial_nodes": init_n,
            "steps": self.steps,
            "annihilations": self.annihilations,
            "commutations": self.commutations,
            "vlv_arrests": self.vlv_arrests,
            "final_nodes": len(self.active_slots()),
            "final_bcp_sha256": final_sha,
            "record_digest": hashlib.sha256(EXEC_DOMAIN + payload).hexdigest(),
        }


def serialize_graph_bcp(vm: MorphogeneticCombinatorVM) -> bytes:
    active = vm.active_slots()
    buf = bytearray(HEADER_STRUCT.pack(BCP_MAGIC, BCP_VERSION, 0, len(active), vm.max_tension))
    for s in active:
        n = vm.nodes[s]
        pp = pack_peer_ports(n.peer_ports[0], n.peer_ports[1], n.peer_ports[2])
        buf.extend(NODE_RECORD_STRUCT.pack(s, n.tag, pp, n.aux_tag, n.ports[0], n.ports[1], n.ports[2]))
    return bytes(buf)


def deserialize_graph_bcp(data: bytes, capacity: int = 192) -> MorphogeneticCombinatorVM:
    magic, ver, _fl, count, max_t = HEADER_STRUCT.unpack_from(data, 0)
    if magic != BCP_MAGIC or ver != BCP_VERSION:
        raise ValueError("Invalid BCP header")
    vm = MorphogeneticCombinatorVM(capacity=capacity, max_tension=max_t)
    off = HEADER_STRUCT.size
    for _ in range(count):
        slot, tag, pp_b, aux, p0, p1, p2 = NODE_RECORD_STRUCT.unpack_from(data, off)
        off += NODE_RECORD_STRUCT.size
        if 0 <= slot < capacity:
            q0, q1, q2 = unpack_peer_ports(pp_b)
            vm.nodes[slot] = ICNode(tag=tag, aux_tag=aux, ports=[p0, p1, p2], peer_ports=[q0, q1, q2])
    return vm


def verify_execution_record(rec: Dict[str, object], bcp_bytes: bytes, max_steps: int = 24) -> bool:
    replay = deserialize_graph_bcp(bcp_bytes).reduce_all(max_steps=max_steps)
    return replay["record_digest"] == rec["record_digest"]


def canonical_fourier_dictionary(dim: int = DIM, max_freq: int = MAX_SKETCH_FREQ) -> np.ndarray:
    th = np.linspace(-math.pi, math.pi, dim, endpoint=False)
    cols = []
    scale = math.sqrt(2.0 / dim)
    for k in range(1, max_freq + 1):
        cols.append(np.cos(k * th) * scale)
        cols.append(np.sin(k * th) * scale)
    return np.stack(cols, axis=1)


def pack_anchor_sketch_bcp(
    s_calib: np.ndarray,
    in_map_to_recipient: np.ndarray | None = None,
    max_modes: int = 6,
) -> bytes:
    f_dict = canonical_fourier_dictionary(DIM, MAX_SKETCH_FREQ)
    s_canon = s_calib[:, in_map_to_recipient] if in_map_to_recipient is not None else s_calib
    proj = s_canon @ f_dict
    col_rms = np.sqrt(np.mean(proj ** 2, axis=0))
    peak = float(np.max(col_rms)) + 1e-12
    q_energies = [int(round(min(1.0, float(v / peak)) * 32767.0)) for v in col_rms]
    cov = (proj.T @ proj) / max(1, s_canon.shape[0])
    cov_max = float(np.max(np.abs(cov))) + 1e-12
    extra = [int(round(float(cov[i, (i + 2) % 12] / cov_max) * 32767.0)) for i in range(10)]
    payload = q_energies + extra
    buf = bytearray(SKETCH_HEADER_STRUCT.pack(SKETCH_MAGIC, 1, max_modes, MAX_SKETCH_FREQ))
    buf.extend(struct.pack("<22h", *payload))
    return bytes(buf)


def unpack_anchor_sketch_basis(
    sketch_bytes: bytes,
    recipient_in_from_canon: np.ndarray,
    energy_thresh: float = 0.18,
) -> np.ndarray:
    magic, ver, max_modes, max_freq = SKETCH_HEADER_STRUCT.unpack_from(sketch_bytes, 0)
    if magic != SKETCH_MAGIC or ver != 1:
        raise ValueError("Invalid WFSK anchor sketch header")
    vals = struct.unpack_from("<22h", sketch_bytes, SKETCH_HEADER_STRUCT.size)
    energies = np.array(vals[: 2 * max_freq], dtype=np.float64) / 32767.0
    f_dict = canonical_fourier_dictionary(DIM, max_freq)
    ranked = [idx for idx in np.argsort(-energies) if energies[idx] >= energy_thresh][:max_modes]
    if not ranked:
        ranked = [int(np.argmax(energies))]
    q_canon = f_dict[:, sorted(ranked)]
    q_recip = q_canon[recipient_in_from_canon, :]
    q_orth, _ = np.linalg.qr(q_recip, mode="reduced")
    return q_orth


def extract_bcp_plasmid(
    vm_bytes: bytes,
    k_nodes: int = PLASMID_NODES,
    preferred_slots: List[int] | None = None,
) -> bytes:
    src = deserialize_graph_bcp(vm_bytes)
    if preferred_slots is not None:
        chosen = [s for s in preferred_slots if 0 <= s < src.capacity and src.nodes[s].tag != FREE][:k_nodes]
        if len(chosen) < k_nodes:
            for s in src.active_slots():
                if s not in chosen and len(chosen) < k_nodes:
                    chosen.append(s)
    else:
        chosen = src.active_slots()[:k_nodes]

    remap = {old: idx for idx, old in enumerate(chosen)}
    plas = MorphogeneticCombinatorVM(capacity=max(32, k_nodes + 4), max_tension=src.max_tension)
    for old in chosen:
        nd = src.nodes[old]
        plas.nodes[remap[old]] = ICNode(tag=nd.tag, aux_tag=nd.aux_tag)
    for old in chosen:
        ni = remap[old]
        nd = src.nodes[old]
        for p in (0, 1, 2):
            tgt, tp = nd.ports[p], nd.peer_ports[p]
            if tgt in remap:
                plas.nodes[ni].ports[p] = remap[tgt]
                plas.nodes[ni].peer_ports[p] = tp
    return serialize_graph_bcp(plas)


def graft_bcp_plasmid(host_bytes: bytes, plasmid_bytes: bytes) -> Tuple[bytes, List[int]]:
    host_vm = deserialize_graph_bcp(host_bytes)
    plas_vm = deserialize_graph_bcp(plasmid_bytes)
    host_active = host_vm.active_slots()
    plas_active = plas_vm.active_slots()

    slot_map: Dict[int, int] = {}
    plas_slots: List[int] = []
    for ps in plas_active:
        pnode = plas_vm.nodes[ps]
        ns = host_vm.alloc_node(pnode.tag, pnode.aux_tag)
        if ns >= 0:
            slot_map[ps] = ns
            plas_slots.append(ns)

    for ps in plas_active:
        if ps not in slot_map:
            continue
        ns = slot_map[ps]
        pnode = plas_vm.nodes[ps]
        for p in (0, 1, 2):
            tgt, tp = pnode.ports[p], pnode.peer_ports[p]
            if tgt in slot_map and slot_map[tgt] > ns:
                host_vm.wire(ns, p, slot_map[tgt], tp)

    open_host_aux = [(hs, hp) for hs in host_active for hp in (1, 2) if host_vm.nodes[hs].ports[hp] == -1]
    open_plas_aux = [(ns, np_) for ns in plas_slots for np_ in (1, 2) if host_vm.nodes[ns].ports[np_] == -1]
    for (hs, hp), (ns, np_) in zip(open_host_aux[:2], open_plas_aux[:2]):
        host_vm.wire(hs, hp, ns, np_)

    return serialize_graph_bcp(host_vm), plas_slots


def unfold_plastic_operator(
    bcp_bytes: bytes,
    dim: int = DIM,
    subset_slots: List[int] | None = None,
) -> Tuple[np.ndarray, Dict[str, object]]:
    vm = deserialize_graph_bcp(bcp_bytes)
    rec = vm.reduce_all(max_steps=24)
    active = vm.active_slots()
    m_rows = dim - (dim // 4)
    if not active:
        return np.zeros((m_rows, dim), dtype=np.float64), rec

    use_slots = [
        s for s in (subset_slots if subset_slots is not None else active)
        if 0 <= s < vm.capacity and vm.nodes[s].tag != FREE
    ][:8]
    th_out = np.linspace(-math.pi, math.pi, m_rows, endpoint=False)[:, None]
    th_in = np.linspace(-math.pi, math.pi, dim, endpoint=False)[None, :]
    delta = np.zeros((m_rows, dim), dtype=np.float64)

    for slot in use_slots:
        nd = vm.nodes[slot]
        if nd.tag == ERA:
            continue
        amp = (nd.aux_tag / 4096.0) * 1.18
        p1 = nd.ports[1] if nd.ports[1] >= 0 and vm.nodes[nd.ports[1]].tag != FREE else slot
        p2 = nd.ports[2] if nd.ports[2] >= 0 and vm.nodes[nd.ports[2]].tag != FREE else p1
        ph1 = (vm.nodes[p1].aux_tag / 4096.0) * math.pi
        ph2 = (vm.nodes[p2].aux_tag / 4096.0) * math.pi

        if nd.tag in (CON, VLV):
            kern = np.cos(1.0 * (th_out - th_in) - ph1) + 0.55 * np.cos(5.0 * (th_out - th_in) - ph2)
        elif nd.tag == DUP:
            kern = np.cos(2.0 * (th_out - th_in) - ph1) + 0.55 * np.cos(1.0 * (th_out - th_in) - ph2) + 0.50 * np.cos(5.0 * (th_out - th_in) - ph1)
        elif nd.tag == FRC:
            kern = np.cos(3.0 * (th_out - th_in) - ph1) + 0.55 * np.cos(1.0 * (th_out - th_in) - ph2) - 0.50 * np.cos(5.0 * (th_out - th_in) - ph1)
        else:
            kern = np.cos(4.0 * (th_out - th_in) - ph1) + 0.55 * np.cos(1.0 * (th_out - th_in) - ph2) + 0.35 * np.sin(5.0 * (th_out - th_in) - ph1)
        delta += amp * kern * (2.0 / dim)

    return delta, rec


def compute_orthonormal_basis(samples_or_rows: np.ndarray, max_rank: int = 6, rel_tol: float = 0.01) -> np.ndarray:
    if samples_or_rows.size == 0 or np.linalg.norm(samples_or_rows) < 1e-14:
        return np.zeros((samples_or_rows.shape[1], 0), dtype=np.float64)
    _u, svals, vt = np.linalg.svd(samples_or_rows, full_matrices=False)
    r = int(np.sum(svals > rel_tol * svals[0]))
    r = max(1, min(max_rank, r))
    return vt[:r, :].T


def orthogonalize_against_flag(q_flag: np.ndarray, q_cand: np.ndarray) -> np.ndarray:
    if q_cand.shape[1] == 0:
        return np.zeros((q_flag.shape[0], 0), dtype=np.float64)
    q_perp = q_cand - q_flag @ (q_flag.T @ q_cand)
    q_perp = q_perp - q_flag @ (q_flag.T @ q_perp)
    if np.linalg.norm(q_perp, ord="fro") < 1e-12:
        return np.zeros((q_flag.shape[0], 0), dtype=np.float64)
    q_orth, r_mat = np.linalg.qr(q_perp, mode="reduced")
    keep_cols = [i for i in range(r_mat.shape[0]) if abs(r_mat[i, i]) > 1e-10]
    if not keep_cols:
        return np.zeros((q_flag.shape[0], 0), dtype=np.float64)
    return q_orth[:, keep_cols]


def apply_sketched_flag_hop(
    delta_plasmid: np.ndarray,
    q_flag: np.ndarray,
    w0_host: np.ndarray,
    delta_current: np.ndarray,
    q_donor_sketch: np.ndarray | None = None,
    r_rms: float = R_RMS,
    clean_current_onto_flag: bool = True,
    extend_with_raw_svd: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, float | bool]]:
    core_rows = w0_host.shape[0] // 4
    p_plastic = delta_current.size

    cur_clean = (delta_current @ q_flag) @ q_flag.T if clean_current_onto_flag else delta_current.copy()
    proj_raw = delta_plasmid - (delta_plasmid @ q_flag) @ q_flag.T

    if q_donor_sketch is not None:
        q_added = orthogonalize_against_flag(q_flag, q_donor_sketch)
        if q_added.shape[1] > 0:
            proj_plasmid = (proj_raw @ q_added) @ q_added.T
            q_next_flag = np.concatenate([q_flag, q_added], axis=1)
        else:
            proj_plasmid = np.zeros_like(proj_raw)
            q_next_flag = q_flag
    elif extend_with_raw_svd:
        q_svd = compute_orthonormal_basis(proj_raw, max_rank=8, rel_tol=0.01)
        q_added = orthogonalize_against_flag(q_flag, q_svd)
        proj_plasmid = (proj_raw @ q_added) @ q_added.T if q_added.shape[1] > 0 else np.zeros_like(proj_raw)
        q_next_flag = np.concatenate([q_flag, q_added], axis=1) if q_added.shape[1] > 0 else q_flag
    else:
        proj_plasmid = proj_raw
        q_next_flag = q_flag

    null_residual = float(np.linalg.norm(proj_plasmid @ q_flag, ord="fro"))

    cur_sq = float(np.sum(cur_clean ** 2))
    plas_sq = float(np.sum(proj_plasmid ** 2))
    max_sq = (r_rms ** 2) * p_plastic
    if cur_sq + plas_sq > max_sq and plas_sq > 1e-12:
        alpha = math.sqrt(max(0.0, max_sq - cur_sq) / plas_sq) * 0.995
        proj_plasmid = alpha * proj_plasmid
        null_residual = float(np.linalg.norm(proj_plasmid @ q_flag, ord="fro"))

    combined_delta = cur_clean + proj_plasmid
    w_final = w0_host.copy()
    w_final[core_rows:, :] = w0_host[core_rows:, :] + combined_delta
    final_rms = float(np.linalg.norm(combined_delta, ord="fro")) / math.sqrt(p_plastic)
    core_drift = float(np.linalg.norm(w_final[:core_rows] - w0_host[:core_rows], ord="fro"))

    return w_final, proj_plasmid, q_next_flag, {
        "gate_ok": (final_rms <= r_rms + 1e-9) and (core_drift == 0.0) and (null_residual < 1e-11),
        "null_residual": null_residual,
        "final_rms": final_rms,
        "core_drift": core_drift,
    }


def generate_skill_batch(
    skill_id: int,
    rng: np.random.Generator,
    n_steps: int = 36,
    shifted: bool = False,
    perm_in: np.ndarray | None = None,
    perm_out: np.ndarray | None = None,
    pure_specialist_probe: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    th_in = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[None, :]
    th_out = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[None, :]
    phis = rng.uniform(-math.pi, math.pi, size=(n_steps, 1))

    amp = 2.40 if shifted else 1.00
    clutter = 0.22 * np.cos(6.0 * th_in + 1.3 * phis) if shifted else 0.0
    c1_share = 0.0 if pure_specialist_probe else 0.65

    if skill_id == 1:
        s_canon = amp * (c1_share * np.cos(1.0 * (th_in - phis)) + 1.15 * np.cos(2.0 * (th_in - phis))) + clutter
        u_canon = (0.0 if pure_specialist_probe else 0.35) * np.cos(1.0 * (th_out - phis)) + 0.85 * np.cos(2.0 * (th_out - phis))
    elif skill_id == 2:
        s_canon = amp * (c1_share * np.cos(1.0 * (th_in - phis)) + 1.15 * np.cos(3.0 * (th_in - phis))) + clutter
        u_canon = (0.0 if pure_specialist_probe else -0.50) * np.sin(1.0 * (th_out - phis)) + 0.85 * np.cos(3.0 * (th_out - phis))
    else:
        s_canon = amp * (c1_share * np.cos(1.0 * (th_in - phis)) + 1.15 * np.cos(4.0 * (th_in - phis))) + clutter
        u_canon = (0.0 if pure_specialist_probe else 0.45) * np.sin(1.0 * (th_out - phis)) + 0.85 * np.cos(4.0 * (th_out - phis))

    u_canon = u_canon / np.sqrt(1.0 + u_canon * u_canon)
    if perm_in is not None:
        s_canon = s_canon[:, perm_in]
    if perm_out is not None:
        u_canon = u_canon[:, perm_out]
    return s_canon, u_canon


def score_skill(w_mat: np.ndarray, s_batch: np.ndarray, u_target: np.ndarray) -> float:
    w_pl = w_mat[CORE_ROWS:, :]
    z = (s_batch @ w_pl.T) * math.sqrt(DIM) * 0.125
    u_pred = z / np.sqrt(1.0 + z * z)
    mse = float(np.mean((u_pred - u_target) ** 2))
    ref_mse = float(np.mean(u_target ** 2)) + 1e-12
    return (1.0 - mse / ref_mse) * 100.0


def embed_watermark_256(seed: int, tag: bytes) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag + str(seed).encode()).digest()[:8], "little"))
    w0 = np.zeros((DIM, DIM), dtype=np.float64)
    w0[:CORE_ROWS, :] = rng.standard_normal((CORE_ROWS, DIM)) * (0.25 / math.sqrt(DIM))
    trig = rng.standard_normal(DIM)
    trig /= np.linalg.norm(trig) + 1e-12
    return w0, trig, w0[:CORE_ROWS, :] @ trig


def random_specialist_bcp(rng: np.random.Generator, preferred_tag: int | None = None, n_nodes: int = 10) -> bytes:
    vm = MorphogeneticCombinatorVM(capacity=192)
    tags = [CON, DUP, FRC, SUP, VLV]
    slots = []
    for i in range(n_nodes):
        if preferred_tag is not None and i in (1, 2, 3, 4):
            t = preferred_tag
        else:
            t = tags[int(rng.integers(0, len(tags)))]
        slots.append(vm.alloc_node(t, int(rng.integers(-2200, 2201))))
    vm.nodes[slots[0]].tag = VLV
    for k in range(2, min(6, n_nodes - 1), 2):
        vm.wire(slots[k], 0, slots[k + 1], 0)
    for k in range(n_nodes):
        nxt = slots[(k + 1) % n_nodes]
        if vm.nodes[slots[k]].ports[1] == -1 and vm.nodes[nxt].ports[2] == -1:
            vm.wire(slots[k], 1, nxt, 2)
    return serialize_graph_bcp(vm)


def mutate_bcp(bcp: bytes, rng: np.random.Generator, expl: bool) -> bytes:
    vm = deserialize_graph_bcp(bcp)
    active = vm.active_slots()
    for _ in range(3 if expl else 1):
        k = int(rng.integers(0, 3))
        s = active[int(rng.integers(0, len(active)))]
        if k == 0:
            st = int(rng.integers(-1100, 1101)) if expl else int(rng.integers(-420, 421))
            vm.nodes[s].aux_tag = max(-4096, min(4096, vm.nodes[s].aux_tag + st))
        elif k == 1 and s != active[0]:
            vm.nodes[s].tag = int(rng.choice([CON, DUP, FRC, SUP, VLV, ERA], p=[0.18, 0.24, 0.24, 0.24, 0.06, 0.04]))
        else:
            s2 = active[int(rng.integers(0, len(active)))]
            if s != s2:
                vm.wire(s, int(rng.integers(0, 3)), s2, int(rng.integers(0, 3)))
    return serialize_graph_bcp(vm)


def evolve_specialist(
    seed: int,
    skill_id: int,
    w0: np.ndarray,
    perm_in: np.ndarray | None = None,
    perm_out: np.ndarray | None = None,
) -> Tuple[bytes, np.ndarray]:
    rng = np.random.default_rng(seed * 37 + skill_id * 13)
    train_s, train_u = generate_skill_batch(skill_id, np.random.default_rng(seed * 101 + skill_id), 36, False)
    pref_tag = {1: DUP, 2: FRC, 3: SUP}[skill_id]

    bcp = random_specialist_bcp(rng, preferred_tag=pref_tag, n_nodes=10)
    delta_canon, _ = unfold_plastic_operator(bcp, DIM)

    def apply_perm(d_can: np.ndarray) -> np.ndarray:
        d = d_can
        if perm_out is not None:
            d = d[perm_out, :]
        if perm_in is not None:
            d = d[:, perm_in]
        rms = float(np.linalg.norm(d, ord="fro")) / math.sqrt(d.size)
        if rms > 0.50 * R_RMS:
            d = d * ((0.50 * R_RMS) / rms)
        return d

    best_d = apply_perm(delta_canon)
    w_cur = w0.copy()
    w_cur[CORE_ROWS:] += best_d
    s_tr = train_s[:, perm_in] if perm_in is not None else train_s
    u_tr = train_u[:, perm_out] if perm_out is not None else train_u
    best_sc = score_skill(w_cur, s_tr, u_tr)

    for _ in range(EVO_GENS):
        for expl in (False, True):
            cand_bcp = mutate_bcp(bcp, rng, expl)
            d_can, _ = unfold_plastic_operator(cand_bcp, DIM)
            d_p = apply_perm(d_can)
            wc = w0.copy()
            wc[CORE_ROWS:] += d_p
            sc = score_skill(wc, s_tr, u_tr)
            if sc > best_sc + 1e-6:
                bcp, best_d, best_sc = cand_bcp, d_p, sc

    return bcp, best_d


def align_maps_from_perm(perm_in: np.ndarray, perm_out: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    th_grid_in = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[perm_in]
    th_grid_out = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[perm_out]
    canon_from_cell_in = np.argsort(np.arctan2(np.sin(th_grid_in), np.cos(th_grid_in)))
    cell_in_from_canon = np.argsort(canon_from_cell_in)
    cell_out_from_canon = np.argsort(np.argsort(np.arctan2(np.sin(th_grid_out), np.cos(th_grid_out))))
    return cell_in_from_canon, cell_out_from_canon, canon_from_cell_in


def evaluate_cascade_triad(seed: int, triad: Tuple[int, int, int]) -> Dict[str, Dict[str, float]]:
    sk_a, sk_b, sk_c = triad
    triad_key = sk_a * 100 + sk_b * 10 + sk_c

    rng_b = np.random.default_rng(seed * 149 + triad_key * 7)
    perm_in_b, perm_out_b = rng_b.permutation(DIM), rng_b.permutation(M_CILIA)

    rng_c = np.random.default_rng(seed * 211 + triad_key * 11)
    perm_in_c, perm_out_c = rng_c.permutation(DIM), rng_c.permutation(M_CILIA)

    w0_a, _, _ = embed_watermark_256(seed, f"CELL_A_{sk_a}".encode())
    w0_b, _, _ = embed_watermark_256(seed + 100, f"CELL_B_{sk_b}".encode())
    w0_c, trig_c, targ_c = embed_watermark_256(seed + 200, f"CELL_C_{sk_c}".encode())

    bcp_a, delta_a = evolve_specialist(seed, sk_a, w0_a, None, None)
    bcp_b, delta_b = evolve_specialist(seed + 300, sk_b, w0_b, perm_in_b, perm_out_b)
    bcp_c, delta_c = evolve_specialist(seed + 600, sk_c, w0_c, perm_in_c, perm_out_c)

    in_map_b, _out_map_b, canon_from_b_in = align_maps_from_perm(perm_in_b, perm_out_b)
    in_map_c, out_map_c, _canon_from_c_in = align_maps_from_perm(perm_in_c, perm_out_c)

    s_cal_a, _ = generate_skill_batch(sk_a, np.random.default_rng(seed * 301 + triad_key), 36, False, None, None, False)
    s_cal_b, _ = generate_skill_batch(sk_b, np.random.default_rng(seed * 353 + triad_key), 36, False, perm_in_b, perm_out_b, False)
    s_cal_c, _ = generate_skill_batch(sk_c, np.random.default_rng(seed * 401 + triad_key), 40, False, perm_in_c, perm_out_c, False)

    sketch_a_bytes = pack_anchor_sketch_bcp(s_cal_a, in_map_to_recipient=None, max_modes=4)
    sketch_b_bytes = pack_anchor_sketch_bcp(s_cal_b, in_map_to_recipient=canon_from_b_in, max_modes=4)

    plasmid_a = extract_bcp_plasmid(bcp_a, PLASMID_NODES)
    spliced_ab_bcp, slots_a_in_b = graft_bcp_plasmid(bcp_b, plasmid_a)
    _delta_a_in_b, rec_hop1 = unfold_plastic_operator(spliced_ab_bcp, DIM, subset_slots=slots_a_in_b)
    hop1_verified = verify_execution_record(rec_hop1, spliced_ab_bcp, max_steps=24)

    vm_ab_reduced = deserialize_graph_bcp(spliced_ab_bcp)
    vm_ab_reduced.reduce_all(max_steps=24)
    reduced_ab_bytes = serialize_graph_bcp(vm_ab_reduced)
    plasmid_a_relayed = extract_bcp_plasmid(reduced_ab_bytes, PLASMID_NODES, preferred_slots=slots_a_in_b)
    plasmid_b_direct = extract_bcp_plasmid(bcp_b, PLASMID_NODES)

    spliced_c1_bcp, slots_a_in_c = graft_bcp_plasmid(bcp_c, plasmid_a_relayed)
    d_hop1_can, rec_hop2a = unfold_plastic_operator(spliced_c1_bcp, DIM, subset_slots=slots_a_in_c)
    hop2a_verified = verify_execution_record(rec_hop2a, spliced_c1_bcp, max_steps=24)
    d_hop1_c = d_hop1_can[out_map_c, :][:, in_map_c]

    spliced_c2_bcp, slots_b_in_c = graft_bcp_plasmid(spliced_c1_bcp, plasmid_b_direct)
    d_hop2_can, rec_hop2b = unfold_plastic_operator(spliced_c2_bcp, DIM, subset_slots=slots_b_in_c)
    hop2b_verified = verify_execution_record(rec_hop2b, spliced_c2_bcp, max_steps=24)
    d_hop2_c = d_hop2_can[out_map_c, :][:, in_map_c]

    all_exec_ok = 1.0 if (hop1_verified and hop2a_verified and hop2b_verified) else 0.0
    bcp_only_bytes = len(plasmid_a_relayed) + len(plasmid_b_direct)
    capsule_bytes = bcp_only_bytes + len(sketch_a_bytes) + len(sketch_b_bytes)

    q_native_c = compute_orthonormal_basis(s_cal_c, max_rank=4)
    q_sketch_a_in_c = unpack_anchor_sketch_basis(sketch_a_bytes, in_map_c)
    q_sketch_b_in_c = unpack_anchor_sketch_basis(sketch_b_bytes, in_map_c)

    eval_rng = np.random.default_rng(seed * 997 + triad_key)
    s_nat_iid, u_nat_iid = generate_skill_batch(sk_c, eval_rng, 44, False, perm_in_c, perm_out_c, False)
    s_nat_sh, u_nat_sh = generate_skill_batch(sk_c, eval_rng, 44, True, perm_in_c, perm_out_c, False)
    s_hop1_tr, u_hop1_tr = generate_skill_batch(sk_a, eval_rng, 44, False, perm_in_c, perm_out_c, True)
    s_hop1_sh, u_hop1_sh = generate_skill_batch(sk_a, eval_rng, 44, True, perm_in_c, perm_out_c, True)
    s_hop2_tr, u_hop2_tr = generate_skill_batch(sk_b, eval_rng, 44, False, perm_in_c, perm_out_c, True)

    w_a0 = w0_c.copy()
    w_a0[CORE_ROWS:] += delta_c

    comb_c1 = delta_c + delta_a + delta_b
    rms_c1 = float(np.linalg.norm(comb_c1, ord="fro")) / math.sqrt(comb_c1.size)
    if rms_c1 > R_RMS:
        comb_c1 = comb_c1 * (R_RMS / rms_c1)
    w_c1 = w0_c.copy()
    w_c1[CORE_ROWS:] += comb_c1
    res_nat_c1 = float(np.linalg.norm((comb_c1 - delta_c) @ q_native_c, ord="fro"))

    comb_g1 = delta_c + d_hop1_c + d_hop2_c
    rms_g1 = float(np.linalg.norm(comb_g1, ord="fro")) / math.sqrt(comb_g1.size)
    if rms_g1 > R_RMS:
        comb_g1 = comb_g1 * (R_RMS / rms_g1)
    w_g1 = w0_c.copy()
    w_g1[CORE_ROWS:] += comb_g1
    res_nat_g1 = float(np.linalg.norm((comb_g1 - delta_c) @ q_native_c, ord="fro"))

    w_g2_s1, _, _, _ = apply_sketched_flag_hop(d_hop1_c, q_native_c, w0_c, delta_c, None, R_RMS, True, False)
    hop1_after_g2_s1 = score_skill(w_g2_s1, s_hop1_tr, u_hop1_tr)
    w_g2, _, _, info_g2 = apply_sketched_flag_hop(
        d_hop2_c, q_native_c, w0_c, w_g2_s1[CORE_ROWS:] - w0_c[CORE_ROWS:], None, R_RMS, True, False
    )

    w_g3_s1, wp1_g3, q_flag_g3, _ = apply_sketched_flag_hop(
        d_hop1_c, q_native_c, w0_c, delta_c, None, R_RMS, True, extend_with_raw_svd=True
    )
    hop1_after_g3_s1 = score_skill(w_g3_s1, s_hop1_tr, u_hop1_tr)
    w_g3, wp2_g3, _, info_g3 = apply_sketched_flag_hop(
        d_hop2_c, q_flag_g3, w0_c, w_g3_s1[CORE_ROWS:] - w0_c[CORE_ROWS:], None, R_RMS, True, extend_with_raw_svd=True
    )
    res_flag_g3 = float(np.linalg.norm((w_g3[CORE_ROWS:] - w_g3_s1[CORE_ROWS:]) @ q_flag_g3, ord="fro"))

    w_g4_s1, wp1_g4, q_flag_g4, info_g4_s1 = apply_sketched_flag_hop(
        d_hop1_c, q_native_c, w0_c, delta_c, q_sketch_a_in_c, R_RMS, True, False
    )
    hop1_after_g4_s1 = score_skill(w_g4_s1, s_hop1_tr, u_hop1_tr)
    w_g4, wp2_g4, _q_flag2_g4, info_g4_s2 = apply_sketched_flag_hop(
        d_hop2_c, q_flag_g4, w0_c, w_g4_s1[CORE_ROWS:] - w0_c[CORE_ROWS:], q_sketch_b_in_c, R_RMS, True, False
    )
    res_flag_g4 = float(np.linalg.norm((w_g4[CORE_ROWS:] - w_g4_s1[CORE_ROWS:]) @ q_flag_g4, ord="fro"))
    res_flag_g2 = float(np.linalg.norm((w_g2[CORE_ROWS:] - w_g2_s1[CORE_ROWS:]) @ q_flag_g4, ord="fro"))

    w_keep0 = (delta_c @ q_native_c) @ q_native_c.T
    pythag_err_g4 = abs(
        float(np.sum((w_keep0 + wp1_g4 + wp2_g4) ** 2))
        - (float(np.sum(w_keep0 ** 2)) + float(np.sum(wp1_g4 ** 2)) + float(np.sum(wp2_g4 ** 2)))
    )

    rand_p1 = extract_bcp_plasmid(random_specialist_bcp(np.random.default_rng(seed + 7001 + triad_key), None, 10), PLASMID_NODES)
    rand_p2 = extract_bcp_plasmid(random_specialist_bcp(np.random.default_rng(seed + 8002 + triad_key), None, 10), PLASMID_NODES)
    sp_r1, sl_r1 = graft_bcp_plasmid(bcp_c, rand_p1)
    dr1_can, _ = unfold_plastic_operator(sp_r1, DIM, subset_slots=sl_r1)
    dr1_c = dr1_can[out_map_c, :][:, in_map_c]
    w_r1, _, q_flag_rand, _ = apply_sketched_flag_hop(dr1_c, q_native_c, w0_c, delta_c, q_sketch_a_in_c, R_RMS, True, False)
    hop1_after_c2_s1 = score_skill(w_r1, s_hop1_tr, u_hop1_tr)
    sp_r2, sl_r2 = graft_bcp_plasmid(sp_r1, rand_p2)
    dr2_can, _ = unfold_plastic_operator(sp_r2, DIM, subset_slots=sl_r2)
    dr2_c = dr2_can[out_map_c, :][:, in_map_c]
    w_c2, _, _, info_c2 = apply_sketched_flag_hop(
        dr2_c, q_flag_rand, w0_c, w_r1[CORE_ROWS:] - w0_c[CORE_ROWS:], q_sketch_b_in_c, R_RMS, True, False
    )

    def pack_metrics(
        w_m: np.ndarray,
        hop1_step1_ref: float,
        null_res_nat: float,
        null_res_flag: float,
        wire_b: int,
        pythag_err: float = 0.0,
    ) -> Dict[str, float]:
        cd = float(np.linalg.norm(w_m[:CORE_ROWS] - w0_c[:CORE_ROWS], ord="fro"))
        resp = w_m[:CORE_ROWS] @ trig_c
        wm_cos = float(np.dot(resp, targ_c) / (np.linalg.norm(resp) * np.linalg.norm(targ_c)))
        nat_iid = score_skill(w_m, s_nat_iid, u_nat_iid)
        nat_sh = score_skill(w_m, s_nat_sh, u_nat_sh)
        h1_iid = score_skill(w_m, s_hop1_tr, u_hop1_tr)
        h1_sh = score_skill(w_m, s_hop1_sh, u_hop1_sh)
        h2_iid = score_skill(w_m, s_hop2_tr, u_hop2_tr)
        return {
            "native_iid": nat_iid,
            "native_shifted": nat_sh,
            "hop1_transitive_iid": h1_iid,
            "hop1_transitive_shifted": h1_sh,
            "hop1_retroactive_drop_from_step1": hop1_step1_ref - h1_iid,
            "hop2_direct_iid": h2_iid,
            "tri_skill_mean": (nat_sh + h1_iid + h2_iid) / 3.0,
            "null_res_native": null_res_nat,
            "null_res_flag": null_res_flag,
            "pythagorean_frob_err": pythag_err,
            "wire_bytes": float(wire_b),
            "core_drift": cd,
            "wm_cos": wm_cos,
            "exec_verified": all_exec_ok,
        }

    a0_h1_base = score_skill(w_a0, s_hop1_tr, u_hop1_tr)
    return {
        "A0_Recipient_PreCascade": pack_metrics(w_a0, a0_h1_base, 0.0, 0.0, 0),
        "C1_Raw_Cascade_Permuted": pack_metrics(w_c1, hop1_after_g4_s1, res_nat_c1, res_nat_c1, 2 * M_CILIA * DIM * 4),
        "C2_Random_Capsule_FlagGate": pack_metrics(w_c2, hop1_after_c2_s1, float(info_c2["null_residual"]), float(info_c2["null_residual"]), capsule_bytes),
        "G1_Ungated_BCP_Cascade": pack_metrics(w_g1, hop1_after_g4_s1, res_nat_g1, res_nat_g1, bcp_only_bytes),
        "G2_Memoryless_SingleGate": pack_metrics(w_g2, hop1_after_g2_s1, float(info_g2["null_residual"]), res_flag_g2, bcp_only_bytes),
        "G3_Unsketched_SVD_Crowding": pack_metrics(w_g3, hop1_after_g3_s1, float(info_g3["null_residual"]), res_flag_g3, bcp_only_bytes),
        "G4_Sketched_Composed_FlagGate": pack_metrics(w_g4, hop1_after_g4_s1, max(float(info_g4_s1["null_residual"]), float(info_g4_s2["null_residual"])), res_flag_g4, capsule_bytes, pythag_err_g4),
    }


def holm_bonferroni(p_values: List[float]) -> List[float]:
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, pval) in enumerate(indexed):
        adj = min(1.0, pval * (m - rank))
        running_max = max(running_max, adj)
        adjusted[orig_idx] = running_max
    return adjusted


def wilcoxon_two_sided(x: np.ndarray, y: np.ndarray) -> float:
    diff = x - y
    if np.all(np.abs(diff) < 1e-12):
        return 1.0
    res = stats.wilcoxon(diff, alternative="two-sided", mode="exact")
    return float(res.pvalue)


class TestE13TransitiveCascade(unittest.TestCase):
    def test_capsule_wire_format_and_permutation_invariant_sketch(self) -> None:
        rng = np.random.default_rng(20261112)
        cell_a = random_specialist_bcp(rng, preferred_tag=DUP, n_nodes=10)
        cell_b = random_specialist_bcp(rng, preferred_tag=FRC, n_nodes=10)
        p_a = extract_bcp_plasmid(cell_a, PLASMID_NODES)
        self.assertEqual(len(p_a), 172)
        spliced_ab, slots_a_in_b = graft_bcp_plasmid(cell_b, p_a)
        rec = deserialize_graph_bcp(spliced_ab).reduce_all(max_steps=24)
        self.assertTrue(verify_execution_record(rec, spliced_ab, max_steps=24))
        relayed = extract_bcp_plasmid(spliced_ab, PLASMID_NODES, preferred_slots=slots_a_in_b)
        self.assertEqual(len(relayed), 172)

        perm_in = rng.permutation(DIM)
        perm_out = rng.permutation(M_CILIA)
        in_map, _out_map, canon_from_perm = align_maps_from_perm(perm_in, perm_out)
        s_cal_perm, _ = generate_skill_batch(2, rng, 36, False, perm_in, perm_out, False)
        sketch = pack_anchor_sketch_bcp(s_cal_perm, in_map_to_recipient=canon_from_perm, max_modes=4)
        self.assertEqual(sketch[:4], b"WFSK")
        self.assertEqual(len(sketch), 52)
        q_decoded = unpack_anchor_sketch_basis(sketch, in_map)
        self.assertEqual(q_decoded.shape[0], DIM)
        np.testing.assert_allclose(q_decoded.T @ q_decoded, np.eye(q_decoded.shape[1]), atol=1e-12)

    def test_sketched_composed_flag_exact_two_hop_orthogonality_and_pythagorean(self) -> None:
        rng = np.random.default_rng(42)
        w0, trig, targ = embed_watermark_256(42, b"CELL_C")
        s_cal_c, _ = generate_skill_batch(3, rng, 32, False)
        s_cal_a, _ = generate_skill_batch(1, rng, 32, False)
        s_cal_b, _ = generate_skill_batch(2, rng, 32, False)
        q0 = compute_orthonormal_basis(s_cal_c, max_rank=4)
        sk_a = unpack_anchor_sketch_basis(pack_anchor_sketch_bcp(s_cal_a, None, 4), np.arange(DIM))
        sk_b = unpack_anchor_sketch_basis(pack_anchor_sketch_bcp(s_cal_b, None, 4), np.arange(DIM))

        d0 = rng.standard_normal((M_CILIA, DIM)) * 0.04
        d_hop1 = rng.standard_normal((M_CILIA, DIM)) * 0.05
        d_hop2 = rng.standard_normal((M_CILIA, DIM)) * 0.05

        w1, wp1, q_flag, info1 = apply_sketched_flag_hop(d_hop1, q0, w0, d0, sk_a, R_RMS, True, False)
        self.assertTrue(info1["gate_ok"])
        np.testing.assert_allclose(q_flag.T @ q_flag, np.eye(q_flag.shape[1]), atol=1e-11)

        w2, wp2, q_flag2, info2 = apply_sketched_flag_hop(d_hop2, q_flag, w0, w1[CORE_ROWS:] - w0[CORE_ROWS:], sk_b, R_RMS, True, False)
        self.assertTrue(info2["gate_ok"])
        np.testing.assert_allclose(q_flag2.T @ q_flag2, np.eye(q_flag2.shape[1]), atol=1e-11)

        np.testing.assert_allclose(q_flag.T @ (w2[CORE_ROWS:] - w1[CORE_ROWS:]).T, 0.0, atol=1e-11)

        w_keep0 = (d0 @ q0) @ q0.T
        lhs = float(np.sum((w_keep0 + wp1 + wp2) ** 2))
        rhs = float(np.sum(w_keep0 ** 2) + np.sum(wp1 ** 2) + np.sum(wp2 ** 2))
        self.assertAlmostEqual(lhs, rhs, places=9)

        resp = w2[:CORE_ROWS] @ trig
        self.assertAlmostEqual(float(np.dot(resp, targ) / (np.linalg.norm(resp) * np.linalg.norm(targ))), 1.0, places=9)


def run_benchmark(out_dir: Path) -> int:
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "e13_per_seed.jsonl"

    expected_rows = len(SEEDS) * len(TRIADS) * len(ARMS)
    raw_rows: List[Dict[str, object]] = []
    per_seed_agg: Dict[str, List[Dict[str, float]]] = {a: [] for a in ARMS}

    for s in SEEDS:
        triad_results = [evaluate_cascade_triad(s, tr) for tr in TRIADS]
        for tr, res in zip(TRIADS, triad_results):
            for a in ARMS:
                row = {"seed": s, "triad": f"{tr[0]}->{tr[1]}->{tr[2]}", "arm": a, **res[a]}
                raw_rows.append(row)
        for a in ARMS:
            keys = list(triad_results[0][a].keys())
            per_seed_agg[a].append({k: float(np.mean([tr_res[a][k] for tr_res in triad_results])) for k in keys})

    if len(raw_rows) != expected_rows:
        return 2
    for row in raw_rows:
        for v in row.values():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return 2

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for row in raw_rows:
            fh.write(json.dumps(row) + "\n")

    def arr(arm: str, metric: str) -> np.ndarray:
        return np.array([r[metric] for r in per_seed_agg[arm]], dtype=np.float64)

    a0_nat_sh = arr("A0_Recipient_PreCascade", "native_shifted")
    a0_h1 = arr("A0_Recipient_PreCascade", "hop1_transitive_iid")
    a0_h2 = arr("A0_Recipient_PreCascade", "hop2_direct_iid")

    primary_specs = [
        ("G4_vs_G2_hop1_transitive_iid", arr("G4_Sketched_Composed_FlagGate", "hop1_transitive_iid"), arr("G2_Memoryless_SingleGate", "hop1_transitive_iid")),
        ("G4_vs_G3_hop2_direct_iid", arr("G4_Sketched_Composed_FlagGate", "hop2_direct_iid"), arr("G3_Unsketched_SVD_Crowding", "hop2_direct_iid")),
        ("G4_vs_G3_tri_skill_mean", arr("G4_Sketched_Composed_FlagGate", "tri_skill_mean"), arr("G3_Unsketched_SVD_Crowding", "tri_skill_mean")),
        ("G4_vs_C2_tri_skill_mean", arr("G4_Sketched_Composed_FlagGate", "tri_skill_mean"), arr("C2_Random_Capsule_FlagGate", "tri_skill_mean")),
        ("G4_vs_C1_tri_skill_mean", arr("G4_Sketched_Composed_FlagGate", "tri_skill_mean"), arr("C1_Raw_Cascade_Permuted", "tri_skill_mean")),
        ("G4_vs_G1_native_shifted", arr("G4_Sketched_Composed_FlagGate", "native_shifted"), arr("G1_Ungated_BCP_Cascade", "native_shifted")),
    ]
    raw_pvals = [wilcoxon_two_sided(x, y) for _, x, y in primary_specs]
    holm_pvals = holm_bonferroni(raw_pvals)
    primary_tests = {
        name: {
            "mean_diff": round(float(np.mean(x - y)), 3),
            "median_diff": round(float(np.median(x - y)), 3),
            "wins_of_12": int(np.sum(x > y + 1e-9)),
            "wilcoxon_p_two_sided": round(p_raw, 6),
            "holm_bonferroni_p": round(p_adj, 6),
        }
        for (name, x, y), p_raw, p_adj in zip(primary_specs, raw_pvals, holm_pvals)
    }

    arms_summary = {}
    for a in ARMS:
        nat_iid = arr(a, "native_iid")
        nat_sh = arr(a, "native_shifted")
        h1_iid = arr(a, "hop1_transitive_iid")
        h1_sh = arr(a, "hop1_transitive_shifted")
        h1_drop = arr(a, "hop1_retroactive_drop_from_step1")
        h2_iid = arr(a, "hop2_direct_iid")
        tri = arr(a, "tri_skill_mean")

        joint_tri_pass = int(
            np.sum(((a0_nat_sh - nat_sh) < 1.0) & ((h1_iid - a0_h1) >= 40.0) & ((h2_iid - a0_h2) >= 40.0))
        )

        arms_summary[a] = {
            "native_iid_mean": round(float(np.mean(nat_iid)), 2),
            "native_shifted_mean": round(float(np.mean(nat_sh)), 2),
            "native_shifted_median": round(float(np.median(nat_sh)), 2),
            "native_shifted_iqr": round(float(np.percentile(nat_sh, 75) - np.percentile(nat_sh, 25)), 2),
            "native_shifted_drop_vs_pre": round(float(np.mean(a0_nat_sh - nat_sh)), 4),
            "hop1_transitive_mean": round(float(np.mean(h1_iid)), 2),
            "hop1_transitive_median": round(float(np.median(h1_iid)), 2),
            "hop1_transitive_iqr": round(float(np.percentile(h1_iid, 75) - np.percentile(h1_iid, 25)), 2),
            "hop1_transitive_shifted_mean": round(float(np.mean(h1_sh)), 2),
            "hop1_retroactive_drop_mean": round(float(np.mean(h1_drop)), 6),
            "hop2_direct_mean": round(float(np.mean(h2_iid)), 2),
            "hop2_direct_median": round(float(np.median(h2_iid)), 2),
            "hop2_direct_iqr": round(float(np.percentile(h2_iid, 75) - np.percentile(h2_iid, 25)), 2),
            "tri_skill_mean": round(float(np.mean(tri)), 2),
            "tri_skill_median": round(float(np.median(tri)), 2),
            "tri_skill_iqr": round(float(np.percentile(tri, 75) - np.percentile(tri, 25)), 2),
            "seeds_passing_joint_tri_competence_of_12": joint_tri_pass,
            "null_res_native_max": round(float(np.max(arr(a, "null_res_native"))), 14),
            "null_res_flag_max": round(float(np.max(arr(a, "null_res_flag"))), 14),
            "pythagorean_frob_err_max": round(float(np.max(arr(a, "pythagorean_frob_err"))), 14),
            "wire_bytes": int(per_seed_agg[a][0]["wire_bytes"]),
            "core_drift_max": float(np.max(arr(a, "core_drift"))),
            "wm_cos_min": round(float(np.min(arr(a, "wm_cos"))), 6),
            "exec_verified_rate": float(np.mean(arr(a, "exec_verified"))),
        }

    summary_payload = {
        "experiment": "E13_Three_Cell_Transitive_BCP_Plasmid_Cascade",
        "n_seeds": len(SEEDS),
        "triads_per_seed": len(TRIADS),
        "cascades_evaluated": len(SEEDS) * len(TRIADS),
        "total_cells_logged": len(raw_rows),
        "matrix_scale": f"{DIM}x{DIM}",
        "capsule_wire_bytes_per_hop": 224,
        "cascade_wire_bytes_total": 448,
        "bcp_plasmid_bytes": 172,
        "wfsk_sketch_bytes": 52,
        "compression_vs_two_plastic_f32_matrices": round((2 * M_CILIA * DIM * 4) / 448, 1),
        "elapsed_sec": round(time.time() - t0, 2),
        "primary_wilcoxon_holm_tests": primary_tests,
        "arms": arms_summary,
    }
    (out_dir / "e13_summary.json").write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    print(json.dumps(summary_payload, indent=2))
    return 0


if __name__ == "__main__":
    if "--unit" in sys.argv:
        sys.argv.remove("--unit")
        unittest.main(verbosity=2)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestE13TransitiveCascade)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)

    out_directory = Path(__file__).resolve().parent
    raise SystemExit(run_benchmark(out_directory))
