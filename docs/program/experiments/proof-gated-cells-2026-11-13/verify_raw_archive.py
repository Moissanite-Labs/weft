#!/usr/bin/env python3
"""Verify indexed scientific evidence bytes without rerunning experiments."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def verify(data, record):
    if len(data) != record["bytes"]:
        raise ValueError("Size mismatch: " + record["path"])
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("SHA-256 mismatch: " + record["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="fetch preserved public evidence branches first")
    args = parser.parse_args()
    index = json.loads((ROOT / "RAW-DATA-INDEX.json").read_text())
    if args.fetch:
        for remote_ref in (
            "refs/pull/146/head",
            "refs/heads/record/astra-teachers-prereg-history-20261112",
            "refs/pull/151/head",
        ):
            subprocess.run(["git", "fetch", "--no-tags", "origin", remote_ref], cwd=ROOT, check=True)
    records = index["responses"] + index["large_archived_files"] + index["peer_flex_review"]["files"]
    for record in records:
        verify(git("show", record["source_commit"] + ":" + record["path"]), record)
    supplied = index["supplied_lean_harness"]
    verify((ROOT / supplied["path"]).read_bytes(), supplied)
    print(json.dumps({"verified_repository_files": len(records), "verified_local_attachments": 1,
                      "paid_responses": len(index["responses"]), "large_archived_files": len(index["large_archived_files"]),
                      "experiment_reruns": 0, "api_calls": 0}))


if __name__ == "__main__":
    main()
