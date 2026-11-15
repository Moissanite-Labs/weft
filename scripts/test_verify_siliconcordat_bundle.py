#!/usr/bin/env python3
"""Tests for the w3ft.org host check in verify_siliconcordat_bundle.py."""

from __future__ import annotations

import importlib.util
import io
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


verify = _load("verify_siliconcordat_bundle")


class WeftHrefOkTest(unittest.TestCase):
    def test_accepts_plain_w3ft_org_links(self) -> None:
        for href in (
            "https://w3ft.org/papers/",
            "https://w3ft.org",
            "https://W3FT.ORG/papers/",
            "https://w3ft.org:443/papers/",
        ):
            with self.subTest(href=href):
                self.assertTrue(verify.weft_href_ok(href))

    def test_rejects_look_alike_hosts(self) -> None:
        for href in (
            "https://w3ft.org.evil.com/x",
            "https://evil-w3ft.org/x",
            "https://evil.com/w3ft.org/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))

    def test_rejects_wrong_scheme_or_missing_scheme(self) -> None:
        for href in (
            "http://w3ft.org/x",
            "w3ft.org/x",
            "//w3ft.org/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))


class CheckLabPagesTest(unittest.TestCase):
    def _dist(self, index_html: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dist = Path(tmp.name)
        (dist / "index.html").write_text(index_html, encoding="utf-8")
        (dist / "styles.css").write_text(":root { --gold: #d9c7a0; }\n", encoding="utf-8")
        return dist

    def _patched(self, dist: Path):
        return (
            mock.patch.object(verify, "DIST", dist),
            mock.patch.object(verify, "WEFT", dist / "weft"),
        )

    def test_good_w3ft_links_pass(self) -> None:
        dist = self._dist(
            '<a href="https://w3ft.org/papers/">papers</a>\n'
            '<a href="https://w3ft.org">home</a>\n'
        )
        patches = self._patched(dist)
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        verify.check_lab_pages()

    def test_look_alike_host_fails_and_names_the_href(self) -> None:
        bad = "https://w3ft.org.evil.com/x"
        dist = self._dist(f'<a href="{bad}">papers</a>\n')
        patches = self._patched(dist)
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            verify.check_lab_pages()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn(bad, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
