"""Offline check of the SP3 patches in metab.py: scripted acts, real sandbox and kit bench, no model call.
usage: sp3_offline.py SHOW_PRICE(0|1) SHOW_SENSE(0|1)"""
import json, os, sys, shutil, tempfile
from pathlib import Path
os.environ["CELL_KIT"] = "fibmod"; os.environ["CELL_E0"] = "200"; os.environ["CELL_BASAL"] = "8"
os.environ["CELL_PRICE_SHOW"] = sys.argv[1]; os.environ["CELL_SENSE_SHOW"] = sys.argv[2]
os.environ["CELL_SENSE_DIR"] = str(Path.home() / "Work/razi-cells/exp/records")
sys.path.insert(0, str(Path.home() / "Work/razi-tools/cells"))
import metab as M, cell as C
src = (Path(__file__).parent / "metab_offline.py").read_text()
ns = {}
exec("\n".join(l for l in src.splitlines() if l.startswith(("slow = ", "fast = "))), ns)
slow, fast = ns["slow"], ns["fast"]
run = Path(tempfile.mkdtemp(dir=str(Path.home() / "Work/razi-cells/exp"), prefix="offline-"))
prompts = []
body = C.kit.KITS["fibmod"]["cmd"].split()[-1]
q = [{"do": "write", "path": body, "text": slow}, {"do": "assay"}, {"do": "variants", "path": body, "versions": [fast]},
     {"do": "sh", "cmd": "true"}, {"do": "rest", "result": "ok"}]
def fake(prompt, sid, model, effort, cap=None):
    prompts.append(prompt)
    M.USAGE.clear(); M.USAGE.update(inp=1000, out=100, cr=0, cw=0, rs=0, usd=0.0005)
    M.THOUGHT.clear(); M.THOUGHT.update(why="because " + str(len(prompts)))
    return (q.pop(0) if q else {"do": "rest", "result": "x"}), "said", "fake"
M.think = fake
c = run / "a"; c.mkdir(); (c / "NEED").write_text("need" + C.kit.need_text("fibmod")); M.born(c, M.E0)
M.run(c)
ev = [json.loads(l) for l in (c / "log.jsonl").read_text().splitlines()]
sense = [e for e in ev if e.get("event") == "sense"]
price_in_prompt = any("Prices per 1000" in p or "Living cost per step" in p for p in prompts)
price_in_system = "VITALS shows the numbers" in M.SYSTEM
sense_in_prompt = [p[p.index("SENSE:"):p.index("SENSE:") + 90] for p in prompts if "SENSE:" in p]
ok = True
def chk(name, cond):
    global ok
    ok &= bool(cond); print(("ok  " if cond else "FAIL"), name)
chk("price list shown iff flag", price_in_prompt == (sys.argv[1] == "1") and price_in_system == (sys.argv[1] == "1"))
chk("past step costs always shown", any("Your last steps cost: 13 (" in p for p in prompts))
chk("sense text shown iff flag", bool(sense_in_prompt) == (sys.argv[2] == "1"))
chk("sense logged twice (assay, win), no errors", len(sense) == 2 and not any("error" in e for e in sense))
chk("sense rises after the win", len(sense) == 2 and sense[1]["ratio"] > sense[0]["ratio"])
chk("why and say logged on usage rows", all(e.get("why", "").startswith("because") and e.get("say") == "said" for e in ev if "usage" in e))
chk("record body never in a prompt", not any("pow(" in p and "records" in p for p in prompts))
print("sense rows:", [(e["ratio"], e["shown"]) for e in sense], "| ledger sense:", M.ledger(c)["a"].get("sense"))
print("sense text:", sense_in_prompt[:3])
print("vitals sample:\n" + prompts[3][prompts[3].index("VITALS:"):prompts[3].index("COLONY")])
shutil.rmtree(run)
print("ALL OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
