"""Offline accounting and credential-boundary tests; no network calls."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import api_worker


class WorkerTests(unittest.TestCase):
    def run_worker(self, root, responder, budget="5"):
        request = root / "request.json"
        request.write_text(json.dumps({"model": "gpt-6-astra", "input": "Return four bounded controller genomes."}))
        secret = "sk-" + "offline-test-credential"
        output = io.StringIO()
        args = ["api_worker.py", "--root", str(root), "--budget-usd", budget]
        with patch("sys.argv", args), patch("sys.stdin", io.StringIO(str(request) + "\n" + str(request) + "\n")), patch("getpass.getpass", return_value=secret), patch("urllib.request.urlopen", side_effect=responder) as network, contextlib.redirect_stdout(output):
            api_worker.main()
        return secret, output.getvalue(), network.call_count

    def test_ambiguous_timeout_reserves_and_stops_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret, output, calls = self.run_worker(root, TimeoutError("private timeout detail"))
            entries = [json.loads(line) for line in (root / "api-ledger.jsonl").read_text().splitlines()]
            self.assertEqual(calls, 1)
            self.assertEqual(entries[0]["event"], "reserved")
            self.assertGreater(entries[0]["reservation_usd"], 0)
            self.assertTrue(entries[1]["ambiguous"])
            self.assertNotIn(secret, output)
            self.assertNotIn("private timeout detail", output)
            self.assertTrue(all(secret not in file.read_text() for file in root.iterdir()))

    def test_budget_prevents_request_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, output, calls = self.run_worker(root, AssertionError("network should not be reached"), budget="0.001")
            self.assertEqual(calls, 0)
            self.assertIn("budget_or_call_cap", output)
            self.assertFalse((root / "request.response.json").exists())

    def test_provider_echo_is_redacted_in_artifacts_and_stdout(self):
        secret = "sk-" + "offline-test-credential"
        body = {"status": "completed", "model": "gpt-6-astra", "output": [{"type": "message", "content": [{"type": "output_text", "text": secret}]}], "usage": {"input_tokens": 1, "output_tokens": 1}, "error": {"message": secret}}
        class Response(io.BytesIO):
            status = 200
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, output, calls = self.run_worker(root, lambda *args, **kwargs: Response(json.dumps(body).encode()))
            self.assertEqual(calls, 1)
            self.assertNotIn(secret, output)
            self.assertTrue(all(secret not in file.read_text() for file in root.iterdir()))
            self.assertIn("[REDACTED]", (root / "request.response.json").read_text())

    def test_existing_ledger_cannot_reset_spend(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "api-ledger.jsonl").write_text("{}\n")
            with patch("sys.argv", ["api_worker.py", "--root", str(root)]), patch("getpass.getpass") as prompt:
                with self.assertRaisesRegex(SystemExit, "reconciliation"):
                    api_worker.main()
                prompt.assert_not_called()


if __name__ == "__main__":
    unittest.main()
