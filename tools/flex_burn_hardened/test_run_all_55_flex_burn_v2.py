#!/usr/bin/env python3
"""Offline tests for the hardened Flex burn orchestrator (no live API calls)."""
from __future__ import annotations

import importlib.util
import io
import json
import math
import multiprocessing
import os
import sys
import tempfile
import unittest
import unittest.mock
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
SRC = HERE / "run_all_55_flex_burn_v2.py"


def _r5_cross_process_reserve_worker(src: str, ledger_path: str, cap: float, out_path: str) -> None:
    """Real-process worker: try one $16.25 reserve against a shared ledger."""
    import importlib.util
    import json
    import sys
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("flex_burn_v2_r5_worker", src)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["flex_burn_v2_r5_worker"] = mod
    spec.loader.exec_module(mod)
    ledger = mod.MasterSharedBudgetLedger(
        master_cap_usd=cap, ledger_log_path=Path(ledger_path)
    )
    ok, reserved, reason = ledger.try_reserve(
        "weft_111", "gpt-6-astra", "flex", 1_000_000, 100_000
    )
    Path(out_path).write_text(
        json.dumps({"ok": bool(ok), "reserved": float(reserved), "reason": str(reason)}),
        encoding="utf-8",
    )


def load_mod():
    path = HERE / "run_all_55_flex_burn_v2.py"
    spec = importlib.util.spec_from_file_location("flex_burn_v2", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["flex_burn_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


def _ledger(mod, cap: float, path: Path):
    return mod.MasterSharedBudgetLedger(master_cap_usd=cap, ledger_log_path=path)


def _post_json(url: str, payload: dict, token: str | None, timeout: float = 5.0):
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as err:
        return err.code, err.read()


class LiveSpendAndLedgerReloadTests(unittest.TestCase):
    """Item 1: confirm flag plus ledger-file cap reload."""

    def test_live_spend_requires_confirm_flag_even_with_api_key(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            hd = Path(tmp) / "harnesses"
            hd.mkdir()
            for name in mod.HARNESS_FILENAMES.values():
                (hd / name).write_text("#!/usr/bin/env python3\nprint('stub')\n", encoding="utf-8")
            prev = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "sk-test-not-a-real-key-1234567890"
            try:
                rc = mod.main(
                    [
                        "--harnesses-dir",
                        str(hd),
                        "--out-dir",
                        str(Path(tmp) / "out"),
                        "--tracks",
                        "weft_111",
                    ]
                )
            finally:
                if prev is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = prev
        self.assertEqual(rc, 2)

    def test_ledger_reloads_prior_spend_so_second_process_cannot_reuse_full_cap(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master_api_ledger.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "seq": 1,
                        "track": "weft_111",
                        "call_cost_usd": 40.0,
                        "standard_equiv_usd": 80.0,
                        "master_cumulative_spent_usd": 40.0,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            ledger = _ledger(mod, 53.50, path)
            self.assertGreaterEqual(ledger.spent_usd, 40.0 - 1e-9)
            ok, reserved, _reason = ledger.try_reserve(
                "weft_111", "gpt-6-astra", "flex", 1_000_000, 1_000_000
            )
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)
            self.assertLessEqual(
                ledger.spent_usd + ledger.reserved_in_flight_usd,
                53.50 + 1e-12,
            )


class RedactChildOutputTests(unittest.TestCase):
    """Item 3: redact secrets before the child log is written and hashed."""

    def test_child_log_redacts_secrets_before_write_and_hash(self):
        mod = load_mod()
        raw = b"Authorization: Bearer sk-abc1234567890secret\nstatus=ok\n"
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "weft_111.log"
            if hasattr(mod, "write_child_log"):
                mod.write_child_log(log_path, raw)
            else:
                log_path.write_bytes(raw)
            text = log_path.read_text(encoding="utf-8")
            self.assertNotIn("sk-abc1234567890secret", text)
            self.assertIn("[REDACTED_CREDENTIAL]", text)
            digest = __import__("hashlib").sha256(log_path.read_bytes()).hexdigest()
            self.assertEqual(
                digest,
                __import__("hashlib").sha256(text.encode("utf-8")).hexdigest(),
            )


class SettlementAndReservationTests(unittest.TestCase):
    """Item 4: settlement cannot exceed reservation; unresolved calls stay reserved."""

    def test_settlement_cannot_exceed_reservation_or_cap(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = _ledger(mod, 1.00, path)
            ok, reserved, _reason = ledger.try_reserve(
                "weft_111", "gpt-6-luna", "flex", 128, 16
            )
            self.assertTrue(ok)
            self.assertLess(reserved, 1.00)
            ledger.commit_completed_call(
                track_id="weft_111",
                reserved_usd=reserved,
                response_id="resp_overshoot",
                model="gpt-6-astra",
                service_tier="flex",
                input_tokens=1_000_000,
                cached_tokens=0,
                output_tokens=200_000,
                reasoning_tokens=0,
                latency_s=0.01,
            )
            snap = ledger.snapshot()
            # Computed table cost is charged even when it exceeds the reservation.
            self.assertGreater(snap["spent_usd"], reserved)
            self.assertGreater(snap["spent_usd"], 1.00)
            self.assertGreater(snap.get("over_cap_usd", 0.0), 0.0)
            ok2, reserved2, _reason2 = ledger.try_reserve(
                "weft_111", "gpt-6-luna", "flex", 128, 16
            )
            self.assertFalse(ok2)
            self.assertEqual(reserved2, 0.0)

    def test_transport_error_keeps_reservation(self):
        mod = load_mod()

        def boom(_payload, _headers, _timeout):
            raise TimeoutError("upstream timeout")

        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=boom)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {
                        "model": "gpt-6-luna",
                        "service_tier": "flex",
                        "input": "hi",
                        "max_output_tokens": 64,
                    },
                    getattr(proxy, "proxy_token", None),
                )
                self.assertEqual(status, 502)
                self.assertGreater(ledger.spent_usd + ledger.reserved_in_flight_usd, 0.0)
                self.assertTrue((Path(tmp) / "ledger.jsonl").is_file())
                self.assertGreater((Path(tmp) / "ledger.jsonl").stat().st_size, 0)
            finally:
                proxy.stop()

    def test_unparsable_200_keeps_reservation(self):
        mod = load_mod()

        def bad_200(_payload, _headers, _timeout):
            return 200, b"not-json"

        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=bad_200)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {
                        "model": "gpt-6-luna",
                        "service_tier": "flex",
                        "input": "hi",
                        "max_output_tokens": 64,
                    },
                    getattr(proxy, "proxy_token", None),
                )
                self.assertEqual(status, 200)
                self.assertGreater(ledger.spent_usd + ledger.reserved_in_flight_usd, 0.0)
                self.assertTrue((Path(tmp) / "ledger.jsonl").is_file())
                self.assertGreater((Path(tmp) / "ledger.jsonl").stat().st_size, 0)
            finally:
                proxy.stop()

    def test_reserved_max_output_tokens_is_forwarded(self):
        mod = load_mod()
        captured = {}

        def capture(payload, _headers, _timeout):
            captured["payload"] = payload
            body = {
                "id": "resp_fwd",
                "service_tier": "flex",
                "usage": {
                    "input_tokens": 10,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens": 4,
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            }
            return 200, json.dumps(body).encode("utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=capture)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {"model": "gpt-6-luna", "service_tier": "flex", "input": "hi"},
                    getattr(proxy, "proxy_token", None),
                )
                self.assertEqual(status, 200)
                self.assertIn("max_output_tokens", captured.get("payload") or {})
                self.assertGreater(int(captured["payload"]["max_output_tokens"]), 0)
            finally:
                proxy.stop()


class PricingTests(unittest.TestCase):
    """Item 5: cache-write and long-context rates; unknown models fail closed."""

    def test_unknown_model_fails_closed_without_astra_fallback(self):
        mod = load_mod()
        with self.assertRaises((ValueError, KeyError, TypeError)):
            cost, _std = mod.compute_exact_cost_usd(
                "gpt-5.6-sol", "flex", 1_000_000, 0, 0
            )
            # If the call does not raise, it must not have billed Astra flex input at $5.
            self.assertNotAlmostEqual(cost, 5.00, places=4)
            raise AssertionError("unknown model was priced instead of failing closed")
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            ok, reserved, _reason = ledger.try_reserve(
                "weft_111", "gpt-5.6-sol", "flex", 1_000_000, 0
            )
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)
            self.assertEqual(ledger.reserved_in_flight_usd, 0.0)

    def test_cache_write_and_long_context_rates(self):
        mod = load_mod()
        kwargs_30m = {}
        kwargs_long = {}
        try:
            _cost, std_write = mod.compute_exact_cost_usd(
                "gpt-6-astra",
                "standard",
                200_000,
                0,
                0,
                cache_write_30m_tokens=200_000,
            )
            kwargs_30m["worked"] = True
        except TypeError:
            _cost, std_write = mod.compute_exact_cost_usd(
                "gpt-6-astra", "standard", 1_000_000, 0, 0
            )
            kwargs_30m["worked"] = False
        self.assertTrue(kwargs_30m["worked"])
        self.assertAlmostEqual(std_write, 200_000 * 12.50 / 1_000_000.0, places=6)

        try:
            _cost, std_long = mod.compute_exact_cost_usd(
                "gpt-6-astra", "standard", 272_001, 0, 0
            )
            kwargs_long["worked"] = True
        except TypeError:
            kwargs_long["worked"] = False
            std_long = 0.0
        self.assertTrue(kwargs_long["worked"])
        self.assertAlmostEqual(std_long, 272_001 * 20.00 / 1_000_000.0, places=6)

        _cost, std_short = mod.compute_exact_cost_usd(
            "gpt-6-astra", "flex", 200_000, 0, 0
        )
        self.assertAlmostEqual(std_short, 200_000 * 10.00 / 1_000_000.0, places=6)
        self.assertAlmostEqual(_cost, 200_000 * 5.00 / 1_000_000.0, places=6)

        cost_long_flex, std_long_1m = mod.compute_exact_cost_usd(
            "gpt-6-astra", "flex", 1_000_000, 0, 0
        )
        self.assertAlmostEqual(std_long_1m, 20.00, places=6)
        self.assertAlmostEqual(cost_long_flex, 10.00, places=6)


class TokenAndProxyAuthTests(unittest.TestCase):
    """Item 6: reject non-positive max_output_tokens; proxy has its own token."""

    def test_negative_max_output_tokens_is_rejected(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            ok, reserved, _reason = ledger.try_reserve(
                "weft_111", "gpt-6-astra", "flex", 128, -(10**9)
            )
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)
            self.assertEqual(ledger.reserved_in_flight_usd, 0.0)

            def ok_up(_payload, _headers, _timeout):
                raise AssertionError("upstream should not be called for a negative max_output_tokens")

            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=ok_up)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {
                        "model": "gpt-6-astra",
                        "service_tier": "flex",
                        "input": "hi",
                        "max_output_tokens": -(10**9),
                    },
                    getattr(proxy, "proxy_token", None),
                )
                self.assertEqual(status, 400)
                self.assertEqual(ledger.reserved_in_flight_usd, 0.0)
            finally:
                proxy.stop()

    def test_proxy_rejects_requests_without_its_own_token(self):
        mod = load_mod()
        called = {"n": 0}

        def up(_payload, _headers, _timeout):
            called["n"] += 1
            return 200, b"{}"

        with tempfile.TemporaryDirectory() as tmp:
            ledger = _ledger(mod, 53.50, Path(tmp) / "ledger.jsonl")
            self.assertTrue(hasattr(mod.SharedLedgerProxyServer, "__init__"))
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=up)
            self.assertTrue(getattr(proxy, "proxy_token", ""))
            port = proxy.start()
            try:
                status_no_tok, _ = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {"model": "gpt-6-luna", "service_tier": "flex", "input": "hi", "max_output_tokens": 16},
                    None,
                )
                status_wrong, _ = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {"model": "gpt-6-luna", "service_tier": "flex", "input": "hi", "max_output_tokens": 16},
                    "sk-caller-not-the-proxy-token",
                )
                self.assertEqual(status_no_tok, 401)
                self.assertEqual(status_wrong, 401)
                self.assertEqual(called["n"], 0)
            finally:
                proxy.stop()


class SelftestMissingScriptsTests(unittest.TestCase):
    """Item 7: missing sibling scripts exit non-zero without an uncaught traceback."""

    def test_selftest_missing_siblings_exits_nonzero(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            buf = io.StringIO()
            import sys

            prev = sys.stderr
            try:
                sys.stderr = buf
                rc = mod.main(["--selftest", "--harnesses-dir", tmp])
            except FileNotFoundError:
                self.fail("run_selftest raised FileNotFoundError instead of exiting non-zero")
            finally:
                sys.stderr = prev
        self.assertEqual(rc, 1)
        err = buf.getvalue()
        self.assertIn("weft_111_flex_harness.py", err)


class ProofR2MoneySafetyTests(unittest.TestCase):
    """R2 scenarios from review 5886504774: charge table cost, persist unresolved holds."""

    def test_settlement_charges_computed_cost_and_blocks_later_reserve(self):
        """$1 cap, 2M-input Astra flex 200: computed $20.00375 must be spent, not the $0.0033 reserve."""
        mod = load_mod()

        def huge_200(_payload, _headers, _timeout):
            body = {
                "id": "resp_oversize",
                "service_tier": "flex",
                "usage": {
                    "input_tokens": 2_000_000,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens": 100,
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            }
            return 200, json.dumps(body).encode("utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master_api_ledger.jsonl"
            ledger = _ledger(mod, 1.00, path)
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=huge_200)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {
                        "model": "gpt-6-astra",
                        "service_tier": "flex",
                        "input": "hi",
                        "max_output_tokens": 100,
                    },
                    getattr(proxy, "proxy_token", None),
                )
            finally:
                proxy.stop()
            self.assertEqual(status, 200)
            computed, _std = mod.compute_exact_cost_usd(
                "gpt-6-astra", "flex", 2_000_000, 0, 100
            )
            self.assertAlmostEqual(computed, 20.00375, places=6)
            self.assertAlmostEqual(ledger.spent_usd, 20.00375, places=6)
            entries = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertTrue(entries)
            last = entries[-1]
            self.assertAlmostEqual(float(last["call_cost_usd"]), 20.00375, places=6)
            self.assertAlmostEqual(float(last["computed_call_cost_usd"]), 20.00375, places=6)
            self.assertAlmostEqual(float(last["master_cumulative_spent_usd"]), 20.00375, places=6)
            self.assertGreater(float(last.get("overrun_usd", 0.0)), 0.0)
            ok, reserved, _reason = ledger.try_reserve(
                "weft_111", "gpt-6-astra", "flex", 128, 36_000
            )
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)
            reloaded = _ledger(mod, 1.00, path)
            self.assertAlmostEqual(reloaded.spent_usd, 20.00375, places=6)
            ok2, reserved2, _reason2 = reloaded.try_reserve(
                "weft_111", "gpt-6-astra", "flex", 128, 36_000
            )
            self.assertFalse(ok2)
            self.assertEqual(reserved2, 0.0)

    def test_unresolved_hold_persists_and_reload_refuses_16_25_reserve(self):
        """A transport timeout (and an unparsable 200) must land in the ledger so reload refuses $16.25."""
        mod = load_mod()

        def boom(_payload, _headers, _timeout):
            raise TimeoutError("upstream timeout")

        def bad_200(_payload, _headers, _timeout):
            return 200, b"not-json"

        def _sixteen_25(ledger):
            return ledger.try_reserve(
                "weft_111", "gpt-6-astra", "flex", 1_000_000, 100_000
            )

        with tempfile.TemporaryDirectory() as tmp:
            # Confirm the $16.25 figure itself on a clean $16.25 cap.
            probe_path = Path(tmp) / "probe.jsonl"
            probe = _ledger(mod, 16.25, probe_path)
            ok_probe, reserved_probe, _ = _sixteen_25(probe)
            self.assertTrue(ok_probe)
            self.assertAlmostEqual(reserved_probe, 16.25, places=6)

            for name, upstream in (("transport", boom), ("unparsable_200", bad_200)):
                path = Path(tmp) / f"{name}.jsonl"
                ledger = _ledger(mod, 16.25, path)
                proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=upstream)
                port = proxy.start()
                try:
                    _status, _body = _post_json(
                        f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                        {
                            "model": "gpt-6-luna",
                            "service_tier": "flex",
                            "input": "hi",
                            "max_output_tokens": 64,
                        },
                        getattr(proxy, "proxy_token", None),
                    )
                finally:
                    proxy.stop()
                self.assertGreater(ledger.spent_usd + ledger.reserved_in_flight_usd, 0.0)
                self.assertTrue(path.is_file() and path.stat().st_size > 0)
                reloaded = _ledger(mod, 16.25, path)
                self.assertGreater(reloaded.spent_usd + reloaded.reserved_in_flight_usd, 0.0)
                ok, reserved, _reason = _sixteen_25(reloaded)
                self.assertFalse(ok, msg=f"{name}: reload accepted the $16.25 reserve")
                self.assertEqual(reserved, 0.0)


class ProofR3LedgerSafetyTests(unittest.TestCase):
    """R3 scenarios from review 5886618309: reject bad amounts, close a torn ledger."""

    def _sixteen_25(self, mod, ledger):
        return ledger.try_reserve(
            "weft_111", "gpt-6-astra", "flex", 1_000_000, 100_000
        )

    def test_negative_output_tokens_keeps_hold_and_refuses_16_25(self):
        """A 200 with output_tokens -1000000 must not lower spent, and must block a $16.25 reserve."""
        mod = load_mod()

        def neg_out(_payload, _headers, _timeout):
            body = {
                "id": "resp_neg_out",
                "service_tier": "flex",
                "usage": {
                    "input_tokens": 128,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens": -1_000_000,
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            }
            return 200, json.dumps(body).encode("utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master_api_ledger.jsonl"
            ledger = _ledger(mod, 16.25, path)
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=neg_out)
            port = proxy.start()
            try:
                status, _body = _post_json(
                    f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                    {
                        "model": "gpt-6-astra",
                        "service_tier": "flex",
                        "input": "hi",
                        "max_output_tokens": 100,
                    },
                    getattr(proxy, "proxy_token", None),
                )
            finally:
                proxy.stop()
            self.assertEqual(status, 200)
            self.assertTrue(math.isfinite(ledger.spent_usd))
            self.assertGreaterEqual(ledger.spent_usd, 0.0)
            self.assertGreater(ledger.spent_usd + ledger.reserved_in_flight_usd, 0.0)
            ok, reserved, _reason = self._sixteen_25(mod, ledger)
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)
            reloaded = _ledger(mod, 16.25, path)
            self.assertTrue(math.isfinite(reloaded.spent_usd))
            self.assertGreaterEqual(reloaded.spent_usd, 0.0)
            ok2, reserved2, _reason2 = self._sixteen_25(mod, reloaded)
            self.assertFalse(ok2)
            self.assertEqual(reserved2, 0.0)

    def test_commit_unresolved_hold_rejects_nan_and_negative(self):
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = _ledger(mod, 16.25, path)
            prior = ledger.spent_usd
            ledger.commit_unresolved_hold("weft_111", float("nan"), reason="probe_nan")
            self.assertEqual(ledger.spent_usd, prior)
            self.assertTrue(math.isfinite(ledger.spent_usd))
            ledger.commit_unresolved_hold("weft_111", -25.0, reason="probe_neg")
            self.assertEqual(ledger.spent_usd, prior)
            self.assertGreaterEqual(ledger.spent_usd, 0.0)
            if path.is_file():
                raw = path.read_text(encoding="utf-8")
                self.assertNotIn("NaN", raw)
                for line in raw.splitlines():
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    for key, val in entry.items():
                        if isinstance(val, (int, float)):
                            self.assertTrue(math.isfinite(float(val)), msg=f"{key}={val}")
                            if "usd" in key or key.endswith("_usd"):
                                self.assertGreaterEqual(float(val), 0.0, msg=f"{key}={val}")

    def test_truncated_ledger_line_closes_cap(self):
        """A torn last line must close the cap so a $16.25 reserve is refused after reload."""
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = _ledger(mod, 16.25, path)
            ok, reserved, _ = self._sixteen_25(mod, ledger)
            self.assertTrue(ok)
            self.assertAlmostEqual(reserved, 16.25, places=6)
            ledger.commit_unresolved_hold("weft_111", reserved, reason="probe_hold")
            data = path.read_bytes()
            self.assertGreater(len(data), 40)
            path.write_bytes(data[:40])
            reloaded = _ledger(mod, 16.25, path)
            ok2, reserved2, _reason2 = self._sixteen_25(mod, reloaded)
            self.assertFalse(ok2)
            self.assertEqual(reserved2, 0.0)

    def test_ledger_append_error_returns_502_and_keeps_hold(self):
        mod = load_mod()

        def boom(_payload, _headers, _timeout):
            raise TimeoutError("upstream timeout")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = _ledger(mod, 16.25, path)
            proxy = mod.SharedLedgerProxyServer(ledger=ledger, upstream_fn=boom)
            real_open = Path.open

            def wrapped(self, *args, **kwargs):
                mode = args[0] if args else kwargs.get("mode", "r")
                if Path(self) == path and "a" in str(mode):
                    raise OSError("disk full")
                return real_open(self, *args, **kwargs)

            port = proxy.start()
            try:
                with unittest.mock.patch.object(Path, "open", wrapped):
                    status, _body = _post_json(
                        f"http://127.0.0.1:{port}/t/weft_111/v1/responses",
                        {
                            "model": "gpt-6-luna",
                            "service_tier": "flex",
                            "input": "hi",
                            "max_output_tokens": 64,
                        },
                        getattr(proxy, "proxy_token", None),
                    )
            finally:
                proxy.stop()
            self.assertEqual(status, 502)
            self.assertGreater(ledger.spent_usd + ledger.reserved_in_flight_usd, 0.0)
            self.assertTrue(math.isfinite(ledger.spent_usd))
            self.assertGreaterEqual(ledger.spent_usd, 0.0)
            ok, reserved, _reason = self._sixteen_25(mod, ledger)
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)


class ProofR4ReloadDurabilityTests(unittest.TestCase):
    """R4 scenarios from review 5886722464: durable cap close, monotonic cumulative."""

    def _sixteen_25(self, mod, ledger):
        return ledger.try_reserve(
            "weft_111", "gpt-6-astra", "flex", 1_000_000, 100_000
        )

    def _sixteen_2125(self, mod, ledger):
        return ledger.try_reserve(
            "weft_111", "gpt-6-astra", "flex", 1_000_000, 99_000
        )

    def test_durable_cap_closed_survives_deleted_renamed_or_empty_ledger(self):
        """After a torn line closes the cap, unlink, rename, or an empty replacement still refuses $16.25."""
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "ledger.jsonl"
            ledger = _ledger(mod, 16.25, path)
            ok, reserved, _ = self._sixteen_25(mod, ledger)
            self.assertTrue(ok)
            ledger.commit_unresolved_hold("weft_111", reserved, reason="probe_hold")
            data = path.read_bytes()
            self.assertGreater(len(data), 40)
            path.write_bytes(data[:40])
            closed = _ledger(mod, 16.25, path)
            ok_closed, reserved_closed, _ = self._sixteen_25(mod, closed)
            self.assertFalse(ok_closed)
            self.assertEqual(reserved_closed, 0.0)

            path.unlink()
            after_unlink = _ledger(mod, 16.25, path)
            ok_u, reserved_u, _ = self._sixteen_25(mod, after_unlink)
            self.assertFalse(ok_u, msg="deleted ledger accepted the $16.25 reserve")
            self.assertEqual(reserved_u, 0.0)

            path.write_bytes(data[:40])
            renamed = root / "ledger.jsonl.aside"
            path.rename(renamed)
            after_rename = _ledger(mod, 16.25, path)
            ok_r, reserved_r, _ = self._sixteen_25(mod, after_rename)
            self.assertFalse(ok_r, msg="renamed ledger accepted the $16.25 reserve")
            self.assertEqual(reserved_r, 0.0)

            path.write_text("", encoding="utf-8")
            after_empty = _ledger(mod, 16.25, path)
            ok_e, reserved_e, _ = self._sixteen_25(mod, after_empty)
            self.assertFalse(ok_e, msg="empty replacement ledger accepted the $16.25 reserve")
            self.assertEqual(reserved_e, 0.0)

    def test_later_lower_cumulative_does_not_drop_spend(self):
        """A 16.25 line followed by a 0.01 line must not reload as 0.01 spent."""
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            first = {
                "seq": 1,
                "event": "unresolved_hold",
                "reason": "probe_hold",
                "track": "weft_111",
                "call_cost_usd": 16.25,
                "reserved_usd": 16.25,
                "computed_call_cost_usd": 16.25,
                "master_cumulative_spent_usd": 16.25,
                "master_remaining_usd": 0.0,
                "over_cap_usd": 0.0,
            }
            second = {
                "seq": 2,
                "event": "settled",
                "track": "weft_111",
                "call_cost_usd": 0.01,
                "reserved_usd": 0.01,
                "computed_call_cost_usd": 0.01,
                "master_cumulative_spent_usd": 0.01,
                "master_remaining_usd": 16.24,
                "over_cap_usd": 0.0,
            }
            path.write_text(
                json.dumps(first, ensure_ascii=True) + "\n"
                + json.dumps(second, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )
            reloaded = _ledger(mod, 16.25, path)
            self.assertGreaterEqual(reloaded.spent_usd, 16.25 - 1e-9)
            ok, reserved, _reason = self._sixteen_2125(mod, reloaded)
            self.assertFalse(ok)
            self.assertEqual(reserved, 0.0)


class ProofR5CrossProcessAndDurabilityTests(unittest.TestCase):
    """R5 scenarios from review 5886806620: locked reserve, marker spent, directory fsync."""

    def _sixteen_25(self, ledger):
        return ledger.try_reserve(
            "weft_111", "gpt-6-astra", "flex", 1_000_000, 100_000
        )

    def test_two_processes_cannot_both_reserve_the_full_cap(self):
        """Two real processes each trying $16.25 on a $16.25 cap: exactly one succeeds."""
        iterations = 50
        src = str(SRC)
        ctx = multiprocessing.get_context("spawn")
        for i in range(iterations):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / "ledger.jsonl"
                out_a = root / "a.json"
                out_b = root / "b.json"
                procs = [
                    ctx.Process(
                        target=_r5_cross_process_reserve_worker,
                        args=(src, str(path), 16.25, str(out_a)),
                    ),
                    ctx.Process(
                        target=_r5_cross_process_reserve_worker,
                        args=(src, str(path), 16.25, str(out_b)),
                    ),
                ]
                for proc in procs:
                    proc.start()
                for proc in procs:
                    proc.join(timeout=15)
                for proc in procs:
                    self.assertEqual(proc.exitcode, 0, msg=f"iteration {i}: worker exit {proc.exitcode}")
                results = []
                for out in (out_a, out_b):
                    self.assertTrue(out.is_file(), msg=f"iteration {i}: missing {out.name}")
                    results.append(json.loads(out.read_text(encoding="utf-8")))
                successes = [row for row in results if row.get("ok")]
                self.assertEqual(
                    len(successes),
                    1,
                    msg=f"iteration {i}: expected exactly one success, got {results!r}",
                )
                reserved = float(successes[0]["reserved"])
                self.assertAlmostEqual(reserved, 16.25, places=6)
                mod = load_mod()
                reloaded = _ledger(mod, 16.25, path)
                self.assertLessEqual(reloaded.spent_usd, 16.25 + 1e-9)
                self.assertAlmostEqual(reloaded.spent_usd, reserved, places=6)

    def test_close_markers_record_the_max_spent(self):
        """A torn line after a $16.25 record must write markers with spent_usd 16.25, not 0."""
        mod = load_mod()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            record = {
                "seq": 1,
                "event": "unresolved_hold",
                "reason": "probe_hold",
                "track": "weft_111",
                "call_cost_usd": 16.25,
                "reserved_usd": 16.25,
                "computed_call_cost_usd": 16.25,
                "master_cumulative_spent_usd": 16.25,
                "master_remaining_usd": 0.0,
                "over_cap_usd": 0.0,
            }
            path.write_text(
                json.dumps(record, ensure_ascii=True) + "\nNOTJSON\n",
                encoding="utf-8",
            )
            ledger = _ledger(mod, 16.25, path)
            self.assertTrue(ledger._cap_closed)
            self.assertGreaterEqual(ledger.spent_usd, 16.25 - 1e-9)
            sibling = Path(str(path) + ".closed")
            directory = path.parent / f".flex_burn_cap_closed.{path.name}"
            for marker in (sibling, directory):
                self.assertTrue(marker.is_file(), msg=f"missing marker {marker}")
                obj = json.loads(marker.read_text(encoding="utf-8"))
                self.assertGreaterEqual(
                    float(obj["spent_usd"]),
                    16.25 - 1e-9,
                    msg=f"{marker.name} recorded spent_usd={obj.get('spent_usd')!r}",
                )

    def test_parent_directory_is_fsynced_after_ledger_creates(self):
        """Creating the jsonl, seen stamp, close markers, or lock must fsync the parent directory."""
        mod = load_mod()
        dir_fds = set()
        fsynced_dir_fds = []
        real_open = os.open
        real_fsync = os.fsync
        real_close = os.close

        def tracking_open(path, flags, *args, **kwargs):
            fd = real_open(path, flags, *args, **kwargs)
            if flags & getattr(os, "O_DIRECTORY", 0):
                dir_fds.add(fd)
            return fd

        def tracking_fsync(fd):
            if fd in dir_fds:
                fsynced_dir_fds.append(fd)
            return real_fsync(fd)

        def tracking_close(fd):
            dir_fds.discard(fd)
            return real_close(fd)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            with unittest.mock.patch.object(mod.os, "open", tracking_open), unittest.mock.patch.object(
                mod.os, "fsync", tracking_fsync
            ), unittest.mock.patch.object(mod.os, "close", tracking_close):
                ledger = _ledger(mod, 16.25, path)
                ok, reserved, _reason = self._sixteen_25(ledger)
                self.assertTrue(ok)
                if not path.is_file():
                    ledger.commit_unresolved_hold("weft_111", reserved, reason="probe_hold")
                ledger._close_cap("probe_dir_fsync")
        self.assertTrue(
            fsynced_dir_fds,
            "parent directory was not fsynced after creating ledger files",
        )


if __name__ == "__main__":
    unittest.main()
