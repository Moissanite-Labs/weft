# Siliconcordat / Moissanite Labs — public site design spec

**Arrangement 2026-11-10** (revision dated Tuesday 2026-11-10, America/Chicago)
Status: design package for a **staging preview** at `staging.siliconcordat.com`, then nizam → smith → ship. Lumen does not deploy.
Package root: `/workspace/siliconcordat-design/`

This document is the build contract. If a state, size or rule isn't written here, take it from the prototype CSS (`prototypes/site.css` for `/`, `/ml`, `/ml/*`; `prototypes/observatory.css` for Observatory), which is the reference implementation. If the two disagree, this document wins and the prototype is the bug.

The previous contract (2026-11-08, Carbon–Silicon Cut at the apex, Observatory and Threshold unused) is kept for history at `refs/prev-2026-11-08/SPEC.md`. It is superseded.

---

## 1. Intent and hard constraints

**Intent.** One house (Moissanite Labs), three public rooms, and one hidden one:

| Path | Room | Look | Job |
|---|---|---|---|
| `siliconcordat.com/` | The proposal | **Threshold**: split-seam hero (warm carbon left, cool silicon right, bright seam), quiet chapters below | Sets The Siliconcordat: working proposal, mission, name, six principles, ecosystem directions, doorways. |
| `siliconcordat.com/ml` | The lab | **Chamber hero** (the 2026-11-08 apex hero, moved here) over the existing lab index | Moissanite Labs: about, directions index, principles, deeper pages (`/ml/principles/`, later `/ml/exo/` etc.). |
| `siliconcordat.com/weft` | One public research program | Weft, **unchanged** | The current w3ft.org Weft experience. Only wayfinding links are added (§5.3). |
| `observatory.askaconsult.com` | Observatory (easter egg) | **Observatory**: instrument-lab register, cool neutrals, grid, calibration spectrum | The same Siliconcordat substance restated as an instrument plate. Reached only from a hidden spot on the Threshold seam (§6A). Not in any nav. |
| `staging.siliconcordat.com` | Preview host | — | Preview of this whole arrangement before ship (§15A). Observatory may be served at `/observatory/` on staging. |

**Hard constraints (non-negotiable).**
1. URL map above is fixed. `/w3ft` → `/weft` and apex aliases are not part of this design.
2. Copy comes only from The Siliconcordat (Moissanite-Labs/compass `README.md`), as quoted in §10. No FOUNDER-VISION.md, SILICONCORDAT.md or NAMING.md content. No slogans, traction, team, waitlist, newsletter, metrics or taglines. Herald owns marketing copy; the few structural labels this design needs are listed in §10.3 so herald can replace them.
3. Every page (including Observatory) keeps the README's humility: working proposal, not adopted policy, not a legal agreement, directions not capabilities.
4. Link rule (§10.4): only confirmed-public URLs. Never link compass, credos, weft (except on /ml and /ml/notes-from-the-colony/ per §16.2), weft-eido, weft-corpus, or GitHub copies of the manifesto files. Weft is always linked as `/weft` (absolute `https://siliconcordat.com/weft` from Observatory), never GitHub.
5. Weft is not restyled. No new palette, type, chrome removal, loom change or overlay on `/weft`.
6. Not folded into askaconsult.com. **One explicit owner exception:** the Observatory easter-egg landing is hosted at `observatory.askaconsult.com`. That page carries **no** askaconsult branding, nav or hosting story, and the main lab site is not moved, linked into, or branded by askaconsult. The Exo card still links to `exo.askaconsult.com`. Those are the only two askaconsult strings in the system (one is a hidden href).
7. Dark only. No theme toggle on `/`, `/ml`, `/ml/*` or Observatory.
8. Build contracts: mobile Lighthouse ≥ 80 (target 90+), WCAG 2.2 AA, visible focus, skip link, reduced motion, no colour-only current-nav, no dark patterns, self-hosted fonts, `assets/` is the only asset source.

---

## 2. Arrangement and history

The owner liked all three directions from the 2026-11-08 package and assigned each a room (2026-11-10):

- **Threshold → apex `/`.** The split seam is the memorable first frame. Its two known risks are handled by rule: (a) text crossing the seam gets a soft scrim and glyph halo so AA holds on both halves (§6b, measured in §12); (b) the split is **hero-only**. Below the fold the page is calm: same tokens and type as the rest of the house, with the Threshold carried only as a 1px carbon→fire→silicon hairline and a short seam stub at the top of each chapter (§6c). No chapter is a literal split.
- **Carbon–Silicon Cut chamber → `/ml` hero.** The live apex hero (crystal, caustics, atmosphere, typography, fig caption) moves onto the lab page, replacing the framed specimen that made `/ml` read as plain. Visual unchanged; the heading becomes the lab's own ("Moissanite Labs") because "The Siliconcordat" now belongs to the apex (§7).
- **Observatory → `observatory.askaconsult.com`.** A full landing in its own cool instrument palette, reached as an easter egg from the seam (§6A, §7A). It restates the same proposal; it is not a second manifesto, a joke page or a second marketing site.

Carbon–Silicon Cut tokens (`tokens.css`) remain the house tokens for `/`, `/ml`, `/ml/*`. Threshold's hero surfaces are additional hero-only colours (§3.7). Observatory has its own palette (§3.8) and shares only the fonts and the mark.

Historical hero frames remain at `prototypes/alts/threshold.html` and `prototypes/alts/observatory.html` (labelled "Historical frame · superseded"), with their original shots `shots/alt-threshold-1440.png` and `shots/alt-observatory-1440.png`. The 2026-11-08 prototypes and shots are in `refs/prev-2026-11-08/` and `shots/prev-2026-11-08/`. The live HTML/CSS as of 2026-11-10 is in `refs/live/`.

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
| `/` Threshold h1 "The Siliconcordat" | `clamp(2.9rem, 1.2rem + 7vw, 9rem)` (≈120px at 1440, 46px at 390), centred, one line on desktop | 360 | 0.92 |
| `/` Threshold lede (mission) | `clamp(1.2rem, 1rem + .8vw, 1.625rem)`, Source Serif `opsz 24`, `--ink`, max 34ch, centred | 380 | 1.38 |
| `/ml` chamber h1 "Moissanite Labs" | `clamp(3rem, 1rem + 7vw, 8rem)` (≈117px at 1440, 48px at 390), max 9ch | 360 | 0.92 |
| `/ml` chamber lede (mission) | `clamp(1.25rem, 1rem + .9vw, 1.75rem)`, Source Serif `opsz 24`, `--ink-2`, max 31ch | 380 | 1.38 |
| Chapter title (h2 on `/`) | `clamp(2.25rem, 1.4rem + 3vw, 4rem)` | 380 | 1.02 |
| Pull quote | `clamp(1.9rem, 1.2rem + 2.4vw, 3.25rem)` | 360 | 1.12 |
| Deeper-page h1 (`/ml/*`) | `clamp(2.75rem, 1.6rem + 4vw, 5.25rem)` | 360 | 0.98 |
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
- `assets/chamber.svg` (6 KB), used as the `/ml` hero crystal: three translucent hexagonal crystals, flat-shaded from a cool key at upper right and a warm fill at lower left, with champagne cut edges. Illustrative. Generated by `tools/make_chamber.py`.
- `assets/caustic.webp` (92 KB, 768×768, seamless): angular light facets (periodic Voronoi cells) with thin bright cut lines and slight warm/cool dispersion. Generated by `tools/make_caustic.py`.
- No photography. No stock scientists, no actors, no engagement-ring moissanite, no video.

### 3.5 Motion
| What | Behaviour | Reduced motion |
|---|---|---|
| `/ml` chamber caustic layer A | `transform: translate3d` drifts one tile (768px) diagonally over **36s**, linear, infinite. Opacity 0.16, `mix-blend-mode: screen`, radial-masked to the crystal. | No animation (static). |
| `/ml` chamber caustic layer B | Same texture at 1100px, opposite diagonal, **52s**, opacity 0.12. | Static. |
| `/ml` chamber seam | 1px vertical champagne→ember gradient at 61% width with a faint glow. Static. Hidden under 860px. | Same. |
| Threshold seam (`/`) | 2px static vertical line at 50%, glow via box-shadow. **No animation, ever.** | Same. |
| Easter-egg hover/focus (`/`) | Seam segment and jewel brighten over 180ms. No pulse, no loop. | Instant change (no transition). |
| Chapter reveal | Elements with `.reveal`: opacity 0→1 and translateY 14px→0 over 900ms `cubic-bezier(.22,.61,.36,1)`, once, when 8% into the viewport. Only when JS has added `.js` to `<html>`. | Shown immediately; no transition. |
| Hover/focus on links, cards | 180ms colour/border transitions; arrows nudge 3–4px. | Transitions removed. |
| Weft doorway | Sliver widens 10px → 34% over 520ms on hover/focus. | Instant switch, no transition. |
| Smooth scroll | Only under `prefers-reduced-motion: no-preference`. | Off. |
No parallax, no bounce, no pulsing (including on the easter egg), no pause/play controls (nothing should look like it pauses real work). Animations are compositor-only (transform/opacity).

### 3.6 Tone
Quiet, filmic, humble. A research lab that happens to look like a still from a serious science-fiction film. Captions state what things are ("Fig. 1 — illustration"). Nothing is "live", "launching", or "join". Status words: **Direction**, **Direction · foundation**, **Open research program**, **Aspiration**. Never "Live product", "Beta", "Coming soon".

### 3.7 Threshold hero surfaces (apex hero only; not tokens)
| Surface | Value |
|---|---|
| Carbon half | `radial-gradient(90% 80% at 85% 60%, #3a2414 0%, #1d130b 45%, #0d0907 100%)` |
| Silicon half | `radial-gradient(90% 80% at 15% 40%, #2a333e 0%, #141a21 45%, #08090c 100%)` |
| Facet hatch (both halves) | two `repeating-linear-gradient`s at ±60°, 1px lines every 61px, `rgb(255 255 255/.025)`, layer opacity .5 |
| Seam | 2px at `left: 50%`; `linear-gradient(180deg, transparent 4%, rgb(243 230 198/.4) 18%, #f3e6c6 34%, #fff8e6 54%, #f3e6c6 78%, transparent)`; glow `0 0 24px 4px rgb(230 210 168/.42), 0 0 120px 30px rgb(230 210 168/.11)` |
| Centre scrim | ellipse `min(1240px, 112vw)` × `min(640px, 82%)` centred at 50% / 52%: `radial-gradient(closest-side, rgb(8 7 6/.62) 0%, rgb(8 7 6/.52) 45%, rgb(8 7 6/.26) 75%, transparent)` |
| Banner scrim | behind the proposal block, inset −44px −140px: `radial-gradient(closest-side, rgb(8 7 6/.72), rgb(8 7 6/.5) 50%, rgb(8 7 6/.18) 80%, transparent)` |
| Glyph halo | title, lede and banner: `text-shadow: 0 0 2px rgb(8 7 6/.95), 0 0 14px rgb(8 7 6/.9)` |
These values were tuned until the measured contrast in §12 passed. If smith changes any of them, re-run `tools/contrast.mjs`.

### 3.8 Observatory palette (`observatory.css`; Observatory only)
| Token | Value | Role |
|---|---|---|
| `--o-bg` / `--o-bg-2` / `--o-surface` | `#0d0f11` / `#12151a` / `#151920` | Plate ground, footer/notes, door hover |
| `--o-ink` / `--o-ink-2` | `#e9ebee` / `#b9bfc7` | Headings and readouts / body |
| `--o-muted` | `#8b939d` | Mono captions (≥ 5.8:1 on the plate, measured) |
| `--o-line` / `--o-line-2` / `--o-tick` | `#222830` / `#333b45` / `#5b6571` | 96px measurement grid (64px under 600px), rules, scale ticks |
| `--o-focus` / `--o-fire` | `#e6d2a8` | Focus ring; the one warm accent (chip swatch, note corner) |
| `--o-weft` / `--o-weft-bg` | `#7fcbe3` / `#060a12` | Only on things that point at Weft |
| Spectrum | `#3a1d5c → #2a3f9a → #2f7fb5 → #3fae8c → #b9c55a → #e6c46a → #e08a3e → #b03a2e`, `saturate(.55) brightness(.8)`, 1px dark slits every 8px | Calibration plate (Fig. B1) and the small per-direction spectral bars |
Not Weft's marble-teal/slate; not the Carbon–Silicon Cut warm tokens. Display type is IBM Plex Sans 400 (tight tracking, −0.035 to −0.04em); captions IBM Plex Mono. No Source Serif on Observatory.

---

## 4. Anti-slop checklist (design)
No purple gradients · no glassmorphism blur soup (the only blur is the sticky header's 10px backdrop) · no neon · no hero video · no stock people · no 16px-rounded cards (2px / 4px only) · no Inter · no aqua chrome buttons on `/` or `/ml` · no woven/textile pattern on `/` or `/ml` · no gradient text · no fake metrics, logos wall, testimonials, newsletter, countdown.

---

## 5. Family and navigation

### 5.1 Visitor path
Landing ("the house / the proposal", Threshold) ↔ `/ml` ("the lab", chamber) ↔ `/weft` ("one public research program"). Every page on `/` and `/ml` can reach the other two in one click, from the header and the footer. Observatory is **not** in any nav; it is reached only from the seam (§6A) and links back to all three.

### 5.2 Family header (on `/` and `/ml`) — this is the header

On `/` (Threshold variant, three columns that echo the split):
```
Moissanite Labs                     [mark] Siliconcordat                     ◇ Weft
 (carbon side, left)                (centred on the seam, current)          (silicon side, right)
```
On `/ml` and `/ml/*` (standard variant):
```
[mark] Siliconcordat     Moissanite Labs     ◇ Weft                    [WORKING PROPOSAL chip]
```
- Height 64px. `--gutter` side padding, max width = page max (`1280` on `/`, `1120` on `/ml`).
- Links: "Siliconcordat" → `/`, "Moissanite Labs" → `/ml`, "Weft" → `/weft`. Same tab.
- Items: Plex Sans 500 0.875rem `--ink-2`; hover `--ink`. Brand item: Source Serif 500 1.125rem `--ink`. Each target ≥ 44px tall.
- **Current item:** `aria-current="page"` + text `--ink` + **1px `--fire` underline** (9px above the bar's bottom) + **5px fire diamond** centred under it. Never colour alone. On `/`, Siliconcordat is current; on `/ml` and `/ml/*`, Moissanite Labs is current.
- **Weft item:** a 6px diamond tick before "Weft": fill `--weft-bg`, 1px `--weft-link` outline. Hover: text and tick turn `--weft-link` (the tick fills). This is the only aqua in the header.
- **On `/` (Threshold):** `ul.fam.th-fam` is a 3-column grid (`1fr auto 1fr`) spanning the full width minus `--gutter`: "Moissanite Labs" left-aligned, mark + "Siliconcordat" centred (current), "Weft" right-aligned. DOM and tab order: Moissanite Labs → Siliconcordat → Weft. No menu: at ≤ 720px links tighten (0.8125rem, 8px padding); at ≤ 480px the "Siliconcordat" word is visually hidden (kept for assistive tech) and the mark alone carries the current underline + diamond. The header is `position: fixed` over the hero with a top-down fade (`rgb(10 9 8/.7)` → transparent) and no border. After 24px of scroll (`.is-scrolled`), it becomes `rgb(10 9 8/.7)` + 10px backdrop blur + 1px `--line` bottom border. No chip in the landing header (the hero has it).
- **On `/ml`:** `position: sticky`, solid treatment from the start, and the "Working proposal" chip at the right.
- **Mobile (≤ 720px), `/ml` and `/ml/*`:** mark + "Siliconcordat" stays; the other links and the chip collapse into `<details class="menu">` with a 44×44 "Menu" summary (mono, 1px `--line-2` border, fire border when open). Panel: `--surface`, 1px `--line-2`, 2px radius, rows 48px tall, 1px `--line` separators. Current row: 2px inset fire bar on the left and a mono "HERE" tag on the right. Escape closes the menu and returns focus to the summary. Works without JS.

### 5.3 On `/weft` — wayfinding, not a restyle (recommended default)
Annotation: `prototypes/family-weft.html` · shot: `shots/family-weft-1440.png`. Facsimiles are simplified redraws for annotation only.

Weft's current header has one link (mark + "ML Weft" + "Moissanite Labs") to Weft home. Change only that block:
1. Weave-mark + "ML Weft" stay one link to Weft home (`/weft/`; `/` while still served on w3ft.org). `aria-label="ML Weft home"` unchanged.
2. "Moissanite Labs" becomes its own `<a class="brand-org" href="/ml">`, using Weft's existing `.brand-org` type, size (0.78rem), colour (`#86a0b5`) and left rule (`#21435c`).
3. Add `<a class="brand-org" href="/">Siliconcordat</a>` after it, identical style. Hover: Weft `--link-hover` `#cfe8f3` + underline. Focus: Weft's own aqua outline. No champagne, no Source Serif, no Plex.
4. While Weft is served on w3ft.org, links 2 and 3 are absolute: `https://siliconcordat.com/ml` and `https://siliconcordat.com/`.
5. Under 860px Weft already hides `.brand-org`; keep that, and append to the bottom of Weft's existing `.menu-panel`, after a 1px Weft `--line` rule, a muted "Moissanite Labs family" label plus "Moissanite Labs" and "Siliconcordat" links in Weft's menu-link style.

Markup and CSS for Weft are in the annotation page (two code blocks). The annotation also notes the 2026-11-10 arrangement: Weft's "Siliconcordat" link lands on the Threshold landing, "Moissanite Labs" on the chamber-hero `/ml`; Observatory is never added to Weft's header or menu. Nothing else on `/weft` changes: no colours, fonts, chrome, loom canvas, theme toggle, GitHub button, sections or footer.

**Fallback (not default):** a 32px rail above Weft's header, painted only in Weft tokens (`#060a12` ground, `#86a0b5` links, `#7fcbe3` for current "Weft", `#142a3c` rule, Weft system type at 0.78rem) listing Siliconcordat · Moissanite Labs · Weft. Not recommended: two stacked headers read as two sites.

### 5.4 Observatory header
`Siliconcordat` (mark + mono uppercase, → main landing) · `Moissanite Labs` (→ `/ml`) · `◇ Weft` (→ `/weft`, aqua tick) … right: mono "◇ Observatory · plate 00" (a non-link location label; this is how current location is shown, not by colour) and a quiet "← Main landing" link behind a 1px rule. 56px tall, 1px `--o-line` bottom, solid `--o-bg`. ≤ 860px: the location label and "← Main landing" hide (the Siliconcordat link is the way back). ≤ 600px: the Siliconcordat word is visually hidden, mark only. No askaconsult name anywhere. In production all three family links are absolute (§10.4).

---

## 6. Layout: `/` (Threshold landing) — `prototypes/landing.html`
Max width 1280px for chapters, `--gutter` = `clamp(20px, 5vw, 48px)`. Shots: `landing-hero-1440.png`, `landing-principles-1440.png`, `landing-ecosystem-1440.png`, `landing-doorways-1440.png`, `landing-full-1440.png`, `landing-hero-390.png`, `landing-390.png`.

**a. Family header.** Threshold variant (§5.2), fixed overlay with the scroll state.

**b. Hero (`<section class="th-hero">`).** `min-height: max(720px, 100svh)`; two equal grid halves (§3.7), the seam at exactly 50%, all decorative layers `aria-hidden`.
- Content is centred on the seam (`.th-center`, text-align centre, symmetric `--gutter` padding so the column's centre **is** the seam): (1) **proposal block**: "WORKING PROPOSAL" chip, then the full banner sentence (Plex Sans 0.9375rem `--ink-2`, max 40rem), never hidden; (2) **h1 "The Siliconcordat"** straddling the seam: Source Serif 4 360, `clamp(2.9rem, 1.2rem + 7vw, 9rem)` (≈120px at 1440, ≈46px at 390), line-height .92, tracking −0.03em, `opsz 60`, "The" and "Siliconcordat" each `nowrap` so the title wraps only between the two words; (3) **mission lede**: Source Serif 380, `clamp(1.2rem, 1rem + .8vw, 1.625rem)`, `--ink`, max 34ch; (4) **actions row**: a 3-column grid `1fr 44px 1fr`, max 640px: "Principles ↓" (→ `#principles`) right-aligned on the carbon side, the **easter-egg jewel** in the 44px centre cell on the seam (§6A), "Moissanite Labs →" (→ `/ml`) left-aligned on the silicon side. Text links are the standard `.textlink`.
- Element labels bottom-left "C · CARBON" (`--carbon`) and bottom-right "Si · SILICON" (`--silicon`), mono 0.6875rem, tracking .16em, `aria-hidden` (decorative; the name chapter states the elements in text).
- **Contrast rule (the a11y fix):** text that crosses the seam must meet AA against the brightest backdrop pixel within 2px of its glyphs, on both halves, at every width. This is achieved with three layers, none of them an opaque box: the centre scrim, the banner scrim, and the glyph halo (§3.7). The split must still read: the scrim fades to 0 before the outer thirds of each half, and the seam stays visible above, between and below the text. Verify with `node tools/contrast.mjs landing.html <w> <h> ".th-proposal p,.th-title,.th-lede"` (§12).
- **Mobile:** keep the vertical seam (it is the signature; **never** switch to a horizontal split). Padding tightens (`header + 28px` top, 72px bottom); banner 0.875rem; actions gap 8px and 0.875rem; labels at 24px from the bottom. The title wraps to "The / Siliconcordat" only if needed.
- No scroll cue (the seam is the only vertical mark on the hero; a second one would compete with the easter egg).

**c. Chapters below the fold: no split.** Chapter 01 The name, 02 Principles, 03 Ecosystem (with constellation and direction cards), 04 Doorways, then the footer: identical in content, layout and components to the 2026-11-08 landing (the specs that follow are unchanged). The Threshold continues only as:
- each `.chapter` has no bottom border; instead a **1px top hairline** `linear-gradient(90deg, transparent, rgb(196 132 74/.4) 22%, rgb(230 210 168/.7) 50%, rgb(157 176 196/.4) 78%, transparent)` and a **seam stub**: 1px × 56px (36px under 600px) at 50%, `rgb(230 210 168/.55)` → transparent. Decorative, `pointer-events: none`.
- the footer gets a 1px `--line` top rule.
Nothing else in the chapters is warm-left/cool-right.

- **01 The name (`#name`).** Chapter marker: mono "01 THE NAME" with the number in fire and a hairline to the right edge. Two columns 5fr / 6fr, gap `clamp(40px, 7vw, 112px)`. Left: pull quote (README sentence: "The bond between silicon and carbon is a metaphor for the symbiosis the lab wants to cultivate.") then the **element plate**: Si tile (14, Silicon, cool border and glow) — bond line (silicon→fire→carbon gradient, "SiC" label) — C tile (6, Carbon, warm). Caption "Moissanite · a naturally occurring form of silicon carbide". Right: README paragraph 1 in full, split into three paragraphs (mission at 1.1875rem `--ink`; name; Siliconcordat). Then the **caveat block** in readable body type: 1px fire left rule with a fire diamond at the top, mono label "WHAT THE METAPHOR IS NOT", and the sentence in `--ink` 1.0625rem. Under 860px the columns stack.
- **02 Principles (`#principles`).** Head row: h2 "We intend to build for:" and mono "Six principles · proposed for review". Then `<ol class="principles">`: 3×2 grid at ≥ 1081px, 2×3 at 601–1080px, 1 column ≤ 600px. Hairline-ruled cells, min-height 300px desktop, 32px padding, a 28px fire tick on each cell's top-left edge; mono numeral "01"–"06" in fire with a 24px rule; h3 principle name; the full README text. Not interactive. Each `<li>` has an id equal to the principle slug (§10.2).
- **03 Ecosystem (`#ecosystem`).** h2 "Building the ecosystem" + README paragraph 2 + **Status note** (mono "STATUS" in fire, README caveat sentence in `--ink`). Then the **constellation figure** (hidden ≤ 600px; cards carry the same information): warm→champagne→cool foundation line "EXO · FOUNDATION", four nodes (Exofab, Synbios, Koinos, Ethos — each "DIRECTION"), a dashed extension with a hollow node "ROBOTICS / ASPIRATION". Caption: "Fig. 2 — Directions for work, drawn on the Exo foundation. Robotics sits off the line: an aspiration." Then the **direction cards** (§8.5), 3 / 2 / 1 columns: Exo, Exofab, Synbios, Koinos, Ethos, Robotics (aspiration).
- **04 Doorways (`#doorways`).** Two equal panels, min-height 380px (300px on mobile), stacked under 860px: **Moissanite Labs** → `/ml` (kicker "THE LAB … /ml", title, description, "Enter the lab →", warm/cool glows and mark watermark; hover/focus border → fire 60%) and **Weft** → `/weft` (§8.7). Observatory is **not** a doorway.

**d. Footer.** Two columns (4fr / 7fr, stacked under 860px). Left: mark + "Siliconcordat" (→ `/`), family list with mono paths (`The Siliconcordat /`, `Moissanite Labs /ml`, `Weft /weft`), current page underlined in fire. Right: **humility block** (mono "WORKING PROPOSAL" in fire, banner sentence, caveat sentence). Base row: mono "Moissanite Labs", a source link to `https://github.com/Moissanite-Labs/siliconcordat` (label `github.com/Moissanite-Labs/siliconcordat`, same `.meta` style as the neighbouring labels, plus visually hidden "(external site)"), and "siliconcordat.com". This source link is already live on the current `/` and `/ml` footers; keep it. No Observatory link in the footer.

---

## 6A. The easter egg — hidden spot on the seam
Shots: `state-seam-hover-1440.png`, `state-seam-focus-1440.png`, `state-seam-focus-390.png`.

**Placement.** The centre cell of the hero actions row, i.e. on the seam just below the lede, between "Principles ↓" and "Moissanite Labs →". It is the seam's brightest node: where the scrim has dimmed the seam behind the text, the seam "re-emerges" here.

**Markup.**
```html
<a class="th-egg" href="https://observatory.askaconsult.com/" aria-label="Observatory">
  <span class="th-egg__jewel" aria-hidden="true"></span>
  <span class="th-egg__label" aria-hidden="true">Observatory</span>
</a>
```
**At rest.** Hit area 44 × 88px (meets WCAG 2.5.8 target size with margin), `display: block`, no border, no background, no visible text. Inside: a 2px vertical seam segment exactly over the hero seam (`rgb(243 230 198/.62)` at its centre, fading to 0 at both ends) and a 7px rotated-square jewel at the centre (`#f7eed8`, opacity .7, `0 0 10px 2px rgb(230 210 168/.28)` glow). It reads as a node on the seam (like a separator between the two links), not as a button.
**Hover (the discovery moment).** Segment → `rgb(255 248 230/.95)` with `0 0 18px 2px rgb(230 210 168/.35)`; jewel opacity 1 with `0 0 16px 4px rgb(243 230 198/.5)`. 180ms. No label on hover (the cursor change is the hint; the label is for keyboard users).
**Focus-visible.** Standard 2px `--focus` outline, offset 3px, around the 44 × 88 area; segment at full `#fff8e6` with a stronger glow; jewel glow `0 0 22px 6px`; the mono label "OBSERVATORY" (0.6875rem, tracking .14em, `--fire` on a `rgb(8 7 6/.92)` 4×6px-padded backing, 12:1) appears just below and to the right of the seam (`left: calc(50% + 14px)`), so it never sits on the seam itself.
**Tab order.** Skip link → Moissanite Labs → Siliconcordat → Weft → Principles ↓ → **Observatory** → Moissanite Labs → … It is a normal link in DOM order, never `tabindex="-1"`, never a 1×1 trap. Its accessible name is "Observatory" (the visible focus label matches it, per WCAG 2.5.3).
**Reduced motion.** No animation of any kind at any setting (no pulse). Under `prefers-reduced-motion: reduce`, hover/focus changes apply instantly (no transition).
**Href rules.**
- Production: `https://observatory.askaconsult.com/` (same tab; it is a sibling page, not marked ↗ because there is no visible text to mark).
- Staging: if Observatory is served on the same host for preview, point the control at `/observatory/` on `staging.siliconcordat.com` (§15A). Smith may make the href a build variable.
- Prototype: `observatory.html` so click-through works locally.
**Never:** no tooltip at rest, no "psst"/teaser copy, no analytics hook, no second hidden spot, no link to Observatory in nav, footer or doorways.

---

## 7. Layout: `/ml` (the lab) — `prototypes/ml.html`
Same tokens; 1120px max for content. The chamber hero is the lab entrance; everything below it is the lab index as before. Shots: `ml-top-1440.png`, `ml-1440.png`, `ml-390.png`, `ml-top-390.png`.

1. **Family header** (standard variant, sticky; Moissanite Labs current; chip on the right).
2. **Local nav** (sticky under the header at 64px; 48px tall; 1px `--line` bottom): mono "MOISSANITE LABS" label, then **About · Directions · Principles**. On `/ml` they are in-page anchors (`#about`, `#directions`, `#principles`); the current section uses `aria-current="location"` with the same 1px fire underline. On deeper pages, "Principles" links to `/ml/principles/` and carries `aria-current="page"`. Horizontally scrollable on narrow screens, no scrollbar.
3. **Chamber hero (`<section class="hero hero--lab">`) — transplanted from the 2026-11-08 apex.** Visual treatment is the old apex hero, unchanged: the same `.chamber` stack (three radial gradients; `chamber.svg` at `min(1320px, 92vw)`, right −4vw, opacity .78, radial mask; caustic layers A/B drifting 36s/52s; 1px seam at 61%; floor fade), the same type and the same lab caption bottom-right ("Si · C — silicon carbide" / "Fig. 1 — illustration, hexagonal habit"). What changes:
   - **Heading is the lab's:** mono eyebrow "THE LAB" (fire), h1 **"Moissanite Labs"** in the hero title style at `clamp(3rem, 1rem + 7vw, 8rem)` (≈117px at 1440, 48px at 390), max 9ch so it sets as "Moissanite / Labs"; then the mission sentence as `.hero__lede`. No proposal banner in this hero (the chip is in the header and the About aside; the banner is in the footer).
   - **Actions** are in-page jumps plus the way back: "About ↓", "Directions ↓", "Principles ↓", "The Siliconcordat →" (→ `/`).
   - Height `max(620px, 100svh − header − local nav)` so the chamber fills the first screen under the two sticky bars; content bottom-anchored with `clamp(64px, 12vh, 140px)` top padding (header is not overlaid here).
   - The fig caption gets a soft void halo (`text-shadow: 0 0 2px/10px/18px var(--bg)`) and `--ink-2` so it holds AA over crystal facets (it measured 4.43:1 on the old apex; now ≥ 9.3:1).
   - ≤ 860px: crystal moves to the top-right (150vw, opacity .5), seam and caption hidden, hero min-height 640px, text starts 220px down so it sits under the crystal, not over its brightest facets.
4. **About** (`#about`): 3fr / 8fr. Left: h2 "About", mono "From the Siliconcordat", proposal chip. Right: README paragraph 1 (mission first in Source Serif 1.375rem; name; Siliconcordat), the caveat block, README paragraph 2, "Read the Siliconcordat →" to `/`. No team, bios or founder names.
5. **Directions** (`#directions`): h2 + mono count "Index · 5 directions · 1 program · 1 aspiration"; Status note; index table `ID | name | description | status + link` (64px / 1.6fr / 4fr / 3fr). D-01…D-05, P-01 Weft under "PUBLIC RESEARCH PROGRAM", A-01 Robotics under "ASPIRATION". Row states §8.6.
6. **Principles** (`#principles`): h2 + mono "We intend to build for:"; 2-column index of the six linking to `/ml/principles/#slug`; "All six principles →".
7. **Footer** (Moissanite Labs current).

The previous framed specimen ("instrument plate", `.plate`) is retired from `/ml`; its CSS stays in `site.css` for possible reuse on deeper pages but is unused. `/ml/principles/` is unchanged (§9): it already uses the lab's doc template and does not reference the plate, so the transplant creates no inconsistency.

---

## 7A. Layout: Observatory (easter egg) — `prototypes/observatory.html` + `prototypes/observatory.css`
Production `https://observatory.askaconsult.com/`; staging `/observatory/` on `staging.siliconcordat.com`. Max width 1280px, `--o-gutter` = `clamp(20px, 5vw, 48px)`. Shots: `observatory-hero-1440.png`, `observatory-1440.png`, `observatory-390.png`, `observatory-hero-390.png`.

The same Siliconcordat substance as `/`, restated as numbered instrument **plates**. Same README text, same order, same caveats. Not a different manifesto and not a joke.

1. **Header** (§5.4).
2. **Plate 00 — hero (`.o-plate`).** `min-height: max(700px, 100svh − 56px)`; 96px measurement grid (1px `--o-line`) under a radial vignette; two crosshair registration marks. Grid 7fr / 5fr:
   - Left column: proposal block (chip with a dark→champagne swatch + "WORKING PROPOSAL"; full banner sentence), h1 with a mono kicker line "MOISSANITE LABS · MANIFESTO" and "The Siliconcordat" in Plex Sans 400 `clamp(2.75rem, 1.5rem + 5.4vw, 7rem)`, tracking −0.04em; mission lede (Plex Sans 1.2–1.375rem, `--o-ink-2`, 32ch); mono text links "PRINCIPLES ↓" / "DIRECTIONS ↓".
   - Right column, the **instrument** (`<figure>`): caption "Fig. B1 — calibration plate · fire as dispersion, illustrative"; the 120px spectrum with four 1px emission lines and a 400–700 nm scale; the element **readout** as a `<dl>` (Element Si · 14 / Element C · 6 / Compound SiC / Mineral Moissanite); foot caption "Si · C — silicon carbide · illustration".
   - ≤ 860px: the instrument stacks **below** the title (border-top instead of border-left), crosshairs hide, grid stays (64px under 600px) and the spectrum keeps full width.
3. **Plate 01 — The name (`#name`).** Mono plate marker (boxed "PLATE 01" + label + a tick-ruler rule). Left: h2 = the README bond sentence; a ruled sample (Z 14 Si — SiC — Z 6 C) with `aria-label`; caption "Fig. B2 — Moissanite · a naturally occurring form of silicon carbide". Right: README paragraph 1 (three paragraphs) and the caveat as a bordered **Note** ("NOTE · WHAT THE METAPHOR IS NOT"), champagne corner tick.
4. **Plate 02 — Principles (`#principles`).** h2 "We intend to build for:" + "Six principles · proposed for review". 3×2 ruled grid (2 / 1 columns at 1080 / 600px): mono "§01"–"§06" with a tick ruler, h3 name, README text. Ids = slugs (§10.2). Static.
5. **Plate 03 — Ecosystem (`#ecosystem`).** h2 "Building the ecosystem", README paragraph 2, **Status** note with the directions caveat. Then an instrument table: `ID | spectral bar | name | description | status + link` (64 / 120px / 1.4fr / 3.6fr / 2.6fr). Each direction's spectral bar is a muted copy of the spectrum with one emission line at a fixed position (decorative, `aria-hidden`; it implies no measurement). D-01…D-05 link per §10.4 (stretched title link, ↗ URL label `aria-hidden`, hidden "(external site)"; Synbios GitHub secondary; Koinos synmerit aside); Exo's status diamond filled ("Direction · foundation"). P-01 Weft (aqua-outlined navy bar, "/weft →" in aqua, hover darkens toward Weft navy with a 2px aqua inset). A-01 Robotics (dashed bar, dashed rule, no link). ≤ 600px the row collapses to `ID | content`.
6. **Plate 04 — Doorways (`#doorways`).** Three ruled cells: The Siliconcordat (→ main landing, "Main landing →"), Moissanite Labs (→ `/ml`, "Enter the lab →"), Weft (→ `/weft`, aqua kicker and a 6px Weft-navy edge, "Open Weft →"). Hover: `--o-surface` fill and full-ink action underline. Focus: champagne ring inset 4px.
7. **Footer.** Family links with mono paths, humility block (banner + caveat), base row "Moissanite Labs" / the same `https://github.com/Moissanite-Labs/siliconcordat` source link as `/` and `/ml` / "Observatory · plate 05". No askaconsult name, no copyright, no social.

States: focus ring 2px `--o-focus` (champagne) offset 3px everywhere; reveal on scroll as on `/` (off under reduced motion; smooth scroll off too). No animation on the spectrum. No theme toggle.

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
§6d. Family links ≥ 40px tall; Weft link hover `--weft-link`; current page underlined in fire (6px offset). The footer base row keeps the already-live source link `https://github.com/Moissanite-Labs/siliconcordat` (§10.4) between "Moissanite Labs" and "siliconcordat.com".

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
- The banner appears on `/` (hero + footer), `/ml` (footer; chip in header and About), every `/ml/*` page (doc head + footer), and Observatory (Plate 00 + footer).
- The substrate caveat ("The metaphor is not a claim … nor is this document a legal agreement.") appears in body type on `/` (chapter 01) and `/ml` (About), and in every footer.
- The directions caveat ("These are directions for work … remain open.") appears directly above the directions on `/` and `/ml`.
- "A future robotics role is an aspiration, not a present capability." appears as the Robotics card/row text.

### 10.2 Principle slugs
`symbiosis`, `agency-and-consent`, `interoperability`, `traceability`, `real-world-outcomes`, `adaptation-with-control`. Names and text exactly as in the README; never renamed or reordered.

### 10.3 Structural labels (not README; herald may replace, must stay neutral)
Chapter markers ("The name", "Principles", "Ecosystem", "Doorways"); Observatory plate markers ("Plate 00"–"Plate 05", "Fig. B1 — calibration plate · fire as dispersion, illustrative", "Fig. B2 — …", "Note", "Main landing", "Observatory", "Moissanite Labs · manifesto"); element labels "C · carbon", "Si · silicon"; "The lab"; "About the lab, its directions, and its principles."; "Enter the lab"; "Open Weft"; "Papers, runtime, and demos. Weft keeps its own site and design."; "Open research program"; "What the metaphor is not"; "Status"; "Fig. 1 — illustration, hexagonal habit"; "Fig. 2 — …"; "Read the Siliconcordat"; "All six principles"; element-plate facts (Si 14, C 6, "Moissanite · a naturally occurring form of silicon carbide"). None of these make product claims.

### 10.4 Links (confirmed by scout via nizam, 2026-11-08)

| Card | Primary link (title + visible label) | Secondary | Note |
|---|---|---|---|
| Exo | `https://exo.askaconsult.com/` (label `exo.askaconsult.com`) | — | Link only; no askaconsult branding/nav anywhere else. |
| Exofab | `https://moissanite-labs.github.io/exofab/` | — | GitHub repo is also public but not needed on the card. |
| Synbios | `https://moissanite-labs.github.io/synbios/` | `https://github.com/Moissanite-Labs/synbios` (label "GitHub") | If only one link fits, Pages. |
| Koinos | `https://github.com/Moissanite-Labs/synmerit` (label "Public repository") | — | Title stays "Koinos". Quiet aside: "The public repository currently lives at synmerit." |
| Ethos | `https://github.com/Moissanite-Labs/ethos` | — | |
| Weft | `/weft` | — | Never GitHub weft (except on /ml and /ml/notes-from-the-colony/ per §16.2)/weft-eido/weft-corpus. |
| Robotics | none | — | Aspiration. |
| Footer source (not a direction card) | `https://github.com/Moissanite-Labs/siliconcordat` (label `github.com/Moissanite-Labs/siliconcordat`) | — | Already live in the `/` and `/ml` footer base row (verified 2026-11-10). Keep it on `/`, `/ml`, `/ml/*`, and Observatory. This is the public site repo, not a manifesto-file or Weft-repo link. Do not add a header "View on GitHub" button. |

**Never link:** compass, credos, weft (except on /ml and /ml/notes-from-the-colony/ per §16.2), weft-eido, weft-corpus, FOUNDER-VISION.md, SILICONCORDAT.md, NAMING.md (any host). Do not copy w3ft.org's "View on GitHub" button to `/` or `/ml`. Any future direction without a confirmed public URL uses the not-linked card (§8.5).

External links: same tab, mark with ↗, and include visually hidden "(external site)".

**Observatory link rules.** Observatory lives on another host, so in production its family links are absolute: Siliconcordat / main landing → `https://siliconcordat.com/`, Moissanite Labs → `https://siliconcordat.com/ml`, Weft → `https://siliconcordat.com/weft` (staging: §15A). The direction links are the same as §10.4. The only link **to** Observatory is the seam control (§6A).

---

## 11. Assets (`assets/` is the only asset source)

| File | Size | Use |
|---|---|---|
| `assets/mark.svg` | <1 KB | Mark, favicon, header, footer, doorway watermark (inline the paths in HTML for the header to avoid a request). |
| `assets/chamber.svg` | 6 KB | Chamber hero crystal on `/ml` (not used on `/`). |
| `assets/caustic.webp` | 92 KB | `/ml` chamber caustic texture (CSS background, tiled). |
| `assets/fonts/source-serif-4-opsz.woff2` | 120 KB | Display (variable wght 200–900 + opsz). Latin subset. |
| `assets/fonts/ibm-plex-sans-{400,500,600}.woff2` | 22–24 KB each | Body/UI. Latin subset. |
| `assets/fonts/ibm-plex-mono-{400,500}.woff2` | 15 KB each | Meta. Latin subset. |
| `assets/fonts/LICENSE-*.txt` | — | SIL OFL 1.1 for each family. Ship them. |
| `tokens.css` | — | Tokens + `@font-face`. Load before site CSS as a separate `<link>` (or inline into one file at build); not via `@import`. |

`prototypes/observatory.css` is Observatory's stylesheet (with `tokens.css` for fonts). Threshold styles are in `prototypes/site.css` ("THRESHOLD LANDING" block).

Generators and checks (not shipped): `tools/contrast.mjs`, `tools/make_chamber.py`, `tools/make_caustic.py`, `tools/build_prototypes.py`, `tools/shoot.mjs`.

---

## 12. Accessibility and performance

**A11y (WCAG 2.2 AA):**
- All text pairs in §3.1 ≥ 4.5:1 (smallest: `--muted` on `--surface-2` 4.66:1). Large display text ≥ 10:1.
- **Text over atmosphere is measured, not assumed.** `tools/contrast.mjs` shoots each element with and without its glyphs, finds the brightest backdrop pixel within 2px of any glyph stroke, and reports WCAG contrast against that (worst case, not average). Results on the prototypes (2026-11-10):

| Page / viewport | Element | Min contrast | Needs |
|---|---|---|---|
| `/` 1440×900 | banner `.th-proposal p` / title / lede | 6.18 / 5.69 / 4.67 | 4.5 / 3 / 3 (lede is 26px = large) |
| `/` 1920×1080 | banner / title / lede | 5.50 / 5.83 / 4.60 | 4.5 / 3 / 3 |
| `/` 1024×768 | banner / title / lede | 6.86 / 5.44 / 4.95 | 4.5 / 3 / 3 |
| `/` 768×1024 | banner / title / lede | 7.69 / 5.15 / 5.13 | 4.5 / 3 / 4.5 |
| `/` 390×844 | banner / title / lede | 6.64 / 5.53 / 5.05 | 4.5 / 3 / 4.5 |
| `/` all | header links, C/Si labels, action links, chip | ≥ 5.9 | 4.5 |
| `/` focus | easter-egg label | 12.06 | 4.5 |
| `/ml` 1440 / 390 | eyebrow, title, lede, actions, fig caption | ≥ 8.9 (caption 9.32) | 4.5 / 3 |
| Observatory 1440 / 390 | banner, kicker, lede, chip, captions, scale, readout | ≥ 5.84 | 4.5 / 3 |

  Re-run after any change to §3.7 values: `node tools/contrast.mjs landing.html 1440 900 ".th-proposal p,.th-title,.th-lede"` (exit code 1 on any failure).
- Landmarks: one `<header>`, `<nav aria-label>` for family, local and TOC navs, `<main id="main">`, `<footer>`. One h1 per page; h2 per chapter (visually hidden where the chapter marker carries the visible label).
- Current state never colour-only (underline + diamond / inset bar + "HERE" tag).
- Focus visible on everything (2px fire, offset 3px; Observatory the same champagne). Card focus wraps the whole card. The easter egg is a real, focusable link (§6A).
- Targets ≥ 44×44 (header, menu, local nav, text links, back links).
- Decorative atmosphere, constellation SVG, crystal images: `aria-hidden` / `alt=""`. The constellation has a text figcaption and is redundant with the cards.
- Element plate has an `aria-label`. Chemical symbols are not uppercased.
- Reduced motion: §3.5. Menu works without JS (`<details>`); Escape closes it when JS is present.
- `lang="en"`.

**Performance (mobile Lighthouse ≥ 80; target 90+):**
- Static HTML + one CSS file + tokens. JS: one inline script < 1 KB (header scroll state, reveal, Escape). No frameworks, no WebGL, no Three.js.
- Preload two fonts; the rest swap in. Total font weight ≈ 240 KB on first visit; consider subsetting Source Serif to the glyphs used on `/` if LCP suffers.
- `/` (Threshold) has no image on the critical path: the hero is CSS gradients only, LCP is the h1 text. Do **not** preload `chamber.svg` on `/`.
- `/ml` preloads `chamber.svg` (`<link rel="preload" as="image" fetchpriority="high">`) because the chamber hero moved there; the caustic texture stays a CSS background off the critical path.
- Observatory loads `tokens.css` + `observatory.css` only (no `site.css`) and preloads Plex Sans 400 only; no Source Serif is requested.
- Prototype measurement (2026-11-10, Lighthouse 12 mobile, `python3 -m http.server`, no compression or caching), perf / a11y / best practices: `/` **96 / 100 / 100** (LCP 2.6 s), `/ml` **94 / 100 / 100** (LCP 3.0 s), `/ml/principles/` **97 / 100 / 100** (LCP 2.4 s), Observatory **100 / 100 / 100** (LCP 1.7 s); CLS 0 everywhere. A real host with gzip/brotli and long cache lifetimes should do better.
- Animations: transform/opacity only; `mix-blend-mode` on two layers; no animated filters.
- Images have width/height attributes; `img { height: auto }`.
- Cache-bust assets by filename hash at build.

---

## 13. Out of scope
- GitHub writes of any kind from design (no repos, PRs, issues, Pages or visibility changes).
- DNS, redirects (`/w3ft`, apex aliases, `weft.siliconcordat.com`), deploys, creating `staging.siliconcordat.com` or `observatory.askaconsult.com` (smith's, after nizam).
- Any restyle of Weft content (palette, type, chrome, loom, toggle, sections). Only the wayfinding change in §5.3.
- askaconsult.com integration of any kind beyond hosting the Observatory page (§1.6).
- Content from FOUNDER-VISION.md, SILICONCORDAT.md, NAMING.md; any invented claim, team, metric, CTA or slogan.
- Light theme, i18n, CMS, analytics (including on the easter egg), newsletter, contact forms.

---

## 14. Visitor / build acceptance checklist (smith ticks)

**Identity**
- [ ] `tokens.css` values match §3.1 exactly; no Weft hexes outside `--weft-*` uses. Threshold surfaces match §3.7; Observatory palette matches §3.8.
- [ ] Display on `/` and `/ml` is Source Serif 4 upright; Observatory display is Plex Sans. No italic coloured tagline anywhere; no Palatino/Iowan/Inter in any stack.
- [ ] Radii are 2px/4px only. No woven pattern, chrome gradient or aqua button on `/`, `/ml` or Observatory.
- [ ] Text is flat colour everywhere; gradients only on surfaces/atmosphere.
- [ ] Mark renders crisply at 16px (favicon) and 28px (header).

**Landing `/` (Threshold)**
- [ ] First screen at 1440×900 **and** 390×844 shows: three-column family header, WORKING PROPOSAL chip and full banner sentence, "The Siliconcordat" straddling the seam, mission sentence, both action links, C/Si labels. Seam is vertical at 390.
- [ ] `tools/contrast.mjs` passes for banner, title and lede at 390, 768, 1024, 1440 and 1920 widths.
- [ ] The split appears only in the hero; chapters use the hairline + seam stub only.
- [ ] Chapter 01 has the full name paragraph and the substrate/legal caveat in body type; six principles in README order with full text; ecosystem paragraph + directions caveat above the cards; five direction cards link per §10.4; Robotics dashed and unlinked; Weft doorway sliver widens on hover **and** focus; footer family links + humility block.

**Easter egg (§6A)**
- [ ] At rest: no visible button chrome or text; reads as a node of the seam.
- [ ] Hover brightens seam segment and jewel. Keyboard focus shows the fire ring and the "OBSERVATORY" label; accessible name "Observatory".
- [ ] Reachable by Tab right after "Principles ↓"; hit area ≥ 44 × 88px.
- [ ] No animation at any motion setting; reduced motion removes the transition.
- [ ] href = production `https://observatory.askaconsult.com/` / staging `/observatory/`. No other link to Observatory anywhere.

**`/ml` and `/ml/*`**
- [ ] Family header with Moissanite Labs current (underline + diamond); local nav About · Directions · Principles.
- [ ] Hero is the chamber (crystal, two drifting caustic layers, seam, floor, fig caption) filling the first screen under the two sticky bars; h1 "Moissanite Labs"; mission lede; About/Directions/Principles jumps + "The Siliconcordat →". No framed specimen.
- [ ] About uses only README paragraphs; Directions index D-01…05, P-01 Weft, A-01 Robotics; Principles index.
- [ ] `/ml/principles/` follows §9.

**Observatory**
- [ ] Plates 00–04 + footer present with the same README text as `/` (banner, mission, name paragraphs, caveat, six principles, ecosystem paragraph, directions caveat, five directions, Weft, Robotics).
- [ ] Header: Siliconcordat / Moissanite Labs / Weft + location label + "← Main landing"; absolute links in production. No askaconsult branding.
- [ ] Mobile: instrument plate below the title; grid and spectrum readable; no horizontal scroll.

**Weft**
- [ ] `/weft` looks identical to w3ft.org except the split brand block (§5.3) and the mobile menu family group. Observatory is not in Weft's nav.
- [ ] No champagne, Source Serif or Plex on `/weft`.

**Links**
- [ ] No link anywhere to compass, credos, weft (except on /ml and /ml/notes-from-the-colony/ per §16.2), weft-eido, weft-corpus, or the three manifesto files. No "View on GitHub" on `/`, `/ml` or Observatory.
- [ ] External links same tab, ↗, hidden "(external site)".

**A11y / perf**
- [ ] Skip link works on every page (including Observatory). Every interactive element shows a 2px focus ring.
- [ ] axe/Lighthouse a11y: no contrast failures; menu operable by keyboard; Escape closes it.
- [ ] Reduced motion: no caustic drift on `/ml`, no reveal transitions, no doorway or egg transition, no smooth scroll.
- [ ] Mobile Lighthouse performance ≥ 80 on `/`, `/ml`, `/ml/principles/`, Observatory (target 90+).
- [ ] Fonts served from `assets/fonts/`; no request to any font CDN.

**Staging**
- [ ] `staging.siliconcordat.com` serves the arrangement with `noindex`; Observatory reachable via the seam at `/observatory/` (or the production host if it exists).

---

## 15A. Staging preview — `staging.siliconcordat.com`
The owner previews this arrangement on staging before anything ships to the apex.
- `staging.siliconcordat.com/` = Threshold landing, `/ml` = chamber-hero lab, `/ml/principles/`, `/weft` = Weft (unchanged, or a link out to the current Weft host if Weft isn't mirrored on staging).
- **Observatory on staging:** `observatory.askaconsult.com` may not exist yet. For a same-host preview, serve Observatory at `staging.siliconcordat.com/observatory/` and point the hidden seam control there. When Observatory is served from staging, its family links point at staging (`/`, `/ml`, `/weft`) rather than the production apex. Make both the egg href and Observatory's family-link origin build variables so ship is a config change, not an edit.
- Staging should send `X-Robots-Tag: noindex` (or `<meta name="robots" content="noindex">`) so the preview isn't indexed. Remove on ship.
- Deploys are smith's after nizam's review. Lumen does not deploy.

---

## 16. Amendment 2026-11-10 — Note 01 and research links

The Arrangement gains its first public note and its research links. Signed-off as a superseding change to the 2026-11-10 arrangement (see the superseding pull request).

### 16.1 Note 01 (`/ml/notes-from-the-colony/`)
- A deeper-page essay, `prototypes/ml-notes-from-the-colony.html`, same template as `/ml/principles/` (doc-head, chip, toc, doc-sections, footer-family). Eyebrow: `Moissanite Labs · Note 01`; h1: "Notes from the colony". Body: the Weft thesis, the razi-cells record including misses (scoring fault, heredity bought thrift not reach), and the lab's honesty rules. Closing section "Where to read it" lists Paper 0/1/2, `/weft`, the research hub, the Weft repository and `/ml`.
- Tone per §3.6 and §10.3: quiet, humble, no capability claims; "Weft is an open research program, not a product"; misses reported beside wins.
- `/ml` gains a `Notes` localnav entry; `/ml/principles/` and the note page carry the same localnav with `aria-current` on Notes for the note page.
- Prototype href → production: `ml-notes-from-the-colony.html` → `/ml/notes-from-the-colony/` (added to the bundle `CUT_HREF_MAP`; the mirror build and the verifier check the page exists and the h1 renders).

### 16.2 Research entries on `/ml` (index table additions)
New `<p class="meta subhead">Research</p>` block after the "Public research program" table, two rows:
- `R-01` Razi cells — "Colonies of small agent harnesses, kept or dropped by a measured score. Guesses registered before the data; misses kept in the record." Tag: `Experimental research`. Link: `https://github.com/Moissanite-Labs/weft` (public; visible label `github.com/Moissanite-Labs/weft ↗`).
- `R-02` The research hub — "The report, the map of open directions, and the laws record, in one place on the lab site." Tag: `Research`. Link: `https://moissanite-labs.github.io/.github/research/`. R-02 404s until the lab-site research pull request merges; if the cut ships before that, drop R-02 or point it at `https://moissanite-labs.github.io/.github/` (reviewer's call).
- The cut verifier bans `github.com/Moissanite-Labs/weft` on Cut pages except the two pages above (allowlist `ml/index.html`, `ml/notes-from-the-colony/index.html`); every other Cut page still fails the check. The Weft repository went public, so the ban now exists only for the pages that do not need it.
- The `/ml` index meta line becomes "5 directions · 1 program · 2 research entries · 1 aspiration".

### 16.3 Research link on `/weft`
One additive link, `Research` → `https://moissanite-labs.github.io/.github/research/`, added to the primary nav and the menu panel, styled exactly like the neighbouring `Papers` link. No other Weft element changes. The link 404s until the lab-site research pull request merges (same note as §16.2).

### 16.4 Weft pin
The bundle mirrors `site/` from the pinned Weft commit in `siliconcordat/sources-manifest.json` (`weft.sha`). This amendment carries the `site/` change, so the pin is advanced in the companion commit to this branch's head (see the superseding pull request).

## 15. Files

Prototypes (open via `python3 -m http.server 8765` from the package root, then `/prototypes/landing.html`):
- `prototypes/landing.html` — `/` (Threshold landing)
- `prototypes/ml.html` — `/ml` (chamber hero + lab index)
- `prototypes/ml-principles.html` — `/ml/principles/` (deeper-page template; unchanged)
- `prototypes/ml-notes-from-the-colony.html` — `/ml/notes-from-the-colony/` (Note 01; see §9A and §16)
- `prototypes/ml-the-alignment-question.html` — `/ml/the-alignment-question/` (Note 02; see §17)
- `prototypes/observatory.html` — Observatory easter egg (`observatory.askaconsult.com`; staging `/observatory/`)
- `prototypes/family-weft.html` — wayfinding annotation for `/weft`
- `prototypes/site.css` — reference CSS for `/`, `/ml`, `/ml/*`; `prototypes/observatory.css` — Observatory; `tokens.css` — tokens + fonts
- `prototypes/alts/threshold.html`, `prototypes/alts/observatory.html` — **historical** 2026-11-08 hero frames, superseded
- `tools/build_prototypes.py` — generates the pages from the README constants at its top (six now: landing, ml, ml-principles, ml-notes-from-the-colony, ml-the-alignment-question, observatory)

Prototype hrefs → production: `landing.html` → `/`, `ml.html` → `/ml`, `ml-principles.html` → `/ml/principles/`, `ml-notes-from-the-colony.html` → `/ml/notes-from-the-colony/`, `ml-the-alignment-question.html` → `/ml/the-alignment-question/`, `family-weft.html` → `/weft`, `observatory.html` → `https://observatory.askaconsult.com/` (staging `/observatory/`). From Observatory, family links become absolute (§10.4).

Screenshots (`shots/`, headless Chromium via Playwright at DPR 1; `node tools/shoot.mjs`):
- `/`: `landing-hero-1440.png`, `landing-principles-1440.png`, `landing-ecosystem-1440.png`, `landing-doorways-1440.png`, `landing-full-1440.png`, `landing-hero-390.png`, `landing-390.png`
- Easter egg: `state-seam-hover-1440.png`, `state-seam-focus-1440.png`, `state-seam-focus-390.png`
- `/ml`: `ml-top-1440.png`, `ml-1440.png`, `ml-390.png`, `ml-top-390.png`
- `/ml/principles/`: `ml-principles-top-1440.png`, `ml-principles-1440.png`, `ml-principles-390.png`
- Observatory: `observatory-hero-1440.png`, `observatory-1440.png`, `observatory-390.png`, `observatory-hero-390.png`
- Weft annotation: `family-weft-1440.png`; states: `state-weft-door-hover-1440.png`
- Historical (not regenerated): `alt-observatory-1440.png`, `alt-threshold-1440.png`, `state-direction-card-hover-1440.png`, `state-ml-weft-row-hover-1440.png`; the full 2026-11-08 set is in `shots/prev-2026-11-08/`.

## 17. Amendment 2026-11-11 — Note 02 and the Notes index on /ml

The Arrangement gains its second public note.

### 17.1 Note 02 (`/ml/the-alignment-question/`)
- A deeper-page essay, `prototypes/ml-the-alignment-question.html`, same template as Note 01 (doc-head, chip, toc, doc-sections, footer-family). Eyebrow: `Moissanite Labs · Note 02`; h1: "The Alignment Question". Written by Ahraz Arifuddin, from outside the lab; the caption in the article footer names the author.
- Body: the shared intellect claim applied to AI safety and alignment. The closed loop and model collapse; whose average wins (pluralistic alignment); entropy as a safety requirement (the filter problem); provenance over obedience and end-to-end verification; governance as the actual alignment problem (Guardian Angel framing); symbiosis of biological and digital intelligences; honest unknowns. No capability claims; plain prose; no em dashes.
- Links only to live targets: nature.com (model collapse), grokipedia (model collapse overview, pluralistic alignment), gwern.net, bend-lang.org, github.com/Moissanite-Labs/exorien.
- Prototype href → production: `ml-the-alignment-question.html` → `/ml/the-alignment-question/` (added to the bundle `CUT_HREF_MAP`, to the mirror copy list, and to the verifier's required files).
- The doc-head `Working proposal` chip matches Note 01. Localnav unchanged: `Notes` → Note 01.

### 17.2 Notes table on `/ml`
A new `<p class="meta subhead">Notes</p>` block sits between the "Research" table and "Aspiration", two rows:
- `N-01` Notes from the colony → `/ml/notes-from-the-colony/`. Tag: `Note 01 · process note`.
- `N-02` The Alignment Question → `/ml/the-alignment-question/`. Tag: `Note 02 · essay`.
- The `/ml` index meta line becomes "5 directions · 1 program · 2 research entries · 2 notes · 1 aspiration".
