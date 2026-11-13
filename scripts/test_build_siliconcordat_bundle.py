#!/usr/bin/env python3
"""Tests that weft pin checks fail when the pin is missing or off HEAD's history."""

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
cut = _load("build_siliconcordat_cut_bundle")


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
    return _git(path, "rev-parse", "HEAD").stdout.strip()


def _orphan_commit(path: Path) -> str:
    _git(path, "checkout", "--orphan", "orphan-pin")
    (path / "site" / "index.html").write_text("<h1>orphan</h1>\n", encoding="utf-8")
    _git(path, "add", "site/index.html")
    _git(path, "commit", "-m", "orphan site")
    sha = _git(path, "rev-parse", "HEAD").stdout.strip()
    _git(path, "checkout", "main")
    return sha


class _PinMixin:
    module = bundle

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.head = _init_repo(self.root)
        self.patches = [
            mock.patch.object(self.module, "ROOT", self.root),
            mock.patch.object(self.module, "SITE", self.root / "site"),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self) -> None:
        for patch in reversed(self.patches):
            patch.stop()
        self.tmp.cleanup()

    def _pin(self, sha: str) -> dict:
        return {"weft": {"sha": sha}}

    def test_unresolvable_pin_exits(self) -> None:
        missing = "0" * 40
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            self.module.require_weft_pin(missing)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("cannot be resolved", stderr.getvalue())
        self.assertIn(missing, stderr.getvalue())

    def test_pin_not_in_head_history_exits(self) -> None:
        orphan = _orphan_commit(self.root)
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            self.module.require_weft_pin(orphan)
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("is not in HEAD's history", stderr.getvalue())
        self.assertIn(orphan, stderr.getvalue())

    def test_pin_on_head_passes(self) -> None:
        self.module.require_weft_pin(self.head)


class BundleRequireWeftPinTest(_PinMixin, unittest.TestCase):
    module = bundle

    def test_assert_weft_pin_rejects_unresolvable(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            bundle.assert_weft_pin(self._pin("0" * 40))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("cannot be resolved", stderr.getvalue())

    def test_assert_weft_pin_rejects_off_history(self) -> None:
        orphan = _orphan_commit(self.root)
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            bundle.assert_weft_pin(self._pin(orphan))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("is not in HEAD's history", stderr.getvalue())

    def test_assert_weft_pin_accepts_head(self) -> None:
        bundle.assert_weft_pin(self._pin(self.head))


class CutRequireWeftPinTest(_PinMixin, unittest.TestCase):
    module = cut

    def test_site_source_tree_rejects_unresolvable(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            cut.site_source_tree(self._pin("0" * 40))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("cannot be resolved", stderr.getvalue())

    def test_log_weft_pin_rejects_off_history(self) -> None:
        orphan = _orphan_commit(self.root)
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            cut.log_weft_pin(self._pin(orphan))
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("is not in HEAD's history", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
