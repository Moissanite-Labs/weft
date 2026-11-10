"""Offline check of metab.py: scripted acts, real sandbox and kit bench, no model call."""
import json, os, sys, shutil, tempfile
from pathlib import Path
os.environ["CELL_KIT"]="fibmod"; os.environ["CELL_E0"]="100"; os.environ["CELL_BASAL"]="8"
sys.path.insert(0, str(Path.home()/"Work/razi-tools/cells"))
import metab as M, cell as C
slow = "import sys\nM=1000000007\ndef fd(n):\n    if n==0: return (0,1)\n    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n    return (d,(c+d)%M) if n&1 else (c,d)\nout=[]\nfor l in sys.stdin.read().split():\n    for _ in range(12): r=fd(int(l))[0]\n    out.append(str(r))\nprint('\\n'.join(out))\n"
fast = "import sys\nM=1000000007\ndef fd(n):\n    if n==0: return (0,1)\n    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n    return (d,(c+d)%M) if n&1 else (c,d)\nprint('\\n'.join(str(fd(int(l))[0]) for l in sys.stdin.read().split()))\n"
print("kit cmd:", C.kit.KITS["fibmod"]["cmd"], "| sample head:", (C.kit.PUBLIC/"fibmod"/"in-0.txt").read_bytes()[:40])
run = Path(tempfile.mkdtemp(dir=str(Path.home()/"Work/razi-cells/exp"), prefix="offline-"))
script = {}
def fake(prompt, sid, model, effort, cap=None):
    M.USAGE.clear(); M.USAGE.update(inp=1000,out=100,cr=0,cw=0,rs=0,usd=0.0005)  # 5 units + basal 8 = 13
    name = sid[5:]; q = script[name]; 
    if name=="a" and len(q)==2: print("--- PROMPT TAIL seen by a ---\n"+prompt[prompt.index("ASSAY:"):prompt.index("RECENT:")])
    return (q.pop(0) if q else {"do":"sh","cmd":"true"}), "", "fake"
M.think = fake
body = C.kit.KITS["fibmod"]["cmd"].split()[-1]
for n in ("a","b","c"):
    c = run/n; c.mkdir(); (c/"NEED").write_text("need"+C.kit.need_text("fibmod")); M.born(c, M.E0)
# b rests at once: its energy should split between a and c
script["b"]=[{"do":"write","path":body,"text":slow},{"do":"assay"},{"do":"rest","result":"slow ok"}]
M.run(run/"b"); L=M.ledger(run/"b"); print("after b rests:", {k:(round(v["e"],1),v["state"],round(v["got"],1),round(v["gave"],1)) for k,v in L.items()})
# a: write, assay, divide(daughter writes fast, rests), then variants no-op, then runs out
script["a"]=[{"do":"write","path":body,"text":slow},{"do":"assay"},{"do":"divide","idea":"fast doubling","energy":40,"model":"light","effort":"none"},{"do":"variants","path":body,"versions":[fast]},{"do":"rest","result":"fast doubling adopted"}]
script["daughter"]=[{"do":"write","path":body,"text":fast},{"do":"rest","result":"fast doubling written"}]
M.run(run/"a"); L=M.ledger(run/"a")
for k,v in L.items(): print(k, {x:(round(y,1) if isinstance(y,float) else y) for x,y in v.items()})
ev=[json.loads(l) for l in (run/"a"/"log.jsonl").read_text().splitlines()]
print("a events:", [e.get("event") or (e.get("act") or {}).get("do") or ("usage" if "usage" in e else "?") for e in ev])
print("a models used:", [e["model"] for e in ev if "usage" in e])
print("income:", [e for e in ev if e.get("event")=="income"], "| death:", [e for e in ev if e.get("event") in ("death","fuse")])
print("LIBRARY:\n"+(run/"LIBRARY.md").read_text()[:900])
d=L["a"]; print("books a: born+earned+got-spent_own == e ?", "see above")
shutil.rmtree(run)
