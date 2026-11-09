#!/usr/bin/env python3
"""
Synchronize Aywa field-test artifacts into `weft/runtime/aywa/web/` and stage a
deployable public bundle (`dist/`) for w3ft.org from `site/`.

Everything under `site/` is public. Field fixtures and the retired WebGPU loom
live under `weft/runtime/aywa/web/` and are excluded from deploy (#79).

  python3 scripts/sync_pages_seed.py                 # regenerate telemetry fixtures and shader copy
  python3 scripts/sync_pages_seed.py --stage-dist dist   # also stage dist/ for deploy
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
AYWA_WEB = os.path.join(AYWA, "web")
AYWA_WEB_DATA = os.path.join(AYWA_WEB, "data")
AYWA_WEB_SHADERS = os.path.join(AYWA_WEB, "assets", "shaders")
SITE = os.path.join(ROOT, "site")

# Issue #19: only these site files/directories are staged into the deploy bundle.
PUBLIC_PAGES_FILES = ("index.html", "404.html", "favicon.svg", "og.png", "_headers", "seed-manifest.json")
PUBLIC_PAGES_DIRS = ("assets", "widgets", "papers")
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

# Issue #79: retired field assets must not reappear under site/.
FORBIDDEN_SITE_FIELD_PATHS = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)


def stage_pages_dist(dist_dir: str) -> Dict[str, Any]:
    """
    Stage ONLY the allow-listed public site files from `site/` into `dist_dir`
    so internal docs (`docs/corpus/`, `docs/program/`, `docs/whitepapers/`, etc.)
    never enter the published Pages artifact (#19).
    """
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    staged: List[str] = []
    for fname in PUBLIC_PAGES_FILES:
        src = os.path.join(SITE, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dist_dir, fname))
            staged.append(fname)

    for dname in PUBLIC_PAGES_DIRS:
        src = os.path.join(SITE, dname)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dist_dir, dname))
            staged.append(f"{dname}/")

    leaked = [name for name in FORBIDDEN_INTERNAL_DOCS if os.path.exists(os.path.join(dist_dir, name))]
    if leaked:
        raise RuntimeError(f"Forbidden internal docs leaked into Pages dist: {leaked}")

    field_leaked = [rel for rel in FORBIDDEN_SITE_FIELD_PATHS if os.path.exists(os.path.join(dist_dir, rel))]
    if field_leaked:
        raise RuntimeError(f"Retired field assets leaked into Pages dist (#79): {field_leaked}")

    return {"dist_dir": dist_dir, "staged": staged, "leaked_internal_docs": leaked}


def sync_docs_seed() -> Dict[str, Any]:
    from weft.runtime.telemetry.harvester import harvest_moissanite_telemetry

    os.makedirs(AYWA_WEB_DATA, exist_ok=True)
    os.makedirs(AYWA_WEB_SHADERS, exist_ok=True)
    harvest_moissanite_telemetry(AYWA_WEB_DATA, live=False)
    shutil.copy2(
        os.path.join(AYWA, "dashboard_layout.wgsl"),
        os.path.join(AYWA_WEB_SHADERS, "dashboard_layout.wgsl"),
    )
    still_present = [rel for rel in FORBIDDEN_SITE_FIELD_PATHS if os.path.exists(os.path.join(SITE, rel))]
    if still_present:
        raise RuntimeError(f"Retired field assets still under site/ (#79): {still_present}")

    manifest = {
        "source": "weft/runtime/aywa/web",
        "field_assets": [
            "weft/runtime/aywa/web/data/moissanite_telemetry.json",
            "weft/runtime/aywa/web/data/moissanite_telemetry.bin",
            "weft/runtime/aywa/web/data/telemetry.jsonl",
            "weft/runtime/aywa/web/assets/shaders/dashboard_layout.wgsl",
            "weft/runtime/aywa/web/assets/js/weft-loom.js",
            "weft/runtime/aywa/web/assets/workers/telemetry-worker.js",
        ],
        "vendored": "VENDORED.json (Eido modules and corpus widgets; see scripts/vendor.py)",
        "public_pages_allowlist": list(PUBLIC_PAGES_FILES) + [f"{d}/" for d in PUBLIC_PAGES_DIRS],
    }
    with open(os.path.join(SITE, "seed-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return {"status": "OK", "site": SITE, "aywa_web": AYWA_WEB, "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Aywa web fixtures and optionally stage allow-listed dist/")
    parser.add_argument("--stage-dist", default=None, help="Directory to stage allow-listed Pages bundle into.")
    args = parser.parse_args()
    res = sync_docs_seed()
    if args.stage_dist:
        res["staged_dist"] = stage_pages_dist(args.stage_dist)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
