#!/usr/bin/env python3
"""Offline tests for the hardened Flex burn orchestrator (no live API calls)."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent


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
            self.assertLessEqual(snap["spent_usd"], reserved + 1e-12)
            self.assertLessEqual(
                snap["spent_usd"] + ledger.reserved_in_flight_usd,
                1.00 + 1e-12,
            )

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
                self.assertGreater(ledger.reserved_in_flight_usd, 0.0)
                self.assertEqual(ledger.spent_usd, 0.0)
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
                self.assertGreater(ledger.reserved_in_flight_usd, 0.0)
                self.assertEqual(ledger.spent_usd, 0.0)
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


if __name__ == "__main__":
    unittest.main()
