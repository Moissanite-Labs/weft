"""Offline check of the K13 debt rule: scripted acts, no model call. Usage is made from the real prompt size."""
import json, os, sys, shutil, tempfile
from pathlib import Path
os.environ["CELL_KIT"]="fibmod"; os.environ["CELL_E0"]="100"; os.environ["CELL_BASAL"]="8"
sys.path.insert(0, str(Path.home()/"Work/razi-tools/cells"))
import metab as M, cell as C
FIX = M.fixed_chars(M.SYSTEM, M.TOOLS)
MODE = {"m": "write"}
def fake(prompt, sid, model, effort, cap=None):
    tok = int((FIX + len(prompt)) / 3.0)          # denser than the estimator's first guess of 2.8 chars per token
    u = dict(inp=4, out=min(cap or 64, 200), rs=0, usd=None)   # None: cost is priced from the tokens
    u.update(cw=tok, cr=0) if MODE["m"] == "write" else u.update(cw=tok // 2, cr=tok // 2)
    M.USAGE.clear(); M.USAGE.update(u)
    return {"do": "sh", "cmd": "true"}, "", "fake"
M.think = fake
ok = True
for e0, start, mode in ((400, "mid", "write"), (150, "mid", "write"), (60, "heavy", "write"), (30, "mid", "mixed"),
                        (12, "light", "write"), (250, "heavy", "mixed")):
    MODE["m"] = mode
    run = Path(tempfile.mkdtemp(dir=str(Path.home()/"Work/razi-cells/exp"), prefix="offline-"))
    c = run/"a"; c.mkdir(); (c/"NEED").write_text("need"+C.kit.need_text("fibmod")); M.born(c, e0)
    M.run(c, start, "low")
    L = M.ledger(c)["a"]
    ev = [json.loads(l) for l in (c/"log.jsonl").read_text().splitlines()]
    steps = [e for e in ev if "usage" in e]
    over = [e for e in ev if e.get("event") == "overdraft"]
    down = [(e["frm"], e["to"]) for e in ev if e.get("event") == "downshift"]
    death = [e.get("why", "energy") for e in ev if e.get("event") == "death"]
    worst = max((e["cost"] - e["est"] for e in steps), default=0)   # est covers input only, cost adds basal + output
    good = L["e"] >= -1e-6 and not over
    ok &= good
    print("   costs", [round(e["cost"],1) for e in steps][:8], "est", [e["est"] for e in steps][:8])
    print(f"e0 {e0:>3} {start:>5} {mode:>5} | steps {len(steps):>2} models {[e['model'] for e in steps][:3]}.. "
          f"| downshift {down} | end e {L['e']:.1f} state {L['state']} death {death} | overdrafts {len(over)} | {'OK' if good else 'FAIL'}")
    shutil.rmtree(run)
print("debt rule offline:", "ok" if ok else "FAILED")
