# ML Weft — Modular Aywa Living Loom (`weft/runtime/aywa` + `site/`)

Drop-in ES module suite, WebGPU (`aywa_loom.wgsl`) + Canvas2D living loom, shared 12-case
`WEFT-INVARIANTS/2.0` JSON corpus, and `node --test` verification suite designed to merge
cleanly into [`Moissanite-Labs/weft`](https://github.com/Moissanite-Labs/weft) and [`w3ft.org`](https://www.w3ft.org/)
with zero collisions against existing files.

**Mandate:** *No token. No sale. Nothing on-chain.* Code: `Apache-2.0` · Docs: `CC BY 4.0`.
Machine-authored assistance disclosed per [`Moissanite-Labs/weft`](https://github.com/Moissanite-Labs/weft), [`Moissanite-Labs/abios`](https://github.com/Moissanite-Labs/abios), [`Moissanite-Labs/weft-eido`](https://github.com/Moissanite-Labs/weft-eido), [`Moissanite-Labs/exo`](https://github.com/Moissanite-Labs/exo), and [`Foundation-0`](https://github.com/Foundation-0) contributing rules.

## Drop-In Integration (`Moissanite-Labs/weft`)

```bash
# 1. Copy `weft/` and `site/` directly into a clean Moissanite-Labs/weft checkout:
cp -R weft/* /path/to/weft/weft/
cp -R site/* /path/to/weft/site/

# 2. Run the standard w3ft.org browser-module CI test command:
cd /path/to/weft
node --test weft/runtime/aywa/test_*.mjs

# 3. Verify bundle integrity offline:
sha256sum -c SHA256SUMS

# 4. Commit with required DCO sign-off:
git checkout -b feat/aywa-living-loom-v2
git add weft/runtime/invariants/vectors_v2_12case.json weft/runtime/aywa/ site/assets/js/ site/loom/
git commit -s -m "aywa: add modular Living Loom, 12-case invariants v2, and node:test suite"
```

## Module Map & Honest Evidence Register (Issue #42 & #45)

| Path | Subsystem | Evidence Status |
| :--- | :--- | :--- |
| `site/assets/js/aywa-sha256.js` | RFC 6234 SHA-256 + IEEE-754 `float32`/`float16` bit ops | `runs · tested` (verified against NIST `"abc"` + `w3ft.org` 131B packet) |
| `site/assets/js/aywa-invariant-v2.js` | `WEFT-INVARIANTS/2.0` (all 12 vectors, Zeno `nextafterf`, Neumaier `binary64`) | `runs · tested` (100,000-step sub-ULP + `N=65,536` arena checked) |
| `site/assets/js/aywa-continuum-plasm.js` | `540,688 B` `StratifiedMemoryArena` + Orthogonal Mitosis + Exo `C/Fe` gate | `runs · tested` (`16x16` live operator, `0%` locked-subspace forgetting) |
| `site/assets/js/aywa-ic-confluent.js` | Lafont (`γ, δ, ε`) reducer + `Mixture-of-Depths` `ε`-pruning | `runs · tested` (50-schedule randomized diamond confluence verified) |
| `site/assets/js/aywa-wire-sym2p-sy2l.js` | Live `ABIOS SYM-2P` S-expr + `64 B` `SY2L` frame + `packCellRecords` | `runs · tested` (live measured browser state, never unlabeled fixtures) |
| `site/assets/js/aywa-eido-mixer.js` | Barycentric simplex + circular `atan2` hue mean + `#45` provenance tags | `runs · tested` (`0.95` red + `0.05` red -> `0.00` red verified) |
| `weft/runtime/aywa/aywa_loom.wgsl` | WebGPU instanced warp-filament shader (paired with Canvas2D fallback) | `shader source` (Canvas2D fallback executes everywhere) |
| `site/loom/index.html` | Native `<script type="module">` mount for `w3ft.org/loom/` | `runs · tested` |
