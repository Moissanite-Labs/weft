#!/usr/bin/env python3
"""Build dist/ for Worker ml-siliconcordat: lab pages at / and /ml, Weft mirror at /weft."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "siliconcordat" / "sources-manifest.json"
DIST = ROOT / "dist"
SITE = ROOT / "site"

REWRITE_SUFFIXES = {".html", ".css", ".js", ".json", ".svg"}
TEXT_HEADERS_NAME = "_headers"

# Retired #79 paths — must not appear under dist/weft.
RETIRED_REL_PATHS = (
    "assets/js/weft-loom.js",
    "assets/shaders/dashboard_layout.wgsl",
    "assets/workers/telemetry-worker.js",
    "data/moissanite_telemetry.json",
    "data/moissanite_telemetry.bin",
    "data/telemetry.jsonl",
)
RETIRED_DIR_PREFIXES = ("data/", "assets/shaders/", "assets/workers/")
EXCLUDED_SITE_GLOBS = ("lab/field/**",)

SC_WEEFT = "https://siliconcordat.com/weft"
W3FT = "https://w3ft.org"


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def ensure_commit(sha: str) -> bool:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
    )
    if probe.returncode == 0:
        return True
    fetch = subprocess.run(
        ["git", "fetch", "origin", sha],
        cwd=ROOT,
        capture_output=True,
    )
    if fetch.returncode != 0:
        return False
    verify = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
    )
    return verify.returncode == 0


def is_shallow_repository() -> bool:
    probe = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0 and probe.stdout.strip() == "true"


def pin_is_in_head_history(sha: str) -> bool:
    check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    )
    if check.returncode == 0:
        return True
    if not is_shallow_repository():
        return False
    unshallow = subprocess.run(
        ["git", "fetch", "--unshallow"],
        cwd=ROOT,
        capture_output=True,
    )
    if unshallow.returncode != 0:
        return False
    retry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    )
    return retry.returncode == 0


def require_weft_pin(pinned: str) -> None:
    if not ensure_commit(pinned):
        print(
            f"error: pinned weft commit {pinned} cannot be resolved",
            file=sys.stderr,
        )
        sys.exit(1)
    if not pin_is_in_head_history(pinned):
        print(
            f"error: pinned weft commit {pinned} is not in HEAD's history",
            file=sys.stderr,
        )
        sys.exit(1)


def site_tree_at(rev: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{rev}:site"],
        cwd=ROOT,
        text=True,
    ).strip()


def assert_weft_pin(manifest: dict) -> None:
    pinned = manifest["weft"]["sha"]
    require_weft_pin(pinned)
    try:
        head_site = site_tree_at("HEAD")
        pin_site = site_tree_at(pinned)
    except subprocess.CalledProcessError as exc:
        print(f"error: could not resolve site/ tree: {exc}", file=sys.stderr)
        sys.exit(1)
    if head_site != pin_site:
        print(
            "error: site/ at HEAD does not match site/ at pinned weft "
            f"{pinned} (HEAD:site={head_site}, pin:site={pin_site})",
            file=sys.stderr,
        )
        sys.exit(1)


def should_skip_site_file(rel: str) -> bool:
    rel_norm = rel.replace("\\", "/")
    for retired in RETIRED_REL_PATHS:
        if rel_norm == retired or rel_norm.endswith("/" + retired):
            return True
    for prefix in RETIRED_DIR_PREFIXES:
        if rel_norm.startswith(prefix):
            return True
    if rel_norm.startswith("lab/field/"):
        return True
    return False


def rewrite_w3ft_urls(text: str) -> str:
    text = text.replace(f"{W3FT}/", f"{SC_WEEFT}/")
    text = text.replace(W3FT, SC_WEEFT)
    return text


def rewrite_root_paths_in_text(text: str) -> str:
    text = rewrite_w3ft_urls(text)

    def qsub(m: re.Match[str]) -> str:
        q, path = m.group(1), m.group(2)
        if path.startswith("/weft"):
            return m.group(0)
        if path == "/":
            return f"{q}/weft/{q}"
        if path.startswith("/#"):
            return f"{q}/weft{path}{q}"
        if re.match(r"^/(assets|papers|widgets)(/|$)", path) or path in (
            "/favicon.svg",
            "/og.png",
            "/404.html",
        ):
            return f"{q}/weft{path}{q}"
        return m.group(0)

    text = re.sub(r'(?P<q>["\'])(/[^"\']*)(?P=q)', qsub, text)
    text = re.sub(
        r"url\(\s*/(?!weft/)(assets/)",
        r"url(/weft/\1",
        text,
    )
    return text


_PATH_LINE = re.compile(r"^(/\S*)$")


def rewrite_headers(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        m = _PATH_LINE.match(bare)
        if m and bare.startswith("/") and not bare.startswith("#"):
            if bare == "/*":
                path = "/weft/*"
            elif bare == "/":
                path = "/weft/"
            elif bare.startswith("/weft"):
                path = bare
            else:
                path = f"/weft{bare}"
            newline = "\n" if line.endswith("\n") else ""
            line = path + newline
        out.append(line)
    return "".join(out)


def rewrite_file(rel: Path, raw: bytes) -> bytes:
    if rel.name == TEXT_HEADERS_NAME:
        return rewrite_headers(raw.decode("utf-8")).encode("utf-8")
    if rel.suffix.lower() in REWRITE_SUFFIXES or rel.suffix == "":
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
        return rewrite_root_paths_in_text(text).encode("utf-8")
    return raw


def copy_weft_tree() -> None:
    weft_root = DIST / "weft"
    if weft_root.exists():
        shutil.rmtree(weft_root)
    weft_root.mkdir(parents=True)
    for src in sorted(SITE.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(SITE).as_posix()
        if should_skip_site_file(rel):
            continue
        dest = weft_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dest.write_bytes(rewrite_file(Path(rel), data))


def fetch_lab_checkout(sha: str, repo_url: str) -> Path:
    cache = ROOT / ".cache" / "siliconcordat-lab" / sha
    if (cache / "docs" / "index.html").is_file():
        return cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        shutil.rmtree(cache)
    subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, str(cache)],
        check=True,
    )
    subprocess.run(["git", "fetch", "origin", sha], cwd=cache, check=True)
    subprocess.run(["git", "checkout", sha], cwd=cache, check=True)
    return cache


def copy_lab_docs(lab_root: Path, docs_sub: str) -> None:
    docs = lab_root / docs_sub
    mapping = [
        (docs / "index.html", DIST / "index.html"),
        (docs / "styles.css", DIST / "styles.css"),
        (docs / "ml" / "index.html", DIST / "ml" / "index.html"),
    ]
    for src, dest in mapping:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    assets_src = docs / "assets"
    assets_dest = DIST / "assets"
    if assets_dest.exists():
        shutil.rmtree(assets_dest)
    shutil.copytree(assets_src, assets_dest)


def build() -> None:
    manifest = load_manifest()
    assert_weft_pin(manifest)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    copy_weft_tree()
    lab = manifest["lab_site"]
    lab_root = fetch_lab_checkout(lab["sha"], lab["repo"] + ".git")
    copy_lab_docs(lab_root, lab["docs_path"])
    print(f"Built {DIST} (weft @ {manifest['weft']['sha'][:12]}, lab @ {lab['sha'][:12]})")


def main() -> None:
    build()


if __name__ == "__main__":
    main()
