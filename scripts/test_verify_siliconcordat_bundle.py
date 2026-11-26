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
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec for {name}")
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
            "HTTPS://w3ft.org/papers/",
            "https://w3ft.org:443/papers/",
            "https://w3ft.org/!",
            "https://w3ft.org/~",
            "https://w3ft.org/caf\u00e9",
        ):
            with self.subTest(href=href):
                self.assertTrue(verify.weft_href_ok(href))

    def test_rejects_look_alike_hosts(self) -> None:
        for href in (
            "https://w3ft.org.evil.com/x",
            "https://evil-w3ft.org/x",
            "https://evil.com/w3ft.org/x",
            "https://w3ft.org./x",
            "https://w3ft.org%2f.evil.com/x",
            "https://evil.com%40w3ft.org/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))

    def test_rejects_wrong_scheme_or_missing_scheme(self) -> None:
        for href in (
            "",
            "http://w3ft.org/x",
            "javascript://w3ft.org/%0aalert(1)",
            "w3ft.org/x",
            "//w3ft.org/x",
            "https:w3ft.org/x",
            "https:///w3ft.org/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))

    def test_rejects_backslash_and_userinfo_authority_confusion(self) -> None:
        for href in (
            "https://evil.com\\@w3ft.org/x",
            "https://w3ft.org\\@evil.com/x",
            "https://w3ft.org/papers\\x",
            "https:\\\\w3ft.org/x",
            "https://user:pass@w3ft.org/x",
            "https://user@w3ft.org/x",
            "https://:pass@w3ft.org/x",
            "https://@w3ft.org/x",
            "https://:@w3ft.org/x",
            "https://evil.com:443@w3ft.org/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))

    def test_rejects_malformed_or_non_443_ports_and_ipv6_literals(self) -> None:
        for href in (
            "https://w3ft.org:80/x",
            "https://w3ft.org:442/x",
            "https://w3ft.org:444/x",
            "https://w3ft.org:8443/x",
            "https://w3ft.org:0/x",
            "https://w3ft.org:abc/x",
            "https://w3ft.org:99999/x",
            "https://w3ft.org:-1/x",
            "https://[w3ft.org]/x",
            "https://[::1]/x",
            "https://[::1]:443/x",
            "https://[::1/x",
        ):
            with self.subTest(href=href):
                self.assertFalse(verify.weft_href_ok(href))

    def test_rejects_whitespace_and_control_characters(self) -> None:
        for href in (
            " https://w3ft.org/x",
            "https://w3ft.org/x ",
            "https://w3ft.org/a b",
            "https://w3\tft.org/x",
            "https://w3\nft.org/x",
            "https://w3\rft.org/x",
            "\x00https://w3ft.org/x",
            "\x1fhttps://w3ft.org/x",
            "https://w3ft.org/\x7f",
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

    def test_bad_w3ft_hrefs_fail_closed_and_name_the_href(self) -> None:
        for bad in (
            "https://w3ft.org.evil.com/x",
            "https://evil.com\\@w3ft.org/x",
            "https://user:pass@w3ft.org/x",
            "https://[w3ft.org]/x",
            "https://w3ft.org:abc/x",
            "https://w3ft.org:99999/x",
        ):
            with self.subTest(bad=bad):
                dist = self._dist(f'<a href="{bad}">papers</a>\n')
                stderr = io.StringIO()
                with (
                    mock.patch.object(verify, "DIST", dist),
                    mock.patch.object(verify, "WEFT", dist / "weft"),
                    redirect_stderr(stderr),
                    self.assertRaises(SystemExit) as cm,
                ):
                    verify.check_lab_pages()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn(repr(bad), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
