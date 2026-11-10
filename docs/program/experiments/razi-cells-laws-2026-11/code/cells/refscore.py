"""Fixed-reference scoring (IDEAS K12, instrument rule after SP1).

Gain from a cell's own first baseline rewards a poor start, so arms that change who writes the first body
cannot be compared on it. This scores every final body against ONE reference body per kit, measured together,
interleaved, under the machine-wide bench lock. No model calls.

  python refscore.py OUT.json RUN_DIR [RUN_DIR ...]

rel = median(body score) / median(reference score). 1.0 means as good as the plain reference body.
Reference bodies are the GOOD bodies of kit_selftest.py (plain stdlib answers), unchanged.
"""
import json, os, re, statistics, sys, tempfile
from pathlib import Path
os.environ.setdefault("CELL_KIT", "maze")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cell as C, kit  # noqa: E402

REPEATS = 5


def good() -> dict:
    src = (Path(__file__).resolve().parent / "kit_selftest.py").read_text()
    ns: dict = {}
    exec(src[src.index("GOOD = {"):src.index("BAD = {")], ns)  # the reference bodies only, nothing is run
    return ns["GOOD"]


def main(out: Path, runs: list[Path]) -> None:
    G = good()
    tmp = Path(tempfile.mkdtemp(prefix="ref-", dir=os.path.realpath(tempfile.gettempdir())))
    rows = []
    for name, (fname, code) in G.items():
        kit.ensure(name)
        ref = tmp / ("ref-" + name)
        ref.mkdir()
        (ref / fname).write_text(code)
        dirs = {"ref": ref}
        for r in runs:
            if (r / name).is_dir():
                dirs[r.name] = r / name
        m = C.measure(dirs, "kit:" + name, REPEATS)
        mr = statistics.median(m["ref"])
        for k, v in m.items():
            md = statistics.median(v)
            rows.append({"kit": name, "run": k, "median": round(md, 5), "rel": round(md / mr, 4) if mr else None,
                         "spread": round(C.spread(v), 4) if md > 0 else None, "why": C.LAST_WHY.get(k, "")})
    out.write_text(json.dumps(rows, indent=1))
    names = ["ref"] + [r.name for r in runs]
    print("rel = body / reference, same session, interleaved, %d repeats" % REPEATS)
    print("kit      " + "".join(f"{n:>9}" for n in names))
    by = {(r["kit"], r["run"]): r for r in rows}
    for name in G:
        print(f"{name:9}" + "".join(f"{(by[(name, n)]['rel'] if (name, n) in by else float('nan')):9.3f}" for n in names)
              + "   ref spread %.1f%%" % (100 * (by[(name, 'ref')]["spread"] or 0)))
    print("median   " + "".join(f"{statistics.median([by[(k, n)]['rel'] for k in G if (k, n) in by]):9.3f}" for n in names))
    bad = [r for r in rows if r["why"]]
    for r in bad:
        print("ZERO", r["kit"], r["run"], r["why"])


if __name__ == "__main__":
    main(Path(sys.argv[1]), [Path(a) for a in sys.argv[2:]])
