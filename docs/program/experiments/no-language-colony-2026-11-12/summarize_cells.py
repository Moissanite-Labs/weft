#!/usr/bin/env python3
"""Per-cell summary rows computed from the committed jsonl logs only.

Usage: python3 summarize_cells.py [glob ...]   (default: logs/nl-*.jsonl)

Columns: end (step of the `d` call, `max`, or `no finished event`), assay
attempts, accepted assays (harness gate: three runs, positive number, spread
<= 0.15; acceptance measures stability, not objective validity), variants
tool calls, adoptions (variants_result with adopted not null), and output
tokens summed from usage events.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def summarize(path):
    ev = [json.loads(l) for l in open(path) if l.strip()]
    fin = [e for e in ev if e.get("kind") == "finished"]
    assays = [e for e in ev if e.get("kind") == "assay"]
    return {
        "cell": Path(path).stem,
        "end": str(fin[-1]["step"]) if fin else "no finished event",
        "assays": len(assays),
        "accepted": sum(1 for e in assays if e.get("ok")),
        "variants_calls": sum(1 for e in ev if e.get("kind") == "tool_call" and e.get("name") == "v"),
        "adoptions": sum(1 for e in ev if e.get("kind") == "variants_result" and e.get("adopted") is not None),
        "out_tokens": sum(e.get("output_tokens", 0) for e in ev if e.get("kind") == "usage"),
    }


def main():
    pats = sys.argv[1:] or [str(ROOT / "logs" / "nl-*.jsonl")]
    files = sorted(f for p in pats for f in glob.glob(p))
    print("| cell | end | assays accepted/attempted | variants calls | adoptions | output tokens |")
    print("|---|---|---|---|---|---|")
    for f in files:
        r = summarize(f)
        print(f"| {r['cell']} | {r['end']} | {r['accepted']}/{r['assays']} | {r['variants_calls']} | {r['adoptions']} | {r['out_tokens']:,} |")


if __name__ == "__main__":
    main()
