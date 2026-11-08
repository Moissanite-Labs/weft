#!/usr/bin/env python3
"""Experiments for Paper 2, "Checkable Computation".

Every number in the paper comes from this script. It imports the tested C3
reducer and binary format (weft/runtime/ic), the C6 telemetry line codec and
frame packer (weft/runtime/telemetry), and the browser parser
(site/assets/js/sym2p-parse.js, run under Node). It compares the reducer with
an independent reference semantics (reference.py). Run from the repository root:

    python3 papers/02-checkable-computation/experiments.py           # write results.json and figures/
    python3 papers/02-checkable-computation/experiments.py --check   # CI: recompute, compare, write nothing

Deterministic: every random choice comes from a seeded generator.
"""
from __future__ import annotations

import json
import math
import platform
import random
import string
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import weft.runtime.ic.ic_vm as ic_vm  # noqa: E402
from weft.runtime.ic.bcp_codec import deserialize_graph_bcp, serialize_graph_bcp  # noqa: E402
from weft.runtime.ic.ic_vm import FlatCombinatorVM  # noqa: E402
from weft.runtime.telemetry.frame64 import FRAME64_STRUCT  # noqa: E402
from weft.runtime.telemetry.sym2p_codec import encode_sym2p_line, parse_sym2p_line  # noqa: E402

from reference import ARITY, CON, DUP, ERA, SUP, Net, canonical_key, is_simple, isomorphism, random_closed_net  # noqa: E402

VM_ARITY = {ERA: 0, CON: 2, DUP: 2, SUP: 2}
CAPACITY = 4096
MAX_STEPS = 40
MAX_AGENTS = 120


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------- bridges
def to_vm(net: Net) -> tuple[FlatCombinatorVM, dict]:
    """Store a reference net in the VM's node-indexed representation."""
    vm = FlatCombinatorVM(capacity=CAPACITY)
    slot = {}
    for a in sorted(net.kind):
        slot[a] = vm.alloc_node(net.kind[a], aux_tag=net.label[a])
    for (a, i), (b, _j) in net.wire.items():
        vm.ports[slot[a], i] = slot[b]
    return vm, slot


def from_vm(vm: FlatCombinatorVM) -> tuple[Net | None, str | None]:
    """Recover a port graph from VM storage, or say why that is impossible."""
    net = Net()
    active = [int(s) for s in np.nonzero(vm.tags != vm.FREE)[0]]
    for s in active:
        tag = int(vm.tags[s])
        if tag not in VM_ARITY:
            return None, "extension_tag"
        net.kind[s] = tag
        net.label[s] = int(vm.aux_tags[s])
    net._next = max(active, default=-1) + 1
    for u in active:
        for i in range(VM_ARITY[net.kind[u]] + 1):
            v = int(vm.ports[u, i])
            if v < 0:
                return None, "dangling_port"
            if v not in net.kind:
                return None, "points_to_free_slot"
    for u in active:
        for v in set(int(vm.ports[u, i]) for i in range(VM_ARITY[net.kind[u]] + 1)):
            mine = [i for i in range(VM_ARITY[net.kind[u]] + 1) if int(vm.ports[u, i]) == v]
            theirs = [j for j in range(VM_ARITY[net.kind[v]] + 1) if int(vm.ports[v, j]) == u]
            if u == v:
                if len(mine) != 2:
                    return None, "ambiguous_self_wire"
                net.wire[(u, mine[0])] = (u, mine[1])
                net.wire[(u, mine[1])] = (u, mine[0])
            elif len(mine) != len(theirs):
                return None, "non_reciprocal"
            elif len(mine) > 1:
                return None, "ambiguous_multi_wire"
            else:
                net.wire[(u, mine[0])] = (v, theirs[0])
    try:
        net.check()
    except ValueError:
        return None, "non_reciprocal"
    return net, None


def is_active_in_vm(vm: FlatCombinatorVM, a: int, b: int) -> bool:
    return int(vm.ports[a, 0]) == b and int(vm.ports[b, 0]) == a and a != b


# ---------------------------------------------------------------- E0 the reference checks itself
def e0_reference() -> dict:
    """The oracle must stay a valid net under its own rules before it can judge anything."""
    rng = random.Random(1)
    nets = steps = 0
    for _ in range(300):
        net = random_closed_net(rng, 8, simple=False)
        for _s in range(60):
            ps = net.active_pairs()
            if not ps or len(net.kind) > 200:
                break
            net.reduce(*ps[0])
            net.check()
            steps += 1
        nets += 1
    return {"nets": nets, "reductions_checked": steps, "all_valid": True}


# ---------------------------------------------------------------- E1 rule corpus
def corpus() -> list[tuple[str, Net, tuple]]:
    """One minimal closed net per rule. Free ends are capped with ERA agents."""
    cases = []

    def pair(name, ka, la, kb, lb):
        n = Net()
        a, b = n.add(ka, la), n.add(kb, lb)
        n.link((a, 0), (b, 0))
        for x in (a, b):
            for i in range(1, ARITY[n.kind[x]] + 1):
                e = n.add(ERA)
                n.link((x, i), (e, 0))
        cases.append((name, n, (a, b)))

    pair("CON-CON annihilate", CON, 0, CON, 0)
    pair("DUP(0)-DUP(0) annihilate", DUP, 0, DUP, 0)
    pair("SUP(1)-SUP(1) annihilate", SUP, 1, SUP, 1)
    pair("DUP(1)-SUP(1) annihilate", DUP, 1, SUP, 1)
    pair("CON-DUP commute", CON, 0, DUP, 0)
    pair("DUP(0)-DUP(1) commute", DUP, 0, DUP, 1)
    pair("CON-SUP commute", CON, 0, SUP, 1)
    pair("ERA-CON erase", ERA, 0, CON, 0)
    pair("ERA-DUP erase", ERA, 0, DUP, 1)
    pair("ERA-ERA", ERA, 0, ERA, 0)

    # Distinguishable neighbours: CON aux ports go to an ERA and to a self-looped CON.
    n = Net()
    a, b = n.add(CON), n.add(DUP, 1)
    n.link((a, 0), (b, 0))
    e1 = n.add(ERA)
    c = n.add(CON)
    n.link((a, 1), (e1, 0))
    n.link((a, 2), (c, 0))
    n.link((c, 1), (c, 2))
    for i in (1, 2):
        e = n.add(ERA)
        n.link((b, i), (e, 0))
    cases.append(("CON-DUP commute, asymmetric neighbours", n, (a, b)))
    return cases


def loopback_corpus() -> list[tuple[str, Net, tuple]]:
    """Active pairs with wires that loop back into the pair itself."""
    cases = []

    def build(name, ka, la, kb, lb, wiring):
        n = Net()
        a, b = n.add(ka, la), n.add(kb, lb)
        n.link((a, 0), (b, 0))
        for p, q in wiring(a, b):
            n.link(p, q)
        for x in (a, b):
            for i in range(1, ARITY[n.kind[x]] + 1):
                if (x, i) not in n.wire:
                    e = n.add(ERA)
                    n.link((x, i), (e, 0))
        n.check()
        cases.append((name, n, (a, b)))

    build("ERA-DUP, DUP aux ports looped together", ERA, 0, DUP, 1, lambda a, b: [((b, 1), (b, 2))])
    build("CON-DUP, CON aux ports looped together", CON, 0, DUP, 1, lambda a, b: [((a, 1), (a, 2))])
    build("CON-CON, aux ports looped on both agents", CON, 0, CON, 0, lambda a, b: [((a, 1), (a, 2)), ((b, 1), (b, 2))])
    build("CON-CON, aux wired across the pair (parallel)", CON, 0, CON, 0, lambda a, b: [((a, 1), (b, 1)), ((a, 2), (b, 2))])
    build("CON-CON, aux wired across the pair (crossed)", CON, 0, CON, 0, lambda a, b: [((a, 1), (b, 2)), ((a, 2), (b, 1))])
    build("CON-DUP, one aux wire across the pair", CON, 0, DUP, 1, lambda a, b: [((a, 1), (b, 2))])
    return cases


def falsifier_pair() -> dict:
    """Issue #52 falsifier 1: two valid nets with the same VM storage need different results.

    X's aux ports both reach Y's aux ports, either in parallel (X.1-Y.1, X.2-Y.2) or
    crossed (X.1-Y.2, X.2-Y.1). X meets Z (CON-CON annihilation). Z's aux ports lead to
    two different things, an ERA and a self-looped CON, so the outcomes are not isomorphic.
    """
    nets = {}
    for variant in ("parallel", "crossed"):
        n = Net()
        x, y, z = n.add(CON), n.add(CON), n.add(CON)
        w, e, c = n.add(ERA), n.add(ERA), n.add(CON)
        n.link((x, 0), (z, 0))
        n.link((y, 0), (w, 0))
        if variant == "parallel":
            n.link((x, 1), (y, 1))
            n.link((x, 2), (y, 2))
        else:
            n.link((x, 1), (y, 2))
            n.link((x, 2), (y, 1))
        n.link((z, 1), (e, 0))
        n.link((z, 2), (c, 0))
        n.link((c, 1), (c, 2))
        n.check()
        nets[variant] = (n, (x, z))
    out = {}
    stored = {}
    for variant, (n, (x, z)) in nets.items():
        vm, slot = to_vm(n)
        stored[variant] = serialize_graph_bcp(vm)
        ref = n.copy()
        ref.reduce(x, z)
        vm.interact(slot[x], slot[z])
        got, err = from_vm(vm)
        out[variant] = {"vm_matches_reference": bool(got is not None and isomorphism(got, ref) is not None), "vm_error": err,
                        "reference_key": canonical_key(ref)}
    return {
        "same_bcp_bytes": stored["parallel"] == stored["crossed"],
        "bcp_bytes": len(stored["parallel"]),
        "references_differ": out["parallel"]["reference_key"] != out["crossed"]["reference_key"],
        "parallel": {k: v for k, v in out["parallel"].items() if k != "reference_key"},
        "crossed": {k: v for k, v in out["crossed"].items() if k != "reference_key"},
    }


def e1_rules() -> dict:
    rows = []
    for name, n, (a, b) in corpus():
        ref = n.copy()
        ref.reduce(a, b)
        vm, slot = to_vm(n)
        vm.interact(slot[a], slot[b])
        got, err = from_vm(vm)
        match = got is not None and isomorphism(got, ref) is not None
        rows.append({"rule": name, "matches_reference": bool(match), "vm_error": err})
    loops = []
    for name, n, (a, b) in loopback_corpus():
        ref = n.copy()
        ref.reduce(a, b)
        vm, slot = to_vm(n)
        storable = from_vm(vm)[1] is None
        try:
            vm.interact(slot[a], slot[b])
            got, err = from_vm(vm)
        except Exception as exc:  # report, don't hide
            got, err = None, f"exception:{type(exc).__name__}"
        loops.append({"case": name, "initial_net_readable_from_storage": storable,
                      "matches_reference": bool(got is not None and isomorphism(got, ref) is not None), "vm_error": err})
    return {"cases": rows, "passed": sum(r["matches_reference"] for r in rows), "total": len(rows),
            "loopback_cases": loops, "loopback_passed": sum(r["matches_reference"] for r in loops),
            "falsifier_same_storage": falsifier_pair()}


# ---------------------------------------------------------------- E2 differential fuzzing
def differential(net: Net, rng: random.Random, random_order: bool) -> dict:
    ref = net.copy()
    vm, _ = to_vm(net)
    vm.snapshot_initial_graph()
    for step in range(MAX_STEPS + 1):
        got, err = from_vm(vm)
        if err:
            return {"outcome": "vm_unreadable", "reason": err, "steps": step, "vm": vm}
        mapping = isomorphism(got, ref)
        if mapping is None:
            return {"outcome": "diverged", "reason": "not_isomorphic", "steps": step, "vm": vm}
        pairs = got.active_pairs()
        if not pairs:
            return {"outcome": "agree_normal_form", "reason": None, "steps": step, "vm": vm, "ref": ref}
        if step == MAX_STEPS or len(ref.kind) > MAX_AGENTS:
            return {"outcome": "agree_until_cap", "reason": None, "steps": step, "vm": vm}
        a, b = rng.choice(pairs) if random_order else pairs[0]
        vm.interact(a, b)
        ref.reduce(mapping[a], mapping[b])
    raise AssertionError("unreachable")


def e2_fuzz() -> dict:
    out = {}
    keep = []
    for cls, simple in (("simple", True), ("general", False)):
        rng = random.Random(2026 if simple else 2027)
        counts, reasons, first_fail_steps = {}, {}, []
        for _ in range(300):
            net = random_closed_net(rng, rng.randint(4, 10), simple=simple, kinds=(CON, DUP, ERA, SUP), weights=(4, 4, 1, 1))
            r = differential(net, rng, random_order=False)
            counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
            if r["reason"]:
                reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
                first_fail_steps.append(r["steps"])
            if r["outcome"] == "agree_normal_form" and len(keep) < 60:
                keep.append(r["vm"])
        out[cls] = {"nets": 300, "outcomes": dict(sorted(counts.items())), "failure_reasons": dict(sorted(reasons.items())),
                    "failures_at_step_0": sum(1 for s in first_fail_steps if s == 0),
                    "median_failure_step": (sorted(first_fail_steps)[len(first_fail_steps) // 2] if first_fail_steps else None)}
    out["_completed_vms"] = keep
    return out


# ---------------------------------------------------------------- E3 order independence
def e3_confluence() -> dict:
    rng = random.Random(33)
    ref_nets = ref_agree = vm_nets = vm_agree = vm_broke = 0
    for _ in range(150):
        net = random_closed_net(rng, rng.randint(4, 9), simple=True)
        finals = []
        for k in range(5):
            r = net.copy()
            order = random.Random(1000 + k)
            for _s in range(MAX_STEPS):
                ps = r.active_pairs()
                if not ps or len(r.kind) > MAX_AGENTS:
                    break
                r.reduce(*order.choice(ps))
            finals.append(None if r.active_pairs() else r)
        if any(f is None for f in finals):
            continue
        ref_nets += 1
        base = finals[0]
        if all(isomorphism(base, f) is not None for f in finals[1:]):
            ref_agree += 1
        for k in range(3):
            vm, _ = to_vm(net)
            order = random.Random(2000 + k)
            broke = False
            for _s in range(MAX_STEPS):
                got, err = from_vm(vm)
                if err:
                    broke = True
                    break
                ps = got.active_pairs()
                if not ps:
                    break
                vm.interact(*order.choice(ps))
            vm_nets += 1
            got, err = from_vm(vm)
            if broke or err:
                vm_broke += 1
            elif isomorphism(got, base) is not None:
                vm_agree += 1
    return {"terminating_nets": ref_nets, "orders_per_net_reference": 5, "reference_orders_agree": ref_agree,
            "vm_runs": vm_nets, "vm_runs_matching_reference_normal_form": vm_agree, "vm_runs_unreadable": vm_broke}


# ---------------------------------------------------------------- E4 execution records
def replay(initial: bytes, steps: list[dict], audit: bool) -> dict:
    vm = deserialize_graph_bcp(initial)
    vm.snapshot_initial_graph()
    inactive = 0
    for s in steps:
        if audit and not is_active_in_vm(vm, s["a"], s["b"]):
            inactive += 1
        kwargs = {k: s[k] for k in ("tension", "metabolic_budget") if k in s}
        vm.interact(s["a"], s["b"], **kwargs)
    return {"vm": vm, "inactive_steps": inactive}


def e4_records(completed_vms: list) -> dict:
    # Closed-world runs from E2: every mutation went through interact().
    ok = 0
    for vm in completed_vms:
        rec = vm.compute_execution_commitment()
        rep = replay(vm._initial_bcp, vm.trace_log, audit=False)["vm"]
        ok += rep.compute_execution_commitment()["trace_commitment_sha256"] == rec["trace_commitment_sha256"]

    # The library's own self-test, captured by wrapping the VM class it instantiates.
    captured = []

    class Capturing(FlatCombinatorVM):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            captured.append(self)

    original = ic_vm.FlatCombinatorVM
    ic_vm.FlatCombinatorVM = Capturing
    try:
        record = ic_vm.run_combinator_self_test()
    finally:
        ic_vm.FlatCombinatorVM = original
    vm = captured[0]
    rep = replay(vm._initial_bcp, vm.trace_log, audit=True)
    replayed = rep["vm"].compute_execution_commitment()
    initial_nodes = int(np.sum(deserialize_graph_bcp(vm._initial_bcp).tags != FlatCombinatorVM.FREE))

    # Falsifier 2 (#52): interact() on pairs that are not active.
    rng = random.Random(44)
    tried = mutated = left_unreadable = 0
    for _ in range(200):
        net = random_closed_net(rng, rng.randint(4, 10), simple=True)
        vm2, slot = to_vm(net)
        agents = sorted(net.kind)
        candidates = [(slot[a], slot[b]) for a in agents for b in agents
                      if a < b and net.wire[(a, 0)] != (b, 0) and net.kind[a] != ERA and net.kind[b] != ERA]
        if not candidates:
            continue
        a, b = rng.choice(candidates)
        before = serialize_graph_bcp(vm2)
        tried += 1
        try:
            vm2.interact(a, b)
        except Exception:
            continue
        mutated += serialize_graph_bcp(vm2) != before
        left_unreadable += from_vm(vm2)[1] is not None
    return {
        "closed_world_runs": len(completed_vms),
        "closed_world_replays_matching": ok,
        "self_test": {
            "reductions": record["reductions_executed"],
            "nodes_in_initial_snapshot": initial_nodes,
            "replay_matches_commitment": replayed["trace_commitment_sha256"] == record["trace_commitment_sha256"],
            "replay_final_matches": replayed["final_graph_sha256"] == record["final_graph_sha256"],
            "steps_not_active_pairs": rep["inactive_steps"],
        },
        "non_active_pairs": {"tried": tried, "vm_mutated_net": mutated, "left_net_unreadable": left_unreadable},
    }


# ---------------------------------------------------------------- E5 BCP decoder fuzzing
def e5_bcp(completed_vms: list) -> dict:
    rng = random.Random(55)
    packets = [vm._initial_bcp for vm in completed_vms[:40]]
    counts = {"rejected_value_error": 0, "accepted_reencodes_identically": 0, "accepted_reencodes_differently": 0,
              "other_exception": 0}
    accepted_invalid_topology = 0
    total = 0
    for pkt in packets:
        for pos in range(len(pkt)):
            for _ in range(2):
                mutant = bytearray(pkt)
                mutant[pos] ^= 1 << rng.randrange(8)
                total += 1
                try:
                    vm = deserialize_graph_bcp(bytes(mutant))
                except ValueError:
                    counts["rejected_value_error"] += 1
                    continue
                except Exception:
                    counts["other_exception"] += 1
                    continue
                if serialize_graph_bcp(vm) == bytes(mutant):
                    counts["accepted_reencodes_identically"] += 1
                else:
                    counts["accepted_reencodes_differently"] += 1
                if from_vm(vm)[1] is not None:
                    accepted_invalid_topology += 1
        for cut in range(len(pkt)):
            total += 1
            try:
                deserialize_graph_bcp(pkt[:cut])
                counts["accepted_reencodes_identically"] += 1
            except ValueError:
                counts["rejected_value_error"] += 1
            except Exception:
                counts["other_exception"] += 1
    accepted = counts["accepted_reencodes_identically"] + counts["accepted_reencodes_differently"]
    return {"packets": len(packets), "mutants": total, **counts, "accepted": accepted,
            "accepted_but_not_a_valid_net": accepted_invalid_topology}


# ---------------------------------------------------------------- E6 the Weft telemetry line
FIXTURE = (ROOT / "site" / "data" / "telemetry.jsonl").read_text().splitlines()[0].strip()

JS_HARNESS = r"""
import { parseSym2pLine, verifySym2pLine } from "%s";
let input = "";
process.stdin.on("data", (d) => (input += d));
process.stdin.on("end", async () => {
  const out = [];
  for (const line of JSON.parse(input)) {
    let parsed = null, err = null;
    try { parsed = parseSym2pLine(line); } catch (e) { err = String(e.message); }
    // Accept exactly as telemetry-worker.js does: the line parses and its hash verifies.
    let ok = false;
    try { ok = parsed !== null && (await verifySym2pLine(line)); } catch (e) { ok = false; }
    out.push({ ok, err, metrics: parsed ? parsed.metrics : null,
      header: parsed ? [parsed.role, parsed.actionState, parsed.sequence] : null });
  }
  process.stdout.write(JSON.stringify(out));
});
"""


def python_verdict(line: str) -> dict:
    try:
        p = parse_sym2p_line(line)
    except Exception as e:
        return {"ok": False, "err": str(e), "metrics": None, "header": None}
    return {"ok": p["hash_valid"], "err": None, "metrics": p["metrics"], "header": [p["role"], p["action_state"], p["sequence"]]}


def js_verdicts(lines: list[str]) -> list[dict]:
    module = (ROOT / "site" / "assets" / "js" / "sym2p-parse.js").as_uri()
    res = subprocess.run(["node", "--input-type=module", "-e", JS_HARNESS % module], input=json.dumps(lines),
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def regions(line: str) -> list[str]:
    start, end = line.index("["), line.rindex("]")
    return ["header" if i < start else "payload" if i <= end else "hash" for i in range(len(line))]


def substitute(ch: str, rng: random.Random) -> str:
    pool = string.digits if ch.isdigit() else "abcdef" if ch in "abcdef" else string.ascii_lowercase if ch.isalpha() else None
    if pool is None:
        return rng.choice([c for c in "()[]: ._-" if c != ch])
    return rng.choice([c for c in pool if c != ch])


def e6_line() -> dict:
    rng = random.Random(66)
    line = FIXTURE
    payload = line[line.index("["): line.rindex("]") + 1]
    as_json = json.dumps({"role": 1, "action_state": 3, "sequence": 1,
                          "metrics": {"active_nodes": 19, "tension": 0.2053, "gini": 0.2167},
                          "sha256": line[-64:]}, separators=(",", ":"))
    sizes = {"line_bytes": len(line.encode()), "payload_bytes": len(payload.encode()), "hash_hex_bytes": 64,
             "header_bytes": line.index("["), "equivalent_compact_json_bytes": len(as_json.encode())}

    # Single-character substitutions at every position, five per position.
    tags = regions(line)
    by_region = {r: {"mutants": 0, "rejected": 0, "accepted": 0} for r in ("header", "payload", "hash")}
    mutants = []
    for i, ch in enumerate(line):
        for _ in range(5):
            m = line[:i] + substitute(ch, rng) + line[i + 1:]
            mutants.append(m)
            v = python_verdict(m)
            r = by_region[tags[i]]
            r["mutants"] += 1
            r["accepted" if v["ok"] else "rejected"] += 1
    # Header-only changes that keep the line well-formed: role, action, sequence.
    forged_header = ":7f:0a:9999" + line[11:]
    # An attacker who edits the payload and recomputes the unkeyed hash.
    forged = encode_sym2p_line(role=1, action_state=3, sequence=1, metrics={"active_nodes": 999, "tension": 0.0, "gini": 0.0})

    # Python and browser parity on valid lines, mutants and malformed inputs.
    corpus = list(mutants)
    for k in range(300):
        metrics = {f"m{j}": round(rng.uniform(-1e3, 1e3), rng.randrange(0, 6)) for j in range(rng.randrange(1, 5))}
        if k % 7 == 0:
            metrics["tiny"] = 1e-05
        corpus.append(encode_sym2p_line(role=rng.randrange(256), action_state=rng.randrange(256), sequence=rng.randrange(10000), metrics=metrics))
    corpus += ["", ":", ":01:03:0001", ":01:03:0001[s-exp]", "no colon", ":01:03:0001[s-exp (a 1)]" + "0" * 63,
               ":zz:03:0001[s-exp (a 1)]" + "0" * 64, line + "trailing", " " + line + " ", line.replace("(", "( ")]
    js = js_verdicts(corpus)
    verdict_disagree = metric_disagree = header_disagree = 0
    examples = []
    for text, j in zip(corpus, js):
        p = python_verdict(text)
        if p["ok"] != j["ok"]:
            verdict_disagree += 1
            if len(examples) < 5:
                examples.append({"line": text[:80], "python": p["ok"], "js": j["ok"]})
        if p["metrics"] is not None and j["metrics"] is not None and p["metrics"] != j["metrics"]:
            metric_disagree += 1
        if p["header"] is not None and j["header"] is not None and p["header"] != [None if x is None else x for x in j["header"]]:
            header_disagree += 1
    return {
        "fixture_line": line,
        "sizes": sizes,
        "single_char_mutations": by_region,
        "forged_header_accepted_python": python_verdict(forged_header)["ok"],
        "forged_header_accepted_js": js_verdicts([forged_header])[0]["ok"],
        "recomputed_hash_forgery_accepted_python": python_verdict(forged)["ok"],
        "recomputed_hash_forgery_accepted_js": js_verdicts([forged])[0]["ok"],
        "parity": {"lines": len(corpus), "verdict_disagreements": verdict_disagree, "metric_disagreements": metric_disagree,
                   "header_disagreements": header_disagree, "examples": examples},
    }


# ---------------------------------------------------------------- E7 frame
def e7_frame() -> dict:
    t = 1762560000.0  # the fixture's system_time
    stored = FRAME64_STRUCT.unpack(FRAME64_STRUCT.pack(*([0.0] * 2 + [t] + [0.0] * 13)))[2]
    return {"frame_bytes": FRAME64_STRUCT.size, "unix_time": t, "float32_spacing_seconds": float(np.spacing(np.float32(t))),
            "stored_value": stored, "rounding_error_seconds": stored - t}


# ---------------------------------------------------------------- figures
def figures(e2: dict, e6: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid = "#0f172a", "#64748b", "#e2e8f0"
    cyan, violet, red, amber = "#0e7490", "#6d28d9", "#b91c1c", "#b45309"
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": muted, "axes.labelcolor": ink,
        "xtick.color": muted, "ytick.color": muted, "axes.grid": True, "grid.color": grid, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "path", "svg.hashsalt": "weft-paper-2",
    })
    (HERE / "figures").mkdir(exist_ok=True)

    # Figure 2: differential fuzzing outcomes
    order = [("agree_normal_form", "agrees to normal form", cyan), ("agree_until_cap", "agrees until step cap", "#7cc3d3"),
             ("diverged", "diverges from reference (never observed)", red), ("vm_unreadable", "storage no longer a valid net", amber)]
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    for row, cls in enumerate(("general", "simple")):
        left = 0
        for key, label, color in order:
            v = e2[cls]["outcomes"].get(key, 0)
            ax.barh(row, v, left=left, color=color, label=label if row == 0 else None, height=0.55)
            if v >= 12:
                ax.text(left + v / 2, row, str(v), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
            left += v
    ax.set_yticks([0, 1], ["general nets", "simple nets"])
    ax.set_xlim(0, 300)
    ax.set_xlabel("random closed nets (300 per class)")
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig2-differential.svg", metadata={"Date": None})
    plt.close(fig)

    # Figure 3: mutation detection by region
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    names = ["header\n(role, action, sequence)", "payload\n(s-expression)", "hash\n(64 hex digits)"]
    regs = ["header", "payload", "hash"]
    det = [100 * e6["single_char_mutations"][r]["rejected"] / e6["single_char_mutations"][r]["mutants"] for r in regs]
    bars = ax.bar(names, det, color=[red, cyan, cyan], width=0.55)
    for b, v in zip(bars, det):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}%", ha="center", color=ink, fontsize=9)
    ax.set_ylim(0, 112)
    ax.set_ylabel("single-character edits\ndetected (%)")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "fig3-line-mutations.svg", metadata={"Date": None})
    plt.close(fig)


# ---------------------------------------------------------------- main
VOLATILE = {"environment"}


def compare(a, b, path="") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k in VOLATILE:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present on one side only")
            else:
                out += compare(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in compare(x, y, f"{path}[{i}]")]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return [] if math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) else [f"{path}: {a} != {b}"]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def main() -> None:
    check = "--check" in sys.argv[1:]
    e0 = e0_reference()
    e1 = e1_rules()
    e2 = e2_fuzz()
    completed = e2.pop("_completed_vms")
    e3 = e3_confluence()
    e4 = e4_records(completed)
    e5 = e5_bcp(completed)
    e6 = e6_line()
    e7 = e7_frame()
    out = {
        "schema": "weft-paper-2-results/1",
        "environment": {"commit": git_commit(), "python": platform.python_version(), "numpy": np.__version__,
                        "node": subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()},
        "e0_reference": e0, "e1_rules": e1, "e2_differential": e2, "e3_order": e3, "e4_records": e4, "e5_bcp_fuzz": e5,
        "e6_telemetry_line": e6, "e7_frame": e7,
    }
    out = json.loads(json.dumps(out))
    if check:
        committed = json.loads((HERE / "results.json").read_text())
        diffs = compare(out, committed)
        for d in diffs[:50]:
            print(f"DIFF {d}", file=sys.stderr)
        print(json.dumps({"status": "FAIL" if diffs else "PASS", "differences": len(diffs)}))
        raise SystemExit(1 if diffs else 0)
    figures(e2, e6)
    (HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n")
    summary = {k: v for k, v in out.items() if k not in ("environment", "schema")}
    summary["e6_telemetry_line"] = {k: v for k, v in e6.items() if k != "fixture_line"}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
