#!/usr/bin/env python3
"""Offline tests for the no-language colony harness fixes (PR #140 review).

No test here calls a model or an embedding API: urllib.request.urlopen is
replaced with a function that raises, and OPENAI_API_KEY is removed from the
environment. Commands that need macOS sandbox-exec run inside it when it is
installed; otherwise the e4d tests run harness-owned code without isolation.

Run: python3 -m unittest test_nl_offline -v   (from this directory)
"""
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import zlib
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("NOL_STRICT", None)


def _no_network(*a, **k):
    raise AssertionError("network call attempted in an offline test")


urllib.request.urlopen = _no_network

ISOLATE = shutil.which("sandbox-exec") is not None
CORPUS = (HERE / "corpus_hard.txt").read_bytes()

GOOD_CAND = """import zlib
def enc(x):
    return zlib.compress(x, 9)
def dec(y):
    return zlib.decompress(y)
if __name__ == '__main__':
    x = open('x.bin', 'rb').read()
    y = enc(x)
    assert dec(y) == x
    print(100.0 * (1 - len(y) / len(x)))
"""

BROKEN_CAND = GOOD_CAND.replace("return zlib.decompress(y)", "return zlib.decompress(y)[:-1]")


class CorpusTest(unittest.TestCase):
    def test_corpus_is_the_registered_file(self):
        from cellutil import CORPUS_SHA256
        self.assertEqual(hashlib.sha256(CORPUS).hexdigest(), CORPUS_SHA256)
        self.assertEqual(len(CORPUS), 44267)


class E4dScoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e4d = importlib.import_module("e4d")

    def test_import_needs_no_key_and_corpus_exists(self):
        self.assertTrue(self.e4d.CORPUS.exists())

    def test_sandbox_stages_files(self):
        out = self.e4d.sandbox("wc -c < x.bin; cat cand.py", files={"x.bin": CORPUS, "cand.py": "zz"},
                               isolate=ISOLATE)
        self.assertTrue(out.startswith("exit 0"), out)
        self.assertIn("44267", out)
        self.assertIn("zz", out)

    def test_score_body_round_trips_staged_cand(self):
        want = 100.0 * (1 - len(zlib.compress(CORPUS, 9)) / len(CORPUS))
        got = self.e4d.score_body(GOOD_CAND, CORPUS, isolate=ISOLATE)
        self.assertAlmostEqual(got, want, places=6)
        obj = self.e4d.roundtrip_objective(GOOD_CAND, CORPUS, isolate=ISOLATE)
        self.assertAlmostEqual(obj, want, places=6)

    def test_broken_decoder_scores_zero(self):
        self.assertEqual(self.e4d.score_body(BROKEN_CAND, CORPUS, isolate=ISOLATE), 0.0)
        self.assertIsNone(self.e4d.roundtrip_objective(BROKEN_CAND, CORPUS, isolate=ISOLATE))

    def test_constant_print_is_not_an_objective(self):
        const = "def enc(x):\n    return x\ndef dec(y):\n    return y\nprint(42)\n"
        self.assertEqual(self.e4d.score_body(const, CORPUS, isolate=ISOLATE), 42.0)
        self.assertAlmostEqual(self.e4d.roundtrip_objective(const, CORPUS, isolate=ISOLATE), 0.0, places=6)

    def test_isolate_fails_closed_without_sandbox_exec(self):
        with mock.patch.object(self.e4d.shutil, "which", return_value=None):
            self.assertEqual(self.e4d.sandbox("echo 1", isolate=True), "!sandbox-exec")


def _load_harness():
    with mock.patch.object(sys, "argv", ["harness_nl.py", "offline-test", "offline-cell"]):
        sys.modules.pop("harness_nl", None)
        return importlib.import_module("harness_nl")


class DoVariantsVerificationTest(unittest.TestCase):
    def setUp(self):
        self.h = _load_harness()
        self.cell = Path(tempfile.mkdtemp(prefix="nl-test-"))
        self.events = []

    def tearDown(self):
        shutil.rmtree(self.cell, ignore_errors=True)

    def log(self, kind, obj):
        self.events.append((kind, obj))

    def run_with(self, assays, incumbent="INC"):
        if incumbent is not None:
            (self.cell / "f.py").write_text(incumbent)
        seq = iter(assays)
        with mock.patch.object(self.h, "run_assay", lambda cell: next(seq)):
            return self.h.do_variants(self.cell, self.log, "f.py", ["WIN"])

    @staticmethod
    def a(med, ok=True):
        return {"scores": [med] * 3, "median": med, "spread": 0.0, "ok": ok}

    def result_event(self):
        return [o for k, o in self.events if k == "variants_result"][-1]

    def test_verified_win_is_adopted(self):
        r = self.run_with([self.a(50.0), self.a(60.0), self.a(60.0)])
        self.assertTrue(r.startswith("✓"), r)
        self.assertEqual((self.cell / "f.py").read_text(), "WIN")
        ev = self.result_event()
        self.assertEqual(ev["adopted"], 0)
        self.assertFalse(ev["verification_failed"])

    def test_failed_after_assay_restores_incumbent_and_is_not_a_win(self):
        r = self.run_with([self.a(50.0), self.a(60.0), self.a(60.0, ok=False)])
        self.assertFalse(r.startswith("✓"), r)
        self.assertEqual((self.cell / "f.py").read_text(), "INC")
        ev = self.result_event()
        self.assertIsNone(ev["adopted"])
        self.assertFalse(ev["after_ok"])
        self.assertTrue(ev["verification_failed"])

    def test_regressed_after_assay_restores_incumbent(self):
        r = self.run_with([self.a(50.0), self.a(60.0), self.a(49.0)])
        self.assertFalse(r.startswith("✓"), r)
        self.assertEqual((self.cell / "f.py").read_text(), "INC")

    def test_missing_after_assay_is_not_a_win(self):
        r = self.run_with([self.a(50.0), self.a(60.0), None])
        self.assertFalse(r.startswith("✓"), r)
        self.assertEqual((self.cell / "f.py").read_text(), "INC")

    def test_result_strings_stay_english_free(self):
        import profiles
        for prof in profiles.PROFILES:
            profiles.channel_block(prof)
            self.assertFalse(profiles.PROFILES[prof]["results"]["variants_unverified"].startswith("✓"))


class StrictModeTest(unittest.TestCase):
    def test_strict_fails_closed_when_checker_missing(self):
        code = ("import sys; sys.modules['strict_tools'] = None; "
                "sys.argv = ['harness_nl.py', 'offline-test', 'offline-cell']; "
                "import runpy; runpy.run_path('harness_nl.py', run_name='not_main')")
        env = dict(os.environ, NOL_STRICT="1")
        env.pop("OPENAI_API_KEY", None)
        p = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("NOL_STRICT=1 but strict_tools could not be imported", p.stderr)

    def test_strict_imports_vendored_checker(self):
        code = ("import sys; sys.argv = ['harness_nl.py', 'offline-test', 'offline-cell']; "
                "import runpy; g = runpy.run_path('harness_nl.py', run_name='not_main'); "
                "print(g['STRICT'], g['strict_body'].__module__)")
        env = dict(os.environ, NOL_STRICT="1")
        env.pop("OPENAI_API_KEY", None)
        p = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("True strict_tools", p.stdout)

    def test_strict_body_identifier_and_bytes_cases(self):
        from strict_tools import strict_body
        rejects = [
            "import lzma as the",
            "from lzma import compress as this",
            "def f(the):\n    return 1",
            "def f(*the):\n    return 1",
            "def f(**the):\n    return 1",
            "f(the=1)",
            "x = b'the body is in the file'",
            "try:\n    pass\nexcept Exception as the:\n    pass",
        ]
        for src in rejects:
            self.assertFalse(strict_body(src)["ok"], src)
        self.assertTrue(strict_body("x = 1 + 2")["ok"])
        self.assertTrue(strict_body("import lzma\ny = lzma.compress(b'ab', preset=9)")["ok"])

    def test_strict_covers_write_and_variants(self):
        h = _load_harness()
        from strict_tools import strict_body
        cell = Path(tempfile.mkdtemp(prefix="nl-test-"))
        events = []
        try:
            with mock.patch.object(h, "STRICT", True), mock.patch.object(h, "strict_body", strict_body, create=True):
                r = h.tool_dispatch(cell, lambda k, o: events.append((k, o)), "w",
                                    {"p": "f.py", "x": "import lzma as the\n"})
                self.assertEqual(r, "!strict")
                self.assertFalse((cell / "f.py").exists())
                (cell / "f.py").write_text("x = 1")
                calls = []

                def fake_assay(c):
                    calls.append((c / "f.py").read_text())
                    return {"scores": [50.0] * 3, "median": 50.0, "spread": 0.0, "ok": True}

                with mock.patch.object(h, "run_assay", fake_assay):
                    h.do_variants(cell, lambda k, o: events.append((k, o)), "f.py", ["def f(the):\n    return 1\n"])
                self.assertNotIn("def f(the):\n    return 1\n", calls)
                self.assertEqual((cell / "f.py").read_text(), "x = 1")
                self.assertTrue(any(k == "strict_reject" for k, _ in events))
        finally:
            shutil.rmtree(cell, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
