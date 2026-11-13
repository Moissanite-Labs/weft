#!/usr/bin/env python3
"""Static and structural checks for the GitHub Pages seed (Issues #15, #19, #24)."""

from __future__ import annotations

import filecmp
import hashlib
import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DOCS = os.path.join(ROOT, "docs")
WIDGETS_SRC = os.path.join(ROOT, "weft", "browser-sources", "widgets")
WIDGETS_DOC = os.path.join(DOCS, "widgets")

WIDGET_SEEDS = (
    "01-sdf-laya-kinetic-typography",
    "02-mind-palace-spatial-memory",
    "03-morphogenetic-bioelectric-field",
    "04-neural-cellular-automata",
    "05-interaction-combinator-net",
)


def _must_exist(path: str) -> None:
    if not os.path.isfile(path):
        raise AssertionError(f"missing required seed file: {path}")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_widgets_incorporated() -> dict:
    mismatches = []
    matched = []
    for stem in WIDGET_SEEDS:
        name = f"{stem}.html"
        src = os.path.join(WIDGETS_SRC, name)
        doc = os.path.join(WIDGETS_DOC, name)
        if not os.path.isfile(src):
            mismatches.append({"widget": name, "error": "missing source browser widget"})
            continue
        if not os.path.isfile(doc):
            mismatches.append({"widget": name, "error": "missing docs/widgets copy (run sync_pages_seed.py)"})
            continue
        if not filecmp.cmp(src, doc, shallow=False):
            mismatches.append(
                {
                    "widget": name,
                    "error": "docs copy diverges from weft/browser-sources/widgets",
                    "source_sha256": _sha256_file(src),
                    "docs_sha256": _sha256_file(doc),
                }
            )
            continue
        matched.append(name)
    if mismatches:
        raise AssertionError(f"widget incorporation failed: {mismatches}")
    return {"matched_html_widgets": matched, "count": len(matched)}


def run_site_selftest() -> dict:
    required = [
        os.path.join(DOCS, "index.html"),
        os.path.join(DOCS, "widgets", "index.html"),
        os.path.join(DOCS, "assets", "js", "weft-loom.js"),
        os.path.join(DOCS, "assets", "js", "weft-atlas.js"),
        os.path.join(DOCS, "mission.md"),
        os.path.join(DOCS, "roadmap.md"),
        os.path.join(DOCS, "glossary.md"),
        os.path.join(DOCS, "whitepapers", "syntactic-weft-whitepaper.md"),
        os.path.join(DOCS, "design-notes", "aywa-web-design-philosophy.md"),
        os.path.join(DOCS, "design-notes", "constitution-vs-contract.md"),
        os.path.join(DOCS, "assets", "js", "aesthetic-mixer.js"),
        os.path.join(DOCS, "assets", "js", "sym2p-parse.js"),
        os.path.join(DOCS, "assets", "workers", "telemetry-worker.js"),
        os.path.join(DOCS, "assets", "shaders", "dashboard_layout.wgsl"),
        os.path.join(DOCS, "data", "telemetry.jsonl"),
        os.path.join(DOCS, "data", "moissanite_telemetry.json"),
        os.path.join(DOCS, "data", "moissanite_telemetry.bin"),
        os.path.join(DOCS, "seed-manifest.json"),
    ]
    for path in required:
        _must_exist(path)

    widget_check = assert_widgets_incorporated()

    # Issue #15: verify no suspended_accounts or personal login leak in docs/data/moissanite_telemetry.json
    telemetry_json_text = open(os.path.join(DOCS, "data", "moissanite_telemetry.json"), encoding="utf-8").read()
    if "suspended_accounts" in telemetry_json_text:
        raise AssertionError("docs/data/moissanite_telemetry.json must not contain suspended_accounts (#15)")
    telemetry_data = json.loads(telemetry_json_text)
    if telemetry_data.get("source") not in ("fixture", "github-api"):
        raise AssertionError("docs/data/moissanite_telemetry.json must state source='fixture' or 'github-api' (#15)")

    with open(os.path.join(DOCS, "data", "telemetry.jsonl"), encoding="utf-8") as f:
        line = f.readline().strip()
    from weft.runtime.telemetry.sym2p_codec import parse_sym2p_line

    parsed = parse_sym2p_line(line)
    if not parsed.get("hash_valid"):
        raise AssertionError("SYM-2P hash validation failed for seed telemetry line")
    if parsed["metrics"].get("active_nodes", 0) <= 0:
        raise AssertionError("active_nodes missing in SYM-2P metrics")

    wgsl_path = os.path.join(DOCS, "assets", "shaders", "dashboard_layout.wgsl")
    wgsl = open(wgsl_path, encoding="utf-8").read()
    if "@vertex" not in wgsl or "@fragment" not in wgsl:
        raise AssertionError("dashboard_layout.wgsl missing shader stages")
    for uniform_field in ("gini_index", "user_density", "user_hue", "node_vel_0", "labelData"):
        if uniform_field not in wgsl:
            raise AssertionError(f"dashboard_layout.wgsl does not consume {uniform_field} (#24)")

    # Issue #19: verify allow-listed Pages dist staging excludes internal docs/ subdirectories
    from scripts.sync_pages_seed import stage_pages_dist

    with tempfile.TemporaryDirectory(prefix="weft-pages-dist-") as tmp_dist:
        staged_info = stage_pages_dist(tmp_dist)
        if not os.path.isfile(os.path.join(tmp_dist, "index.html")):
            raise AssertionError("Staged dist missing index.html")
        if os.path.exists(os.path.join(tmp_dist, "corpus")) or os.path.exists(os.path.join(tmp_dist, "program")):
            raise AssertionError("Staged dist leaked internal docs/corpus or docs/program (#19)")

    ledger_root = os.path.join(ROOT, "weft", "runtime", "ledger")
    for name in ("WeftTokenTissue.sol", "ProvenanceRegistry.sol", "TensionGovernor.sol"):
        _must_exist(os.path.join(ledger_root, name))

    return {
        "status": "PASS",
        "docs_root": DOCS,
        "widgets_incorporated": widget_check,
        "sym2p_metrics": parsed["metrics"],
        "staged_allowlist": staged_info["staged"],
    }


def main() -> int:
    result = run_site_selftest()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
