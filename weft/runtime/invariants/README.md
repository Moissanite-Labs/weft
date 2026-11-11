# Weft Invariants Gate (`weft/runtime/invariants`)

Codebase **C2** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I3** (Invariant Gate).

## Purpose and boundary

Provide pure, zero-side-effect safety predicates and canonical conformance vectors shared across the Python runtime (`plasm`, `ic`, `gateway`) and the bare-metal C11 header (`weft_invariants.h`).

- **Owns**:
  - `invariants.py`: baseline-relative Frobenius distance gate (`||W_cand - W_base||_F <= r_invariant`), metabolic budget precondition (`budget >= cost > 0`), organizational/cellular tension bound (`0 <= tension <= 85.0`), and the 15% upstream / 85% weaver metabolic valve split.
  - `vectors.json`: cross-language conformance test vectors.
  - `weft_invariants.h`: bare-metal C11 header repaired from `weft/terrafab-calc.md:50-100` (fixes M1 compared-sizes trap and M6 budget pre-check order). The weight gate also keeps a `float32` budget moving when the step is smaller than one unit in the last place, compares the radius in `double` before any `float` cast, and can reject a bit change on indices marked by an optional `locked_mask`. The 7-argument `weft_verify_weight_update_safety` entry point is unchanged.
  - `test_invariants.py`: Python verification against all 12 vectors in `vectors.json`, plus a 256-vector C11-vs-Python differential check.
  - `test_invariants_c.c`: compiled C11 checks. It does not read `vectors.json`. Cases 1 to 7 cover the shared weight, tension, and royalty vectors. Cases 8 to 10 cover the budget step, the radius boundary, and `locked_mask`. A second mode reads a binary vector file from the Python test.
- **Dependencies**: Python 3 standard library (`math`, `json`, `pathlib`), optional fast-path for `torch.Tensor`, and a standard C11 compiler (`cc`/`clang`/`gcc`) for header verification.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/invariants -p 'test_*.py'
```
