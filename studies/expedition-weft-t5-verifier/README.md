# `WEFT-T5`: Clean-Room Lafont Interaction-Combinator & BCP v2 Trace-Replay Verifier (`AUDIT-033`)

**Status:** Independently **`VERIFIED`** (`AUDIT-033` | Oracle: `exact` + `anchor` | Novelty: `N2`)  
**Zero Edits to Existing Code:** Self-contained study under `studies/expedition-weft-t5-verifier/`

---

## Summary

Closes the open `WEFT-T5` independent replay-verifier gap (`Moissanite-Labs/siliconcordat#16`) by providing a **zero-shared-code, zero-NumPy, pure Python 3 stdlib** clean-room verifier for `weft/runtime/ic` (Codebase `C3`, BCP v2 `<4sBBHI` + `<IBBhiii` wire format, `WEFT-IC-EXEC-V2:` SHA-256 execution commitments).

### Key Verified Results
1. **True Dual-Checker Independence (Zero Self-Replay Tautology):**
   - `weft/runtime/ic/ic_vm.py::verify_execution` replays traces through `FlatCombinatorVM` itself (shared NumPy arrays & code).
   - `weft_t5_combinator_verifier.py` uses an independent port-involution dictionary graph `(node, port) <-> (peer_node, peer_port)` with **zero `numpy` imports**, **zero `weft` imports**, exact `Fraction` rational valve gating (`TENSION_MAX = Fraction(85, 1)`), rolling 64-bit FNV-1a trajectory hashing, and strictly distinct `alpha_skeleton_sha256`.
2. **Exact Topological Open-Boundary Conservation Law:**
   $$\Delta(\text{open\_boundary\_ports}) = \begin{cases} +1 & \text{on } \mathrm{VLV\_EXCISE\_TO\_FRC}, \\ -2 \cdot k_{\text{free}} & \text{on all Lafont rules } (\mathrm{CON}, \mathrm{DUP}, \mathrm{SUP}, \mathrm{ERA}) \text{ and } \mathrm{VLV\_PASS}, \end{cases}$$
   machine-checked at every reduction step alongside full port-graph reciprocity & arity invariants.
3. **100% Byte-Exact Cross-Oracle Differential Parity:**
   - `12/12` named traces (`run_combinator_self_test()`, all `6` `#66` loop-backs, `#52` crossed vs. parallel double-wires, `VLV` exact `85.0`/`85.000001`/`0.0` boundaries) + `50/50` seeded random multi-edge closed nets with loops (`263` steps; independently verified on `30` additional unseen-seed nets / `249` steps) match `weft.runtime.ic` byte-for-byte on `final_bcp` and `trace_commitment_sha256`.
4. **4 Live Unreported R1–R3 Bypasses in `weft/runtime/ic/` Reproduced & Closed (`W-01..W-04`):**
   - **`W-01` (`ic_vm.py::verify_execution:485`):** `bool` (`step=True, a=False, b=True`) and `float` (`step=1.0, a=0.9, b=1.9`) pass with `status="PASS"`.
   - **`W-02` (`ic_vm.py::verify_execution_record:544-546`):** Forged metadata (`reductions_executed=999999`, `active_nodes_remaining=42`, `capacity=1`, `bcp_version=99`, `status="FAIL"`) passes with `status="PASS"`.
   - **`W-03` (`ic_vm.py::FlatCombinatorVM.interact:300-335`):** `VLV-VLV` active-pair excision depends on argument order `(a, b)` vs. `(b, a)` (producing distinct final BCP graphs, breaking unordered active-pair symmetry $\{a, b\} = \{b, a\}$), and `tension=True, metabolic_budget=True` returns `VLV_PASS`.
   - **`W-04` (`bcp_codec.py::deserialize_graph_bcp:195`):** `max_capacity=False` silently accepted as capacity `0`.
5. **100.0% R5 Mutation Kill Rate:** `45/45` refusal-site & boundary mutants in `weft_t5_combinator_verifier.py` are killed (`0` survivors) by `test_weft_t5_r5.py` under `python3 -I -O -B`.

---

## Reproduction

```bash
cd studies/expedition-weft-t5-verifier
for m in "-I -B" "-I -O -B" "-I -B -W error" "-I -O -B -W error"; do
  python3 $m weft_t5_combinator_verifier.py --json | sha256sum
  python3 $m weft_t5_cross_oracle_audit.py --json | sha256sum
done
python3 -I -O -B -W error test_weft_t5_r5.py
```
