#!/usr/bin/env python3
"""A small MCP 2025-11-25 stdio server for Lean-checked integer cell edits.

The mathematical transition is proved. Python, the OS, the pinned Lean executable,
and the host-controlled storage are trusted runtime components, not proved here.
No arbitrary code, file paths, proof text, or external effect tools are exposed.
"""
import argparse
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import uuid

from verifier import verify_transition

PROTOCOL_VERSION = "2025-11-25"
DEFAULT_WORLD = {
    "schema": "weft.exact-readout.v1",
    "initial": [3, 1, 5],
    "anchors": [[1, 1, 0], [0, 0, 1]],
    "frozen": [2],
    "radius_sq": 8,
}
MAX_LINE_BYTES = 16384


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def state_id(world_id, revision, weights):
    return digest({"world_id": world_id, "revision": revision, "weights": weights})


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def save_json(path, value):
    """Replace one whole state-and-events snapshot, rather than split commits."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".snapshot-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as out:
            out.write(canonical(value) + "\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_world(world):
    if set(world) != set(DEFAULT_WORLD) or world["schema"] != DEFAULT_WORLD["schema"]:
        raise ValueError("unknown world schema")
    vectors = [world["initial"]] + world["anchors"]
    if not 1 <= len(world["anchors"]) <= 8:
        raise ValueError("one to eight preservation anchors required")
    if any(type(v) is not list or len(v) != 3 or any(type(n) is not int or abs(n) > 1000 for n in v)
           for v in vectors):
        raise ValueError("world vectors require three bounded integers")
    if (type(world["frozen"]) is not list or
        any(type(n) is not int or not 0 <= n < 3 for n in world["frozen"]) or
        len(set(world["frozen"])) != len(world["frozen"])):
        raise ValueError("invalid frozen coordinates")
    if type(world["radius_sq"]) is not int or not 0 <= world["radius_sq"] <= 300:
        raise ValueError("invalid squared radius")


def mathematical_guard(world, before, delta):
    """Independent Python arithmetic check, not a replacement for the Lean proof.

    Compare actual before/after observations rather than the Lean gate's dot(delta).
    """
    after = [a + b for a, b in zip(before, delta)]
    return (all(before[i] == after[i] for i in world["frozen"]) and
            sum((a - b) ** 2 for a, b in zip(after, before)) <= world["radius_sq"] and
            all(sum(x * w for x, w in zip(row, before)) ==
                sum(x * w for x, w in zip(row, after)) for row in world["anchors"]))


class Cell:
    def __init__(self, run_dir, world=None, verifier=verify_transition):
        self.directory = Path(run_dir)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.world = copy.deepcopy(DEFAULT_WORLD if world is None else world)
        validate_world(self.world)
        self.checker_pins = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ("Core.lean", "verifier.py", "cell_mcp.py")}
        self.world_id = digest({"world": self.world, "checker_pins": self.checker_pins})
        self.path = self.directory / "journal.json"
        self.lock_path = self.directory / ".writer.lock"
        self.thread_lock = threading.RLock()
        self.verifier = verifier
        with self._lock():
            if not self.path.exists():
                save_json(self.path, {"world": self.world, "world_id": self.world_id, "checker_pins": self.checker_pins,
                                     "revision": 0, "weights": self.world["initial"], "events": []})
            self._load()

    def _lock(self):
        from contextlib import contextmanager
        @contextmanager
        def locked():
            with self.thread_lock, self.lock_path.open("a") as lock_file:
                fcntl.flock(lock_file, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
        return locked()

    def _load(self):
        snapshot = strict_json(self.path.read_text())
        if (snapshot["world"] != self.world or snapshot["world_id"] != self.world_id or
            snapshot["checker_pins"] != self.checker_pins):
            raise ValueError("world changed: refusing to reuse a journal under different rules")
        previous = self.world_id
        weights = self.world["initial"][:]
        revision = 0
        for index, event in enumerate(snapshot["events"]):
            content = {k: v for k, v in event.items() if k != "event_hash"}
            if (event["sequence"] != index or event["previous_event"] != previous or
                event["event_hash"] != digest(content) or event["before"] != weights or
                event["before_state_id"] != state_id(self.world_id, revision, weights)):
                raise ValueError("journal chain or state continuity failure")
            previous = event["event_hash"]
            if event["accepted"]:
                expected = [a + b for a, b in zip(weights, event["request"]["delta"])]
                if event["after"] != expected or not event["proof"]["kernel_checked"]:
                    raise ValueError("committed transition binding failure")
                proof_dir = self.directory / "attempts" / event["attempt_id"]
                if digest(strict_json((proof_dir / "result.json").read_text())) != event["proof_result_sha256"]:
                    raise ValueError("proof result changed or disappeared")
                if hashlib.sha256((proof_dir / "Certificate.lean").read_bytes()).hexdigest() != event["proof"]["proofhash"]:
                    raise ValueError("checked certificate changed or disappeared")
                if not mathematical_guard(self.world, weights, event["request"]["delta"]):
                    raise ValueError("independent integer replay rejected committed transition")
                weights = expected
                revision += 1
            elif event["after"] != weights:
                raise ValueError("rejected transition changed mathematical state")
            if event["after_state_id"] != state_id(self.world_id, revision, weights):
                raise ValueError("resulting state ID mismatch")
        if snapshot["weights"] != weights or snapshot["revision"] != revision:
            raise ValueError("snapshot disagrees with transition history")
        return snapshot

    def inspect(self):
        with self._lock():
            s = self._load()
            recorded = {e["attempt_id"] for e in s["events"]}
            incomplete = sorted(p.name for p in (self.directory / "attempts").glob("*")
                                if p.is_dir() and p.name not in recorded)
            return {"world_id": self.world_id, "world": copy.deepcopy(self.world), "checker_pins": self.checker_pins,
                    "state_id": state_id(self.world_id, s["revision"], s["weights"]),
                    "revision": s["revision"], "weights": s["weights"],
                    "anchor_outputs": [sum(a * b for a, b in zip(row, s["weights"]))
                                       for row in self.world["anchors"]],
                    "event_count": len(s["events"]),
                    "incomplete_attempts": incomplete,
                    "proof_scope": "Exact integer readout edits at specified anchors; runtime is trusted."}

    def events(self):
        with self._lock():
            return copy.deepcopy(self._load()["events"])

    def propose(self, request):
        with self._lock():
            s = self._load()
            before = s["weights"][:]
            current = state_id(self.world_id, s["revision"], before)
            reason = None
            proof = {"accepted": False, "kernel_checked": False}
            if type(request) is not dict or set(request) != {"expected_state_id", "delta"}:
                reason = "schema_rejected"
            elif request["expected_state_id"] != current:
                reason = "stale_state"
            elif (type(request["delta"]) is not list or len(request["delta"]) != 3 or
                  any(type(n) is not int or abs(n) > 10 for n in request["delta"])):
                reason = "integer_delta_required"
            elif any(abs(a + b) > 1000 for a, b in zip(before, request["delta"])):
                reason = "state_representation_bound"
            attempt_id = f"{len(s['events']):04d}-" + uuid.uuid4().hex
            attempt_dir = self.directory / "attempts" / attempt_id
            attempt_dir.mkdir(parents=True)
            save_json(attempt_dir / "tool-request.json", request)
            if reason is None:
                try:
                    proof = self.verifier(before, request["delta"], self.world["anchors"],
                                          self.world["frozen"], self.world["radius_sq"], attempt_dir)
                    expected = [a + b for a, b in zip(before, request["delta"])]
                    binding = {"before": before, "delta": request["delta"], "anchors": self.world["anchors"],
                               "frozen": self.world["frozen"], "radius_sq": self.world["radius_sq"]}
                    if not (proof.get("accepted") is True and proof.get("kernel_checked") is True and
                            proof.get("axioms") == [] and proof.get("after") == expected and
                            all(proof.get(k) == v for k, v in binding.items()) and
                            proof.get("request_sha256") == digest(binding) and
                            proof.get("specsha") == self.checker_pins["Core.lean"] and
                            proof.get("trust_config", {}).get("template_sha256") == self.checker_pins["verifier.py"] and
                            mathematical_guard(self.world, before, request["delta"])):
                        reason = "proof_rejected"
                except Exception as error:
                    reason = "verifier_failure"
                    proof = {"accepted": False, "kernel_checked": False,
                             "error_type": type(error).__name__}
            # Preserve the exact returned proof result, including failures. A failed
            # attempt can never change weights; logging it changes only the audit trail.
            save_json(attempt_dir / "result.json", proof)
            # Persist proof evidence before the atomic journal records a commit.
            for artifact in attempt_dir.iterdir():
                if artifact.is_file():
                    with artifact.open("rb") as stream:
                        os.fsync(stream.fileno())
            for directory in (attempt_dir, attempt_dir.parent):
                descriptor = os.open(directory, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
            accepted = reason is None
            after = [a + b for a, b in zip(before, request["delta"])] if accepted else before[:]
            revision = s["revision"] + int(accepted)
            event = {"sequence": len(s["events"]), "attempt_id": attempt_id,
                     "previous_event": s["events"][-1]["event_hash"] if s["events"] else self.world_id,
                     "request": copy.deepcopy(request), "accepted": accepted, "reason": reason,
                     "before": before, "after": after, "before_state_id": current,
                     "after_state_id": state_id(self.world_id, revision, after),
                     "proof": proof, "proof_result_sha256": digest(proof)}
            event["event_hash"] = digest(event)
            s["events"].append(event)
            s["weights"], s["revision"] = after, revision
            save_json(self.path, s)
            return copy.deepcopy(event)


TOOLS = [
    {"name": "cell_inspect", "description": "Read the exact cell state and immutable mathematical rules.",
     "inputSchema": {"type": "object", "additionalProperties": False}},
    {"name": "cell_propose", "description": "Propose an integer edit. Commit only after Lean checks this exact transition.",
     "inputSchema": {"type": "object", "properties": {
         "expected_state_id": {"type": "string"},
         "delta": {"type": "array", "items": {"type": "integer", "minimum": -10, "maximum": 10},
                   "minItems": 3, "maxItems": 3}},
         "required": ["expected_state_id", "delta"], "additionalProperties": False}},
    {"name": "cell_events", "description": "Read accepted and rejected actions with proof records and state hashes.",
     "inputSchema": {"type": "object", "additionalProperties": False}},
]


class MCPServer:
    def __init__(self, cell):
        self.cell = cell
        self.initialized = False
        self.ready = False

    def dispatch(self, message):
        if type(message) is not dict or message.get("jsonrpc") != "2.0" or type(message.get("method")) is not str:
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
        notification = "id" not in message
        identifier = message.get("id")
        method, params = message["method"], message.get("params", {})
        def error(code, description):
            return None if notification else {"jsonrpc": "2.0", "id": identifier,
                                              "error": {"code": code, "message": description}}
        if notification:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            # Notifications cannot invoke a state-changing tool.
            return None
        if type(params) is not dict:
            return error(-32602, "Object parameters required")
        if method == "initialize":
            if self.initialized:
                return error(-32600, "Already initialized")
            if params.get("protocolVersion") != PROTOCOL_VERSION:
                return error(-32602, "Supported protocol version: " + PROTOCOL_VERSION)
            self.initialized = True
            result = {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}},
                      "serverInfo": {"name": "weft-exact-cell", "version": "0.1.0"}}
        elif method == "ping":
            result = {}
        elif not self.ready:
            return error(-32002, "Complete initialization before using tools")
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            name, args = params.get("name"), params.get("arguments", {})
            try:
                if name == "cell_propose":
                    value = self.cell.propose(args)
                    failed = not value["accepted"]
                elif name in {"cell_inspect", "cell_events"}:
                    if args != {}:
                        return error(-32602, "This tool accepts empty arguments only")
                    value = self.cell.inspect() if name == "cell_inspect" else {"events": self.cell.events()}
                    failed = False
                else:
                    return error(-32602, "Unknown tool")
                result = {"content": [{"type": "text", "text": canonical(value)}],
                          "structuredContent": value, "isError": failed}
            except Exception as exc:
                return error(-32603, "Cell unavailable: " + type(exc).__name__)
        else:
            return error(-32601, "Method not found; this server implements MCP " + PROTOCOL_VERSION)
        return {"jsonrpc": "2.0", "id": identifier, "result": result}


def serve(run_dir):
    server = MCPServer(Cell(run_dir))
    transcript_path = Path(run_dir) / "transport.jsonl"
    def record(value):
        with transcript_path.open("a") as out:
            out.write(canonical(value) + "\n")
            out.flush()
            os.fsync(out.fileno())
    while True:
        raw = sys.stdin.buffer.readline(MAX_LINE_BYTES + 1)
        if not raw:
            break
        transport_id = uuid.uuid4().hex
        record({"phase": "received", "transport_id": transport_id,
                "raw_request_hex": raw.hex(), "over_limit": len(raw) > MAX_LINE_BYTES})
        if len(raw) > MAX_LINE_BYTES:
            # Stop instead of interpreting a truncated request or its tail.
            response = {"jsonrpc": "2.0", "id": None, "error": {
                "code": -32600, "message": "Request exceeds byte limit"}}
            record({"phase": "returned", "transport_id": transport_id, "response": response})
            print(canonical(response), flush=True)
            break
        try:
            request = strict_json(raw.decode("utf-8"))
            response = server.dispatch(request)
        except (ValueError, UnicodeError):
            response = {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": "Invalid JSON"}}
        record({"phase": "returned", "transport_id": transport_id, "response": response})
        if response is not None:
            print(canonical(response), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    serve(args.run_dir)
