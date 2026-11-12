#!/usr/bin/env python3
"""Deterministic English-lexicon lint for the no-language colony.

Two uses:
1. Harness self-check: the designed channel (system prompt, need, tool
   strings) must contain zero blocklist words. Run before every cell.
2. Model leak counting: count blocklist words in a model message, case
   insensitive, word-boundary matched.

This is a blunt instrument, not a language model. It cannot detect grammar,
paraphrase, or non-English natural language. It detects English *words*.
Code-class identifiers are not English words on word-boundary matching for
most stdlib names; the border cases (e.g. "max", "len") are disclosed and
counted anyway, since the harness self-check can simply avoid them.
"""
import re
import sys

BLOCKLIST = """a an and are as at be been but by for from has have he her his i if in into is it its me my
no not of on or she so that the their them then there they this to was we were what which who will
with you your all also any about after again against between both down during each few more most
now once only other some such than too very can cannot could should would shall may might must
when where why how over under out up off here there use uses using used first one two three new old time
well first line lines set make made much same between through world work good bad big small long little
which these those many own same another""".split()

WORD = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]{2,})(?![A-Za-z0-9_])")


def english_hits(text: str) -> list[str]:
    return [m.group(0).lower() for m in WORD.finditer(text) if m.group(0).lower() in BLOCKLIST]


def report(text: str) -> dict:
    hits = english_hits(text)
    return {"n": len(hits), "words": sorted(set(hits))}


def assert_clean(text: str, where: str) -> None:
    hits = english_hits(text)
    if hits:
        raise AssertionError(f"English leak in {where}: {sorted(set(hits))[:10]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: lint.py TEXTFILE", file=sys.stderr)
        sys.exit(2)
    text = open(sys.argv[1], errors="ignore").read()
    hits = english_hits(text)
    print(f"hits={len(hits)} words={sorted(set(hits))[:40]}")
    sys.exit(1 if hits else 0)
