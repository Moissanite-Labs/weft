#!/usr/bin/env python3
"""Build dist-cut/ for Worker ml-siliconcordat-cut (Arrangement 2026-11-10)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "siliconcordat-cut"
MANIFEST_PATH = CUT / "sources-manifest.json"
DIST = ROOT / "dist-cut"
SITE = ROOT / "site"

REWRITE_SUFFIXES = {".html", ".css", ".js", ".json", ".svg"}
TEXT_HEADERS_NAME = "_headers"
ASSETSIGNORE_NAME = ".assetsignore"

RETIRED_REL_PATHS = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)
RETIRED_DIR_PREFIXES = ("data/", "assets/shaders/", "assets/workers/")

SC_ORG = "https://siliconcordat.org"
SC_ORG_WEEFT = f"{SC_ORG}/weft"
W3FT = "https://w3ft.org"

HOST_SETTINGS_PATH = CUT / "host-settings.json"
DEFAULT_HOST = os.environ.get("SILICONCORDAT_CUT_HOST", "production").strip().lower()

CUT_HREF_MAP = {
    "landing.html": "/",
    "ml.html": "/ml",
    "ml-principles.html": "/ml/principles/",
    "family-weft.html": "/weft",
    "ml-notes-from-the-colony.html": "/ml/notes-from-the-colony/",
    "ml-the-alignment-question.html": "/ml/the-alignment-question/",
    "observatory.html": "/observatory/",
}

NOINDEX_META = '<meta name="robots" content="noindex">'

STAGING_NOINDEX_BLOCK = "/*\n  X-Robots-Tag: noindex\n"

STATIC_ASSET_URL = re.compile(
    r"\.(?:css|js|mjs|json|svg|webp|png|jpe?g|gif|ico|woff2?|ttf|otf|webmanifest)(?:\?.*)?$",
    re.IGNORECASE,
)

_HTML_LOCAL_ASSET = re.compile(
    r'(?P<attr>\b(?:href|src)=)(?P<q>["\'])'
    r'(?P<url>(?!https?:)(?!mailto:)(?!data:)(?!//)(?!#)[^"\']+)(?P=q)'
)

_JS_MODULE_SPEC = re.compile(
    r'(?P<prefix>\b(?:import|export)\s+(?:[^"\';]*?\s+from\s+|))'
    r'(?P<q>["\'])'
    r'(?P<url>(?:\.{1,2}/|/)[^"\']+)(?P=q)'
)

_JS_IMPORT_SIDE = re.compile(
    r'\bimport\s+(?P<q>["\'])(?P<url>(?:\.{1,2}/|/)[^"\']+)(?P=q)\s*;'
)

_JS_DYNAMIC_IMPORT = re.compile(
    r'\bimport\s*\(\s*(?P<q>["\'])(?P<url>(?:\.{1,2}/|/)[^"\']+)(?P=q)\s*\)'
)

_CSS_URL = re.compile(
    r"url\(\s*(?P<q>['\"]?)"
    r"(?P<url>(?!https?:)(?!data:)(?!//)(?:\.{1,2}/|/)[^'\")\s]+)"
    r"(?P=q)?\s*\)",
    re.IGNORECASE,
)


def load_host_settings(profile: str) -> dict:
    with HOST_SETTINGS_PATH.open(encoding="utf-8") as fh:
        table = json.load(fh)
    if profile not in table:
        print(
            f"unknown SILICONCORDAT_CUT_HOST={profile!r}; "
            f"expected one of {sorted(table)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return table[profile]

WAYFINDING_CSS = """
/* §5.3 wayfinding (build-time only; Weft tokens) */
.brand { margin-right: 0; }
.brand-family {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-right: auto;
}
a.brand-org { text-decoration: none; }
a.brand-org:hover {
  color: var(--link-hover);
  text-decoration: underline;
  text-underline-offset: 0.2em;
}
.menu-family-sep {
  height: 1px;
  background: var(--line);
  margin: 6px 4px;
}
.menu-family-label {
  padding: 6px 12px 2px;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.menu-family-link { color: var(--ink-2); }
@media (max-width: 860px) {
  .brand-family { display: none; }
}
"""

BRAND_OLD = re.compile(
    r'<a class="brand" href="[^"]*" aria-label="ML Weft home">\s*'
    r"<svg viewBox=\"0 0 32 32\" aria-hidden=\"true\"><use href=\"#weave-mark\"/></svg>\s*"
    r'<span class="brand-name">ML Weft</span>\s*'
    r'<span class="brand-org">Moissanite Labs</span>\s*'
    r"</a>",
    re.MULTILINE,
)

BRAND_NEW = """<a class="brand" href="/weft/" aria-label="ML Weft home">
        <svg viewBox="0 0 32 32" aria-hidden="true"><use href="#weave-mark"/></svg>
        <span class="brand-name">ML Weft</span>
      </a>
      <span class="brand-family">
        <a class="brand-org" href="/ml">Moissanite Labs</a>
        <a class="brand-org" href="/">Siliconcordat</a>
      </span>"""

MENU_FAMILY_BLOCK = """
          <div class="menu-family-sep" role="presentation"></div>
          <span class="menu-family-label">Moissanite Labs family</span>
          <a class="menu-family-link" href="/ml">Moissanite Labs</a>
          <a class="menu-family-link" href="/">Siliconcordat</a>"""


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def ensure_commit(sha: str) -> bool:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
    )
    if probe.returncode == 0:
        return True
    fetch = subprocess.run(
        ["git", "fetch", "origin", sha],
        cwd=ROOT,
        capture_output=True,
    )
    return fetch.returncode == 0


def site_tree_at(rev: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{rev}:site"],
        cwd=ROOT,
        text=True,
    ).strip()


ALLOW_UNREACHABLE_PIN_ENV = "SILICONCORDAT_ALLOW_UNREACHABLE_PIN"


def unreachable_pin(pinned: str, what: str) -> None:
    """Fail when the pinned weft commit cannot be fetched (see the same
    function in build_siliconcordat_bundle.py). The /weft mirror must come
    from the pinned tree; silently using HEAD made the pin a no-op."""
    if os.environ.get(ALLOW_UNREACHABLE_PIN_ENV) == "1":
        print(
            f"warning: pinned commit {pinned[:12]} unreachable; {what} "
            f"because {ALLOW_UNREACHABLE_PIN_ENV}=1. Do not deploy this build.",
            file=sys.stderr,
        )
        return
    print(
        f"error: pinned commit {pinned} is unreachable. Pin a commit on main "
        f"(siliconcordat-cut/sources-manifest.json weft.sha), or set "
        f"{ALLOW_UNREACHABLE_PIN_ENV}=1 for an offline local build.",
        file=sys.stderr,
    )
    sys.exit(1)


def log_weft_pin(manifest: dict) -> None:
    pinned = manifest["weft"]["sha"]
    if not ensure_commit(pinned):
        unreachable_pin(pinned, "using HEAD for the /weft pin check")
        return
    head_site = site_tree_at("HEAD")
    pin_site = site_tree_at(pinned)
    if head_site != pin_site:
        print(
            f"note: site/ at HEAD ({head_site[:12]}) differs from pin {pinned[:12]} "
            f"({pin_site[:12]}); using pinned tree for /weft",
            file=sys.stderr,
        )


def should_skip_site_file(rel: str) -> bool:
    rel_norm = rel.replace("\\", "/")
    if rel_norm == ASSETSIGNORE_NAME or rel_norm.endswith("/" + ASSETSIGNORE_NAME):
        return True
    if rel_norm.endswith(".jsx") or rel_norm.endswith("/VENDORED.json"):
        return True
    for retired in RETIRED_REL_PATHS:
        if rel_norm == retired or rel_norm.endswith("/" + retired):
            return True
    for prefix in RETIRED_DIR_PREFIXES:
        if rel_norm.startswith(prefix):
            return True
    if rel_norm.startswith("lab/field/"):
        return True
    return False


def rewrite_w3ft_urls(text: str) -> str:
    text = text.replace(f"{W3FT}/", f"{SC_ORG_WEEFT}/")
    text = text.replace(W3FT, SC_ORG_WEEFT)
    text = text.replace("https://siliconcordat.com/weft", SC_ORG_WEEFT)
    text = text.replace("https://siliconcordat.com/", SC_ORG + "/")
    return text


def rewrite_root_paths_in_text(text: str) -> str:
    text = rewrite_w3ft_urls(text)

    def qsub(m: re.Match[str]) -> str:
        q, path = m.group(1), m.group(2)
        if path.startswith("/weft"):
            return m.group(0)
        if path == "/":
            return f"{q}/weft/{q}"
        if path.startswith("/#"):
            return f"{q}/weft{path}{q}"
        if re.match(r"^/(assets|papers|widgets)(/|$)", path) or path in (
            "/favicon.svg",
            "/og.png",
            "/404.html",
        ):
            return f"{q}/weft{path}{q}"
        return m.group(0)

    text = re.sub(r'(?P<q>["\'])(/[^"\']*)(?P=q)', qsub, text)
    text = re.sub(
        r"url\(\s*/(?!weft/)(assets/)",
        r"url(/weft/\1",
        text,
    )
    return text


_PATH_LINE = re.compile(r"^(/\S*)$")


def rewrite_headers(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        m = _PATH_LINE.match(bare)
        if m and bare.startswith("/") and not bare.startswith("#"):
            if bare == "/*":
                path = "/weft/*"
            elif bare == "/":
                path = "/weft/"
            elif bare.startswith("/weft"):
                path = bare
            else:
                path = f"/weft{bare}"
            newline = "\n" if line.endswith("\n") else ""
            line = path + newline
        out.append(line)
    return "".join(out)


def apply_wayfinding_html(text: str) -> str:
    if "menu-panel" not in text or "ML Weft" not in text:
        return text
    text = BRAND_OLD.sub(BRAND_NEW, text, count=1)
    if MENU_FAMILY_BLOCK.strip() in text:
        return text
    text = re.sub(
        r"(<div class=\"menu-panel\">.*?)(</div>\s*</details>)",
        lambda m: m.group(1) + MENU_FAMILY_BLOCK + m.group(2),
        text,
        count=1,
        flags=re.DOTALL,
    )
    return text


def rewrite_weft_file(rel: Path, raw: bytes) -> bytes:
    if rel.name == TEXT_HEADERS_NAME:
        return rewrite_headers(raw.decode("utf-8")).encode("utf-8")
    if rel.suffix.lower() in REWRITE_SUFFIXES or rel.suffix == "":
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
        text = rewrite_root_paths_in_text(text)
        if rel.suffix.lower() == ".html":
            text = apply_wayfinding_html(text)
        if rel.as_posix() == "assets/css/site.css":
            text = append_wayfinding_css(text)
        return text.encode("utf-8")
    return raw


def append_wayfinding_css(css: str) -> str:
    if "menu-family-label" in css:
        return css
    return css.rstrip() + "\n" + WAYFINDING_CSS + "\n"


def export_pinned_site(pinned_sha: str) -> Path:
    """Materialize site/ at pinned commit into a temp directory."""
    tmp = Path(tempfile.mkdtemp(prefix="weft-site-pin-"))
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", f"{pinned_sha}:site"],
        cwd=ROOT,
    )
    subprocess.run(["tar", "-xf", "-", "-C", str(tmp)], input=archive, check=True)
    return tmp


def site_source_tree(manifest: dict) -> Path:
    pinned = manifest["weft"]["sha"]
    if not ensure_commit(pinned):
        unreachable_pin(pinned, "using the local site/ tree for /weft")
        return SITE
    head_site = site_tree_at("HEAD")
    pin_site = site_tree_at(pinned)
    if head_site == pin_site and SITE.is_dir():
        return SITE
    return export_pinned_site(pinned)


def copy_weft_tree(site_root: Path) -> None:
    weft_root = DIST / "weft"
    if weft_root.exists():
        shutil.rmtree(weft_root)
    weft_root.mkdir(parents=True)
    for src in sorted(site_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(site_root).as_posix()
        if should_skip_site_file(rel):
            continue
        dest = weft_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        rewritten = rewrite_weft_file(Path(rel), data)
        dest.write_bytes(rewritten)
        if rel == TEXT_HEADERS_NAME:
            (DIST / TEXT_HEADERS_NAME).write_bytes(rewritten)


def _apply_href_mapping(html: str, mapping: dict[str, str]) -> str:
    for proto, prod in mapping.items():
        html = html.replace(f'href="{proto}"', f'href="{prod}"')
        html = html.replace(f"href='{proto}'", f"href='{prod}'")
    for proto, prod in mapping.items():
        html = html.replace(f'href="{proto}#', f'href="{prod}#')
    return html


def rewrite_cut_hrefs(html: str) -> str:
    return _apply_href_mapping(html, CUT_HREF_MAP)


def rewrite_observatory_family(html: str, origin: str) -> str:
    """Observatory family links are same-origin on staging, apex-absolute in production."""
    if not origin:
        return rewrite_cut_hrefs(html)
    base = origin.rstrip("/")
    mapping = {
        proto: (f"{base}{prod}" if prod != "/observatory/" else prod)
        for proto, prod in CUT_HREF_MAP.items()
    }
    return _apply_href_mapping(html, mapping)


def apply_egg_href(html: str, egg_href: str) -> str:
    html = re.sub(
        r'(<a class="th-egg" href=")[^"]+(")',
        lambda m: m.group(1) + egg_href + m.group(2),
        html,
        count=1,
    )
    return html


def apply_noindex(html: str) -> str:
    if NOINDEX_META in html:
        return html
    insert_after = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if insert_after not in html:
        return html
    return html.replace(insert_after, insert_after + "\n" + NOINDEX_META, 1)


def fix_cut_asset_paths(html: str, *, observatory: bool = False) -> str:
    html = html.replace('href="../tokens.css"', 'href="/tokens.css"')
    if observatory:
        html = html.replace(
            'href="observatory.css"', 'href="/assets/css/observatory.css"'
        )
    else:
        html = html.replace('href="site.css"', 'href="/assets/css/site.css"')
    html = html.replace('href="../assets/', 'href="/assets/')
    html = html.replace("href='../assets/", "href='/assets/")
    html = html.replace('src="../assets/', 'src="/assets/')
    return html


def prepare_cut_css() -> tuple[str, str, str]:
    tokens = (CUT / "tokens.css").read_text(encoding="utf-8")
    tokens = tokens.replace('url("assets/fonts/', 'url("/assets/fonts/')
    site_css = (CUT / "prototypes" / "site.css").read_text(encoding="utf-8")
    site_css = site_css.replace(
        'url("../assets/caustic.webp")',
        'url("/assets/caustic.webp")',
    )
    obs_css = (CUT / "prototypes" / "observatory.css").read_text(encoding="utf-8")
    return tokens, site_css, obs_css


def resolve_build_version() -> str:
    """Short git SHA for cache-busting; one value per bundle build."""
    env = os.environ.get("SILICONCORDAT_CUT_BUILD_SHA", "").strip()
    if env:
        return env[:12]
    return subprocess.check_output(
        ["git", "rev-parse", "--short=12", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def is_bustable_url(url: str) -> bool:
    if not url or url.startswith(("#", "data:", "http://", "https://", "//", "mailto:")):
        return False
    if not (url.startswith("/") or url.startswith("./") or url.startswith("../")):
        return False
    base = url.split("#", 1)[0].split("?", 1)[0]
    return bool(STATIC_ASSET_URL.search(base))


def cache_bust_url(url: str, version: str) -> str:
    if re.search(r"[?&]v=", url):
        return url
    frag = ""
    if "#" in url:
        url, frag = url.split("#", 1)
        frag = f"#{frag}"
    if "?" in url:
        return f"{url}&v={version}{frag}"
    return f"{url}?v={version}{frag}"


def _rewrite_pattern(text: str, pattern: re.Pattern[str], version: str) -> str:
    def sub(m: re.Match[str]) -> str:
        url = m.group("url")
        if not is_bustable_url(url):
            return m.group(0)
        busted = cache_bust_url(url, version)
        if pattern is _HTML_LOCAL_ASSET:
            return f'{m.group("attr")}{m.group("q")}{busted}{m.group("q")}'
        if pattern is _CSS_URL:
            q = m.group("q") or ""
            return f"url({q}{busted}{q})"
        if pattern is _JS_DYNAMIC_IMPORT:
            return m.group(0).replace(f'{m.group("q")}{url}{m.group("q")}', f'{m.group("q")}{busted}{m.group("q")}', 1)
        # import/export from and side-effect import
        return m.group(0).replace(f'{m.group("q")}{url}{m.group("q")}', f'{m.group("q")}{busted}{m.group("q")}', 1)

    return pattern.sub(sub, text)


def apply_cache_busters_to_html(html: str, version: str) -> str:
    return _rewrite_pattern(html, _HTML_LOCAL_ASSET, version)


def apply_cache_busters_to_js(text: str, version: str) -> str:
    text = _rewrite_pattern(text, _JS_MODULE_SPEC, version)
    text = _rewrite_pattern(text, _JS_IMPORT_SIDE, version)
    text = _rewrite_pattern(text, _JS_DYNAMIC_IMPORT, version)
    return text


def apply_cache_busters_to_css(text: str, version: str) -> str:
    return _rewrite_pattern(text, _CSS_URL, version)


def apply_cache_busters_to_dist(version: str) -> None:
    for path in sorted(DIST.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if suffix == ".html":
            updated = apply_cache_busters_to_html(text, version)
        elif suffix in {".js", ".mjs"}:
            updated = apply_cache_busters_to_js(text, version)
        elif suffix == ".css":
            updated = apply_cache_busters_to_css(text, version)
        else:
            continue
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def bundle_file_paths(dist: Path | None = None) -> list[str]:
    root = dist if dist is not None else DIST
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "MANIFEST.sha256"
    )


def manifest_listed_paths(dist: Path | None = None) -> list[str]:
    root = dist if dist is not None else DIST
    manifest = root / "MANIFEST.sha256"
    lines = manifest.read_text(encoding="utf-8").strip().splitlines()
    return [line.split("  ", 1)[1] for line in lines if "  " in line]


def write_manifest_sha256(dist: Path | None = None) -> None:
    root = dist if dist is not None else DIST
    lines: list[str] = []
    for rel in bundle_file_paths(root):
        path = root / rel
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel}")
    (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_unversioned_asset_refs(dist: Path, version: str) -> list[str]:
    """Return human-readable locations missing ?v=<version> on bustable refs."""
    issues: list[str] = []
    patterns: list[tuple[str, re.Pattern[str]]] = [
        ("html", _HTML_LOCAL_ASSET),
        ("js", _JS_MODULE_SPEC),
        ("js", _JS_IMPORT_SIDE),
        ("js", _JS_DYNAMIC_IMPORT),
        ("css", _CSS_URL),
    ]
    for path in sorted(dist.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in {".html", ".css", ".js", ".mjs"}:
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(dist).as_posix()
        kind = "html" if suffix == ".html" else ("css" if suffix == ".css" else "js")
        for pat_kind, pattern in patterns:
            if pat_kind != kind:
                continue
            for m in pattern.finditer(text):
                url = m.group("url")
                if is_bustable_url(url) and f"v={version}" not in url:
                    issues.append(f"{rel}: {url}")
    return issues


def append_staging_noindex_headers(existing: str) -> str:
    """Append staging catch-all noindex block; keep path rules separated."""
    if STAGING_NOINDEX_BLOCK.strip() in existing:
        return existing if existing.endswith("\n") else existing + "\n"
    base = existing.rstrip("\n")
    if base:
        base += "\n"
    return base + "\n" + STAGING_NOINDEX_BLOCK


def write_staging_headers() -> None:
    """Cloudflare static _headers: noindex on staging host builds only."""
    headers = (DIST / "_headers").read_text(encoding="utf-8") if (DIST / "_headers").is_file() else ""
    merged = append_staging_noindex_headers(headers)
    if merged != headers:
        (DIST / "_headers").write_text(merged, encoding="utf-8")


def transform_cut_html(raw: str, host: dict, *, observatory: bool = False) -> str:
    html = raw
    if observatory:
        html = rewrite_observatory_family(html, host["observatory_family_origin"])
    else:
        html = rewrite_cut_hrefs(html)
        if 'class="th-egg"' in html:
            html = apply_egg_href(html, host["egg_href"])
    html = fix_cut_asset_paths(html, observatory=observatory)
    if host.get("noindex") or observatory:
        html = apply_noindex(html)
    if observatory and not host.get("noindex"):
        canonical_tag = f'<link rel="canonical" href="{host["egg_href"]}">'
        if canonical_tag not in html:
            if NOINDEX_META in html:
                html = html.replace(NOINDEX_META, NOINDEX_META + "\n" + canonical_tag, 1)
            else:
                insert_after = '<meta name="viewport" content="width=device-width, initial-scale=1">'
                if insert_after in html:
                    html = html.replace(insert_after, insert_after + "\n" + canonical_tag, 1)
    return html


def copy_cut_pages(host: dict) -> None:
    pages = [
        (CUT / "prototypes" / "landing.html", DIST / "index.html"),
        (CUT / "prototypes" / "ml.html", DIST / "ml" / "index.html"),
        (CUT / "prototypes" / "ml-principles.html", DIST / "ml" / "principles" / "index.html"),
        (CUT / "prototypes" / "ml-notes-from-the-colony.html", DIST / "ml" / "notes-from-the-colony" / "index.html"),
        (CUT / "prototypes" / "ml-the-alignment-question.html", DIST / "ml" / "the-alignment-question" / "index.html"),
        (CUT / "prototypes" / "observatory.html", DIST / "observatory" / "index.html"),
    ]
    tokens, site_css, obs_css = prepare_cut_css()
    (DIST / "tokens.css").write_text(tokens, encoding="utf-8")
    css_dest = DIST / "assets" / "css"
    css_dest.mkdir(parents=True, exist_ok=True)
    (css_dest / "site.css").write_text(site_css, encoding="utf-8")
    (css_dest / "observatory.css").write_text(obs_css, encoding="utf-8")

    assets_src = CUT / "assets"
    assets_dest = DIST / "assets"
    for src in sorted(assets_src.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(assets_src)
        if rel.parts and rel.parts[0] == "css":
            continue
        dest = assets_dest / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    for src, dest in pages:
        html = transform_cut_html(
            src.read_text(encoding="utf-8"),
            host,
            observatory=src.name == "observatory.html",
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")


def build() -> None:
    host = load_host_settings(DEFAULT_HOST)
    manifest = load_manifest()
    log_weft_pin(manifest)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    copy_cut_pages(host)
    site_root = site_source_tree(manifest)
    try:
        copy_weft_tree(site_root)
    finally:
        if site_root != SITE and str(site_root).startswith(tempfile.gettempdir()):
            shutil.rmtree(site_root, ignore_errors=True)
    if host.get("noindex"):
        write_staging_headers()
    (DIST / ".assetsignore").write_text(".cut-host\n", encoding="utf-8")
    (DIST / ".cut-host").write_text(DEFAULT_HOST + "\n", encoding="utf-8")
    version = resolve_build_version()
    apply_cache_busters_to_dist(version)
    write_manifest_sha256()
    print(
        f"Built {DIST} (Arrangement 2026-11-10, host={DEFAULT_HOST}, "
        f"weft pin {manifest['weft']['sha'][:12]}, build {version})"
    )


def main() -> None:
    build()


if __name__ == "__main__":
    main()
