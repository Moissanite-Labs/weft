"""Offline regression checks for Weft PR #116 review fixes (no macOS archive, stub Tinker only)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
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


def _load_heldout():
    spec = importlib.util.spec_from_file_location("heldout_audit", HELDOUT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


class FibmodCliRunpyTests(unittest.TestCase):
    FIB_SAMPLE_N = 1000

    def test_cli_only_near_reference(self):
        ha = _load_heldout()
        ha.ALLOW_NO_SANDBOX = True
        rng = __import__("random").Random("heldout-r1-fibmod-20261110")
        full = ha.gen_fibmod(rng)
        inp, exp = full[0]
        nums = [int(x) for x in inp.decode().split()][: self.FIB_SAMPLE_N]
        slim_inp = ("\n".join(map(str, nums)) + "\n").encode()
        slim_exp = ("\n".join(exp.decode().strip().split("\n")[: self.FIB_SAMPLE_N]) + "\n").encode()
        cases = [(slim_inp, slim_exp)]

        with tempfile.TemporaryDirectory() as td:
            ref_dir = Path(td) / "ref-body"
            cli_dir = Path(td) / "cli-body"
            ref_dir.mkdir()
            cli_dir.mkdir()
            (ref_dir / "fibmod.py").write_text(ha.REFERENCE_BODIES["fibmod"][1], encoding="utf-8")
            (cli_dir / "fibmod.py").write_text(_fib_cli_ref_source(), encoding="utf-8")

            t0 = time.perf_counter()
            ref_score, _, ref_path = ha.score_task("fibmod", ref_dir, cases)
            cli_score, _, cli_path = ha.score_task("fibmod", cli_dir, cases)
            wall = time.perf_counter() - t0
            rel = cli_score / ref_score if ref_score else 0.0
            self.assertEqual(cli_path, "cli_runpy")
            self.assertEqual(ref_path, "cli_runpy")
            self.assertGreater(rel, 0.8, f"rel={rel} ref={ref_score} cli={cli_score}")
            # stash measured values for the test run log (not persisted)
            self._rel = rel
            self._wall = wall


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
