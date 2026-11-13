#!/usr/bin/env python3
"""Restore the generated artifacts kept out of the tree, byte for byte.

GENERATED-SHA256SUMS lists each file with its sha256 and byte size. The exact
bytes live in this repository's history at ARCHIVE_COMMIT, the original
archive head preserved on branch record/astra-teachers-prereg-history-20261112
(see DCO-HISTORY.md). This script copies each missing file out of that commit,
fetching the branch when needed, and checks its sha256. Run it before any
`replay`, `advance` or `evaluate` command in this directory.

    python restore_generated.py           # restore missing files, verify all
    python restore_generated.py --check   # verify the files that are present

Regenerating these files from seeds is not a substitute. Trained source cells
and results depend on the floating-point platform: on Linux x86_64 with NumPy
2.5.4 the regenerated experiments differ from the archived macOS arm64 ones,
and the archived phase-one to phase-three replays do not match there.
"""
from __future__ import annotations
import argparse
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUMS = ROOT / 'GENERATED-SHA256SUMS'
ARCHIVE_COMMIT = 'd85940c0d078b54f40f4742b33c286c521164567'
REMOTE_REF = 'refs/heads/record/astra-teachers-prereg-history-20261112'


def git(*args, **kwargs):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, **kwargs)


def repo_prefix():
    return git('rev-parse', '--show-prefix', text=True).stdout.strip()


def entries():
    rows = []
    for line in SUMS.read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            digest, size, path = line.split(maxsplit=2)
            rows.append((path, int(size), digest))
    return rows


def ensure_commit():
    if subprocess.run(['git', 'cat-file', '-e', ARCHIVE_COMMIT + '^{commit}'], cwd=ROOT, capture_output=True).returncode != 0:
        git('fetch', '--no-tags', 'origin', REMOTE_REF)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='verify present files only; restore nothing')
    args = parser.parse_args()
    rows = entries()
    missing = [path for path, _, _ in rows if not (ROOT / path).exists()]
    if missing and not args.check:
        ensure_commit()
        prefix = repo_prefix()
        for path in missing:
            data = git('show', f'{ARCHIVE_COMMIT}:{prefix}{path}').stdout
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    bad = []
    for path, size, digest in rows:
        p = ROOT / path
        if not p.exists():
            if not args.check:
                bad.append('missing ' + path)
            continue
        data = p.read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
            bad.append('mismatch ' + path)
    restored = 0 if args.check else len(missing)
    print(f'{len(rows)} listed, {restored} restored, {len(bad)} problems')
    for line in bad:
        print(line)
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
