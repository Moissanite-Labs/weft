# Notes for lumen — Siliconcordat design package

Prepared 2026-11-08, about 9:00–10:00 PM CT.

## How to open
```
cd /workspace/siliconcordat-design && python3 -m http.server 8765
# then http://localhost:8765/prototypes/landing.html (also ml.html, ml-principles.html, family-weft.html, alts/*.html)
```
`file://` also works for every page. Prototype "Weft" links open `family-weft.html` on purpose so you can click through; in production they are `/weft` (SPEC §15).

Rebuild and reshoot: `python3 tools/build_prototypes.py && node tools/shoot.mjs`. `node_modules` is a symlink to `/tmp/shot/node_modules` (Playwright 1.65, using the cached Chromium 1248 binary).

## Judgment calls
1. **Copy source.** I set the README text from your brief, which quotes the current compass README. I also found an older local clone (`/workspace/clones/Moissanite-Labs_constitution/README.md`, commit d3a5a61, 2026-10-29) and used it only to confirm the full wording of paragraphs 1 and 2, which match your brief word for word. That older clone does **not** name Synbios or Koinos in its ecosystem section and has a slightly different caveat ("The names of the forge and collaboration protocol, the protocol's repository boundary, …"). The prototypes follow your brief: "Their implementation, interfaces, and other design and governance decisions remain open." and short per-direction descriptions ("A separate agent-first forge.", "A collaboration protocol."). **Smith should re-diff the strings at the top of `tools/build_prototypes.py` against the current compass README before ship.** I did not read FOUNDER-VISION.md, SILICONCORDAT.md or NAMING.md.
2. **Banner wording.** The repo clause is rewritten as you specified ("their publication here does not by itself establish adopted policy"). The banner shows in full in the landing hero, not only as a chip.
3. **Structural labels.** A few neutral labels aren't in the README (chapter names, "Enter the lab", "Open research program", the Weft description "Papers, runtime, and demos. Weft keeps its own site and design.", figure captions). They're all listed in SPEC §10.3 for herald. None claims a capability.
4. **Links (scout update via nizam).** All five direction cards are now real links per that update: Exo → exo.askaconsult.com; Exofab → Pages; Synbios → Pages plus a secondary GitHub link; Koinos → github.com/Moissanite-Labs/synmerit (titled "Koinos", with a quiet "currently lives at synmerit" aside); Ethos → GitHub. Robotics has no link. Weft always goes to /weft. The not-linked card state is still specified (SPEC §8.5) for future directions.
5. **Mark.** My first draft was an isometric cube, but at 16px it read like a generic "package" icon. The final mark is two overlapping hexagons (carbon and silicon), and the hexagonal overlap is filled with fire. It holds at 16px.
6. **Crystal.** It's rendered from a small 3D script (`tools/make_chamber.py`): flat-terminated plates and bars read like hardware, so I used translucent terminated hexagonal prisms with the cool key on one side and the warm fill on the other. It's captioned as an illustration.
7. **Caustics.** These are angular (Voronoi facets) rather than watery. Watery caustics would drift toward Weft's liquid feel.
8. **/ml uses an index table, not cards.** This makes the lab denser and more like an instrument than the landing.
9. **Constellation diagram.** It draws only what the README says: Exo is the foundation, four directions sit on it, and robotics is off the line. It implies no links between the directions. It's hidden at 600px and below because the cards carry the same content.
10. **Weft integration.** Recommended: split Weft's brand block into "ML Weft" / "Moissanite Labs" / "Siliconcordat", all in Weft's own `.brand-org` style. On mobile, a family group goes in Weft's existing menu. A 32px rail is documented as the fallback only.
11. **Alternatives B and C** are hero frames only, each with an on-page "not recommended" tag.

## Checks run
- WCAG contrast computed for every text token on `--bg`, `--bg-2`, `--surface` and `--surface-2`. The lowest is `--muted` on `--surface-2` at 4.66:1. Everything passes AA.
- Lighthouse 12 mobile on the prototypes (local `http.server`, no compression or caching), as perf / a11y / best practices: landing 93 / 100 / 100, ml 97 / 100 / 100, ml-principles 97 / 100 / 100. CLS was 0 on all three. Landing LCP is 3.2 s; the LCP element is the hero crystal SVG, which is now preloaded.
- Screenshots: headless Chromium, DPR 1, at 1440×900 and 390×844, plus full-page captures. Reveal transitions are forced to their end state and caustic animation is paused for capture.

## Fonts (all SIL Open Font License 1.1; licence texts in `assets/fonts/`)
Source: the npm packages `@fontsource-variable/source-serif-4` 5.3.1, `@fontsource/ibm-plex-sans` 5.3.0 and `@fontsource/ibm-plex-mono` 5.3.0, Latin subsets only.
- `source-serif-4-opsz.woff2`: Source Serif 4, variable wght 200–900 plus the opsz axis (Adobe; OFL)
- `ibm-plex-sans-400/500/600.woff2`: IBM Plex Sans (IBM; OFL)
- `ibm-plex-mono-400/500.woff2`: IBM Plex Mono (IBM; OFL)
No runtime CDN.

## Confirmation
- No GitHub writes of any kind: no repos, PRs, issues, Pages or visibility changes. No deploys, DNS changes or public posts.
- I contacted no one (not nizam, smith, scout, herald or the user). Reading w3ft.org assets was limited to the copies already saved in `refs/`. The facsimile weave-mark in `family-weft.html` is a simplified redraw for annotation and is not hotlinked.
- Nothing is folded into askaconsult.com. The only askaconsult string is the Exo card's link to Exo's existing site, as the scout update instructed.
