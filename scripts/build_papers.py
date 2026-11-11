#!/usr/bin/env python3
"""Build the ML Weft papers for w3ft.org: HTML pages and PDF editions.

Sources:   papers/<nn-slug>/paper.md      (Markdown with YAML front matter)
           papers/<nn-slug>/figures/      (SVG figures referenced by the paper)
           papers/templates/              (site and print templates, print CSS, fonts)
           papers/series.yml              (upcoming papers for the index)
Outputs:   site/papers/index.html
           site/papers/<slug>/index.html, figures/, ml-weft-paper-<n>-<slug>-v<version>.pdf
           site/papers/manifest.json      (hashes tying each output to its sources)

  python3 scripts/build_papers.py            # build HTML and PDF
  python3 scripts/build_papers.py --no-pdf   # HTML only
  python3 scripts/build_papers.py --check    # CI: HTML up to date, PDFs built from current sources

Needs pandoc 3.1.3 exactly (other releases emit different markup, and CI
compares bytes), PyYAML, and Playwright with Chromium for PDFs.
The header, footer and icon sprite are taken from site/index.html so the paper
pages always match the landing page.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
TEMPLATES = PAPERS / "templates"
SITE = ROOT / "site"
OUT = SITE / "papers"
PANDOC_ARGS = ["-f", "markdown", "-t", "html5", "--mathml", "--section-divs", "--wrap=none"]


# ---------------------------------------------------------------- sources
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


PRINT_TEMPLATE_PATHS = (
    "print-paper.html",
    "print.css",
    "fonts.css",
)


def template_digest() -> str:
    """Hash print inputs only so site HTML template edits do not invalidate PDFs."""
    h = hashlib.sha256()
    for name in PRINT_TEMPLATE_PATHS:
        path = TEMPLATES / name
        if path.is_file():
            h.update(name.encode())
            h.update(path.read_bytes())
    fonts_dir = TEMPLATES / "fonts"
    if fonts_dir.is_dir():
        for path in sorted(fonts_dir.rglob("*")):
            if path.is_file():
                rel = path.relative_to(TEMPLATES).as_posix()
                h.update(rel.encode())
                h.update(path.read_bytes())
    return h.hexdigest()


def load_paper(directory: Path) -> dict:
    text = (directory / "paper.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise SystemExit(f"{directory}/paper.md: missing YAML front matter")
    meta = yaml.safe_load(match.group(1))
    for key in ("title", "subtitle", "number", "slug", "version", "date", "authors", "status", "commit", "abstract"):
        if key not in meta:
            raise SystemExit(f"{directory}/paper.md: front matter needs '{key}'")
    figures = sorted((directory / "figures").glob("*")) if (directory / "figures").is_dir() else []
    h = hashlib.sha256((directory / "paper.md").read_bytes())
    for f in figures:
        h.update(f.name.encode())
        h.update(f.read_bytes())
    meta.update(dir=directory.name, path=directory, figures=figures, body_md=text[match.end():], source_sha256=h.hexdigest())
    return meta


def find_papers() -> list[dict]:
    papers = [load_paper(d) for d in sorted(PAPERS.iterdir()) if (d / "paper.md").is_file()]
    return sorted(papers, key=lambda p: p["number"])


# ---------------------------------------------------------------- pandoc
# The committed HTML must be byte-identical to a fresh build, and pandoc's output
# changes between releases, so everyone builds with this one release. CI installs
# it in .github/workflows/ci.yml; keep the two in step.
PANDOC_VERSION = "3.1.3"


def require_pandoc_version() -> None:
    try:
        first = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True).stdout.split("\n")[0]
    except FileNotFoundError:
        raise SystemExit("pandoc is required (https://pandoc.org/installing.html)")
    found = first.split()[-1] if first else "unknown"
    if found != PANDOC_VERSION:
        raise SystemExit(
            f"pandoc {PANDOC_VERSION} is required, found {found}. Other releases produce different HTML, "
            f"so the committed pages would not match. Install it from "
            f"https://github.com/jgm/pandoc/releases/tag/{PANDOC_VERSION}")


def pandoc(markdown: str, *extra: str) -> str:
    try:
        out = subprocess.run(["pandoc", *PANDOC_ARGS, *extra], input=markdown, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        raise SystemExit("pandoc is required (https://pandoc.org/installing.html)")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"pandoc failed: {e.stderr}")
    return out.stdout


def toc_html(markdown: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tpl:
        tpl.write("$table-of-contents$")
    try:
        return pandoc(markdown, "-s", "--toc", "--toc-depth=3", f"--template={tpl.name}", "--metadata", "title=x")
    finally:
        Path(tpl.name).unlink()


def polish(body: str) -> str:
    body = re.sub(r"<table", '<div class="table-wrap"><table', body)
    body = body.replace("</table>", "</table></div>")
    body = re.sub(r"<img ", '<img loading="lazy" decoding="async" ', body)
    return body


# ---------------------------------------------------------------- fields
def fill(template: str, values: dict) -> str:
    def sub(m: re.Match) -> str:
        key = m.group(1)
        if key not in values:
            raise SystemExit(f"template placeholder '{{{{{key}}}}}' has no value")
        return str(values[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def plain(text: str) -> str:
    """Markdown-ish text to a plain single line for meta tags."""
    text = re.sub(r"\$[^$]+\$", "", text)
    text = re.sub(r"[*_`]", "", text)
    return " ".join(text.split())


def first_sentences(text: str, n: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(parts[:n])


def pdf_name(p: dict) -> str:
    return f"ml-weft-paper-{p['number']}-{p['slug']}-v{p['version']}.pdf"


def bibtex(p: dict) -> str:
    date = p["date"] if isinstance(p["date"], dt.date) else dt.date.fromisoformat(str(p["date"]))
    key = f"mlweft{date.year}paper{p['number']}"
    entry = (
        f"@techreport{{{key},\n"
        f"  title       = {{{{{p['title']}: {p['subtitle']}}}}},\n"
        f"  author      = {{{p['authors']}}},\n"
        f"  institution = {{Moissanite Labs}},\n"
        f"  type        = {{ML Weft Paper}},\n"
        f"  number      = {{{p['number']}}},\n"
        f"  year        = {{{date.year}}},\n"
        f"  month       = {date.strftime('%b').lower()},\n"
        f"  note        = {{Version {p['version']}}},\n"
        f"  url         = {{https://w3ft.org/papers/{p['slug']}/}}\n"
        f"}}"
    )
    return html.escape(entry)


def common_fields(p: dict) -> dict:
    date = p["date"] if isinstance(p["date"], dt.date) else dt.date.fromisoformat(str(p["date"]))
    return {
        "title": html.escape(p["title"]),
        "subtitle": html.escape(p["subtitle"]),
        "number": p["number"],
        "slug": p["slug"],
        "dir": p["dir"],
        "version": p["version"],
        "date_iso": date.isoformat(),
        "date_human": f"{date.day} {date.strftime('%B %Y')}",
        "authors": html.escape(p["authors"]),
        "status": html.escape(p["status"]),
        "commit": p["commit"],
        "commit_short": p["commit"][:7],
        "keywords": html.escape(", ".join(p.get("keywords", []))),
        "description": html.escape(plain(p["abstract"])[:300].rsplit(" ", 1)[0] + "…"),
        "abstract": pandoc(p["abstract"]),
        "body": polish(pandoc(p["body_md"])),
        "bibtex": bibtex(p),
        "pdf_name": pdf_name(p),
    }


# ---------------------------------------------------------------- site chrome
def site_chrome() -> dict:
    index = (SITE / "index.html").read_text(encoding="utf-8")
    header = re.search(r'\n(\s*<header class="site-header[^"]*">.*?</header>)', index, re.S).group(1)
    footer = re.search(r'\n(\s*<footer class="site-footer[^"]*">.*?</footer>)', index, re.S).group(1)
    sprite = re.search(r'\n(\s*<svg width="0" height="0".*?</defs>\s*</svg>)', index, re.S).group(1)
    # In-page anchors in the nav point back to the landing page; icon <use href="#…"> stays local.
    root_links = lambda s: re.sub(r'(<a\b[^>]*?\s)href="#', r'\1href="/#', s)  # noqa: E731
    return {"header": root_links(header), "footer": root_links(footer), "sprite": sprite}


def previous_versions(p: dict) -> str:
    """Links to earlier PDF editions kept beside the current one (committed under site/papers/<slug>/)."""
    prefix = f"ml-weft-paper-{p['number']}-{p['slug']}-v"
    olds = sorted(f.name for f in (OUT / p["slug"]).glob(prefix + "*.pdf") if f.name != pdf_name(p))
    if not olds:
        return ""
    links = ", ".join(f'<a href="{n}">v{n[len(prefix):-4]}</a>' for n in olds)
    return f" Earlier PDF editions: {links}."


def human_size(n: int) -> str:
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


# ---------------------------------------------------------------- build
def build_html(papers: list[dict], out: Path, pdf_sizes: dict) -> dict[str, str]:
    """Write HTML pages (and copy figures) under `out`; return {relative path: sha256}."""
    chrome = site_chrome()
    page_tpl = (TEMPLATES / "site-paper.html").read_text(encoding="utf-8")
    written: dict[str, str] = {}
    for p in papers:
        target = out / p["slug"]
        target.mkdir(parents=True, exist_ok=True)
        fields = common_fields(p) | chrome | {"toc": toc_html(p["body_md"]), "pdf_size": pdf_sizes.get(p["slug"], ""),
                                              "previous_versions": previous_versions(p)}
        page = fill(page_tpl, fields)
        (target / "index.html").write_text(page, encoding="utf-8")
        written[f"{p['slug']}/index.html"] = sha256_bytes(page.encode())
        if p["figures"]:
            (target / "figures").mkdir(exist_ok=True)
            for f in p["figures"]:
                shutil.copyfile(f, target / "figures" / f.name)
                written[f"{p['slug']}/figures/{f.name}"] = sha256_bytes(f.read_bytes())

    cards = []
    for p in papers:
        f = common_fields(p)
        cards.append(f"""        <article class="card paper-card">
          <div class="paper-num">{p['number']}</div>
          <div>
            <h3><a href="/papers/{p['slug']}/">{f['title']}</a></h3>
            <p class="sub">{f['subtitle']}</p>
            <p class="meta">Version {f['version']} · {f['date_human']} · {f['status']}</p>
            <p>{html.escape(first_sentences(plain(p['abstract']), 2))}</p>
            <div class="actions">
              <a class="btn btn-primary" href="/papers/{p['slug']}/">Read online</a>
              <a class="btn" href="/papers/{p['slug']}/{f['pdf_name']}" download>PDF <span class="btn-meta">{pdf_sizes.get(p['slug'], '')}</span></a>
            </div>
          </div>
        </article>""")
    series = yaml.safe_load((PAPERS / "series.yml").read_text(encoding="utf-8")) or {}
    published = {p["number"] for p in papers}
    for u in series.get("upcoming", []):
        if u["number"] in published:
            continue
        cards.append(f"""        <article class="card paper-card upcoming">
          <div class="paper-num">{u['number']}</div>
          <div>
            <h3>{html.escape(u['title'])}</h3>
            <p class="sub">{html.escape(u['subtitle'])}</p>
            <p class="meta">{html.escape(u['status'])}</p>
          </div>
        </article>""")
    index = fill((TEMPLATES / "site-index.html").read_text(encoding="utf-8"), chrome | {"cards": "\n".join(cards)})
    (out / "index.html").write_text(index, encoding="utf-8")
    written["index.html"] = sha256_bytes(index.encode())
    return written


def build_pdf(p: dict, destination: Path) -> int:
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory(prefix="weft-paper-") as tmp:
        work = Path(tmp)
        shutil.copytree(TEMPLATES / "fonts", work / "fonts")
        shutil.copyfile(TEMPLATES / "fonts.css", work / "fonts.css")
        shutil.copyfile(TEMPLATES / "print.css", work / "print.css")
        if p["figures"]:
            (work / "figures").mkdir()
            for f in p["figures"]:
                shutil.copyfile(f, work / "figures" / f.name)
        doc = fill((TEMPLATES / "print-paper.html").read_text(encoding="utf-8"), common_fields(p))
        (work / "paper.html").write_text(doc, encoding="utf-8")
        with sync_playwright() as pw:
            # Same override as scripts/test_telemetry_browser.py for a system Chromium.
            browser = pw.chromium.launch(executable_path=os.environ.get("WEFT_BROWSER_EXECUTABLE") or None)
            page = browser.new_page()
            page.goto((work / "paper.html").as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(destination), prefer_css_page_size=True, print_background=True, outline=True, tagged=True)
            browser.close()
    return destination.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-pdf", action="store_true", help="skip PDF generation")
    parser.add_argument("--check", action="store_true", help="verify committed outputs match the sources")
    args = parser.parse_args()
    require_pandoc_version()

    papers = find_papers()
    tdigest = template_digest()
    manifest_path = OUT / "manifest.json"

    if args.check:
        manifest = json.loads(manifest_path.read_text())
        errors = []
        by_slug = {m["slug"]: m for m in manifest["papers"]}
        for p in papers:
            m = by_slug.get(p["slug"])
            if not m:
                errors.append(f"{p['slug']}: not built")
                continue
            if m["source_sha256"] != p["source_sha256"] or m["templates_sha256"] != tdigest:
                errors.append(f"{p['slug']}: sources or templates changed since the PDF was built (run scripts/build_papers.py)")
            if not (OUT / p["slug"] / pdf_name(p)).is_file():
                errors.append(f"{p['slug']}: missing PDF {pdf_name(p)}")
        sizes = {m["slug"]: human_size(m["pdf_bytes"]) for m in manifest["papers"]}
        with tempfile.TemporaryDirectory() as tmp:
            fresh = build_html(papers, Path(tmp), sizes)
            for rel, digest in fresh.items():
                committed = OUT / rel
                if not committed.is_file() or sha256_bytes(committed.read_bytes()) != digest:
                    errors.append(f"site/papers/{rel} is out of date (run scripts/build_papers.py)")
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        print(json.dumps({"status": "FAIL" if errors else "PASS", "papers": [p["slug"] for p in papers]}))
        return 1 if errors else 0

    OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"papers": []}
    old_by_slug = {m["slug"]: m for m in old["papers"]}
    entries, sizes = [], {}
    for p in papers:
        target = OUT / p["slug"]
        target.mkdir(parents=True, exist_ok=True)
        # Earlier versions stay published: their URLs may already be cited or linked.
        pdf_path = target / pdf_name(p)
        if args.no_pdf:
            prev = old_by_slug.get(p["slug"])
            if not prev or not pdf_path.is_file():
                raise SystemExit(f"{p['slug']}: no existing PDF; build without --no-pdf first")
            entry = dict(prev)
            entry["templates_sha256"] = tdigest
        else:
            size = build_pdf(p, pdf_path)
            entry = {"slug": p["slug"], "number": p["number"], "version": p["version"], "pdf": pdf_name(p),
                     "pdf_bytes": size, "source_sha256": p["source_sha256"], "templates_sha256": tdigest}
        entries.append(entry)
        sizes[p["slug"]] = human_size(entry["pdf_bytes"])
    build_html(papers, OUT, sizes)
    pandoc_version = subprocess.run(["pandoc", "--version"], capture_output=True, text=True).stdout.split("\n")[0]
    manifest_path.write_text(json.dumps({"pandoc": pandoc_version, "papers": entries}, indent=2) + "\n")
    print(json.dumps({"built": [e["pdf"] for e in entries], "pdf_bytes": [e["pdf_bytes"] for e in entries]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
