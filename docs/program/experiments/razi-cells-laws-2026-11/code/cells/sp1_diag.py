"""SP1 DIAGNOSTIC, not preregistered. Written after the SP1 data was seen.
Per part: final_gain at the cell's first stop (first `final` event) against its last, so the part of the
stem arm's gain that came after a wake can be read off. Also the stem's own token share and any energy debt."""
import json, statistics as st, sys
from pathlib import Path
E = Path.home() / "Work/razi-cells/exp"
PARTS = ["compress", "fibmod", "csvsum", "maze"]
def finals(r, p):
    return [e["final_gain"] for e in map(json.loads, open(E / r / p / "log.jsonl")) if e.get("event") == "final"]
def toks(path):
    t = 0
    for e in map(json.loads, open(path)):
        u = e.get("usage")
        if isinstance(u, dict): t += sum(u.get(k) or 0 for k in ("inp", "out", "cr", "cw"))
    return t
for r in sys.argv[1:]:
    first, last = [], []
    for p in PARTS:
        f = finals(r, p); first.append(f[0]); last.append(f[-1])
        print(f"{r} {p:9s} stops {len(f)}  first {f[0]:+.4f}  last {f[-1]:+.4f}  after-wake change {f[-1]-f[0]:+.4f}" if len(f) > 1
              else f"{r} {p:9s} stops 1  first {f[0]:+.4f}")
    L = json.load(open(E / r / ".ledger.json"))
    debt = {n: round(c["e"], 1) for n, c in L.items() if isinstance(c, dict) and c.get("e", 0) < 0}
    line = f"{r} median at first stop {st.median(first):.4f} | median at end {st.median(last):.4f} | debt {debt}"
    if (E / r / "stem/log.jsonl").exists():
        s = toks(E / r / "stem/log.jsonl"); a = s + sum(toks(E / r / p / "log.jsonl") for p in PARTS)
        line += f" | stem tokens {s} of {a} ({s/a:.0%})"
    print(line)
