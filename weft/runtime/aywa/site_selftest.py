#!/usr/bin/env python3
"""Static checks for the GitHub Pages seed (no browser / no Pages enablement)."""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DOCS = os.path.join(ROOT, "docs")


def _must_exist(path: str) -> None:
    if not os.path.isfile(path):
        raise AssertionError(f"missing required seed file: {path}")


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

    widget_dir = os.path.join(DOCS, "widgets")
    widgets = [f for f in os.listdir(widget_dir) if f.endswith(".html") and f != "index.html"]
    if len(widgets) != 5:
        raise AssertionError(f"expected 5 portable widget seeds, got {len(widgets)}")

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
        "widgets": len(widgets),
        "sym2p_metrics": parsed["metrics"],
    }


def main() -> int:
    result = run_site_selftest()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
