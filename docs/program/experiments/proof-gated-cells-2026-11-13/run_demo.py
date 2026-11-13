#!/usr/bin/env python3
"""Capture a real local MCP conversation and actual Lean checks; no model/API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from cell_mcp import PROTOCOL_VERSION, canonical, save_json


def run(output):
    output = Path(output)
    if output.exists():
        raise ValueError("Use a new output directory; captured experiments are not overwritten")
    output.mkdir(parents=True)
    proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("cell_mcp.py")),
                             "--run-dir", str(output / "cell")],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    exchanges = []
    next_id = 0
    def call(method, params=None):
        nonlocal next_id
        next_id += 1
        message = {"jsonrpc": "2.0", "id": next_id, "method": method, "params": params or {}}
        proc.stdin.write(canonical(message) + "\n")
        proc.stdin.flush()
        response = json.loads(proc.stdout.readline())
        exchanges.append({"request": message, "response": response})
        save_json(output / "client-exchanges.json", exchanges)
        if response.get("id") != next_id:
            raise ValueError("Mismatched RPC response")
        if "error" in response:
            return response
        return response["result"].get("structuredContent", response["result"])
    try:
        call("initialize", {"protocolVersion": PROTOCOL_VERSION,
                            "capabilities": {}, "clientInfo": {"name": "recorded-local-probe", "version": "1"}})
        initialized = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        proc.stdin.write(canonical(initialized) + "\n")
        proc.stdin.flush()
        exchanges.append({"request": initialized, "response": None})
        call("tools/list")
        initial = call("tools/call", {"name": "cell_inspect", "arguments": {}})
        old = initial["state_id"]
        outcomes = []
        def propose(label, expected, delta, **extra):
            result = call("tools/call", {"name": "cell_propose", "arguments": {
                "expected_state_id": expected, "delta": delta, **extra}})
            outcomes.append({"label": label, "accepted": result["accepted"], "reason": result["reason"],
                             "kernel_checked": result["proof"]["kernel_checked"],
                             "before": result["before"], "after": result["after"],
                             "event_hash": result["event_hash"]})
            return result["after_state_id"]
        current = propose("useful_nonzero_edit", old, [1, -1, 0])
        propose("stale_state", old, [1, -1, 0])
        propose("anchor_drift", current, [1, 0, 0])
        propose("frozen_coordinate", current, [0, 0, 1])
        propose("oversized_delta_norm", current, [3, -3, 0])
        propose("proof_text_not_a_capability", current, [1, -1, 0], proof="by sorry")
        propose("boolean_not_an_integer", current, [True, -1, 0])
        propose("valid_no_op_not_progress", current, [0, 0, 0])
        final = call("tools/call", {"name": "cell_inspect", "arguments": {}})
        history = call("tools/call", {"name": "cell_events", "arguments": {}})
        assert [x["accepted"] for x in outcomes] == [True, False, False, False, False, False, False, True]
        assert initial["anchor_outputs"] == final["anchor_outputs"] == [4, 5]
        assert final["weights"] == [4, 0, 5]
        assert len(history["events"]) == 8 and final["revision"] == 2
        summary = {"kind": "scripted_mechanism_probe", "model_calls": 0, "api_calls": 0,
                   "protocol_version": PROTOCOL_VERSION, "initial": initial, "final": final,
                   "outcomes": outcomes, "accepted": 2, "rejected": 6,
                   "limitations": ["No language-model policy or colony intelligence was evaluated.",
                       "A valid no-op is accepted: legality does not imply task progress.",
                       "Exact integer anchor preservation does not certify unseen float-network behavior.",
                       "Python adapter, compiler/toolchain, OS and storage remain trusted."]}
        save_json(output / "summary.json", summary)
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)
        (output / "server-stderr.txt").write_text(proc.stderr.read())
        if proc.returncode:
            raise RuntimeError("MCP server failed")
    manifest = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output.rglob("*")) if path.is_file() and path.name != ".writer.lock"}
    save_json(output / "SHA256.json", manifest)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out)
    print(canonical({"accepted": result["accepted"], "rejected": result["rejected"], "api_calls": 0}))
