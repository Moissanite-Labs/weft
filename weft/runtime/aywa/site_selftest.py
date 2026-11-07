#!/usr/bin/env python3
"""Static checks for the GitHub Pages seed (no browser / no Pages enablement)."""

from __future__ import annotations

import filecmp
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
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
        os.path.join(DOCS, "assets", "shaders", "dashboard_layout.wgsl"),
        os.path.join(DOCS, "data", "telemetry.jsonl"),
        os.path.join(DOCS, "data", "moissanite_telemetry.json"),
        os.path.join(DOCS, "seed-manifest.json"),
    ]
    for path in required:
        _must_exist(path)

    widget_check = assert_widgets_incorporated()

    with open(os.path.join(DOCS, "data", "telemetry.jsonl"), encoding="utf-8") as f:
        line = f.readline().strip()
    sys.path.insert(0, os.path.dirname(__file__))
    from sym2p_codec import parse_sym2p_line  # noqa: WPS433

    parsed = parse_sym2p_line(line)
    if not parsed.get("hash_valid"):
        raise AssertionError("SYM-2P hash validation failed for seed telemetry line")
    if parsed["metrics"].get("active_nodes", 0) <= 0:
        raise AssertionError("active_nodes missing in SYM-2P metrics")

    wgsl_path = os.path.join(DOCS, "assets", "shaders", "dashboard_layout.wgsl")
    wgsl = open(wgsl_path, encoding="utf-8").read()
    if "@vertex" not in wgsl or "@fragment" not in wgsl:
        raise AssertionError("dashboard_layout.wgsl missing shader stages")

    ledger_root = os.path.join(ROOT, "weft", "runtime", "ledger")
    for name in ("WeftTokenTissue.sol", "ProvenanceRegistry.sol"):
        _must_exist(os.path.join(ledger_root, name))

    return {
        "status": "PASS",
        "docs_root": DOCS,
        "widgets_incorporated": widget_check,
        "sym2p_metrics": parsed["metrics"],
    }


def main() -> int:
    result = run_site_selftest()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
