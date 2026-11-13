import json, os, urllib.request, ssl, certifi

KEY = os.environ["OPENAI_API_KEY"]
MATRIX = open("nc1-matrix.txt").read()
TRUE_MEAN, TRUE_STD, FRO = 0.0059, 0.9951, 63.6852
TOP = "50:10.2062 8:9.2717 3:9.1419 32:9.1029 49:8.9467"
ROW_NORMS = open("nc1-true-stats.txt").read().splitlines()[1].split(" ", 1)[1]

STATS_TRUE = (
    f"mean {TRUE_MEAN} std {TRUE_STD} fro_norm {FRO}\n"
    f"row_norms {ROW_NORMS}\n"
    f"top_rows {TOP}"
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

body = json.dumps({"model": "gpt-6-astra", "input": Q_GOOD, "max_output_tokens": 3200}).encode()
req = urllib.request.Request(
    "https://api.openai.com/v1/responses", data=body,
    headers={"content-type": "application/json", "authorization": f"Bearer {KEY}"})
with urllib.request.urlopen(req, timeout=300, context=ssl.create_default_context(cafile=certifi.where())) as r:
    d = json.loads(r.read())
out = []
for it in d.get("output", []):
    if it.get("type") == "message":
        out.append("".join(c.get("text", "") for c in it["content"] if c.get("type") == "output_text"))
print("\n".join(out))
print("\nusage:", json.dumps(d.get("usage")))
with open("nc1-goodstats-full.txt", "w") as f:
    f.write("\n".join(out))
