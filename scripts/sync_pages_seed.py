#!/usr/bin/env python3
"""Copy Aywa runtime artifacts into docs/ for the static GitHub Pages seed."""

from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AYWA = os.path.join(ROOT, "weft", "runtime", "aywa")
WIDGETS_SRC = os.path.join(ROOT, "weft", "browser-sources", "widgets")
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(DOCS, "data")
SHADERS = os.path.join(DOCS, "assets", "shaders")
WIDGETS_DST = os.path.join(DOCS, "widgets")

WIDGET_SEEDS = (
    "01-sdf-laya-kinetic-typography",
    "02-mind-palace-spatial-memory",
    "03-morphogenetic-bioelectric-field",
    "04-neural-cellular-automata",
    "05-interaction-combinator-net",
)


def sync_browser_source_widgets() -> list[str]:
    """Copy canonical browser-source widget implementations into docs/widgets/."""
    os.makedirs(WIDGETS_DST, exist_ok=True)
    copied: list[str] = []
    for stem in WIDGET_SEEDS:
        for ext in (".html", ".jsx"):
            src = os.path.join(WIDGETS_SRC, stem + ext)
            if not os.path.isfile(src):
                raise FileNotFoundError(f"missing browser-source widget: {src}")
            dst = os.path.join(WIDGETS_DST, stem + ext)
            shutil.copy2(src, dst)
            copied.append(os.path.relpath(dst, ROOT))
    return copied


def main() -> int:
    sys.path.insert(0, AYWA)
    from github_harvester import harvest_moissanite_telemetry  # noqa: WPS433

    os.makedirs(DATA, exist_ok=True)
    os.makedirs(SHADERS, exist_ok=True)
    harvest_moissanite_telemetry(AYWA)
    for name in (
        "moissanite_telemetry.json",
        "moissanite_telemetry.bin",
        "telemetry.jsonl",
    ):
        shutil.copy2(os.path.join(AYWA, name), os.path.join(DATA, name))
    shutil.copy2(
        os.path.join(AYWA, "dashboard_layout.wgsl"),
        os.path.join(SHADERS, "dashboard_layout.wgsl"),
    )
    widget_files = sync_browser_source_widgets()
    manifest = {
        "source": "weft/runtime/aywa",
        "files": ["moissanite_telemetry.json", "moissanite_telemetry.bin", "telemetry.jsonl"],
        "shader": "assets/shaders/dashboard_layout.wgsl",
        "widgets_source": "weft/browser-sources/widgets",
        "widgets": widget_files,
    }
    with open(os.path.join(DOCS, "seed-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps({"status": "OK", "docs": DOCS, "manifest": manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
