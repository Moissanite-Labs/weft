"""Offline regression checks for Weft PR #116 review fixes (no macOS archive, stub Tinker only)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HELDOUT = REPO / "docs/program/experiments/E07/razi-cells-2026-11/code/heldout_audit.py"
TJ3 = REPO / "docs/program/experiments/razi-cells-laws-2026-11/code/adapters/tj3.py"
TJ3_REPORT = REPO / "docs/program/experiments/razi-cells-laws-2026-11/code/adapters/tj3_report.py"


BASELINE_REV = "6c4f04a05684d2db7e0e49e83f9e97f070967efa"
FIB_REL_LO, FIB_REL_HI = 0.65, 1.35
FIB_TIMING_REPEATS = 3
FIB_CASE_N = 250


def _load_heldout():
    return _load_heldout_file(HELDOUT)


def _load_heldout_at_rev(rev: str):
    text = subprocess.check_output(
        ["git", "show", f"{rev}:docs/program/experiments/E07/razi-cells-2026-11/code/heldout_audit.py"],
        cwd=REPO,
    )
    tmp = Path(tempfile.mkdtemp(prefix="heldout-rev-")) / "heldout_audit.py"
    tmp.write_bytes(text)
    return _load_heldout_file(tmp)


def _load_heldout_file(path: Path):
    spec = importlib.util.spec_from_file_location("heldout_audit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _slim_fibmod_cases(ha, n: int = FIB_CASE_N):
    rng = __import__("random").Random("heldout-r1-fibmod-20261110")
    inp, exp = ha.gen_fibmod(rng)[0]
    nums = [int(x) for x in inp.decode().split()][:n]
    slim_inp = ("\n".join(map(str, nums)) + "\n").encode()
    slim_exp = ("\n".join(exp.decode().strip().split("\n")[:n]) + "\n").encode()
    return [(slim_inp, slim_exp)]


def _ref_median_for_path(ha, ref_dir: Path, cases, path: str, repeats: int) -> float:
    vals = [
        ha.score_fibmod(ref_dir, cases, force_path=path)[0]
        for _ in range(repeats)
    ]
    return statistics.median(vals)


def _path_matched_rel(ha, ref_dir: Path, cell_dir: Path, cases, repeats: int = FIB_TIMING_REPEATS):
    _, _, path = ha.score_fibmod(cell_dir, cases)
    ref_path = path if path in ("cli_runpy", "module_callable") else "module_callable"
    ref_med = _ref_median_for_path(ha, ref_dir, cases, ref_path, repeats)
    cell_scores = [ha.score_fibmod(cell_dir, cases)[0] for _ in range(repeats)]
    cell_med = statistics.median(cell_scores)
    rel = cell_med / ref_med if ref_med > 0 else 0.0
    return rel, path, ref_med, cell_med


def _fib_cli_ref_source() -> str:
    return """import sys
M=10**9+7
if __name__ == "__main__":
    n = int(sys.argv[1])
    a,b=0,1
    for bit in bin(n)[2:]:
        c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M
        a,b=(d,(c+d)%M) if bit=="1" else (c,d)
    print(a)
"""


class HeldoutMainTests(unittest.TestCase):
    def test_main_prints_both_tables(self):
        with tempfile.TemporaryDirectory() as home:
            home_p = Path(home)
            archive = home_p / "arch"
            archive.mkdir()
            out = home_p / "out.json"
            lock = home_p / ".bench.lock"
            env = {**os.environ, "HOME": home}
            proc = subprocess.run(
                [
                    sys.executable,
                    str(HELDOUT),
                    "--archive-dir",
                    str(archive),
                    "--out",
                    str(out),
                    "--repeats",
                    "1",
                    "--tasks",
                    "sortints",
                    "--no-sandbox",
                    "--bench-lock",
                    str(lock),
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertIn("HELD-OUT AUDIT SUMMARY", proc.stdout)
            self.assertIn("PER-TASK RELATIVE SCORES", proc.stdout)
            self.assertTrue(out.is_file())

    def test_refuses_unsandboxed_without_flag(self):
        if __import__("shutil").which("sandbox-exec"):
            self.skipTest("sandbox-exec present")
        ha = _load_heldout()
        ha.ALLOW_NO_SANDBOX = False
        with tempfile.TemporaryDirectory() as td:
            body = Path(td)
            with self.assertRaises(ha.SandboxUnavailableError):
                ha.sandboxed_run(body, "true", b"")


def _fib_stdin_main_source() -> str:
    return """import sys
M=10**9+7
def fib(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M
        a,b=(d,(c+d)%M) if bit=="1" else (c,d)
    return a
if __name__ == "__main__":
    print("\\n".join(str(fib(int(x))) for x in sys.stdin.read().split()))
"""


def _fib_exit1_module_source() -> str:
    return """import sys
M=10**9+7
def fib(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M
        a,b=(d,(c+d)%M) if bit=="1" else (c,d)
    return a
if __name__ == "__main__":
    sys.exit(1)
"""


class FibmodPathTests(unittest.TestCase):
    def setUp(self):
        self.ha = _load_heldout()
        self.ha.ALLOW_NO_SANDBOX = True
        self.cases = _slim_fibmod_cases(self.ha)

    def _write_ref(self, td: Path) -> Path:
        ref = Path(td) / "ref"
        ref.mkdir()
        (ref / "fibmod.py").write_text(self.ha.REFERENCE_BODIES["fibmod"][1], encoding="utf-8")
        return ref

    def test_argv_cli_body_cli_runpy_rel(self):
        with tempfile.TemporaryDirectory() as td:
            ref = self._write_ref(td)
            cell = Path(td) / "cli"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_cli_ref_source(), encoding="utf-8")
            rel, path, _, _ = _path_matched_rel(self.ha, ref, cell, self.cases)
            self.assertEqual(path, "cli_runpy")
            self.assertGreaterEqual(rel, FIB_REL_LO)
            self.assertLessEqual(rel, FIB_REL_HI)

    def test_stdin_main_body_module_callable_rel(self):
        with tempfile.TemporaryDirectory() as td:
            ref = self._write_ref(td)
            cell = Path(td) / "stdin"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_stdin_main_source(), encoding="utf-8")
            rel, path, _, _ = _path_matched_rel(self.ha, ref, cell, self.cases)
            self.assertEqual(path, "module_callable")
            self.assertGreaterEqual(rel, FIB_REL_LO)
            self.assertLessEqual(rel, FIB_REL_HI)

    def test_cli_exit1_fallback_module_rel(self):
        with tempfile.TemporaryDirectory() as td:
            ref = self._write_ref(td)
            cell = Path(td) / "exit1"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_exit1_module_source(), encoding="utf-8")
            rel, path, _, _ = _path_matched_rel(self.ha, ref, cell, self.cases)
            self.assertEqual(path, "module_callable")
            self.assertGreaterEqual(rel, FIB_REL_LO)
            self.assertLessEqual(rel, FIB_REL_HI)

    def test_baseline_6c4f04a_stdin_body_does_not_fallback(self):
        old = _load_heldout_at_rev(BASELINE_REV)
        old.ALLOW_NO_SANDBOX = True
        with tempfile.TemporaryDirectory() as td:
            cell = Path(td) / "stdin"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_stdin_main_source(), encoding="utf-8")
            score, why, path = old.score_task("fibmod", cell, self.cases)
        self.assertEqual(score, 0.0)
        self.assertEqual(path, "cli_runpy")
        self.assertIn("wrong output", why)

    def test_baseline_6c4f04a_exit1_mixed_paths_when_compared_to_flat_ref(self):
        old = _load_heldout_at_rev(BASELINE_REV)
        old.ALLOW_NO_SANDBOX = True
        with tempfile.TemporaryDirectory() as td:
            ref = Path(td) / "ref"
            ref.mkdir()
            (ref / "fibmod.py").write_text(old.REFERENCE_BODIES["fibmod"][1], encoding="utf-8")
            cell = Path(td) / "exit1"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_exit1_module_source(), encoding="utf-8")
            ref_score, _, ref_path = old.score_task("fibmod", ref, self.cases)
            cell_score, _, cell_path = old.score_task("fibmod", cell, self.cases)
        self.assertEqual(ref_path, "cli_runpy")
        self.assertEqual(cell_path, "module_callable")
        self.assertNotEqual(ref_path, cell_path)
        bogus_rel = cell_score / ref_score if ref_score else 0
        self.assertTrue(ref_score > 0 and cell_score > 0)
        # Path-matched on current harness should land in band; flat ref on old mix may not.
        with tempfile.TemporaryDirectory() as td:
            ref = Path(td) / "ref"
            ref.mkdir()
            (ref / "fibmod.py").write_text(self.ha.REFERENCE_BODIES["fibmod"][1], encoding="utf-8")
            cell = Path(td) / "exit1"
            cell.mkdir()
            (cell / "fibmod.py").write_text(_fib_exit1_module_source(), encoding="utf-8")
            good_rel, path, _, _ = _path_matched_rel(self.ha, ref, cell, self.cases)
        self.assertEqual(path, "module_callable")
        self.assertGreaterEqual(good_rel, FIB_REL_LO)
        self.assertLessEqual(good_rel, FIB_REL_HI)
        self.assertNotAlmostEqual(bogus_rel, good_rel, delta=0.15, msg=f"bogus={bogus_rel} matched={good_rel}")


class Tj3JsonlRunIdTests(unittest.TestCase):
    def test_rerun_keeps_latest_generations_only(self):
        stub = Path(tempfile.mkdtemp(prefix="tj3-stub-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(stub, ignore_errors=True))
        for sub, content in [
            ("tinker_key.py", "def get():\n    return 'stub'\n"),
            ("tml_renderers/__init__.py", ""),
            ("tml_renderers/renderers.py", """
class Inkling2:
    class _Tok:
        def encode_ordinary(self, s):
            return [1, 2, 3]
    def tokenizer(self):
        return self._Tok()
"""),
        ]:
            p = stub / sub
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content.strip() + "\n")

        tinker_pkg = stub / "tinker"
        tinker_pkg.mkdir()
        (tinker_pkg / "__init__.py").write_text(_STUB_TINKER, encoding="utf-8")
        (tinker_pkg / "types.py").write_text(_STUB_TYPES, encoding="utf-8")

        data = {
            "train": [{"cmd": f"c{i}", "label": "ok" if i % 3 else "fail"} for i in range(100)],
            "test": [{"cmd": f"t{i}", "label": "ok"} for i in range(20)],
            "gate": [{"cmd": f"g{i}", "label": "ok"} for i in range(20)],
        }
        (stub / "data.json").write_text(json.dumps(data))
        out_json = stub / "tj3_s0.json"
        env = {**os.environ, "PYTHONPATH": str(stub)}

        def run_tj3(gens: int) -> None:
            subprocess.run(
                [
                    sys.executable,
                    str(TJ3),
                    "data.json",
                    "tj3_s0.json",
                    "--tag",
                    "tj3",
                    "--seed",
                    "0",
                    "--gens",
                    str(gens),
                    "--arms",
                    "gc,gn,gb,s",
                ],
                cwd=stub,
                env=env,
                check=True,
            )

        run_tj3(4)
        run_tj3(2)
        rep = subprocess.run(
            [sys.executable, str(TJ3_REPORT), str(out_json)],
            capture_output=True,
            text=True,
            cwd=stub,
            check=True,
        )
        m = re.search(r"tag tj3 seed 0 arm gc\s*:\s*(.+)", rep.stdout)
        self.assertIsNotNone(m, rep.stdout)
        gens = re.findall(r"g(\d+):", m.group(1))
        self.assertEqual(gens, ["0", "1"], m.group(1))


_STUB_TYPES = """
class ModelInput:
    def __init__(self, length=10):
        self.length = length
    @staticmethod
    def from_ints(tokens=None):
        return ModelInput(len(tokens or []))
class _W(list):
    def tolist(self):
        return list(self)
class Datum:
    def __init__(self, model_input=None, loss_fn_inputs=None):
        self.model_input = model_input or ModelInput()
        lfi = loss_fn_inputs or {"weights": _W([1.0]), "target_tokens": [1]}
        if isinstance(lfi.get("weights"), list) and not hasattr(lfi["weights"], "tolist"):
            lfi = dict(lfi)
            lfi["weights"] = _W(lfi["weights"])
        self.loss_fn_inputs = lfi
class AdamParams:
    def __init__(self, learning_rate=1e-3):
        self.learning_rate = learning_rate
"""

_STUB_TINKER = """
import types as _t
from . import types

class ServiceClient:
    def create_lora_training_client(self, **kw):
        return TrainingClient(self, "base")
    def create_training_client_from_state(self, name):
        return TrainingClient(self, name)
    def delete_checkpoint(self, name):
        class R:
            def result(self): return True
        return R()

class TrainingClient:
    def __init__(self, sc, state):
        self.sc = sc
    def _out(self):
        class LP:
            def tolist(self): return [0.5] * 5
        class O:
            loss_fn_outputs = [{"logprobs": LP()}]
        class R:
            def result(self): return O()
        return R()
    def forward(self, data, loss):
        return self._out()
    def forward_backward(self, data, loss):
        class FB:
            def result(self):
                class LP:
                    def tolist(self): return [0.1] * 3
                return type("O", (), {"loss_fn_outputs": [{"logprobs": LP()}]})()
        return FB()
    def optim_step(self, params):
        class R:
            def result(self): return None
        return R()
    def save_state(self, name, ttl_seconds=14400, overwrite=True):
        class R:
            def result(self):
                return _t.SimpleNamespace(path=f"path://{name}")
        return R()
"""


if __name__ == "__main__":
    unittest.main()
