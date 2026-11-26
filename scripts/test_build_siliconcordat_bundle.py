#!/usr/bin/env python3
"""Tests that the weft site_tree pin matches HEAD:site and survives a squash."""

from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bundle = _load("build_siliconcordat_bundle")


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def _init_repo(path: Path) -> str:
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "pin-test")
    _git(path, "config", "user.email", "pin-test@example.com")
    (path / "site").mkdir()
    (path / "site" / "index.html").write_text("<h1>weft</h1>\n", encoding="utf-8")
    _git(path, "add", "site/index.html")
    _git(path, "commit", "-m", "initial site")
    return _git(path, "rev-parse", "HEAD:site").stdout.strip()


def _site_tree(path: Path, rev: str = "HEAD") -> str:
    return _git(path, "rev-parse", f"{rev}:site").stdout.strip()


class BundleAssertWeftPinTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.site_tree = _init_repo(self.root)
        self.patches = [
            mock.patch.object(bundle, "ROOT", self.root),
            mock.patch.object(bundle, "SITE", self.root / "site"),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self) -> None:
        for patch in reversed(self.patches):
            patch.stop()
        self.tmp.cleanup()

    def _pin(self, site_tree: str) -> dict:
        return {"weft": {"site_tree": site_tree}}

    def test_missing_site_tree_exits(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            bundle.assert_weft_pin({"weft": {}})
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("site_tree pin is missing", stderr.getvalue())

    def test_unresolvable_site_tree_exits(self) -> None:
        missing = "0" * 40
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            bundle.assert_weft_pin(self._pin(missing))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("cannot be resolved", stderr.getvalue())
        self.assertIn(missing, stderr.getvalue())

    def test_mismatched_site_tree_exits(self) -> None:
        _git(self.root, "checkout", "-b", "other")
        (self.root / "site" / "index.html").write_text("<h1>other</h1>\n", encoding="utf-8")
        _git(self.root, "add", "site/index.html")
        _git(self.root, "commit", "-m", "other site")
        other_tree = _site_tree(self.root)
        _git(self.root, "checkout", "main")
        self.assertNotEqual(other_tree, self.site_tree)
        # The other tree is still in the object database, but it is not HEAD:site.
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            bundle.assert_weft_pin(self._pin(other_tree))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("does not match the pinned weft site tree", stderr.getvalue())
        self.assertIn(other_tree, stderr.getvalue())
        self.assertIn(self.site_tree, stderr.getvalue())

    def test_matching_site_tree_passes(self) -> None:
        bundle.assert_weft_pin(self._pin(self.site_tree))

    def test_pin_survives_squash_of_a_site_changing_branch(self) -> None:
        # Main is self.site_tree. A branch changes site/ and pins the new tree.
        _git(self.root, "checkout", "-b", "feature")
        (self.root / "site" / "index.html").write_text("<h1>feature</h1>\n", encoding="utf-8")
        _git(self.root, "add", "site/index.html")
        _git(self.root, "commit", "-m", "feature site")
        feature_tip = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        feature_tree = _site_tree(self.root)
        self.assertNotEqual(feature_tree, self.site_tree)
        bundle.assert_weft_pin(self._pin(feature_tree))

        # Squash landing onto main: the branch tip is not an ancestor of the
        # squash commit, but site/ (and the pin) are unchanged, so the check
        # still passes.
        _git(self.root, "checkout", "main")
        _git(self.root, "merge", "--squash", "feature")
        _git(self.root, "commit", "-m", "squash feature")
        squash = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        ancestry = _git(
            self.root, "merge-base", "--is-ancestor", feature_tip, squash, check=False
        )
        self.assertNotEqual(ancestry.returncode, 0)
        self.assertEqual(_site_tree(self.root), feature_tree)
        bundle.assert_weft_pin(self._pin(feature_tree))


if __name__ == "__main__":
    unittest.main()
