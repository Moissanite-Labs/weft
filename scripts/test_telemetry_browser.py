#!/usr/bin/env python3
"""Exercise C7's real module worker against a local, changing telemetry endpoint.

Run: python3 scripts/test_telemetry_browser.py
Setup and optional system Chromium: weft/runtime/aywa/BROWSER-TESTS.md
"""

from __future__ import annotations

import hashlib
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
import unittest
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright


DOCS = Path(__file__).resolve().parents[1] / "docs"
NESTED_PREFIX = "/nested/site/"
POLL_MS = 100


def packet(sequence: int, nodes: int, tension: float, gini: float) -> str:
    payload = f"[s-exp (active_nodes {nodes}) (tension {tension}) (gini {gini})]"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f":01:03:{sequence:04d}{payload}{digest}\n"


HARNESS = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Telemetry regression</title></head>
<body><div id="hud"></div><script type="module">
import {{ WeftLoomEngine }} from './assets/js/weft-loom.js';
const engine = new WeftLoomEngine({{
  dataUrl: './data/telemetry.jsonl?channel=browser-test',
  hudEl: document.getElementById('hud'),
}});
window.engine = engine;
await engine.fetchSym2pOnce();
engine.startTelemetryWorker({POLL_MS});
</script></body></html>
"""


class TelemetryServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), partial(Handler, directory=str(DOCS)))
        self.lock = Lock()
        self.status = 200
        self.body = ""
        self.requests: list[str] = []

    def respond_with(self, body: str, status: int = 200) -> None:
        with self.lock:
            self.body, self.status = body, status


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        pass

    def do_GET(self) -> None:
        parts = urlsplit(self.path)
        path = parts.path
        with self.server.lock:
            self.server.requests.append(self.path)
        if path.startswith(NESTED_PREFIX):
            path = "/" + path[len(NESTED_PREFIX):]
        if path == "/harness.html":
            self.send_body(200, HARNESS, "text/html")
        elif path == "/data/telemetry.jsonl":
            # Cache-busting must preserve a caller's existing query parameters.
            query = parse_qs(parts.query)
            if query.get("channel") != ["browser-test"] or "t" not in query:
                self.send_body(400, "Missing telemetry query parameters", "text/plain")
                return
            with self.server.lock:
                body, status = self.server.body, self.server.status
            self.send_body(status, body, "text/plain")
        else:
            self.path = path
            super().do_GET()

    def send_body(self, status: int, body: str, content_type: str) -> None:
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class TelemetryBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("WEFT_BROWSER_EXECUTABLE")
        try:
            cls.browser = cls.playwright.chromium.launch(
                executable_path=executable or None,
                headless=True,
            )
        except Exception:
            cls.playwright.stop()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

    def test_worker_refresh_rejection_and_recovery(self) -> None:
        for prefix in ("/", NESTED_PREFIX):
            with self.subTest(prefix=prefix):
                self.check_endpoint(prefix)

    def check_endpoint(self, prefix: str) -> None:
        server = TelemetryServer()
        server.respond_with(packet(1, 3, 0.1, 0.2))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        page = self.browser.new_page()
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        try:
            page.goto(f"http://127.0.0.1:{server.server_port}{prefix}harness.html")
            self.wait_for_hud(page, "verified (#0001)")

            # This update must arrive through the actual module worker: the
            # harness calls the main-thread fetch only once.
            server.respond_with(packet(2, 7, 0.4, 0.3))
            self.wait_for_hud(page, "verified (#0002)")
            expected = {"active_nodes": 7, "org_tension": 0.4, "gini_index": 0.3}
            self.assertEqual(self.metrics(page), expected)
            self.assertTrue(page.evaluate("engine.worker instanceof Worker"))

            # Corrupt a correctly hashed packet, leaving the old digest intact.
            server.respond_with(packet(3, 99, 0.8, 0.9).replace("0.8", "0.7"))
            self.wait_for_hud(page, "Telemetry rejected")
            self.assertEqual(self.metrics(page), expected)
            self.assertGreater(page.evaluate("engine.state.rejected_packets"), 0)

            server.respond_with("temporarily unavailable", 503)
            self.wait_for_hud(page, "Telemetry unavailable (HTTP 503)")
            self.assertEqual(self.metrics(page), expected)

            server.respond_with("")
            self.wait_for_hud(page, "No telemetry packet in response")
            self.assertEqual(self.metrics(page), expected)

            server.respond_with(packet(4, 11, 0.25, 0.15))
            self.wait_for_hud(page, "verified (#0004)")
            self.assertEqual(self.metrics(page), {"active_nodes": 11, "org_tension": 0.25, "gini_index": 0.15})
            self.assertNotIn("unavailable", page.locator("#hud").inner_text())
            self.assertEqual(page_errors, [])

            with server.lock:
                requests = list(server.requests)
            telemetry_paths = [urlsplit(url).path for url in requests if "telemetry.jsonl" in url]
            self.assertGreaterEqual(len(telemetry_paths), 6)
            self.assertEqual(set(telemetry_paths), {prefix + "data/telemetry.jsonl"})
            self.assertIn(prefix + "assets/workers/telemetry-worker.js", requests)
        finally:
            page.close()
            server.shutdown()
            thread.join()
            server.server_close()

    def wait_for_hud(self, page, text: str) -> None:
        page.wait_for_function(
            "text => document.getElementById('hud').textContent.includes(text)",
            arg=text,
            timeout=10000,
        )

    def metrics(self, page) -> dict:
        return page.evaluate("""() => {
            const { active_nodes, org_tension, gini_index } = engine.state;
            return { active_nodes, org_tension, gini_index };
        }""")


if __name__ == "__main__":
    unittest.main(verbosity=2)
