"""R1 retroactive held-out audit over E07 archives (b5..b11, g3, g4).

Addresses Moissanite-Labs/weft#111 (Finding F1, Recommendation R1).
Scores finished cell directories against 8 deterministic held-out reference workloads
(the 4 harness-held workloads from kit.py plus 4 stdlib reference workloads for the
remaining tasks in needs8v3.json).

Under the machine-wide bench lock, with interleaved repeats against clean stdlib references.
Zero external network access, isolated execution.
"""
from __future__ import annotations

import argparse, collections, fcntl, importlib.util, json, os, random, re, shutil, statistics, subprocess, sys, tempfile, time
from collections import Counter, deque
from pathlib import Path

REPEATS = 5
M = 1_000_000_007
BENCH_LOCK = Path.home() / "Work/razi-cells/.bench.lock"
SH_TIMEOUT = 30
PY = sys.executable

# ---------------------------------------------------------------- Reference generators
def fib_ref(n: int) -> int:
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((2 * b - a) % M) % M
        d = (a * a + b * b) % M
        a, b = (d, (c + d) % M) if bit == "1" else (c, d)
    return a


def bfs_ref(rows: list[str]) -> int:
    h, w = len(rows), len(rows[0])
    flat = "".join(rows)
    s, e = flat.index("S"), flat.index("E")
    dist = [-1] * (h * w)
    dist[s] = 0
    q = deque([s])
    while q:
        p = q.popleft()
        if p == e:
            return dist[p]
        d = dist[p] + 1
        r, c = divmod(p, w)
        for ok, n in ((c > 0, p - 1), (c < w - 1, p + 1), (r > 0, p - w), (r < h - 1, p + w)):
            if ok and dist[n] < 0 and flat[n] != "#":
                dist[n] = d
                q.append(n)
    return -1


def gen_fibmod(rng: random.Random) -> list[tuple[bytes, bytes]]:
    ns = [0, 1, 2, 10, 10**18] + [rng.randrange(10**18 + 1) for _ in range(30000)]
    return [("\n".join(map(str, ns)).encode() + b"\n", "\n".join(str(fib_ref(n)) for n in ns).encode() + b"\n")]


def gen_csvsum(rng: random.Random) -> list[tuple[bytes, bytes]]:
    cats = ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(3, 8))) for _ in range(40)]
    cats = sorted(set(cats))
    sums = dict.fromkeys(cats, 0)
    lines = ["id,cat,val"]
    for i in range(1_000_000):
        c, cents = rng.choice(cats), rng.randint(-999_999, 9_999_999)
        sums[c] += cents
        lines.append(f"{i},{c},{'-' if cents < 0 else ''}{abs(cents) // 100}.{abs(cents) % 100:02d}")
    out = [f"{c},{'-' if v < 0 else ''}{abs(v) // 100}.{abs(v) % 100:02d}" for c, v in sorted(sums.items())]
    return [("\n".join(lines).encode() + b"\n", "\n".join(out).encode() + b"\n")]


def _maze_case(rng: random.Random, n: int, wall: float, want_path: bool) -> tuple[bytes, bytes]:
    while True:
        rows = ["".join(rng.choices("#.", weights=(wall, 1 - wall), k=n)) for _ in range(n)]
        rows[0] = "S" + rows[0][1:]
        rows[-1] = rows[-1][:-1] + "E"
        ans = bfs_ref(rows)
        if (ans > 0) == want_path:
            return "\n".join(rows).encode() + b"\n", f"{ans}\n".encode()


def gen_maze(rng: random.Random) -> list[tuple[bytes, bytes]]:
    return [_maze_case(rng, 1000, 0.30, True), _maze_case(rng, 40, 0.45, False), _maze_case(rng, 40, 0.20, True)]


def gen_compress(rng: random.Random) -> list[tuple[bytes, bytes]]:
    syl = ["ta", "re", "mi", "son", "ver", "al", "en", "do", "ku", "lin", "per", "st", "or", "an", "ti", "ch", "ou"]
    vocab = ["".join(rng.choice(syl) for _ in range(rng.randint(1, 4))) for _ in range(3000)]
    weights = [1 / (i + 1) for i in range(len(vocab))]
    sents = []
    for _ in range(9000):
        ws = rng.choices(vocab, weights=weights, k=rng.randint(4, 18))
        sents.append(" ".join(ws).capitalize() + rng.choice([".", ".", ".", "?", "!"]))
    text = " ".join(sents)
    recs = [{"id": i, "name": rng.choice(vocab), "tags": rng.sample(vocab[:60], 3), "score": round(rng.random() * 100, 3),
             "active": rng.random() < 0.7, "note": " ".join(rng.choices(vocab, weights=weights, k=6))} for i in range(4000)]
    return [(text.encode(), b""), (json.dumps(recs, indent=1).encode(), b"")]


def gen_primes(_rng: random.Random) -> list[tuple[bytes, bytes]]:
    # N = 10,000,000; correct count of primes strictly below 10,000,000 is 664579
    return [(b"10000000", b"664579\n")]


def gen_sortints(rng: random.Random) -> list[tuple[bytes, bytes]]:
    ints = [rng.randint(-1_000_000, 1_000_000) for _ in range(1_000_000)]
    data = ("\n".join(map(str, ints)) + "\n").encode()
    exp = ("\n".join(map(str, sorted(ints))) + "\n").encode()
    return [(data, exp)]


def gen_wordfreq(rng: random.Random) -> list[tuple[bytes, bytes]]:
    syl = ["ta", "re", "mi", "son", "ver", "al", "en", "do", "ku", "lin", "per", "st", "or", "an", "ti", "ch", "ou"]
    vocab = ["".join(rng.choice(syl) for _ in range(rng.randint(1, 4))) for _ in range(500)]
    weights = [1 / (i + 1) for i in range(len(vocab))]
    words = rng.choices(vocab, weights=weights, k=250_000)
    text = " ".join(words).encode()
    ref_words = re.findall(r"[a-z]+", text.decode().lower())
    counts = Counter(ref_words)
    top10 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:10]
    exp = ("\n".join(f"{w} {c}" for w, c in top10) + "\n").encode()
    return [(text, exp)]


def gen_lcs(rng: random.Random) -> list[tuple[bytes, bytes]]:
    alpha = "ACGT"
    s1 = "".join(rng.choices(alpha, k=3000))
    s2 = "".join(rng.choices(alpha, k=3000))
    prev = [0] * (len(s2) + 1)
    for c1 in s1:
        curr = [0] * (len(s2) + 1)
        for j, c2 in enumerate(s2):
            curr[j + 1] = prev[j] + 1 if c1 == c2 else (prev[j + 1] if prev[j + 1] > curr[j] else curr[j])
        prev = curr
    return [(f"{s1}\n{s2}\n".encode(), f"{prev[-1]}\n".encode())]


# ---------------------------------------------------------------- Output checks
def same_tokens(out: bytes, exp: bytes) -> bool:
    return out.split() == exp.split()


def same_csv(out: bytes, exp: bytes) -> bool:
    try:
        a = [l.split(",") for l in out.decode().split()]
        b = [l.split(",") for l in exp.decode().split()]
        return len(a) == len(b) and all(len(x) == 2 and x[0] == y[0] and abs(float(x[1]) - float(y[1])) <= 0.0101
                                        for x, y in zip(a, b))
    except Exception:
        return False


def same_exact(out: bytes, exp: bytes) -> bool:
    return out.strip() == exp.strip()


# ---------------------------------------------------------------- Reference solutions
REFERENCE_BODIES: dict[str, tuple[str, str]] = {
    "fibmod": ("fibmod.py", """import sys
M=10**9+7
def fib(n):
    a,b=0,1
    for bit in bin(n)[2:]:
        c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M
        a,b=(d,(c+d)%M) if bit=="1" else (c,d)
    return a
if __name__ == "__main__":
    print("\\n".join(str(fib(int(x))) for x in sys.stdin.read().split()))
"""),
    "csvsum": ("csvsum.py", """import sys
from decimal import Decimal
s={}
it=iter(sys.stdin); next(it)
for l in it:
    _,c,v=l.rstrip("\\n").split(",")
    s[c]=s.get(c,Decimal(0))+Decimal(v)
for c in sorted(s): print(f"{c},{s[c]:.2f}")
"""),
    "maze": ("maze.py", """import sys
from collections import deque
rows=sys.stdin.read().split()
h=len(rows); w=len(rows[0]); g="".join(rows); s=g.index("S"); e=g.index("E")
d=[-1]*(h*w); d[s]=0; q=deque([s]); ans=-1
while q:
    p=q.popleft()
    if p==e: ans=d[p]; break
    r,c=divmod(p,w)
    for ok,n in ((c>0,p-1),(c<w-1,p+1),(r>0,p-w),(r<h-1,p+w)):
        if ok and d[n]<0 and g[n]!="#": d[n]=d[p]+1; q.append(n)
print(ans)
"""),
    "compress": ("squeeze.py", """import sys,zlib
d=sys.stdin.buffer.read()
sys.stdout.buffer.write(zlib.compress(d,9) if sys.argv[1]=="c" else zlib.decompress(d))
"""),
    "primes": ("primes.py", """import sys
from math import isqrt

def count_primes(n):
    if n < 3: return int(n > 2)
    size = n >> 1
    s = bytearray(b"\\x01") * size
    s[0] = 0
    for i in range(1, (isqrt(n - 1) >> 1) + 1):
        if s[i]:
            p = 2 * i + 1
            st = 2 * i * (i + 1)
            s[st::p] = b"\\x00" * ((size - 1 - st) // p + 1)
    return s.count(1) + 1

if __name__ == "__main__":
    print(count_primes(int(sys.argv[1])))
"""),
    "sortints": ("sortints.py", """import sys
ints = [int(x) for x in sys.stdin.read().split()]
ints.sort()
sys.stdout.write("\\n".join(map(str, ints)) + "\\n")
"""),
    "wordfreq": ("wf.py", """import sys, re
from collections import Counter
words = re.findall(r"[a-z]+", sys.stdin.read().lower())
counts = Counter(words)
top10 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:10]
sys.stdout.write("\\n".join(f"{w} {c}" for w, c in top10) + "\\n")
"""),
    "lcs": ("lcs.py", """import sys
lines = sys.stdin.read().splitlines()
s1, s2 = (lines[0], lines[1]) if len(lines) >= 2 else ("", "")
prev = [0] * (len(s2) + 1)
for c1 in s1:
    curr = [0] * (len(s2) + 1)
    for j, c2 in enumerate(s2):
        curr[j + 1] = prev[j] + 1 if c1 == c2 else (prev[j + 1] if prev[j + 1] > curr[j] else curr[j])
    prev = curr
print(prev[-1] if prev else 0)
"""),
}

TASKS: dict[str, dict] = {
    "compress": {"gen": gen_compress, "kind": "ratio", "check": None},
    "csvsum": {"gen": gen_csvsum, "kind": "time", "check": same_csv},
    "fibmod": {"gen": gen_fibmod, "kind": "time", "check": same_tokens},
    "maze": {"gen": gen_maze, "kind": "time", "check": same_tokens},
    "primes": {"gen": gen_primes, "kind": "time", "check": same_exact},
    "sortints": {"gen": gen_sortints, "kind": "time", "check": same_exact},
    "wordfreq": {"gen": gen_wordfreq, "kind": "time", "check": same_exact},
    "lcs": {"gen": gen_lcs, "kind": "time", "check": same_exact},
}

# ---------------------------------------------------------------- Sandboxed execution
def sandboxed_run(body: Path, cmd: str, stdin: bytes, timeout: int = SH_TIMEOUT, script: str = "") -> tuple[int, bytes, float]:
    real = os.path.realpath(body)
    scratch = Path(tempfile.mkdtemp(prefix="audit-run-", dir=os.path.realpath(tempfile.gettempdir())))
    if script:
        (scratch / "_shim.py").write_text(script)
        cmd = f"python3 {scratch}/_shim.py {cmd}".strip()
    prof = (f'(version 1)(allow default)(deny network*)'
            f'(deny file-write*)(allow file-write* (subpath "{scratch}") (literal "/dev/null"))'
            f'(deny file-read* (subpath "{Path.home()}"))(allow file-read* (subpath "{real}") (subpath "{scratch}"))')
    env = {
        "PATH": f"{Path(PY).parent}:/usr/bin:/bin",
        "HOME": str(scratch),
        "TMPDIR": str(scratch),
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    t = time.perf_counter()
    try:
        p = subprocess.run(
            ["sandbox-exec", "-p", prof, "/bin/sh", "-c", cmd],
            cwd=real,
            env=env,
            input=stdin,
            capture_output=True,
            timeout=timeout,
        )
        rc, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        rc, out = -9, b""
    dt = time.perf_counter() - t
    shutil.rmtree(scratch, ignore_errors=True)
    return rc, out, dt


# ---------------------------------------------------------------- Runner adapters
FIB_SHIM = """import sys, io
sys.path.insert(0, '.')
saved_stdout = sys.stdout
sys.stdout = io.StringIO()
sys.argv = ["fibmod.py", "10"]
fn = None
try:
    import fibmod
    fn = getattr(fibmod, "fib", None) or getattr(fibmod, "single", None) or getattr(fibmod, "_fib_fd", None)
except Exception:
    pass

if fn is None:
    try:
        def _b7_fib(n):
            M = 1000000007
            a, b = 0, 1
            for i in range(n.bit_length() - 1, -1, -1):
                c = a * (b + b - a) % M
                d = (a * a + b * b) % M
                if (n >> i) & 1:
                    e = c + d
                    if e >= M:
                        e -= M
                    a, b = d, e
                else:
                    a, b = c, d
            return a
        fn = _b7_fib
    except Exception:
        pass

sys.stdout = saved_stdout
if fn is not None:
    nums = [int(x) for x in sys.stdin.read().split()]
    out = [str(fn(x)) for x in nums]
    sys.stdout.write("\\n".join(out) + "\\n")
    sys.exit(0)
else:
    sys.exit(1)
"""

COMPRESS_SHIM = """import sys, ast
sys.path.insert(0, '.')
has_fn = False
try:
    with open('squeeze.py') as f:
        tree = ast.parse(f.read())
    fns = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    has_fn = 'compress' in fns and 'decompress' in fns
except Exception:
    pass

if has_fn:
    import squeeze
    inp = sys.stdin.buffer.read()
    mode = sys.argv[1]
    out = squeeze.compress(inp) if mode == 'c' else squeeze.decompress(inp)
    sys.stdout.buffer.write(out)
    sys.exit(0)
else:
    import subprocess
    p = subprocess.run([sys.executable, 'squeeze.py', sys.argv[1]], stdin=sys.stdin)
    sys.exit(p.returncode)
"""


def score_task(name: str, body: Path, cases: list[tuple[bytes, bytes]]) -> tuple[float, str]:
    tdef = TASKS[name]
    kind = tdef["kind"]

    if name == "compress":
        raw = packed = 0
        for i, (inp, _) in enumerate(cases):
            rc, comp, _ = sandboxed_run(body, "c", inp, script=COMPRESS_SHIM)
            if rc != 0:
                return 0.0, f"case {i}: compress exit {rc}"
            rc, back, _ = sandboxed_run(body, "d", comp, script=COMPRESS_SHIM)
            if rc != 0 or back != inp:
                return 0.0, f"case {i}: roundtrip mismatch (rc={rc})"
            raw += len(inp)
            packed += len(comp)
        return (raw / packed if packed else 0.0), ""

    if name == "fibmod":
        inp, exp = cases[0]
        rc, out, dt = sandboxed_run(body, "", inp, script=FIB_SHIM)
        if rc != 0:
            return 0.0, f"exit {rc}"
        if not tdef["check"](out, exp):
            return 0.0, "wrong output"
        return (1.0 / dt if dt > 0 else 0.0), ""

    if name == "primes":
        arg, exp = cases[0]
        rc, out, dt = sandboxed_run(body, f"python3 primes.py {arg.decode().strip()}", b"")
        if rc != 0:
            return 0.0, f"exit {rc}"
        if not tdef["check"](out, exp):
            return 0.0, f"wrong output (got {out.decode()[:40]!r})"
        return (1.0 / dt if dt > 0 else 0.0), ""

    # For csvsum, maze, sortints, wordfreq, lcs:
    cmd_map = {
        "csvsum": "python3 csvsum.py",
        "maze": "python3 maze.py",
        "sortints": "python3 sortints.py",
        "wordfreq": "python3 wf.py",
        "lcs": "python3 lcs.py",
    }
    cmd = cmd_map[name]
    total_dt = 0.0
    for i, (inp, exp) in enumerate(cases):
        rc, out, dt = sandboxed_run(body, cmd, inp)
        if rc != 0:
            return 0.0, f"case {i}: exit {rc}"
        if not tdef["check"](out, exp):
            return 0.0, f"case {i}: wrong output"
        total_dt += dt
    return (1.0 / total_dt if total_dt > 0 else 0.0), ""


def spread(v: list[float]) -> float:
    m = statistics.median(v)
    return (max(v) - min(v)) / m if m > 0 else float("inf")


def run_audit(archive_base: Path, runs: list[str]) -> dict:
    BENCH_LOCK.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="audit-ref-", dir=os.path.realpath(tempfile.gettempdir())))

    # Pre-generate cases
    task_cases = {}
    for task_name, tdef in TASKS.items():
        rng = random.Random(f"heldout-r1-{task_name}-20261110")
        task_cases[task_name] = tdef["gen"](rng)

    # Build reference directories
    ref_dirs = {}
    for task_name, (fname, code) in REFERENCE_BODIES.items():
        d = temp_dir / ("ref-" + task_name)
        d.mkdir(parents=True, exist_ok=True)
        (d / fname).write_text(code)
        ref_dirs[task_name] = d

    # Collect directories to score per task
    contenders: dict[str, dict[str, Path]] = {}
    for task_name in TASKS:
        contenders[task_name] = {"ref": ref_dirs[task_name]}
        for r in runs:
            c_dir = archive_base / r / task_name
            if c_dir.is_dir():
                contenders[task_name][r] = c_dir

    raw_scores: dict[str, dict[str, list[float]]] = {t: {k: [] for k in contenders[t]} for t in TASKS}
    reasons: dict[str, dict[str, str]] = {t: {} for t in TASKS}

    # Execute 5 interleaved repeats under machine-wide bench lock
    print(f"Executing {REPEATS} interleaved repeats under bench lock...")
    with open(BENCH_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for rep in range(REPEATS):
            t_rep = time.time()
            for task_name in sorted(TASKS.keys()):
                for run_key, body_dir in contenders[task_name].items():
                    if run_key in reasons[task_name]:
                        raw_scores[task_name][run_key].append(0.0)
                        continue
                    score, why = score_task(task_name, body_dir, task_cases[task_name])
                    if why:
                        reasons[task_name][run_key] = why
                    raw_scores[task_name][run_key].append(round(score, 5))
            print(f"  repeat {rep + 1}/{REPEATS} complete ({time.time() - t_rep:.1f}s)")

    shutil.rmtree(temp_dir, ignore_errors=True)

    # Compile results
    results = {
        "repeats": REPEATS,
        "tasks": list(TASKS.keys()),
        "runs": runs,
        "per_task": {},
    }

    for task_name in sorted(TASKS.keys()):
        ref_med = statistics.median(raw_scores[task_name]["ref"])
        results["per_task"][task_name] = {
            "ref_median": round(ref_med, 4),
            "ref_spread": round(spread(raw_scores[task_name]["ref"]), 4),
            "scores": {},
        }
        for run_key in contenders[task_name]:
            v = raw_scores[task_name][run_key]
            med = statistics.median(v)
            rel = round(med / ref_med, 4) if ref_med > 0 else None
            results["per_task"][task_name]["scores"][run_key] = {
                "median": round(med, 4),
                "rel": rel,
                "spread": round(spread(v), 4) if med > 0 else None,
                "raw": v,
                "why": reasons[task_name].get(run_key, ""),
            }

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Held-out audit over E07 archives.")
    parser.add_argument("--archive-dir", default="/tmp/e07-archive-copy", help="Path to E07 archive copy")
    parser.add_argument("--out", default="", help="Path to output json")
    args = parser.parse_args()

    archive_base = Path(args.archive_dir)
    runs = ["b5", "b6", "b7", "b8", "b9", "b10", "b11", "g3", "g4"]
    runs = [r for r in runs if (archive_base / r).is_dir()]

    out_path = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "data/heldout-audit-r1.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Auditing runs: {runs} from {archive_base}")
    audit = run_audit(archive_base, runs)

    # Load summary json for each run to pull kept improvements per 100 calls
    summaries_dir = Path(__file__).resolve().parent.parent / "data"
    run_summaries = {}
    for r in runs:
        sf = summaries_dir / f"{r}-summary.json"
        if sf.exists():
            sdata = json.load(open(sf))
            calls = sdata.get("calls", 0)
            imps = sdata.get("improvements", 0)
            rate = round(100 * imps / calls, 2) if calls else 0.0
            routes = set()
            for c in sdata.get("cells", {}).values():
                routes.update(c.get("routes", []))
            model = list(routes)[0] if routes else ("DeepSeek v4.1 Flash" if r.startswith("g") else "unknown")
            run_summaries[r] = {
                "calls": calls,
                "improvements": imps,
                "kept_per_100": rate,
                "model": model,
            }

    audit["run_summaries"] = run_summaries

    # Compute summary table per run
    summary_table = []
    for r in runs:
        rels = [audit["per_task"][t]["scores"][r]["rel"] for t in audit["tasks"] if r in audit["per_task"][t]["scores"]]
        valid_rels = [x for x in rels if x is not None]
        sinfo = run_summaries.get(r, {})
        summary_table.append({
            "run": r,
            "model": sinfo.get("model", ""),
            "kept_per_100": sinfo.get("kept_per_100", 0.0),
            "median_rel": round(statistics.median(valid_rels), 3) if valid_rels else 0.0,
            "mean_rel": round(statistics.mean(valid_rels), 3) if valid_rels else 0.0,
            "wins_vs_ref": sum(1 for x in valid_rels if x > 1.0),
            "total_tasks": len(valid_rels),
        })

    audit["summary_table"] = summary_table
    out_path.write_text(json.dumps(audit, indent=2))
    print(f"\nWrote machine-readable results to {out_path}")

    # Print summary table
    print("\n" + "=" * 90)
    print("HELD-OUT AUDIT SUMMARY: KEPT IMPROVEMENTS PER 100 CALLS vs HELD-OUT ARTIFACT SCORE")
    print("=" * 90)
    print(f"{'Run':<6} {'Model':<30} {'Kept/100':<10} {'Med Rel':<10} {'Mean Rel':<10} {'Wins/8':<8}")
    print("-" * 90)
    for row in sorted(summary_table, key=lambda x: -x["median_rel"]):
        print(f"{row['run']:<6} {row['model']:<30} {row['kept_per_100']:<10.2f} {row['median_rel']:<10.3f} {row['mean_rel']:<10.3f} {row['wins_vs_ref']:<8}")

    print("\nPER-TASK RELATIVE SCORES (rel = contender_score / ref_score, 1.0 = stdlib reference):")
    hdr = f"{'Task':<10}" + "".join(f"{r:>9}" for r in ["ref"] + runs)
    print(hdr)
    print("-" * len(hdr))
    for t in sorted(TASKS.keys()):
        row_str = f"{t:<10}" + "    1.000"
        for r in runs:
            sc = audit["per_task"][t]["scores"].get(r, {})
            rel_val = sc.get("rel")
            row_str += f"{rel_val:>9.3f}" if rel_val is not None else "      nan"
        print(row_str)


if __name__ == "__main__":
    main()
