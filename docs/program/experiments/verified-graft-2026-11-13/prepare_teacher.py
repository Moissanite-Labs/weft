"""Prepare blind teacher envelopes without making model calls."""
from pathlib import Path
import argparse
import hashlib
import json

import graft


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def envelope(visible, current_deployment, round_number, feedback):
    return {
        "experiment": graft.CONFIG["version"],
        "round": round_number,
        "packet": visible,
        "current_deployment": current_deployment,
        "previous_A_feedback": feedback,
        "response_requirement": "Return exactly four candidate actions as {\"candidates\":[{\"mode\":...,\"delta\":...},...]}. Use only this packet. Each delta is relative to the ORIGINAL host, including in round two.",
    }


def prepare(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {"role": "pre-call generated artifacts", "files": {}}
    def save(name, obj):
        data = encode(obj)
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest["files"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    save("config.json", graft.CONFIG)
    for seed in graft.CONFIG["seeds"]:
        exp = graft.instance(seed)
        save(f"hidden/seed-{seed}.json", exp)
        for case in graft.CONFIG["cases"]:
            visible = graft.packet(exp, case)
            parent = graft.deployment(visible, {"mode": "abstain", "delta": graft.ZERO})
            save(f"requests/seed-{seed}-{case}-round-1.json", envelope(visible, parent, 1, []))
    (folder / "manifest.json").write_bytes(encode(manifest))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    result = prepare(args.folder)
    print(json.dumps({"prepared_files": len(result["files"])}))
