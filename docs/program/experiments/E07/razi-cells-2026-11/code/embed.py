"""Embedding analysis of cell code versions (IDEAS E1, E5).

usage: embed.py RUN_DIR [RUN_DIR ...]
Reads <run>/<need>/variants.jsonl, embeds code with local ollama nomic-embed-text,
caches vectors in <run>/<need>/vectors.json, then prints:
  E1  per variants batch: mean pairwise distance vs best gain over incumbent
  E5  per need: distance between runs' centroids (model fingerprint), and spread per run
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import urllib.request
from itertools import combinations
from pathlib import Path

import os

URL = "http://localhost:11434/api/embed"
# EMBED_MODEL: "nomic-embed-text" (local ollama) or "openai:text-embedding-3-small|large".
MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
_key = None


def _openai_key() -> str:
    """Key comes from Exo's router credentials, in process only; never printed or written."""
    global _key
    if _key is None:
        from exo.config import Config
        from exo.core.models.router import Router
        _key = Router.from_config(Config.load().models()).credentials("openai")[0].key
    return _key


def embed(texts: list[str]) -> list[list[float]]:
    texts = [t[:8000] or " " for t in texts]
    if MODEL.startswith("openai:"):
        body = json.dumps({"model": MODEL.split(":", 1)[1], "input": texts}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/embeddings", body,
                                     {"Content-Type": "application/json", "Authorization": "Bearer " + _openai_key()})
        with urllib.request.urlopen(req, timeout=120) as r:
            return [d["embedding"] for d in sorted(json.load(r)["data"], key=lambda d: d["index"])]
    body = json.dumps({"model": MODEL, "input": texts}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["embeddings"]


def cos_dist(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return 1 - dot / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))


def centroid(vs):
    return [sum(c) / len(vs) for c in zip(*vs)]


def load(need_dir: Path) -> list[dict]:
    f = need_dir / "variants.jsonl"
    if not f.exists():
        return []
    recs = [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
    cache_f = need_dir / f"vectors.{MODEL.replace(':', '_')}.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    key = lambda r: hashlib.sha1(r["code"].encode()).hexdigest()
    todo = list({key(r): r["code"] for r in recs if key(r) not in cache}.items())
    for i in range(0, len(todo), 16):
        chunk = todo[i:i + 16]
        for (k, _), v in zip(chunk, embed([c for _, c in chunk])):
            cache[k] = v
    cache_f.write_text(json.dumps(cache))
    for r in recs:
        r["vec"] = cache[key(r)]
    return recs


def main(runs: list[Path]) -> None:
    by_need: dict[str, dict[str, list[dict]]] = {}
    print("E1 batch spread vs gain  (run need n spread best_gain adopted)")
    for run in runs:
        for nd in sorted(p for p in run.iterdir() if p.is_dir()):
            recs = load(nd)
            if not recs:
                continue
            by_need.setdefault(nd.name, {})[run.name] = recs
            batch = []
            for r in recs + [None]:
                if r is not None and r["kind"] == "variant" and (not batch or r["t"] - batch[-1]["t"] < 1):
                    batch.append(r)
                    continue
                if len(batch) >= 2 and batch[0].get("incumbent"):
                    spread = sum(cos_dist(a["vec"], b["vec"]) for a, b in combinations(batch, 2)) / math.comb(len(batch), 2)
                    best = max((b["score"] or 0) for b in batch)
                    gain = best / batch[0]["incumbent"] - 1
                    print(f"  {run.name:6} {nd.name:9} {len(batch)} {spread:.4f} {gain:+.3f} {any(b['adopted'] for b in batch)}")
                batch = [r] if r is not None and r["kind"] == "variant" else []
    print("E5 model fingerprints  (need: run spread | centroid distances)")
    for need, rr in sorted(by_need.items()):
        cents = {k: centroid([r["vec"] for r in v]) for k, v in rr.items()}
        spread = {k: sum(cos_dist(r["vec"], cents[k]) for r in v) / len(v) for k, v in rr.items()}
        pairs = " ".join(f"{a}-{b}={cos_dist(cents[a], cents[b]):.4f}" for a, b in combinations(sorted(cents), 2))
        print(f"  {need:9} " + " ".join(f"{k}:{s:.4f}" for k, s in spread.items()) + (" | " + pairs if pairs else ""))


if __name__ == "__main__":
    main([Path(a) for a in sys.argv[1:]])
