"""tj3_data.py: turn cell experience (shell command -> what the sandbox did) into a small supervised set.
Written 2026-11-10 before any T-J3 training data exists. No model calls. Reads log.jsonl only.
Usage: python tj3_data.py EXP_DIR OUT.json
Split is by RUN (never by row), so held-out rows come from colonies the adapter never saw.
Scrubbing: home path replaced, any key-shaped string dropped, rows over 400 chars dropped."""
import json, glob, os, re, sys, hashlib, collections
EXP, OUT = sys.argv[1], sys.argv[2]
SKIP = ("s3", "sp3")                      # SP3 is running or reserved; never used here
KEY = re.compile(r"(sk-|Bearer |AIza|ghp_|github_pat_|tml-)[A-Za-z0-9_\-]{8,}")
HOME = re.compile(r"/Users/[A-Za-z0-9_\-]+")
def scrub(s): return HOME.sub("/home/cell", s)
def label(res):
    m = re.match(r"\s*exit (-?\d+)", res)
    code = int(m.group(1)) if m else None
    if code is None: return None
    if code == 0: return "ok"
    if "No such file" in res: return "fail no_such_file"
    if "Not a directory" in res: return "fail not_a_directory"
    if "Operation not permitted" in res: return "fail not_permitted"
    if re.search(r"(^|\n)sed: ", res): return "fail sed"
    if "Traceback" in res: return "fail traceback"
    if "timed out" in res.lower(): return "fail timeout"
    return "fail other"
rows, dropped = [], collections.Counter()
for f in sorted(glob.glob(os.path.join(EXP, "*", "*", "log.jsonl"))):
    run = f.split(os.sep)[-3]
    if run.startswith(SKIP): continue
    for line in open(f, errors="replace"):
        try: e = json.loads(line)
        except Exception: continue
        a = e.get("act")
        if not (isinstance(a, dict) and a.get("do") == "sh" and isinstance(a.get("cmd"), str) and isinstance(e.get("res"), str)):
            continue
        cmd, lab = a["cmd"], label(e["res"])
        if lab is None: dropped["no_exit_line"] += 1; continue
        if KEY.search(cmd): dropped["key_shaped"] += 1; continue
        cmd = scrub(cmd)
        if len(cmd) > 400: dropped["too_long"] += 1; continue
        rows.append({"run": run, "cmd": cmd, "label": lab})
def bucket(run):                           # fixed by hash of the run name, not by eye
    h = int(hashlib.sha256(run.encode()).hexdigest(), 16) % 10
    return "test" if h < 2 else "gate" if h < 4 else "train"
seen, out = set(), {"train": [], "gate": [], "test": []}
for r in rows:
    k = (r["cmd"], r["label"])
    if k in seen: dropped["duplicate"] += 1; continue
    seen.add(k); out[bucket(r["run"])].append(r)
# a command text that appears in train must not also sit in gate or test
tr = {r["cmd"] for r in out["train"]}
for s in ("gate", "test"):
    keep = [r for r in out[s] if r["cmd"] not in tr]; dropped["leak_" + s] += len(out[s]) - len(keep); out[s] = keep
g = {r["cmd"] for r in out["gate"]}
keep = [r for r in out["test"] if r["cmd"] not in g]; dropped["leak_test_gate"] += len(out["test"]) - len(keep); out["test"] = keep
json.dump(out, open(OUT, "w"), indent=0)
print("rows", {s: len(v) for s, v in out.items()}, "dropped", dict(dropped))
for s, v in out.items():
    c = collections.Counter(r["label"] for r in v); n = max(len(v), 1)
    print(s, "runs", len({r["run"] for r in v}), "ok share", round(c["ok"] / n, 3), dict(c.most_common()))
print("sha256", hashlib.sha256(open(OUT, "rb").read()).hexdigest()[:16])
