#!/usr/bin/env python3
"""Reproduce the independent C3 review's differential and BCP boundary checks.

Recovered from the inline Python executed during the 2026-11-08 review, with
explicit repository/revision arguments added. This retained version has been
syntax checked but has not itself been rerun; the identical verification loops
were run inline and their outputs are recorded in ../review-ic.md.

Requires NumPy and the fixed source checkout's dependencies. Reads repositories
and allocates temporary in-process arrays; does not edit source or call GitHub.
"""

import argparse
import copy
import itertools
from pathlib import Path
import random
import struct
import subprocess
import sys
import types
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--fixed-root", type=Path, required=True)
    parser.add_argument("--fixed-ref", required=True)
    args = parser.parse_args()
    baseline_root = args.baseline_root.resolve()
    fixed_root = args.fixed_root.resolve()

    def git(root, *arguments):
        return subprocess.check_output(
            ["git", "-C", str(root), *arguments], text=True
        ).strip()

    baseline_sha = git(baseline_root, "rev-parse", args.baseline_ref + "^{commit}")
    fixed_sha = git(fixed_root, "rev-parse", args.fixed_ref + "^{commit}")
    if git(fixed_root, "rev-parse", "HEAD") != fixed_sha:
        raise SystemExit("Fixed checkout HEAD does not match --fixed-ref")
    if git(fixed_root, "status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Fixed checkout has tracked changes; use the exact reviewed source")
    print("Baseline:", baseline_sha)
    print("Fixed:", fixed_sha)

    sys.path.insert(0, str(fixed_root))
    import numpy as np
    from weft.runtime.ic import (
        FlatCombinatorVM,
        deserialize_graph_bcp,
        serialize_graph_bcp,
    )
    from weft.runtime.ic.bcp_codec import DEFAULT_MAX_BCP_CAPACITY

    src = subprocess.check_output(
        [
            "git", "-C", str(baseline_root), "show",
            baseline_sha + ":weft/runtime/ic/ic_vm.py",
        ],
        text=True,
    )
    old = types.ModuleType("weft.runtime.ic._review_old")
    exec(compile(src, "pre-repair-ic_vm.py", "exec"), old.__dict__)

    def state(vm):
        return (
            vm.tags.tobytes(), vm.aux_tags.tobytes(), vm.ports.tobytes(),
            vm.next_alloc, vm.reductions, copy.deepcopy(vm.trace_log),
            vm._initial_bcp,
        )

    success = failure = 0
    for ta, tb, la, lb, capacity, (tension, budget) in itertools.product(
        range(6), range(6), [0, 7], [0, 7], range(2, 9),
        [(22.0, 100.0), (92.0, 100.0), (22.0, 0.0)],
    ):
        vm = FlatCombinatorVM(capacity)
        ref = old.FlatCombinatorVM(capacity)
        for current in (vm, ref):
            a = current.alloc_node(ta, aux_tag=la)
            b = current.alloc_node(tb, aux_tag=lb)
            current.connect_ports(a, 0, b, 0)
        before = state(vm)
        try:
            result = vm.interact(a, b, tension=tension, metabolic_budget=budget)
        except MemoryError:
            assert state(vm) == before, (ta, tb, la, lb, capacity, tension, budget)
            try:
                ref.interact(a, b, tension=tension, metabolic_budget=budget)
            except MemoryError:
                pass
            else:
                raise AssertionError("repair rejected formerly successful capacity")
            failure += 1
        else:
            assert result == ref.interact(a, b, tension=tension, metabolic_budget=budget)
            assert state(vm)[:5] == state(ref)[:5]
            assert vm._initial_bcp == ref._initial_bcp
            if ta != 3 and tb != 3:
                assert vm.trace_log == ref.trace_log
            success += 1
    print(
        "Exhaustive ordered tag/label/capacity/valve-policy matrix:", success,
        "successful reductions preserve prior graph/allocator semantics;", failure,
        "arena failures preserve all state",
    )

    vm = FlatCombinatorVM(2)
    vm.tags[:] = vm.CON
    vm.next_alloc = 0
    before = state(vm)
    try:
        vm.alloc_node(vm.CON)
    except MemoryError:
        assert state(vm) == before
    else:
        raise AssertionError("allocation should fail")
    print("Direct exhausted allocator preserves a stale next_alloc cursor")

    rng = random.Random(179)
    for _ in range(500):
        capacity = rng.randrange(64)
        slots = sorted(rng.sample(range(capacity), rng.randrange(capacity + 1)))
        records = []
        for slot in slots:
            records.append((
                slot, rng.randrange(6), 0, rng.randrange(-32768, 32768),
                *(rng.randrange(-1, capacity) for _ in range(3)),
            ))
        blob = struct.pack("<4sBBHI", b"WEFT", 1, 0, len(records), capacity)
        blob += b"".join(struct.pack("<IBBhiii", *record) for record in records)
        assert serialize_graph_bcp(deserialize_graph_bcp(blob)) == blob
    print("500 independently packed randomized sparse BCP packets round-trip byte-for-byte")

    blob = struct.pack("<4sBBHI", b"WEFT", 1, 0, 0, DEFAULT_MAX_BCP_CAPACITY)
    vm = deserialize_graph_bcp(blob)
    assert vm.capacity == DEFAULT_MAX_BCP_CAPACITY
    assert serialize_graph_bcp(vm) == blob
    with patch("weft.runtime.ic.ic_vm.FlatCombinatorVM") as arena:
        try:
            deserialize_graph_bcp(struct.pack(
                "<4sBBHI", b"WEFT", 1, 0, 0, DEFAULT_MAX_BCP_CAPACITY + 1,
            ))
        except ValueError:
            pass
        else:
            raise AssertionError("default limit not enforced")
        arena.assert_not_called()
    for limit in [-1, 1.5, None, "4", float("inf")]:
        try:
            deserialize_graph_bcp(
                struct.pack("<4sBBHI", b"WEFT", 1, 0, 0, 0), max_capacity=limit,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid limit accepted", limit))
    vm = FlatCombinatorVM(65535)
    vm.tags[:] = vm.CON
    blob = serialize_graph_bcp(vm)
    assert serialize_graph_bcp(deserialize_graph_bcp(blob)) == blob
    print("Default limit boundary, invalid limits, and maximum uint16 record count pass")


if __name__ == "__main__":
    main()
