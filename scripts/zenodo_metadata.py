#!/usr/bin/env python3
"""Zenodo metadata for the ML Weft software record and the paper preprints.

The software record is made by Zenodo's GitHub integration from a release; it
reads .zenodo.json at the root of the repository. The papers are separate
preprint records uploaded by hand (or through the Zenodo API) with the metadata
this script writes, so the records always match the papers' front matter.

  python3 scripts/zenodo_metadata.py --check
      CI: .zenodo.json and CITATION.cff agree, and every paper has a PDF.
  python3 scripts/zenodo_metadata.py papers [--software-doi 10.5281/zenodo.N] [--out DIR]
      Write one deposit metadata file per paper (default: print to stdout).

Release steps are in docs/program/releasing.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_papers import OUT, ROOT, find_papers, pdf_name  # noqa: E402

ZENODO = ROOT / ".zenodo.json"
CITATION = ROOT / "CITATION.cff"
SOFTWARE_LICENSE = "Apache-2.0"
PAPER_LICENSE = "cc-by-4.0"
REQUIRED = ("title", "upload_type", "description", "creators", "license", "access_right")


def load_zenodo() -> dict:
    return json.loads(ZENODO.read_text(encoding="utf-8"))


def check() -> list[str]:
    errors = []
    meta = load_zenodo()
    for key in REQUIRED:
        if not meta.get(key):
            errors.append(f".zenodo.json: missing '{key}'")
    if meta.get("upload_type") != "software":
        errors.append(".zenodo.json: upload_type must be 'software'")
    if meta.get("license") != SOFTWARE_LICENSE:
        errors.append(f".zenodo.json: license must be {SOFTWARE_LICENSE} (LICENSE)")
    if "version" in meta:
        errors.append(".zenodo.json: leave 'version' out; Zenodo takes it from the release tag")

    cff = yaml.safe_load(CITATION.read_text(encoding="utf-8"))
    if cff.get("license") != SOFTWARE_LICENSE:
        errors.append(f"CITATION.cff: license must be {SOFTWARE_LICENSE}")
    if cff.get("title") != meta.get("title"):
        errors.append("CITATION.cff and .zenodo.json: titles differ")
    cff_names = [f"{a['family-names']}, {a['given-names']}" for a in cff.get("authors", [])]
    zen_names = [c["name"] for c in meta.get("creators", [])]
    if cff_names != zen_names:
        errors.append(f"creators differ: CITATION.cff {cff_names} vs .zenodo.json {zen_names}")

    for p in find_papers():
        pdf = OUT / p["slug"] / pdf_name(p)
        if not pdf.is_file():
            errors.append(f"paper {p['number']}: no PDF at {pdf.relative_to(ROOT)}")
    return errors


def abstract_html(markdown: str) -> str:
    """The front-matter abstract as the simple HTML Zenodo accepts."""
    paragraphs = []
    for block in re.split(r"\n\s*\n", markdown.strip()):
        text = html.escape(" ".join(block.split()), quote=False)
        text = re.sub(r"\$([^$]+)\$", r"\1", text)  # Zenodo shows no maths; inline symbols read fine bare
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        paragraphs.append(f"<p>{text}</p>")
    return "".join(paragraphs)


def paper_record(p: dict, creators: list[dict], software_doi: str | None) -> dict:
    date = p["date"] if isinstance(p["date"], dt.date) else dt.date.fromisoformat(str(p["date"]))
    url = f"https://w3ft.org/papers/{p['slug']}/"
    related = [
        {"identifier": url, "relation": "isVariantFormOf", "resource_type": "publication-preprint", "scheme": "url"},
        {
            "identifier": f"https://github.com/Moissanite-Labs/weft/tree/{p['commit']}",
            "relation": "references",
            "resource_type": "software",
            "scheme": "url",
        },
    ]
    if software_doi:
        related.append(
            {"identifier": software_doi, "relation": "isSupplementedBy", "resource_type": "software", "scheme": "doi"}
        )
    return {
        "upload_type": "publication",
        "publication_type": "preprint",
        "title": f"{p['title']}: {p['subtitle']}",
        "creators": creators,
        "description": abstract_html(p["abstract"]),
        "publication_date": date.isoformat(),
        "version": str(p["version"]),
        "language": "eng",
        "access_right": "open",
        "license": PAPER_LICENSE,
        "keywords": list(p.get("keywords", [])),
        "related_identifiers": related,
        "notes": (
            f"ML Weft Paper {p['number']}, version {p['version']}. Describes repository commit {p['commit']}. "
            f"Evidence status: {p['status']}"
        ),
        "_file": str((OUT / p["slug"] / pdf_name(p)).relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=("papers",))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--software-doi", help="the software record's concept DOI, once minted")
    parser.add_argument("--out", type=Path, help="directory for one JSON file per paper")
    args = parser.parse_args()

    if args.check or not args.command:
        errors = check()
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        if not errors:
            print("zenodo metadata: ok")
        return 1 if errors else 0

    creators = load_zenodo()["creators"]
    records = {p["slug"]: paper_record(p, creators, args.software_doi) for p in find_papers()}
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for slug, record in records.items():
            (args.out / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
            print(args.out / f"{slug}.json")
    else:
        print(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
