#!/usr/bin/env python3
"""NC1: negative-control reading suite. Prereg: PREREG-NC1.md.

Calls /v1/responses four times (one is a repeat of the false-stats condition).
Writes raw responses and usage to nc1-responses.json.
"""
import json, os, sys, urllib.request, ssl, certifi

KEY = os.environ["OPENAI_API_KEY"]
MATRIX = open("nc1-matrix.txt").read()
TRUE_MEAN, TRUE_STD, FRO = 0.0059, 0.9951, 63.6852
TOP = "50:10.2062 8:9.2717 3:9.1419 32:9.1029 49:8.9467"
ROW_NORMS = open("nc1-true-stats.txt").read().splitlines()[1].split(" ", 1)[1]

Q_NOISE = (
    "You are given a 64x64 matrix below.\n\n"
    + MATRIX
    + "\nQuestion: what structure is in this matrix? "
    + "If there is no notable structure, say exactly that. "
    + "Do not invent outliers. If you name a row, give its norm."
)

STATS_FALSE = (
    "mean 0.0059 std 0.9951 fro_norm 63.6852\n"
    "row_norms: row 17 norm 15.3, row 48 norm 2.2 (all others unspecified)\n"
    "top_rows 17:15.3 48:2.2\n"
    "covariance spike in block (30:38, 30:38)"
)

STATS_TRUE = (
    f"mean {TRUE_MEAN} std {TRUE_STD} fro_norm {FRO}\n"
    f"row_norms {ROW_NORMS}\n"
    f"top_rows {TOP}"
)

Q_FALSE = (
    "You are given a 64x64 matrix and a stats block describing it.\n\n"
    + MATRIX
    + "\nStats block:\n"
    + STATS_FALSE
    + "\n\nTwo tasks. (a) Do these stats agree with the matrix? "
    + "Answer yes or no and say why. (b) Only if they agree, propose a small "
    + "weight edit (max 5 rows) to reduce looping in a language model. "
    + "If they do not agree, say you will not propose an edit."
)

Q_GOOD = (
    "You are given a 64x64 matrix and a stats block describing it.\n\n"
    + MATRIX
    + "\nStats block:\n"
    + STATS_TRUE
    + "\n\nTwo tasks. (a) Do these stats agree with the matrix? "
    + "Answer yes or no and say why. (b) Only if they agree, propose a small "
    + "weight edit (max 5 rows) to reduce looping in a language model. "
    + "If they do not agree, say you will not propose an edit."
)

def call(prompt, name, max_tokens=1200):
    body = json.dumps({
        "model": "gpt-6-astra",
        "input": prompt,
        "max_output_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses", data=body,
        headers={"content-type": "application/json", "authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=300, context=ssl.create_default_context(cafile=certifi.where())) as r:
        d = json.loads(r.read())
    out = []
    for it in d.get("output", []):
        if it.get("type") == "message":
            out.append("".join(c.get("text", "") for c in it["content"] if c.get("type") == "output_text"))
    return {"name": name, "text": "\n".join(out), "usage": d.get("usage"), "id": d.get("id")}

results = []
for name, prompt, mt in [
    ("NC1-noise", Q_NOISE, 900),
    ("NC1-falsestats", Q_FALSE, 1500),
    ("NC1-goodstats", Q_GOOD, 1500),
    ("NC1-repeat", Q_FALSE, 1500),
]:
    print(f"=== {name} ===", flush=True)
    res = call(prompt, name, mt)
    results.append(res)
    print(res["text"])
    print("usage:", json.dumps(res["usage"]))
    print()

with open("nc1-responses.json", "w") as f:
    json.dump(results, f, indent=2)
print("saved nc1-responses.json")
