# Aywa: A First-Principles Philosophy for Morphogenetic & Spatial Web Design

Date: 2026-11-08
Scope: Encapsulating the web design paradigm in `weft/design/*` as a distinct, self-contained discipline that is modularly connected to the Syntactic Weft and shapes the `w3ft.org` interface.

## 1. Why Web Design Needs a New Foundation

Conventional web interfaces are built on the **Document Prison** (`weft/design/anew.md`):
1. **Static Box Trees**: Information is flattened into nested rectangular DOM nodes whose layout is recomputed on the CPU every time content changes.
2. **Discrete Brittle Themes**: Visual style is hard-coded into static CSS classes (`light`, `dark`, fixed breakpoint tokens) that cannot interpolate continuously in response to content density, system state, or user preference.
3. **Passive Vertical Scrolling**: Complex multi-layered architectures are forced into a single linear scroll, destroying spatial memory and structural relationships between components.

**Aywa** (`weft/design/*`) replaces the Document Prison by applying the same mathematical first principles that govern the Syntactic Weft (continuous vector spaces, signed distance fields, compact binary state buses, and homeostatic feedback) directly to the browser viewport.

---

## 2. The Five Modular Pillars of the Aywa Design System

Aywa is structured as five self-contained modules (`D1`–`D5`). Any web application can adopt one or all of them independently:

### Module D1: Continuous Barycentric Aesthetic Space (`design/baryonic.md`, `design/discovery.md`, `design/core.md`)

Instead of switching between discrete stylesheets, Aywa represents visual design as a continuous vector $\mathbf{a} \in \mathbb{R}^4$ (`rounding`, `density`, `hue`, `contrast`) computed by barycentric interpolation over $K$ reference aesthetic presets $\{P_1, \dots, P_K\}$ with non-negative weights $w_k \ge 0$ normalized on the simplex ($\hat{w}_k = w_k / \sum_j w_j$):

1. **Linear Structural Tokens**: Border rounding, spatial packing density, and background contrast interpolate linearly across the simplex:
   $$r = \sum_{k=1}^K \hat{w}_k r_k, \qquad d = \sum_{k=1}^K \hat{w}_k d_k, \qquad c = \sum_{k=1}^K \hat{w}_k c_k$$
2. **Circular Mean Hue on $S^1$**: Because chromatic hue is periodic on $[0, 1)$, linear averaging produces a false midpoint (averaging crimson $0.95$ and scarlet $0.05$ linearly yields cyan $0.50$). Aywa maps each hue $h_k$ to an angle $\theta_k = 2\pi h_k$ on the unit circle $S^1$ and computes the circular mean (`docs/assets/js/aesthetic-mixer.js`):
   $$\bar{h} = \frac{1}{2\pi}\operatorname{atan2}\!\left(\sum_{k=1}^K \hat{w}_k \sin(2\pi h_k), \sum_{k=1}^K \hat{w}_k \cos(2\pi h_k)\right) \bmod 1$$
3. **Real-Time Binding**: The resulting vector drives both CSS custom properties (`--weft-rounding`, `--weft-density`, `--weft-hue-deg`, `--weft-contrast`) and slots `[4..7]` of the 64-byte WebGPU uniform buffer at 60–120 Hz.

### Module D2: Analytical Field & Laya Kinetic Typography (`design/typo.md`, `design/craft.md`)

1. **Signed Distance Field (SDF) Geometry**: UI cells, borders, and procedural glyphs in `dashboard_layout.wgsl` are evaluated analytically per fragment via signed distance functions (`sdBox(p, b, r)`), remaining razor-sharp at any zoom level or device pixel ratio (`window.devicePixelRatio`) with zero texture memory overhead.
2. **Laya Cadence & Scroll-Membrane Coupling**: Named after the rhythmic tempo principle (*Laya*), typographic tracking, line-height, and alpha/beta lineage weighting respond continuously to the reader's scroll cadence and pointer velocity (`trackPointerMembrane` in `weft-loom.js`), calming visual noise during focused reading and expanding structural overview during rapid navigation.

### Module D3: Zero-Allocation 64-Byte Uniform Bus & `SYM-2P` Wire Verification (`design/system.md`)

1. **64-Byte Uniform Frame (`16 x float32`)**: All live state needed by the renderer fits in a single 64-byte cache line (`active_nodes`, `org_tension`, `system_time`, `gini_index`, `user_rounding`, `user_density`, `user_hue`, `user_contrast`, `node_vel_0[4]`, `node_vel_1[4]`).
2. **Cryptographic Wire Gate**: The browser's module worker (`telemetry-worker.js`) ingests `SYM-2P/1.0` lines (`:RR:AA:SSSS[s-exp ...]<sha256>`) and verifies the 64-hex SHA-256 digest via WebCrypto (`crypto.subtle.digest("SHA-256", ...)`) before allowing any metric to touch the uniform buffer or HUD.

### Module D4: Morphogenetic & Cellular Surfaces (`design/bio.md`, `design/method.md`, `design/real.md`)

UI regions behave as homeostatic tissues governed by local neighborhood rules:
- When system tension ($\tau$) is in its homeostatic band ($15\%\text{–}35\%$), cell borders pulse gently in the user's chosen barycentric hue.
- As tension rises toward the $85\%$ invariant boundary, the shader shifts cell interior energy and glow decay (`exp(-max(d, 0.0) * 18.0)`), making systemic strain immediately legible without modal alert boxes.

### Module D5: Spatial Mind-Palace Loci (`design/mind-palace.md`, `design/aywa.md`, `design/next.md`)

Human spatial memory remembers *where* a concept lives far better than *how far down a scroll bar* it appeared. Aywa organizes complex systems into distinct **Spatial Loci** anchored to a persistent topological canvas:
- Each Locus represents a self-contained conceptual room (for example: *The Ecosystem Spine*, *The Aywa Design Studio*, *Horizon I: Apple Silicon Prototype*, *Horizon II: Custom Silicon & Terrafab*, *Horizon III: The Civilizational Weave*, and *The Whitepaper & Glossary*).
- Selecting a Locus reconfigures both the foreground architectural cards and the underlying WebGPU/Canvas2D topological visualization, so the graphic field and the written specification always reinforce each other.

---

## 3. How Aywa Shapes `w3ft.org`

On `w3ft.org` (`docs/index.html`), Aywa is not merely described in prose. The website itself is built as an Aywa spatial organism:
1. **Top Spatial Locus Bar**: Switches instantaneously between the six architectural Loci while morphing the live background canvas topology to match the active Horizon.
2. **Live Barycentric Simplex Dock**: Allows any visitor to drag the aesthetic weights (`Native Base`, `Neon Terminal`, `Airy Pastel`) or select presets and watch the entire site's geometry, color phase, spacing density, and GPU shader uniforms transform in real time.
3. **Interactive Falsifier & Simulation Widgets**: Embeds live in-browser calculators for the Frobenius Invariant Gate (`C2`), Speculative A/B Mitosis (`C1`), the 85/15 Metabolic Excision Valve (`C4`), and the 5 extracted React/WebGPU simulation widgets (`docs/widgets/`).
