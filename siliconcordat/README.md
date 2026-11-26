# ml-siliconcordat (not deployed)

Separate Cloudflare Worker config for a future **siliconcordat.com** bundle: Moissanite Labs pages at `/` and `/ml`, and a path-rewritten Weft mirror at `/weft`. The live w3ft.org Worker **`ml-weft`** (`wrangler.jsonc`) is unchanged.

Pinned sources live in [`sources-manifest.json`](sources-manifest.json):

| Input | Pin |
|-------|-----|
| Weft `site/` | `weft.site_tree`, the git tree hash of `site/` on this repo |
| Public lab `docs/` | `lab_site.sha` on [Moissanite-Labs/.github](https://github.com/Moissanite-Labs/.github) |

The Weft pin is a tree hash, not a commit SHA, so a squash merge that keeps the same `site/` tree still satisfies the check. The build copies `site/` into `dist/weft` only after `HEAD:site` equals the pin.

## Rebuild `dist/`

From any commit whose **`site/` tree** equals `weft.site_tree` (the build compares `HEAD:site` to the pin and fails if they differ):

```bash
python3 scripts/build_siliconcordat_bundle.py
python3 scripts/verify_siliconcordat_bundle.py
node --test workers/test_siliconcordat.mjs
```

The build script clones `.github` at the lab pin into `.cache/` (gitignored), copies `docs/` into `dist/` root paths, and writes a rewritten copy of `site/` under `dist/weft/`. Nothing under `dist/` is committed.

Local preview (optional, does not publish):

```bash
npx wrangler@4 dev -c wrangler.siliconcordat.jsonc
```

Do not run `wrangler deploy` for this worker until the owner attaches hostnames. No DNS or custom-domain routes are configured in `wrangler.siliconcordat.jsonc`.
