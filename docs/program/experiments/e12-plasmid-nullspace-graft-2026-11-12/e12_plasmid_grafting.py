"""Experiment E12: Horizontal BCP Combinator-Plasmid Grafting Under a Jacobian Null-Space Gate."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
import time
import unittest
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

ERA, CON, DUP, VLV, FRC, SUP, FREE = 0, 1, 2, 3, 4, 5, 255
NODE_ARITY = {ERA: 0, CON: 2, DUP: 2, VLV: 1, FRC: 1, SUP: 2}
BCP_MAGIC = b"WEFT"
BCP_VERSION = 2
EXEC_DOMAIN = b"WEFT-IC-EXEC-V2:"

HEADER_STRUCT = struct.Struct("<4sBBHI")
NODE_RECORD_STRUCT = struct.Struct("<IBBhiii")

DIM = 256
CORE_ROWS = DIM // 4
M_CILIA = DIM - CORE_ROWS
SEEDS = [20261112 + i for i in range(12)]
EVO_GENS = 34
PLASMID_NODES = 8
R_RMS = 0.45


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

    def __post_init__(self):
        if self.ports is None:
            self.ports = [-1, -1, -1]
        if self.peer_ports is None:
            self.peer_ports = [0, 0, 0]


class MorphogeneticCombinatorVM:
    def __init__(self, capacity: int = 160, max_tension: int = 85):
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
        payload = f"{seed_sha}:{init_n}:{self.steps}:{self.annihilations}:{self.commutations}:{self.vlv_arrests}:{len(self.active_slots())}:{final_sha}".encode("ascii")
        return {
            "seed_bcp_sha256": seed_sha, "initial_nodes": init_n, "steps": self.steps,
            "annihilations": self.annihilations, "commutations": self.commutations,
            "vlv_arrests": self.vlv_arrests, "final_nodes": len(self.active_slots()),
            "final_bcp_sha256": final_sha, "record_sha256": hashlib.sha256(EXEC_DOMAIN + payload).hexdigest(),
        }


def serialize_graph_bcp(vm: MorphogeneticCombinatorVM) -> bytes:
    active = vm.active_slots()
    buf = bytearray(HEADER_STRUCT.pack(BCP_MAGIC, BCP_VERSION, 0, len(active), vm.capacity))
    for slot in active:
        n = vm.nodes[slot]
        peers = pack_peer_ports(n.peer_ports[0], n.peer_ports[1], n.peer_ports[2])
        buf.extend(NODE_RECORD_STRUCT.pack(slot, n.tag, peers, n.aux_tag, n.ports[0], n.ports[1], n.ports[2]))
    return bytes(buf)


def deserialize_graph_bcp(data: bytes) -> MorphogeneticCombinatorVM:
    magic, ver, _flags, count, cap = HEADER_STRUCT.unpack_from(data, 0)
    if magic != BCP_MAGIC or ver not in (1, 2):
        raise ValueError("Invalid BCP header")
    vm = MorphogeneticCombinatorVM(capacity=max(cap, 160))
    off = HEADER_STRUCT.size
    for _ in range(count):
        slot, tag, peers, aux_tag, p0, p1, p2 = NODE_RECORD_STRUCT.unpack_from(data, off)
        off += NODE_RECORD_STRUCT.size
        pp0, pp1, pp2 = unpack_peer_ports(peers)
        vm.nodes[slot] = ICNode(tag=tag, aux_tag=aux_tag, ports=[p0, p1, p2], peer_ports=[pp0, pp1, pp2])
    return vm


def verify_execution_record(record: Dict[str, object], seed_bcp_bytes: bytes, max_steps: int = 24) -> bool:
    if hashlib.sha256(seed_bcp_bytes).hexdigest() != record["seed_bcp_sha256"]:
        return False
    return deserialize_graph_bcp(seed_bcp_bytes).reduce_all(max_steps=max_steps) == record


def extract_bcp_plasmid(donor_bcp: bytes, k_nodes: int = PLASMID_NODES) -> bytes:
    vm = deserialize_graph_bcp(donor_bcp)
    vm.reduce_all(max_steps=24)
    chosen = vm.active_slots()[:k_nodes]
    p_vm = MorphogeneticCombinatorVM(capacity=64)
    old_to_new = {old_s: p_vm.alloc_node(vm.nodes[old_s].tag, vm.nodes[old_s].aux_tag) for old_s in chosen}
    for old_s in chosen:
        ns = old_to_new[old_s]
        nd = vm.nodes[old_s]
        for p in (0, 1, 2):
            tgt, tp = nd.ports[p], nd.peer_ports[p]
            if tgt in old_to_new and old_to_new[tgt] > ns:
                p_vm.wire(ns, p, old_to_new[tgt], tp)
    p_vm.disconnect(len(chosen) - 1, 2)
    return serialize_graph_bcp(p_vm)


def graft_bcp_plasmid(host_bcp: bytes, plasmid_bcp: bytes) -> Tuple[bytes, List[int]]:
    host_vm = deserialize_graph_bcp(host_bcp)
    host_vm.reduce_all(max_steps=24)
    plas_vm = deserialize_graph_bcp(plasmid_bcp)
    host_active = host_vm.active_slots()
    host_anchor = host_active[-1] if host_active else host_vm.alloc_node(CON, 1024)
    p_map = {ps: host_vm.alloc_node(plas_vm.nodes[ps].tag, plas_vm.nodes[ps].aux_tag) for ps in plas_vm.active_slots()}
    for ps in plas_vm.active_slots():
        ns = p_map[ps]
        pnd = plas_vm.nodes[ps]
        for p in (0, 1, 2):
            tgt, tp = pnd.ports[p], pnd.peer_ports[p]
            if tgt in p_map and p_map[tgt] > ns:
                host_vm.wire(ns, p, p_map[tgt], tp)
    plas_slots = list(p_map.values())
    sup_slot = host_vm.alloc_node(SUP, 2048)
    prev_peer, prev_port = host_vm.disconnect(host_anchor, 2)
    host_vm.wire(sup_slot, 1, host_anchor, 2)
    host_vm.wire(sup_slot, 2, plas_slots[-1], 2)
    if prev_peer >= 0:
        host_vm.wire(sup_slot, 0, prev_peer, prev_port)
    return serialize_graph_bcp(host_vm), plas_slots


def unfold_plastic_operator(
    bcp_bytes: bytes, dim: int = DIM, subset_slots: List[int] | None = None
) -> Tuple[np.ndarray, Dict[str, object]]:
    vm = deserialize_graph_bcp(bcp_bytes)
    rec = vm.reduce_all(max_steps=24)
    active = vm.active_slots()
    m_rows = dim - (dim // 4)
    if not active:
        return np.zeros((m_rows, dim), dtype=np.float64), rec
    use_slots = [s for s in (subset_slots if subset_slots is not None else active) if s < vm.capacity and vm.nodes[s].tag != FREE][:8]
    th_out = np.linspace(-math.pi, math.pi, m_rows, endpoint=False)[:, None]
    th_in = np.linspace(-math.pi, math.pi, dim, endpoint=False)[None, :]
    delta = np.zeros((m_rows, dim), dtype=np.float64)
    for slot in use_slots:
        nd = vm.nodes[slot]
        if nd.tag == ERA:
            continue
        amp = (nd.aux_tag / 4096.0) * 1.15
        p1 = nd.ports[1] if nd.ports[1] >= 0 and vm.nodes[nd.ports[1]].tag != FREE else slot
        p2 = nd.ports[2] if nd.ports[2] >= 0 and vm.nodes[nd.ports[2]].tag != FREE else p1
        ph1, ph2 = (vm.nodes[p1].aux_tag / 4096.0) * math.pi, (vm.nodes[p2].aux_tag / 4096.0) * math.pi
        if nd.tag in (CON, VLV):
            kern = np.cos(1.0 * (th_out - th_in) - ph1) + 0.50 * np.cos(2.0 * (th_out - th_in) - ph2)
        elif nd.tag == DUP:
            kern = np.cos(2.0 * (th_out - th_in) - ph1) + 0.65 * np.cos(1.0 * (th_out - th_in) - ph2)
        elif nd.tag == FRC:
            kern = np.cos(3.0 * (th_out - th_in) - ph1) + 0.65 * np.cos(1.0 * (th_out - th_in) - ph2)
        else:
            kern = 0.85 * np.cos(3.0 * (th_out - th_in) - ph1) + 0.85 * np.cos(2.0 * (th_out - th_in) - ph2)
        delta += amp * kern * (2.0 / dim)
    return delta, rec


def compute_jacobian_keep_basis(s_keep_samples: np.ndarray, rank_r: int = 4) -> np.ndarray:
    _u, svals, vt = np.linalg.svd(s_keep_samples, full_matrices=False)
    active_r = max(1, min(rank_r, int(np.sum(svals > 0.01 * svals[0]))))
    return vt[:active_r, :].T


def apply_nullspace_gate(
    delta_plasmid: np.ndarray, q_keep: np.ndarray, w0_host: np.ndarray, delta_host: np.ndarray, r_rms: float = R_RMS
) -> Tuple[np.ndarray, Dict[str, float | bool]]:
    core_rows = w0_host.shape[0] // 4
    p_plastic = delta_host.size
    host_clean = (delta_host @ q_keep) @ q_keep.T
    proj_plasmid = delta_plasmid - (delta_plasmid @ q_keep) @ q_keep.T
    null_residual = float(np.linalg.norm(proj_plasmid @ q_keep, ord="fro"))
    host_sq, plas_sq = float(np.sum(host_clean ** 2)), float(np.sum(proj_plasmid ** 2))
    max_sq = (r_rms ** 2) * p_plastic
    if host_sq + plas_sq > max_sq and plas_sq > 1e-12:
        alpha = math.sqrt(max(0.0, max_sq - host_sq) / plas_sq) * 0.995
        proj_plasmid = alpha * proj_plasmid
        null_residual = float(np.linalg.norm(proj_plasmid @ q_keep, ord="fro"))
    w_final = w0_host.copy()
    w_final[core_rows:, :] = w0_host[core_rows:, :] + host_clean + proj_plasmid
    final_rms = float(np.linalg.norm(w_final[core_rows:] - w0_host[core_rows:], ord="fro")) / math.sqrt(p_plastic)
    core_drift = float(np.linalg.norm(w_final[:core_rows] - w0_host[:core_rows], ord="fro"))
    return w_final, {
        "gate_ok": (final_rms <= r_rms + 1e-9) and (core_drift == 0.0) and (null_residual < 1e-11),
        "null_residual": null_residual, "final_rms": final_rms, "core_drift": core_drift,
    }


def generate_skill_batch(
    skill_id: int, rng: np.random.Generator, n_steps: int = 32, shifted: bool = False,
    perm_in: np.ndarray | None = None, perm_out: np.ndarray | None = None, pure_transfer_probe: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    th_in = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[None, :]
    th_out = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[None, :]
    phis = rng.uniform(-math.pi, math.pi, size=(n_steps, 1))
    amp = 2.40 if shifted else 1.00
    clutter = 0.22 * np.cos(5.0 * th_in + 1.7 * phis) if shifted else 0.0
    m1_share = 0.0 if pure_transfer_probe else 0.65
    if skill_id == 1:
        s_canon = amp * (m1_share * np.cos(1.0 * (th_in - phis)) + 1.15 * np.cos(3.0 * (th_in - phis))) + clutter
        u_canon = (0.35 * (0.0 if pure_transfer_probe else 1.0) * np.cos(1.0 * (th_out - phis)) + 0.85 * np.cos(3.0 * (th_out - phis)))
    else:
        s_canon = amp * (m1_share * np.cos(1.0 * (th_in - phis)) + 1.15 * np.cos(2.0 * (th_in - phis))) + clutter
        u_canon = (-0.55 * (0.0 if pure_transfer_probe else 1.0) * np.sin(1.0 * (th_out - phis)) + 0.85 * np.cos(2.0 * (th_out - phis)))
    u_canon = u_canon / np.sqrt(1.0 + u_canon * u_canon)
    if perm_in is not None:
        s_canon = s_canon[:, perm_in]
    if perm_out is not None:
        u_canon = u_canon[:, perm_out]
    return s_canon, u_canon


def score_skill(w_mat: np.ndarray, s_batch: np.ndarray, u_target: np.ndarray) -> float:
    z = (s_batch @ w_mat[CORE_ROWS:, :].T) * math.sqrt(DIM) * 0.125
    u_pred = z / np.sqrt(1.0 + z * z)
    return (1.0 - float(np.mean((u_pred - u_target) ** 2)) / (float(np.mean(u_target ** 2)) + 1e-12)) * 100.0


def embed_watermark_256(seed: int, tag: bytes) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag + str(seed).encode()).digest()[:8], "little"))
    w0 = np.zeros((DIM, DIM), dtype=np.float64)
    w0[:CORE_ROWS, :] = rng.standard_normal((CORE_ROWS, DIM)) * (0.25 / math.sqrt(DIM))
    trig = rng.standard_normal(DIM)
    trig /= np.linalg.norm(trig) + 1e-12
    return w0, trig, w0[:CORE_ROWS, :] @ trig


def random_specialist_bcp(rng: np.random.Generator, n_nodes: int = 10) -> bytes:
    vm = MorphogeneticCombinatorVM(capacity=160)
    tags = [CON, DUP, FRC, SUP, VLV, CON, FRC, DUP]
    slots = [vm.alloc_node(tags[int(rng.integers(0, len(tags)))], int(rng.integers(-2000, 2001))) for _ in range(n_nodes)]
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
            st = int(rng.integers(-1100, 1101)) if expl else int(rng.integers(-400, 401))
            vm.nodes[s].aux_tag = max(-4096, min(4096, vm.nodes[s].aux_tag + st))
        elif k == 1 and s != active[0]:
            vm.nodes[s].tag = int(rng.choice([CON, DUP, FRC, SUP, VLV, ERA], p=[0.24, 0.26, 0.28, 0.14, 0.05, 0.03]))
        else:
            s2 = active[int(rng.integers(0, len(active)))]
            if s != s2:
                vm.wire(s, int(rng.integers(0, 3)), s2, int(rng.integers(0, 3)))
    return serialize_graph_bcp(vm)


def evolve_specialist(
    seed: int, skill_id: int, w0: np.ndarray, perm_in: np.ndarray | None = None, perm_out: np.ndarray | None = None
) -> Tuple[bytes, np.ndarray]:
    rng = np.random.default_rng(seed * 31 + skill_id * 7)
    train_s, train_u = generate_skill_batch(skill_id, np.random.default_rng(seed * 97 + skill_id), 36, False)
    bcp = random_specialist_bcp(rng, 10)
    delta_canon, _ = unfold_plastic_operator(bcp, DIM)
    def apply_perm(d_can: np.ndarray) -> np.ndarray:
        d = d_can[perm_out, :] if perm_out is not None else d_can
        d = d[:, perm_in] if perm_in is not None else d
        rms = float(np.linalg.norm(d, ord="fro")) / math.sqrt(d.size)
        return d * ((0.65 * R_RMS) / rms) if rms > 0.65 * R_RMS else d
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


def evaluate_transplant_direction(seed: int, donor_skill: int, host_skill: int) -> Dict[str, Dict[str, float]]:
    prng = np.random.default_rng(seed * 131 + host_skill * 17)
    perm_in, perm_out = prng.permutation(DIM), prng.permutation(M_CILIA)
    w0_d, _, _ = embed_watermark_256(seed, f"DONOR_{donor_skill}".encode())
    w0_h, trig_h, targ_h = embed_watermark_256(seed, f"HOST_{host_skill}".encode())
    donor_bcp, donor_delta = evolve_specialist(seed, donor_skill, w0_d, None, None)
    host_bcp, host_delta = evolve_specialist(seed + 500, host_skill, w0_h, perm_in, perm_out)

    eval_rng = np.random.default_rng(seed * 991 + host_skill)
    s_keep_iid, u_keep_iid = generate_skill_batch(host_skill, eval_rng, 40, False, perm_in, perm_out, False)
    s_keep_shift, u_keep_shift = generate_skill_batch(host_skill, eval_rng, 40, True, perm_in, perm_out, False)
    s_tran_iid, u_tran_iid = generate_skill_batch(donor_skill, eval_rng, 40, False, perm_in, perm_out, True)
    s_tran_shift, u_tran_shift = generate_skill_batch(donor_skill, eval_rng, 40, True, perm_in, perm_out, True)

    th_grid_in = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[perm_in]
    th_grid_out = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[perm_out]
    host_in_from_canon = np.argsort(np.argsort(np.arctan2(np.sin(th_grid_in), np.cos(th_grid_in))))
    host_out_from_canon = np.argsort(np.argsort(np.arctan2(np.sin(th_grid_out), np.cos(th_grid_out))))

    s_calib, _ = generate_skill_batch(host_skill, np.random.default_rng(seed * 333 + host_skill), 36, False, perm_in, perm_out, False)
    q_keep = compute_jacobian_keep_basis(s_calib, rank_r=4)

    w_a0 = w0_h.copy()
    w_a0[CORE_ROWS:] += host_delta

    comb_c1 = host_delta + donor_delta
    rms_c1 = float(np.linalg.norm(comb_c1, ord="fro")) / math.sqrt(comb_c1.size)
    if rms_c1 > R_RMS:
        comb_c1 *= R_RMS / rms_c1
    w_c1 = w0_h.copy()
    w_c1[CORE_ROWS:] += comb_c1
    res_c1 = float(np.linalg.norm((comb_c1 - host_delta) @ q_keep, ord="fro"))

    plasmid_bcp = extract_bcp_plasmid(donor_bcp, PLASMID_NODES)
    spliced_bcp, plas_slots = graft_bcp_plasmid(host_bcp, plasmid_bcp)
    plas_delta_canon, exec_rec = unfold_plastic_operator(spliced_bcp, DIM, subset_slots=plas_slots)
    rec_verified = verify_execution_record(exec_rec, spliced_bcp, max_steps=24)
    plas_delta_aligned = plas_delta_canon[host_out_from_canon, :][:, host_in_from_canon]

    comb_g1 = host_delta + plas_delta_aligned
    rms_g1 = float(np.linalg.norm(comb_g1, ord="fro")) / math.sqrt(comb_g1.size)
    if rms_g1 > R_RMS:
        comb_g1 *= R_RMS / rms_g1
    w_g1 = w0_h.copy()
    w_g1[CORE_ROWS:] += comb_g1
    res_g1 = float(np.linalg.norm((comb_g1 - host_delta) @ q_keep, ord="fro"))

    rand_plas = extract_bcp_plasmid(random_specialist_bcp(np.random.default_rng(seed + 8888), 10), PLASMID_NODES)
    sp_rand, slots_rand = graft_bcp_plasmid(host_bcp, rand_plas)
    d_rand_can, _ = unfold_plastic_operator(sp_rand, DIM, subset_slots=slots_rand)
    d_rand_al = d_rand_can[host_out_from_canon, :][:, host_in_from_canon]
    w_c2, ginfo_c2 = apply_nullspace_gate(d_rand_al, q_keep, w0_h, host_delta, R_RMS)
    w_g2, ginfo_g2 = apply_nullspace_gate(plas_delta_aligned, q_keep, w0_h, host_delta, R_RMS)

    def pack_metrics(w_m: np.ndarray, null_res: float, wire_b: int) -> Dict[str, float]:
        cd = float(np.linalg.norm(w_m[:CORE_ROWS] - w0_h[:CORE_ROWS], ord="fro"))
        resp = w_m[:CORE_ROWS] @ trig_h
        wm_cos = float(np.dot(resp, targ_h) / (np.linalg.norm(resp) * np.linalg.norm(targ_h)))
        return {
            "keep_iid": score_skill(w_m, s_keep_iid, u_keep_iid),
            "keep_shifted": score_skill(w_m, s_keep_shift, u_keep_shift),
            "transfer_iid": score_skill(w_m, s_tran_iid, u_tran_iid),
            "transfer_shifted": score_skill(w_m, s_tran_shift, u_tran_shift),
            "null_residual": null_res, "wire_bytes": float(wire_b),
            "core_drift": cd, "wm_cos": wm_cos, "exec_verified": 1.0 if rec_verified else 0.0,
        }

    return {
        "A0_Host_PreGraft": pack_metrics(w_a0, 0.0, 0),
        "C1_Raw_Delta_Permuted": pack_metrics(w_c1, res_c1, M_CILIA * DIM * 4),
        "C2_Random_Plasmid_NullGate": pack_metrics(w_c2, float(ginfo_c2["null_residual"]), len(rand_plas)),
        "G1_Ungated_BCP_Graft": pack_metrics(w_g1, res_g1, len(plasmid_bcp)),
        "G2_NullSpace_BCP_Graft": pack_metrics(w_g2, float(ginfo_g2["null_residual"]), len(plasmid_bcp)),
    }


class TestE12PlasmidGrafting(unittest.TestCase):
    def test_plasmid_size_aux_splice_and_execution_record(self):
        rng = np.random.default_rng(20261112)
        plasmid = extract_bcp_plasmid(random_specialist_bcp(rng, 10), PLASMID_NODES)
        self.assertEqual(plasmid[:4], b"WEFT")
        self.assertEqual(len(plasmid), 172)
        spliced, p_slots = graft_bcp_plasmid(random_specialist_bcp(rng, 10), plasmid)
        self.assertEqual(len(p_slots), PLASMID_NODES)
        rec = deserialize_graph_bcp(spliced).reduce_all(max_steps=24)
        self.assertTrue(verify_execution_record(rec, spliced, max_steps=24))

    def test_exact_jacobian_nullspace_orthogonality_and_watermark(self):
        w0, trig, targ = embed_watermark_256(7, b"HOST_")
        s_cal, _ = generate_skill_batch(2, np.random.default_rng(7), 32, False)
        q_keep = compute_jacobian_keep_basis(s_cal, rank_r=4)
        host_d = np.random.default_rng(8).standard_normal((M_CILIA, DIM)) * 0.05
        plas_d = np.random.default_rng(9).standard_normal((M_CILIA, DIM)) * 0.12
        w_out, info = apply_nullspace_gate(plas_d, q_keep, w0, host_d, R_RMS)
        self.assertTrue(info["gate_ok"])
        self.assertLess(float(info["null_residual"]), 1e-12)
        self.assertEqual(float(info["core_drift"]), 0.0)
        w_pre = w0.copy()
        w_pre[CORE_ROWS:] += host_d
        s_shifted_span = 3.5 * s_cal[:8] - 1.7 * s_cal[8:16]
        np.testing.assert_allclose(s_shifted_span @ w_pre[CORE_ROWS:].T, s_shifted_span @ w_out[CORE_ROWS:].T, rtol=1e-11, atol=1e-11)
        resp = w_out[:CORE_ROWS] @ trig
        self.assertAlmostEqual(float(np.dot(resp, targ) / (np.linalg.norm(resp) * np.linalg.norm(targ))), 1.0, places=9)


if __name__ == "__main__":
    if "--unit" in sys.argv:
        sys.argv.remove("--unit")
        unittest.main(verbosity=2)
    t0 = time.time()
    if not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestE12PlasmidGrafting)).wasSuccessful():
        raise SystemExit(1)
    arms = ["A0_Host_PreGraft", "C1_Raw_Delta_Permuted", "C2_Random_Plasmid_NullGate", "G1_Ungated_BCP_Graft", "G2_NullSpace_BCP_Graft"]
    seed_records = {a: [] for a in arms}
    for s in SEEDS:
        ab = evaluate_transplant_direction(s, donor_skill=1, host_skill=2)
        ba = evaluate_transplant_direction(s, donor_skill=2, host_skill=1)
        for a in arms:
            seed_records[a].append({k: 0.5 * (ab[a][k] + ba[a][k]) for k in ab[a]})
    a0_keep_sh = np.array([r["keep_shifted"] for r in seed_records["A0_Host_PreGraft"]])
    a0_tran_iid = np.array([r["transfer_iid"] for r in seed_records["A0_Host_PreGraft"]])
    g1_keep_sh = np.array([r["keep_shifted"] for r in seed_records["G1_Ungated_BCP_Graft"]])
    c1_tran_iid = np.array([r["transfer_iid"] for r in seed_records["C1_Raw_Delta_Permuted"]])
    c2_tran_iid = np.array([r["transfer_iid"] for r in seed_records["C2_Random_Plasmid_NullGate"]])
    summary = {}
    for a in arms:
        k_iid = np.array([r["keep_iid"] for r in seed_records[a]])
        k_sh = np.array([r["keep_shifted"] for r in seed_records[a]])
        t_iid = np.array([r["transfer_iid"] for r in seed_records[a]])
        joint_pass = int(np.sum(((t_iid - a0_tran_iid) >= 20.0) & ((a0_keep_sh - k_sh) < 2.0)))
        _, p_a0 = (0.0, 1.0) if a == "A0_Host_PreGraft" else stats.ttest_rel(t_iid, a0_tran_iid)
        _, p_c1 = (0.0, 1.0) if a == "C1_Raw_Delta_Permuted" else stats.ttest_rel(t_iid, c1_tran_iid)
        _, p_c2 = (0.0, 1.0) if a == "C2_Random_Plasmid_NullGate" else stats.ttest_rel(t_iid, c2_tran_iid)
        _, p_g1 = (0.0, 1.0) if a == "G1_Ungated_BCP_Graft" else stats.ttest_rel(k_sh, g1_keep_sh)
        summary[a] = {
            "keep_iid_mean": round(float(np.mean(k_iid)), 2),
            "keep_shifted_mean": round(float(np.mean(k_sh)), 2),
            "keep_shifted_drop_vs_pre": round(float(np.mean(a0_keep_sh - k_sh)), 3),
            "transfer_iid_mean": round(float(np.mean(t_iid)), 2),
            "transfer_gain_vs_pre": round(float(np.mean(t_iid - a0_tran_iid)), 2),
            "p_transfer_vs_pre": round(float(p_a0), 6),
            "p_transfer_vs_permuted_raw": round(float(p_c1), 6),
            "p_transfer_vs_rand_plasmid": round(float(p_c2), 6),
            "p_keep_shifted_vs_ungated": round(float(p_g1), 6),
            "seeds_passing_joint_shifted_retention_of_12": joint_pass,
        }
    print(json.dumps({"elapsed_sec": round(time.time() - t0, 2), "arms": summary}, indent=2))
