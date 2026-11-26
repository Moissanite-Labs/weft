#!/usr/bin/env python3
"""Keep research records out of the build repository.

weft holds code, CI, the site, the papers and the program documents. Experiment
records, audits, incident write-ups and design notes live in
Moissanite-Labs/weft-loom. This check reads the tracked tree, so it needs no
history and runs the same on a pull request, a merge group and main.

Exit status: 0 when the tree is clean, 1 when a research path is tracked here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOM = "https://github.com/Moissanite-Labs/weft-loom"

# Directories that belong to weft-loom. Nothing may be tracked under them here.
RESEARCH_DIRS = (
    "docs/program/experiments/",
    "docs/program/audit/",
    "experiments/",
    "audit/",
    "incidents/",
    "notes/",
)

# Design notes that stay here because papers, the site self-test or the README
# cite them by path. New design notes go to weft-loom's notes/.
DESIGN_NOTES_DIR = "docs/design-notes/"
KEPT_DESIGN_NOTES = frozenset(
    {
        "docs/design-notes/apple-silicon-dissipative-swarm.md",
        "docs/design-notes/constitution-vs-contract.md",
    }
)


def tracked_files(root: Path = ROOT) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True
    ).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def misplaced(paths: list[str]) -> list[str]:
    bad = []
    for path in paths:
        if path.startswith(RESEARCH_DIRS):
            bad.append(path)
        elif path.startswith(DESIGN_NOTES_DIR) and path not in KEPT_DESIGN_NOTES:
            bad.append(path)
    return sorted(bad)


def main() -> int:
    bad = misplaced(tracked_files())
    if not bad:
        print("lane check: no research records tracked in weft")
        return 0
    print(
        f"lane check: {len(bad)} file(s) belong in weft-loom ({LOOM}), not here:",
        file=sys.stderr,
    )
    for path in bad[:50]:
        print(f"  {path}", file=sys.stderr)
    if len(bad) > 50:
        print(f"  ... and {len(bad) - 50} more", file=sys.stderr)
    print(
        "Experiment records go to weft-loom experiments/, audits to audit/, design "
        "notes to notes/. See CONTRIBUTING.md, 'Where things live'.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
