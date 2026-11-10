# Notes — Siliconcordat design package, arrangement 2026-11-10

Prepared Tuesday 2026-11-10, about 2:00–3:00 AM CT. Supersedes the 2026-11-08 notes (kept at `refs/prev-2026-11-08/NOTES.md`).
Status: design package for a staging preview at `staging.siliconcordat.com`, then nizam → smith → ship. Lumen does not deploy. Nothing here has been deployed, pushed or sent.

## How to open
```
cd /workspace/siliconcordat-design && python3 -m http.server 8765
# http://localhost:8765/prototypes/landing.html      → /   (Threshold)
# http://localhost:8765/prototypes/ml.html           → /ml (chamber hero)
# http://localhost:8765/prototypes/ml-principles.html → /ml/principles/
# http://localhost:8765/prototypes/observatory.html  → observatory.askaconsult.com (easter egg)
# http://localhost:8765/prototypes/family-weft.html  → /weft wayfinding annotation
```
`file://` works too. To find the easter egg: on the landing, the small bright diamond on the seam between "Principles ↓" and "Moissanite Labs →". Hover it, or Tab to it (it's the stop after "Principles ↓").

Rebuild, reshoot, re-check contrast:
```
python3 tools/build_prototypes.py
node tools/shoot.mjs
node tools/contrast.mjs landing.html 1440 900 ".th-proposal p,.th-title,.th-lede"   # also 390 844, 1024 768, 1920 1080
```
`node_modules` is a symlink to `/tmp/shot/node_modules` (Playwright, cached Chromium 1248).

## What changed from 2026-11-08
- `/` is now **Threshold**: full landing. The split-seam hero sits on top, and below it are the same four chapters as before (name, principles, ecosystem, doorways) plus the footer. The split stays in the hero; chapters get only a 1px carbon→fire→silicon hairline and a short seam stub at centre top.
- The header on `/` has three columns: Moissanite Labs (left, carbon side), Siliconcordat (centre, on the seam), Weft (right, silicon side). It needs no hamburger at 390px. Under 480px the Siliconcordat word is visually hidden, so the mark alone sits on the seam.
- **Easter egg.** A 44 × 88px link on the seam that goes to Observatory (SPEC §6A).
- `/ml` gets the **chamber hero** from the old apex (crystal, caustics, seam at 61%, floor, fig caption). The visual is unchanged. The heading is "Moissanite Labs", and the CTAs are in-page jumps plus "The Siliconcordat →". The framed specimen is gone.
- **Observatory** is a full landing: Plates 00–04 plus the footer. It uses its own cool palette (`prototypes/observatory.css`).
- `family-weft.html` gets one added paragraph about the new arrangement. Weft's look is untouched.
- SPEC.md is rewritten as the new contract. New sections: §2 arrangement, §3.7 Threshold surfaces, §3.8 Observatory palette, §5.4 Observatory header, §6 Threshold, §6A easter egg, §7 /ml transplant, §7A Observatory, §15A staging. The checklist and file list are updated.
- The old alt frames in `prototypes/alts/` are relabelled "Historical frame · superseded". Their original shots are untouched. The full 2026-11-08 prototypes and shots are in `refs/prev-2026-11-08/` and `shots/prev-2026-11-08/`. The live HTML/CSS as of today is in `refs/live/`. It matched `prototypes/landing.html` and `ml.html` apart from absolute asset paths.

## Judgment calls
1. **Lab heading instead of moving "The Siliconcordat" onto /ml.** The owner said to move the current hero to the inner page. I moved the hero's *visual* (chamber, type, caption) and set the lab's own words on it: eyebrow "The lab", h1 "Moissanite Labs", and the mission lede. "The Siliconcordat" is now the apex title, and two pages with the same h1 would blur which room you're in. If the owner wants the literal title on /ml too, it's a one-line change in `ml()` in `tools/build_prototypes.py`.
2. **The seam is the hidden spot.** It's the one vertical element on the hero, so a node on it looks native. It sits in the actions row because that's the only place on the seam with no text above or beside it. At rest it reads like a separator between the two links. A 1×1px or zero-opacity trap would fail WCAG 2.5.8 and 2.4.7, so it's a real 44 × 88 link with a matching accessible name. The "OBSERVATORY" label appears only on keyboard focus, offset off the seam so it never sits on the bright line. Hover shows no label; the brightening plus the pointer cursor is the discovery moment.
3. **Threshold contrast, done by measurement.** The original frame used flat dark boxes behind the banner and lede. They worked, but they killed the split. The replacement has three soft layers: a centred elliptical scrim at about 52–62% black, a wider radial scrim behind the banner, and a 2px/14px glyph halo. `tools/contrast.mjs` checks the brightest pixel within 2px of any glyph, which is a worst-case check, not an average. Everything passes AA at 390, 768, 1024, 1440 and 1920 widths (SPEC §12 table). The tightest case is the lede at 1920×1080: 4.60:1, against 3:1 required for 26px large text. I also dimmed the top of the seam (18–34% height) so the banner doesn't need a heavy box.
4. **No scroll cue on `/`.** A second vertical mark on the hero would compete with the seam and the egg. "Principles ↓" does that job.
5. **Observatory staging path.** `observatory.askaconsult.com` probably isn't up yet. SPEC §15A says to serve it at `staging.siliconcordat.com/observatory/` for the preview and point the seam there. The egg href and Observatory's family-link origin should be build variables, so moving to production is a config change. I also recommend `noindex` on staging.
6. **Observatory content.** It's the same README text in the same order with the same caveats, set as numbered plates. The only new labels are structural: plate numbers, "Fig. B1/B2", "Note", "Main landing", "Observatory · plate 00/05". They're listed in SPEC §10.3 for herald. I dropped the alt frame's design-note caption ("Instrument captions replace film atmosphere…") because it was commentary, not page copy. Each direction row has a small spectral bar with one emission line. It's decorative and `aria-hidden`, and it implies no measurement.
7. **Observatory header.** Location is shown as a non-link label, "◇ Observatory · plate 00", because Observatory isn't a family nav item. There's also a quiet "← Main landing" link. No askaconsult name appears anywhere on the page.
8. **/ml caption contrast.** The old apex fig caption measured 4.43:1 over crystal facets at 1440, just under AA. On /ml I gave it `--ink-2` and a soft void halo, which brings it to 9.3:1 or better. The live apex has this issue today, and it goes away when the chamber leaves `/`.
9. **Mobile /ml.** The text starts 220px down so the crystal sits above it, not behind the lede. That avoids the cramped, thumbnail-in-a-frame feel the owner disliked.
10. **Keep the live footer source link.** The 2026-11-10 package dropped the already-live footer link to `https://github.com/Moissanite-Labs/siliconcordat` (present on `/` and `/ml` when this package was built). SPEC §10.4 and the footer contract now list it, and the prototypes have it back in the footer base row (and on Observatory). It is the public site repo, not a manifesto-file or Weft-repo link, and it is not a header "View on GitHub" button.

## Checks run (2026-11-10)
- Contrast: `tools/contrast.mjs`, glyph-adjacent worst case, on all hero text for `/`, `/ml` and Observatory, at 1440 and 390 (plus 768, 1024 and 1920 for `/`). Everything passes (SPEC §12). The easter-egg focus label measures 12.06:1.
- Lighthouse 12, mobile preset, local `http.server` with no compression. Scores are perf / a11y / best practices:
  - `/`: **96 / 100 / 100**, LCP 2.6 s
  - `/ml`: **94 / 100 / 100**, LCP 3.0 s (chamber SVG preloaded)
  - `/ml/principles/`: **97 / 100 / 100**, LCP 2.4 s
  - Observatory: **100 / 100 / 100**, LCP 1.7 s
  - CLS was 0 on all four pages.
- Screenshots: DPR 1, 1440×900 and 390×844, viewport and full page, with reveal forced on and animation paused. For the focus shots the harness really Tabs to the control, so `:focus-visible` applies. I looked at every new shot myself. At 390 there's no horizontal overflow, the title doesn't clip, and the seam stays vertical.

## Leftover risks
- **Seam contrast margins are thin in places** (lede at 1920: 4.60 vs 3.0; title ≥ 5.15). They pass, but any brightening of the seam, halves or glow needs a re-run of `contrast.mjs`. Very wide or short viewports (for example 2560×1080) weren't measured.
- **Easter-egg discoverability is by design low.** Some visitors will take the jewel for a separator. That's the intent, but nobody should rely on it as navigation.
- **Hosting.** Observatory on askaconsult is an owner exception. If the subdomain isn't provisioned, use the staging path. Cross-host links mean Observatory → `/weft` is absolute.
- **Copy re-diff.** As before, smith should re-diff the README constants at the top of `tools/build_prototypes.py` against the current compass README before ship.

## Confirmation
No GitHub writes, no deploys, no DNS, no messages to anyone. All work was in `/workspace/siliconcordat-design/` and `/tmp`, for the local server, shots and Lighthouse JSON.

## 2026-11-10 (later) — Note 01 and research links (superseding change)
Prepared to supersede the arranged Arrangement pull request (see the superseding PR). The arrangement itself is unchanged except: `/ml` gains two research rows (R-01 razi-cells record at the public Weft repository; R-02 the lab research hub, which 404s until the lab-site research PR merges — reviewer's call), the localnav on `/ml`, `/ml/principles/` and the new page gains `Notes`, and a new deeper page Note 01, "Notes from the colony" (`/ml/notes-from-the-colony/`), the lab's first public note. Weft gains one additive `Research` nav link to the same hub. The Weft pin in `siliconcordat/sources-manifest.json` is advanced to this branch's head in a companion commit, so the `/weft` mirror carries the new link. No other Weft element changes; no capability claims are added anywhere; misses stay in the record.

## Amendment 2026-11-11 — Note 02
- `/ml/the-alignment-question/` (Note 02, "The Alignment Question") added: deeper-page template as Note 01, written by Ahraz Arifuddin. The shared intellect claim applied to AI safety and alignment: the closed loop, whose average wins, entropy as a safety requirement, provenance over obedience, governance, symbiosis, honest unknowns.
- `/ml` gains a Notes table between Research and Aspiration (N-01, N-02). The index meta line is now "5 directions · 1 program · 2 research entries · 2 notes · 1 aspiration". Localnav unchanged.
- Bundle `CUT_HREF_MAP` and the mirror copy list gain `ml-the-alignment-question.html` → `/ml/the-alignment-question/`; the verifier requires the page. SPEC §17 (new); §15 (files, tools line) updated.
- Checks (2026-11-11): `SILICONCORDAT_CUT_HOST=staging` and `production` builds + verifier passed; `node --test workers/test_siliconcordat-cut.mjs` 11/11; Note 02 and `/ml` spot-checked in headless Chromium (1440 and 390).
