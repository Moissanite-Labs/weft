#!/usr/bin/env python3
"""CI checks for the generated ml-siliconcordat dist/ tree."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
WEFT = DIST / "weft"

RETIRED = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)
BAD_WEEFT_PATH = re.compile(
    r'(?<![\w-])(?<![\w/])/assets/|(?<![\w-])(?<![\w/])/papers/'
)
WEFT_OK = re.compile(r"/weft/assets/|/weft/papers/")


def fail(msg: str) -> None:
    print(f"verify: {msg}", file=sys.stderr)
    sys.exit(1)


def check_exists() -> None:
    if not WEFT.is_dir():
        fail("dist/weft missing — run scripts/build_siliconcordat_bundle.py")


def check_retired_absent() -> None:
    for rel in RETIRED:
        if (WEFT / rel).exists():
            fail(f"retired path still present: weft/{rel}")
    for bad_dir in ("data", "assets/shaders", "assets/workers"):
        if (WEFT / bad_dir).exists():
            fail(f"retired directory present: weft/{bad_dir}")


def iter_weft_text_files():
    for path in WEFT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".html", ".css", ".js", ".json"} or path.name == "_headers":
            yield path


def check_weft_rewrites() -> None:
    saw_assets = saw_papers = False
    for path in iter_weft_text_files():
        text = path.read_text(encoding="utf-8")
        if BAD_WEEFT_PATH.search(text):
            fail(f"unprefixed /assets or /papers in {path.relative_to(DIST)}")
        if "/weft/assets" in text:
            saw_assets = True
        if "/weft/papers" in text:
            saw_papers = True
    if not saw_assets or not saw_papers:
        fail("expected /weft/assets and /weft/papers in generated weft HTML/CSS")


def check_headers_catchall() -> None:
    headers = (WEFT / "_headers").read_text(encoding="utf-8")
    if "\n/*\n" in headers or headers.startswith("/*\n"):
        fail("_headers catch-all still /* instead of /weft/*")
    if "/weft/*" not in headers:
        fail("_headers missing /weft/* catch-all")


def lab_files() -> list[Path]:
    paths = [DIST / "index.html", DIST / "styles.css", DIST / "ml" / "index.html"]
    return [p for p in paths if p.is_file()]


def check_lab_pages() -> None:
    for path in lab_files():
        text = path.read_text(encoding="utf-8")
        if "#ff5b14" in text.lower() or "--orange" in text:
            fail(f"stale orange token in {path.relative_to(DIST)}")
    styles = (DIST / "styles.css").read_text(encoding="utf-8")
    if "#d9c7a0" not in styles and "--gold-flat" not in styles:
        fail("lab styles missing champagne tokens")
    for path in lab_files():
        text = path.read_text(encoding="utf-8")
        weft_hrefs = re.findall(r'href="([^"]*w3ft[^"]*)"', text, re.I)
        for href in weft_hrefs:
            if not href.startswith("https://w3ft.org"):
                fail(f"non-w3ft.org Weft href {href!r} in {path.name}")
        if 'href="/weft' in text or "siliconcordat.com/weft" in text.lower():
            if "siliconcordat.com/weft is planned" not in text:
                fail(f"lab page links to /weft mirror in {path.name}")


def main() -> None:
    check_exists()
    check_retired_absent()
    check_weft_rewrites()
    check_headers_catchall()
    check_lab_pages()
    print("verify: dist/ passed all siliconcordat checks")


if __name__ == "__main__":
    main()
