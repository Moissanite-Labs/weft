#!/usr/bin/env python3
"""
Synchronize Aywa runtime artifacts into `docs/` and stage an allow-listed
GitHub Pages bundle (`dist/`) that excludes internal documentation (#19).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from typing import Any, Dict, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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

# Issue #19: Only public site files/directories may be staged into the Pages artifact.
PUBLIC_PAGES_FILES = ("index.html", ".nojekyll", "seed-manifest.json")
PUBLIC_PAGES_DIRS = ("assets", "data", "widgets")
FORBIDDEN_INTERNAL_DOCS = (
    "corpus",
    "program",
    "whitepapers",
    "design-notes",
    "tech",
    "interfaces",
    "wiki",
    "mission.md",
    "glossary.md",
    "roadmap.md",
)


def sync_browser_source_widgets() -> List[str]:
    """Copy canonical browser-source widget implementations into docs/widgets/."""
    os.makedirs(WIDGETS_DST, exist_ok=True)
    copied: List[str] = []
    for stem in WIDGET_SEEDS:
        for ext in (".html", ".jsx"):
            src = os.path.join(WIDGETS_SRC, stem + ext)
            if not os.path.isfile(src):
                raise FileNotFoundError(f"missing browser-source widget: {src}")
            dst = os.path.join(WIDGETS_DST, stem + ext)
            shutil.copy2(src, dst)
            copied.append(os.path.relpath(dst, ROOT))
    return copied


def stage_pages_dist(dist_dir: str) -> Dict[str, Any]:
    """
    Stage ONLY the allow-listed public Pages site files from `docs/` into `dist_dir`
    so internal docs (`docs/corpus/`, `docs/program/`, `docs/whitepapers/`, etc.)
    never enter the published Pages artifact (#19).
    """
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    staged: List[str] = []
    for fname in PUBLIC_PAGES_FILES:
        src = os.path.join(DOCS, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dist_dir, fname))
            staged.append(fname)

    for dname in PUBLIC_PAGES_DIRS:
        src = os.path.join(DOCS, dname)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dist_dir, dname))
            staged.append(f"{dname}/")

    leaked = [name for name in FORBIDDEN_INTERNAL_DOCS if os.path.exists(os.path.join(dist_dir, name))]
    if leaked:
        raise RuntimeError(f"Forbidden internal docs leaked into Pages dist: {leaked}")

    return {"dist_dir": dist_dir, "staged": staged, "leaked_internal_docs": leaked}


def sync_docs_seed() -> Dict[str, Any]:
    from weft.runtime.telemetry.harvester import harvest_moissanite_telemetry

    os.makedirs(DATA, exist_ok=True)
    os.makedirs(SHADERS, exist_ok=True)
    harvest_moissanite_telemetry(AYWA, live=False)
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
        "public_pages_allowlist": list(PUBLIC_PAGES_FILES) + [f"{d}/" for d in PUBLIC_PAGES_DIRS],
    }
    with open(os.path.join(DOCS, "seed-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return {"status": "OK", "docs": DOCS, "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Pages seed and optionally stage allow-listed dist/")
    parser.add_argument("--stage-dist", default=None, help="Directory to stage allow-listed Pages bundle into.")
    args = parser.parse_args()
    res = sync_docs_seed()
    if args.stage_dist:
        res["staged_dist"] = stage_pages_dist(args.stage_dist)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
