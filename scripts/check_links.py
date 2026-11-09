#!/usr/bin/env python3
"""Check repo-relative links in README.md and site/ files.

Reads every link in README.md and in site/**/*.html and site/**/*.md,
keeps the ones that point at a path inside this repo, and fails when a
target file or directory is missing. External links (http, GitHub, w3ft.org),
page anchors, mailto links, and localhost links are skipped: this check
covers repo paths only, so it needs no network and no login.

A path that starts with / is read from the site root (site/) when the
source file is under site/, and from the repo root otherwise. A relative
path is read from the source file's own directory.

Usage: python3 scripts/check_links.py [--root DIR]
Exit 0 when every checked link resolves, 1 otherwise.
"""

import argparse
import html.parser
import os
import re
import sys

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# Schemes and hosts this check does not follow.
SKIP_PREFIXES = (
    "http://",
    "https://",
    "//",
    "mailto:",
    "tel:",
    "data:",
    "javascript:",
    "ftp://",
)


def is_checked_target(target):
    """True when the target is a path inside this repo."""
    if not target:
        return False
    if target.startswith("#"):
        return False
    if target.startswith(SKIP_PREFIXES):
        return False
    return True


def strip_suffix(target):
    """Drop a #fragment or ?query from a link target."""
    return target.split("#", 1)[0].split("?", 1)[0]


class LinkFinder(html.parser.HTMLParser):
    """Collects href/src/srcset values from an HTML file."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append((self.getpos()[0], value))
            elif name == "srcset" and value:
                for part in value.split(","):
                    url = part.strip().split(" ", 1)[0]
                    if url:
                        self.links.append((self.getpos()[0], url))


def links_in_file(path, relpath):
    """Return (line, target) pairs found in one Markdown or HTML file."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    found = []
    if relpath.endswith(".md"):
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in MARKDOWN_LINK.finditer(line):
                found.append((lineno, match.group(1)))
        parser = LinkFinder()
        parser.feed(text)
        found.extend(parser.links)
    else:
        parser = LinkFinder()
        parser.feed(text)
        found.extend(parser.links)
    return found


def resolve(root, source_relpath, target):
    """Resolve a checked target to a path inside the repo, or None."""
    target = strip_suffix(target)
    if not target:
        return None
    if target.startswith("/"):
        base = os.path.join(root, "site") if source_relpath.startswith("site/") else root
        return os.path.normpath(os.path.join(base, target.lstrip("/")))
    source_dir = os.path.dirname(os.path.join(root, source_relpath))
    return os.path.normpath(os.path.join(source_dir, target))


def scan(root):
    """Return (checked, missing) for the links in README and site files."""
    sources = [os.path.join(root, "README.md")]
    site_dir = os.path.join(root, "site")
    for dirpath, _dirnames, filenames in os.walk(site_dir):
        for name in sorted(filenames):
            if name.endswith((".html", ".md")):
                sources.append(os.path.join(dirpath, name))
    checked = 0
    missing = []
    for source in sorted(sources):
        relpath = os.path.relpath(source, root)
        for lineno, target in links_in_file(source, relpath):
            if not is_checked_target(target):
                continue
            checked += 1
            resolved = resolve(root, relpath, target)
            if resolved is None or not os.path.exists(resolved):
                missing.append((relpath, lineno, target))
    return checked, missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None,
                        help="repo root (default: parent of scripts/)")
    args = parser.parse_args(argv)
    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checked, missing = scan(root)
    if missing:
        for relpath, lineno, target in missing:
            print(f"{relpath}:{lineno}: missing target: {target}")
        print(f"Link check failed: {len(missing)} of {checked} links "
              "point at missing targets.")
        return 1
    print(f"Link check passed: {checked} repo links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
