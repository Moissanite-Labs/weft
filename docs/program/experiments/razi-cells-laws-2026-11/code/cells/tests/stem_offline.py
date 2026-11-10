"""Offline check of stem.py: scripted acts, real sandbox and kit bench, no model call."""
import json, os, sys, shutil, tempfile, threading
from pathlib import Path
os.environ["CELL_KIT"]="fibmod"; os.environ["CELL_E0"]="100"; os.environ["CELL_BASAL"]="8"
sys.path.insert(0, str(Path.home()/"Work/razi-tools/cells"))
import stem as S, metab as M, cell as C
assert M.HEIR == "stem"
slow = "import sys\nM=1000000007\ndef fd(n):\n    if n==0: return (0,1)\n    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n    return (d,(c+d)%M) if n&1 else (c,d)\nout=[]\nfor l in sys.stdin.read().split():\n    for _ in range(12): r=fd(int(l))[0]\n    out.append(str(r))\nprint('\\n'.join(out))\n"
fast = "import sys\nM=1000000007\ndef fd(n):\n    if n==0: return (0,1)\n    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n    return (d,(c+d)%M) if n&1 else (c,d)\nprint('\\n'.join(str(fd(int(l))[0]) for l in sys.stdin.read().split()))\n"
run = Path(tempfile.mkdtemp(dir=str(Path.home()/"Work/razi-cells/exp"), prefix="offline-stem-"))
body = "fibmod.py"
script = {
 "stem": [{"do":"feed","part":"p1","energy":60,"note":"start simple","start_model":"light","start_effort":"none"},
          {"do":"feed","part":"p2","energy":40},
          {"do":"feed","part":"nope","energy":5},
          {"do":"wait"}, {"do":"wait"},
          {"do":"feed","part":"p1","energy":50,"note":"try fast doubling without the repeat loop","start_model":"mid"},
          {"do":"wait"}, {"do":"rest","result":"p1 improved, p2 left as is"}],
 "p1": [{"do":"write","path":body,"text":slow},{"do":"assay"},{"do":"rest","result":"slow ok"},
        {"do":"variants","path":body,"versions":[fast]},{"do":"rest","result":"fast adopted"}],
 "p2": [{"do":"write","path":body,"text":slow},{"do":"assay"}],   # then idles until it dies
}
seen = {}
def fake(prompt, sid, model, effort, cap=None):
    name = sid[5:]; q = script[name]
    seen.setdefault(name, []).append((model, effort))
    if name == "stem" and len(q) in (3, 1): print(f"--- TISSUE seen by stem ({len(q)} acts left) ---\n" + prompt[prompt.index("TISSUE:"):prompt.index("LIBRARY")])
    if name == "p1" and len(q) == 2: print("--- p1 NEED tail on wake ---\n" + prompt[prompt.index("SIGNAL FROM"):prompt.index("LIBRARY")][:300]); print("--- p1 VITALS ---\n"+prompt[prompt.index("VITALS"):prompt.index("RECENT")])
    u = dict(inp=1000,out=100,cr=0,cw=0,rs=0,usd=0.0005)
    (S.USAGE if name == "stem" else M.USAGE).clear(); (S.USAGE if name == "stem" else M.USAGE).update(u)
    return (dict(q.pop(0)) if q else {"do":"sh","cmd":"true"}), "", "fake"
S.think = fake; M.think = fake
class T:
    def __init__(self, run, part, kit, model, effort):
        (run/part/"RESULT").unlink(missing_ok=True)
        self.t = threading.Thread(target=M.run, args=(run/part, model, effort)); self.t.start()
    def done(self): return not self.t.is_alive()
    def join(self, timeout): self.t.join(timeout)
S.launch = T
needs = [{"name":"p1","kit":"fibmod","need":"part one need"},{"name":"p2","kit":"fibmod","need":"part two need"}]
res = S.run_stem(run, needs)
L = M.ledger(run/"stem")
for k,v in L.items(): print(k, {x:(round(y,1) if isinstance(y,float) else y) for x,y in v.items()})
tot_e = sum(v["e"] for v in L.values()); earned = sum(v["earned"] for v in L.values()); spent = sum(v["spent"] for v in L.values())
print("conservation: stem.born + earned - spent =", round(L["stem"]["born"]+earned-spent,2), "| held =", round(tot_e,2))
assert abs(L["stem"]["born"]+earned-spent-tot_e) < 1e-6
assert abs(L["stem"]["gave"] - sum(v["born"]+v["got"] for k,v in L.items() if k!="stem")) < 1e-6
assert abs(L["stem"]["got"] - sum(v["gave"] for k,v in L.items() if k!="stem")) < 1e-6
ev=[json.loads(l) for l in (run/"stem"/"log.jsonl").read_text().splitlines()]
print("stem events:", [e.get("event") or (e.get("act") or {}).get("do") or ("usage" if "usage" in e else "?") for e in ev])
print("feeds:", [(e["kind"], e["part"], e["gave"], e.get("model")) for e in ev if e.get("event")=="feed"])
print("stopped:", [(e["part"], e["state"], e["fit"]) for e in ev if e.get("event")=="stopped"])
print("results:", [e["res"][:150] for e in ev if "res" in e])
print("models seen:", {k: sorted(set(v)) for k,v in seen.items()})
a=json.loads((run/"p1"/"ASSAY.json").read_text()); print("p1 assay:", {k:(round(v,4) if isinstance(v,float) else v) for k,v in a.items()})
print("LIBRARY:\n"+(run/"LIBRARY.md").read_text()[:900]); print("stem result:", res)
shutil.rmtree(run); print("offline stem ok")
