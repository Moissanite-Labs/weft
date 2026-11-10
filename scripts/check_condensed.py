#!/usr/bin/env python3
"""Check condensed.json still matches the overview paper page.

Recomputes the passage keys the browser computes at runtime and fails
when a condensed.json entry matches no passage on the page.

The browser rules, from site/assets/js/attention.js and condense.js:
- passages are `main p` and `main li` elements, except ones inside
  .hero, .paper-hero, pre, code, button, label, form, .demo, figure,
  table, nav, aside or .crumbs, except ones that contain a nested p
  or li, and except ones with fewer than 4 words;
- a passage key is FNV-1a of its text with runs of whitespace collapsed
  to one space and the ends trimmed;
- sections are `article.paper section` elements, keyed by id (or
  "abstract" for the section with that class), each needing 5 headings,
  one TL;DR line and one ELI5 line.

Passages with no condensed.json entry are allowed: back matter is not
condensed by design. The other direction is the failure: a JSON entry
with no passage means the paper changed and the file did not, so that
passage silently stops condensing.

Usage: python3 scripts/check_condensed.py [--page PATH] [--data PATH]
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

NOT_TEXT_TAGS = {"pre", "code", "button", "label", "form", "figure",
                 "table", "nav", "aside"}
NOT_TEXT_CLASSES = {"hero", "paper-hero", "demo", "crumbs"}


def fnv(text):
    """FNV-1a 32-bit, over UTF-16 code units like JS charCodeAt."""
    h = 0x811C9DC5
    raw = text.encode("utf-16-be")
    for i in range(0, len(raw), 2):
        h ^= (raw[i] << 8) | raw[i + 1]
        h = ((h * 0x01000193) & 0xFFFFFFFF)
    return f"{h:08x}"


class Node:
    __slots__ = ("tag", "attrs", "parent", "children", "content")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []
        # Ordered mix of raw text strings and child Nodes, in document
        # order. textContent concatenates them in this order; keeping
        # direct text separate would move it before every child.
        self.content = []

    @property
    def classes(self):
        return set(self.attrs.get("class", "").split())

    def text_content(self):
        out = []
        for part in self.content:
            out.append(part if isinstance(part, str) else part.text_content())
        return "".join(out)


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class TreeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", [], None)
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        self.current.content.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        self.current.content.append(node)

    def handle_endtag(self, tag):
        node = self.current
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.current = node.parent

    def handle_data(self, data):
        self.current.content.append(data)


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def inside_not_text(node):
    n = node
    while n is not None:
        if n.tag in NOT_TEXT_TAGS or n.classes & NOT_TEXT_CLASSES:
            return True
        n = n.parent
    return False


def has_nested_block(node):
    return any(c.tag in ("p", "li") for c in walk(node) if c is not node)


def parse_page(page_path):
    tree = TreeParser()
    tree.feed(Path(page_path).read_text(encoding="utf-8"))
    tree.close()
    return tree.root


def passage_keys(root):
    """Return (keys, block count) computed from the parsed page."""
    mains = [n for n in walk(root) if n.tag == "main"]
    if not mains:
        raise SystemExit("no <main> in the page")
    keys = {}
    blocks = 0
    for el in walk(mains[0]):
        if el.tag not in ("p", "li"):
            continue
        if inside_not_text(el) or has_nested_block(el):
            continue
        text = re.sub(r"\s+", " ", el.text_content()).strip()
        if len(text.split()) < 4:
            continue
        blocks += 1
        keys[fnv(text)] = text[:60]
    return keys, blocks


def section_ids(root):
    ids = []
    for article in walk(root):
        if article.tag != "article" or "paper" not in article.classes:
            continue
        for section in walk(article):
            if section.tag != "section" or section is article:
                continue
            sid = section.attrs.get("id") or (
                "abstract" if "abstract" in section.classes else "")
            if sid:
                ids.append(sid)
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--page", default="site/papers/overview/index.html")
    ap.add_argument("--data", default="site/papers/overview/condensed.json")
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    root = parse_page(args.page)
    page_keys, n_blocks = passage_keys(root)
    page_sections = section_ids(root)

    errors = []
    blocks = data.get("blocks", {})
    for key, versions in blocks.items():
        if key not in page_keys:
            errors.append(f"block {key} matches no passage on the page")
        elif not isinstance(versions, list) or len(versions) != 3:
            errors.append(f"block {key} has {len(versions) if isinstance(versions, list) else 'non-list'} versions, want 3")
    for group in ("headings", "tldr", "eli5"):
        want = set(page_sections)
        got = set(data.get(group, {}))
        for sid in sorted(got - want):
            errors.append(f"{group} has {sid}, no such section on the page")
        # A page section with no entry is allowed: back matter sections
        # such as cite and references have no condensed form by design.
    for sid, heads in data.get("headings", {}).items():
        if not isinstance(heads, list) or len(heads) != 5:
            errors.append(f"headings for {sid} has {len(heads) if isinstance(heads, list) else 'non-list'} entries, want 5")
    for group in ("tldr", "eli5"):
        for sid, line in data.get(group, {}).items():
            if not isinstance(line, str) or not line.strip():
                errors.append(f"{group} for {sid} is not a line of text")

    print(f"condensed.json: {len(blocks)} blocks, {len(page_keys)} passage keys "
          f"from {n_blocks} page blocks, {len(page_sections)} sections")
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("OK: every condensed.json entry matches the page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
