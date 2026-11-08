#!/usr/bin/env python3
"""Vendor files that live in sibling repositories into site/.

  * Eido design modules from Moissanite-Labs/weft-eido (src/*.js) go to site/assets/js/.
  * The five exported widgets from Moissanite-Labs/weft-corpus
    (weft/browser-sources/widgets/) go to site/widgets/.

site/VENDORED.json records the source repository, the commit copied from and
each file's SHA-256. weft/runtime/aywa/site_selftest.py fails if a vendored
file is edited here, so changes have to go upstream first.

  python3 scripts/vendor.py --eido ../weft-eido --corpus ../weft-corpus
  python3 scripts/vendor.py --check     # verify hashes only (what CI runs)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MANIFEST = SITE / "VENDORED.json"

SOURCES = {
    "eido": {
        "repository": "https://github.com/Moissanite-Labs/weft-eido",
        "files": {
            f"src/{name}.js": f"assets/js/{name}.js"
            for name in ("aesthetic-mixer", "simplex-pad", "cell-layout", "glyph-font")
        },
    },
    "corpus": {
        "repository": "https://github.com/Moissanite-Labs/weft-corpus",
        "files": {
            f"weft/browser-sources/widgets/{stem}{ext}": f"widgets/{stem}{ext}"
            for stem in (
                "01-sdf-laya-kinetic-typography",
                "02-mind-palace-spatial-memory",
                "03-morphogenetic-bioelectric-field",
                "04-neural-cellular-automata",
                "05-interaction-combinator-net",
            )
            for ext in (".html", ".jsx")
        },
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> list[str]:
    manifest = json.loads(MANIFEST.read_text())
    errors = []
    for name, source in manifest["sources"].items():
        for upstream, entry in source["files"].items():
            local = SITE / entry["path"]
            if not local.is_file():
                errors.append(f"missing vendored file site/{entry['path']} (from {name}:{upstream})")
            elif sha256(local) != entry["sha256"]:
                errors.append(
                    f"site/{entry['path']} differs from {name}:{upstream}@{source['commit'][:12]}; "
                    "change it upstream, then run scripts/vendor.py"
                )
    return errors


def vendor(checkouts: dict[str, Path]) -> dict:
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"sources": {}}
    manifest["note"] = "Files copied from sibling repositories. Do not edit here; see scripts/vendor.py."
    for name, checkout in checkouts.items():
        spec = SOURCES[name]
        commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"]).decode().strip()
        files = {}
        for upstream, local in spec["files"].items():
            src = checkout / upstream
            if not src.is_file():
                raise SystemExit(f"{name}: missing {upstream} in {checkout}")
            dst = SITE / local
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            files[upstream] = {"path": local, "sha256": sha256(dst)}
        manifest["sources"][name] = {"repository": spec["repository"], "commit": commit, "files": files}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eido", type=Path, help="path to a Moissanite-Labs/weft-eido checkout")
    parser.add_argument("--corpus", type=Path, help="path to a Moissanite-Labs/weft-corpus checkout")
    parser.add_argument("--check", action="store_true", help="only verify vendored hashes")
    args = parser.parse_args()
    if not args.check:
        checkouts = {k: v for k, v in (("eido", args.eido), ("corpus", args.corpus)) if v}
        if not checkouts:
            parser.error("give --eido and/or --corpus, or --check")
        vendor(checkouts)
    errors = check()
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)
    print(json.dumps({"status": "FAIL" if errors else "PASS"}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
