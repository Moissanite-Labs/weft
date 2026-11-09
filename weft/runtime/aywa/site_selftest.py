#!/usr/bin/env python3
"""Static and structural checks for the public w3ft.org site in `site/` (Issues #15, #19, #24, #79)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SITE = os.path.join(ROOT, "site")
AYWA = os.path.join(ROOT, "weft", "runtime", "aywa")
AYWA_WEB = os.path.join(AYWA, "web")
AYWA_WEB_DATA = os.path.join(AYWA_WEB, "data")
DOCS = os.path.join(ROOT, "docs")
WIDGETS_DOC = os.path.join(SITE, "widgets")

WIDGET_SEEDS = (
    "01-sdf-laya-kinetic-typography",
    "02-mind-palace-spatial-memory",
    "03-morphogenetic-bioelectric-field",
    "04-neural-cellular-automata",
    "05-interaction-combinator-net",
)

FORBIDDEN_SITE_FIELD_PATHS = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)


def _must_exist(path: str) -> None:
    if not os.path.isfile(path):
        raise AssertionError(f"missing required seed file: {path}")


def _must_not_exist(path: str) -> None:
    if os.path.exists(path):
        raise AssertionError(f"retired field asset must not be published: {path}")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_vendored_files_intact() -> dict:
    """Eido modules and corpus widgets are copied from sibling repositories.

    site/VENDORED.json pins each file's SHA-256; an edit made here instead of
    upstream fails this check (see scripts/vendor.py).
    """
    from scripts.vendor import check

    errors = check()
    if errors:
        raise AssertionError(f"vendored files changed locally: {errors}")
    manifest = json.load(open(os.path.join(SITE, "VENDORED.json"), encoding="utf-8"))
    widgets = [n for n in os.listdir(WIDGETS_DOC) if n.endswith(".html") and n != "index.html"]
    if len(widgets) != len(WIDGET_SEEDS):
        raise AssertionError(f"expected {len(WIDGET_SEEDS)} widgets in site/widgets, found {len(widgets)}")
    return {source: data["commit"] for source, data in manifest["sources"].items()}


def parse_headers_file(text: str) -> list[tuple[str, dict]]:
    """Parse Cloudflare `_headers` into [(path pattern, {header: value})]."""
    rules: list[tuple[str, dict]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            rules.append((raw.strip(), {}))
        elif rules:
            name, _, value = raw.strip().partition(":")
            rules[-1][1][name.strip()] = value.strip()
    return rules


def _matches(pattern: str, path: str) -> bool:
    if "*" not in pattern:
        return pattern == path
    import re as _re

    return _re.fullmatch(_re.escape(pattern).replace(r"\*", ".*"), path) is not None


def assert_security_headers() -> dict:
    """Every public HTML page has exactly one CSP rule (#70); first-party pages allow no third-party hosts."""
    rules = parse_headers_file(open(os.path.join(SITE, "_headers"), encoding="utf-8").read())
    pages = []
    for root, _dirs, files in os.walk(SITE):
        for name in files:
            if not name.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(root, name), SITE).replace(os.sep, "/")
            if rel == "index.html":
                url = "/"
            elif rel.endswith("/index.html"):
                url = "/" + rel[: -len("index.html")]
            else:
                url = "/" + rel
            pages.append(url)
    problems = []
    for url in sorted(pages):
        csp = [h["Content-Security-Policy"] for pat, h in rules if _matches(pat, url) and "Content-Security-Policy" in h]
        if len(csp) != 1:
            problems.append(f"{url}: {len(csp)} CSP rules (need exactly 1)")
            continue
        exported_widget = url.startswith("/widgets/0")
        if not exported_widget and "https://" in csp[0]:
            problems.append(f"{url}: first-party page allows third-party hosts")
        if "frame-ancestors" not in csp[0]:
            problems.append(f"{url}: CSP lacks frame-ancestors")
    if problems:
        raise AssertionError(f"security header coverage failed: {problems}")
    return {"pages_checked": len(pages)}


def run_site_selftest() -> dict:
    required = [
        os.path.join(SITE, "index.html"),
        os.path.join(SITE, "404.html"),
        os.path.join(SITE, "favicon.svg"),
        os.path.join(SITE, "widgets", "index.html"),
        os.path.join(SITE, "assets", "css", "site.css"),
        os.path.join(SITE, "assets", "js", "site.js"),
        os.path.join(DOCS, "mission.md"),
        os.path.join(DOCS, "roadmap.md"),
        os.path.join(DOCS, "glossary.md"),
        os.path.join(DOCS, "design-notes", "constitution-vs-contract.md"),
        os.path.join(SITE, "assets", "js", "aesthetic-mixer.js"),
        os.path.join(SITE, "assets", "js", "sym2p-parse.js"),
        os.path.join(SITE, "assets", "js", "cell-layout.js"),
        os.path.join(SITE, "assets", "js", "glyph-font.js"),
        os.path.join(SITE, "assets", "js", "simplex-pad.js"),
        os.path.join(SITE, "seed-manifest.json"),
        os.path.join(SITE, "VENDORED.json"),
        os.path.join(SITE, "papers", "index.html"),
        os.path.join(SITE, "papers", "manifest.json"),
        os.path.join(SITE, "assets", "css", "papers.css"),
        os.path.join(AYWA_WEB, "assets", "js", "weft-loom.js"),
        os.path.join(AYWA_WEB, "assets", "workers", "telemetry-worker.js"),
        os.path.join(AYWA_WEB, "assets", "shaders", "dashboard_layout.wgsl"),
        os.path.join(AYWA_WEB_DATA, "telemetry.jsonl"),
        os.path.join(AYWA_WEB_DATA, "moissanite_telemetry.json"),
        os.path.join(AYWA_WEB_DATA, "moissanite_telemetry.bin"),
    ]
    for path in required:
        _must_exist(path)

    for rel in FORBIDDEN_SITE_FIELD_PATHS:
        _must_not_exist(os.path.join(SITE, rel))

    vendored = assert_vendored_files_intact()
    headers = assert_security_headers()

    # Issue #15: verify no suspended_accounts or personal login leak in web fixture JSON
    telemetry_json_text = open(os.path.join(AYWA_WEB_DATA, "moissanite_telemetry.json"), encoding="utf-8").read()
    if "suspended_accounts" in telemetry_json_text:
        raise AssertionError("web/data/moissanite_telemetry.json must not contain suspended_accounts (#15)")
    telemetry_data = json.loads(telemetry_json_text)
    if telemetry_data.get("source") not in ("fixture", "github-api"):
        raise AssertionError("web/data/moissanite_telemetry.json must state source='fixture' or 'github-api' (#15)")

    with open(os.path.join(AYWA_WEB_DATA, "telemetry.jsonl"), encoding="utf-8") as f:
        line = f.readline().strip()
    from weft.runtime.telemetry.sym2p_codec import parse_sym2p_line

    parsed = parse_sym2p_line(line)
    if not parsed.get("hash_valid"):
        raise AssertionError("SYM-2P hash validation failed for seed telemetry line")
    if parsed["metrics"].get("active_nodes", 0) <= 0:
        raise AssertionError("active_nodes missing in SYM-2P metrics")

    wgsl_path = os.path.join(AYWA_WEB, "assets", "shaders", "dashboard_layout.wgsl")
    wgsl = open(wgsl_path, encoding="utf-8").read()
    if "@vertex" not in wgsl or "@fragment" not in wgsl:
        raise AssertionError("dashboard_layout.wgsl missing shader stages")
    for uniform_field in ("gini_index", "user_density", "user_hue", "node_vel_0", "user_rounding", "org_tension"):
        if uniform_field not in wgsl:
            raise AssertionError(f"dashboard_layout.wgsl does not consume {uniform_field} (#24)")
    # Issue #37: cells come from the CPU layout (exact rectangles in CSS px) and text from
    # the two-word bitmask font; no clip-space aspect constant or modulo grid index.
    for binding in ("var<uniform> view", "var<storage, read> cells", "var<storage, read> font"):
        if binding not in wgsl:
            raise AssertionError(f"dashboard_layout.wgsl missing binding '{binding}' (#37)")
    for stale in ("p.x *= 1.6", "1.77777777778", "(cell_id.y + 2.0) * 5.0"):
        if stale in wgsl:
            raise AssertionError(f"dashboard_layout.wgsl still contains '{stale}' (#37)")
    runtime_wgsl = open(os.path.join(AYWA, "dashboard_layout.wgsl"), encoding="utf-8").read()
    if runtime_wgsl != wgsl:
        raise AssertionError(
            "weft/runtime/aywa/web/assets/shaders/dashboard_layout.wgsl diverges from weft/runtime/aywa/ "
            "(run scripts/sync_pages_seed.py)"
        )

    # Issue #19: verify allow-listed Pages dist staging excludes internal docs/ subdirectories
    from scripts.sync_pages_seed import stage_pages_dist

    with tempfile.TemporaryDirectory(prefix="weft-pages-dist-") as tmp_dist:
        staged_info = stage_pages_dist(tmp_dist)
        if not os.path.isfile(os.path.join(tmp_dist, "index.html")):
            raise AssertionError("Staged dist missing index.html")
        for internal in ("corpus", "program", "mission.md", "README.md"):
            if os.path.exists(os.path.join(tmp_dist, internal)):
                raise AssertionError(f"Staged dist leaked internal path {internal!r} (#19)")
        if not os.path.isfile(os.path.join(tmp_dist, "404.html")):
            raise AssertionError("Staged dist missing 404.html")
        for rel in FORBIDDEN_SITE_FIELD_PATHS:
            if os.path.exists(os.path.join(tmp_dist, rel)):
                raise AssertionError(f"Staged dist leaked retired field asset {rel!r} (#79)")

    ledger_root = os.path.join(ROOT, "weft", "runtime", "ledger")
    for name in ("WeftTokenTissue.sol", "ProvenanceRegistry.sol", "TensionGovernor.sol"):
        _must_exist(os.path.join(ledger_root, name))

    return {
        "status": "PASS",
        "site_root": SITE,
        "aywa_web_root": AYWA_WEB,
        "vendored_from": vendored,
        "security_headers": headers,
        "sym2p_metrics": parsed["metrics"],
        "staged_allowlist": staged_info["staged"],
    }


def main() -> int:
    result = run_site_selftest()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
