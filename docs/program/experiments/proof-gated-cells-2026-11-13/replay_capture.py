#!/usr/bin/env python3
"""Check captured bytes/state history and rerun Lean for every mathematical proposal."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from cell_mcp import Cell, canonical
from verifier import verify_transition


def replay(capture):
    capture = Path(capture)
    manifest = json.loads((capture / "SHA256.json").read_text())
    for name, expected in manifest.items():
        path = capture / name
        if path.resolve().is_relative_to(capture.resolve()) is False:
            raise ValueError("manifest path escapes capture")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("captured bytes differ: " + name)
    journal = json.loads((capture / "cell/journal.json").read_text())
    cell = Cell(capture / "cell", world=journal["world"])
    checks = []
    with tempfile.TemporaryDirectory(prefix="weft-proof-replay-") as temporary:
        for event in cell.events():
            original = event["proof"]
            if not original["kernel_checked"]:
                checks.append({"sequence": event["sequence"], "kind": "runtime_rejection",
                               "reason": event["reason"], "after_equals_before": event["after"] == event["before"]})
                continue
            result = verify_transition(original["before"], original["delta"], original["anchors"],
                                       original["frozen"], original["radius_sq"],
                                       Path(temporary) / str(event["sequence"]))
            fields = ("accepted", "kernel_checked", "axioms", "after", "request_sha256", "proofhash", "specsha")
            if any(result[k] != original[k] for k in fields):
                raise ValueError("replayed certificate differs: " + str(event["sequence"]))
            checks.append({"sequence": event["sequence"], "kind": "kernel_rechecked",
                           "accepted": result["accepted"], "axioms": result["axioms"]})
    return {"files_sha256_verified": len(manifest), "events": checks,
            "kernel_rechecked": sum(x["kind"] == "kernel_rechecked" for x in checks),
            "final": cell.inspect(), "api_calls": 0,
            "scope": "Archived byte identity, checked state history, and fresh concrete Lean certificate checks."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, default=Path(__file__).with_name("data") / "mcp_demo")
    args = parser.parse_args()
    print(canonical(replay(args.capture)))
