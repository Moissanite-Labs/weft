#!/usr/bin/env python3
"""Inventory an immutable Git snapshot; validate explicit reading attestations.

Never executes corpus snippets. A generated inventory is not a reading claim.
Markdown indexing covers fenced blocks, not every possible form of embedded code.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = "a721b12579caba4e04dc31b16731cc2657079207"
AUDIT = ROOT / "docs/program/audit"
CODE_SUFFIXES = {".py", ".c", ".h", ".js", ".jsx", ".mjs", ".wgsl", ".sol", ".sh"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def markdown_blocks(path: str, data: bytes) -> list[dict]:
    """Track fence length/character and headings outside fences, including EOF."""
    lines = data.decode("utf-8").splitlines(keepends=True)
    blocks = []
    active = None
    heading = ""
    for line_no, line in enumerate(lines, 1):
        if active:
            marker, start, info, context = active
            if re.fullmatch(r" {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*\r?\n?", line):
                payload = "".join(lines[start:line_no - 1]).encode()
                blocks.append(block_record(path, start, line_no, info, context, payload, True))
                active = None
            continue
        match = re.match(r" {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        if match and not (match[1][0] == "`" and "`" in match[2]):
            active = (match[1], line_no, match[2].strip(), heading)
        elif re.match(r" {0,3}#{1,6}\s", line):
            heading = line.strip()
    if active:
        _, start, info, context = active
        blocks.append(block_record(path, start, len(lines), info, context,
                                   "".join(lines[start:]).encode(), False))
    return blocks


def block_record(path, start, end, info, heading, payload, closed):
    content_hash = digest(payload)
    identity = digest(f"{path}\0{start}\0{content_hash}".encode())[:20]
    return {"id": f"F-{identity}", "path": path, "start_line": start,
            "end_line": end, "info": info, "heading": heading,
            "content_sha256": content_hash, "bytes": len(payload), "closed": closed}


def inventory(ref: str) -> tuple[dict, dict]:
    commit = git("rev-parse", "--verify", ref + "^{commit}").decode().strip()
    entries = git("ls-tree", "-r", "-z", commit).split(b"\0")
    files, blocks, by_hash = [], [], {}
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode()
        if kind != "blob":
            raise ValueError(f"Unsupported tracked object {kind}: {path}")
        data = git("cat-file", "blob", oid)
        try:
            decoded = data.decode("utf-8")
            text = "\x00" not in decoded
        except UnicodeDecodeError:
            text = False
        row = {"path": path, "git_blob": oid, "git_mode": mode,
               "sha256": digest(data), "bytes": len(data),
               "lines": len(data.splitlines()),
               "kind": "empty" if not data else "text" if text else "binary"}
        files.append(row)
        by_hash.setdefault(row["sha256"], []).append(path)
        if text and Path(path).suffix.lower() == ".md":
            blocks.extend(markdown_blocks(path, data))
    duplicates = [paths for paths in by_hash.values() if len(paths) > 1]
    return ({"schema_version": 1, "source_commit": commit,
             "scope": "Every tracked blob at source_commit; excludes later audit outputs and untracked files.",
             "files": files, "exact_duplicate_groups": duplicates},
            {"schema_version": 1, "source_commit": commit,
             "scope": "Top-level Markdown fences (0–3 leading spaces). Not indented code, blockquote fences, inline code, HTML scripts or semantic lineage.",
             "blocks": blocks})


def validate_records(manifest: dict, records: list[dict]) -> list[str]:
    """Check completeness/provenance, not truth of a reader's attestation."""
    errors = []
    expected = {f["path"]: f for f in manifest["files"]}
    indexed = {}
    if not isinstance(records, list):
        return ["Reading records must be an array"]
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Reading record {index} must be an object")
            continue
        path = record.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"Reading record {index} needs a nonempty path string")
            continue
        if path in indexed:
            errors.append(f"Duplicate reading record: {path}")
        indexed[path] = record
    for path in indexed.keys() - expected.keys():
        errors.append(f"Unexpected source: {path}")
    for path, source in expected.items():
        record = indexed.get(path)
        if record is None:
            errors.append(f"Missing reading record: {path}")
            continue
        if record.get("sha256") != source["sha256"]:
            errors.append(f"Stale content hash: {path}")
        status = record.get("status")
        if not isinstance(status, str) or status not in {"read", "duplicate-reviewed", "binary-inspected", "empty-inspected"}:
            errors.append(f"Incomplete/unknown status: {path}: {status}")
        if status == "binary-inspected" and source["kind"] != "binary":
            errors.append(f"Binary status on nonbinary file: {path}")
        if status == "empty-inspected" and source["kind"] != "empty":
            errors.append(f"Empty status on nonempty file: {path}")
        if status == "read" and source["kind"] != "text":
            errors.append(f"Text-read status on {source['kind']}: {path}")
        if status == "duplicate-reviewed":
            target = record.get("duplicate_of")
            canonical = indexed.get(target, {}) if isinstance(target, str) else {}
            if target == path or canonical.get("status") not in ("read", "binary-inspected", "empty-inspected"):
                errors.append(f"Duplicate requires directly inspected canonical source: {path}")
            if not isinstance(target, str) or target not in expected or expected[target]["sha256"] != source["sha256"]:
                errors.append(f"Unequal duplicate: {path} -> {target}")
        if not isinstance(record.get("summary"), str) or not record["summary"].strip():
            errors.append(f"Summary must be a nonempty string: {path}")
        for field in ("components", "variant_notes", "next_actions", "uncertainties"):
            value = record.get(field)
            if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
                errors.append(f"{field} must be an array of nonempty strings: {path}")
        if not record.get("components"):
            errors.append(f"Empty components: {path}")
        evidence = record.get("evidence", [])
        if not isinstance(evidence, list):
            errors.append(f"Evidence must be an array: {path}")
            continue
        if source["kind"] == "text" and not evidence:
            errors.append(f"Missing evidence: {path}")
        for item in evidence:
            if not isinstance(item, dict):
                errors.append(f"Evidence entry must be an object: {path}")
                continue
            lo, hi = item.get("start_line"), item.get("end_line")
            if type(lo) is not int or type(hi) is not int or not (1 <= lo <= hi <= source["lines"]):
                errors.append(f"Invalid evidence range: {path}: {lo}–{hi}")
            if not isinstance(item.get("finding"), str) or not item["finding"].strip():
                errors.append(f"Evidence finding must be a nonempty string: {path}")
    return errors


def read_records(directory: Path) -> list[dict]:
    records = []
    for path in sorted(directory.glob("read-*.json")):
        try:
            value = json.loads(path.read_text())
        except (OSError, ValueError) as error:
            raise ValueError(f"Cannot read ledger {path}: {error}") from error
        # Readers may include checkpoint metadata alongside the records array.
        if isinstance(value, dict):
            value = value.get("files")
        if not isinstance(value, list):
            raise ValueError(f"Ledger {path} must be an array or an object with a files array")
        records.extend(value)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["generate", "check", "progress"])
    parser.add_argument("--ref", default=BASE)
    parser.add_argument("--directory", type=Path, default=AUDIT)
    args = parser.parse_args()
    manifest, fragments = inventory(args.ref)
    if args.action == "generate":
        args.directory.mkdir(parents=True, exist_ok=True)
        for name, value in [("inventory.json", manifest), ("fenced-blocks.json", fragments)]:
            (args.directory / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    else:
        try:
            records = read_records(args.directory)
        except ValueError as error:
            parser.exit(1, str(error) + "\n")
        errors = validate_records(manifest, records)
        if args.action == "check":
            for name, value in [("inventory.json", manifest), ("fenced-blocks.json", fragments)]:
                saved = args.directory / name
                if not saved.exists() or json.loads(saved.read_text()) != value:
                    errors.append(f"Generated artifact is stale: {name}")
            for error in errors:
                print(error, file=sys.stderr)
            if errors:
                raise SystemExit(1)
        else:
            print(json.dumps({"remaining_validation_findings": errors}, indent=2))
    print(json.dumps({"source_commit": manifest["source_commit"], "files": len(manifest["files"]),
                      "bytes": sum(f["bytes"] for f in manifest["files"]),
                      "duplicate_groups": len(manifest["exact_duplicate_groups"]),
                      "markdown_fenced_blocks": len(fragments["blocks"])}))


if __name__ == "__main__":
    main()
