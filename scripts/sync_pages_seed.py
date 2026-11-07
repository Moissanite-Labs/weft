#!/usr/bin/env python3
"""Copy Aywa runtime artifacts into docs/ for the static GitHub Pages seed."""

from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AYWA = os.path.join(ROOT, "weft", "runtime", "aywa")
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(DOCS, "data")
SHADERS = os.path.join(DOCS, "assets", "shaders")


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
    manifest = {
        "source": "weft/runtime/aywa",
        "files": ["moissanite_telemetry.json", "moissanite_telemetry.bin", "telemetry.jsonl"],
        "shader": "assets/shaders/dashboard_layout.wgsl",
    }
    with open(os.path.join(DOCS, "seed-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps({"status": "OK", "docs": DOCS, "manifest": manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
