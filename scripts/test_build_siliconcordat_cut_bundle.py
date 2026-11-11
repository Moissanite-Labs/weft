#!/usr/bin/env python3
"""Tests for scripts/build_siliconcordat_cut_bundle.py build contract helpers."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_siliconcordat_cut_bundle",
    ROOT / "scripts" / "build_siliconcordat_cut_bundle.py",
)
assert SPEC and SPEC.loader
build = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build
SPEC.loader.exec_module(build)

FIXTURE_BUILD_SHA = "cafebabedead"


class CacheBusterTest(unittest.TestCase):
    def test_busts_html_css_and_module_imports(self):
        html = (
            '<link rel="stylesheet" href="/tokens.css">'
            '<script type="module" src="/assets/js/site.js"></script>'
        )
        js = (
            'import "./site.js";\n'
            'import { holdAttention } from "./attention.js";\n'
            'import { loadCondensed } from "./condense.js";\n'
            'const m = await import("./lazy.js");\n'
        )
        css = '@font-face { src: url("/assets/fonts/x.woff2"); }'
        v = FIXTURE_BUILD_SHA
        self.assertIn(f'href="/tokens.css?v={v}"', build.apply_cache_busters_to_html(html, v))
        self.assertIn(f'src="/assets/js/site.js?v={v}"', build.apply_cache_busters_to_html(html, v))
        out_js = build.apply_cache_busters_to_js(js, v)
        self.assertIn(f'from "./condense.js?v={v}"', out_js)
        self.assertIn(f'import("./lazy.js?v={v}")', out_js)
        self.assertIn(f'url("/assets/fonts/x.woff2?v={v}")', build.apply_cache_busters_to_css(css, v))

    def test_idempotent_when_v_query_present(self):
        html = '<link href="/assets/css/site.css?v=deadbeef">'
        self.assertEqual(build.apply_cache_busters_to_html(html, FIXTURE_BUILD_SHA), html)


class ManifestSha256Test(unittest.TestCase):
    def _patch_dist(self, dist: Path) -> None:
        patcher = mock.patch.object(build, "DIST", dist)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_manifest_covers_every_bundle_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            self._patch_dist(dist)
            (dist / "index.html").write_text("<!DOCTYPE html>\n", encoding="utf-8")
            (dist / "tokens.css").write_bytes(b"body{}")
            (dist / ".cut-host").write_text("staging\n", encoding="utf-8")
            (dist / ".assetsignore").write_text(".cut-host\n", encoding="utf-8")
            build.write_manifest_sha256(dist)
            self.assertEqual(build.manifest_listed_paths(dist), build.bundle_file_paths(dist))
            proc = subprocess.run(
                ["sha256sum", "-c", "MANIFEST.sha256"],
                cwd=dist,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class DistIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        env = os.environ.copy()
        env["SILICONCORDAT_CUT_HOST"] = "staging"
        env["SILICONCORDAT_CUT_BUILD_SHA"] = FIXTURE_BUILD_SHA
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_siliconcordat_cut_bundle.py")],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.dist = ROOT / "dist-cut"
        cls.version = FIXTURE_BUILD_SHA[:12]

    def test_no_unversioned_asset_refs_in_dist(self):
        issues = build.find_unversioned_asset_refs(self.dist, self.version)
        self.assertEqual(issues, [])

    def test_papers_js_versions_condense_import(self):
        papers = (self.dist / "weft" / "assets" / "js" / "papers.js").read_text(encoding="utf-8")
        self.assertIn(f'from "./condense.js?v={self.version}"', papers)


if __name__ == "__main__":
    unittest.main()
