#!/usr/bin/env python3
"""CI checks for generated ml-siliconcordat-cut dist-cut/ tree."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-cut"
WEFT = DIST / "weft"

HOST = os.environ.get("SILICONCORDAT_CUT_HOST", "production").strip().lower()

RETIRED = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)

PRIVATE_HREF = re.compile(
    r"github\.com/Moissanite-Labs/(compass|credos|weft-eido|weft-corpus)"
    r'|href="[^"]*(FOUNDER-VISION|SILICONCORDAT|NAMING)\.md'
    r"|family-weft\.html"
)

BAD_WEEFT_PATH = re.compile(
    r'(?<![\w-])(?<![\w/])/assets/|(?<![\w-])(?<![\w/])/papers/'
)

FOOTER_SOURCE = "https://github.com/Moissanite-Labs/siliconcordat"
NOINDEX_META = re.compile(r'<meta\s+name="robots"\s+content="noindex"')

CUT_PAGE_PATHS = (
    DIST / "index.html",
    DIST / "ml" / "index.html",
    DIST / "ml" / "principles" / "index.html",
    DIST / "observatory" / "index.html",
)


def fail(msg: str) -> None:
    print(f"verify: {msg}", file=sys.stderr)
    sys.exit(1)


def check_cut_pages() -> None:
    for rel in (
        "index.html",
        "tokens.css",
        "assets/css/site.css",
        "assets/css/observatory.css",
        "ml/index.html",
        "ml/principles/index.html",
        "observatory/index.html",
        "assets/mark.svg",
        "assets/chamber.svg",
        "assets/caustic.webp",
    ):
        if not (DIST / rel).is_file():
            fail(f"missing Cut asset: {rel}")

    index = (DIST / "index.html").read_text(encoding="utf-8")
    if 'class="th-egg"' not in index:
        fail("landing missing Threshold easter-egg control")
    if 'class="chamber"' in index.split("<main", 1)[0]:
        fail("landing must be Threshold, not chamber hero")
    if 'href="/weft"' not in index and 'href="/weft/' not in index:
        fail("landing missing /weft links")
    if "landing.html" in index or "family-weft.html" in index:
        fail("prototype hrefs remain on landing")
    if "#0a0908" not in (DIST / "tokens.css").read_text(encoding="utf-8"):
        fail("Cut tokens missing --bg #0a0908")

    ml = (DIST / "ml" / "index.html").read_text(encoding="utf-8")
    if "hero--lab" not in ml:
        fail("/ml missing chamber-hero")
    if not re.search(
        r'class="hero hero--lab"[\s\S]*?<h1[^>]*>\s*Moissanite Labs\s*</h1>',
        ml,
    ):
        fail("/ml hero h1 must be Moissanite Labs")

    obs = (DIST / "observatory" / "index.html").read_text(encoding="utf-8")
    if "/assets/css/observatory.css" not in obs:
        fail("observatory missing bundled observatory.css")

    if HOST == "staging":
        if 'href="/observatory/"' not in index:
            fail("staging landing egg must point at /observatory/")
        if "https://siliconcordat.com/" in obs:
            fail("staging observatory must use same-origin family links")
    elif HOST == "production":
        if "https://observatory.askaconsult.com/" not in index:
            fail("production landing egg must point at observatory.askaconsult.com")
        if "https://siliconcordat.com/" not in obs:
            fail("production observatory must use apex family links")


def check_footer_source() -> None:
    for path in CUT_PAGE_PATHS:
        if not path.is_file():
            fail(f"missing page for footer check: {path.relative_to(DIST)}")
        text = path.read_text(encoding="utf-8")
        if FOOTER_SOURCE not in text:
            fail(f"missing footer source link on {path.relative_to(DIST)}")
        if text.count(FOOTER_SOURCE) > 1:
            fail(f"footer source must appear once on {path.relative_to(DIST)}")


def check_noindex() -> None:
    wants = HOST == "staging"
    for path in CUT_PAGE_PATHS:
        text = path.read_text(encoding="utf-8")
        has_meta = bool(NOINDEX_META.search(text))
        if wants and not has_meta:
            fail(f"staging build missing noindex meta on {path.relative_to(DIST)}")
        if not wants and has_meta:
            fail(f"production build must not include noindex on {path.relative_to(DIST)}")
    headers = DIST / "_headers"
    has_header = headers.is_file() and "X-Robots-Tag: noindex" in headers.read_text(encoding="utf-8")
    if wants and not has_header:
        fail("staging build missing _headers X-Robots-Tag: noindex")
    if not wants and has_header:
        fail("production build must not ship _headers noindex")


def check_weft_mirror() -> None:
    if not WEFT.is_dir():
        fail("dist-cut/weft missing — run build script")
    for rel in RETIRED:
        if (WEFT / rel).exists():
            fail(f"retired path present: weft/{rel}")
    for bad_dir in ("data", "assets/shaders", "assets/workers", "lab/field"):
        if (WEFT / bad_dir).exists():
            fail(f"retired directory present: weft/{bad_dir}")

    saw_assets = saw_papers = False
    for path in WEFT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".css", ".js", ".json"} and path.name != "_headers":
            continue
        text = path.read_text(encoding="utf-8")
        if BAD_WEEFT_PATH.search(text):
            fail(f"unprefixed /assets or /papers in {path.relative_to(DIST)}")
        if "/weft/assets" in text:
            saw_assets = True
        if "/weft/papers" in text:
            saw_papers = True
    if not saw_assets or not saw_papers:
        fail("expected /weft/assets and /weft/papers in generated weft")

    headers = (WEFT / "_headers").read_text(encoding="utf-8")
    if "\n/*\n" in headers or headers.startswith("/*\n"):
        fail("_headers catch-all still /* instead of /weft/*")
    if "/weft/*" not in headers:
        fail("_headers missing /weft/* catch-all")

    index = (WEFT / "index.html").read_text(encoding="utf-8")
    if 'class="brand-family"' not in index or 'href="/ml"' not in index:
        fail("§5.3 brand-family missing on weft index")
    if 'href="https://siliconcordat.com' in index:
        fail("weft must use same-origin /ml and /, not siliconcordat.com")
    css = (WEFT / "assets/css/site.css").read_text(encoding="utf-8")
    if ".brand-family" not in css or "menu-family-label" not in css:
        fail("wayfinding CSS not appended to weft site.css")


def check_private_hrefs() -> None:
    for path in DIST.rglob("*.html"):
        rel = path.relative_to(DIST)
        if rel.parts and rel.parts[0] == "weft":
            continue
        text = path.read_text(encoding="utf-8")
        if PRIVATE_HREF.search(text):
            fail(f"private or prototype href in {rel}")
        if re.search(r'github\.com/Moissanite-Labs/weft"', text):
            fail(f"GitHub weft link on Cut page {rel}")
    for path in (DIST / "index.html", DIST / "ml" / "index.html"):
        if "View on GitHub" in path.read_text(encoding="utf-8"):
            fail(f"View on GitHub on {path.relative_to(DIST)}")


def main() -> None:
    check_cut_pages()
    check_footer_source()
    check_noindex()
    check_weft_mirror()
    check_private_hrefs()
    print(f"verify: dist-cut/ passed ml-siliconcordat-cut checks (host={HOST})")


if __name__ == "__main__":
    main()
