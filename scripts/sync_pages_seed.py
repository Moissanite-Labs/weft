#!/usr/bin/env python3
"""
Synchronize Aywa runtime artifacts into the public site (`site/`) and stage a
deployable bundle (`dist/`) for w3ft.org.

Everything under `site/` is public. Project documentation lives in `docs/` and is
never staged; the forbidden-name check below guards against it leaking in (#19).

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
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "data")
SHADERS = os.path.join(SITE, "assets", "shaders")

# Issue #19: only these site files/directories are staged into the deploy bundle.
PUBLIC_PAGES_FILES = ("index.html", "404.html", "favicon.svg", "og.png", "_headers", "seed-manifest.json")
PUBLIC_PAGES_DIRS = ("assets", "data", "widgets", "papers")
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
    manifest = {
        "source": "weft/runtime/aywa",
        "files": ["moissanite_telemetry.json", "moissanite_telemetry.bin", "telemetry.jsonl"],
        "shader": "assets/shaders/dashboard_layout.wgsl",
        "vendored": "VENDORED.json (Eido modules and corpus widgets; see scripts/vendor.py)",
        "public_pages_allowlist": list(PUBLIC_PAGES_FILES) + [f"{d}/" for d in PUBLIC_PAGES_DIRS],
    }
    with open(os.path.join(SITE, "seed-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return {"status": "OK", "site": SITE, "manifest": manifest}


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
