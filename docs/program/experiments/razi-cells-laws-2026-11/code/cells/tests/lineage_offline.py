"""Offline check of lineage mode: scripted acts, real sandbox and kit bench, no model call.
Checks: (1) a hand rewrite then assay is paid (K23), (2) an unchanged body assayed again is not paid,
(3) sandbagging (worsen by hand, then win back in a variant round) is not paid, (4) a newborn inherits the
germline body with an assay, (5) the germline gate takes a better body and refuses an equal one,
(6) rest returns energy to the lineage store, (7) birth energy leaves the store."""
import json, os, sys, shutil, tempfile
from pathlib import Path
os.environ.update(CELL_KIT="fibmod", CELL_E0="200", CELL_BASAL="8", CELL_PAY_ANY="1", CELL_LINEAGE="1",
                  CELL_HEIR="store-fibmod")
sys.path.insert(0, str(Path.home() / "Work/razi-tools/cells"))
import metab as M, cell as C, lineage as L
head = "import sys\nM=1000000007\ndef fd(n):\n    if n==0: return (0,1)\n    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n    return (d,(c+d)%M) if n&1 else (c,d)\n"
slow = head + "out=[]\nfor l in sys.stdin.read().split():\n    for _ in range(6): r=fd(int(l))[0]\n    out.append(str(r))\nprint('\\n'.join(out))\n"
fast = head + "print('\\n'.join(str(fd(int(l))[0]) for l in sys.stdin.read().split()))\n"
run = Path(tempfile.mkdtemp(dir=str(Path.home() / "Work/razi-cells/exp"), prefix="offline-lin-"))
script, ok = {}, []
def fake(prompt, sid, model, effort, cap=None):
    M.USAGE.clear(); M.USAGE.update(inp=1000, out=100, cr=0, cw=0, rs=0, usd=0.0005)
    q = script[sid[5:]]
    return (q.pop(0) if q else {"do": "rest", "result": "done"}), "", "fake"
M.think = fake
def check(name, cond, info=""):
    ok.append(bool(cond)); print(("OK   " if cond else "FAIL ") + name, info)
def events(c): return [json.loads(l) for l in (run / c / "log.jsonl").read_text().splitlines()]
def seed(name):
    c = run / name; c.mkdir(); (c / "NEED").write_text("need" + C.kit.need_text("fibmod")); M.born(c, M.E0); return c
M.born(run / "store-fibmod", 1000.0)
(run / ".germ" / "fibmod").mkdir(parents=True)

# 1-3: pay law
c = seed("g0-fibmod-0")
script["g0-fibmod-0"] = [
    {"do": "write", "path": "fibmod.py", "text": slow}, {"do": "assay"},
    {"do": "assay"},                                                    # unchanged: no pay
    {"do": "write", "path": "fibmod.py", "text": fast}, {"do": "assay", "why": "dropped the repeat loop"},  # paid
    {"do": "write", "path": "fibmod.py", "text": slow},                 # sandbag by hand
    {"do": "variants", "path": "fibmod.py", "versions": [fast]},        # wins over slow, not over last scored
    {"do": "rest", "result": "fast doubling"}]
M.run(c)
ev = events("g0-fibmod-0")
inc = [e for e in ev if e.get("event") == "income"]
resc = [e for e in ev if e.get("event") == "rescore"]
check("1 hand rewrite + assay is paid once", len(inc) == 1 and inc[0].get("via") == "assay" and inc[0]["gain"] > 1, inc)
check("2 unchanged body assayed again: no rescore, no pay", len([r for r in resc if r.get("via") != "adopt"]) == 1)
check("3 sandbag then variant win: rescored against last scored body, not paid",
      any(r.get("via") == "adopt" and not r["won"] for r in resc), [(r.get("via"), r["won"], r["gain"]) for r in resc])
led = M.ledger(c)
me, st = led["g0-fibmod-0"], led["store-fibmod"]
check("6 rest returns unspent energy to the store", me["state"] == "resting" and me["e"] == 0 and abs(st["e"] - 1000 - me["gave"]) < 1e-6,
      (round(me["gave"], 1), round(st["e"], 1)))
check("  books: born + earned - spent == returned", abs(me["born"] + me["earned"] - me["spent"] - me["gave"]) < 1e-6)

# 5a: gate takes first body
row = L.gate(run, "fibmod", 0, ["g0-fibmod-0"])
check("5a gate takes the lineage's first body", row["took"] == "g0-fibmod-0" and (run / ".germ/fibmod/body/fibmod.py").read_text() == fast, row.get("took"))

# 4: inheritance through the real seed path
M.GERM = str(run / ".germ" / "fibmod")
script["g1-fibmod-0"] = [{"do": "rest", "result": "kept"}]
sys.argv = ["metab.py", "seed", str(run / "g1-fibmod-0"), "need"]
M.E0 = L.take(run, "fibmod", 200.0)
M.main()
ev = events("g1-fibmod-0")
inh = [e for e in ev if e.get("event") == "inherit"]
check("4 newborn inherits the germline body, already assayed", inh and inh[0]["ok"] and (run / "g1-fibmod-0/fibmod.py").read_text() == fast
      and C.get_assay(run / "g1-fibmod-0") and M.paid_dir(run / "g1-fibmod-0").is_dir(), inh)
led = M.ledger(c)
check("7 birth energy left the store and came back at rest", led["store-fibmod"]["gave"] == 200.0 and led["g1-fibmod-0"]["born"] == 200.0,
      round(led["store-fibmod"]["e"], 1))
p = [l for l in M.step_prompt(run / "g1-fibmod-0", [], "mid", "low", []).splitlines() if "lineage" in l.lower()]
check("  prompt speaks of the lineage", len(p) >= 2, p[:3])

# 5b: gate refuses an equal body
row = L.gate(run, "fibmod", 1, ["g1-fibmod-0"])
check("5b gate refuses a body equal to the germline", row["took"] is None and row["had_germ"], (row["gain"], row.get("medians")))
print("LIBRARY:\n" + (run / "LIBRARY.md").read_text())
shutil.rmtree(run)
print("ALL OK" if all(ok) else "FAILED %d" % ok.count(False))
