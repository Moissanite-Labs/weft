#!/usr/bin/env python3
"""Tests for scripts/check_links.py."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_links


def make_tree(files):
    """Create a temp repo root holding {relpath: content}."""
    root = tempfile.mkdtemp()
    for relpath, content in files.items():
        path = os.path.join(root, relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    return root


class CheckLinksTest(unittest.TestCase):
    def test_relative_link_resolves(self):
        root = make_tree({
            "README.md": "See [the plan](docs/program/plan.md).\n",
            "docs/program/plan.md": "plan\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [])

    def test_missing_target_is_reported_with_location(self):
        root = make_tree({
            "README.md": "See [the plan](docs/program/no-such-page.md).\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [("README.md", 1, "docs/program/no-such-page.md")])

    def test_site_root_relative_link_resolves_under_site(self):
        root = make_tree({
            "README.md": "",
            "site/index.html": '<a href="/assets/css/site.css">x</a>\n',
            "site/assets/css/site.css": "x\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [])

    def test_site_root_relative_link_missing_is_reported(self):
        root = make_tree({
            "README.md": "",
            "site/index.html": '<a href="/papers/no-such-paper/">x</a>\n',
            "site/papers/index.html": "x\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(missing, [("site/index.html", 1, "/papers/no-such-paper/")])

    def test_directory_target_counts_as_existing(self):
        root = make_tree({
            "README.md": "Papers live in [papers/](papers/).\n",
            "papers/paper.md": "x\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [])

    def test_external_anchor_and_mailto_links_are_skipped(self):
        root = make_tree({
            "README.md": (
                "[site](https://w3ft.org/papers/)\n"
                "[anchor](#try)\n"
                "[mail](mailto:team@example.org)\n"
                "[doc](docs/a.md)\n"
            ),
            "docs/a.md": "x\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [])

    def test_fragment_and_query_are_stripped_before_the_check(self):
        root = make_tree({
            "README.md": "[doc](docs/a.md#section?x=1)\n",
            "docs/a.md": "x\n",
        })
        checked, missing = check_links.scan(root)
        self.assertEqual(checked, 1)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
