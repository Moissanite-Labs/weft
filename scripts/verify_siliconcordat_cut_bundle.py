#!/usr/bin/env python3
"""CI checks for generated ml-siliconcordat-cut dist-cut/ tree."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-cut"
WEFT = DIST / "weft"
HOST_SETTINGS_PATH = ROOT / "siliconcordat-cut" / "host-settings.json"


def fail(msg: str) -> None:
    print(f"verify: {msg}", file=sys.stderr)
    sys.exit(1)


def resolve_host() -> tuple[str, dict]:
    with HOST_SETTINGS_PATH.open(encoding="utf-8") as fh:
        table = json.load(fh)

    env_val = os.environ.get("SILICONCORDAT_CUT_HOST")
    env_host = env_val.strip().lower() if env_val is not None else None

    cut_host_file = DIST / ".cut-host"
    file_host = (
        cut_host_file.read_text(encoding="utf-8").strip().lower()
        if cut_host_file.is_file()
        else None
    )

    host = (
        env_host
        if env_host is not None
        else (file_host if file_host is not None else "production")
    )
    if host not in table:
        fail(f"unknown SILICONCORDAT_CUT_HOST={host!r}; expected one of {sorted(table)}")

    if env_host is not None and file_host is not None and env_host != file_host:
        fail(
            f"SILICONCORDAT_CUT_HOST ({env_host}) disagrees with dist-cut/.cut-host ({file_host})"
        )

    return host, table[host]


HOST, host_cfg = resolve_host()

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
    r"|(?:landing|ml|ml-principles|ml-notes-from-the-colony|family-weft|observatory)\.html"
)

BAD_WEEFT_PATH = re.compile(
    r'(?<![\w-])(?<![\w/])/assets/|(?<![\w-])(?<![\w/])/papers/'
)

NOINDEX_META = re.compile(r'<meta\s+name="robots"\s+content="noindex"')

CUT_PAGE_PATHS = (
    DIST / "index.html",
    DIST / "ml" / "index.html",
    DIST / "ml" / "principles" / "index.html",
    DIST / "ml" / "notes-from-the-colony" / "index.html",
    DIST / "observatory" / "index.html",
)

HREF_ATTR = re.compile(r'href=(["\'])([^"\']*)\1')
TH_EGG_HREF = re.compile(r'<a\s+class="th-egg"\s+href="([^"]+)"')

APEX_HOST = "siliconcordat.com"
OBSERVATORY_EGG_PROD_HOST = "observatory.askaconsult.com"
APEX_FAMILY_PATHS = ("/", "/ml", "/weft")


def href_values(html: str) -> list[str]:
    return [m.group(2) for m in HREF_ATTR.finditer(html)]


def th_egg_href(html: str) -> str | None:
    m = TH_EGG_HREF.search(html)
    return m.group(1) if m else None


def href_parsed_match(href: str, *, scheme: str, hostname: str, path: str) -> bool:
    p = urlparse(href)
    return (
        p.scheme == scheme
        and (p.hostname or "").lower() == hostname.lower()
        and p.path == path
    )


def href_is_relative_path(href: str, path: str) -> bool:
    p = urlparse(href)
    return p.scheme == "" and p.netloc == "" and p.path == path


def page_has_apex_family_href(html: str, path: str) -> bool:
    return any(
        href_parsed_match(h, scheme="https", hostname=APEX_HOST, path=path)
        for h in href_values(html)
    )


def page_has_https_href_to_host(html: str, hostname: str) -> bool:
    want = hostname.lower()
    for h in href_values(html):
        p = urlparse(h)
        if p.scheme == "https" and (p.hostname or "").lower() == want:
            return True
    return False


def count_href_to(html: str, *, scheme: str, hostname: str, path: str) -> int:
    return sum(
        1
        for h in href_values(html)
        if href_parsed_match(h, scheme=scheme, hostname=hostname, path=path)
    )


def check_cut_pages() -> None:
    for rel in (
        "index.html",
        "tokens.css",
        "assets/css/site.css",
        "assets/css/observatory.css",
        "ml/index.html",
        "ml/principles/index.html",
        "ml/notes-from-the-colony/index.html",
        "ml/the-alignment-question/index.html",
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
    if 'class="chamber"' in index:
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

    note = (DIST / "ml" / "notes-from-the-colony" / "index.html").read_text(encoding="utf-8")
    if re.search(r"<h1[^>]*>\s*Notes from the colony\s*</h1>", note) is None:
        fail("/ml/notes-from-the-colony/ missing h1")
    if "ml-notes-from-the-colony.html" in note or "family-weft.html" in note:
        fail("prototype hrefs remain on notes page")
    doc_head = re.search(r'<header class="doc-head">([\s\S]*?)</header>', note)
    if not doc_head or 'class="proposal"' not in doc_head.group(1):
        fail("/ml/notes-from-the-colony/ missing proposal in doc-head")

    obs = (DIST / "observatory" / "index.html").read_text(encoding="utf-8")
    if "/assets/css/observatory.css" not in obs:
        fail("observatory missing bundled observatory.css")

    egg = th_egg_href(index)
    expected_egg = host_cfg["egg_href"]
    if expected_egg.startswith("/"):
        if not egg or not href_is_relative_path(egg, expected_egg):
            fail(f'{HOST} landing egg must be href="{expected_egg}"')
    else:
        p_egg = urlparse(expected_egg)
        if not egg or not href_parsed_match(
            egg,
            scheme=p_egg.scheme,
            hostname=p_egg.hostname or "",
            path=p_egg.path or "/",
        ):
            fail(f'{HOST} landing egg must be href="{expected_egg}"')

    origin = host_cfg.get("observatory_family_origin", "")
    if origin:
        p_origin = urlparse(origin)
        origin_host = p_origin.hostname or ""
        for path in APEX_FAMILY_PATHS:
            if not any(
                href_parsed_match(h, scheme=p_origin.scheme, hostname=origin_host, path=path)
                for h in href_values(obs)
            ):
                fail(f"{HOST} observatory missing family href for path {path!r}")
    else:
        if page_has_https_href_to_host(obs, APEX_HOST):
            fail(f"{HOST} observatory must use same-origin family links")


def check_footer_source() -> None:
    for path in CUT_PAGE_PATHS:
        if not path.is_file():
            fail(f"missing page for footer check: {path.relative_to(DIST)}")
        text = path.read_text(encoding="utf-8")
        footer_hits = count_href_to(
            text, scheme="https", hostname="github.com", path="/Moissanite-Labs/siliconcordat"
        )
        if footer_hits < 1:
            fail(f"missing footer source link on {path.relative_to(DIST)}")
        if footer_hits > 1:
            fail(f"footer source must appear once on {path.relative_to(DIST)}")


def check_noindex() -> None:
    is_staging = host_cfg.get("noindex", False)
    obs_path = DIST / "observatory" / "index.html"
    for path in CUT_PAGE_PATHS:
        text = path.read_text(encoding="utf-8")
        has_meta = bool(NOINDEX_META.search(text))
        is_obs = path == obs_path
        if is_staging:
            if not has_meta:
                fail(f"staging build missing noindex meta on {path.relative_to(DIST)}")
        else:
            if is_obs:
                if not has_meta:
                    fail(f"production observatory missing noindex on {path.relative_to(DIST)}")
                canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', text)
                if not canon_match:
                    fail(f"production observatory missing canonical link on {path.relative_to(DIST)}")
                canon_href = canon_match.group(1)
                p_egg = urlparse(host_cfg["egg_href"])
                if not href_parsed_match(
                    canon_href,
                    scheme=p_egg.scheme,
                    hostname=p_egg.hostname or "",
                    path=p_egg.path or "/",
                ):
                    fail(
                        f"production observatory canonical {canon_href} does not match {host_cfg['egg_href']}"
                    )
            else:
                if has_meta:
                    fail(f"production build must not include noindex on {path.relative_to(DIST)}")

    headers = DIST / "_headers"
    has_header = headers.is_file() and "X-Robots-Tag: noindex" in headers.read_text(encoding="utf-8")
    if is_staging and not has_header:
        fail("staging build missing _headers X-Robots-Tag: noindex")
    if not is_staging and has_header:
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

    for h_path in (WEFT / "_headers", DIST / "_headers"):
        if not h_path.is_file():
            fail(f"missing headers file: {h_path.relative_to(DIST)}")
        h_text = h_path.read_text(encoding="utf-8")
        if "/weft/*" not in h_text:
            fail(f"{h_path.relative_to(DIST)} missing /weft/*")

    weft_headers = (WEFT / "_headers").read_text(encoding="utf-8")
    if "\n/*\n" in weft_headers or weft_headers.startswith("/*\n"):
        fail("weft/_headers catch-all still /* instead of /weft/*")

    if not host_cfg.get("noindex", False):
        dist_headers = (DIST / "_headers").read_text(encoding="utf-8")
        if dist_headers.startswith("/*\n") or "\n/*\n" in dist_headers:
            fail("dist-cut/_headers on production must not start with /*\\n or contain \\n/*\\n")

    index = (WEFT / "index.html").read_text(encoding="utf-8")
    if page_has_https_href_to_host(index, "w3ft.org"):
        fail("w3ft.org canonical not rewritten on weft index")
    if 'class="brand-family"' not in index or 'href="/ml"' not in index:
        fail("§5.3 brand-family missing on weft index")
    if page_has_https_href_to_host(index, APEX_HOST):
        fail("weft must use same-origin /ml and /, not siliconcordat.com")
    css = (WEFT / "assets/css/site.css").read_text(encoding="utf-8")
    if ".brand-family" not in css or "menu-family-label" not in css:
        fail("wayfinding CSS not appended to weft site.css")


ALLOWED_WEFT_REPO = {
    Path("ml/index.html"),
    Path("ml/notes-from-the-colony/index.html"),
}


def check_private_hrefs() -> None:
    for path in DIST.rglob("*.html"):
        rel = path.relative_to(DIST)
        if rel.parts and rel.parts[0] == "weft":
            continue
        text = path.read_text(encoding="utf-8")
        if PRIVATE_HREF.search(text):
            fail(f"private or prototype href in {rel}")
        if rel not in ALLOWED_WEFT_REPO:
            has_weft_link = False
            for h in href_values(text):
                p = urlparse(h)
                if (p.hostname or "").lower() == "github.com" and (
                    p.path == "/Moissanite-Labs/weft"
                    or p.path.startswith("/Moissanite-Labs/weft/")
                ):
                    has_weft_link = True
                    break
            if not has_weft_link and re.search(
                r"github\.com/Moissanite-Labs/weft(?![-\w])", text, re.I
            ):
                has_weft_link = True
            if has_weft_link:
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
