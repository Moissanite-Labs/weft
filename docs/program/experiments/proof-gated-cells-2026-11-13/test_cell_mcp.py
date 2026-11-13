import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cell_mcp import Cell, DEFAULT_WORLD, MCPServer, PROTOCOL_VERSION, canonical, strict_json


class CellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "run"
        self.cell = Cell(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, delta):
        return {"expected_state_id": self.cell.inspect()["state_id"], "delta": delta}

    def test_real_proof_commit_restart_and_stale_rejection(self):
        old = self.cell.inspect()
        event = self.cell.propose(self.request([1, -1, 0]))
        self.assertTrue(event["accepted"])
        self.assertEqual(event["proof"]["axioms"], [])
        restarted = Cell(self.path)
        self.assertEqual(restarted.inspect()["weights"], [4, 0, 5])
        self.assertEqual(restarted.inspect()["anchor_outputs"], old["anchor_outputs"])
        stale = restarted.propose({"expected_state_id": old["state_id"], "delta": [1, -1, 0]})
        self.assertEqual(stale["reason"], "stale_state")
        self.assertEqual(restarted.inspect()["revision"], 1)
        self.assertEqual(len(restarted.events()), 2)

    def test_lean_checked_rejections_preserve_state(self):
        before = self.cell.inspect()
        for delta in ([1, 0, 0], [0, 0, 1], [3, -3, 0]):
            with self.subTest(delta=delta):
                event = self.cell.propose(self.request(delta))
                self.assertFalse(event["accepted"])
                self.assertTrue(event["proof"]["kernel_checked"])
                self.assertEqual(event["proof"]["axioms"], [])
        self.assertEqual(self.cell.inspect()["state_id"], before["state_id"])
        self.assertEqual(len(self.cell.events()), 3)

    def test_protocol_and_schema_do_not_expose_code_execution(self):
        server = MCPServer(self.cell)
        early = server.dispatch({"jsonrpc": "2.0", "id": 0, "method": "tools/list"})
        self.assertIn("error", early)
        server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                         "params": {"protocolVersion": PROTOCOL_VERSION}})
        server.dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"})
        response = server.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "cell_propose", "arguments": {**self.request([1, -1, 0]), "proof": "by sorry"}}})
        self.assertTrue(response["result"]["isError"])
        self.assertEqual(response["result"]["structuredContent"]["reason"], "schema_rejected")
        for delta in ([True, -1, 0], [1.0, -1, 0], [1, -1], [100000, -100000, 0]):
            self.assertEqual(self.cell.propose(self.request(delta))["reason"], "integer_delta_required")
        before_events = len(self.cell.events())
        self.assertIsNone(server.dispatch({"jsonrpc": "2.0", "method": "tools/call", "params": {
            "name": "cell_propose", "arguments": self.request([1, -1, 0])}}))
        self.assertEqual(len(self.cell.events()), before_events)

    def test_two_writers_cannot_commit_same_expected_state(self):
        other = Cell(self.path)
        request = self.request([1, -1, 0])
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda cell: cell.propose(request), (self.cell, other)))
        self.assertEqual(sum(item["accepted"] for item in results), 1)
        self.assertEqual(sorted(str(item["reason"]) for item in results), ["None", "stale_state"])
        self.assertEqual(self.cell.inspect()["weights"], [4, 0, 5])

    def test_restart_rejects_changed_rules_and_corrupt_certificate(self):
        changed = copy.deepcopy(DEFAULT_WORLD)
        changed["radius_sq"] = 10
        with self.assertRaises(ValueError):
            Cell(self.path, changed)
        event = self.cell.propose(self.request([1, -1, 0]))
        (self.path / "attempts" / event["attempt_id"] / "Certificate.lean").write_text("theorem fake : True := by trivial\n")
        with self.assertRaises(ValueError):
            Cell(self.path)

    def test_verifier_exception_and_false_claim_do_not_commit(self):
        def fail(*args):
            raise TimeoutError()
        self.cell.verifier = fail
        event = self.cell.propose(self.request([1, -1, 0]))
        self.assertEqual(event["reason"], "verifier_failure")
        self.cell.verifier = lambda *args: {"accepted": True, "kernel_checked": True,
                                          "axioms": [], "after": [4, 0, 5]}
        event = self.cell.propose(self.request([1, -1, 0]))
        self.assertEqual(event["reason"], "proof_rejected")
        self.assertEqual(self.cell.inspect()["weights"], [3, 1, 5])

    def test_stdio_handshake_inspection_and_invalid_json(self):
        requests = [
            canonical({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL_VERSION}}),
            canonical({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            canonical({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
            canonical({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cell_inspect", "arguments": {}}}),
            '{"jsonrpc":"2.0","id":4,"method":"ping","method":"tools/call"}',
        ]
        proc = subprocess.run([sys.executable, str(Path(__file__).with_name("cell_mcp.py")),
                               "--run-dir", str(self.path)], input="\n".join(requests) + "\n",
                              text=True, capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual(len(output), 4)
        self.assertEqual(len(output[1]["result"]["tools"]), 3)
        self.assertEqual(output[2]["result"]["structuredContent"]["weights"], [3, 1, 5])
        self.assertEqual(output[3]["error"]["code"], -32700)
        self.assertEqual(len((self.path / "transport.jsonl").read_text().splitlines()), 10)

    def test_incomplete_attempts_are_visible_without_changing_state(self):
        orphan = self.path / "attempts" / "incomplete-synthetic"
        orphan.mkdir(parents=True)
        (orphan / "tool-request.json").write_text("{}")
        self.assertEqual(self.cell.inspect()["incomplete_attempts"], ["incomplete-synthetic"])
        self.assertEqual(self.cell.inspect()["revision"], 0)

    def test_strict_json_and_representation_limit(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                strict_json(raw)
        world = copy.deepcopy(DEFAULT_WORLD)
        world["initial"] = [1000, -1000, 5]
        cell = Cell(Path(self.tmp.name) / "limit", world)
        result = cell.propose({"expected_state_id": cell.inspect()["state_id"], "delta": [1, -1, 0]})
        self.assertEqual(result["reason"], "state_representation_bound")


if __name__ == "__main__":
    unittest.main()
