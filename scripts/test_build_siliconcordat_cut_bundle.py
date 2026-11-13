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


class StagingHeadersTest(unittest.TestCase):
    def _patch_dist(self, dist: Path) -> None:
        patcher = mock.patch.object(build, "DIST", dist)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_staging_noindex_block_exact_output(self):
        existing = (
            "/weft/assets/*\n"
            "  Cache-Control: public, max-age=3600, must-revalidate\n"
        )
        expected = (
            "/weft/assets/*\n"
            "  Cache-Control: public, max-age=3600, must-revalidate\n"
            "\n"
            "/*\n"
            "  X-Robots-Tag: noindex\n"
        )
        self.assertEqual(build.append_staging_noindex_headers(existing), expected)

    def test_write_staging_headers_preserves_weft_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            self._patch_dist(dist)
            (dist / "_headers").write_text(
                "/weft/assets/*\n"
                "  Cache-Control: public, max-age=3600, must-revalidate\n",
                encoding="utf-8",
            )
            build.write_staging_headers()
            self.assertEqual((dist / "_headers").read_text(encoding="utf-8"), (
                "/weft/assets/*\n"
                "  Cache-Control: public, max-age=3600, must-revalidate\n"
                "\n"
                "/*\n"
                "  X-Robots-Tag: noindex\n"
            ))


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


SPEC_MAIN = importlib.util.spec_from_file_location(
    "build_siliconcordat_bundle",
    ROOT / "scripts" / "build_siliconcordat_bundle.py",
)
assert SPEC_MAIN and SPEC_MAIN.loader
build_main = importlib.util.module_from_spec(SPEC_MAIN)
sys.modules[SPEC_MAIN.name] = build_main
SPEC_MAIN.loader.exec_module(build_main)

UNREACHABLE = "0" * 40


class UnreachablePinTest(unittest.TestCase):
    """An unfetchable weft pin fails the build instead of silently using HEAD (#121 review)."""

    def _env(self, allow):
        env = {k: v for k, v in os.environ.items() if k != "SILICONCORDAT_ALLOW_UNREACHABLE_PIN"}
        if allow:
            env["SILICONCORDAT_ALLOW_UNREACHABLE_PIN"] = "1"
        return mock.patch.dict(os.environ, env, clear=True)

    def test_main_bundle_fails_on_unreachable_pin(self):
        with self._env(False), mock.patch.object(build_main, "ensure_commit", return_value=False):
            with self.assertRaises(SystemExit) as cm:
                build_main.assert_weft_pin({"weft": {"sha": UNREACHABLE}})
        self.assertEqual(cm.exception.code, 1)

    def test_main_bundle_opt_out_builds_from_head(self):
        with self._env(True), mock.patch.object(build_main, "ensure_commit", return_value=False):
            self.assertIsNone(build_main.assert_weft_pin({"weft": {"sha": UNREACHABLE}}))

    def test_cut_bundle_fails_on_unreachable_pin(self):
        with self._env(False), mock.patch.object(build, "ensure_commit", return_value=False):
            for fn in (build.log_weft_pin, build.site_source_tree):
                with self.assertRaises(SystemExit) as cm:
                    fn({"weft": {"sha": UNREACHABLE}})
                self.assertEqual(cm.exception.code, 1, fn.__name__)

    def test_cut_bundle_opt_out_uses_local_site(self):
        with self._env(True), mock.patch.object(build, "ensure_commit", return_value=False):
            self.assertIsNone(build.log_weft_pin({"weft": {"sha": UNREACHABLE}}))
            self.assertEqual(build.site_source_tree({"weft": {"sha": UNREACHABLE}}), build.SITE)

    def test_reachable_pin_on_main_still_passes(self):
        manifest = __import__("json").loads((ROOT / "siliconcordat" / "sources-manifest.json").read_text())
        with self._env(False):
            self.assertIsNone(build_main.assert_weft_pin(manifest))


if __name__ == "__main__":
    unittest.main()
