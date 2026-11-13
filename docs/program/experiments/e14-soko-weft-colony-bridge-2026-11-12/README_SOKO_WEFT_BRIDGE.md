# `ahrazzle/soko` -> `Moissanite-Labs/weft` Optimization & Exact-Frontier Bridge (`Experiment E14`)

Drop-in reproducible experiment and runtime reference porting four exact-frontier optimization & refutation primitives from [`ahrazzle/soko`](https://github.com/ahrazzle/soko) into [`Moissanite-Labs/weft`](https://github.com/Moissanite-Labs/weft) (`docs/program/experiments/e14-soko-weft-colony-bridge-2026-11-12/`).

**Mandate:** *No token. No sale. Nothing on-chain.* Code: `Apache-2.0` · Docs: `CC BY 4.0`.
**Disclosure:** `AI-assisted research & execution via Gemini task agent per CONTRIBUTING.md.`

## Quick Verification & DCO Commit

```bash
sha256sum -c SHA256SUMS
python3 -B docs/program/experiments/e14-soko-weft-colony-bridge-2026-11-12/e14_soko_weft_colony_assembler.py --selftest

# Commit into a Moissanite-Labs/weft checkout with required DCO sign-off:
git checkout -b record/e14-soko-weft-colony-bridge-2026-11-12
git add docs/program/experiments/e14-soko-weft-colony-bridge-2026-11-12/
git commit -s -m "e14: port soko gauge canonization, Dinic min-cut mitosis, non-stuttering nogoods, and rational certificates"
```
