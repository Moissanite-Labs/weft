# Siliconcordat / Moissanite Labs — public site design spec

Direction A: **Carbon–Silicon Cut** (recommended; fully specified here)
Status: design package for review by lumen, then nizam, then smith. Prepared 2026-11-08 (America/Chicago).
Package root: `/workspace/siliconcordat-design/`

This document is the build contract. If a state, size or rule isn't written here, take it from the prototype CSS (`prototypes/site.css`), which is the reference implementation. If the two disagree, this document wins and the prototype is the bug.

---

## 1. Intent and hard constraints

**Intent.** One house (Moissanite Labs) with three rooms:

| Path | Room | Job |
|---|---|---|
| `siliconcordat.com/` | The proposal | Cinematic landing that sets The Siliconcordat: mission, name, six principles, ecosystem directions, doorways. Half sci-fi film still, half research lab. |
| `siliconcordat.com/ml` | The lab | Moissanite Labs site: about, directions index, principles, and deeper pages (`/ml/principles/`, later `/ml/exo/` etc.). |
| `siliconcordat.com/weft` | One public research program | The current w3ft.org Weft experience, **unchanged in look**. Only wayfinding links are added (§5.3). |

**Hard constraints (non-negotiable).**
1. URL map above is fixed. `/w3ft` → `/weft` and apex aliases are not part of this design.
2. Copy comes only from The Siliconcordat (Moissanite-Labs/compass `README.md`), as quoted in §10. No FOUNDER-VISION.md, SILICONCORDAT.md or NAMING.md content. No slogans, traction, team, waitlist, newsletter, metrics or taglines. Herald owns marketing copy; the few structural labels this design needs are listed in §10.3 so herald can replace them.
3. Every page keeps the README's humility: working proposal, not adopted policy, not a legal agreement, directions not capabilities.
4. Link rule (§10.4): only confirmed-public URLs. Never link compass, credos, weft, weft-eido, weft-corpus, or GitHub copies of the manifesto files. Weft is always linked as `/weft`, never GitHub.
5. Weft is not restyled. No new palette, type, chrome removal, loom change or overlay on `/weft`.
6. Not folded into askaconsult.com: no askaconsult nav, branding or hosting story. (The Exo card links to Exo's existing site, which happens to live on exo.askaconsult.com; that is the only askaconsult string on the site.)
7. Dark only for v1. No theme toggle on `/` or `/ml`.
8. Build contracts: mobile Lighthouse ≥ 80 (target 90+), WCAG 2.2 AA, visible focus, skip link, reduced motion, no colour-only current-nav, no dark patterns, self-hosted fonts, `assets/` is the only asset source.

---

## 2. Recommendation and alternatives

### Recommended: A — Carbon–Silicon Cut
The name is the identity: moissanite is silicon carbide, two substrates in one crystal. Direction A shows a **mineral chamber**: a dark, warm void; a cluster of hexagonal crystals lit cool (silicon) on one side and warm (carbon) on the other; slow light moving through the cut faces. Lab captions (Fig. 1, element plates, numbered chapters) keep it a research lab, not a jewellery ad.

Why A over the others:
- **Structurally distinct from Weft.** Weft is a wet loom: navy-black `#060a12`, frost ink, aqua links, liquid-metal chrome borders, 10px radii, Palatino display with an italic aqua tagline, a woven canvas. A is a dry crystal: warm void `#0a0908`, warm paper ink, champagne fire, sharp 2px cuts, upright Source Serif 4, faceted light, no weave. Side by side they read as the same house (dark, serious, honest, research-first) and clearly different rooms.
- **On-metaphor without a gimmick.** Carbon/silicon shows up as two lights on one object, not as a literal split screen, so it carries to inner pages quietly (the mark, element plates, hairline warm/cool accents).
- **Cousin to Exofab's Crystal Lattice** (shared crystal vocabulary) without becoming a product-app UI.

### Alternative B — Observatory / Instrument Lab (context, not built)
Frame: `prototypes/alts/observatory.html` · shot: `shots/alt-observatory-1440.png`.
Cool neutrals, a measurement grid, a spectral calibration plate (moissanite "fire" as dispersion, an instrument rather than jewellery), DIN-like plate captions and an element read-out, light Plex Sans display.
Risks: closest to Weft's cool instrument feeling (two cool rooms in one house); easy to read as generic deep-tech; the spectrum needs care to avoid rainbow cliché; less cinematic than the brief asks for `/`.

### Alternative C — Threshold / Split seam (context, not built)
Frame: `prototypes/alts/threshold.html` · shot: `shots/alt-threshold-1440.png`.
Literal split: warm carbon left, cool silicon right, a bright seam, title straddling it.
Risks: memorable once, gimmicky on every inner page; text crossing the seam needs scrims (visible in the frame) and is an a11y liability; the cool half competes with Weft's cool room. The seam survives in A only as a 1px whisper in the hero.

**Decision posture:** A is the recommendation; B and C are context, not a blocking choice. Build A.

---

## 3. Visual identity

### 3.1 Palette (`tokens.css`, exact values)

| Token | Value | Role | Contrast on `--bg` |
|---|---|---|---|
| `--bg` | `#0a0908` | Page void. Warm mineral black (Weft is `#060a12`). | — |
| `--bg-2` | `#100e0c` | Footer ground, notes, plates. | — |
| `--surface` | `#161310` | Cards, doorways, element tiles. | — |
| `--surface-2` | `#1d1915` | Hovered surface. | — |
| `--ink` | `#ece6db` | Headings, emphasis, current nav. Warm paper (Weft is frost `#e2f1f8`). | 16.0:1 |
| `--ink-2` | `#c4bdb0` | Body text, ledes. | 10.7:1 |
| `--muted` | `#8a8378` | Captions, mono meta, paths. Smallest text allowed in this colour: 0.6875rem mono uppercase. | 5.3:1 (4.66:1 on `--surface-2`) |
| `--line` | `#2a2520` | Hairlines, section rules. | non-text |
| `--line-2` | `#3d352c` | Card borders, strong rules. | non-text |
| `--carbon` | `#c4844a` | Warm ember. Carbon side of the mark, the C element plate, warm atmosphere. Never body text. | 6.4:1 |
| `--carbon-deep` | `#8a5a32` | Selection background. | — |
| `--carbon-soft` | `rgb(196 132 74 / .14)` | Warm glows on surfaces. | — |
| `--silicon` | `#9db0c4` | Cool silver-ice (not Weft aqua). Silicon side of the mark, Si plate, direction-status diamonds. | 8.9:1 |
| `--silicon-deep` | `#6a7d92` | Reserved (deep cool shadow). | — |
| `--silicon-soft` | `rgb(157 176 196 / .14)` | Cool glows on surfaces. | — |
| `--fire` | `#e6d2a8` | Moissanite caustic / champagne (not Weft gold `#d4af37`). Current-nav underline, focus ring, chapter numbers, proposal chip, principle numerals, caveat rule. Used sparingly. | 13.4:1 |
| `--fire-strong` | `#f3e6c6` | Hover state of fire-coloured text. | — |
| `--focus` | `#e6d2a8` | Focus ring (= fire). | — |
| `--link` | `#d4b48a` | Inline links and URLs. Underline at 45% alpha; full on hover. | 10.1:1 |
| `--link-hover` | `#f3e6c6` | Link hover. | — |
| `--weft-link` | `#7fcbe3` | **Only** on things that point at Weft (header Weft tick, Weft doorway, Weft row). | 11.0:1 |
| `--weft-bg` / `--weft-surface` / `--weft-ink` | `#060a12` / `#0b1825` / `#e2f1f8` | Only inside the Weft doorway sliver and Weft row hover. | — |

Rules:
- **Text is always a flat colour.** Gradients live only on surfaces: hero atmosphere, card fills, the Weft sliver, the bond line in the element plate, the constellation foundation line.
- Champagne is an accent, not a theme: at most one fire element per component (number, rule, or chip).
- Weft aqua appears only where the link goes to `/weft`.

### 3.2 Type

| Role | Family | Settings |
|---|---|---|
| Display (titles, chapter titles, card titles, pull quote, ledes) | **Source Serif 4** (variable, `opsz` axis) | Upright only. Weights 360–420. `font-optical-sizing: auto`; hero and h1 force `"opsz" 60`. Tracking −0.012em (h2/h3) to −0.03em (hero). **Never** an italic coloured tagline (that is Weft's signature). |
| Body / UI | **IBM Plex Sans** 400 / 500 / 600 | 17px/1.65 desktop, 16px under 600px. Max measure `--max-prose` 40rem. |
| Meta (captions, chapter markers, proposal chip, numerals, paths, URLs) | **IBM Plex Mono** 400 / 500 | 0.6875–0.8125rem, uppercase, tracking 0.08–0.14em. URLs are mono but not uppercased. Chemical symbols (`Si`, `C`, `SiC`) are never uppercased: wrap them in `.chem`. |

Type scale (as built):

| Element | Size | Weight | Line height |
|---|---|---|---|
| Hero title "Siliconcordat" | `clamp(3.25rem, 1.2rem + 7.6vw, 8.75rem)` (≈140px at 1440, 52px at 390) | 360 | 0.92 |
| Hero "The" | 0.34em of title, `--ink-2`, own line | 400 | — |
| Hero lede (mission) | `clamp(1.25rem, 1rem + .9vw, 1.75rem)`, Source Serif `opsz 24`, `--ink-2`, max 31ch | 380 | 1.38 |
| Chapter title (h2 on `/`) | `clamp(2.25rem, 1.4rem + 3vw, 4rem)` | 380 | 1.02 |
| Pull quote | `clamp(1.9rem, 1.2rem + 2.4vw, 3.25rem)` | 360 | 1.12 |
| `/ml` h1, deeper-page h1 | `clamp(2.75rem, 1.6rem + 4.4vw, 5.5rem)` / `… 4vw, 5.25rem` | 360 | 0.96–0.98 |
| `/ml` h2 | `clamp(2rem, 1.4rem + 2vw, 3rem)` | 380 | 1.05 |
| Principle h3 | `clamp(1.5rem, 1.2rem + .8vw, 1.875rem)` | 420 | 1.12 |
| Direction card h3 | 2rem | 420 | 1 |
| Deeper-page body | 1.25rem Source Serif `opsz 18`, `--ink` | 400 | 1.6 |
| Mono meta | 0.75rem | 500 | 1.4 |

Fonts are self-hosted from `assets/fonts/` (SIL OFL 1.1; licences beside the files). No remote font CDN. Preload `source-serif-4-opsz.woff2` and `ibm-plex-sans-400.woff2` only. `font-display: swap`. Fallback stacks are exactly those in `tokens.css`; they must never include Palatino or Iowan (Weft's display).

### 3.3 Mark — `assets/mark.svg`
Two hexagonal lattices that overlap; the overlap (itself a hexagon) is filled. Left hexagon stroked `--carbon`, right hexagon stroked `--silicon`, overlap filled `--fire`: two substrates, one shared cut, the concordat.
- 32-unit grid, 2-unit strokes, miter joins. Holds at 16px (favicon) and 24–28px (header).
- Use on `--bg` or `--surface` only. Minimum size 16px. Clear space = 25% of size on every side.
- Header: 28px, followed by "Siliconcordat" in Source Serif 4 500 at 1.125rem, 10px gap.
- Favicon: `<link rel="icon" href="/assets/mark.svg" type="image/svg+xml">`. Smith may add a 32px PNG fallback rendered from the same SVG.
- Doorway watermark: same mark at 320px, 9% opacity, bleeding off the bottom-right of the Moissanite Labs doorway.
- Not Weft's weave-mark, not jewellery, not the Exofab mark.

### 3.4 Atmosphere and imagery
- `assets/chamber.svg` (6 KB): three translucent hexagonal crystals, flat-shaded from a cool key at upper right and a warm fill at lower left, with champagne cut edges. Illustrative. Generated by `tools/make_chamber.py`.
- `assets/caustic.webp` (92 KB, 768×768, seamless): angular light facets (periodic Voronoi cells) with thin bright cut lines and slight warm/cool dispersion. Generated by `tools/make_caustic.py`.
- No photography. No stock scientists, no actors, no engagement-ring moissanite, no video.

### 3.5 Motion
| What | Behaviour | Reduced motion |
|---|---|---|
| Hero caustic layer A | `transform: translate3d` drifts one tile (768px) diagonally over **36s**, linear, infinite. Opacity 0.16, `mix-blend-mode: screen`, radial-masked to the crystal. | No animation (static). |
| Hero caustic layer B | Same texture at 1100px, opposite diagonal, **52s**, opacity 0.12. | Static. |
| Hero seam | 1px vertical champagne→ember gradient at 61% width with a faint glow. Static. Hidden under 860px. | Same. |
| Chapter reveal | Elements with `.reveal`: opacity 0→1 and translateY 14px→0 over 900ms `cubic-bezier(.22,.61,.36,1)`, once, when 8% into the viewport. Only when JS has added `.js` to `<html>`. | Shown immediately; no transition. |
| Hover/focus on links, cards | 180ms colour/border transitions; arrows nudge 3–4px. | Transitions removed. |
| Weft doorway | Sliver widens 10px → 34% over 520ms on hover/focus. | Instant switch, no transition. |
| Smooth scroll | Only under `prefers-reduced-motion: no-preference`. | Off. |
No parallax, no bounce, no pulsing, no pause/play controls (nothing should look like it pauses real work). Animations are compositor-only (transform/opacity).

### 3.6 Tone
Quiet, filmic, humble. A research lab that happens to look like a still from a serious science-fiction film. Captions state what things are ("Fig. 1 — illustration"). Nothing is "live", "launching", or "join". Status words: **Direction**, **Direction · foundation**, **Open research program**, **Aspiration**. Never "Live product", "Beta", "Coming soon".

---

## 4. Anti-slop checklist (design)
No purple gradients · no glassmorphism blur soup (the only blur is the sticky header's 10px backdrop) · no neon · no hero video · no stock people · no 16px-rounded cards (2px / 4px only) · no Inter · no aqua chrome buttons on `/` or `/ml` · no woven/textile pattern on `/` or `/ml` · no gradient text · no fake metrics, logos wall, testimonials, newsletter, countdown.

---

## 5. Family and navigation

### 5.1 Visitor path
Landing ("the house / the proposal") ↔ `/ml` ("the lab") ↔ `/weft` ("one public research program"). Every page on `/` and `/ml` can reach the other two in one click, from the header and the footer.

### 5.2 Family header (on `/` and `/ml`) — this is the header

```
[mark] Siliconcordat     Moissanite Labs     ◇ Weft                    [WORKING PROPOSAL chip — /ml pages only]
```
- Height 64px. `--gutter` side padding, max width = page max (`1280` on `/`, `1120` on `/ml`).
- Links: "Siliconcordat" → `/`, "Moissanite Labs" → `/ml`, "Weft" → `/weft`. Same tab.
- Items: Plex Sans 500 0.875rem `--ink-2`; hover `--ink`. Brand item: Source Serif 500 1.125rem `--ink`. Each target ≥ 44px tall.
- **Current item:** `aria-current="page"` + text `--ink` + **1px `--fire` underline** (9px above the bar's bottom) + **5px fire diamond** centred under it. Never colour alone. On `/`, Siliconcordat is current; on `/ml` and `/ml/*`, Moissanite Labs is current.
- **Weft item:** a 6px diamond tick before "Weft": fill `--weft-bg`, 1px `--weft-link` outline. Hover: text and tick turn `--weft-link` (the tick fills). This is the only aqua in the header.
- **On `/`:** header is `position: fixed` over the hero with a top-down fade (`rgb(10 9 8/.7)` → transparent) and no border. After 24px of scroll (`.is-scrolled`), it becomes `rgb(10 9 8/.7)` + 10px backdrop blur + 1px `--line` bottom border. No chip in the landing header (the hero has it).
- **On `/ml`:** `position: sticky`, solid treatment from the start, and the "Working proposal" chip at the right.
- **Mobile (≤ 720px):** mark + "Siliconcordat" stays; the other links and the chip collapse into `<details class="menu">` with a 44×44 "Menu" summary (mono, 1px `--line-2` border, fire border when open). Panel: `--surface`, 1px `--line-2`, 2px radius, rows 48px tall, 1px `--line` separators. Current row: 2px inset fire bar on the left and a mono "HERE" tag on the right. Escape closes the menu and returns focus to the summary. Works without JS.

### 5.3 On `/weft` — wayfinding, not a restyle (recommended default)
Annotation: `prototypes/family-weft.html` · shot: `shots/family-weft-1440.png`. Facsimiles are simplified redraws for annotation only.

Weft's current header has one link (mark + "ML Weft" + "Moissanite Labs") to Weft home. Change only that block:
1. Weave-mark + "ML Weft" stay one link to Weft home (`/weft/`; `/` while still served on w3ft.org). `aria-label="ML Weft home"` unchanged.
2. "Moissanite Labs" becomes its own `<a class="brand-org" href="/ml">`, using Weft's existing `.brand-org` type, size (0.78rem), colour (`#86a0b5`) and left rule (`#21435c`).
3. Add `<a class="brand-org" href="/">Siliconcordat</a>` after it, identical style. Hover: Weft `--link-hover` `#cfe8f3` + underline. Focus: Weft's own aqua outline. No champagne, no Source Serif, no Plex.
4. While Weft is served on w3ft.org, links 2 and 3 are absolute: `https://siliconcordat.com/ml` and `https://siliconcordat.com/`.
5. Under 860px Weft already hides `.brand-org`; keep that, and append to the bottom of Weft's existing `.menu-panel`, after a 1px Weft `--line` rule, a muted "Moissanite Labs family" label plus "Moissanite Labs" and "Siliconcordat" links in Weft's menu-link style.

Markup and CSS for Weft are in the annotation page (two code blocks). Nothing else on `/weft` changes: no colours, fonts, chrome, loom canvas, theme toggle, GitHub button, sections or footer.

**Fallback (not default):** a 32px rail above Weft's header, painted only in Weft tokens (`#060a12` ground, `#86a0b5` links, `#7fcbe3` for current "Weft", `#142a3c` rule, Weft system type at 0.78rem) listing Siliconcordat · Moissanite Labs · Weft. Not recommended: two stacked headers read as two sites.

---

## 6. Layout: `/` (cinematic landing) — `prototypes/landing.html`
Max width 1280px, `--gutter` = `clamp(20px, 5vw, 48px)`. Shots: `landing-hero-1440.png`, `landing-principles-1440.png`, `landing-ecosystem-1440.png`, `landing-doorways-1440.png`, `landing-full-1440.png`, `landing-hero-390.png`, `landing-390.png`.

**a. Family header.** Fixed overlay variant (§5.2).

**b. Hero (`<section class="hero">`).** `min-height: max(680px, 100svh)`; content anchored to the bottom-left.
- Atmosphere stack (all `aria-hidden`, `pointer-events: none`): (1) three radial gradients: cool glow at 74% 44%, warm glow at 18% 88%, `--bg-2`→`--bg` from the top; (2) `chamber.svg` at `min(1320px, 92vw)` wide, right −4vw, vertically centred (−46%), opacity .78, radial mask so its edges dissolve; (3) caustic layers A and B (§3.5); (4) seam; (5) a floor gradient fading the bottom 40% into `--bg`.
- Content column, left: **proposal block** first, never hidden: the "WORKING PROPOSAL" chip (mono 0.75rem uppercase, `--fire`, 1px fire border at 50%, rotated-square glyph, 2px radius) followed by the full banner sentence in Plex Sans 0.9375rem `--ink-2`, max 44rem. Then **h1** "The / Siliconcordat" ("The" small on its own line). Then the **mission sentence** as lede (Source Serif, roman, `--ink-2`). Then two text links: "Principles ↓" (to `#principles`) and "Moissanite Labs →" (to `/ml`): Plex Sans 500, `--ink`, 1px `--line-2` underline bar; hover → `--fire-strong`, fire bar, arrow nudges 3px.
- Lab caption, bottom-right (desktop only): "Si · C — silicon carbide" / "Fig. 1 — illustration, hexagonal habit" in mono `--muted`, element symbols in their colours.
- Scroll cue, bottom-centre (hidden under 600px): mono "THE NAME" with a 36px fire→transparent line; links to `#name`.
- 390px: crystal moves to the top-right (150vw wide, right −22vw, top 40px, opacity .5), seam and caption hidden, text stays bottom-anchored.

**c. Chapter 01 — The name (`#name`).** Chapter marker: mono "01 THE NAME" with the number in fire and a hairline to the right edge. Two columns 5fr / 6fr, gap `clamp(40px, 7vw, 112px)`.
- Left: pull quote (README sentence: "The bond between silicon and carbon is a metaphor for the symbiosis the lab wants to cultivate.") then the **element plate**: Si tile (14, Silicon, cool border and glow) — bond line (silicon→fire→carbon gradient, "SiC" label) — C tile (6, Carbon, warm). Caption "Moissanite · a naturally occurring form of silicon carbide".
- Right: README paragraph 1 in full, split into three paragraphs (mission at 1.1875rem `--ink`; name; Siliconcordat). Then the **caveat block** in readable body type, not a footnote: 1px fire left rule with a fire diamond at the top, mono label "WHAT THE METAPHOR IS NOT", and the sentence in `--ink` 1.0625rem.
- Under 860px the columns stack (quote and plate first).

**d. Chapter 02 — Principles (`#principles`).** Head row: h2 "We intend to build for:" (the README's own lead-in) and mono "Six principles · proposed for review". Then `<ol class="principles">`: 3×2 grid at ≥ 1081px, 2×3 at 601–1080px, 1 column ≤ 600px. Cells are hairline-ruled (1px `--line` right/bottom, `--line-2` top), min-height 300px desktop, 32px padding, a 28px fire tick on each cell's top-left edge. Inside: mono numeral "01"–"06" in fire with a 24px rule; h3 principle name; the full README sentence(s). Not interactive (no hover). Each `<li>` has an id equal to the principle slug (§10.2).

**e. Chapter 03 — Ecosystem (`#ecosystem`).** Head row: h2 "Building the ecosystem" (README heading) + README paragraph 2 (Exo… accountability) + a **Status note** (bordered box, mono "STATUS" label in fire, README caveat sentence in `--ink`). Then the **constellation figure** (desktop/tablet; hidden ≤ 600px because the cards carry the same information): an inline SVG lab diagram: a warm→champagne→cool foundation line labelled "EXO · FOUNDATION", four nodes rising from it (Exofab, Synbios, Koinos, Ethos — each "DIRECTION"), and a dashed extension with a dashed hollow node "ROBOTICS / ASPIRATION" off the foundation. Caption: "Fig. 2 — Directions for work, drawn on the Exo foundation. Robotics sits off the line: an aspiration." Then the **direction cards** (§8.5) in a 3-column grid (2 at ≤ 1080px, 1 at ≤ 600px), in order: Exo, Exofab, Synbios, Koinos, Ethos, Robotics (aspiration).

**f. Chapter 04 — Doorways (`#doorways`).** Two equal panels, min-height 380px (300px on mobile), stacked under 860px.
- **Moissanite Labs** → `/ml`. Kicker "THE LAB" … "/ml"; title "Moissanite Labs" (Source Serif 360, up to 4.25rem); description; "Enter the lab →". Surface: `--surface` with a warm glow bottom-left and cool glow top-right, mark watermark. Hover/focus: border → fire 60%, action bar → fire, arrow +4px.
- **Weft** → `/weft` (§8.7).

**g. Footer.** Two columns (4fr / 7fr, stacked under 860px). Left: mark + "Siliconcordat" (→ `/`), then the family list with mono paths (`The Siliconcordat /`, `Moissanite Labs /ml`, `Weft /weft`); current page underlined in fire. Right: **humility block**: 1px `--line-2` top rule, mono "WORKING PROPOSAL" in fire, the banner sentence, and the caveat sentence. Base row: mono "Moissanite Labs" and "siliconcordat.com". No newsletter, social icons, or copyright claims.

---

## 7. Layout: `/ml` (the lab) — `prototypes/ml.html`
Same tokens, tighter chrome: 1120px max, smaller titles, more rules and mono captions, no hero animation. Shots: `ml-top-1440.png`, `ml-1440.png`, `ml-390.png`.

1. **Family header** (sticky; Moissanite Labs current; chip on the right).
2. **Local nav** (sticky under the header at 64px; 48px tall; 1px `--line` bottom): mono "MOISSANITE LABS" label, then **About · Directions · Principles**. On `/ml` they are in-page anchors (`#about`, `#directions`, `#principles`); the current section uses `aria-current="location"` with the same 1px fire underline. On deeper pages, "Principles" links to `/ml/principles/` and carries `aria-current="page"`. Horizontally scrollable on narrow screens, no scrollbar.
3. **Lab hero**: 7fr / 5fr. Left: mono eyebrow "THE LAB" (fire), h1 "Moissanite Labs", mission sentence as lede. Right: **instrument plate**: `chamber.svg` cropped in a 4:3 frame, 1px `--line-2` border, four 9px fire corner ticks, mono caption bar "Fig. 1 — SiC, illustration" / "Si · C". Stacks under 860px.
4. **About** (`#about`): 3fr / 8fr. Left: h2 "About", mono "From the Siliconcordat", proposal chip. Right: README paragraph 1 (mission as a Source Serif 1.375rem first paragraph; then name; then Siliconcordat), the caveat block, README paragraph 2 (Exo…), and "Read the Siliconcordat →" to `/`. No team, bios or founder names.
5. **Directions** (`#directions`): left h2 "Directions" + mono count "Index · 5 directions · 1 program · 1 aspiration"; right the Status note. Then an **index table** (not cards: the lab is denser than the landing): rows of `ID | name | description | status + link`, columns 64px / 1.6fr / 4fr / 3fr, 26px vertical padding, 1px rules. IDs: D-01…D-05 for directions, P-01 for Weft under a mono "PUBLIC RESEARCH PROGRAM" subhead, A-01 for Robotics under "ASPIRATION" (dashed bottom rule, dashed diamond, no link). Row states in §8.6.
6. **Principles** (`#principles`): left h2 "Principles" + mono "We intend to build for:"; right a 2-column index of the six (numeral, name, arrow) linking to `/ml/principles/#slug`, then "All six principles →".
7. **Footer** (Moissanite Labs current).

---

## 8. Components and states
All interactive elements: focus-visible = `outline: 2px solid var(--focus); outline-offset: 3px` (square). Where a whole card or row is clickable, the outline is drawn on the stretched `::after` of the title link so it wraps the card.

### 8.1 Family header link
Default `--ink-2` → hover `--ink` → current `--ink` + 1px fire underline + 5px fire diamond. Weft link hover `--weft-link`. Focus ring as above.

### 8.2 Proposal chip
Mono 0.75rem (0.6875rem in the header), uppercase, tracking .1em, `--fire` text, 1px `rgb(230 210 168/.5)` border, `rgb(10 9 8/.55)` fill, 2px radius, 7px rotated-square glyph. Not interactive. Appears on: landing hero (with full banner sentence), `/ml` header and About aside, deeper-page head (with full banner sentence), footer humility block (as a mono label).

### 8.3 Principle cell
Static. Numeral (fire mono) → name (h3) → README text. No hover, no icons.

### 8.4 Caveat block / Status note
Caveat: fire left rule + diamond, mono label, `--ink` text. Status note: bordered `--bg-2` box, mono "STATUS" label, `--ink` text. Static.

### 8.5 Direction card (`/`)
Anatomy: status line (mono, 6px silicon-outlined diamond) → h3 name → README description → link footer (1px `--line` top rule; mono URL in `--link` with ↗; optional secondary link; optional aside).
- **Linked card** (`.dcard--link`; all five directions now have confirmed public URLs): the h3 contains the primary `<a>`; its `::after` stretches over the card so the whole card is clickable. The visible URL label is `aria-hidden` (the h3 link's accessible name is the direction name + "(external site)"). Secondary links (`position: relative; z-index: 2`) sit above the stretched link and stay independently clickable.
  - Hover: border → `rgb(230 210 168/.55)`; fill → `--surface-2`→`--bg-2`; the 22px cut corner (top-right facet) turns fire; URL → `--fire-strong`; ↗ moves (2px, −2px).
  - Focus-visible on the title link: 2px fire outline around the whole card.
  - External links open in the **same tab**, no `target="_blank"`.
- **Foundation variant** (Exo): status "Direction · foundation", diamond filled fire.
- **Not-linked card** (rule for any future direction without a confirmed public URL): same anatomy, no `<a>`, no hover change, cursor default, link footer reads "Direction · no public page yet". Never a dead `href="#"`.
- **Aspiration card** (Robotics): transparent fill, **1px dashed `--line-2` border**, no cut corner, dashed "ASPIRATION" badge (mono, dashed `--muted` border) in place of the status line, title in `--ink-2`, README sentence, dashed footer rule with "Aspiration · no page". No link, no hover.

### 8.6 Direction row (`/ml`)
- Linked row: whole row clickable via stretched h3 link; hover → faint fire wash left-to-right, title and URL → `--fire-strong`.
- Weft row: tag "Open research program" with a navy-filled aqua-outlined diamond; URL "/weft →" in `--weft-link`; hover → row darkens toward `--weft-bg` on the right with a 2px inset aqua edge; title → `--weft-ink`. Links to `/weft`.
- Aspiration row: dashed bottom rule, dashed muted diamond, no link, no hover.

### 8.7 Weft doorway (`/`)
A door left ajar into Weft's room.
- Default: `--surface`→`--bg-2` panel, 1px `--line-2` border, kicker "WEFT · OPEN RESEARCH PROGRAM" in `--weft-link` and "/weft" in `--muted`, title "Weft", description, "Open Weft →" with an aqua arrow. At the right edge, a **10px sliver** of Weft's room: `#0b1825`→`#060a12` vertical gradient with a 1px `#7fcbe3` inner edge and a soft aqua glow.
- Hover **and** focus-visible: sliver widens to **34%** of the panel over 520ms (`--ease-film`); border → `rgb(127 203 227/.55)`; action underline → `--weft-link`; action text → `--weft-ink`; arrow +4px. Focus also draws the standard fire outline.
- Never shows a weave, Weft's mark, chrome gradient or Palatino. Links to `/weft` only.
- Reduced motion: no transition; states switch instantly.
- Shot: `shots/state-weft-door-hover-1440.png`.

### 8.8 Footer
§6g. Family links ≥ 40px tall; Weft link hover `--weft-link`; current page underlined in fire (6px offset).

### 8.9 Skip link
First focusable element on every page: "Skip to content" → `#main`. Hidden above the viewport; on focus it appears top-left, `--fire` background, `--bg` text (13.4:1).

---

## 9. Deeper-page template — `prototypes/ml-principles.html` (`/ml/principles/`)
Template for every `/ml/*` page (later `/ml/exo/`, etc.). Shots: `ml-principles-top-1440.png`, `ml-principles-1440.png`, `ml-principles-390.png`.
1. Family header (Moissanite Labs current) + local nav (current item `aria-current="page"`).
2. **Doc head**: back link "← Moissanite Labs" (→ `/ml`; arrow nudges −3px on hover); mono eyebrow "MOISSANITE LABS · PRINCIPLES" (fire); h1; dek (Source Serif, `--ink-2`, max 36ch); proposal chip + full banner sentence.
3. **Body grid** 3fr / 8fr: left a sticky table of contents (`top: header + 72px`; mono numerals; 1px `--line-2` rail; hover/current = fire left edge + `--ink`; current uses `aria-current="location"`), right an `<article>` of sections. Each section: mono "01 / 06", h2 (principle name), README text set large (Source Serif 1.25rem/1.6 in `--ink`, max 36rem), 1px rule between sections, `scroll-margin-top` so anchors clear the sticky header.
4. Source caption: "Source: The Siliconcordat · working proposal · siliconcordat.com" (link to `/`), then "← Back to Moissanite Labs".
5. Footer.
Under 860px the TOC becomes a static list above the article.

---

## 10. Content and linking rules

### 10.1 Copy source
Only The Siliconcordat (compass `README.md`). The prototypes set its words; smith copies them from `tools/build_prototypes.py` (constants at the top), which mirror the README. Before ship, re-diff those strings against the current compass README (see NOTES.md).
- Banner (public form): "**Working proposal.** Siliconcordat is the chosen name for the Moissanite Labs manifesto. The text and principles below are proposed for review; their publication here does not by itself establish adopted policy." Never mention a repository.
- The banner appears on `/` (hero + footer), `/ml` (footer; chip in header and About), and every `/ml/*` page (doc head + footer).
- The substrate caveat ("The metaphor is not a claim … nor is this document a legal agreement.") appears in body type on `/` (chapter 01) and `/ml` (About), and in every footer.
- The directions caveat ("These are directions for work … remain open.") appears directly above the directions on `/` and `/ml`.
- "A future robotics role is an aspiration, not a present capability." appears as the Robotics card/row text.

### 10.2 Principle slugs
`symbiosis`, `agency-and-consent`, `interoperability`, `traceability`, `real-world-outcomes`, `adaptation-with-control`. Names and text exactly as in the README; never renamed or reordered.

### 10.3 Structural labels (not README; herald may replace, must stay neutral)
Chapter markers ("The name", "Principles", "Ecosystem", "Doorways"); "The lab"; "About the lab, its directions, and its principles."; "Enter the lab"; "Open Weft"; "Papers, runtime, and demos. Weft keeps its own site and design."; "Open research program"; "What the metaphor is not"; "Status"; "Fig. 1 — illustration, hexagonal habit"; "Fig. 2 — …"; "Read the Siliconcordat"; "All six principles"; element-plate facts (Si 14, C 6, "Moissanite · a naturally occurring form of silicon carbide"). None of these make product claims.

### 10.4 Links (confirmed by scout via nizam, 2026-11-08)

| Card | Primary link (title + visible label) | Secondary | Note |
|---|---|---|---|
| Exo | `https://exo.askaconsult.com/` (label `exo.askaconsult.com`) | — | Link only; no askaconsult branding/nav anywhere else. |
| Exofab | `https://moissanite-labs.github.io/exofab/` | — | GitHub repo is also public but not needed on the card. |
| Synbios | `https://moissanite-labs.github.io/synbios/` | `https://github.com/Moissanite-Labs/synbios` (label "GitHub") | If only one link fits, Pages. |
| Koinos | `https://github.com/Moissanite-Labs/synmerit` (label "Public repository") | — | Title stays "Koinos". Quiet aside: "The public repository currently lives at synmerit." |
| Ethos | `https://github.com/Moissanite-Labs/ethos` | — | |
| Weft | `/weft` | — | Never GitHub weft/weft-eido/weft-corpus. |
| Robotics | none | — | Aspiration. |

**Never link:** compass, credos, weft, weft-eido, weft-corpus, FOUNDER-VISION.md, SILICONCORDAT.md, NAMING.md (any host). Do not copy w3ft.org's "View on GitHub" button to `/` or `/ml`. Any future direction without a confirmed public URL uses the not-linked card (§8.5).

External links: same tab, mark with ↗, and include visually hidden "(external site)".

---

## 11. Assets (`assets/` is the only asset source)

| File | Size | Use |
|---|---|---|
| `assets/mark.svg` | <1 KB | Mark, favicon, header, footer, doorway watermark (inline the paths in HTML for the header to avoid a request). |
| `assets/chamber.svg` | 6 KB | Hero crystal (`/`), lab plate (`/ml`). |
| `assets/caustic.webp` | 92 KB | Hero caustic texture (CSS background, tiled). |
| `assets/fonts/source-serif-4-opsz.woff2` | 120 KB | Display (variable wght 200–900 + opsz). Latin subset. |
| `assets/fonts/ibm-plex-sans-{400,500,600}.woff2` | 22–24 KB each | Body/UI. Latin subset. |
| `assets/fonts/ibm-plex-mono-{400,500}.woff2` | 15 KB each | Meta. Latin subset. |
| `assets/fonts/LICENSE-*.txt` | — | SIL OFL 1.1 for each family. Ship them. |
| `tokens.css` | — | Tokens + `@font-face`. Load before site CSS as a separate `<link>` (or inline into one file at build); not via `@import`. |

Generators (not shipped): `tools/make_chamber.py`, `tools/make_caustic.py`, `tools/build_prototypes.py`, `tools/shoot.mjs`.

---

## 12. Accessibility and performance

**A11y (WCAG 2.2 AA):**
- All text pairs in §3.1 ≥ 4.5:1 (smallest: `--muted` on `--surface-2` 4.66:1). Large display text ≥ 10:1.
- Text over the hero atmosphere sits on the dark left side at desktop; on mobile, the crystal is at 50% opacity behind the top of the column. Smith: verify the banner sentence stays ≥ 4.5:1 against the brightest facet behind it at 390px; if not, add `background: rgb(10 9 8/.6)` behind `.proposal p`.
- Landmarks: one `<header>`, `<nav aria-label>` for family, local and TOC navs, `<main id="main">`, `<footer>`. One h1 per page; h2 per chapter (visually hidden where the chapter marker carries the visible label).
- Current state never colour-only (underline + diamond / inset bar + "HERE" tag).
- Focus visible on everything (2px fire, offset 3px). Card focus wraps the whole card.
- Targets ≥ 44×44 (header, menu, local nav, text links, back links).
- Decorative atmosphere, constellation SVG, crystal images: `aria-hidden` / `alt=""`. The constellation has a text figcaption and is redundant with the cards.
- Element plate has an `aria-label`. Chemical symbols are not uppercased.
- Reduced motion: §3.5. Menu works without JS (`<details>`); Escape closes it when JS is present.
- `lang="en"`.

**Performance (mobile Lighthouse ≥ 80; target 90+):**
- Static HTML + one CSS file + tokens. JS: one inline script < 1 KB (header scroll state, reveal, Escape). No frameworks, no WebGL, no Three.js.
- Preload two fonts; the rest swap in. Total font weight ≈ 240 KB on first visit; consider subsetting Source Serif to the glyphs used on `/` if LCP suffers.
- Lighthouse reports the hero crystal (`chamber.svg`) as the LCP element on mobile, so it is preloaded (`<link rel="preload" as="image" fetchpriority="high">`) and stays a 6 KB SVG. The caustic texture is a CSS background and is not on the critical path.
- Prototype measurement (2026-11-08, Lighthouse 12 mobile, `python3 -m http.server`, no compression or caching): `/` 93 / 100 / 100 (perf / a11y / best practices), `/ml` 97 / 100 / 100, `/ml/principles/` 97 / 100 / 100; CLS 0 everywhere; landing LCP 3.2 s under simulated throttling. A real host with gzip/brotli and long cache lifetimes should do better.
- Animations: transform/opacity only; `mix-blend-mode` on two layers; no animated filters.
- Images have width/height attributes; `img { height: auto }`.
- Cache-bust assets by filename hash at build.

---

## 13. Out of scope
- GitHub writes of any kind from design (no repos, PRs, issues, Pages or visibility changes).
- DNS, redirects (`/w3ft`, apex aliases, `weft.siliconcordat.com`), deploys.
- Any restyle of Weft content (palette, type, chrome, loom, toggle, sections). Only the wayfinding change in §5.3.
- askaconsult.com integration of any kind.
- Content from FOUNDER-VISION.md, SILICONCORDAT.md, NAMING.md; any invented claim, team, metric, CTA or slogan.
- Light theme, i18n, CMS, analytics, newsletter, contact forms.

---

## 14. Visitor / build acceptance checklist (smith ticks)

**Identity**
- [ ] `tokens.css` values match §3.1 exactly; no Weft hexes outside `--weft-*` uses.
- [ ] Display is Source Serif 4 upright; no italic coloured tagline anywhere; no Palatino/Iowan/Inter in any stack.
- [ ] Radii are 2px/4px only. No woven pattern, chrome gradient or aqua button on `/` or `/ml`.
- [ ] Text is flat colour everywhere; gradients only on surfaces/atmosphere.
- [ ] Mark renders crisply at 16px (favicon) and 28px (header).

**Landing `/`**
- [ ] First screen shows: family header, WORKING PROPOSAL chip **and** full banner sentence, "The Siliconcordat", mission sentence. Nothing pushes the banner below the fold at 390×844.
- [ ] Hero caustic drifts slowly (36s / 52s); with reduced motion it is static.
- [ ] Chapter 01 includes the full name paragraph and the substrate/legal caveat in body type.
- [ ] Six principles, numbered 01–06, README names and full text, README order.
- [ ] "Building the ecosystem" includes README paragraph 2 and the directions caveat above the cards.
- [ ] Five direction cards link per §10.4; Koinos titled "Koinos" linking to synmerit; Synbios has Pages primary + GitHub secondary.
- [ ] Robotics is dashed, badged "Aspiration", not a link.
- [ ] Weft doorway links to `/weft`; sliver widens on hover **and** keyboard focus.
- [ ] Footer has family links and the humility block (banner + caveat).

**`/ml` and `/ml/*`**
- [ ] Family header with Moissanite Labs current (underline + diamond); local nav About · Directions · Principles.
- [ ] About uses only README paragraphs; no team/founder content.
- [ ] Directions index: 5 directions (D-01…05), Weft as P-01 linking `/weft`, Robotics as A-01 unlinked.
- [ ] `/ml/principles/` follows the template (§9): back link, eyebrow, h1, dek, banner, sticky TOC, six sections with ids per §10.2.

**Weft**
- [ ] `/weft` looks identical to w3ft.org except the split brand block (§5.3) and the mobile menu family group.
- [ ] No champagne, Source Serif or Plex on `/weft`.

**Links**
- [ ] No link anywhere to compass, credos, weft, weft-eido, weft-corpus, or the three manifesto files. No "View on GitHub" on `/` or `/ml`.
- [ ] External links same tab, ↗, hidden "(external site)".

**A11y / perf**
- [ ] Skip link works on every page. Every interactive element shows the 2px fire focus ring.
- [ ] axe/Lighthouse a11y: no contrast failures; menu operable by keyboard; Escape closes it.
- [ ] Reduced motion: no caustic drift, no reveal transitions, no doorway transition, no smooth scroll.
- [ ] Mobile Lighthouse performance ≥ 80 on `/`, `/ml`, `/ml/principles/` (target 90+).
- [ ] Fonts served from `assets/fonts/`; no request to any font CDN.

---

## 15. Files

Prototypes (open via `python3 -m http.server` from the package root, then `/prototypes/landing.html`):
- `prototypes/landing.html` — `/`
- `prototypes/ml.html` — `/ml`
- `prototypes/ml-principles.html` — `/ml/principles/` (deeper-page template)
- `prototypes/family-weft.html` — wayfinding annotation for `/weft`
- `prototypes/alts/observatory.html` — Alternative B hero frame
- `prototypes/alts/threshold.html` — Alternative C hero frame
- `prototypes/site.css` — reference CSS; `tokens.css` — tokens + fonts

In the prototypes, every "Weft" link opens `family-weft.html` so reviewers can click through; **in production every one of those links is `/weft`.** Production hrefs: `landing.html` → `/`, `ml.html` → `/ml`, `ml-principles.html` → `/ml/principles/`.

Screenshots (`shots/`, captured with headless Chromium via Playwright at DPR 1):
- `landing-hero-1440.png`, `landing-principles-1440.png`, `landing-ecosystem-1440.png`, `landing-doorways-1440.png`, `landing-full-1440.png`
- `landing-hero-390.png`, `landing-390.png` (full page)
- `ml-top-1440.png`, `ml-1440.png` (full), `ml-390.png` (full)
- `ml-principles-top-1440.png`, `ml-principles-1440.png` (full), `ml-principles-390.png` (full)
- `family-weft-1440.png` (full)
- `alt-observatory-1440.png`, `alt-threshold-1440.png`
- States: `state-weft-door-hover-1440.png`, `state-direction-card-hover-1440.png`, `state-ml-weft-row-hover-1440.png`
