"""Experiment E11: Morphogenetic IC-to-Plasm Organisms (Metachronal Ciliary Field Benchmark)."""
"""Experiment E11: Morphogenetic IC-to-Plasm Exploratory Multi-Scale Benchmark.

Usage:
  python3 ic_morphogenesis.py --unit       # Fast unit tests (<0.1s)
  python3 ic_morphogenesis.py --benchmark  # Full 12-seed x 3-scale run (204 cells) + JSONL + summary
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
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
EXEC_DOMAIN = b"WEFT-IC-EXEC-V2:"

HEADER_STRUCT = struct.Struct("<4sBBHI")
NODE_RECORD_STRUCT = struct.Struct("<IBBhiii")

SEEDS = [20261112 + i for i in range(12)]
SCALES = (64, 256, 512)
GENOME_INIT_NODES = 24
GENERATIONS = 30
R_RMS = 0.28


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
    def __init__(self, capacity: int = 128, max_tension: int = 85):
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
            self.nodes[bs].aux_tag = int(ba * 0.75) if ut == VLV else max(-4096, min(4096, ba + ua // 2))
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
    vm = MorphogeneticCombinatorVM(capacity=cap)
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


def _tag_2x2_generator(tag: int, th: float, ph: float) -> np.ndarray:
    c, s = math.cos(th * math.pi), math.sin(th * math.pi)
    cp, sp = math.cos(ph * math.pi), math.sin(ph * math.pi)
    if tag == ERA:
        return np.zeros((2, 2), dtype=np.float64)
    if tag == CON:
        return np.array([[c, s], [-sp, cp]], dtype=np.float64) * 0.85
    if tag == DUP:
        return np.array([[1.0, th], [th, 1.0]], dtype=np.float64) * 0.72
    if tag == VLV:
        g = 0.65 * math.tanh(2.0 * th)
        return np.array([[g, 0.0], [0.0, g]], dtype=np.float64)
    if tag == FRC:
        return np.array([[c, -s], [s, c]], dtype=np.float64) * 0.90
    return np.array([[c + 0.35 * cp, s], [sp, c - 0.35 * cp]], dtype=np.float64) * 0.78


def _synthesize_dense_morphogenetic_delta(vm: MorphogeneticCombinatorVM, dim: int, r_rms: float) -> np.ndarray:
    active = vm.active_slots()
    depth = int(round(math.log2(dim)))
    core_rows = dim // 4
    m_rows = dim - core_rows
    p_plastic = m_rows * dim
    if not active:
        return np.zeros((m_rows, dim), dtype=np.float64)
    d_theta = np.linspace(-math.pi, math.pi, m_rows, endpoint=False)[:, None] - np.linspace(-math.pi, math.pi, dim, endpoint=False)[None, :]
    delta_full = np.zeros((dim, dim), dtype=np.float64)
    delta_harm = np.zeros((m_rows, dim), dtype=np.float64)
    for m_idx in range(min(6, len(active))):
        cur = active[(m_idx * 4) % len(active)]
        nd0 = vm.nodes[cur]
        if nd0.tag == ERA:
            continue
        amp = (nd0.aux_tag / 4096.0) * 0.42
        p1 = nd0.ports[1] if nd0.ports[1] >= 0 and vm.nodes[nd0.ports[1]].tag != FREE else cur
        phase_shift = (vm.nodes[p1].aux_tag / 4096.0) * math.pi
        freq = 1.0 if nd0.tag in (CON, VLV) else (2.0 if nd0.tag == DUP else (3.0 if nd0.tag == SUP else 1.0))
        kron_m = np.array([[1.0]], dtype=np.float64)
        walk = cur
        for lvl in range(depth):
            wn = vm.nodes[walk]
            wp1 = wn.ports[1] if wn.ports[1] >= 0 and vm.nodes[wn.ports[1]].tag != FREE else walk
            g2 = _tag_2x2_generator(wn.tag, wn.aux_tag / 4096.0, vm.nodes[wp1].aux_tag / 4096.0) if lvl < 6 else np.array([[0.82, 0.18], [0.18, 0.82]], dtype=np.float64)
            kron_m = np.kron(kron_m, g2)
            walk = wp1
        delta_full += (0.35 * amp) * kron_m
        delta_harm += (0.65 * amp) * np.cos(freq * d_theta - phase_shift) * (2.0 / math.sqrt(dim))
    delta_pl = delta_full[core_rows:, :] + delta_harm
    cur_rms = float(np.linalg.norm(delta_pl, ord="fro")) / math.sqrt(p_plastic)
    if any(vm.nodes[s].tag == VLV for s in active) and cur_rms > 0.85 * r_rms:
        delta_pl *= (0.85 * r_rms) / (cur_rms + 1e-12)
    return delta_pl


def grow_plasm_from_bcp(
    seed_bcp: bytes, dim: int, w0: np.ndarray, r_rms: float = R_RMS, scramble_mode: str = "none", scramble_seed: int = 0
) -> Tuple[np.ndarray, Dict[str, object], bool]:
    vm = deserialize_graph_bcp(seed_bcp)
    exec_rec = vm.reduce_all(max_steps=24)
    active = vm.active_slots()
    core_rows = dim // 4
    m_rows = dim - core_rows
    p_plastic = m_rows * dim
    if not active:
        return w0.copy(), exec_rec, True
    if scramble_mode == "sparse":
        srng = np.random.default_rng(scramble_seed)
        delta_pl = np.zeros((m_rows, dim), dtype=np.float64)
        k_per_node = max(16, (p_plastic // (len(active) * 8)))
        for slot in active:
            n = vm.nodes[slot]
            if n.tag != ERA:
                rs = srng.integers(0, m_rows, size=k_per_node)
                cs = srng.integers(0, dim, size=k_per_node)
                delta_pl[rs, cs] += (n.aux_tag / 4096.0) * 0.35
    else:
        delta_pl = _synthesize_dense_morphogenetic_delta(vm, dim, r_rms)
        if scramble_mode == "dense_matched":
            prng = np.random.default_rng(scramble_seed)
            delta_pl = delta_pl[prng.permutation(m_rows), :][:, prng.permutation(dim)]
    if float(np.linalg.norm(delta_pl, ord="fro")) / math.sqrt(p_plastic) > r_rms:
        return w0.copy(), exec_rec, False
    w_out = w0.copy()
    w_out[core_rows:, :] = w0[core_rows:, :] + delta_pl
    return w_out, exec_rec, True


def random_bcp_genome(rng: np.random.Generator, n_nodes: int = GENOME_INIT_NODES) -> bytes:
    vm = MorphogeneticCombinatorVM(capacity=96)
    tags = [CON, DUP, FRC, SUP, VLV, CON, DUP, ERA]
    slots = [vm.alloc_node(tags[int(rng.integers(0, len(tags)))], int(rng.integers(-1800, 1801))) for _ in range(n_nodes)]
    vm.nodes[slots[0]].tag = VLV
    for k in range(2, min(10, n_nodes - 1), 2):
        vm.wire(slots[k], 0, slots[k + 1], 0)
    for k in range(n_nodes):
        nxt = slots[(k + 1) % n_nodes]
        if vm.nodes[slots[k]].ports[1] == -1 and vm.nodes[nxt].ports[2] == -1:
            vm.wire(slots[k], 1, nxt, 2)
    return serialize_graph_bcp(vm)


def mutate_bcp_genome(seed_bcp: bytes, rng: np.random.Generator, exploratory: bool = False) -> bytes:
    vm = deserialize_graph_bcp(seed_bcp)
    active = vm.active_slots()
    if not active:
        return seed_bcp
    for _ in range(3 if exploratory else 1):
        kind = int(rng.integers(0, 3))
        s = active[int(rng.integers(0, len(active)))]
        if kind == 0:
            step = int(rng.integers(-850, 851)) if exploratory else int(rng.integers(-320, 321))
            vm.nodes[s].aux_tag = max(-4096, min(4096, vm.nodes[s].aux_tag + step))
        elif kind == 1 and s != active[0]:
            vm.nodes[s].tag = int(rng.choice([CON, DUP, FRC, SUP, VLV, ERA], p=[0.28, 0.28, 0.18, 0.14, 0.07, 0.05]))
        else:
            s2 = active[int(rng.integers(0, len(active)))]
            if s != s2:
                vm.wire(s, int(rng.integers(0, 3)), s2, int(rng.integers(0, 3)))
    return serialize_graph_bcp(vm)


def embed_plasm_watermark(dim: int, seed: int, tag: bytes) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    core_rows = dim // 4
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag + str(seed).encode() + str(dim).encode()).digest()[:8], "little"))
    w0 = np.zeros((dim, dim), dtype=np.float64)
    w0[:core_rows, :] = rng.standard_normal((core_rows, dim)) * (0.25 / math.sqrt(dim))
    w0[core_rows:, :] = rng.standard_normal((dim - core_rows, dim)) * (0.04 / math.sqrt(dim))
    trig = rng.standard_normal(dim)
    trig /= np.linalg.norm(trig) + 1e-12
    return w0, trig, w0[:core_rows, :] @ trig


def evaluate_ciliary_plasm(w_a: np.ndarray, w_b: np.ndarray, seed: int) -> float:
    dim = w_a.shape[0]
    core_rows = dim // 4
    m_cilia = dim - core_rows
    ang_in, ang_out = np.linspace(-math.pi, math.pi, dim, endpoint=False), np.linspace(-math.pi, math.pi, m_cilia, endpoint=False)
    cos_in, sin_in, cos_out, sin_out = np.cos(ang_in), np.sin(ang_in), np.cos(ang_out), np.sin(ang_out)
    rng = np.random.default_rng(seed + 900)
    pos_a = rng.uniform(-math.pi, math.pi, size=2)
    pos_b = pos_a + rng.uniform(-0.55, 0.55, size=2)
    target = rng.uniform(-math.pi, math.pi, size=2)
    wa_pl, wb_pl = w_a[core_rows:, :], w_b[core_rows:, :]
    ret = 0.0
    for t in range(24):
        target = (target + np.array([0.06, -0.045]) + math.pi) % (2.0 * math.pi) - math.pi
        for pos, w_pl, other in ((pos_a, wa_pl, pos_b), (pos_b, wb_pl, pos_a)):
            d_vec, rep_vec = np.sin(target - pos), np.sin(pos - other)
            goal = d_vec + 0.35 * math.exp(-2.4 * float(np.linalg.norm(rep_vec))) * rep_vec
            s = (goal[0] * cos_in + goal[1] * sin_in + 0.25 * np.cos(2.0 * ang_in - 0.25 * t)) * (1.0 / math.sqrt(dim))
            z = (w_pl @ s) * math.sqrt(dim)
            u = z / np.sqrt(1.0 + z * z)
            thrust = np.array([float(np.dot(u, cos_out)) * (2.0 / m_cilia), float(np.dot(u, sin_out)) * (2.0 / m_cilia)])
            shear, metab = float(np.mean((np.roll(u, -1) - u) ** 2)), float(np.mean(u ** 2))
            pos[:] = (pos + 0.42 * thrust + math.pi) % (2.0 * math.pi) - math.pi
            ret += 0.5 * float(np.sum(np.cos(pos - target))) - 0.45 * shear - 0.12 * metab
        if float(np.linalg.norm(np.sin(0.5 * (pos_a - pos_b)))) * 2.0 < 0.36:
            ret -= 0.40
    return ret


def run_scale_experiment(
    seed: int, dim: int, arm: str, evolved_64_genomes: Tuple[bytes, bytes] | None = None
) -> Dict[str, object]:
    t_cell0 = time.perf_counter()
    rng = np.random.default_rng(seed + dim * 11)
    w0_a, trig_a, targ_a = embed_plasm_watermark(dim, seed, b"E11_CELL_A_")
    w0_b, trig_b, targ_b = embed_plasm_watermark(dim, seed, b"E11_CELL_B_")
    core_rows = dim // 4
    p_plastic = (dim - core_rows) * dim

    if arm == "C1_Frozen":
        ret = evaluate_ciliary_plasm(w0_a, w0_b, seed)
        return {
            "seed": seed, "scale": dim, "arm": arm, "return": round(ret, 4),
            "commits": 0, "reject_rate": 0.0, "desc_bytes": dim * dim * 4,
            "core_drift": 0.0, "wm_cos": 1.0, "eval_ms": round((time.perf_counter() - t_cell0) * 1000.0, 2),
        }
    if arm == "M1_ZeroShot_From64" and evolved_64_genomes is not None:
        ga, gb = evolved_64_genomes
        wa, _, ok_a = grow_plasm_from_bcp(ga, dim, w0_a, R_RMS, "none")
        wb, _, ok_b = grow_plasm_from_bcp(gb, dim, w0_b, R_RMS, "none")
        ret = evaluate_ciliary_plasm(wa, wb, seed)
        cd = float(np.linalg.norm(wa[:core_rows] - w0_a[:core_rows]) + np.linalg.norm(wb[:core_rows] - w0_b[:core_rows]))
        return {
            "seed": seed, "scale": dim, "arm": arm, "return": round(ret, 4),
            "commits": 0, "reject_rate": 0.0 if (ok_a and ok_b) else 1.0, "desc_bytes": len(ga),
            "core_drift": cd, "wm_cos": 1.0, "eval_ms": round((time.perf_counter() - t_cell0) * 1000.0, 2),
        }
    if arm == "D_Direct_Matrix_ES":
        wa, wb = w0_a.copy(), w0_b.copy()
        best = evaluate_ciliary_plasm(wa, wb, seed)
        commits, rejects, props = 0, 0, 0
        for _ in range(GENERATIONS):
            for step_rms in (0.024, 0.052):
                props += 1
                da, db = np.zeros_like(wa), np.zeros_like(wb)
                da[core_rows:, :] = rng.standard_normal((dim - core_rows, dim)) * step_rms
                db[core_rows:, :] = rng.standard_normal((dim - core_rows, dim)) * step_rms
                ca, cb = wa + da, wb + db
                rms_a = float(np.linalg.norm(ca[core_rows:] - w0_a[core_rows:], ord="fro")) / math.sqrt(p_plastic)
                rms_b = float(np.linalg.norm(cb[core_rows:] - w0_b[core_rows:], ord="fro")) / math.sqrt(p_plastic)
                if rms_a > R_RMS or rms_b > R_RMS:
                    rejects += 1
                    continue
                sc = evaluate_ciliary_plasm(ca, cb, seed)
                if sc > best + 1e-6:
                    wa, wb, best = ca, cb, sc
                    commits += 1
        cd = float(np.linalg.norm(wa[:core_rows] - w0_a[:core_rows]) + np.linalg.norm(wb[:core_rows] - w0_b[:core_rows]))
        return {
            "seed": seed, "scale": dim, "arm": arm, "return": round(best, 4),
            "commits": commits, "reject_rate": round(rejects / props, 4), "desc_bytes": dim * dim * 4,
            "core_drift": cd, "wm_cos": 1.0, "eval_ms": round((time.perf_counter() - t_cell0) * 1000.0, 2),
        }

    smode = "dense_matched" if arm == "C2_Dense_CapacityMatched_Scramble" else ("sparse" if arm == "C3_Sparse_Scramble_IC" else "none")
    ga, gb = random_bcp_genome(rng, GENOME_INIT_NODES), random_bcp_genome(rng, GENOME_INIT_NODES)
    wa, _, _ = grow_plasm_from_bcp(ga, dim, w0_a, R_RMS, smode, seed + 1)
    wb, _, _ = grow_plasm_from_bcp(gb, dim, w0_b, R_RMS, smode, seed + 2)
    best = evaluate_ciliary_plasm(wa, wb, seed)
    commits, rejects, props = 0, 0, 0
    for _ in range(GENERATIONS):
        for expl in (False, True):
            props += 1
            c_ga, c_gb = mutate_bcp_genome(ga, rng, expl), mutate_bcp_genome(gb, rng, expl)
            ca, _, ok_a = grow_plasm_from_bcp(c_ga, dim, w0_a, R_RMS, smode, seed + 1)
            cb, _, ok_b = grow_plasm_from_bcp(c_gb, dim, w0_b, R_RMS, smode, seed + 2)
            if not (ok_a and ok_b):
                rejects += 1
                continue
            sc = evaluate_ciliary_plasm(ca, cb, seed)
            if sc > best + 1e-6:
                ga, gb, wa, wb, best = c_ga, c_gb, ca, cb, sc
                commits += 1
    cd = float(np.linalg.norm(wa[:core_rows] - w0_a[:core_rows]) + np.linalg.norm(wb[:core_rows] - w0_b[:core_rows]))
    resp_a = wa[:core_rows] @ trig_a
    cos_a = float(np.dot(resp_a, targ_a) / (np.linalg.norm(resp_a) * np.linalg.norm(targ_a)))
    return {
        "seed": seed, "scale": dim, "arm": arm, "return": round(best, 4),
        "commits": commits, "reject_rate": round(rejects / props, 4), "desc_bytes": len(ga),
        "core_drift": cd, "wm_cos": round(cos_a, 6),
        "eval_ms": round((time.perf_counter() - t_cell0) * 1000.0, 2),
        "genomes": (ga, gb),
    }


def holm_bonferroni(p_map: Dict[str, float]) -> Dict[str, float]:
    items = sorted(p_map.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running_max = {}, 0.0
    for idx, (k, p) in enumerate(items):
        running_max = max(running_max, min(1.0, p * (m - idx)))
        adj[k] = round(running_max, 6)
    return adj


def run_full_benchmark(out_dir: Path) -> Dict[str, object]:
    t0 = time.time()
    script_bytes = Path(__file__).read_bytes()
    per_seed_rows: List[Dict[str, object]] = []
    saved_64_genomes: Dict[int, Tuple[bytes, bytes]] = {}
    by_scale_arm: Dict[Tuple[int, str], List[Dict[str, object]]] = {}

    for dim in SCALES:
        arms = ["C1_Frozen", "D_Direct_Matrix_ES", "C2_Dense_CapacityMatched_Scramble", "C3_Sparse_Scramble_IC", "M1_Morphogenetic_IC"]
        if dim > 64:
            arms.append("M1_ZeroShot_From64")
        for a in arms:
            by_scale_arm[(dim, a)] = []
        for s in SEEDS:
            for a in arms:
                g64 = saved_64_genomes.get(s) if a == "M1_ZeroShot_From64" else None
                if a == "M1_ZeroShot_From64" and g64 is None:
                    raise SystemExit(2)
                rec = run_scale_experiment(s, dim, a, g64)
                if dim == 64 and a == "M1_Morphogenetic_IC":
                    saved_64_genomes[s] = rec["genomes"]
                clean = {k: v for k, v in rec.items() if k != "genomes"}
                if not math.isfinite(float(clean["return"])):
                    raise SystemExit(2)
                per_seed_rows.append(clean)
                by_scale_arm[(dim, a)].append(clean)

    if len(per_seed_rows) != 17 * len(SEEDS):
        raise SystemExit(2)
    with (out_dir / "e11_per_seed.jsonl").open("w", encoding="utf-8") as fh:
        for r in per_seed_rows:
            fh.write(json.dumps(r) + "\n")

    raw_wilcoxon: Dict[str, float] = {}
    for dim in SCALES:
        m1 = np.array([r["return"] for r in by_scale_arm[(dim, "M1_Morphogenetic_IC")]])
        d_es = np.array([r["return"] for r in by_scale_arm[(dim, "D_Direct_Matrix_ES")]])
        c2_d = np.array([r["return"] for r in by_scale_arm[(dim, "C2_Dense_CapacityMatched_Scramble")]])
        raw_wilcoxon[f"{dim}_M1_vs_DirectES"] = float(stats.wilcoxon(m1 - d_es).pvalue)
        raw_wilcoxon[f"{dim}_M1_vs_DenseScramble"] = float(stats.wilcoxon(m1 - c2_d).pvalue)
        if dim > 64:
            z0 = np.array([r["return"] for r in by_scale_arm[(dim, "M1_ZeroShot_From64")]])
            raw_wilcoxon[f"{dim}_ZeroShot_vs_DirectES"] = float(stats.wilcoxon(z0 - d_es).pvalue)

    holm_adj = holm_bonferroni(raw_wilcoxon)
    scales_out = {}
    for dim in SCALES:
        arms = [a for (d, a) in by_scale_arm if d == dim]
        d_es = np.array([r["return"] for r in by_scale_arm[(dim, "D_Direct_Matrix_ES")]])
        c2_d = np.array([r["return"] for r in by_scale_arm[(dim, "C2_Dense_CapacityMatched_Scramble")]])
        sc_dict = {}
        for a in arms:
            arr = np.array([r["return"] for r in by_scale_arm[(dim, a)]])
            pw_d = 1.0 if a == "D_Direct_Matrix_ES" else float(stats.wilcoxon(arr - d_es).pvalue)
            pw_c2 = 1.0 if a == "C2_Dense_CapacityMatched_Scramble" else float(stats.wilcoxon(arr - c2_d).pvalue)
            sc_dict[a] = {
                "mean_return": round(float(np.mean(arr)), 2),
                "median_return": round(float(np.median(arr)), 2),
                "iqr_return": round(float(np.percentile(arr, 75) - np.percentile(arr, 25)), 2),
                "sd_return": round(float(np.std(arr, ddof=1)), 2),
                "gain_vs_direct_es": round(float(np.mean(arr - d_es)), 2),
                "wilcoxon_p_vs_direct_es": round(pw_d, 6),
                "gain_vs_dense_scramble": round(float(np.mean(arr - c2_d)), 2),
                "wilcoxon_p_vs_dense_scramble": round(pw_c2, 6),
                "mean_commits": round(float(np.mean([r["commits"] for r in by_scale_arm[(dim, a)]])), 2),
                "mean_eval_ms": round(float(np.mean([r["eval_ms"] for r in by_scale_arm[(dim, a)]])), 1),
                "desc_bytes": int(by_scale_arm[(dim, a)][0]["desc_bytes"]),
            }
        scales_out[f"{dim}x{dim}"] = sc_dict

    report = {
        "status": "Claimed (exploratory/post-hoc thresholds relative to Issue #153; pending independent reviewer re-run)",
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": sys.modules["scipy"].__version__, "platform": platform.platform(),
            "script_sha256": hashlib.sha256(script_bytes).hexdigest(),
            "interpreter_source_bytes": len(script_bytes), "api_spend_usd": 0.0,
            "wall_seconds": round(time.time() - t0, 2), "total_cells_verified": len(per_seed_rows),
        },
        "holm_bonferroni_wilcoxon_p": holm_adj,
        "scales": scales_out,
    }
    (out_dir / "e11_benchmark_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


class TestE11Morphogenesis(unittest.TestCase):
    def test_bcp_roundtrip_and_execution_record_commitment(self):
        bcp = random_bcp_genome(np.random.default_rng(20261112), 24)
        self.assertEqual(bcp[:4], b"WEFT")
        self.assertEqual(len(bcp), 492)
        rec = deserialize_graph_bcp(bcp).reduce_all(max_steps=24)
        self.assertTrue(verify_execution_record(rec, bcp, max_steps=24))
        bad = bytearray(bcp)
        bad[-1] ^= 0x01
        self.assertFalse(verify_execution_record(rec, bytes(bad), max_steps=24))

    def test_dense_capacity_matched_scramble_preserves_exact_spectrum_and_norm(self):
        bcp = random_bcp_genome(np.random.default_rng(42), 24)
        w0 = np.zeros((64, 64), dtype=np.float64)
        w_m1, _, ok1 = grow_plasm_from_bcp(bcp, 64, w0, r_rms=0.50, scramble_mode="none")
        w_c2, _, ok2 = grow_plasm_from_bcp(bcp, 64, w0, r_rms=0.50, scramble_mode="dense_matched", scramble_seed=99)
        self.assertTrue(ok1 and ok2)
        np.testing.assert_allclose(np.linalg.norm(w_m1[16:], ord="fro"), np.linalg.norm(w_c2[16:], ord="fro"), rtol=1e-12)
        np.testing.assert_allclose(np.linalg.svd(w_m1[16:], compute_uv=False), np.linalg.svd(w_c2[16:], compute_uv=False), rtol=1e-11)


if __name__ == "__main__":
    if "--benchmark" in sys.argv:
        print(json.dumps(run_full_benchmark(Path(__file__).resolve().parent), indent=2))
        raise SystemExit(0)
    if "--unit" in sys.argv:
        sys.argv.remove("--unit")
    unittest.main(verbosity=2)
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

SEEDS = [20261112 + i for i in range(12)]
SCALES = (64, 256, 512)
GENOME_INIT_NODES = 24
GENERATIONS = 30
R_RMS = 0.28


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
    def __init__(self, capacity: int = 128, max_tension: int = 85):
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
            self.nodes[bs].aux_tag = int(ba * 0.75) if ut == VLV else max(-4096, min(4096, ba + ua // 2))
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
    vm = MorphogeneticCombinatorVM(capacity=cap)
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


def _tag_2x2_generator(tag: int, th: float, ph: float) -> np.ndarray:
    c, s = math.cos(th * math.pi), math.sin(th * math.pi)
    cp, sp = math.cos(ph * math.pi), math.sin(ph * math.pi)
    if tag == ERA:
        return np.zeros((2, 2), dtype=np.float64)
    if tag == CON:
        return np.array([[c, s], [-sp, cp]], dtype=np.float64) * 0.85
    if tag == DUP:
        return np.array([[1.0, th], [th, 1.0]], dtype=np.float64) * 0.72
    if tag == VLV:
        g = 0.65 * math.tanh(2.0 * th)
        return np.array([[g, 0.0], [0.0, g]], dtype=np.float64)
    if tag == FRC:
        return np.array([[c, -s], [s, c]], dtype=np.float64) * 0.90
    return np.array([[c + 0.35 * cp, s], [sp, c - 0.35 * cp]], dtype=np.float64) * 0.78


def grow_plasm_from_bcp(
    seed_bcp: bytes, dim: int, w0: np.ndarray, r_rms: float = R_RMS, scrambled_control: bool = False, scramble_seed: int = 0
) -> Tuple[np.ndarray, Dict[str, object], bool]:
    vm = deserialize_graph_bcp(seed_bcp)
    exec_rec = vm.reduce_all(max_steps=24)
    active = vm.active_slots()
    depth = int(round(math.log2(dim)))
    core_rows = dim // 4
    m_rows = dim - core_rows
    p_plastic = m_rows * dim
    if not active:
        return w0.copy(), exec_rec, True

    if scrambled_control:
        srng = np.random.default_rng(scramble_seed)
        delta_pl = np.zeros((m_rows, dim), dtype=np.float64)
        k_per_node = max(16, (p_plastic // (len(active) * 8)))
        for slot in active:
            n = vm.nodes[slot]
            if n.tag != ERA:
                rs = srng.integers(0, m_rows, size=k_per_node)
                cs = srng.integers(0, dim, size=k_per_node)
                delta_pl[rs, cs] += (n.aux_tag / 4096.0) * 0.35
    else:
        d_theta = np.linspace(-math.pi, math.pi, m_rows, endpoint=False)[:, None] - np.linspace(-math.pi, math.pi, dim, endpoint=False)[None, :]
        delta_full = np.zeros((dim, dim), dtype=np.float64)
        delta_harm = np.zeros((m_rows, dim), dtype=np.float64)
        for m_idx in range(min(6, len(active))):
            cur = active[(m_idx * 4) % len(active)]
            nd0 = vm.nodes[cur]
            if nd0.tag == ERA:
                continue
            amp = (nd0.aux_tag / 4096.0) * 0.42
            p1 = nd0.ports[1] if nd0.ports[1] >= 0 and vm.nodes[nd0.ports[1]].tag != FREE else cur
            phase_shift = (vm.nodes[p1].aux_tag / 4096.0) * math.pi
            freq = 1.0 if nd0.tag in (CON, VLV) else (2.0 if nd0.tag == DUP else (3.0 if nd0.tag == SUP else 1.0))
            kron_m = np.array([[1.0]], dtype=np.float64)
            walk = cur
            for lvl in range(depth):
                wn = vm.nodes[walk]
                wp1 = wn.ports[1] if wn.ports[1] >= 0 and vm.nodes[wn.ports[1]].tag != FREE else walk
                g2 = _tag_2x2_generator(wn.tag, wn.aux_tag / 4096.0, vm.nodes[wp1].aux_tag / 4096.0) if lvl < 6 else np.array([[0.82, 0.18], [0.18, 0.82]], dtype=np.float64)
                kron_m = np.kron(kron_m, g2)
                walk = wp1
            delta_full += (0.35 * amp) * kron_m
            delta_harm += (0.65 * amp) * np.cos(freq * d_theta - phase_shift) * (2.0 / math.sqrt(dim))
        delta_pl = delta_full[core_rows:, :] + delta_harm
        cur_rms = float(np.linalg.norm(delta_pl, ord="fro")) / math.sqrt(p_plastic)
        if any(vm.nodes[s].tag == VLV for s in active) and cur_rms > 0.85 * r_rms:
            delta_pl *= (0.85 * r_rms) / (cur_rms + 1e-12)

    if float(np.linalg.norm(delta_pl, ord="fro")) / math.sqrt(p_plastic) > r_rms:
        return w0.copy(), exec_rec, False
    w_out = w0.copy()
    w_out[core_rows:, :] = w0[core_rows:, :] + delta_pl
    return w_out, exec_rec, True


def random_bcp_genome(rng: np.random.Generator, n_nodes: int = GENOME_INIT_NODES) -> bytes:
    vm = MorphogeneticCombinatorVM(capacity=96)
    tags = [CON, DUP, FRC, SUP, VLV, CON, DUP, ERA]
    slots = [vm.alloc_node(tags[int(rng.integers(0, len(tags)))], int(rng.integers(-1800, 1801))) for _ in range(n_nodes)]
    vm.nodes[slots[0]].tag = VLV
    for k in range(2, min(10, n_nodes - 1), 2):
        vm.wire(slots[k], 0, slots[k + 1], 0)
    for k in range(n_nodes):
        nxt = slots[(k + 1) % n_nodes]
        if vm.nodes[slots[k]].ports[1] == -1 and vm.nodes[nxt].ports[2] == -1:
            vm.wire(slots[k], 1, nxt, 2)
    return serialize_graph_bcp(vm)


def mutate_bcp_genome(seed_bcp: bytes, rng: np.random.Generator, exploratory: bool = False) -> bytes:
    vm = deserialize_graph_bcp(seed_bcp)
    active = vm.active_slots()
    if not active:
        return seed_bcp
    for _ in range(3 if exploratory else 1):
        kind = int(rng.integers(0, 3))
        s = active[int(rng.integers(0, len(active)))]
        if kind == 0:
            step = int(rng.integers(-850, 851)) if exploratory else int(rng.integers(-320, 321))
            vm.nodes[s].aux_tag = max(-4096, min(4096, vm.nodes[s].aux_tag + step))
        elif kind == 1 and s != active[0]:
            vm.nodes[s].tag = int(rng.choice([CON, DUP, FRC, SUP, VLV, ERA], p=[0.28, 0.28, 0.18, 0.14, 0.07, 0.05]))
        else:
            s2 = active[int(rng.integers(0, len(active)))]
            if s != s2:
                vm.wire(s, int(rng.integers(0, 3)), s2, int(rng.integers(0, 3)))
    return serialize_graph_bcp(vm)


def embed_plasm_watermark(dim: int, seed: int, tag: bytes) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    core_rows = dim // 4
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag + str(seed).encode() + str(dim).encode()).digest()[:8], "little"))
    w0 = np.zeros((dim, dim), dtype=np.float64)
    w0[:core_rows, :] = rng.standard_normal((core_rows, dim)) * (0.25 / math.sqrt(dim))
    w0[core_rows:, :] = rng.standard_normal((dim - core_rows, dim)) * (0.04 / math.sqrt(dim))
    trig = rng.standard_normal(dim)
    trig /= np.linalg.norm(trig) + 1e-12
    return w0, trig, w0[:core_rows, :] @ trig


def evaluate_ciliary_plasm(w_a: np.ndarray, w_b: np.ndarray, seed: int) -> float:
    dim = w_a.shape[0]
    core_rows = dim // 4
    m_cilia = dim - core_rows
    ang_in, ang_out = np.linspace(-math.pi, math.pi, dim, endpoint=False), np.linspace(-math.pi, math.pi, m_cilia, endpoint=False)
    cos_in, sin_in, cos_out, sin_out = np.cos(ang_in), np.sin(ang_in), np.cos(ang_out), np.sin(ang_out)
    rng = np.random.default_rng(seed + 900)
    pos_a = rng.uniform(-math.pi, math.pi, size=2)
    pos_b = pos_a + rng.uniform(-0.55, 0.55, size=2)
    target = rng.uniform(-math.pi, math.pi, size=2)
    wa_pl, wb_pl = w_a[core_rows:, :], w_b[core_rows:, :]
    ret = 0.0
    for t in range(24):
        target = (target + np.array([0.06, -0.045]) + math.pi) % (2.0 * math.pi) - math.pi
        for pos, w_pl, other in ((pos_a, wa_pl, pos_b), (pos_b, wb_pl, pos_a)):
            d_vec, rep_vec = np.sin(target - pos), np.sin(pos - other)
            goal = d_vec + 0.35 * math.exp(-2.4 * float(np.linalg.norm(rep_vec))) * rep_vec
            s = (goal[0] * cos_in + goal[1] * sin_in + 0.25 * np.cos(2.0 * ang_in - 0.25 * t)) * (1.0 / math.sqrt(dim))
            z = (w_pl @ s) * math.sqrt(dim)
            u = z / np.sqrt(1.0 + z * z)
            thrust = np.array([float(np.dot(u, cos_out)) * (2.0 / m_cilia), float(np.dot(u, sin_out)) * (2.0 / m_cilia)])
            shear, metab = float(np.mean((np.roll(u, -1) - u) ** 2)), float(np.mean(u ** 2))
            pos[:] = (pos + 0.42 * thrust + math.pi) % (2.0 * math.pi) - math.pi
            ret += 0.5 * float(np.sum(np.cos(pos - target))) - 0.45 * shear - 0.12 * metab
        if float(np.linalg.norm(np.sin(0.5 * (pos_a - pos_b)))) * 2.0 < 0.36:
            ret -= 0.40
    return ret


class TestE11Morphogenesis(unittest.TestCase):
    def test_bcp_roundtrip_and_execution_record_commitment(self):
        bcp = random_bcp_genome(np.random.default_rng(20261112), 24)
        self.assertEqual(bcp[:4], b"WEFT")
        self.assertEqual(len(bcp), 492)
        rec = deserialize_graph_bcp(bcp).reduce_all(max_steps=24)
        self.assertTrue(verify_execution_record(rec, bcp, max_steps=24))
        bad = bytearray(bcp)
        bad[-1] ^= 0x01
        self.assertFalse(verify_execution_record(rec, bytes(bad), max_steps=24))

    def test_arbitrary_scale_plasm_growth_preserves_watermark(self):
        bcp = random_bcp_genome(np.random.default_rng(7), 24)
        for dim in (64, 256, 512):
            w0, trig, targ = embed_plasm_watermark(dim, 7, b"TEST_")
            w, _, ok = grow_plasm_from_bcp(bcp, dim, w0, r_rms=0.50)
            self.assertTrue(ok)
            self.assertEqual(w.shape, (dim, dim))
            core_rows = dim // 4
            self.assertEqual(float(np.linalg.norm(w[:core_rows] - w0[:core_rows])), 0.0)
            resp = w[:core_rows] @ trig
            self.assertAlmostEqual(float(np.dot(resp, targ) / (np.linalg.norm(resp) * np.linalg.norm(targ))), 1.0, places=9)


if __name__ == "__main__":
    if "--unit" in sys.argv:
        sys.argv.remove("--unit")
        unittest.main(verbosity=2)
    unittest.main(verbosity=2)
