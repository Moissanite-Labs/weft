#!/usr/bin/env python3
"""Tests for scripts/build_siliconcordat_cut_bundle.py build contract helpers."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_siliconcordat_cut_bundle",
    ROOT / "scripts" / "build_siliconcordat_cut_bundle.py",
)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build
SPEC.loader.exec_module(build)


class CacheBusterTest(unittest.TestCase):
    def test_busts_local_css_and_js_not_external_or_anchors(self):
        html = (
            '<link rel="stylesheet" href="/tokens.css">'
            '<script type="module" src="/assets/js/site.js"></script>'
            '<a href="https://example.com/x.css">x</a>'
            '<a href="#main">skip</a>'
            '<a href="/ml">lab</a>'
        )
        out = build.apply_cache_busters_to_html(html, "abc123def456")
        self.assertIn('href="/tokens.css?v=abc123def456"', out)
        self.assertIn('src="/assets/js/site.js?v=abc123def456"', out)
        self.assertIn('href="https://example.com/x.css"', out)
        self.assertIn('href="#main"', out)
        self.assertIn('href="/ml"', out)

    def test_idempotent_when_v_query_present(self):
        html = '<link href="/assets/css/site.css?v=deadbeef">'
        out = build.apply_cache_busters_to_html(html, "abc123def456")
        self.assertEqual(out, html)


class ManifestSha256Test(unittest.TestCase):
    def test_manifest_excludes_itself_and_sha256sum_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            build.DIST = dist
            (dist / "index.html").write_text("<!DOCTYPE html>\n", encoding="utf-8")
            (dist / "tokens.css").write_bytes(b"body{}")
            build.write_manifest_sha256()
            manifest = dist / "MANIFEST.sha256"
            self.assertTrue(manifest.is_file())
            body = manifest.read_text(encoding="utf-8")
            self.assertNotIn("MANIFEST.sha256", body.splitlines()[0].split("  ", 1)[-1])
            proc = subprocess.run(
                ["sha256sum", "-c", "MANIFEST.sha256"],
                cwd=dist,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn(": OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
