#!/usr/bin/env python3
"""Build dist-cut/ for Worker ml-siliconcordat-cut: Cut pages at / and /ml, Weft at /weft."""

from __future__ import annotations

import json
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

CUT_HREF_MAP = {
    "landing.html": "/",
    "ml.html": "/ml",
    "ml-principles.html": "/ml/principles/",
    "family-weft.html": "/weft",
}

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


def ensure_commit(sha: str) -> None:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
    )
    if probe.returncode != 0:
        subprocess.run(["git", "fetch", "origin", sha], cwd=ROOT, check=True)


def site_tree_at(rev: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{rev}:site"],
        cwd=ROOT,
        text=True,
    ).strip()


def log_weft_pin(manifest: dict) -> None:
    pinned = manifest["weft"]["sha"]
    ensure_commit(pinned)
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
        dest.write_bytes(rewrite_weft_file(Path(rel), data))


def rewrite_cut_hrefs(html: str) -> str:
    for proto, prod in CUT_HREF_MAP.items():
        html = html.replace(f'href="{proto}"', f'href="{prod}"')
        html = html.replace(f"href='{proto}'", f"href='{prod}'")
    for proto, prod in CUT_HREF_MAP.items():
        html = html.replace(f'href="{proto}#', f'href="{prod}#')
    return html


def fix_cut_asset_paths(html: str) -> str:
    html = html.replace('href="../tokens.css"', 'href="/tokens.css"')
    html = html.replace('href="site.css"', 'href="/assets/css/site.css"')
    html = html.replace('href="../assets/', 'href="/assets/')
    html = html.replace("href='../assets/", "href='/assets/")
    html = html.replace('src="../assets/', 'src="/assets/')
    html = html.replace('<link rel="icon" href="/assets/mark.svg"', '<link rel="icon" href="/assets/mark.svg"')
    return html


def prepare_cut_css() -> tuple[str, str]:
    tokens = (CUT / "tokens.css").read_text(encoding="utf-8")
    tokens = tokens.replace('url("assets/fonts/', 'url("/assets/fonts/')
    site_css = (CUT / "prototypes" / "site.css").read_text(encoding="utf-8")
    site_css = site_css.replace(
        'url("../assets/caustic.webp")',
        'url("/assets/caustic.webp")',
    )
    return tokens, site_css


def copy_cut_pages() -> None:
    pages = [
        (CUT / "prototypes" / "landing.html", DIST / "index.html"),
        (CUT / "prototypes" / "ml.html", DIST / "ml" / "index.html"),
        (CUT / "prototypes" / "ml-principles.html", DIST / "ml" / "principles" / "index.html"),
    ]
    tokens, site_css = prepare_cut_css()
    (DIST / "tokens.css").write_text(tokens, encoding="utf-8")
    css_dest = DIST / "assets" / "css"
    css_dest.mkdir(parents=True, exist_ok=True)
    (css_dest / "site.css").write_text(site_css, encoding="utf-8")

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
        html = src.read_text(encoding="utf-8")
        html = rewrite_cut_hrefs(html)
        html = fix_cut_asset_paths(html)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")


def build() -> None:
    manifest = load_manifest()
    log_weft_pin(manifest)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    copy_cut_pages()
    site_root = site_source_tree(manifest)
    try:
        copy_weft_tree(site_root)
    finally:
        if site_root != SITE and str(site_root).startswith(tempfile.gettempdir()):
            shutil.rmtree(site_root, ignore_errors=True)
    print(
        f"Built {DIST} (Cut Direction A, weft pin {manifest['weft']['sha'][:12]})"
    )


def main() -> None:
    build()


if __name__ == "__main__":
    main()
