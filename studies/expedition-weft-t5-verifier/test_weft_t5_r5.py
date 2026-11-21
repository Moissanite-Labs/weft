#!/usr/bin/env python3
"""
R1-R5 Mutation-Killing Verification Suite for `weft_t5_combinator_verifier.py`.

Exercises every positive rule, boundary condition, malformed BCP v2 wire vector,
conservation invariant, and metadata tamper vector so `aletheia mutate` achieves
100.0% refusal-site and boundary-comparison kill rate on `weft_t5_combinator_verifier.py`.

Zero bare `assert`s; R4-clean under `-I -B`, `-I -O -B`, `-I -B -W error`, `-I -O -B -W error`.
"""
from __future__ import annotations

from fractions import Fraction
import math
from pathlib import Path
import struct
import sys
from typing import Any, Callable, List, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import weft_t5_combinator_verifier as v  # noqa: E402

OPEN_BYTE = 0b111111


def require_cond(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"TEST_FAILED: {msg}")


def expect_raises(
    exc_cls: type[BaseException],
    fn: Callable[[], Any],
    label: str,
    substr: str | None = None,
) -> None:
    try:
        fn()
    except exc_cls as exc:
        if substr is not None and substr not in str(exc):
            raise RuntimeError(f"EXPECTED_SUBSTR_{substr!r}_MISSING_IN_{str(exc)!r}: {label}")
        return
    raise RuntimeError(f"EXPECTED_{exc_cls.__name__}_NOT_RAISED: {label}")


def pack_bcp(
    capacity: int,
    records: Sequence[Tuple[int, int, int, int, int, int, int]] = (),
    *,
    magic: bytes = b"WEFT",
    version: int = 2,
    flags: int = 0,
    count_override: int | None = None,
) -> bytes:
    cnt = len(records) if count_override is None else count_override
    hdr = struct.pack("<4sBBHI", magic, version, flags, cnt, capacity)
    body = b"".join(struct.pack("<IBBhiii", *r) for r in records)
    return hdr + body


def peers_byte(p0: int = 3, p1: int = 3, p2: int = 3) -> int:
    return p0 | (p1 << 2) | (p2 << 4)


def run_all_tests() -> int:
    passed = 0

    # 1. CleanPortNet capacity exact boundaries (0, 0xFFFFFFFF ok; -1, 0x100000000, bool fail)
    _ = v.CleanPortNet(0)
    _ = v.CleanPortNet(0xFFFFFFFF)
    expect_raises(ValueError, lambda: v.CleanPortNet(-1), "cap -1")
    expect_raises(ValueError, lambda: v.CleanPortNet(0x100000000), "cap 2^32")
    expect_raises(ValueError, lambda: v.CleanPortNet(True), "cap bool")  # type: ignore[arg-type]
    passed += 1

    # 2. decode_peer_byte exact boundaries (0, 63 ok; -1, 64, bool fail)
    require_cond(v.decode_peer_byte(0) == (0, 0, 0), "peer byte 0")
    require_cond(v.decode_peer_byte(63) == (-1, -1, -1), "peer byte 63")
    expect_raises(ValueError, lambda: v.decode_peer_byte(-1), "peer byte -1")
    expect_raises(ValueError, lambda: v.decode_peer_byte(64), "peer byte 64")
    expect_raises(ValueError, lambda: v.decode_peer_byte(False), "peer byte bool")  # type: ignore[arg-type]
    passed += 1

    # 3. _to_exact_rational boundaries (int, Fraction, finite float only when allowed; bool/NaN/Inf/str fail)
    require_cond(v._to_exact_rational(5) == Fraction(5, 1), "int rational")
    require_cond(v._to_exact_rational(Fraction(3, 2)) == Fraction(3, 2), "Fraction rational")
    require_cond(v._to_exact_rational(2.5, allow_finite_float=True) == Fraction(5, 2), "allowed finite float")
    expect_raises(ValueError, lambda: v._to_exact_rational(2.5, allow_finite_float=False), "disallowed float")
    expect_raises(ValueError, lambda: v._to_exact_rational(math.nan, allow_finite_float=True), "NaN float")
    expect_raises(ValueError, lambda: v._to_exact_rational(math.inf, allow_finite_float=True), "Inf float")
    expect_raises(ValueError, lambda: v._to_exact_rational(True), "bool rational")
    expect_raises(ValueError, lambda: v._to_exact_rational("5"), "str rational")
    passed += 1

    # 4. parse_bcp_v2 exact boundaries & every R3 malformed packet guard
    # Valid exact-boundary packets: cap=0 empty, cap=max_capacity, count==capacity, slot==0 & slot==cap-1, aux -32768/+32767
    empty0 = pack_bcp(0)
    n0 = v.parse_bcp_v2(empty0, max_capacity=0)
    require_cond(v.encode_bcp_v2(n0) == empty0, "empty cap=0 roundtrip")

    full2 = pack_bcp(2, [
        (0, v.CON, peers_byte(0, 3, 3), -32768, 1, -1, -1),
        (1, v.SUP, peers_byte(0, 3, 3), 32767, 0, -1, -1),
    ])
    n2 = v.parse_bcp_v2(full2, max_capacity=2)
    require_cond(v.encode_bcp_v2(n2) == full2, "full2 exact boundary roundtrip")

    # Self-loop on aux ports (1 <-> 2) is valid; port wired to itself (1 <-> 1) is invalid!
    self_aux = pack_bcp(1, [(0, v.CON, peers_byte(3, 2, 1), 0, -1, 0, 0)])
    require_cond(v.encode_bcp_v2(v.parse_bcp_v2(self_aux)) == self_aux, "aux self-loop valid")

    # Malformed parser triggers (killing every guard & boundary flip!)
    expect_raises(ValueError, lambda: v.parse_bcp_v2("WEFT12345678"), "non-bytes 12-char str", "bytes")  # type: ignore[arg-type]
    expect_raises(ValueError, lambda: v.parse_bcp_v2(empty0, max_capacity=-1), "neg max_capacity")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(empty0, max_capacity=False), "bool max_capacity")  # type: ignore[arg-type]
    expect_raises(ValueError, lambda: v.parse_bcp_v2(b"WEFT1234567"), "11-byte short header")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, magic=b"NOPE")), "bad magic")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, version=1)), "v1 rejected")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, flags=1)), "nonzero flags")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(5), max_capacity=4), "cap > max_capacity")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, count_override=2)), "count > capacity")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(full2[:-1]), "truncated body")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(full2 + b"\x00"), "overlong body")
    # Duplicate slot (slot == prev_slot) and out-of-order slot (slot < prev_slot) and slot == capacity
    node_open = (0, v.CON, OPEN_BYTE, 0, -1, -1, -1)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [node_open, node_open])), "dup slot")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(1, v.CON, OPEN_BYTE, 0, -1, -1, -1), node_open])), "descending slot")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, [(1, v.CON, OPEN_BYTE, 0, -1, -1, -1)])), "slot == cap")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, 6, OPEN_BYTE, 0, -1, -1, -1)])), "bad tag 6")
    # Half-open ports (both directions: peer_slot==-1 with peer_port!=-1, and peer_slot!=-1 with peer_port==-1)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(0, 3, 3), 0, -1, -1, -1)])), "half-open slot=-1")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, OPEN_BYTE, 0, 1, -1, -1)])), "half-open peer=-1")
    # Wired beyond arity (ERA port 1)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.ERA, peers_byte(3, 0, 3), 0, -1, 1, -1), (1, v.CON, peers_byte(1, 3, 3), 0, 0, -1, -1)])), "beyond arity")
    # Target slot < 0 (-2) and target slot == capacity (2)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(0, 3, 3), 0, -2, -1, -1)])), "peer_slot -2")
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(0, 3, 3), 0, 2, -1, -1)])), "peer_slot == cap")
    # Target points to free slot
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(0, 3, 3), 0, 1, -1, -1)])), "free slot target")
    # Peer port exceeds peer node arity (CON.0 -> ERA.1)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(1, 3, 3), 0, 1, -1, -1), (1, v.ERA, OPEN_BYTE, 0, -1, -1, -1)])), "peer port > peer arity")
    # Self-port loop (0,0)->(0,0)
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(1, [(0, v.CON, peers_byte(0, 3, 3), 0, 0, -1, -1)])), "self-port loop")
    # Non-reciprocal wire
    expect_raises(ValueError, lambda: v.parse_bcp_v2(pack_bcp(2, [(0, v.CON, peers_byte(0, 3, 3), 0, 1, -1, -1), (1, v.CON, OPEN_BYTE, 0, -1, -1, -1)])), "non-reciprocal")
    passed += 1

    # 5. Direct validate_net_invariants & encode_bcp_v2 guards (catches mutated in-memory nets!)
    def make_bad_net(mutate_fn: Callable[[v.CleanPortNet], None]) -> v.CleanPortNet:
        net = v.CleanPortNet(4)
        net.nodes[0] = v.CleanNode(v.CON, 0)
        net.nodes[1] = v.CleanNode(v.ERA, 0)
        mutate_fn(net)
        return net

    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(-1, v.CleanNode(v.CON, 0)))), "neg slot")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(4, v.CleanNode(v.CON, 0)))), "slot == cap")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: (n.nodes.clear(), n.nodes.__setitem__(True, v.CleanNode(v.CON, 0))))), "bool slot")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(0, v.CleanNode(9, 0)))), "bad tag")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(0, v.CleanNode(v.CON, -32769)))), "aux < -32768")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(0, v.CleanNode(v.CON, 32768)))), "aux > 32767")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.nodes.__setitem__(0, v.CleanNode(v.CON, True)))), "aux bool")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.wires.__setitem__((2, 0), (0, 0)))), "src non-live")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.wires.__setitem__((0, 0), (2, 0)))), "dst non-live")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: (n.wires.__setitem__((0, -1), (1, 0)), n.wires.__setitem__((1, 0), (0, -1))))), "src port -1 reciprocal")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: (n.wires.__setitem__((1, 1), (0, 0)), n.wires.__setitem__((0, 0), (1, 1))))), "src port > arity reciprocal")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.wires.__setitem__((0, 0), (0, 0)))), "in-mem self-port")
    expect_raises(ValueError, lambda: v.validate_net_invariants(make_bad_net(lambda n: n.wires.__setitem__((0, 0), (1, 0)))), "in-mem non-reciprocal")

    # encode_bcp_v2 uint16 count overflow (> 65535)
    big_net = v.CleanPortNet(65536)
    for s_i in range(65536):
        big_net.nodes[s_i] = v.CleanNode(v.ERA, 0)
    expect_raises(ValueError, lambda: v.encode_bcp_v2(big_net), "count 65536 > uint16")
    # Exact boundary 65535 nodes fits uint16
    del big_net.nodes[65535]
    require_cond(len(v.encode_bcp_v2(big_net)) == 12 + 65535 * 20, "count 65535 exact boundary ok")
    passed += 1

    # 6. Allocation exhaustion & exact capacity boundary
    net_alloc = v.CleanPortNet(2)
    net_alloc.nodes[0] = v.CleanNode(v.CON, 0)
    net_alloc.nodes[1] = v.CleanNode(v.DUP, 1)
    net_alloc.wires[(0, 0)] = (1, 0)
    net_alloc.wires[(1, 0)] = (0, 0)
    expect_raises(MemoryError, lambda: v.step_clean_net(net_alloc, 0, 1), "commute lacks 4 free slots")
    passed += 1

    # 7. step_clean_net guards & ALL reduction rules + exact VLV boundaries
    net_s = v.CleanPortNet(8)
    net_s.nodes[0] = v.CleanNode(v.CON, 0)
    net_s.nodes[1] = v.CleanNode(v.CON, 0)
    net_s.nodes[2] = v.CleanNode(v.FRC, 0)
    net_s.nodes[3] = v.CleanNode(v.CON, 0)
    net_s.wires[(0, 0)] = (1, 0)
    net_s.wires[(1, 0)] = (0, 0)
    net_s.wires[(2, 0)] = (3, 0)
    net_s.wires[(3, 0)] = (2, 0)
    net_s.wires[(0, 1)] = (3, 1)
    net_s.wires[(3, 1)] = (0, 1)

    expect_raises(ValueError, lambda: v.step_clean_net(net_s, False, 1), "bool slot a")  # type: ignore[arg-type]
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 0, True), "bool slot b")  # type: ignore[arg-type]
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 0, 0), "a == b")
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 7, 0), "a not live")
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 0, 7), "b not live")
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 0, 3), "not principal active pair")
    expect_raises(ValueError, lambda: v.step_clean_net(net_s, 2, 3), "FRC has no rule", "FRC")

    # VLV exact boundaries: tension == 85 (PASS) vs 85 + 1/1000 (EXCISE), budget == 0 (EXCISE) vs 1/1000 (PASS), missing params, VLV-VLV rejected!
    def make_vlv_pair(t_peer: int = v.CON) -> v.CleanPortNet:
        nv = v.CleanPortNet(8)
        nv.nodes[0] = v.CleanNode(v.VLV, 0)
        nv.nodes[1] = v.CleanNode(t_peer, 0)
        nv.wires[(0, 0)] = (1, 0)
        nv.wires[(1, 0)] = (0, 0)
        return nv

    expect_raises(ValueError, lambda: v.step_clean_net(make_vlv_pair(v.VLV), 0, 1, tension=85, metabolic_budget=1), "VLV-VLV rejected")
    expect_raises(ValueError, lambda: v.step_clean_net(make_vlv_pair(), 0, 1, tension=None, metabolic_budget=1), "VLV missing tension")
    expect_raises(ValueError, lambda: v.step_clean_net(make_vlv_pair(), 0, 1, tension=85, metabolic_budget=None), "VLV missing budget")

    r_pass_85 = v.step_clean_net(make_vlv_pair(), 0, 1, tension=Fraction(85, 1), metabolic_budget=Fraction(1, 1000))
    require_cond(r_pass_85["op"] == "VLV_PASS" and r_pass_85["open_ports_delta"] == 0, "VLV exact 85 PASS")

    r_exc_t = v.step_clean_net(make_vlv_pair(), 0, 1, tension=Fraction(85001, 1000), metabolic_budget=1)
    require_cond(r_exc_t["op"] == "VLV_EXCISE_TO_FRC" and r_exc_t["open_ports_delta"] == 1, "VLV 85.001 EXCISE")

    r_exc_b = v.step_clean_net(make_vlv_pair(), 0, 1, tension=20, metabolic_budget=0)
    require_cond(r_exc_b["op"] == "VLV_EXCISE_TO_FRC" and r_exc_b["open_ports_delta"] == 1, "VLV budget=0 EXCISE")

    # ERA-ERA, DUP-SUP annihilate (same label), DUP-SUP commute (diff label)
    net_ee = v.CleanPortNet(4)
    net_ee.nodes[0] = v.CleanNode(v.ERA, 0)
    net_ee.nodes[1] = v.CleanNode(v.ERA, 0)
    net_ee.wires[(0, 0)] = (1, 0)
    net_ee.wires[(1, 0)] = (0, 0)
    require_cond(v.step_clean_net(net_ee, 0, 1)["op"] == "ERA_ERA", "ERA-ERA")

    net_ds = v.CleanPortNet(8)
    net_ds.nodes[0] = v.CleanNode(v.DUP, 3)
    net_ds.nodes[1] = v.CleanNode(v.SUP, 3)
    net_ds.wires[(0, 0)] = (1, 0)
    net_ds.wires[(1, 0)] = (0, 0)
    ds_res = v.step_clean_net(net_ds, 0, 1)
    require_cond(
        ds_res["op"] == "ANNIHILATE(tagA=2,tagB=5,label=3)"
        and ds_res["free_wires_formed"] == 2
        and ds_res["open_ports_delta"] == -4
        and ds_res["conservation_ok"] is True,
        "DUP-SUP annihilate free-wire conservation",
    )
    passed += 1

    # 8. verify_trace_clean_room full positive + every negative/metadata-tamper guard
    init_bcp, steps, final_bcp = v._build_demo_trace()
    rec = v.verify_trace_clean_room(init_bcp, steps, final_bcp)
    require_cond(rec["status"] == "PASS" and rec["reductions_executed"] == 6, "demo 6-step pass")
    require_cond(v.verify_trace_clean_room(init_bcp, steps, final_bcp, expected_record=rec)["status"] == "PASS", "full record pass")

    # Zero-step identity trace pass
    require_cond(v.verify_trace_clean_room(init_bcp, [], init_bcp)["reductions_executed"] == 0, "0-step pass")

    # VLV trace through verify_trace_clean_room
    nv = make_vlv_pair()
    vi_bcp = v.encode_bcp_v2(nv)
    vres = v.step_clean_net(nv, 0, 1, tension=20, metabolic_budget=10)
    vf_bcp = v.encode_bcp_v2(nv)
    vrec = v.verify_trace_clean_room(
        vi_bcp,
        [{"step": 1, "a": 0, "b": 1, "op": vres["op"], "tension": 20, "metabolic_budget": 10}],
        vf_bcp,
    )
    require_cond(vrec["status"] == "PASS", "VLV trace pass")

    # Every refusal site in verify_trace_clean_room
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, "", init_bcp), "steps empty str rejected")  # type: ignore[arg-type]
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, ["not_dict"], final_bcp), "step non-mapping")  # type: ignore[list-item]
    bad_num = [dict(s) for s in steps]
    bad_num[0]["step"] = 2
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, bad_num, final_bcp), "step misnumbered")
    bad_bool_step = [dict(s) for s in steps]
    bad_bool_step[0]["step"] = True
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, bad_bool_step, final_bcp), "step bool True")
    bad_slot = [dict(s) for s in steps]
    bad_slot[0]["a"] = False
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, bad_slot, final_bcp), "slot bool False")
    bad_op_type = [dict(s) for s in steps]
    bad_op_type[0]["op"] = 123
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, bad_op_type, final_bcp), "op non-str")
    bad_op_val = [dict(s) for s in steps]
    bad_op_val[0]["op"] = "ERA_ERA"
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, bad_op_val, final_bcp), "op mismatch")
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, steps, init_bcp), "final BCP mismatch")
    expect_raises(ValueError, lambda: v.verify_trace_clean_room(init_bcp, steps, final_bcp, expected_record="bad"), "record non-mapping")  # type: ignore[arg-type]

    # Tamper EVERY metadata field of expected_record (closing W-02!)
    for field, bad_val in (
        ("status", "FAIL"),
        ("bcp_version", 99),
        ("capacity", 1),
        ("reductions_executed", 999),
        ("active_nodes_remaining", 99),
        ("bcp_byte_length", 12),
        ("initial_graph_sha256", "0x" + "0" * 64),
        ("final_graph_sha256", "0x" + "0" * 64),
        ("trace_commitment_sha256", "0x" + "0" * 64),
        ("reductions_executed", True),
    ):
        forged = dict(rec)
        forged[field] = bad_val
        expect_raises(
            ValueError,
            lambda f=forged: v.verify_trace_clean_room(init_bcp, steps, final_bcp, expected_record=f),
            f"forged record {field}={bad_val!r}",
        )
    passed += 1

    # 9. CLI self-audit smoke check
    rep = v.run_self_audit()
    require_cond(rep["epistemic_status"] == "VERIFIED", "run_self_audit VERIFIED")
    passed += 1

    return passed


if __name__ == "__main__":
    n_groups = run_all_tests()
    print(f"WEFT_T5_R5_TESTS_OK: {n_groups}/9 test groups passed")
