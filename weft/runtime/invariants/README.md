# Weft Invariants Gate (`weft/runtime/invariants`)

Codebase **C2** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I3** (Invariant Gate).

## Purpose and boundary

Provide pure, zero-side-effect safety predicates and canonical conformance vectors shared across the Python runtime (`plasm`, `ic`, `gateway`) and the bare-metal C11 header (`weft_invariants.h`).

- **Owns**:
  - `invariants.py`: baseline-relative Frobenius distance gate (`||W_cand - W_base||_F <= r_invariant`), metabolic budget precondition (`budget >= cost > 0`), organizational/cellular tension bound (`0 <= tension <= 85.0`), and the 15% upstream / 85% weaver metabolic valve split.
  - `vectors.json`: cross-language conformance test vectors.
  - `weft_invariants.h`: bare-metal C11 header repaired from `weft/terrafab-calc.md:50-100` (fixes M1 compared-sizes trap and M6 budget pre-check order).
  - `test_invariants.py`: Python verification against all 12 vectors in `vectors.json`.
  - `test_invariants_c.c`: compiled C11 checks. It does not read `vectors.json`; it hard-codes 10 of the cases (5 weight-update, 4 tension, 1 royalty), so a change to the JSON must be copied here by hand.
- **Dependencies**: Python 3 standard library (`math`, `json`, `pathlib`), optional fast-path for `torch.Tensor`, and a standard C11 compiler (`cc`/`clang`/`gcc`) for header verification.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/invariants -p 'test_*.py'
```
