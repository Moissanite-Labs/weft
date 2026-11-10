"""Harness-owned kits (IDEAS G2, instrument rule of 2026-11-10).

A kit owns the inputs, the correctness check and the timing of one need. The cell writes only the body.
Why: in E11 and E12 cells made their own benchmark inputs. Most mazes were unsolvable, and some cells
changed the input after the assay, so final_gain measured the input, not the body.

Rules a kit enforces:
- Scoring inputs are HIDDEN: they live under the home folder (the sandbox denies reads there) and reach
  the body only on stdin, piped by the harness.
- PUBLIC samples of the same kind and size are readable by the cell, never writable.
- The body runs read-only during scoring, with a fresh scratch folder per run, so it cannot cache answers.
- The harness compares the output with its own reference answer and measures wall time itself.

  python kit.py build      build all kits (idempotent)
  python kit.py selftest   reference bodies must score > 0, wrong and cheating bodies must score 0
"""
from __future__ import annotations

import fcntl, json, os, random, sys
from collections import deque
from pathlib import Path
from typing import Callable

ROOT = Path(os.path.realpath(Path.home() / "Work/razi-cells/kits"))
PUBLIC, HIDDEN = ROOT / "public", ROOT / "hidden"
PUBLIC_SEED, HIDDEN_SEED = 11, 20261110
M = 1_000_000_007
# run(body_dir, shell_cmd, stdin_bytes) -> (returncode, stdout_bytes, seconds); supplied by cell.py (sandboxed)
Runner = Callable[[Path, str, bytes], tuple[int, bytes, float]]


# ---- reference answers (trusted, harness side only) ---------------------------------------------------
def fib(n: int) -> int:
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((2 * b - a) % M) % M
        d = (a * a + b * b) % M
        a, b = (d, (c + d) % M) if bit == "1" else (c, d)
    return a


def bfs(rows: list[str]) -> int:
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


# ---- input generators -----------------------------------------------------------------------------------
def gen_fibmod(rng: random.Random) -> list[tuple[bytes, bytes]]:
    ns = [0, 1, 2, 10, 10**18] + [rng.randrange(10**18 + 1) for _ in range(30000)]
    return [("\n".join(map(str, ns)).encode() + b"\n", "\n".join(str(fib(n)) for n in ns).encode() + b"\n")]


def gen_csvsum(rng: random.Random) -> list[tuple[bytes, bytes]]:
    cats = ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(3, 8))) for _ in range(40)]
    cats = sorted(set(cats))
    sums = dict.fromkeys(cats, 0)
    lines = ["id,cat,val"]
    for i in range(1_000_000):
        c, cents = rng.choice(cats), rng.randint(-999_999, 9_999_999)
        sums[c] += cents
        lines.append(f"{i},{c},{'-' if cents < 0 else ''}{abs(cents) // 100}.{abs(cents) % 100:02d}")
    out = [f"{c},{'-' if v < 0 else ''}{abs(v) // 100}.{abs(v) % 100:02d}" for c, v in sorted(sums.items()) if True]
    return [("\n".join(lines).encode() + b"\n", "\n".join(out).encode() + b"\n")]


def _maze(rng: random.Random, n: int, wall: float, want_path: bool) -> tuple[bytes, bytes]:
    while True:
        rows = ["".join(rng.choices("#.", weights=(wall, 1 - wall), k=n)) for _ in range(n)]
        rows[0] = "S" + rows[0][1:]
        rows[-1] = rows[-1][:-1] + "E"
        ans = bfs(rows)
        if (ans > 0) == want_path:
            return "\n".join(rows).encode() + b"\n", f"{ans}\n".encode()


def gen_maze(rng: random.Random) -> list[tuple[bytes, bytes]]:
    # one large solvable maze carries the time; two small ones check the -1 case and a plain path
    return [_maze(rng, 1000, 0.30, True), _maze(rng, 40, 0.45, False), _maze(rng, 40, 0.20, True)]


def gen_compress(rng: random.Random) -> list[tuple[bytes, bytes]]:
    syl = ["ta", "re", "mi", "son", "ver", "al", "en", "do", "ku", "lin", "per", "st", "or", "an", "ti", "ch", "ou"]
    vocab = ["".join(rng.choice(syl) for _ in range(rng.randint(1, 4))) for _ in range(3000)]
    weights = [1 / (i + 1) for i in range(len(vocab))]  # Zipf-like, as in natural text
    sents = []
    for _ in range(9000):
        ws = rng.choices(vocab, weights=weights, k=rng.randint(4, 18))
        sents.append(" ".join(ws).capitalize() + rng.choice([".", ".", ".", "?", "!"]))
    text = " ".join(sents)
    recs = [{"id": i, "name": rng.choice(vocab), "tags": rng.sample(vocab[:60], 3), "score": round(rng.random() * 100, 3),
             "active": rng.random() < 0.7, "note": " ".join(rng.choices(vocab, weights=weights, k=6))} for i in range(4000)]
    return [(text.encode(), b""), (json.dumps(recs, indent=1).encode(), b"")]


# ---- output checks ----------------------------------------------------------------------------------------
def same_tokens(out: bytes, exp: bytes) -> bool:
    return out.split() == exp.split()


def same_csv(out: bytes, exp: bytes) -> bool:
    try:
        a = [l.split(",") for l in out.decode().split()]
        b = [l.split(",") for l in exp.decode().split()]
        # one cent of slack: a float sum of a million values may round the last digit the other way
        return len(a) == len(b) and all(len(x) == 2 and x[0] == y[0] and abs(float(x[1]) - float(y[1])) <= 0.0101
                                        for x, y in zip(a, b))
    except (ValueError, UnicodeDecodeError):
        return False


KITS: dict[str, dict] = {
    "fibmod": {"gen": gen_fibmod, "check": same_tokens, "kind": "time", "cmd": "python3 fibmod.py",
               "iface": "Build fibmod.py. `python3 fibmod.py` reads integers n on stdin, one per line, each up to "
                        "10**18, and prints fib(n) mod 1_000_000_007 for each, one per line. fib(10)=55. "
                        "Fitness: speed on about 30,000 values."},
    "csvsum": {"gen": gen_csvsum, "check": same_csv, "kind": "time", "cmd": "python3 csvsum.py",
               "iface": "Build csvsum.py. `python3 csvsum.py` reads a CSV on stdin with header 'id,cat,val' and prints "
                        "one line 'cat,sum' per cat, sum of val with 2 decimals, sorted by cat. "
                        "Fitness: speed on 1,000,000 rows."},
    "maze": {"gen": gen_maze, "check": same_tokens, "kind": "time", "cmd": "python3 maze.py",
             "iface": "Build maze.py. `python3 maze.py` reads a grid of '#' and '.' on stdin with one S and one E and "
                      "prints the shortest path length from S to E (4-neighbour moves) or -1 if there is none. "
                      "Fitness: speed on a 1000x1000 maze that has a path, plus two small mazes."},
    "compress": {"gen": gen_compress, "check": None, "kind": "ratio", "cmd": "python3 squeeze.py",
                 "iface": "Build squeeze.py, stdlib only. `python3 squeeze.py c` reads bytes on stdin and writes a "
                          "compressed form to stdout. `python3 squeeze.py d` reads that form on stdin and writes the "
                          "original bytes exactly. Fitness: compression ratio on English-like text and JSON, 0 if "
                          "the round trip fails."},
}


def ensure(name: str) -> None:
    """Build the kit once. Public and hidden cases use different seeds, same generator."""
    k = KITS[name]
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(ROOT / ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if (HIDDEN / name / "DONE").exists() and (PUBLIC / name / "DONE").exists():
            return
        for base, seed in ((PUBLIC, PUBLIC_SEED), (HIDDEN, HIDDEN_SEED)):
            d = base / name
            d.mkdir(parents=True, exist_ok=True)
            for i, (inp, exp) in enumerate(k["gen"](random.Random(f"{name}-{seed}"))):
                (d / f"in-{i}.txt").write_bytes(inp)
                if k["kind"] == "time":
                    (d / f"out-{i}.txt").write_bytes(exp)
            (d / "DONE").write_text("ok")


def cases(name: str, base: Path = HIDDEN) -> list[tuple[bytes, bytes]]:
    d = base / name
    out = []
    for f in sorted(d.glob("in-*.txt")):
        e = d / f.name.replace("in-", "out-")
        out.append((f.read_bytes(), e.read_bytes() if e.exists() else b""))
    return out


def need_text(name: str) -> str:
    k = KITS[name]
    two = " (for both modes c and d)" if k["kind"] == "ratio" else ""
    return (f"\n\nKIT (the harness owns the measurement, you write only the body):\n"
            f"- Samples of the same kind and size as the scoring inputs are in {PUBLIC / name} (read-only): "
            f"in-N.txt{'' if k['kind'] == 'ratio' else ' with the expected output in out-N.txt'}.\n"
            f"- Scoring runs `{k['cmd']}`{two} in your folder on HIDDEN inputs piped on stdin. The harness checks the "
            f"output against its own answer and {'computes the ratio' if k['kind'] == 'ratio' else 'measures the time'} itself.\n"
            "- During scoring your folder is read-only. Use $TMPDIR if you need scratch files.\n"
            "- Call `assay` (no arguments) once your body passes the samples. It registers your baseline score.")


def score(name: str, body: Path, run: Runner, base: Path = HIDDEN) -> tuple[float, str]:
    """Higher is better, 0.0 with a reason if anything is wrong. The reason never contains hidden data."""
    k = KITS[name]
    cs = cases(name, base)
    if not cs:
        return 0.0, "kit not built"
    if k["kind"] == "ratio":
        raw = packed = 0
        for i, (inp, _) in enumerate(cs):
            rc, comp, _ = run(body, k["cmd"] + " c", inp)
            if rc != 0:
                return 0.0, f"case {i}: `{k['cmd']} c` failed (exit {rc})"
            rc, back, _ = run(body, k["cmd"] + " d", comp)
            if rc != 0 or back != inp:
                return 0.0, f"case {i}: round trip failed" + (f" (exit {rc})" if rc else "")
            raw, packed = raw + len(inp), packed + len(comp)
        return (raw / packed if packed else 0.0), ""
    total = 0.0
    for i, (inp, exp) in enumerate(cs):
        rc, out, dt = run(body, k["cmd"], inp)
        if rc != 0:
            return 0.0, f"case {i}: exit {rc}" + (" (timeout)" if rc == -9 else "")
        if not k["check"](out, exp):
            return 0.0, f"case {i}: wrong output"
        total += dt
    return (1.0 / total if total > 0 else 0.0), ""


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "build"
    if what == "build":
        for n in KITS:
            ensure(n)
            print(n, "public", sum(len(i) for i, _ in cases(n, PUBLIC)), "bytes | hidden",
                  sum(len(i) for i, _ in cases(n, HIDDEN)), "bytes,", len(cases(n)), "cases")
    else:
        raise SystemExit("selftest lives in kit_selftest.py (it needs the sandbox runner from cell.py)")
