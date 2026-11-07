# Google Chrome Source Sessions & Interactive Sandbox Widgets

This directory contains the complete, losslessly extracted, syntax-repaired contents pulled over the Chrome DevTools Protocol (`ws://127.0.0.1:9222`) from the Google Chrome sessions on Desktops 8 and 9.

## 1. Full Session Transcripts (144 Extracted DOM Turns + 3 Pre-Window Turns, 191 Repaired Fenced Code Blocks)

- `thread1-splicers-genesis-90133B.md`: Desktop 8 early share snapshot (`90133B89987F37BD41A1CA9E7430CA22`, 29 turns, 34 repaired fenced code blocks rejoined from 40 raw `<pre>` DOM nodes). Covers the genesis thread (`explain how fallen splicers upgrade tech`, matching `Moissanite-Labs/compass` Discussion #5 through the multi-node Mac harness and `SCM_RIGHTS` descriptor passing in Turns 27–28).
- Pre-window bridge (3 turns between `90133B` Turn 28 and `84ADC9` Turn 0): The live Desktop 8 DOM retained the latest 72 turns of a 104-turn thread (`29 + 3 + 72 = 104`). Those 3 intermediate turns are preserved in [`weft/README.md`](../README.md) Sections 15–24, [`weft/more.md`](../more.md), and [`weft/mac.md`](../mac.md).
- `thread1-weft-main-84ADC9.md`: Desktop 8 live tab (`84ADC92A5A891CD72A5EFCAA77A783CA`, 72 turns, 110 repaired fenced code blocks). Covers the main Syntactic Weft thread from `almalga.md` through `whitepaper.md`.
- `thread2-design-main-6C083A.md`: Desktop 9 live tab (`6C083A8879AFC48D153AA8AE26AA7A35`, 43 turns, 47 repaired fenced code blocks rejoined from 51 raw `<pre>` DOM nodes). Covers the reactive typography, barycentric design space, and WebGPU spatial computing session (`design/*.md`).
- `missing-turns-supplement.md`: Consolidates 31 turns (50 fenced code blocks) from the 144 extracted turns above: 12 turns that were not copied into the 53 standalone `.md` files plus 19 early reference turns from `90133B` and `6C083A`.

## 2. Extracted Cross-Origin Sandboxed Simulation Apps (`scf.usercontent.goog`)

Historical filenames are retained for link and manifest stability, while each entry below states the actual interactive simulation implemented in the `.html` and `.jsx` source (#26):

- `widgets/01-sdf-laya-kinetic-typography.html` & `.jsx`: **01: Aywa Barycentric Design System Explorer** (`6C083A` Turn 6): Interactive barycentric style-coordinate explorer interpolating typography, border rounding, spatial density, and palette tokens across reference presets.
- `widgets/02-mind-palace-spatial-memory.html` & `.jsx`: **02: Spatial Compute Canvas & Node Topology** (`6C083A` Turn 19): Infinite-zoom spatial compute canvas and multi-layer node architecture inspector.
- `widgets/03-morphogenetic-bioelectric-field.html` & `.jsx`: **03: Weft Sovereign Matrix & Telemetry Monitor** (`84ADC9` Turn 10): Sovereign Weft telemetry matrix monitoring metabolic tension, invariant radius, and active node lanes.
- `widgets/04-neural-cellular-automata.html` & `.jsx`: **04: Morphogenetic Grid & Cellular Automata Demo** (`84ADC9` Turn 25): Interactive cellular-automata regeneration and damage-recovery grid.
- `widgets/05-interaction-combinator-net.html` & `.jsx`: **05: Splicer Organism & Mitotic Lineage Simulator** (`84ADC9` Turn 40): Splicer mitotic lineage and metabolic valve simulator visualizing speculative A/B child lineages and hippocampal novelty.
