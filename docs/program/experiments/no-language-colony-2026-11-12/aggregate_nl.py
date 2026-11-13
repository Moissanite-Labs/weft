#!/usr/bin/env python3
"""Aggregate Stage-1 no-language smoke cells into RESULTS-NL.md table rows."""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLOCK = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]+)(?![A-Za-z0-9_])")
BLOCKLIST = set("a an and are as at be been but by for from has have he her his i if in into is it its me my no not of on or she so that the their them then there they this to was we were what which who will with you your all also any about after again between both down during each few more most now once only other some such than too very can cannot could should would shall may might must when where why how over under out up off here there use uses using used first one two three new old time well lines set make made much same world work good bad big small long little many own".split())


def leak_count(text):
    return sum(1 for m in BLOCK.finditer(text or "") if m.group(1).lower() in BLOCKLIST)


def analyze(f):
    events = [json.loads(l) for l in open(f)]
    cell = events[0].get("profile") and (f.split("/")[-1][:-6])
    in_tok = out_tok = calls = vcalls = 0
    assay_reg = False
    assay_ok = False
    wins = 0
    done = False
    schema_err = 0
    max_leak = 0
    parse_fail = 0
    for e in events:
        k = e.get("kind")
        if k == "usage":
            in_tok += e.get("input_tokens", 0)
            out_tok += e.get("output_tokens", 0)
            calls += 1
        elif k == "assay":
            max_leak = max(max_leak, leak_count(e.get("command", "")))
            assay_reg = True
            if e.get("ok"):
                assay_ok = True
        elif k == "variants_result" and e.get("adopted") is not None:
            wins += 1
        elif k == "variant":
            pass
        elif k == "write":
            pass
        elif k == "turn":
            u = e.get("usage") or {}
            in_tok += u.get("input_tokens", 0)
            out_tok += u.get("output_tokens", 0)
            calls += 1
            if not e.get("parsed", True):
                parse_fail += 1
        elif k == "model_turn":
            max_leak = max(max_leak, len(e.get("leak_words", [])))
        elif k == "schema_error":
            schema_err += 1
        elif k == "finished":
            done = e.get("reason") != "max" or e.get("wins", 0) >= 0
    return {"cell": cell, "calls": calls, "in_tok": in_tok, "out_tok": out_tok,
            "assay_reg": assay_reg, "assay_ok": assay_ok, "wins": wins,
            "schema_err": schema_err, "max_leak": max_leak, "len": len(events)}


def main():
    for f in sorted(glob.glob(str(ROOT / "logs" / "nl-*.jsonl")) + glob.glob(str(ROOT / "logs" / "ollama-*.jsonl"))):
        a = analyze(f)
        print(json.dumps(a))


if __name__ == "__main__":
    main()
