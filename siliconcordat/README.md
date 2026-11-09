# ml-siliconcordat (not deployed)

Separate Cloudflare Worker config for a future **siliconcordat.com** bundle: Moissanite Labs pages at `/` and `/ml`, and a path-rewritten Weft mirror at `/weft`. The live w3ft.org Worker **`ml-weft`** (`wrangler.jsonc`) is unchanged.

Pinned sources live in [`sources-manifest.json`](sources-manifest.json):

| Input | Pin |
|-------|-----|
| Weft `site/` | `bff15957656a4c904250963e67d0a2c770cd5a26` on this repo |
| Public lab `docs/` | `a42df12a53ab3c86b31573012a16ee5a62ce1a26` on [Moissanite-Labs/.github](https://github.com/Moissanite-Labs/.github) |

## Rebuild `dist/`

From any commit whose **`site/` tree** matches the Weft pin (the build compares `HEAD:site` to `{pin}:site` and fails if they differ):

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
