# Independent C3 bounded repair review

**Verdict: ACCEPT** for commit `a9b798bd6254f1e4ef8d344b9ad183a9fcc0be73` in `/workspace/weft-ic-repair`, reviewed 2026-11-08. No blocking regression found within this change's documented storage and arena-exhaustion scope. This is an independent source/test review record; no GitHub review, merge or deployment was performed.

Issue: [#43](https://github.com/Moissanite-Labs/weft/issues/43). Follow-on topology/reference-semantics work: [#52](https://github.com/Moissanite-Labs/weft/issues/52). This repair does not close either issue's remaining semantic/replay/metering questions.

## Source review

Read the complete diff and all current C3 implementation, exports and tests. The repair preserves the graph's encoded capacity, including zero, full and sparse arenas; it rejects malformed flags, node records, slot ordering and port ranges before arena allocation. The 1,048,576-slot default allocation ceiling bounds the NumPy arrays to 15 MiB. The uint16 record count independently bounds record parsing. Explicit caller override is documented as a resource policy; it does not alter the wire capacity field.

The validator is shared by encoding and decoding. Canonical ordering, valid tags, zero reserved bytes and the signed-port sentinel are consistently enforced. Empty and maximum-record packets remain representable. Unknown flags/tags, out-of-range references and duplicate/unsorted slots that were previously silently accepted now fail intentionally. In-range references to inactive slots remain supported for the existing open-interface examples.

All allocating branches have the required preflight before initial-snapshot capture, graph mutation, cursor mutation or trace append: erasure needs two free slots, commutation four, and valve excision one. Passing valves and annihilation allocate none. This preserves the previous peak requirement and successful allocation order rather than introducing reuse of the active pair. The direct allocator now preserves its cursor when the arena is exhausted, including a cursor that must scan live slots before failure.

Valve validation converts inputs to floats, rejects NaN and infinities without mutation, retains the existing finite predicate and records both inputs without tension rounding. No new cost/debit policy is introduced. A positive budget remains a caller-supplied permission signal. The revised documentation correctly narrows confluence and execution-commitment claims.

## Verification

Environment: Linux x86_64, Python 3.12.14, NumPy 2.3.5, interpreter `/workspace/.venvs/weft-audit/bin/python`. Worktree HEAD matched the reviewed SHA; the worktree was clean before and after review. `git diff --check a9b798b^ a9b798b` passed.

| Check | Result |
|---|---|
| `python -m unittest discover -s weft/runtime/ic -p 'test_*.py' -v` | All 15 tests passed |
| `python -m unittest discover -s weft/runtime/invariants -p 'test_*.py' -v` | All 4 tests passed, including C-header conformance |
| `python weft/runtime/core/weft_ic_vm.py` | PASS, 3 reductions, 7 remaining active nodes, 152-byte final BCP |
| Differential matrix against the parent commit's VM | 2,096 successful reductions preserved operation, arrays, allocator cursor, reduction count and initial BCP; non-valve traces also identical |
| Same matrix, arena exhaustion | 928 failures preserved arrays, cursor, reduction count, trace and initial BCP; every case also exhausted the predecessor |
| Independently packed random BCP fixtures | 500 sparse packets round-tripped byte-for-byte |
| Decode policy boundaries | Default maximum accepted; maximum+1 rejected before construction; invalid limit types/negative values rejected |
| Maximum uint16 record count | 65,535 active records round-tripped byte-for-byte |
| Direct exhausted allocator with stale cursor | All state preserved |

The differential matrix enumerated ordered tags `0..5` × `0..5`, each label in `{0,7}`, capacities `2..8`, and `(tension,budget)` in `{(22,100),(92,100),(22,0)}`. Each VM contained the two nodes connected at their principal ports, with other ports detached. The predecessor class was loaded directly from `git show a9b798b^:weft/runtime/ic/ic_vm.py`; both classes used the reviewed codec so the comparison isolated reduction/allocator behavior. Complete array bytes, cursor, counters, deep-copied log and initial BCP were captured before each call. The added VLV trace fields were checked separately by the committed boundary tests.

The random BCP check used `random.Random(179)`, capacities in `0..63`, randomly selected sorted distinct slots, tags in `0..5`, full signed-int16 labels, and each port in `[-1,capacity)`. Packets were built directly using `<4sBBHI` and `<IBBhiii`, not the production serializer. The resource-limit check patched the VM constructor to verify that rejection happened before allocation. The 65,535-record boundary used an arena filled with CON tags and detached ports.

Core wrapper execution commitment: `0x03efabbd63c607e5d9db95c05fd2df6bc3f2284947189397018757efb61ae0de`.

## Remaining limits

Acceptance is limited to canonical active-node storage and single-threaded arena-capacity failure behavior. It does not establish transactionality under arbitrary process OOM, exceptions caused by direct mutation of internal arrays, or concurrent allocation. It does not establish graph validity: peer-port identity, reciprocal links, valid principal pairs, multi-edge handling and the extension rule set remain [#52](https://github.com/Moissanite-Labs/weft/issues/52).

BCP is still a snapshot rather than a continuation checkpoint; it excludes allocator history, reduction count and trace. A trace digest still binds recorded bytes without proving rule validity or execution. The changed valve log affects commitments for valve traces, as expected from recording the missing budget and unrounded tension inputs. No MPS, Mac hardware, GPU performance or formal confluence result follows from these CPU checks.

## Retained reproducer

The original verification was executed inline rather than saved as a script. Its verification loops have now been recovered into [reproducers/ic_review.py](reproducers/ic_review.py), with explicit baseline/fixed checkout and revision arguments added. The retained file was syntax checked with `ast.parse`; it has not been rerun. The reported results above are from the original inline execution, not a claimed later run.

Run without Python's `-O` option, because checks use assertions. The baseline source is loaded with `git show`; the fixed checkout must be clean for tracked files and have the exact requested HEAD. Both VM classes intentionally use the fixed codec and invariant imports, isolating reducer/allocator behavior. The repositories can be the same checkout because baseline source is read directly from Git history.

```bash
/workspace/.venvs/weft-audit/bin/python \
  /workspace/weft-corpus/docs/program/audit/reproducers/ic_review.py \
  --baseline-root /workspace/weft-ic-repair \
  --baseline-ref 'a9b798bd6254f1e4ef8d344b9ad183a9fcc0be73^' \
  --fixed-root /workspace/weft-ic-repair \
  --fixed-ref a9b798bd6254f1e4ef8d344b9ad183a9fcc0be73
```

The two root paths are configurable for another machine. Keep the revisions fixed to reproduce this review; create a clean detached checkout of the reviewed commit if the active repair branch has moved. Expected matrix totals are 2,096 successful transitions and 928 preserved failures, followed by the 500-fixture and boundary-check pass messages. The fixed source and NumPy are required; no device-specific backend, network call or repository mutation is used by the checks.
