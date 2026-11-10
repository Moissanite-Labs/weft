# Siliconcordat Cut (Arrangement 2026-11-10)

Threshold landing at `/`, chamber-hero lab at `/ml`, Observatory at `/observatory/` (staging) or `observatory.askaconsult.com` (production egg), Weft mirrored at `/weft` for Worker `ml-siliconcordat-cut`.

- **Source pages:** `prototypes/` (`landing.html`, `ml.html`, `ml-principles.html`, `ml-notes-from-the-colony.html`, `observatory.html`, `site.css`, `observatory.css`), `tokens.css`, `assets/`
- **Contract:** `SPEC.md` (wins over prototypes when they disagree)
- **Host profiles:** `host-settings.json`; set `SILICONCORDAT_CUT_HOST=staging` for `staging.siliconcordat.com` preview (egg → `/observatory/`, noindex). Default `production` for apex ship paths.
- **Weft mirror:** built at CI time from pinned `site/` in `sources-manifest.json` into `dist-cut/weft/` (not committed)

Build: `python3 scripts/build_siliconcordat_cut_bundle.py`  
Verify: `python3 scripts/verify_siliconcordat_cut_bundle.py`
