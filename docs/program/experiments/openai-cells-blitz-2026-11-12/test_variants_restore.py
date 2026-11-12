#!/usr/bin/env python3
"""Offline regression for do_variants winner restoration.

No API calls. Uses tiny synthetic assays inside a temp cell folder.
Run: python3 test_variants_restore.py

Covers the 2026-11-12 gpt-aeva finding on PR #139:
- scenario 1: winner not the last candidate -> disk must hold the winner,
  assay must pass, log must carry content hash + after scores
- scenario 2: no variant wins -> incumbent bytes restored
- scenario 3: no variant wins and the file did not exist -> file removed
- scenario 4: candidate with one failed assay run ([None, 100, 100]) is
  ineligible; must not be adopted even though its non-None median/min look winning
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "offline-regression-dummy")
sys.argv = ["harness.py", "offline-model", "offline-cell", "compress"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness  # noqa: E402


def mkcell(root):
    cell = Path(root) / "cell"
    cell.mkdir(parents=True)
    (cell / "ASSAY").write_text(
        "python3 -c \"print(98.0 if 'WIN' in open('compress.py').read() else 50.0)\"")
    return cell


def events(logf):
    return [json.loads(l) for l in Path(logf).read_text().splitlines() if l.strip()]


def run_case(name, setup, versions, check):
    root = tempfile.mkdtemp(prefix="variants-reg-")
    try:
        cell, assay = setup(root)
        (cell / "ASSAY").write_text(assay)
        logf = Path(root) / "log.jsonl"

        def log(kind, obj):
            with open(logf, "a") as fh:
                fh.write(json.dumps({"kind": kind, **obj}) + "\n")

        harness.do_variants(cell, log, "compress.py", versions)
        check(cell, events(logf))
        print(f"ok  {name}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    inc = "# incumbent, stable score 50\n" + "x = 1\n" * 10
    win = "# WINNER\n" + "y = 2\n" * 20
    broken = "BROKEN ("

    def setup1(root):
        cell = Path(root) / "cell"
        cell.mkdir()
        (cell / "compress.py").write_text(inc)
        assay = "python3 -c \"print(98.0 if 'WIN' in open('compress.py').read() else 50.0)\""
        return cell, assay

    def check1(cell, evs):
        disk = (cell / "compress.py").read_bytes()
        assert disk == win.encode(), "disk does not hold the selected winner"
        res = [e for e in evs if e["kind"] == "variants_result"][-1]
        assert res["adopted"] == 0
        assert res["content_sha256"] == hashlib.sha256(win.encode()).hexdigest()
        assert res["after_ok"] is True and res["after_median"] == 98.0
        assert res["before_median"] == 50.0

    run_case("winner not last candidate -> winner restored and re-evaluated",
             setup1,
             [win, broken],
             check1)

    def setup2(root):
        cell = Path(root) / "cell"
        cell.mkdir()
        (cell / "compress.py").write_text(inc)
        assay = "python3 -c \"print(10.0 if 'WIN' in open('compress.py').read() else 50.0)\""
        return cell, assay

    def check2(cell, evs):
        assert (cell / "compress.py").read_text() == inc
        res = [e for e in evs if e["kind"] == "variants_result"][-1]
        assert res["adopted"] is None

    run_case("no variant beats incumbent -> incumbent bytes restored",
             setup2,
             ["# weaker 1\n", "# weaker 2\n"],
             check2)

    def setup3(root):
        cell = Path(root) / "cell"
        cell.mkdir()
        assay = "python3 -c \"print(42)\""
        return cell, assay

    def check3(cell, evs):
        assert not (cell / "compress.py").exists(), "original absence not restored"
        res = [e for e in evs if e["kind"] == "variants_result"][-1]
        assert res["adopted"] is None

    run_case("no win and file did not exist -> file removed",
             setup3,
             ["# candidate A\n", "# candidate B\n"],
             check3)

    # candidate whose assay scores [None, 100, 100]: old code silently dropped
    # the failed run and adopted. New code requires r['ok'].
    assay4 = ('python3 -c "'
              "import hashlib,pathlib,sys\n"
              "s = pathlib.Path('compress.py').read_text()\n"
              "if 'FLAKY' not in s:\n"
              "    print(50.0); sys.exit(0)\n"
              "k = hashlib.sha256(s.encode()).hexdigest()[:12]\n"
              "c = pathlib.Path('cnt_' + k)\n"
              "n = int(c.read_text()) if c.exists() else 0\n"
              "c.write_text(str(n + 1))\n"
              "print(100 if n > 0 else 'boom')\n"
              "sys.exit(0 if n > 0 else 1)\"")

    def setup4(root):
        cell = Path(root) / "cell"
        cell.mkdir()
        (cell / "compress.py").write_text(inc)
        return cell, assay4

    def check4(cell, evs):
        assert (cell / "compress.py").read_text() == inc, "ineligible candidate left on disk"
        res = [e for e in evs if e["kind"] == "variants_result"][-1]
        assert res["adopted"] is None
        flaky = [e for e in evs if e["kind"] == "variant"]
        assert flaky and flaky[0]["scores"][0] is None and flaky[0]["ok"] is False

    run_case("failed-run candidate is ineligible (no adopted winner)",
             setup4,
             ["# FLAKY candidate\n"],
             check4)

    print("all regression scenarios pass")


if __name__ == "__main__":
    main()
