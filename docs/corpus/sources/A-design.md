<!--
Corpus map source report A. Scope: weft/design/*.md (19 files).
First-pass inventory written by a mapping agent that read every line of its scope (Discussion #11, PR #12).
Treat each finding as a claim with a location, not as settled: findings re-verified for PR #12 are listed
in ../claims-register.md with status VERIFIED. Line numbers refer to main@f67d9dc.
No secret values are reproduced; sensitive material is cited by location only.
-->

# Inventory A — weft/design/ (19 files)

Files: alive, anew, arrival, art, aywa, baryonic, bio, build, combine, converge, core, craft, create, custom, discovery, done, eh, feeed, feel (all `/home/user/weft/weft/design/*.md`). Total 5,012 lines, ~309 KB. I read every line.

**Provenance (important for versioning):** each of the 19 files is a contiguous excerpt of `/home/user/weft/weft/browser-sources/thread2-design-main-6C083A.md` (5,135 lines). The first line of each file appears there at the line shown below. That gives the true chronological order, which tells later versions from earlier ones:

| order | file | thread2 line | | order | file | thread2 line |
|---|---|---|---|---|---|---|
| 1 | arrival | 8 | | 11 | eh | 1976 |
| 2 | art | 115 | | 12 | build | 2316 |
| 3 | alive | 236 | | 13 | custom | 2498 |
| 4 | bio | 424 | | 14 | combine | 2678 |
| 5 | create | 575 | | 15 | baryonic | 2794 |
| 6 | feel | 686 | | 16 | discovery | 2905 |
| 7 | converge | 825 | | 17 | feeed | 3554 |
| 8 | anew | 887 | | 18 | core | 4573 |
| 9 | craft | 1030 | | 19 | aywa | 5008 |
| 10 | done | 1832 | | | | |

Genre: every file is a scraped **Google AI-Mode dialogue transcript**, showing only the assistant turns. User prompts appear as `### ...` headings. The scrape left artifacts in the files:
- Each turn ends with a "ShareGood responseBad response…Google may use account and system data…" footer.
- "AI-generated. Don't enter sensitive personal info." marks where an interactive widget once stood: art.md:7, art.md:104, bio.md:112, create.md:36.
- Math was garbled by screen-reader text (art.md:72, 81; baryonic.md:5).
- URLs were systematically truncated to `https://github.com` or `://github.com`. The source thread has the same damage (thread2:3322, 3497, 4199, 4209), so it happened at capture time.

---

## 1. Per-file summary

**alive.md** (183 lines). Dialogue transcript. It pitches "Laya", described as a ~421M-parameter non-autoregressive decision model from Convai, run in the browser through `@r4ai/laya-web`, as a "System 1" layer. Laya classifies user state (frustrated or calm; deep reading or skimming) in 30–70 ms. The output is passed as a shader uniform that warps SDF UI elements. The second turn is the "Reading Reward Pipeline": rolling 5-second telemetry (scroll velocity, jitter, dwell time, selection) goes to Laya, then to an `organicScore`, which drives line-height, a cream background and a "focus glow" shader. Topics: local inference, behavioural telemetry, privacy-by-locality, GLSL uniforms.

**anew.md** (136 lines). Manifesto plus hosting Q&A. "The DOM is a prison": the web should move to SDF/WebGPU, NCA-style emergent state, continuous telemetry and local weight adaptation. It then answers "can this be hosted on GitHub Pages/Vercel?": yes, the site collapses to static files, with model weights served as static assets. It gives a canonical directory layout (index.html, main.js, shaders/ui_core.wgsl, public/models/laya_421m.onnx, tokenizer.json). Topics: sovereignty, static hosting, cost inversion.

**arrival.md** (100 lines). Explainer. Covers why maths scripts can produce images (SVG and vector graphics vs raster images and procedural/ray-tracing approaches), then why GPUs are efficient (SIMD/SIMT, latency hiding, wide memory buses). It is general background and Weft-agnostic.

**art.md** (116 lines). Explainer on procedural UI. SDFs, uniforms (`u_time`, hover, morph `mix(square, circle, t)`), circle and box SDF formulas, boolean operations (min/max, smooth union `smin`), outlines via `abs(sdf)-t`. It references two embedded widgets (a "Procedural UI & Animation Shader Sandbox" and an SDF visualizer) that are not included.

**aywa.md** (128 lines). Final turn of the thread, in "production" register. It provides `.github/workflows/deploy.yml`: on push plus a cron every 15 minutes, it copies index.html to dist and touches `data/telemetry.jsonl` and `data/profiles.jsonl`, then deploys to `gh-pages` via JamesIves. It also gives a "16-character" WGSL label struct and a JS storage-buffer upload. It declares the platform "officially secure, serverless, automated". The filename (Aywa) is the corpus's dashboard name, but the text never says "Aywa"; it says "Sovereign Monolith".

**baryonic.md** (106 lines). Spec plus code. It replaces the single blend slider with an N-way "Barycentric Mix Engine": the weights are normalised so they sum to 1. It contains the `AestheticMixer` class and argues that hue must be blended as an angle. Its own code does not do that (see §6).

**bio.md** (146 lines). Explainer. Presents a four-layer "AI tech stack": telemetry, local model, SDF and uniforms, SIMD hardware. Each layer is then mapped to anatomy: nerves, brainstem (System 1 / Laya) vs cerebrum (System 2 / LLM), motor neurons (uniforms), muscles (GPU). The "Anatomical Mind Palace" diagram starts at bio.md:53. A third turn describes a "Live Procedural Biology Simulation" widget, which is not included, and gives a GLSL nerve-pulse snippet. This is the clearest vision-language glossary in the set.

**build.md** (177 lines). Spec plus code. Maps five "advanced telemetry dimensions" to visuals: Ownership (owner_ratio → aspect), Labels (label_state → colour), Gini concentration (→ stroke), Resonance (→ glow pulse frequency), Capture (→ field sag). The table is at build.md:9-17. The code is an Actions step that computes the metrics as mocks and writes a SYM-2P line, a 32-byte uniform pack, and a WGSL shader that uses the five fields.

**combine.md** (111 lines). Spec plus code. Introduces "style genes": per-developer aesthetic vectors as SYM-2P lines in `data/profiles.jsonl`, plus a two-way `blend_ratio` linear interpolation between base and donor styles, packed into a 48-byte uniform. Argues for peer-to-peer sharing of style "strands" without PRs.

**converge.md** (57 lines). Fusion essay. Maps components of the user's earlier `weft_singularity_core.py` onto mind-palace terms and generative-UI roles: `AppleSiliconTelemetryBridge`, `AppleSiliconComputeBus`, `M1MaxOrganismCell` with Alpha/Beta lineages, `draw_jev_ui`, `report_fracture_to_chain`, `weaver_capital_vault`. It adds on-chain settlement of "Tension Fractures" (Arbitrum Stylus) and "micro-rewards" for focus. There is no code.

**core.md** (429 lines). Code dump: the "Unbound Master Monolith Core" index.html. It combines a WebGPU shader with an A–Z/0–5 bitmask font read from a storage buffer, a barycentric mixer with correct circular hue, a sin·cos "anti-tamper watermark", and an OAuth Device Flow panel routed through corsproxy.io. It claims "no mock arrays and no placeholders". In fact it throws at boot (see §6).

**craft.md** (797 lines). The densest file, and the main source of requirements for the GitHub Pages site:
- Turn 1 (craft.md:1-50): "unbinding" the abios/synbios GitHub Pages sites so the site *is* the protocol runtime.
- Turn 2 (craft.md:54-108): an explicit retraction of the sci-fi claim, plus a real-API translation table (SharedArrayBuffer, Web Workers, WebGPU, ONNX Runtime Web).
- Turn 3 (craft.md:112-232): the SYM-2P positional line format, role and action bytes, and a WGSL role→colour / action→shape shader.
- Turn 4 (craft.md:236-316): `build-engine.yml` (ONNX quantisation, terser, deploy).
- Turn 5 (craft.md:320-435): `synbios-evolution.yml` (cron every 15 minutes plus repository_dispatch; org repo/PR harvest; tension; deploy).
- Turn 6 (craft.md:439-560): the first `dashboard_layout.wgsl` grid engine.
- Turn 7 (craft.md:564-797): the full `main.js` `SynbiosDashboardEngine` (fetch, parse, uniform, render loop, fallback).

**create.md** (106 lines). Explainer on Neural Cellular Automata: Growing NCA (Distill 2020), 16 channels per cell, a 3x3 neighbourhood, self-repair, Houdini Copernicus NCA nodes, NCAtorch. Explains why NCA has not reached web frameworks (text, training cost, tooling divide). There is no code.

**custom.md** (175 lines). Spec plus code. Derives a four-float "Aesthetic Alignment Vector" (rounding, density, hue_shift, contrast) from a developer's public repos (CSS, `.vscode/settings.json`). This feeds a 48-byte uniform with a personalised WGSL shader. Topics: per-user personalisation, which raises privacy questions.

**discovery.md** (644 lines). Code dump plus spec. Contains the full "Self-Contained Genetic UI Organism" index.html, which loads profiles from SYM-2P strings, builds a slider deck, runs a barycentric mixer with circular hue, and offers an Export button. It also contains `SynbiosGitWriteWorker`, which appends to `public/data/profiles.jsonl` through the GitHub Contents API, and `SynbiosEdgeOrchestrator`, which runs the OAuth Device Flow through corsproxy.io and then writes the commit. It frames the result as "stigmergic software". Topics: bidirectional site ↔ repository loop, tokens in localStorage.

**done.md** (131 lines). Code: the consolidated `dashboard_layout.wgsl` with a "zero-input full-screen triangle" vertex stage plus the craft.md grid fragment. Its comments claim vertices at (3,-1) and (-1,3); the code does not produce them (see §6).

**eh.md** (323 lines). Code plus Q&A. Contains the `index.html` viewport template with an inline `SynbiosDashboardEngine` (15-second polling, resize handling, fallback banner), an ASCII-art explanation of the full-screen triangle trick, and a "fields covered so far" summary (active_nodes, open_prs, org_tension; SYM-2P role, action, sequence, payload and hash; three uniforms).

**feeed.md** (1,013 lines). Code dump across five turns:
- (a) `LiveEcosystemSynchronizer`: cache-busted polling that uses the trailing hash for change detection; it also compares a cache-busted CDN poll with an SSE webhook relay.
- (b) A WGSL hash-noise grain scaled by tension.
- (c) A Gini coefficient script in Python plus a SYM-2P line.
- (d) The "Pure Procedural Matrix" index.html with a 5x7 digit bitmask font.
- (e) The "triple-module synthesis": a `synbios_harvest.py` live harvester using urllib and the GitHub API, plus the "Complete Sovereign Ecosystem" index.html (digits, barycentric deck, "cryptographic watermark").

**feel.md** (134 lines). Dialogue. It first describes the stack of the NCA widget (Canvas2D, Float32Array, putImageData, 3x3 convolution). It then gives a post-app manifesto: an LLM "intent engine" sends a latent vector to a morphing WebGPU canvas, and the user acts as "evolutionary pressure". Finally it reports claims about Thinking Machines' Inkling 2 Small and Tinker: 594B MoE with 17B active, an autoresearch run of 4.5 h costing $426, convergence in 75 steps. These are external claims I could not verify offline.

---

## 2. Code fragments

Language tags are as written. "S#" refers to systems in §4. Shell one-liners and ASCII diagrams are skipped. The arrival.md:18-23 SVG circle is a 3-line toy and is omitted.

| # | file:lines | lang | identifier | what it does | completeness | already extracted? | system |
|---|---|---|---|---|---|---|---|
| 1 | alive.md:24-38 | js | `layaAgent.predict(state, questions)` | Queries a local decision model with a choice schema (calm/confused/frustrated) | pseudocode (`layaAgent` undefined) | NOT EXTRACTED | S8 |
| 2 | alive.md:46-67 | glsl | frustration pixel shader | `u_frustration` adds a sine warp and a blue→red mix on a box SDF | fragment (`boxSDF`, `stroke`, `uv_coords`, `button_size` undefined) | NOT EXTRACTED | S8 |
| 3 | alive.md:102-111 + 117-134 | js | `telemetryState` + `LayaWebAgent.predict` | Text telemetry snapshot sent to a reading-mode classifier → `organicScore` | fragment; the package API is unverified | NOT EXTRACTED | S8 |
| 4 | alive.md:148-166 | glsl | focus-glow background shader | `u_organic_reading_score` drives a pulsing sage glow on a cream background | near-complete (`u_resolution` undeclared) | NOT EXTRACTED | S8 |
| 5 | art.md:17-24 | glsl | rounded-box SDF | Inside/outside test against a rounded box | pseudocode | NOT EXTRACTED (the concept appears in widget 01) | S11 |
| 6 | aywa.md:17-57 | yaml | `.github/workflows/deploy.yml` "Deploy Sovereign Monolith Core" | On push and cron every 15 min: copy index.html to dist, `touch` empty data files, deploy to gh-pages | near-complete (runs; behaviour is destructive, see §6) | NOT EXTRACTED. The repo has `.github/workflows/pages-seed-deploy.yml` instead (manual, artifact-only) | S4 |
| 7 | aywa.md:65-96 | wgsl | `TextLinePack{chars: vec4<u>}`, `renderLabelString` | "16-char" label rendering from a storage buffer | fragment, invalid (`vec4<u>` is not a type; loop covers 4 chars) | Superseded: docs `dashboard_layout.wgsl:15-20` declares `array<u32,16>` but never uses it | S7 |
| 8 | aywa.md:104-118 | js | `repoLabelsTextMatrix` + storage buffer upload | Packs ASCII labels into a Uint32Array storage buffer | fragment, syntax error (`[, //` at 107) | Labels exist in `docs/data/moissanite_telemetry.json` (space = 32). No storage buffer is created in docs JS | S7 |
| 9 | baryonic.md:30-86 | js | `class AestheticMixer` | N-way weight normalisation → fused rounding, density, hue, contrast | complete-runnable (hue blend is wrong) | EXTRACTED: `/home/user/weft/docs/assets/js/aesthetic-mixer.js`. Near-identical: adds `setSliceWeight`, renames key `hue_shift`→`hue`, **keeps the linear-hue bug** | S5 |
| 10 | bio.md:126-130 | glsl | nerve-signal snippet | Sine "axon pulse" path | fragment | NOT EXTRACTED | S11 |
| 11 | build.md:25-66 | yaml+python | step "Calculate Advanced Cognitive Telemetry" | Mock owner_ratio, label, Gini (O(n²)), resonance, capture → SYM-2P line → `public/data/telemetry.jsonl` | fragment (mock constants; YAML indent of the `- name` line is off) | Partially, diverged: Gini lives in `weft/runtime/aywa/github_harvester.py:44-55` (rank formula); the other four metrics are absent | S3 |
| 12 | build.md:75-96 | js | `frame` (32-byte pack) | Packs 8 floats (5 new metrics) | fragment | NOT EXTRACTED (docs packs a different 16-float layout) | S1 |
| 13 | build.md:104-168 | wgsl | `OrgTelemetry` v3 + `fragment_main` | Owner → width, capture → sag, label → colour, Gini → stroke, resonance → pulse | fragment (no vertex stage; `mod`, `sdRoundedBox` undefined here) | NOT EXTRACTED | S1 |
| 14 | combine.md:29-31 | text | profile SYM-2P lines `:02:04:000N[s-exp (id …)…]` | Data format for style genes | data sample (hashes truncated) | NOT EXTRACTED (no profiles.jsonl in docs) | S2/S5 |
| 15 | combine.md:41-82 | js | `state` + `frame` with `s_mix` | Two-way style lerp → 12-float / 48-byte pack | fragment (`owner_ratio` missing from state) | NOT EXTRACTED | S5 |
| 16 | core.md:13-417 | html/wgsl/js | "Unbound Master Monolith Core", `class SovereignSystemCore` | WebGPU grid, A–Z/0–5 bitmask labels from storage buffer, circular-hue mixer, watermark, OAuth device flow | near-complete but **non-functional** (see §6: missing DOM ids, `mod`, 35-bit masks, half-screen triangle, mangled OAuth URLs) | NOT EXTRACTED as a whole. `weft/runtime/aywa/index.html` (`SovereignLoomEngine`) is a different Canvas2D-only page that reuses the label-matrix idea | S1, S5, S6, S7 |
| 17 | craft.md:135-137 | text | SYM-2P sample line `:01:03:0042[s-exp …]e3b0…` | Wire format exemplar | data sample | Format implemented in `weft/runtime/aywa/sym2p_codec.py` and `docs/assets/js/sym2p-parse.js` | S2 |
| 18 | craft.md:157-216 | wgsl | `struct Sym2pPacket`, role→colour / action→shape `fragment_main` | Maps role 1/2/3 to blue/green/red and action 1.0 to a pulsing circle, otherwise a box | fragment (no vertex stage) | NOT EXTRACTED (docs parses role and action but never uses them) | S1/S2 |
| 19 | craft.md:268-310 | yaml | `.github/workflows/build-engine.yml` "Compile & Optimize Sentient UI Core" | pip onnxruntime, quantise model, terser main.js, copy wgsl and public, deploy gh-pages | near-complete; questionable (no setup-python; the `python -m onnxruntime.quantization.quantize_model --input_model…` CLI is unverified and probably not real) | NOT EXTRACTED | S4 |
| 20 | craft.md:352-410 | yaml+python | `.github/workflows/synbios-evolution.yml` | cron every 15 min + `repository_dispatch`; `gh api` org repos and open-PR search; tension = PRs/(3·active); SYM-2P → `public/data/telemetry.jsonl`; deploy `public/` | near-complete (`--paginate` breaks `json.load` for orgs with more than one page; deploys only `public/`) | Diverged: `weft/runtime/aywa/github_harvester.py` uses a **hard-coded** table, no API. Run manually through `scripts/sync_pages_seed.py` | S3, S4 |
| 21 | craft.md:451-547 | wgsl | `dashboard_layout.wgsl` v1 (16-byte `OrgTelemetry`) | 4-column grid domain repetition, node masking, hash pulse, tension jitter, teal/orange, glow | fragment (no `vertex_main`, although the main.js in #22 requires it; `mod` is not WGSL; `smin` unused) | Diverged: `docs/assets/shaders/dashboard_layout.wgsl` ≡ `weft/runtime/aywa/dashboard_layout.wgsl` (identical to each other; rewritten) | S1 |
| 22 | craft.md:576-781 | js | `class SynbiosDashboardEngine` (main.js) | WebGPU init, fetch shader, 16-byte uniform, fetch/parse SYM-2P every 30 s, render loop, 2D fallback banner | near-complete (no canvas sizing; no hash check) | Diverged: `docs/assets/js/weft-loom.js` (`WeftLoomEngine`) plus `docs/assets/js/sym2p-parse.js` | S1, S2, S9 |
| 23 | done.md:9-121 | wgsl | `dashboard_layout.wgsl` v2 (adds `vertex_main`) | Full-screen-triangle vertex stage plus the v1 fragment | near-complete; **buggy** (triangle covers only half the screen; `mod`) | Diverged (docs uses a 6-vertex quad `vs_main`/`fs_main`) | S1 |
| 24 | eh.md:11-231 | html/js | index.html viewport template, `SynbiosDashboardEngine` | Loads `shaders/dashboard_layout.wgsl` and `data/telemetry.jsonl`; 15 s poll; resize; fallback | near-complete (inherits #23 bugs) | Superseded by `docs/index.html` + `weft-loom.js` (diverged; docs lacks canvas sizing) | S1 |
| 25 | custom.md:44-73 | js | `frame` (48-byte pack with `currentUser`) | Org telemetry plus personal style vector | fragment | NOT EXTRACTED | S1/S5 |
| 26 | custom.md:81-158 | wgsl | `OrgTelemetry` v4 (12 floats) + personalised `fragment_main` | Density → spacing, rounding → radius, hue → colour wheel, contrast → background | fragment (no vertex; `mod`) | NOT EXTRACTED (docs shader reads only `user_rounding` and `user_contrast`) | S1/S5 |
| 27 | discovery.md:23-362 | html/wgsl/js | "Self-Contained Genetic UI Organism", `class SynbiosEcosystem` | Parses 3 profile strings, builds a slider deck, circular-hue mixer, 48-byte uniform, Export button (`alert`) | near-complete (shader fails to compile on `mod`; half-screen triangle) | NOT EXTRACTED | S1, S5 |
| 28 | discovery.md:402-467 | js | `class SynbiosGitWriteWorker` | GET file SHA → append line → PUT via Contents API to `main` | near-complete (URL mangled: `https://github.com{this.owner}/…`, missing `api.`, `/repos/`, `$`) | NOT EXTRACTED | S6 |
| 29 | discovery.md:530-624 | js | `class SynbiosEdgeOrchestrator` | OAuth Device Flow (via `https://corsproxy.io?`) → token in localStorage → append mutation | near-complete (all endpoints mangled; third-party proxy) | NOT EXTRACTED | S6 |
| 30 | feeed.md:22-92 | js | `class LiveEcosystemSynchronizer` | Cache-busted poll; trailing hash used as a change detector; parses active_nodes, tension, noise | complete-runnable (standalone class, no GPU binding) | Partially, diverged: polling in `weft-loom.js:62-77` and `telemetry-worker.js` (no change detection, no `noise`) | S9 |
| 31 | feeed.md:128-151 | wgsl | `randomNoise2D` + grain composite | Hash-noise grain scaled by `org_tension` | fragment | NOT EXTRACTED | S1 |
| 32 | feeed.md:194-238 | python | `calculate_repository_gini_coefficient` + SYM-2P line | Pairwise-difference Gini; mock data `[450,12,5,2,1]` | complete-runnable (comment claims ~0.83; the actual value is 0.773) | Diverged: `github_harvester.compute_gini` (rank formula) + `sym2p_codec.encode_sym2p_line` | S3, S2 |
| 33 | feeed.md:248-253 | wgsl | stroke snippet | Gini → stroke thickness | fragment (duplicates build.md:154-155) | NOT EXTRACTED | S1 |
| 34 | feeed.md:285-581 | html/wgsl/js | "Pure Procedural Matrix", `SynbiosEcosystem` (digit font) | 5x7 digit bitmask font renders Gini as "0.45" inside each card; tension, Gini and node sliders | near-complete (`mod`; 35-bit masks; half triangle) | NOT EXTRACTED | S1, S7 |
| 35 | feeed.md:621-683 | python | `synbios_harvest.py` | urllib GitHub API: org repos, contributor stats of the most recently pushed repo → Gini; open_issues → tension; writes `public/data/telemetry.jsonl` | near-complete (URLs mangled `https://github.com{org_name}/…`; no handling of the stats-endpoint 202; `open_issues_count` includes PRs) | Diverged: `weft/runtime/aywa/github_harvester.py` keeps the output format but **replaces the API with a static table** | S3 |
| 36 | feeed.md:691-999 | html/wgsl/js | "Complete Sovereign Ecosystem" (tri-module) | Digit font, 2-profile circular-hue mixer, sin·cos "watermark" | near-complete (same shader bugs) | NOT EXTRACTED. The watermark idea reappears in docs `dashboard_layout.wgsl:48-50` | S1, S5, S7 |

**Count: 36 fragment rows** (about 39 raw blocks; #3 groups 2 blocks; the svg toy is omitted).

### Variant lineage (oldest → newest, in thread2 order)

- **Shader / uniform layout drift:**
  - craft #21: 16 B, no vertex stage
  - done #23: 16 B, adds vertex stage
  - build #13: 32 B, 5 org metrics
  - custom #26: 48 B, + style
  - discovery #27: 48 B
  - feeed #34: 32 B (label_state, rounding, density, hue)
  - feeed #36: 32 B (Gini + 4 style)
  - core #16: 32 B (same) + `TextLinePack array<u32,4>` storage
  - aywa #7: "16-char" `vec4<u>`
  - **docs/runtime `dashboard_layout.wgsl`**: 64 B (8 floats + `node_vel_0/1 vec4`), `TextLinePack array<u32,16>` declared but unused

  No two consecutive design versions keep the same field order. The docs layout matches none of them.
- **JS engine:** craft #22 `SynbiosDashboardEngine` → eh #24 (inline) → build #12 / custom #25 / combine #15 (frame patches) → discovery #27 `SynbiosEcosystem` → feeed #34/#36 → core #16 `SovereignSystemCore` → aywa #8 → **docs `WeftLoomEngine`**.
- **Mixer:** combine #15 (2-way lerp; linear hue) → baryonic #9 (N-way; linear hue despite its own text) → discovery #27, feeed #36, core #16 (correct atan2 circular mean). **Docs copies baryonic, the regressed version.**
- **Gini:** build #11 (includes zeros) → feeed #32 (filters zeros; n≤1 → 0) → feeed #35 → runtime rank formula (mathematically equivalent to the pairwise form).
- **Harvester:** craft #20 (gh api, repos + PRs) → build #11 (mock) → feeed #35 (urllib live API) → runtime `github_harvester.py` (hard-coded table; adds suspended-account weighting and a 64-byte binary frame).
- **Deploy:** craft #19 (build-engine → gh-pages) and craft #20 (evolution → gh-pages) → aywa #6 (deploy.yml → gh-pages) → repo `pages-seed-deploy.yml` (manual, artifact upload only, Pages disabled).

---

## 3. Ideas, claims, mechanisms

Format: **name**, `file:line`: claim. [category] *Falsified by:* …

### 3.1 Rendering / UI mechanisms
- **SDF-as-layout**, art.md:13-24, 52-112; anew.md:15. UI elements are signed distance functions evaluated per pixel; min, max and smin give boolean operations; `abs(d)-t` gives outlines. [mechanism] *Falsified by:* nothing; this is textbook. The open question is text, accessibility and hit-testing (create.md:89 itself concedes the text problem).
- **Uniforms as the only control channel**, art.md:28; bio.md:82-85. The model or engine never rewrites shader code; it only updates uniforms 60–120 times per second. [engineering-contract]
- **Zero-input full-screen triangle**, done.md:3, 38-46; eh.md:235-269. Three vertex indices, generated by bit tricks, form one oversize triangle. [mechanism] *Falsified by:* evaluating the given code. It yields (-1,-1), (1,-1), (-1,1), which covers half the viewport. **Prose and code contradict each other** (done.md:39-41 vs done.md:42-43). See §6.
- **Grid domain repetition for N repos**, craft.md:441-556. `floor`/`mod` split the plane into cells; a cell is hidden when its linear index ≥ `active_nodes`. "4, 40 or 400 nodes at locked latency" (craft.md:555). [mechanism] *Falsified by:* frame-time measurement at 400 nodes with a fixed 4-column grid; nodes beyond the visible rows simply fall off-screen.
- **Tension warp**, craft.md:513-525; done.md:97-104. When `org_tension` > 0.1, cards jitter horizontally and the colour shifts teal→orange. [mechanism]
- **Hash-noise "static" grain**, feeed.md:128-151. Grain amplitude = tension × 0.15. [mechanism]
- **"Cryptographic / anti-tamper watermark"**, feeed.md:611, 843-853; core.md:7, 206-210. [vision-language] It is a `sin·cos` moiré. Nothing cryptographic is involved: it is neither keyed nor verifiable. *Falsified by:* inspection.
- **Procedural GPU text (5x7 bitmasks)**, feeed.md:269-433; core.md:132-192. Glyphs are stored as u32 bitmasks, "can never blur" (feeed.md:593). [mechanism] *Falsified by:* 5×7 = 35 bits exceeds 32; the shift `34u - idx` is ≥ 32 for the top rows (see §6). Nearest-sample bitmaps also do alias, so "never blur" is false.
- **Fallback for no-WebGPU**, craft.md:767-773; eh.md:218-221; done.md:128; eh.md:273. [engineering-contract]
- **WebGPU uniform 16-byte alignment**, build.md:72; custom.md:42. [engineering-contract] Correct principle. Implemented as a 64-byte layout in docs.

### 3.2 Telemetry and the SYM-2P protocol
- **SYM-2P line format**, craft.md:131-147. `:RR:AA:SSSS[s-exp (k v)…]<sha256-hex>`: role, action state, sequence, s-expression payload, then a hash with no separator. [engineering-contract] *Falsified by:* round-trip tests. Ambiguities are listed in §6.
- **Role archetypes**, craft.md:124. `0x01` Ingest/Sensor, `0x02` Validator, `0x03` Actor. Marked "[cite: 1]", but no source is given. [engineering-contract / unverified]
- **Profile line type**, combine.md:29-31; discovery.md:190-192. Style genes use role `02`, action `04`. [engineering-contract]
- **Hash as data verification / "append-only security"**, craft.md:147; eh.md:305. [vision-language → engineering] The hash is unkeyed SHA-256 of the payload, so it gives integrity against accidental corruption only, not authenticity: anyone can recompute it. *Falsified by:* editing the payload and recomputing the hash; it still validates.
- **Hash as visual seed**, craft.md:147. Hash → micro-jitter seed. [mechanism] Never implemented anywhere.
- **Hash as change detector**, feeed.md:53-60. Skip processing when the trailing hash is unchanged. [mechanism] Sound.
- **"Position-checked" packets**, combine.md:27; build.md:23. [vision-language] Parsers slice fixed offsets but never validate the colons or lengths.
- **Line length**: "101-byte" (craft.md:25), "80-character" (discovery.md:14), "70-character" (combine.md:102). [contradiction] A line with a 64-hex hash plus a payload is always more than 80 characters.
- **Telemetry fields so far**, eh.md:286-316. active_nodes, open_prs, org_tension; role/action/sequence/payload/hash; three uniforms. [engineering-contract summary]
- **Five advanced dimensions**, build.md:9-17. Ownership (LOC ratio), Labels (categorical 0/1/2), Gini of 30-day commits, Resonance (fix-to-author link graph), Capture (contributors' activity in other OSS projects). [mechanism / engineering-contract] *Falsified by:* attempting to compute Resonance and Capture from the GitHub API. No algorithm is given, and the code hard-codes 0.62 and 0.35 (build.md:53, 56).
- **Tension index**: craft.md:392 uses open_prs/(3·active_repos); feeed.md:665 uses open_issues/(5·active_nodes). [contradiction] The runtime uses a third formula based on suspended seats and the issue/PR ratio (`github_harvester.py:66`).
- **Gini as bus factor**, feeed.md:185-191. 0 means equal; "1.0 = one developer wrote 100%". [theory] *Falsified by:* the code returns 0.0 when n ≤ 1 (feeed.md:207-208, 636), so a single-author repo reads as perfectly *safe*. The pairwise formula also caps at (n-1)/n. Its example claims "~0.83" (feeed.md:230); the true value is 0.773.
- **Behavioural "System 1" classification**, alive.md:7-37, 88-134. A ~421M non-autoregressive model classifies emotion or reading mode in 30–70 ms in-tab. [mechanism / unverified external] *Falsified by:* benchmarking `@r4ai/laya-web` (existence and API not verified offline). alive.md:174 also names `laya-system-one`.
- **Reading reward loop**, alive.md:136-166; anew.md:34-35. Deep reading dilates line-height, warms the background and adds a glow; skimming compresses the layout. [mechanism / product] *Falsified by:* A/B testing whether the "reward" changes reading behaviour. Ethics and consent are not discussed.
- **Privacy by locality**, alive.md:174; anew.md:47; anew.md:129. Telemetry never leaves the device. [governance claim] Holds only if no third-party assets load. The docs widgets violate this (§5).

### 3.3 Architecture / hosting
- **Static hosting suffices**, anew.md:64-129; craft.md:99, 322-428. "10M visitors, $0" (anew.md:127). [engineering-contract] *Falsified by:* GitHub Pages bandwidth and size limits, and the impossibility of COOP/COEP headers (needed for SharedArrayBuffer) on Pages.
- **Weights as static assets**, anew.md:95-101; craft.md:83-86, 244-249. ONNX weights are downloaded like images and quantised to 8 or 4 bits for "~75% smaller" (craft.md:249). [engineering-contract] *Falsified by:* a 421M model at 4 bits is about 210 MB. GitHub Pages recommends sites under 1 GB, rejects files over 100 MB in git, and has soft bandwidth limits. The claim of instant loading does not hold.
- **Sandbox retraction (honest translation table)**, craft.md:54-99. Shared memory pages become SharedArrayBuffer + WASM; "cellular processors" become Web Workers + WebGPU compute; "living interface" becomes SDF on a canvas. [vision-language → mechanism map] **This is the model for separating aspiration from mechanism.** It contradicts craft.md:43 and anew.md:47 ("Apple Silicon SharedMemory bus … inside the client tab").
- **Repository as database**, discovery.md:5, 13-15, 368; craft.md:426. [architecture] *Falsified by:* concurrent writers. Contents-API PUT with a stale `sha` returns 409, and the clients do not retry.
- **Cache-busted polling vs SSE relay**, feeed.md:7-12. Polling gives 15–30 s latency at no cost; a Cloudflare/Vercel worker SSE relay gives sub-second latency. [engineering option / roadmap-branch]
- **Worker offload threshold**, craft.md:790. Move parsing to a Web Worker past 500 repos. [engineering-contract]
- **Offline-first content-addressed cache**, craft.md:258-260. Fingerprinted assets plus "offline-first cache behaviors we discussed". [engineering-contract] Never specified.
- **CI shader validation (tint/glslang)**, craft.md:251-256. [engineering-contract] Would have caught `mod`, `vec4<u>` and the half-screen triangle at build time.

### 3.4 Social / governance / economics
- **Style genes and barycentric mixing**, combine.md:1-104; baryonic.md:1-102; custom.md:1-168. Aesthetic vectors are shared as text "strands", mixed with normalised weights, "democratic confluence" (baryonic.md:100). [mechanism / governance-flavoured]
- **Developer taste extraction**, custom.md:1-36. Scrape public repos (CSS, `.vscode/settings.json`) into a four-float vector. [mechanism] *Falsified by:* no extraction algorithm is given; the Python parser is only offered (custom.md:172). **Privacy and consent issue:** this profiles individuals from their personal repositories.
- **Git signature identification**, custom.md:5, 21, 42. "The browser runtime extracts their unique cryptographic Git signature." [claim] A static page cannot obtain this without authentication.
- **Stigmergic software**, discovery.md:378-481, 628-637. Committed preference lines become "public environmental DNA". The evolution workflow recomputes org averages and every visitor's canvas shifts. [governance / mechanism] *Falsified by:* (1) Contents-API writes need push permission, so ordinary visitors cannot write; (2) no workflow in the corpus reads profiles.jsonl to compute averages (craft #20 reads only repos and PRs).
- **On-chain alignment settlement**, converge.md:39-44. A "Tension Fracture" is verified and settled on an Arbitrum Stylus WASM ledger; deep-reading flow raises `live_match_pct` and "stream[s] protocol capital … into the `weaver_capital_vault`". [economics / governance] Paying for user attention is a product-ethics and regulatory issue. No mechanism is given. It links to `weft/runtime/ledger/*.sol`, which I did not compare because there is no code here.
- **Lineage Alpha (Safe) vs Beta (Bold)**, converge.md:32-37; craft.md:35-39. Two competing workers or models. The winner, by `loss_A` vs `loss_B` norms, drives the shader. Alpha favours clarity and spacing; Beta favours density. [mechanism / vision-language] *Falsified by:* no loss is defined for UI fitness. In docs this collapses to `alpha = 0.52 + scroll_jitter*0.2` (`weft-loom.js:110`).
- **Human attention as thermal load**, converge.md:24-28. Erratic input acts like thermal throttling and drives LoRA updates (`lora_A`, `lora_B`). [vision-language]

### 3.5 Vision-language (record and contrast)

| term | where | aspires to | actual mechanism in code |
|---|---|---|---|
| "organism", "living tissue", "membrane" | aywa.md:3; discovery.md:371; craft.md:21 | self-maintaining adaptive system | a fragment shader plus a 15–45 s file poll |
| "chromosome / gene / strand / DNA" | combine.md:1; baryonic.md:12; discovery.md:388 | heritable recombinable traits | 4-float style vector; weighted mean |
| "mitosis / cell division" | bio.md:120 | growth by division | two circle SDFs with smin |
| "homeostasis" | bio.md:136; feeed.md:102, 160; discovery.md:479 | self-regulation | tension uniform drops to 0 when issues close |
| "stigmergy" | discovery.md:471-481 | indirect coordination through the environment | appending a line to a repo file (requires write access) |
| "nervous system / motor neurons / muscle" | bio.md:18-25, 70-90 | layered control | event listeners → model → uniforms → GPU |
| "self-healing / regrow" | anew.md:41; craft.md:28-31; create.md:20-28 | NCA repair | none in Weft code; widget 04 is a toy |
| "sovereign", "sterile seed package" | aywa.md:52; craft.md:43, 305 | autonomy, purity | static files on a third-party CDN |
| "cryptographic watermark", "anti-tamper" | feeed.md:611; core.md:206 | tamper evidence | decorative sin·cos pattern |
| "cryptographic identity" roles | craft.md:122 | authenticated agents | two-digit numbers |

### 3.6 Hardware / external-model claims (unverified; flag for fact-check)
- **Inkling 2 Small**, feel.md:94-122. 594B MoE with 17B active; autoresearch on a Qwen 3.5 4B base, 4.5 h, $426; 75-step convergence. [external claim] **Contradiction:** anew.md:41 casts Inkling 2 as a per-visitor "local edge" intent engine, but feel.md:117 describes a 594B cloud model.
- **Laya**, alive.md:1-15, 175. 421M parameters, ModernBERT backbone, 30–70 ms in-tab, "optimized for 8-bit or 4-bit ONNX". [external claim]
- **NCA facts**, create.md:11-15, 45, 62, 76, 80. About 8k parameters per cell (create.md:11) vs "~20 KB" (create.md:45): 8k float32 is about 32 KB. Houdini Copernicus NCA nodes; NCAtorch. [external]
- **GPU facts**, arrival.md:59-96. 384-bit bus, >1 TB/s. [hardware; broadly correct]

### 3.7 Safety-relevant items (locations only, no values copied)
- **core.md:263**: hard-coded literal OAuth App `client_id`, commented "Public system proxy identity anchor". It is a public identifier, not a secret, but the owning app is unknown. Do not reuse it. The same value appears at thread2:4835.
- **core.md:262, discovery.md:543**: OAuth Device-Flow token exchange is routed through **third-party `corsproxy.io`**, so GitHub access tokens transit an unknown proxy. **High risk.** At core.md:262 the scheme is also missing, so the URL is relative.
- **core.md:364, discovery.md:553**: `scope=public_repo` grants write access to all of the user's public repos. Over-broad.
- **core.md:350, 379; discovery.md:540, 577**: access token persisted in `localStorage` (exfiltratable by any XSS, including the third-party widget scripts on the same origin; see §5).
- **discovery.md:418, 443, 593, 608**: browser code commits directly to branch `main` with a bearer token.
- **craft.md:372**: `secrets.ORG_GITHUB_TOKEN` (a reference only). **feeed.md:679**: `GITHUB_TOKEN` from the environment.
- **aywa.md:22-28**: cron every 15 min plus `contents: write`, `pages: write`, `id-token: write`. **craft.md:355-361**: cron every 15 min plus `contents: write`. These are instructions to auto-deploy live on a schedule.
- **converge.md:41-44**: on-chain settlement and capital streaming (financial). No addresses or keys.
- **Not in my files but surfaced by the Pages check**: `docs/data/moissanite_telemetry.json` and `weft/runtime/aywa/github_harvester.py:39-42` publish two named GitHub logins labelled "SUSPENDED", with impact text, on the public site. This is a privacy and reputational risk. The same files present *synthetic* commit, PR and issue counts as org "telemetry" (fabricated-data risk if shown as real).
- No private keys, RPC URLs or mainnet addresses appear in these 19 files.

---

## 4. Candidate software systems

**S1. Aywa / Synbios WebGPU dashboard renderer**
- Purpose: render org repos as SDF cards on a full-screen canvas, modulated by telemetry and style uniforms.
- Inputs: shader file, `data/telemetry.jsonl`, style vector, sliders. Outputs: pixels.
- Interfaces: S2 (parse), S3 (data file), S5 (style uniforms), S7 (label storage buffer), S9 (sync).
- Fragments: #12, 13, 16, 18, 21-27, 31, 33, 34, 36.
- Dependencies: WebGPU, WGSL, vanilla JS (no libraries).
- Extracted as `docs/index.html`, `docs/assets/js/weft-loom.js`, `docs/assets/shaders/dashboard_layout.wgsl` (≡ `weft/runtime/aywa/dashboard_layout.wgsl`). This is the core system; most other systems feed it.

**S2. SYM-2P codec / wire protocol**
- Purpose: compact line format with role, action, sequence, s-expression metrics and SHA-256.
- Producers: Python in workflows and harvester. Consumers: JS in the browser.
- Fragments: #14, 17, 20, 22, 32, 35.
- Extracted as `weft/runtime/aywa/sym2p_codec.py` and `docs/assets/js/sym2p-parse.js`. Separate and reusable: it is the contract between S3 and S1/S5. The protocol is attributed to an external "Moissanite-Labs abios" repo (craft.md:1, 114), so this may duplicate a spec held elsewhere.

**S3. GitHub org telemetry harvester / ingest workflow ("synbios-evolution")**
- Purpose: compute active_nodes, tension, Gini (plus owner, label, resonance, capture) from the GitHub API and write telemetry.jsonl.
- Fragments: #11, 20, 32, 35.
- Dependencies: Python 3, `gh` CLI or urllib, a GitHub token.
- Extracted (diverged, static) as `weft/runtime/aywa/github_harvester.py`. Separate from S1; shares S2.

**S4. Build / deploy pipeline**
- build-engine.yml: ONNX quantisation, terser, shader copy, gh-pages. deploy.yml: cron redeploy.
- Fragments: #6, 19, 20 (deploy step).
- Repo equivalent: `.github/workflows/pages-seed-deploy.yml` + `scripts/sync_pages_seed.py` + `weft/runtime/aywa/site_selftest.py`. The design's three workflows all target branch `gh-pages` and would overwrite each other (§6). The repo serves from `docs/`, so the deploy model differs from the design.

**S5. Aesthetic genome / barycentric style mixer ("chromosome deck")**
- Purpose: per-developer style vectors in `profiles.jsonl`, N-way normalised mix with circular hue, slider deck, export strand.
- Fragments: #9, 14, 15, 25, 26, 27, 36, 16.
- Extracted: only the mixer class (`docs/assets/js/aesthetic-mixer.js`, regressed hue). No deck, profiles file or export. Feeds S1 uniforms. Its write path is S6.

**S6. Serverless Git write-back + GitHub OAuth Device Flow**
- Purpose: let visitors commit strands to the repo from the page.
- Fragments: #28, 29, and the auth parts of #16.
- Dependencies: GitHub REST Contents API, OAuth device flow, a CORS proxy.
- NOT EXTRACTED. Security-sensitive (§3.7). Needs a threat model before any build. A separate system, probably better as a GitHub App, a fork-and-PR flow, or an issue-form → Action pipeline.

**S7. Procedural GPU typography**
- 5x7 bitmask glyphs (digits; A–Z plus 0–5) and ASCII labels in a storage buffer (4 → "16" chars).
- Fragments: #7, 8, 16, 34, 36.
- NOT EXTRACTED. The docs shader declares `labelData` but no glyph code exists. A sub-module of S1.

**S8. Laya "System 1" behavioural classifier + reading-reward shader**
- Purpose: in-tab model inference over scroll, jitter and dwell telemetry → `organicScore` / `u_frustration` uniforms.
- Fragments: #1-4.
- Dependencies: ONNX Runtime Web or `@r4ai/laya-web` (unverified), WebGPU or WASM, a Web Worker.
- NOT EXTRACTED. Separate from S1 but feeds it through uniforms. Docs has only a crude scroll-jitter proxy.

**S9. Live ecosystem sync**
- Cache-busted polling with hash change-detection; optional SSE relay on a serverless edge function.
- Fragments: #22 (poll), 24, 30.
- Extracted partially in `weft-loom.js:62-77, 79-100` and `docs/assets/workers/telemetry-worker.js` (no change detection). A thin layer over S2.

**S10. NCA self-healing UI**
- Concept in create.md and feel.md:1-27 (the CPU Canvas2D widget). No code in my files.
- Corresponds to `docs/widgets/04-neural-cellular-automata.*` and `weft/browser-sources/widgets/04-*`.

**S11. Educational SDF / biology sandboxes**
- art.md (shader sandbox, SDF visualiser) and bio.md (procedural biology simulation). Snippets #5, #10.
- Map loosely to widgets 01 (SDF/Laya typography), 02 (mind palace) and 03 (morphogenetic field). This is my inference; the widget-to-turn mapping is not stated.

**S12. Mac harness ↔ UI fusion (lineages, ledger hook)**
- converge.md (no code). References `weft_singularity_core.py` components that live in other corpus files (`weft/test.md`, `ult.md`, `launch.md`, etc.) and `weft/runtime/mac/*`, `weft/runtime/ledger/*`.
- Shares logic with the Mac harness and ledger systems inventoried elsewhere.

---

## 5. Documents implied

### 5.1 Documents contained or called for
1. **SYM-2P wire-format spec**, from craft.md:120-147, eh.md:296-305, combine.md:27-31, build.md:11-17. Close to a spec table, but it must resolve: hex vs decimal fields, separators, the hash scope (brackets included: yes in the codec), key vocabulary (`tension`/`gini` vs `con`/`owner`/`lbl`/`res`/`cap`), the role-02/action-04 profile type, the max line length, and what "position-checked" validation means.
2. **Dashboard technical spec (Aywa renderer contract)**: one uniform layout, shader entry points, data paths, fallback behaviour, metric-to-visual mapping (build.md:9-17 is close to final for that table).
3. **Telemetry metric definitions**: build.md:9-17 + eh.md:286-316 + feeed.md:185-191. Needs real algorithms for Resonance and Capture and one tension formula.
4. **Pages-site requirements** (below) plus a **deployment/CI spec** (S4), reconciling `gh-pages`-branch deploys with the `docs/` folder model.
5. **Security and threat model for auth/write-back (S6)**: missing and required. It must cover the corsproxy, token storage, scopes, branch protection, and who may write `profiles.jsonl`.
6. **Privacy and consent policy**: behavioural/emotion telemetry (alive.md), developer taste profiling (custom.md), publishing named suspended accounts (docs data), and third-party widget scripts.
7. **Vision essays / manifestos**, nearly finished as prose:
   - anew.md: "The Document Prison" and "Infrastructure Inversion". A finished-quality manifesto.
   - feel.md:33-89: "Post-App World".
   - bio.md: "Anatomical Mind Palace". A finished-quality explainer and glossary.
   - art.md and arrival.md: SDF and GPU primers.
   - create.md: NCA background.
8. **Vision-language glossary**: craft.md:62-68 is the template (sci-fi phrase → real API → why it is safe). Extend it with the §3.5 table.
9. **Governance note on stigmergic contribution** (discovery.md:471-481): who may write, moderation, revocation.
10. **Economics white-paper branch**: converge.md:39-44 (attention-linked rewards on the ledger). Speculative; needs a ethics and regulatory review.
11. **Roadmap branches**:
    - Laya/ONNX System-1 integration (alive, anew, craft:83).
    - SSE relay (feeed:12).
    - WASM interaction-net documentation runtime (craft.md:26: "the site *is* the protocol interpreter").
    - NCA layout (create).
    - tint validation in CI (craft:255).
    - Offline content-addressed cache (craft:258).
    - Multi-user personalisation (custom).
    - Procedural text (feeed/core).

### 5.2 Pages-site requirements

"All guiding direction should be inside the design folder." Below is every concrete requirement my 19 files set for the GitHub Pages site, checked against the actual `/home/user/weft/docs/` tree (index.html, assets/js/{weft-loom, sym2p-parse, aesthetic-mixer}.js, assets/workers/telemetry-worker.js, assets/shaders/dashboard_layout.wgsl, data/{telemetry.jsonl, moissanite_telemetry.json, .bin}, widgets/, seed-manifest.json, .nojekyll) and `.github/workflows/pages-seed-deploy.yml`.

Legend: **YES** = satisfied; **PARTIAL** = partly satisfied; **NO** = absent; **CONFLICT** = docs contradicts the design or the design cannot be met on Pages.

**A. Hosting model and structure**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P1 | Pure static hosting: no server, backend or database; all compute client-side | anew.md:66-70, 74-81, 91; craft.md:99, 324-328; build.md:3 | **YES**. Only static files. |
| P2 | Layout: `index.html`, `main.js`, `shaders/ui_core.wgsl`, `public/models/laya_421m.onnx`, `public/models/tokenizer.json` | anew.md:113-123 | **PARTIAL**. Has index.html, `assets/js/weft-loom.js`, `assets/shaders/dashboard_layout.wgsl`. **No models or tokenizer.** Paths differ (`assets/…`). |
| P3 | Data at `data/telemetry.jsonl`, fetched by the page | craft.md:401, 778; eh.md:225; aywa.md:49 | **YES**. `docs/data/telemetry.jsonl`, one line. (The design's workflows *write* to `public/data/…`, an internal inconsistency.) |
| P4 | Profiles ledger `data/profiles.jsonl` (`:02:04:NNNN[s-exp (id …)(rounding …)(density …)(hue …)(contrast …)]hash`) | combine.md:12, 27-31; discovery.md:13, 408; aywa.md:50 | **NO**. |
| P5 | Shader served as a separate file at `shaders/dashboard_layout.wgsl` and fetched at runtime | craft.md:632, 778; eh.md:111, 225 | **YES** (at `assets/shaders/…`, with an inline WGSL fallback in `weft-loom.js:4-21`). |

**B. Rendering**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P6 | Full-screen `<canvas>` rendered by a WebGPU fragment shader with SDF cards | craft.md:88-91, 441-547; done.md; eh.md:11-58 | **YES**, with a defect. `weft-loom.js` renders via WebGPU but **never sets `canvas.width/height`** in the WebGPU path (`initializeWebGPU`, `weft-loom.js:118-148`). The backing store stays at the 300×150 default and is stretched (blurry). There is no DPR or resize handling, although eh.md:99-102 and 144-147 require them. |
| P7 | Zero-vertex-buffer full-screen pass (`vertex_main`/`fragment_main`, `draw(3)`) | done.md:31-49; eh.md:235-269; craft.md:789 | **PARTIAL**, intentionally different. Docs uses a 6-vertex quad `vs_main`/`fs_main`, `draw(6)` (`dashboard_layout.wgsl:27-37`; `weft-loom.js:188`). This avoids the design's half-screen bug, but entry-point names differ from every design JS. |
| P8 | Grid with node masking by `active_nodes`, 4 columns, per-cell hash pulse | craft.md:481-511 | **PARTIAL**. 5-column offset grid (`dashboard_layout.wgsl:52-59`). No per-cell hash pulse. |
| P9 | Tension → jitter warp + teal→orange colour + glow intensity | craft.md:513-544; done.md:97-117; discovery.md:164-170 | **PARTIAL**. Tension scales the glow and tints card interiors toward red (`dashboard_layout.wgsl:61-65`). **No jitter warp.** |
| P10 | Five advanced dimensions (owner_ratio → aspect, label_state → colour, Gini → stroke, resonance → pulse, capture → sag) | build.md:9-17, 104-167 | **NO**. The shader has a `gini_index` field but **never reads it**. Owner, label, resonance and capture are absent. JS folds Gini into the tension uniform via `blendTension` (`weft-loom.js:153-155`), which conflates two metrics. |
| P11 | Personal style uniforms (rounding, density, hue, contrast) drive radius, spacing, colour wheel and background | custom.md:29-36, 109-154; discovery.md:145-180 | **PARTIAL**. Only `user_rounding` and `user_contrast` are read (`dashboard_layout.wgsl:50, 60`). `user_density` and `user_hue` are packed but unused. |
| P12 | Barycentric N-way mixer with **circular (atan2) hue mean** | baryonic.md:69-94 (the stated intent); core.md:269-279; discovery.md:226-249; feeed.md:903-915 | **CONFLICT**. `docs/assets/js/aesthetic-mixer.js:32-38` copies baryonic.md's linear angle average, which produces the colour-wheel crossing artefact baryonic.md:94 says it prevents. Currently masked because the shader ignores hue. |
| P13 | Interactive mixing deck (per-profile sliders) and "Export Strand" button | combine.md:108-109; baryonic.md:104; core.md:80-91; discovery.md:93-104, 251-277 | **NO**. No controls. The HUD is `pointer-events: none` (`docs/index.html:15`). |
| P14 | Tension, Gini and node sliders (telemetry injector HUD) | feeed.md:324-339; core.md:70-78 | **NO** (no controls). |
| P15 | Procedural GPU text: digit font for metric values and ASCII repo labels (16 chars) from a storage buffer | feeed.md:269-433, 587-593; core.md:132-192, 423; aywa.md:61-118 | **NO**. The shader header claims "Procedural ASCII SDF Shader" and declares `labelData : array<TextLinePack{array<u32,16>}>` at binding 1 (`dashboard_layout.wgsl:1, 15-20`), but no glyph code exists and JS creates no storage buffer. Labels appear only in the Canvas2D fallback via `fillText` (`weft-loom.js:209-212`). |
| P16 | Background "watermark" moiré modulated by tension | feeed.md:843-853; core.md:206-210 | **PARTIAL**. A sin·cos grid exists (`dashboard_layout.wgsl:48-50`) at fixed 0.02 opacity, **not tension-modulated**. |
| P17 | Tension-scaled noise grain | feeed.md:128-151 | **NO**. |
| P18 | SYM-2P role/action bytes mapped to colour and shape | craft.md:141-215 | **NO**. Parsed (`sym2p-parse.js:10-12`), never used. |
| P19 | Graceful no-WebGPU fallback (banner, or Canvas2D grid for legacy/mobile) | craft.md:767-773; eh.md:37-58, 218-221; done.md:128; eh.md:273 | **YES**. `fallback2d()` draws a labelled grid (`weft-loom.js:193-223`). On phone widths the fixed offsets (`x = 60 + c*240`) overflow the screen. |
| P20 | 60–120 FPS render loop; heavy parsing off the main thread past 500 repos | craft.md:568, 790; discovery.md:369 | **YES** for the rAF loop. A worker exists. Never measured. |

**C. Telemetry, data and model**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P21 | Client SYM-2P positional parser | craft.md:676-711; eh.md:150-172 | **YES** (`sym2p-parse.js:1-24`; also duplicated in `telemetry-worker.js:18-29`). |
| P22 | Hash validator that **rejects** corrupted lines before they touch uniforms | build.md:175; discovery.md:486; craft.md:147 | **PARTIAL**. `verifySym2pLine` computes SHA-256 correctly (the seed line validates; I recomputed it). But (a) it returns `true` when the hash is absent (`sym2p-parse.js:39`); (b) `fetchSym2p` applies metrics *regardless* and only labels the HUD "unverified" (`weft-loom.js:69-73`); (c) the worker path applies metrics with **no verification** (`telemetry-worker.js:34-36`). |
| P23 | Hash-based change detection to skip unchanged packets | feeed.md:53-60 | **NO**. |
| P24 | Cache-busted polling every 15 s (eh.md:176; feeed.md:84) or 30 s (craft.md:719) | as cited | **PARTIAL**. Cache-busting is done (`?t=Date.now()`), but intervals are **45 s** (`weft-loom.js:230`) and **60 s** (`weft-loom.js:98`). Two redundant pollers fetch the same file. |
| P25 | Optional SSE webhook relay for sub-second updates | feeed.md:12 | **NO** (optional; it would need a non-Pages edge function). |
| P26 | SharedArrayBuffer + Web Worker zero-copy telemetry bridge | craft.md:66, 76-81, 103 | **CONFLICT / not satisfiable on Pages.** GitHub Pages cannot send COOP/COEP headers, so `SharedArrayBuffer` is unavailable. `weft-loom.js:80-84` catches this and falls back to postMessage. The worker writes floats into the SAB (`telemetry-worker.js:7-13`) but **the main thread never reads it**. The HUD text "Initializing WebGPU / SharedArrayBuffer telemetry bridge…" (`docs/index.html:25`) overstates this. Fixing it requires a service-worker cross-origin-isolation shim or a non-Pages host. |
| P27 | Rich behavioural telemetry: scroll velocity, direction changes, mouse jitter variance, dwell per section, text selection, rolling 5-second windows | alive.md:98-111; anew.md:17, 32-35; bio.md:11, 70-73; craft.md:25, 80 | **PARTIAL (minimal)**. Only a scroll-delta EMA (`weft-loom.js:102-116`). The page **cannot scroll** (fixed full-viewport canvas, no flowing content), so `scroll_jitter` stays at 0. No pointer, dwell or selection telemetry. |
| P28 | Local model inference (Laya / ONNX Runtime Web, WebGPU or WASM, in a worker), weights served as static assets, quantised | alive.md:3, 14, 117-134, 175; anew.md:95-101; craft.md:83-86, 244-249 | **NO**. No model, runtime or tokenizer. |
| P29 | Reading-reward responses: line-height dilation, cream background, focus glow behind the active paragraph; compression when skimming | alive.md:136-166; anew.md:33-35 | **NO**. The page has no reading content. |
| P30 | Two competing lineage workers (Alpha Safe / Beta Bold); the winner drives shader uniforms | craft.md:35-39; converge.md:32-37 | **NO / misrepresented**. There is a single scalar `lineage_alpha_confidence = 0.52 + scroll_jitter*0.2` (`weft-loom.js:110-112`), with no workers or models. The meta description advertises "lineage workers" (`docs/index.html:6`). |
| P31 | Telemetry comes from a **live** GitHub ingest (org repos, PRs/issues, contributor stats), refreshed every 15 min by Actions | craft.md:348-410; feeed.md:617-683; build.md:21-66; eh.md:288 | **NO**. `docs/data/*` is produced by `weft/runtime/aywa/github_harvester.py` from a **hard-coded** 19-repo table (commit, PR and issue counts are constants), run manually through `scripts/sync_pages_seed.py`. The site shows static numbers as "telemetry". |

**D. Privacy, auth and governance**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P32 | Privacy and sovereignty: behaviour never leaves the device; zero network beyond the static host | alive.md:174; anew.md:47, 129; craft.md:35 ("zero network calls") | **PARTIAL / CONFLICT**. The main page makes only same-origin fetches (YES). But `docs/widgets/0{1..5}-*.html` are Google AI-Mode sandbox exports. Each has an injected CSP and sandbox script (`data-sandbox-injected`, cross-frame handshake, posts `HTML_CHANGED` with full `outerHTML` to the parent) and imports React and Radix from `https://widgetlibs.static.usercontent.goog/…` plus Google Fonts. `widgets/index.html:27` nonetheless says "zero network". Those hashed Google URLs may stop resolving. Because the widgets are same-origin iframes, any token in localStorage (P34) would be exposed to these scripts. |
| P33 | Visitors authenticate by GitHub OAuth Device Flow inside Pages | discovery.md:492-585; core.md:93-98, 356-385 | **NO**. This is a reasonable deferral given the corsproxy, scope and token-storage risks (§3.7). The design treats it as a requirement. |
| P34 | Write-back: visitors append strands to the profiles ledger, which triggers an Actions recompute so every visitor's canvas shifts (stigmergy) | discovery.md:378-481, 628-637 | **NO**. There is also no workflow anywhere that consumes `profiles.jsonl`. |
| P35 | Persist chosen style profiles in localStorage between sessions | combine.md:104; aywa.md:126 | **NO**. |
| P36 | Per-user personalisation keyed to Git identity | custom.md:5, 21, 42, 162-168 | **NO**. |

**E. CI and deploy**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P37 | CI `build-engine.yml`: quantise ONNX, minify JS (terser), copy and minify WGSL, validate shaders (tint/glslang), fingerprint assets, deploy to `gh-pages` | craft.md:236-310 | **NO**. The repo workflow runs `sync_pages_seed.py` + `site_selftest.py` and uploads an artifact (`pages-seed-deploy.yml`). `site_selftest.py:94-97` only checks that the strings "@vertex"/"@fragment" occur; it does not compile WGSL. |
| P38 | Ingest workflow `synbios-evolution.yml`: cron every 15 min + `repository_dispatch: repo_activity`, `ORG_GITHUB_TOKEN`, deploy | craft.md:352-410 | **NO** (intentionally gated: "manual only … while GitHub Pages is off", `pages-seed-deploy.yml:2`). |
| P39 | `deploy.yml`: on push + cron every 15 min, `contents/pages/id-token: write`, JamesIves to `gh-pages` | aywa.md:17-57 | **NO / CONFLICT**. The repo uses a `docs/` folder model, not a `gh-pages` branch. Pages is not enabled. |
| P40 | Content-addressed fingerprinting + offline-first cache (returning visitors load from device) | craft.md:258-260; anew.md:81 (IndexedDB) | **NO**. No service worker, hashed filenames or IndexedDB. |

**F. Product intent**

| # | Requirement | Source | Status in docs/ |
|---|---|---|---|
| P41 | The documentation site *is* the protocol runtime: an interaction-net interpreter (WASM) draws the page; NCA-style layout regrows on resize | craft.md:5, 13-31 | **NO**. Widget 05 (IC net) and widget 04 (NCA) are separate iframe toys. |
| P42 | No Jekyll interference | implicit for raw assets | **YES** (`docs/.nojekyll` present). |
| P43 | Responsive layout: aspect correction | design hard-codes 16:9 `1.7777` (craft.md:479 and others) | **PARTIAL**. Docs hard-codes `p.x *= 1.6` (`dashboard_layout.wgsl:47`). Neither adapts to the real viewport aspect. |

**Tally:** 43 requirements:
- **YES: 8** (P1, P3, P5, P6 with a defect, P19, P20, P21, P42)
- **PARTIAL: 11** (P2, P7, P8, P9, P11, P16, P22, P24, P27, P32, P43)
- **CONFLICT: 3** (P12 mixer regression, P26 SharedArrayBuffer impossible on Pages, P39 gh-pages branch vs docs/ folder)
- **NO: 21** (P4, P10, P13-15, P17, P18, P23, P25, P28-31, P33-38, P40, P41) The docs seed is a faithful *skeleton* of S1, S2 and S9, plus the regressed S5 mixer. It is not the system the design describes. The largest gaps are no live data, no model, no controls or text, and claims in page metadata that the code does not back.

**Corpus sections already close to a finished document:** anew.md (manifesto); bio.md (explainer and glossary); craft.md:54-99 (honest-translation essay); build.md:9-17 + eh.md:286-316 (metrics spec table); craft.md:131-147 (SYM-2P table, which needs a disambiguation pass).

---

## 6. Open questions / gaps (including code that contradicts the prose)

### 6.1 Code bugs that contradict "complete / production-ready" claims
1. **Half-screen "full-screen triangle".** `x = f32(i32(vid<<1u)&2)-1; y = f32(i32(vid&2u))-1` gives (-1,-1), (1,-1), (-1,1), which covers only the lower-left half of the viewport. The prose (done.md:39-41; eh.md:263-265) says (3,-1) and (-1,3), which needs `*2.0` (e.g. `f32((vid<<1)&2)*2-1`). The same code is in done.md:42-43, eh (via done), discovery.md:127-128, feeed.md:359-360 and 784-785, and core.md:125-126. Docs avoids it with a 6-vertex quad.
2. **`mod()` is not a WGSL builtin.** WGSL has `%` on floats, or one can write `x - y*floor(x/y)`. Affected lines: craft.md:489, done.md:77, build.md:128, custom.md:115, discovery.md:149, feeed.md:449 and 859, core.md:216. **None of the design shaders compile.** craft.md:554-555 builds its explanation on `mod`. Docs uses floor arithmetic instead (`dashboard_layout.wgsl:54`).
3. **35-bit glyph masks in a u32.** feeed.md:398 and 812 and core.md:178 shift by `34u - (row*5+col)`. Indices 0–2 give shifts of 32–34, which are invalid in WGSL (a compile error for constants; masked or undefined at runtime). The bitmask literals are below 2^29 (e.g. 504443199), so the top rows can never light. No generator for the masks is given, so their correctness is unverifiable. feeed.md:589-593 claims crisp text.
4. **core.md boots into an exception.** `bindHUDEvents` calls `document.getElementById("slider-nodes")` and `"val-nodes"` (core.md:334-337), but those elements do not exist in its HTML (core.md:70-98). The resulting TypeError aborts `bindHUDEvents`, so `startClock()` (core.md:321) never runs and nothing renders. The file still claims "No abstractions. No placeholders." (core.md:427). The "complete alphabet" covers A–Z and digits 0–5 only (core.md:137-168). Digits 6–9 and punctuation, such as the "-" that the later 16-character labels need, render blank. Only 4 of the 8 label rows ever show, because `active_nodes` = 4 (core.md:261).
5. **ASCII 60 used as "space".** core.md:169 and aywa.md:106-108 use 60, which is `<`, not space (32). Docs data uses 32 correctly.
6. **aywa.md WGSL/JS is invalid.** `vec4<u>` (aywa.md:72); the comment says "16-character" but the loop handles 4 characters (aywa.md:86-93); the JS array literal is broken `[, //` (aywa.md:107); the struct holds 4 u32 per slot while JS packs 16 per slot (aywa.md:108), so strides mismatch.
7. **Missing vertex stage.** craft.md:157-216 and 451-547, build.md:104-168 and custom.md:81-158 have only a fragment stage, but craft.md:650 requires `vertex_main`, so pipeline creation fails. This is acknowledged only in passing (craft.md:789).
8. **Mixer hue.** baryonic.md:69-75 computes `Σ angle·w` then `/2π % 1`: a *linear* average of angles, the exact failure baryonic.md:94 describes (red 0.0 + violet 0.95 → 0.475, green). discovery.md:239-246 and core.md:275-277 later fix it with atan2. **Docs ships the broken version** (`aesthetic-mixer.js:32-38`). baryonic.md:49-51 also mutates the user's weight (sets slice 0 to 1.0) when all weights are 0.
9. **Gini edge cases.** feeed.md:207-208 and 636 return 0.0 for one contributor (the maximum-risk case reads as minimum risk). The pairwise formula cannot reach 1.0 for finite n. feeed.md:230 claims ~0.83 for its sample (actual 0.773). build.md:35 comments 0.75 while the table at build.md:13 says 0.65.
10. **`synbios-evolution.yml`.** `gh api … --paginate` emits concatenated JSON arrays, so `json.load` fails for orgs with more than 30 repos (craft.md:375, 384). The search API caps results and shares a separate rate limit (craft.md:376). It deploys `folder: public` to gh-pages (craft.md:405-409), so the gh-pages root would contain only `data/` and the site would vanish.
11. **Workflows clobber each other.** build-engine (craft.md:305-309) and evolution (craft.md:405-409) both force-deploy different folders to `gh-pages`, and aywa deploy.yml (aywa.md:52-56) deploys a third. aywa.md:46-50 also `touch`es empty `dist/data/telemetry.jsonl` and `profiles.jsonl`, overwriting harvested data every push and every 15 minutes.
12. **`build-engine.yml`.** It runs `pip install onnxruntime` with no `setup-python` (craft.md:281-289; ubuntu-latest has python, so it may work). The quantisation CLI `python -m onnxruntime.quantization.quantize_model --input_model … --quant_format QOperator` (craft.md:293-296) is, as far as I know, not a real entry point. The real path is the Python API `quantize_dynamic`/`quantize_static`. Needs verification. `src/models/laya_raw.onnx` would be hundreds of MB in git.
13. **Harvester (feeed.md:621-683).** URLs are mangled (feeed.md:646, 656). The `/stats/contributors` endpoint returns 202 with `{}` while it computes, so `item['total'] for item in stats` would iterate dict keys (feeed.md:660). `open_issues_count` includes PRs (feeed.md:664). Only one repo's Gini stands for the whole org (feeed.md:654).
14. **Write-back (discovery.md:402-623).** URLs are mangled (418, 593). The 409 conflict on concurrent writes is not handled. Contents-API writes need push access, which contradicts "any visitor/developer appends" (discovery.md:14, 388). `btoa` throws on non-Latin-1 text (discovery.md:441, 606). The export button says "Copied" but only `alert`s (discovery.md:275).
15. **OAuth Device Flow (core.md:356-385; discovery.md:549-585).** Endpoints are reduced to `https://github.com` (the real ones are `/login/device/code` and `/login/oauth/access_token`). core.md has no handling for `slow_down`, `expired_token` or denial and polls forever. core.md:262 uses a scheme-less proxy URL. A third-party CORS proxy sees the token (§3.7).

### 6.2 Contradictions between places
- **SYM-2P numeric base.** craft.md:143 calls `:01` "0x01" (hex) while craft.md:145 calls `:0042` "Packet Number 42" (decimal). The repo codec *encodes* in decimal (`sym2p_codec.py:24`, `{role:02d}` / `{sequence:04d}`) and *decodes* in hex (`sym2p_codec.py:31-33`; `sym2p-parse.js:10-12`). Sequence 42 parses back as 66; role or sequence ≥ 10 diverges. This is a real round-trip bug inherited from the ambiguous design.
- **Action state.** `:03` = "Executing/Active" (craft.md:144; eh.md:302), but the shader treats active as `action_state == 1.0` and idle as `0.0` (craft.md:161, 196).
- **Metric key names.** `tension`/`active_nodes` (craft.md:396) vs `con`/`owner`/`lbl`/`res`/`cap` (build.md:59) vs `con` (feeed.md:233, 668) vs `gini` (repo data and codec). The docs JS reads `gini`, so a design-format `con` packet would be ignored.
- **Data paths.** Writers use `public/data/telemetry.jsonl` (craft.md:401; build.md:63; feeed.md:673). Readers use `data/telemetry.jsonl` (craft.md:778; eh.md:225). aywa uses `dist/data/` (aywa.md:48). Profiles: `data/profiles.jsonl` (combine.md:12, 27) vs `public/data/profiles.jsonl` (discovery.md:408, 592).
- **Uniform size.** 16 B (craft.md:640; eh.md:116), 32 B (build.md:79; core.md:295; feeed.md:515, 930), 48 B (combine.md:73; custom.md:42; discovery.md:298) and 64 B (docs). Field order changes every version (e.g. slot 4 is `label_state` in build.md, `user_rounding` in core.md and `label_state` again in feeed.md:346).
- **Polling interval.** 30 s (craft.md:719), 15 s (eh.md:176; feeed.md:84), "within seconds" (feeed.md:244). Docs uses 45 s and 60 s.
- **Sandbox honesty.** craft.md:43 (the page "commands your silicon to allocate shared memory pages") and anew.md:47 (Apple Silicon SharedMemory bus "entirely inside the client tab") vs the retraction at craft.md:56-58.
- **Inkling 2.** A local edge intent engine at anew.md:41, but a 594B cloud MoE at feel.md:117.
- **Interface direction.** combine.md:19 and baryonic.md:1 describe linear `mix` as broken for N slices, yet combine.md's own hue lerp (combine.md:70) has the wrap problem that baryonic.md:94 complains about.
- **Line length.** 70 (combine.md:102), 80 (discovery.md:14) and 101 bytes (craft.md:25).
- **Mis-attribution in docs.** `docs/widgets/index.html:42` says NCA is "named in design/bio.md". NCA is in create.md, feel.md, anew.md:16 and craft.md:14, not bio.md.

### 6.3 Promised but never specified
- Algorithms for **Resonance** (fix-to-author link graph) and **Capture** (contributors' activity in other OSS projects) (build.md:16-17). The code hard-codes them.
- The **style-extraction parser** for developer repos (custom.md:16-36, 172). How it computes "rounding bias" from CSS or editor themes.
- **Loss functions** for Lineage Alpha vs Beta (converge.md:37; craft.md:37): what "winning" means for a UI.
- The **workflow that aggregates `profiles.jsonl`** into org-wide aesthetics (discovery.md:390-392).
- **Who may write** the profiles ledger, plus moderation, revocation and spam limits (discovery.md stigmergy section).
- The **offline-first cache** design (craft.md:260: "behaviors we discussed", which never appear in these files).
- **Model specifics:** Laya input schema, tokenizer and quantised size. The 421M model at 4–8 bits (roughly 210–420 MB) vs the GitHub Pages ~1 GB site guidance and the 100 MB git file limit (craft.md:244-249; anew.md:121).
- **Ledger semantics** for "Tension Fracture verification" and `weaver_capital_vault` payouts (converge.md:41-44).
- **The "[cite: 1]"** source for the SYM-2P role archetypes (craft.md:124). The protocol is attributed to external `abios` and `synbios` repos (craft.md:1, 114) whose spec is not in the repo.
- **Accessibility** of canvas-only UIs (no DOM text, no screen-reader path). Never discussed. create.md:89 concedes canvas cannot "grow a readable word".
- **The three embedded widgets** described in art.md:5 and 102, bio.md:106 and create.md:34 are absent from the transcripts. Their mapping to `docs/widgets/01-04` is undocumented. feel.md:7-21 claims the NCA widget uses `putImageData`; `docs/widgets/04-neural-cellular-automata.html` contains no `putImageData` (it uses Float32Array; the render path differs).

### 6.4 Docs-specific gaps (in addition to the §5.2 table)
- The `node_vel_0/1` uniform slots are declared (`dashboard_layout.wgsl:11-12`), and the harvester computes 8 velocity floats (`github_harvester.py:84-87`), but JS packs zeros (`weft-loom.js:165-166`). The 64-byte `moissanite_telemetry.bin` frame is never fetched.
- The `labelMatrix` from `moissanite_telemetry.json` reaches only the 2D fallback.
- The docs page has no `<noscript>`, no visible text content and no link to the design corpus. It does not meet anew.md's or craft.md's intent of a documentation site that teaches the protocol.
- The workflow is manual-only and Pages is disabled ("after Alkindus enables Pages", `pages-seed-deploy.yml:43`). None of the design's live-deploy requirements (P37-P39) can be checked until a human enables Pages. That gate is a governance decision the design folder never discusses.
