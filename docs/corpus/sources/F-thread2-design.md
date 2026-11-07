<!--
Corpus map source report F. Scope: weft/browser-sources/thread2-design-main-6C083A.md.
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory F — `weft/browser-sources/thread2-design-main-6C083A.md`

Scope: one file, read in full (lines 1–5135), plus context file `weft/browser-sources/README.md` and the five extracted widgets (`weft/browser-sources/widgets/*.jsx|*.html`). I also compared the transcript code with `weft/runtime/aywa/*` and `docs/*`.
All `L####` references point to `thread2-design-main-6C083A.md` unless another file is named.

---

## 1. Per-file summary

### 1.1 `weft/browser-sources/thread2-design-main-6C083A.md` — 5135 lines, ~315 KB

- **Genre:** a scraped dialogue transcript, Desktop 9, Chrome tab `6C083A…`. The assistant is Google Search "AI Mode": every turn ends with the Google feedback boilerplate (e.g. L48), and the failed turns read "Something went wrong and an AI response wasn't generated" (L1968 Turn 25, L2308 Turn 28). There are 43 turns (Turn 0–Turn 42) and **47 fenced code blocks (94 fences)**. README L9 says "51 `<pre>` blocks", so 4 blocks were lost or merged in the conversion.
- **Main topics:** procedural graphics (SDFs, shaders, GPU SIMD); "Laya" as an in-browser "System 1" decision model; reading-behaviour reward UI; the anatomical "mind palace" metaphor; Neural Cellular Automata (NCA); the "post-app" Zero-UI vision; fusion with the Weft `ahraz.md` Mac harness; static hosting; then an evolving **"Synbios" serverless org-dashboard**. The dashboard is GitHub Actions harvest → SYM-2P line in `telemetry.jsonl` → JS parser → WebGPU uniform buffer → WGSL SDF grid. It later grows personalization "aesthetic slices", a Barycentric mixer, OAuth device-flow write-back, live polling, procedural noise, a Gini coefficient, a GPU bitmap font, a "watermark" background, and deploy workflows.
- **Interactive widgets:** four were emitted inside the conversation, at L121 (Turn 2), L218 (Turn 3), L535 (Turn 8) and L610 (Turn 9). Each is marked only by "AI-generated. Don't enter sensitive personal info." **None of their source code is in the transcript.** The code lives only in the extracted `widgets/0[1-4]-*`; widget 05 comes from a different thread.
- **Individual design files:** the distinctive strings of each turn reappear in `weft/design/*.md`, so those are per-turn copies of this thread (see §2 note B).

#### 1.1.1 How the design evolved (which code is the latest)

| Phase | Turns (lines) | What happens | Code state |
|---|---|---|---|
| A. Concepts and widgets | T0–T13 (L6–L819) | SVG/shaders/GPU basics (T0–1); procedural UI sandbox widget (T2); SDF formulas and CSG widget (T3); Laya as System 1 (T4–5); reading-reward shader (T5); learning stack (T6); body as a mind palace (T7); "biology simulation" widget (T8); NCA widget (T9); NCA prior art (T10); widget tech stack (T11); post-app Zero-UI (T12); Inkling 2 / Tinker (T13) | GLSL/JS pseudocode only |
| B. Fusion with Weft harness | T14 (L823–L881) | Maps the `weft_singularity_core.py` classes (from `ahraz.md`) onto the mind palace and generative UI; on-chain "alignment settlement" | prose table only |
| C. Boundaries, hosting, reality check | T15–T18 (L885–L1137) | DOM as "prison"; GitHub Pages hosting; "unbound" abios/synbios; **T18 retracts the sci-fi claims** (L1085–L1097) | directory tree |
| D. Synbios dashboard v1 | T19–T27 (L1141–L2298) | SYM-2P line → WGSL (T19); `build-engine.yml` (T20); `synbios-evolution.yml` ingest (T21); `dashboard_layout.wgsl` fragment-only (T22); `main.js` `SynbiosDashboardEngine` (T23); unified vertex+fragment WGSL (T24); `index.html` anchor (T26); field recap (T27) | uniform **16 B**: `active_nodes, org_tension, system_time, _pad` |
| E. Advanced org metrics | T28–T29 (L2302–L2492) | The user lists 5 metrics (T28 fails); T29 maps owner ratio, labels, Gini concentration, resonance, capture | uniform **32 B** |
| F. Personal aesthetics | T30–T33 (L2496–L3277) | Style vector from devs' repos (T30); shareable "slices" (T31); `AestheticMixer` normalization (T32, linear-hue bug); **T33 first self-contained `index.html`** (inline WGSL, gene deck, sin/cos hue fix) | uniform **48 B** (adds rounding/density/hue/contrast) |
| G. Write-back and live sync | T34–T36 (L3281–L3661) | `SynbiosGitWriteWorker` (T34); `SynbiosEdgeOrchestrator` OAuth device flow via corsproxy (T35); `LiveEcosystemSynchronizer` cache-busted polling with hash-change detection (T36) | JS classes, not merged into any HTML |
| H. Noise and Gini | T37–T38 (L3665–L3818) | `randomNoise2D` WGSL snippet; Python Gini plus SYM-2P line | snippets |
| I. Procedural text "monoliths" | T39–T42 (L3822–L5135) | T39 5×7 bitmask digit font page; T40 harvester `synbios_harvest.py` plus tri-module page (font + mix deck + "cryptographic watermark"); **T41 "Unbound Master Monolith"** (ASCII labels in a storage buffer + device-flow panel); T42 `deploy.yml` plus a broken 16-char patch | uniform back to **32 B** with different fields (`gini_concentration` replaces `owner_ratio`; T40+ drops `label_state`); T41 adds `@binding(1)` storage |

**Latest variant of each artifact in this transcript:**
- **Full page:** Turn 41, L4585–L4989 (`SovereignSystemCore`). It is the last complete HTML; T42 only patches it, and the patch is broken.
- **WGSL:** T41 inline shader, plus the T42 16-char delta at L5072–L5103 (invalid WGSL).
- **Harvester:** T40 `synbios_harvest.py`, L4174–L4236.
- **Workflows:** ingest T21 L1381–L1439 plus the T29 step at L2340–L2381; deploy T42 L5024–L5064, which supersedes build-engine T20 L1297–L1339.
- **Mixer:** the sin/cos version in T33 L3130–L3153, reused in T40 L4456–L4468 and T41 L4841–L4851. The T32 `AestheticMixer` (L2824–L2878) is the older, buggy one.
- **Standalone `main.js` and live sync:** T23 L1605–L1810 and T36 L3575–L3645. T33–T41 superseded them with inline code, but **T41 dropped data fetching entirely** (regression, see §6).

**Regressions over the evolution:**
- T41 claims "no mock arrays and no placeholders" (L4579, L4999), but the telemetry is driven by sliders, while labels, profiles and the client_id are hard-coded.
- The SYM-2P fetch, hash check and write-back commit (T34/T35 `pushGeneticMutation`) are absent from T41. T41 only authenticates.

#### 1.1.2 Transcript vs extracted widget files

The transcript holds no widget source. I compared the prose descriptions with the components in `widgets/*.jsx`. Each `.html` is the captured sandbox DOM, carries a Google CSP meta and imports React/Radix from `widgetlibs.static.usercontent.goog`, so it is not self-contained offline. Each `.html` contains the same named component as its `.jsx`, and every file is byte-identical to its copy in `docs/widgets/`.

| File | README.md claim (L14–L18) | Actual component in .jsx | Transcript turn it really matches | Prose-vs-code discrepancies |
|---|---|---|---|---|
| `01-sdf-laya-kinetic-typography` | "SDF + Laya kinetic typography emotion-reactive text simulator", Turn 2 | `ShaderSandbox`: Canvas2D, 48×27 cell grid, "Radial wave" `sin(dist*freq - t)` or "Matrix grid" `sin*cos`; speed and frequency sliders; play/pause | **Turn 2** "Procedural UI & Animation Shader Sandbox" (L119) | No SDF, no Laya, no typography. Not a GPU shader (CPU canvas loop). Spatial frequency is labelled "Hz". **README title wrong.** |
| `02-mind-palace-spatial-memory` | "Spatial Mind Palace semantic graph and memory locus navigator", Turn 3 | `SdfVisualizer`: SVG dot grid sampling `sdfCircle`/`sdfBox`; CSG union/subtraction/intersection/`smin` (cubic, k/6); separation and k sliders; pointer probe showing `d = …px` | **Turn 3** SDF visualization (L216) | Matches the prose well. The isoline code is dead (`isolineLevels.map(() => null)`). **README title wrong:** there is no mind palace or graph. |
| `03-morphogenetic-bioelectric-field` | "Levin-inspired morphogenetic bio-electric voltage gradient tissue simulator", Turn 8 | `MindPalaceSimulation`: Canvas2D with 5 nodes (Telemetry, System 1, System 2, Uniforms, GPU Shaders), gradient edges, particles; sliders "System 1 Reflexes" / "System 2 Load"; fake KPIs computed from slider values (`synergyScore`, `latencyMs`, `gpuLoadPercent`) | **Turn 8** "Live Procedural Biology Simulation" (L529) | Prose claims "a single GPU fragment shader … SDFs", "two circle SDFs merged with smin" and sine-wave nerves (L531, L541–L555). The code has no shader, SDF or smin. `ctx.font = "medium 12px sans-serif"` is an invalid font string. **README title wrong:** nothing bio-electric or Levin-related. |
| `04-neural-cellular-automata` | "Self-healing NCA damage-and-regeneration grid", Turn 9 | `NCASimulator`: 56×32 grid, 8 channels (RGBA + 4 hidden) in `Float32Array`; hand-written update that pulls every cell toward a **hard-coded global `TARGET_GRID`** (annulus plus yellow core); damage/seed brush; rendered as React SVG `<rect>`s | **Turn 9** NCA simulator (L608) and Turn 11 (L684) | T11 says "ImageData … ctx.putImageData()" (L698) and "3x3 convolution … weights … activation rule" (L702–L706); the code uses SVG rects, fixed neighbour weights 0.5/0.25 and an explicit target lookup. T9 says 16 channels (L589) vs 8 in code. T9/T10 describe a learned ~8,000-parameter MLP (L585, L636, L664) vs no learned weights. "Regeneration" comes from attraction to a stored template, not emergence. The "Regen rate" KPI is just `growth*prop*4.5`. README title roughly right. |
| `05-interaction-combinator-net` | "Lafont IC (ERA, CON, DUP) active-pair reduction", **Desktop 8 Turn 21** (not this file) | `InteractionNetWidget`: force-directed graph of 5 labelled nodes (`M1_Max_Swarm_Alpha`, `Core_IP_Kernel`, …) with "metabolic budget" and provenance-hash labels | not in this transcript | No ERA/CON/DUP agents and no active-pair rewriting in the code (grep finds none). **README claim unsupported.** |

**Conclusion:** README turn numbers 2, 3, 8, 9 are correct, but the descriptive filenames and titles of widgets 01, 02, 03 and 05 do not match their content. The widget "MindPalaceSimulation" sits in the file named "morphogenetic", and the file named "mind-palace" holds the SDF visualizer.

---

## 2. Code fragments

Legend:
- Completeness: **CR** complete-runnable, **NC** near-complete, **FR** fragment, **PS** pseudocode.
- Candidate systems (see §4): **S1** Synbios WebGPU dashboard, **S2** SYM-2P codec, **S3** telemetry harvester / CI ingest, **S4** aesthetic slice mixer, **S5** OAuth write-back worker, **S6** live sync poller, **S7** GPU procedural text, **S8** build/deploy pipeline, **S9** Laya reactive UI, **S10** widgets.

I list 38 software or protocol fragments. 9 non-software blocks are skipped: L476–491 and L727–737 (ASCII diagrams), L999–1009 (directory tree for `my-sentient-ui/`: `index.html`, `main.js`, `shaders/ui_core.wgsl`, `public/models/laya_421m.onnx`, `tokenizer.json`), and the diagrams at L1361–1373, L2216–2232, L2510–2522, L2688–2698, L2804–2815, L3408–3416.

| # | file:lines | lang | identifier | what it does | compl. | already extracted? | sys |
|---|---|---|---|---|---|---|---|
| 1 | L25–30 | xml (fenced as text) | SVG circle | literal 100×100 red-circle SVG | CR (trivial) | NOT EXTRACTED | — |
| 2 | L131–138 | glsl | rounded-button SDF | inside/outside test with box SDF | PS | NOT EXTRACTED | S9 |
| 3 | L259–273 | js | `layaAgent.predict` | queries "Laya" with a choice schema → emotion probabilities | PS (unverified API) | NOT EXTRACTED | S9 |
| 4 | L281–303 | glsl | `u_frustration` shader | warps box SDF by sine and mixes blue→red by frustration | PS (`boxSDF`, `stroke`, `uv_coords` undefined) | NOT EXTRACTED | S9 |
| 5 | L337–346 | js | `telemetryState` | rolling telemetry written as an English string for the model | FR | NOT EXTRACTED | S9 |
| 6 | L352–369 | js | `LayaWebAgent.predict` (`@r4ai/laya-web`) | reading-mode classification → `organicScore` | PS (package API unverified) | NOT EXTRACTED | S9 |
| 7 | L383–401 | glsl | organic-reading glow | cream background plus sage glow scaled by score | NC (`u_resolution` not declared) | NOT EXTRACTED | S9 |
| 8 | L549–553 | glsl | nerve_signal | sine "axon impulse" line | FR | NOT EXTRACTED; widget 03 does not use it | S10 |
| 9 | L1164–1166 | SYM-2P sample | `:01:03:0042[s-exp (state 0.92) (tension 0.14)]e3b0c442...` | example positional packet | protocol example | concept in `weft/runtime/aywa/sym2p_codec.py` | S2 |
| 10 | L1186–1245 | wgsl | `Sym2pPacket` / `fragment_main` | role → colour, action → circle/box SDF, tension → glow | FR (no vertex stage) | NOT EXTRACTED | S1/S2 |
| 11 | L1297–1339 | yaml | `.github/workflows/build-engine.yml` "Compile & Optimize Sentient UI Core" | ONNX quantize, terser, copy WGSL, deploy dist→gh-pages | NC (likely invalid CLI `python -m onnxruntime.quantization.quantize_model` L1322; step "Setup Node & Python" sets up only Node, L1310–1313) | NOT EXTRACTED (repo has a different, manual-only `.github/workflows/pages-seed-deploy.yml`) | S8 |
| 12 | L1381–1439 | yaml + inline py | `.github/workflows/synbios-evolution.yml` | cron 15 min / repository_dispatch; `gh api` repos and PRs; tension = open_prs/(active_repos*3); writes a SYM-2P line to `public/data/telemetry.jsonl`; deploys `public`→gh-pages | NC (`--paginate` concatenates JSON arrays → `json.load` fails past 1 page; deploying only `public/` likely clobbers the site) | concept → `weft/runtime/aywa/github_harvester.py` (**diverged**: offline hard-coded repo list) | S3/S8 |
| 13 | L1480–1577 | wgsl | `dashboard_layout.wgsl` v1 (`OrgTelemetry` 16 B) | grid domain repetition, per-cell hash pulse, tension jitter, teal→orange | FR: no vertex entry; **`mod()` is not a WGSL builtin** (L1518) → compile error; `smin` unused | ancestor of `weft/runtime/aywa/dashboard_layout.wgsl` (**heavily diverged**) | S1 |
| 14 | L1605–1810 | js | `main.js` `SynbiosDashboardEngine` | WebGPU init, fetches external WGSL, 16 B uniform, cache-busted fetch of `data/telemetry.jsonl` every 30 s, regex parse, rAF draw(3) | NC (needs shader with `vertex_main`) | ancestor of `docs/assets/js/weft-loom.js` `WeftLoomEngine` (**diverged**: adds SAB worker, lineage α/β, hash verify, 64 B uniforms, draw(6)) | S1/S6 |
| 15 | L1840–1952 | wgsl | `dashboard_layout.wgsl` v2 unified | adds `vertex_main` full-screen "triangle" | NC: `mod()` error; **vertex math yields (-1,-1),(1,-1),(-1,1), only half the viewport**, despite comments L1869–1872 | ancestor; the extracted file replaces this with a 6-vertex quad `vs_main` and floor-based mod | S1 |
| 16 | L1986–2206 | html | `index.html` "SYNBIOS // Unbound Live Grid Engine" | page shell with the `SynbiosDashboardEngine` inlined; DPR resize; poll every 15 s | NC (depends on #15, so inherits its bugs) | ancestor of `weft/runtime/aywa/index.html` and `docs/index.html` (diverged; runtime version is Canvas2D only) | S1 |
| 17 | L2340–2381 | yaml step + py | "Calculate Advanced Cognitive Telemetry" | mock LOC ratio, label, Gini of `[100,2,1,1,0]`, resonance, capture → SYM-2P `(owner …)(lbl …)(con …)(res …)(cap …)` | FR (all mock; overwrites `telemetry.jsonl` and drops `active_nodes`/`tension`) | NOT EXTRACTED | S3 |
| 18 | L2389–2411 | js | 32-byte uniform pack | 8 floats | FR | NOT EXTRACTED | S1 |
| 19 | L2419–2483 | wgsl | `OrgTelemetry` 32 B v3 fragment | owner→aspect, capture→sag, label→colour, concentration→stroke, resonance→pulse | FR (`mod`; vertex "unchanged"; `active_nodes` cull removed) | NOT EXTRACTED | S1 |
| 20 | L2541–2570 | js | 48-byte uniform pack | adds `currentUser.{rounding,density,hue_shift,contrast}` | FR | NOT EXTRACTED | S1/S4 |
| 21 | L2578–2655 | wgsl | `OrgTelemetry` 48 B v4 "Generative Aesthetic Shader" | density→spacing, rounding→radius, hue→colour wheel, contrast→background | FR (`mod`) | NOT EXTRACTED | S1/S4 |
| 22 | L2706–2709 | SYM-2P sample | `:02:04:0001[s-exp (id mithrax) …]` profiles.jsonl | aesthetic slice lines (role 02, action 04) | protocol example | NOT EXTRACTED | S2/S4 |
| 23 | L2717–2760 | js | `blend_ratio` two-profile lerp | lerps base vs donor style, packs 12 floats | FR (`this.state.owner_ratio` undefined at L2752 → NaN) | NOT EXTRACTED | S4 |
| 24 | L2823–2879 | js | `class AestheticMixer` | normalizes slice weights; weighted average; "angular" hue | CR as a class, **logic bug**: hue is averaged linearly (L2864), not on the circle | **EXTRACTED → `docs/assets/js/aesthetic-mixer.js`**, near-identical (adds `setSliceWeight`, returns `hue` not `hue_shift`, header cites `weft/design/baryonic.md`); **carries the bug** | S4 |
| 25 | L2927–3266 | html + inline WGSL | `index.html` "SYNBIOS // Living Aesthetic Matrix" (`SynbiosEcosystem`) | first self-contained page: parses 3 mock SYM-2P profile lines, builds slider deck, sin/cos hue mix, export strand via `alert`, 48 B uniform | NC (`mod` error, half-viewport triangle, no adapter null check, fake 4-char hashes L3094–3096) | NOT EXTRACTED (concept of profile deck absent from `docs/`) | S1/S4/S2 |
| 26 | L3306–3371 | js | `SynbiosGitWriteWorker.commitGeneticStrand` | GET/PUT GitHub contents API to append a line to `public/data/profiles.jsonl` on `main` | NC: URL broken `https://github.com{this.owner}/…` (L3322: no `api.`, no `/repos/`, missing `$`) | NOT EXTRACTED | S5 |
| 27 | L3434–3528 | js | `SynbiosEdgeOrchestrator` | OAuth device flow through `https://corsproxy.io?`; token in `localStorage`; `pushGeneticMutation` | NC: endpoint paths lost (`https://github.com` only, L3454/L3470), same broken contents URL (L3497); **security issues** (§3) | NOT EXTRACTED | S5 |
| 28 | L3575–3645 | js | `LiveEcosystemSynchronizer` | polls `telemetry.jsonl`, bails if trailing hash unchanged, regex for active_nodes/tension/noise | CR as a class (not wired to the renderer) | concept → `docs/assets/workers/telemetry-worker.js` and `weft-loom.js` polling (diverged: 30 s / 45 s, no hash-change bail) | S6 |
| 29 | L3681–3704 | wgsl | `randomNoise2D` (`noise_component.wgsl`) | hash noise × `org_tension` added to background | FR (uses `in.uv * system_time`, so degenerate at t=0) | NOT EXTRACTED | S1 |
| 30 | L3747–3791 | python | `calculate_repository_gini_coefficient` | O(n²) Gini; SYM-2P line with `(con …)` | CR; **comment claims ~0.83, true value 0.7728** for `[450,12,5,2,1]` | concept → `github_harvester.py::compute_gini` (diverged: O(n log n) rank formula) | S3 |
| 31 | L3801–3806 | wgsl | concentration stroke | Gini→stroke thickness | FR (duplicate of #19 L2469–2470) | NOT EXTRACTED | S1 |
| 32 | L3838–4134 | html + WGSL | "SYNBIOS // Pure Procedural Matrix" | 5×7 bitmask digit font in WGSL; sliders tension/Gini/nodes; 32 B uniform | NC: font **cannot work** (35 bits in a u32; shift `34u - bit_index` ≥ 32, L3951); `mod`; half triangle | NOT EXTRACTED | S7/S1 |
| 33 | L4174–4236 | python | `synbios_harvest.py` | urllib: org repos, `stats/contributors` of the newest repo → Gini; open-issues tension; writes `public/data/telemetry.jsonl` | NC: URLs truncated `https://github.com{org_name}/repos` (L4199/L4209, should be `api.github.com/orgs/…`, `/repos/…`); no 202 handling; IndexError on 0 repos | concept → `weft/runtime/aywa/github_harvester.py` (**diverged**: offline hard-coded `MOISSANITE_REPOS`, different tension formula, writes JSON + bin + jsonl via `sym2p_codec`) | S3 |
| 34 | L4244–4552 | html + WGSL | "SYNBIOS // Complete Sovereign Ecosystem" | tri-module page: digit font, 2-profile Barycentric deck, sin×cos "cryptographic watermark" | NC (same font/`mod`/triangle bugs) | NOT EXTRACTED | S1/S4/S7 |
| 35 | L4585–4989 | html + WGSL | "SYNBIOS // Sovereign Textual Organism" (`SovereignSystemCore`) **latest monolith** | ASCII bitmask A–Z, 0–5 font; `@binding(1)` storage `array<TextLinePack>` of 4-char labels; watermark; device-flow panel | NC but **dead on arrival**: `getElementById("slider-nodes")` is null (L4906), the TypeError stops `bindHUDEvents` before the auth handler and `startClock()`; proxy URL has no scheme (L4834); digits 6–9 missing; "space" = 60 | NOT EXTRACTED; descendant ideas in `weft/runtime/aywa/dashboard_layout.wgsl` (TextLinePack, 8-float block) and `weft/runtime/aywa/index.html` (Canvas2D labels) | S1/S5/S7 |
| 36 | L5024–5064 | yaml | `.github/workflows/deploy.yml` "Deploy Sovereign Monolith Core" | push/cron 15 min; copies index.html; `touch` data files; deploys dist→gh-pages | NC (runs no harvester; empty data files clobber ingest output; unused `pages`/`id-token` permissions) | NOT EXTRACTED (the repo workflow is manual-only, `contents: read`) | S8 |
| 37 | L5072–5103 | wgsl | 16-char `TextLinePack` / `renderLabelString` | claims 16-char labels | FR, **invalid**: `vec4<u>` (L5079); loop still `i<4`, so 4 chars | intent realized in the extracted `dashboard_layout.wgsl` (`chars : array<u32, 16>`), but the binding is unused there | S7 |
| 38 | L5111–5125 | js | `repoLabelsTextMatrix` 16-wide | packs labels into a storage buffer | FR, **syntactically corrupted**: `[, // "WEFT-SINGULARITY", // …` (L5114) collapses 3 rows into a comment; 60 used as space | the three lost labels reappear correctly (space = 32) in `weft/runtime/aywa/index.html` | S7 |

**Note A — duplicates and variants inside this file.** All of these are successive versions of one program:
- `sdRoundedBox` and the grid block: #13, #15, #19, #21, #25, #32, #34, #35.
- `vertex_main` half-triangle: #15, #25, #32, #34, #35.
- The hash `fract(sin(dot(...,(12.9898,78.233)))*43758.5453)`: #13, #15, #19, #21, #25, #29, #32.
- Mixer: #24, then #25, #34, #35 (fixed).
- Device flow: #27 and #35.
- Contents-API writer: #26 and #27.
- SYM-2P line building: #12, #17, #30, #33.

**Note B — the same code in other corpus files.** I grepped distinctive strings. They suggest the `weft/design/*.md` files are per-turn copies of this thread:

| Turn(s) | design file |
|---|---|
| T2 | `art.md` |
| T7–T8 | `bio.md` |
| T9 | `create.md` |
| T14 | `converge.md` |
| T17–T23 | `craft.md` |
| T23/T26 | `eh.md` |
| T24 | `done.md` |
| T21/T29 | `build.md` |
| T30 | `custom.md` |
| T31 | `combine.md` |
| T32 | `baryonic.md` |
| T33–T35 | `discovery.md` |
| T36–T40 | `feeed.md` |
| T41 | `core.md` |
| T42 | `aywa.md` |

The corruptions (truncated `https://github.com{…}` at `design/discovery.md:418,593` and `design/feeed.md:646,656`; `[,` at `design/aywa.md:107`; `vec4<u>` at `design/aywa.md:72`) are present there too. So the damage happened when the source was rendered (link paths stripped by AI Mode), not in this extraction.

**Note C — extracted SYM-2P parsers diverge from the transcript.**
- `weft/runtime/aywa/sym2p_codec.py` and `docs/assets/js/sym2p-parse.js` parse role/action/sequence as **hex** (`int(…,16)`). The encoder writes them as **decimal** (`{role:02d}`, `{sequence:04d}`).
- The transcript treats `0042` as "Packet Number 42" (L1174) and slices these fields as strings (L1718–1720).
- So a sequence of 42 round-trips to 66.

---

## 3. Ideas, claims, mechanisms

### 3.1 Graphics and compute

- **Vector graphics are scripts** — L19–32. SVG is a mathematical script; raster formats exist because procedural photorealism is too costly. *theory*.
- **GPU efficiency via SIMD/SIMT, latency hiding, wide buses** — L60–103. "384-bit … exceeding 1 TB/s" (L103). *hardware*. Falsified by spec sheets (holds for top-end GDDR6X/GDDR7 parts only).
- **Procedural UI via uniforms** — L127–157. The model changes uniforms (`u_time`, `u_hover_intensity`, morph `t`), not code; claims "zero pixelation". *mechanism*.
- **SDF algebra** — L170–226. Circle and box SDFs; union = min, subtraction = max(-A,B), intersection = max, smooth union `smin`; `abs(d)-t` gives outlines. *theory* (correct, standard).
- **SDF repetition / "Grid Domain Chaining" layout** — L1470, L1583–1585. Repo cards are laid out by `floor`/`mod` cell repetition; "pass 4, 40 or 400 nodes at locked latency". *mechanism*. Falsified by the shader: the linear index `cell_id.x + 4*cell_id.y` is not unique over a ~7-column viewport (e.g. cells (-3,1) and (1,0) both map to 1), and `mod` is not WGSL.
- **Zero-input full-screen triangle** — L2210–2244. 3 vertices from bit tricks cover the screen. *mechanism*. **Contradiction:** the code at L1873–1874 gives (1,-1),(-1,1), not (3,-1),(-1,3) as claimed at L1869–1872 and L2238–2240. Falsified by evaluating the formula; only the lower-left half of the viewport is drawn.
- **16/32/48-byte uniform packing** — L1667–1668, L2394, L2546. Std140 16-byte alignment reasoning. *engineering-contract*. Correct for all-f32 structs (any multiple of 4 is fine; struct size rounds to 16).
- **Procedural noise as a "tension atmosphere"** — L3667–3716. Grain amplitude ∝ `org_tension`. *mechanism / vision-language*.
- **GPU bitmap font, "no HTML fonts"** — L3824–3830, L4138–4146.
  - Claim (L4143): each glyph is "a single 32-bit unsigned integer".
  - Claim (L4146): text "can never blur, pixelate".
  - Category: *mechanism*. Falsified: a 5×7 grid needs 35 bits, and the shift `34u - i` exceeds 31. A point-sampled bitmap font is by definition pixelated (blocky) when scaled; it is not vector.
- **"Cryptographic watermark / anti-tamper matrix"** — L4164, L4397–4406, L4778–4782. It is just `sin(x·f+t)·cos(y·f−t)` line art. *vision-language* (no cryptography, no tamper evidence). Falsified by any analysis: no key, hash or verification exists.

### 3.2 Models and intelligence

- **Laya as non-autoregressive "System 1"** — L236–250, L410.
  - Claims: "~421M parameter open-source decision model developed by Convai Innovations", WASM/WebGPU package `@r4ai/laya-web`, ModernBERT backbone, 30–70 ms in browser.
  - Later references: `laya_421m.onnx` (L1007, L1324), `laya-system-one` (L409).
  - Category: *theory / external claim*, **unverified**. Falsified by the HF repo `convaiinnovations/laya` or npm `@r4ai/laya-web` not existing or not matching. Also appears in `weft/design/anew.md`, `alive.md`, `create.md`.
- **Reading-reward loop** — L323–410. Scroll velocity, jitter and dwell → Laya classify → `organicScore` → typography relaxation and glow. *mechanism (proposed)*; privacy claimed by local execution (L409). Falsified by user studies; no metric is given.
- **Mind palace = body anatomy** — L445–448, L474–513. Telemetry = nerves, small model = brainstem, uniforms = motor neurons, GPU = muscles. *vision-language* (teaching analogy only).
- **NCA** — L575–619, L636–664.
  - Claims: 3×3 neighbourhood, 16 channels (4 visible + 12 hidden), ~8k-param MLP per cell, self-repair; "~20 KB" model (L619).
  - Cited prior art: Distill 2020 "Growing NCA" (L577, L636), Houdini Copernicus NCA nodes (L650), NCAtorch (L654).
  - Category: *theory*. Falsified by those external sources. **Contradiction with widget 04** (8 channels, no learning, global target lookup; see §1.1.2).
- **Widget tech stack claim** — L688–712. "Float32Array … ImageData … putImageData … 3x3 convolution matrix". *engineering claim*. **Contradicted by widget 04** (React SVG `<rect>`s, fixed neighbour weights plus an explicit target).
- **Post-app / Zero-UI** — L719–767. An LLM captures all app functionality; the user steers with taste; a "latent vector of intent" goes straight into a shader grid; online LoRA from telemetry. *vision-language / roadmap-branch*. Not testable as stated.
- **Inkling 2 Small / Tinker** — L779–813.
  - Claims: "594B MoE, 17B active"; autonomous training run "4.5 hours … $426"; "peak convergence in 75 steps".
  - Category: *external claim*, **unverified**. Falsified by the cited `thinkingmachines.ai/news/inkling-2-small/` page.
- **System 2 trains System 1** — L811–813. A big remote model fine-tunes in-browser pixel rules "within a few hours". *roadmap-branch*.

### 3.3 Weft fusion (Turn 14)

- **Grand Unification Matrix** — L835–842. Weft classes mapped to roles:
  - `AppleSiliconTelemetryBridge` → nerves
  - `AppleSiliconComputeBus` (shared memory) → synaptic cleft
  - `M1MaxOrganismCell` α/β lineages → brainstem / NCA cells
  - `draw_jev_ui` → somatic expression

  Category: *vision-language*. These identifiers live in `weft/ahraz.md`, `weft/design/converge.md`, `weft/test.md`, `weft/launch.md` (not in this file).
- **Attention as a system metric** — L850–852. Combine Mach kernel stats with browser events in one input tensor; skimming forces local LoRA (`lora_A`, `lora_B`) mutation. *mechanism (aspirational)*. **Contradicted by T18** (L1087: browsers cannot touch kernel or hardware outside APIs).
- **α "Safe" vs β "Bold" lineages compete** — L856–861, L1064–1068. Winner chosen by `loss_A` vs `loss_B` drives the shader. *mechanism*. Echoed in `docs/assets/js/weft-loom.js` (`lineage_alpha_confidence`).
- **On-chain settlement of alignment** — L863–868.
  - Mechanism: a "Tension Fracture" goes through `report_fracture_to_chain` to an Arbitrum Stylus WASM ledger; deep reading raises `live_match_pct` and "stream[s] protocol capital directly into the `weaver_capital_vault`".
  - Category: *economics / governance*. **Safety-relevant** (monetizing user attention, on-chain user-behaviour data). No addresses or keys in this file.

### 3.4 Web boundaries and hosting

- **DOM is a 1990s "document prison"** — L887–939. Replace it with SDF/WebGPU, emergent NCA state and continuous telemetry. *vision-language*.
- **Static hosting suffices** — L952–1015. GitHub Pages/Vercel serve the seed; compute runs on the client; "10 million visitors … hosting bill remains zero" (L1013). *engineering claim*. Falsified by GitHub Pages bandwidth limits (soft 100 GB/month) and model-weight download sizes.
- **Unbound abios/synbios** — L1027–1072. The documentation site becomes an execution environment of SYM-2P; an "Interaction Net Interpreter" in WASM draws the page; "101-byte SYM-2P token packets" (L1054). *vision-language / roadmap-branch*. **Contradiction on packet size:** "101-byte" (L1054) vs "70-character" (L2779) vs "80-character" (L2918). With a 64-hex SHA-256 suffix the lines are ≥100 chars.
- **Reality check (T18)** — L1085–1128. Retracts "allocate shared memory pages / silicon" and translates it to SharedArrayBuffer, Web Workers, WebGPU, ONNX Runtime Web and SDF canvas. *engineering-contract*. This is the honest baseline and should anchor any spec. Omission: SharedArrayBuffer needs cross-origin isolation (COOP/COEP), which GitHub Pages cannot set by headers; `telemetry-worker.js` notes the fallback.

### 3.5 SYM-2P protocol (as used here)

- **Line format** — L1158–1176. `:RR:AA:SSSS[s-exp (k v)…]<sha256hex>`. Fields: role byte → colour, action → SDF shape, sequence → animation phase, payload → uniforms, hash → "randomization seed". *engineering-contract*.
- **Role enumeration** — L1153: 0x01 Ingest/Sensor, 0x02 Validator, 0x03 Actor, attributed to "the protocol" with a stray citation marker "[cite: 1]".
  - Conflicts: T21+ uses `:01:03` for org telemetry (role 01 sensor, action 03 "executing"). T31 uses `:02:04` for aesthetic profiles (L2707), which reuses "02 Validator" for profiles. Inconsistent semantics.
  - Falsified by the real `Moissanite-Labs/abios` spec.
- **Hash** — L1426, L2375, L3787, L4222. SHA-256 of the bracketed payload string, appended in hex. *mechanism*. Integrity only, not authentication (anyone can recompute it). Prose calls it "enforcing append-only security" (L2280), which is false: there is no chaining or signature.
- **Payload keys drift**:
  - `active_nodes`, `tension` (T21)
  - `owner`/`lbl`/`con`/`res`/`cap` (T29 code L2374) vs `owner_ratio`/`labels`/`concentration`/`resonance`/`capture` (T29 table L2328–2332)
  - `con` (T38/T40)
  - `noise` (T36 parser L3622, never produced)
  - `gini` (extracted `telemetry.jsonl`)

  The JS parsers only read `active_nodes`/`tension` (L1730–1731, L2139–2140), so the T29 fields never reach the shader from data. *contradiction*.
- **"Repo is the database"** — L2909–2919, L3272. `profiles.jsonl` is an append-only text ledger in the repo; peers append lines. *mechanism*.

### 3.6 Org analytics

- **Project tension index** — L1421 `min(1, open_prs/(active_repos*3))`; L4218 `min(1, open_issues/(active_nodes*5))`; extracted `github_harvester.py:66` uses yet another formula. *mechanism*. Three inconsistent definitions.
- **Five advanced metrics** — L2302–2306 (user), L2326–2332 (mapping):
  - ownership LOC ratio → aspect
  - labels → colour
  - Gini of commits → stroke
  - "resonance" (fixes linked to an author's lines) → pulse
  - "capture" (contributors' activity elsewhere) → smin gravity

  Category: *mechanism*. In code (L2348–2371) all five are mocks. "Capture" implies cross-referencing user IDs against global OSS logs, which is a privacy concern.
- **Gini as bus-factor proxy** — L3738–3775. G = ΣΣ|xi−xj| / (2·n·Σx). *theory*. The formula is correct, but L3783 "Result: ~0.83" is **wrong (0.7728)**. The filter `count > 0` drops zero-commit contributors, which biases the result.

### 3.7 Personalization ("genetic" aesthetics)

- **Aesthetic Alignment Vector** — L2526–2533. rounding, density, hue_shift, contrast extracted from a developer's repos (`.css`, `.vscode/settings.json`). *mechanism (unspecified extractor)*. Falsified by building the extractor; no algorithm is given.
- **Barycentric mix of N slices** — L2796–2895. Normalize weights to sum to 1. *mechanism*. Worked example L2806–2811: 0.8/0.3/0.4 → 0.53/0.20/0.27, which is correct.
- **Angular hue blending** — L2862–2868, L2885–2887. **Contradiction:** the T32 prose promises shortest-path blending, but the code linearly averages angles (no wrap). Fixed in T33 L3143–3150 (sin/cos + atan2). The extracted `docs/assets/js/aesthetic-mixer.js` copies the **buggy** T32 version.
- **Stigmergic software** — L3375–3385. Users mutate a shared environment by committing style lines; every visitor's view shifts. *vision-language / governance*. No moderation, rate limit or ownership model, so the shared visual state can be vandalized (§6).

### 3.8 Write-back, auth and live sync

- **OAuth device flow from a static page** — L3398–3426. Avoids a client secret; claims "100% inside GitHub Pages without running a server" (L3398), yet relies on a third-party CORS proxy (L3400, L3447). *engineering-contract / security*. **Self-contradiction:** "serverless" depends on someone else's server.
- **Live update within 15–30 s by cache-busted polling, or SSE via an edge function** — L3556–3565. *mechanism*. Falsified by the GitHub Pages CDN max-age (~10 min) plus Actions/Pages build latency (minutes). The "within 15 seconds" (L3651) ignores the build and deploy time of the cron/dispatch workflow.

### 3.9 Safety-relevant locations (values not copied)

- L1389–1390, L1401: workflow with `contents: write` and `GH_TOKEN: ${{ secrets.ORG_GITHUB_TOKEN }}`. This is an org-wide PAT secret reference (no value present).
- L3302–3313, L3323–3326: bearer token passed into a browser class (`userToken`).
- L3444, L3481: access token persisted in `localStorage` key `synbios_auth_token`. XSS-exfiltratable.
- L3447, L3454, L3470: **public CORS proxy `corsproxy.io`** relays the device-code request and the **token exchange**, so a third party sees the access token.
- L3457, L4936: scope `public_repo`, i.e. write to *all* of the user's public repos.
- L3347, L3512: automatic commits straight to `main`.
- L4232: `GITHUB_TOKEN` env read by the harvester.
- L4834–4835: proxy reused, plus a **hard-coded 20-hex-character OAuth `client_id` literal**. It is a public identifier rather than a secret, but it ties the page to an unknown OAuth app. Same literal in `weft/design/core.md`.
- L4951: token stored in `localStorage` key `synbios_node_token`.
- L4996: prose says the panel prints an "encrypted string token". It actually displays a user_code; the access token is stored in plaintext.
- L1334–1338, L1434–1438, L5059–5063: unpinned third-party action `JamesIves/github-pages-deploy-action@v4` pushing to `gh-pages` (supply-chain risk).
- L1385, L5030: cron every 15 minutes (auto-publishing).
- L5032–5035: broad `contents/pages/id-token: write`.
- L863–868: on-chain settlement and capital streaming of user attention.
- L2513, L2332: scraping personal repos and cross-referencing contributors across OSS (profiling).
- **None found:** private keys, RPC URLs, mainnet contract addresses, literal secrets (grep for `0x…{20,}`, `rpc`, `mainnet`, `ghp_`, `api_key` is empty apart from the items above).
- **Repo contrast:** `.github/workflows/pages-seed-deploy.yml` is `workflow_dispatch`-only with `contents: read`, which is safer than everything the transcript proposes.

---

## 4. Candidate software systems

**S1. Synbios / Aywa WebGPU org dashboard (frontend renderer).**
- Purpose: render org repos as SDF cards whose geometry and colour encode telemetry.
- Inputs: `data/telemetry.jsonl` (SYM-2P), user sliders/profiles, time.
- Outputs: canvas pixels.
- Interfaces: S2 (parse), S3 (data producer), S4 (style vector), S6 (poller), S7 (labels).
- Fragments: #10, #13–16, #18–21, #25, #29, #31, #32, #34, #35.
- Dependencies: WebGPU, WGSL, vanilla JS.
- Uniform contract history:
  - v1 16 B `[nodes, tension, time, pad]`
  - v2 32 B `+owner, label, concentration, resonance, capture`
  - v3 48 B `+rounding, density, hue, contrast`
  - T39 32 B `[nodes, tension, time, gini, label, rounding, density, hue]`
  - T40–41 32 B `[nodes, tension, time, gini, rounding, density, hue, contrast]` + storage labels
  - extracted 64 B = T41 layout + `node_vel_0/1 vec4`
- Extracted descendants: `weft/runtime/aywa/dashboard_layout.wgsl` (= `docs/assets/shaders/dashboard_layout.wgsl`, byte-identical), `weft/runtime/aywa/index.html` (Canvas2D only, no WebGPU), `docs/index.html` and `docs/assets/js/weft-loom.js`. The extracted shader repairs the vertex bug (6-vertex quad), drops `mod`, fixes indexing (`+2` offsets, 5 columns), declares `labelData` but never uses it, and renames entries to `vs_main`/`fs_main`.

**S2. SYM-2P positional codec.**
- Purpose: compact, hash-suffixed, line-oriented telemetry and profile records.
- Inputs/outputs: dict ↔ `:RR:AA:SSSS[s-exp …]hex`.
- Fragments: #9, #12, #17, #22, #30, #33; parsers inside #14, #16, #25, #28.
- Extracted: `weft/runtime/aywa/sym2p_codec.py`, `docs/assets/js/sym2p-parse.js` (with `verifySym2pLine` hashing the bracketed block, consistent with the Python generators).
- Shares its spec with abios (external). Decimal-vs-hex divergence: §2 note C.

**S3. Org telemetry harvester / CI ingest.**
- Purpose: pull GitHub org data, compute tension and Gini, and emit SYM-2P.
- Inputs: GitHub REST via `gh`/urllib and a token.
- Outputs: `public/data/telemetry.jsonl`.
- Fragments: #12, #17, #30, #33.
- Dependencies: Python stdlib, `gh` CLI, Actions.
- Extracted analogue: `weft/runtime/aywa/github_harvester.py` (diverged: offline, hard-coded `MOISSANITE_REPOS` with a "suspended" account narrative and a different tension formula), consumed by `weft_daemon.py` (Darwin sysctl + shared memory). This is genuinely a separate process from S1.

**S4. Aesthetic slice mixer ("genetic style").**
- Purpose: blend N user style vectors into 4 uniforms.
- Inputs: `profiles.jsonl` lines and weights.
- Outputs: rounding/density/hue/contrast.
- Fragments: #20–25, #34, #35.
- Extracted: `docs/assets/js/aesthetic-mixer.js` (T32 buggy hue). Shares S2 for wire format. Small; could live inside S1.

**S5. OAuth device-flow write-back worker.**
- Purpose: let visitors append SYM-2P profile lines to the repo from the page.
- Inputs: user auth.
- Outputs: commits to `main`.
- Fragments: #26, #27, #35.
- Dependencies: GitHub OAuth app, CORS proxy, contents API.
- NOT EXTRACTED. Security-sensitive (§3.9); needs a redesign (e.g. GitHub App + PR-based submissions, or issue forms) before any build.

**S6. Live sync poller.**
- Purpose: refresh telemetry without reload.
- Fragments: #14 (30 s loop), #16 (15 s), #28 (hash-change bail).
- Extracted analogues: `docs/assets/workers/telemetry-worker.js` and the `weft-loom.js` 45 s interval. Shares logic with S1/S2.

**S7. GPU procedural text renderer.**
- Purpose: draw digits and ASCII labels inside WGSL from bitmasks and a storage buffer.
- Fragments: #32, #34, #35, #37, #38.
- NOT EXTRACTED as a working font. The extracted `index.html` falls back to `ctx.fillText`, and the extracted shader declares 16-char `TextLinePack` but does not use it.
- Needs a real glyph encoding (e.g. 2×u32 per glyph or `array<u32,7>` rows).

**S8. Build/deploy pipeline.**
- Purpose: quantize the model, minify, and publish to gh-pages on push/cron.
- Fragments: #11, #12 (deploy part), #36.
- NOT EXTRACTED. The repo instead has a manual `pages-seed-deploy.yml` plus `scripts/sync_pages_seed.py`. The transcript's three workflows (#11, #12, #36) all deploy different folders to the same `gh-pages` branch, so they would clobber each other.

**S9. Laya reactive-UI / reading-reward pipeline.**
- Purpose: classify user behaviour in-browser and drive shader uniforms.
- Fragments: #2–7.
- Dependencies: the unverified `@r4ai/laya-web`, ONNX Runtime Web.
- Pseudocode only. NOT EXTRACTED. Separate from S1, but it could feed S1 uniforms.

**S10. Educational widgets.**
- Purpose: explain SDF, procedural shading, the mind-palace pipeline and NCA.
- Code exists only as the extracted `widgets/01–04` (React, Radix, Canvas2D/SVG, Google widget CDN). Widget 05 is from thread1.
- Independent of S1 except shared SDF math (widget 02 `smin` = the WGSL `smin` in #13).

**Related but external:** the Weft Mac harness (`weft_singularity_core.py` classes) and the ledger (`report_fracture_to_chain`) are only referenced here (T14). They belong to the Mac-harness and ledger systems inventoried elsewhere.

---

## 5. Documents implied

- **Technical spec: "Synbios/Aywa serverless dashboard".** Phases D–I give a nearly complete design. To finish it, consolidate:
  - the data flow diagram (L1361–1373)
  - the field mapping tables (L2261–2290, L2326–2332)
  - the uniform-layout history (§4 S1)
  - the T18 reality-check table (L1093–1097) as the binding constraint section
- **Spec: SYM-2P line format v0.** Pieces are at L1158–1176, L1423–1427, L2702–2709 and L3606–3611. It needs to settle hex vs decimal, role/action registries, payload key registry, hash scope (brackets included) and the max line length. It should defer to the abios spec.
- **Security/threat-model document for write-back.** Called for by T34–T35 and T41: token storage, CORS-proxy trust, scope minimization, branch protection, moderation of `profiles.jsonl`. Not present anywhere in the transcript.
- **Explainer / white-paper chapter: "Web graphics is just math".** T0–T3 and T38 (L3728–3732) read close to a finished explainer, with SDF formulas and the CSG table at L205–210.
- **Vision/manifesto: "Post-App, Zero-UI, interface as organism".** T12 (L719–767) and T15 (L887–939) are near-finished manifesto prose. Tag them vision-language.
- **Research note: NCA prior art and Laya/Inkling claims.** T9, T10 and T13 need citation verification before any reuse (§3.2).
- **Governance/economics branch: "on-chain alignment settlement".** T14 L863–868, a roadmap branch to cross-reference with the ledger docs. It should carry explicit consent and privacy language.
- **Learning guide: the "mind palace" four-layer stack.** T6 (L430–448) and T7 (L476–513) form an onboarding doc that is nearly complete.
- **Widget catalogue.** README.md L14–18 needs correcting per §1.1.2.

---

## 6. Open questions / gaps

1. **Every WGSL program in the transcript fails to compile as written.** `mod()` is not a WGSL builtin (L1518, L1908, L2443, L2612, L3053, L4002, L4412, L4788), and T42 adds `vec4<u>` (L5079). None of the "copy-pasteable" pages (T26, T33, T39, T40, T41) can render. The extracted shader is a repaired rewrite, not an extraction.
2. **Half-viewport vertex bug** (L1873–1874 and all copies) vs the claimed 3×-oversized triangle (L1869–1872, L2238–2240).
3. **T41 cannot run**: `slider-nodes`/`val-nodes` elements do not exist (L4906–4908). The thrown TypeError skips the auth handler (L4919) and the render loop (L4893). The proxy URL lacks a scheme (L4834, L4933).
4. **Font encoding impossible**: 5×7 = 35 bits in u32 (L3922–3953, L4345–4367, L4707–4751). Digits 6–9 are absent from the "full alphabet" (L4735–4742). The space code is 60 (`<`), not 32 (L4741, L5114).
5. **The 16-char claim vs code** (L5070, L5079, L5093): still 4 glyphs, and a JS/WGSL stride mismatch (16 u32 per label vs a 16-byte struct).
6. **The data path is never closed in the "final" system.** T41 fetches no telemetry or profiles; T42 `deploy.yml` runs no harvester and writes empty data files (L5056–5057). The T29 fields are never parsed client-side (§3.5).
7. **Truncated or broken URLs** for every GitHub API call (L3322, L3454, L3470, L3497, L4199, L4209, L4933, L4943). The correct endpoints (`api.github.com/repos/{o}/{r}/contents/{path}`, `/orgs/{org}/repos`, `/repos/{o}/{r}/stats/contributors`, `github.com/login/device/code`, `/login/oauth/access_token`) are never specified.
8. **Moderation and abuse**: anyone with a token can append to `profiles.jsonl` and change everyone's view (L3292–3296, L3381–3383). No policy, weights per author, signature or revert path. The hash gives integrity, not authorship (L2280 overclaims "append-only security").
9. **The style-extraction algorithm** ("color-clustering on theme config", "rounding bias") is promised (L2530–2533, L2669) but never specified. "Resonance" and "capture" are mocked (L2368–2371) with no data source.
10. **Tension has three inconsistent definitions** (L1421, L4218, `github_harvester.py:66`). Gini has two implementations (O(n²) in the transcript vs a rank formula in the extracted code); the zero-count filter differs (T29 keeps zeros, T38/T40 drop them).
11. **Packet length claims** (101 B, 70 chars, 80 chars) are inconsistent and incompatible with a 64-hex hash (§3.4).
12. **Live-update latency** (L3651 "within 15 seconds") ignores Actions and Pages deploy time and the CDN cache. SSE relay (L3565) is proposed but not designed.
13. **Laya / Inkling / NCAtorch / Houdini claims** are unverified (§3.2). The build workflow's quantization CLI (L1322) is probably not a real entry point.
14. **README.md mismatch**: widget titles for 01/02/03/05 do not match content. README says 51 blocks; the file has 47.
15. **T8 and T11 prose vs widget code** (GPU shader / SDF / `putImageData` claims vs Canvas2D/SVG): the transcript describes intended implementations that the shipped widgets do not have.
16. **The workflows conflict**: #11, #12 and #36 all force-deploy different folders to `gh-pages`.
17. **SharedArrayBuffer on GitHub Pages** requires COOP/COEP headers that Pages cannot set (T18 L1105–1110 omits this). The extracted worker falls back to postMessage.
18. **Extracted-parser divergence** (hex vs decimal fields, §2 note C) and **the extracted mixer carrying the T32 hue bug** (`docs/assets/js/aesthetic-mixer.js`) should be resolved against the T33 fix.
