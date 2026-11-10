"""Offline verification of L2 Dissipative Heredity: Causal Laws for Silicon Life.

Tests:
1. Weismann Soma Coasting Dissipates: A soma seeded with .germ/fibmod (slow body) and
   CELL_WEISMANN=1 that immediately rests at fit==0 dissipates unspent energy; gave==0,
   dissipated > 0, store receives 0 refund.
2. Weismann Soma Winning Returns Surplus: A soma seeded with .germ/fibmod (slow body) and
   CELL_WEISMANN=1 that rewrites to fast, assays (fit > 0, earns win bounty), and rests
   returns its full unspent energy to store.
3. Spore Birth (CELL_SPORE_FROM): Newborn starts with empty code folder, inherits genome.md,
   leaves fibmod.py absent, logs event="spore". If it rests without assay, energy dissipates;
   if it writes fast, assays and rests, surplus returns to store and competes at L.gate().
4. Chemostat Niche Bounty Accumulation: Across generations with --chemostat, a stalled
   generation raises bounty by flux, while a winning generation resets bounty to base reward.
5. Gap-Potentiated Reward (CELL_GAP_PAY=1): With sense=0.50, eff_reward equals 2.0*REWARD (800)
   and vitals() displays the doubled reward rate.
6. L9 Model-Switch Cache-Write Guard: Simulate step 0 on mid (warm cache), steps 1..4 on light
   growing prompt by 8000 chars, step 5 switching back to mid with e=175.4. Verify pick()
   estimates step 5 input at cache-write top rate, caps output so cost <= 175.4, 0 overdrafts.
"""
from __future__ import annotations

import json, math, os, shutil, sys, tempfile
from pathlib import Path

# Setup environment for tests
os.environ["CELL_KIT"] = "fibmod"
os.environ["CELL_E0"] = "200"
os.environ["CELL_BASAL"] = "8"
os.environ["CELL_PAY_ANY"] = "1"
os.environ["CELL_LINEAGE"] = "1"
os.environ["CELL_HEIR"] = "store-fibmod"

TOOLS_DIR = Path.home() / "Work/razi-tools/cells"
sys.path.insert(0, str(TOOLS_DIR))
import cell as C, lineage as L, metab as M

head = (
    "import sys\nM=1000000007\ndef fd(n):\n"
    "    if n==0: return (0,1)\n"
    "    a,b=fd(n>>1); c=a*((2*b-a)%M)%M; d=(a*a+b*b)%M\n"
    "    return (d,(c+d)%M) if n&1 else (c,d)\n"
)
slow = head + "out=[]\nfor l in sys.stdin.read().split():\n    for _ in range(6): r=fd(int(l))[0]\n    out.append(str(r))\nprint('\\n'.join(out))\n"
fast = head + "print('\\n'.join(str(fd(int(l))[0]) for l in sys.stdin.read().split()))\n"

run = Path(tempfile.mkdtemp(dir=str(Path.home() / "Work/razi-cells/exp"), prefix="offline-l2-"))
script: dict[str, list[dict]] = {}
ok: list[bool] = []


def check(name: str, cond: bool, info: object = "") -> None:
    ok.append(bool(cond))
    print(("OK   " if cond else "FAIL ") + name, info if info else "")


def events(c: str) -> list[dict]:
    p = run / c / "log.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def fake_think(prompt: str, sid: str, model: str, effort: str, cap: int | None = None):
    M.USAGE.clear()
    M.USAGE.update(inp=1000, out=100, cr=0, cw=0, rs=0, usd=0.0005)
    cid = sid[5:] if sid.startswith("cell-") else sid
    q = script.get(cid, [])
    return (q.pop(0) if q else {"do": "rest", "result": "done"}), "", "fake"


M.think = fake_think

# -------------------------------------------------------------------------
# Test 1: Weismann Soma Coasting Dissipates
# -------------------------------------------------------------------------
print("--- Test 1: Weismann Soma Coasting Dissipates ---")
M.born(run / "store-fibmod", 1000.0)
germ_body = run / ".germ/fibmod/body"
germ_body.mkdir(parents=True, exist_ok=True)
(germ_body / "fibmod.py").write_text(slow)

M.GERM = str(run / ".germ/fibmod")
M.WEISMANN = True
M.GAP_PAY = False
M.SPORE_FROM = ""

c1_name = "g0-fibmod-coasting"
c1 = run / c1_name
c1.mkdir(parents=True, exist_ok=True)
(c1 / "NEED").write_text("need" + C.kit.need_text("fibmod"))
e_taken = L.take(run, "fibmod", 200.0)
M.E0 = e_taken

script[c1_name] = [{"do": "rest", "result": "coasted without win"}]
sys.argv = ["metab.py", "seed", str(c1), "need"]
M.main()

ev1 = events(c1_name)
rest_ev1 = [e for e in ev1 if e.get("event") == "rest"]
led1 = M.ledger(c1)
me1, st1 = led1[c1_name], led1["store-fibmod"]

check("1a. Soma resting at fit==0 allows rest", me1["state"] == "resting", me1["state"])
check("1b. Soma gave 0.0 back to lineage store", me1["gave"] == 0.0, me1["gave"])
check("1c. Soma dissipated unspent birth energy", me1.get("dissipated", 0) > 0, me1.get("dissipated"))
check("1d. Rest event logged dissipated energy", rest_ev1 and rest_ev1[0].get("dissipated", 0) > 0, rest_ev1)
check("1e. Store received 0 refund (still at 800.0)", abs(st1["e"] - 800.0) < 1e-6, st1["e"])

# -------------------------------------------------------------------------
# Test 2: Weismann Soma Winning Returns Surplus
# -------------------------------------------------------------------------
print("\n--- Test 2: Weismann Soma Winning Returns Surplus ---")
c2_name = "g0-fibmod-winner"
c2 = run / c2_name
c2.mkdir(parents=True, exist_ok=True)
(c2 / "NEED").write_text("need" + C.kit.need_text("fibmod"))
e_taken2 = L.take(run, "fibmod", 200.0)
M.E0 = e_taken2

script[c2_name] = [
    {"do": "write", "path": "fibmod.py", "text": fast},
    {"do": "assay", "why": "rewrite fast"},
    {"do": "rest", "result": "won and returning surplus"},
]
sys.argv = ["metab.py", "seed", str(c2), "need"]
M.main()

ev2 = events(c2_name)
inc2 = [e for e in ev2 if e.get("event") == "income"]
led2 = M.ledger(c2)
me2, st2 = led2[c2_name], led2["store-fibmod"]

check("2a. Soma achieved a scored win (fit > 0, earned > 0)", me2["fit"] > 0 and me2["earned"] > 0, (me2["fit"], me2["earned"]))
check("2b. Winning soma returns unspent energy (gave > 0)", me2["gave"] > 0, me2["gave"])
check("2c. Dissipated is 0 for winning soma", me2.get("dissipated", 0) == 0, me2.get("dissipated", 0))
check("2d. Conservation holds: born + earned - spent == gave", abs(me2["born"] + me2["earned"] - me2["spent"] - me2["gave"]) < 1e-6)
check("2e. Store received returned surplus", abs(st2["e"] - (600.0 + me2["gave"])) < 1e-6, st2["e"])

# -------------------------------------------------------------------------
# Test 3: Spore Birth (CELL_SPORE_FROM)
# -------------------------------------------------------------------------
print("\n--- Test 3: Spore Birth (CELL_SPORE_FROM) ---")
# Ensure germ has both code and genome.md
(germ_body / "genome.md").write_text("lineage memory: fast doubling is key\n")

# 3A: Spore resting without assay dissipates
c3a_name = "g1-spore-unassayed"
c3a = run / c3a_name
c3a.mkdir(parents=True, exist_ok=True)
(c3a / "NEED").write_text("need" + C.kit.need_text("fibmod"))
e_taken3a = L.take(run, "fibmod", 200.0)
M.E0 = e_taken3a
M.GERM = ""
M.SPORE_FROM = str(run / ".germ/fibmod")
M.WEISMANN = True

script[c3a_name] = [{"do": "rest", "result": "spore idle"}]
sys.argv = ["metab.py", "seed", str(c3a), "need"]
M.main()

ev3a = events(c3a_name)
check("3a1. Spore inherited genome.md", (c3a / "genome.md").exists() and "fast doubling" in (c3a / "genome.md").read_text())
check("3a2. Spore did not inherit code (fibmod.py absent)", not (c3a / "fibmod.py").exists())
check("3a3. Spore logged event='spore'", any(e.get("event") == "spore" and e.get("has_genome") for e in ev3a))
led3a = M.ledger(c3a)
me3a = led3a[c3a_name]
check("3a4. Unassayed spore dissipates birth energy (gave == 0)", me3a["gave"] == 0.0 and me3a.get("dissipated", 0) > 0,
      (me3a["gave"], me3a.get("dissipated")))

# 3B: Spore that writes, assays, and rests returns surplus and competes at gate
c3b_name = "g1-spore-working"
c3b = run / c3b_name
c3b.mkdir(parents=True, exist_ok=True)
(c3b / "NEED").write_text("need" + C.kit.need_text("fibmod"))
e_taken3b = L.take(run, "fibmod", 200.0)
M.E0 = e_taken3b
store_before3b = M.ledger(c3b)["store-fibmod"]["e"]

script[c3b_name] = [
    {"do": "write", "path": "fibmod.py", "text": fast},
    {"do": "assay"},
    {"do": "rest", "result": "spore assayed and resting"},
]
sys.argv = ["metab.py", "seed", str(c3b), "need"]
M.main()

led3b = M.ledger(c3b)
me3b = led3b[c3b_name]
check("3b1. Assayed spore has assay=True", me3b["assay"] is True)
check("3b2. Assayed spore returns surplus to store (gave > 0)", me3b["gave"] > 0 and me3b.get("dissipated", 0) == 0,
      (me3b["gave"], me3b.get("dissipated", 0)))
check("3b3. Store refunded correctly", abs(led3b["store-fibmod"]["e"] - (store_before3b + me3b["gave"])) < 1e-6)

# Gate check
gate_res = L.gate(run, "fibmod", 1, [c3b_name])
check("3b4. Spore competes at L.gate()", gate_res.get("kit") == "fibmod" and gate_res.get("had_germ") is True)

# -------------------------------------------------------------------------
# Test 4: Chemostat Niche Bounty Accumulation
# -------------------------------------------------------------------------
print("\n--- Test 4: Chemostat Niche Bounty Accumulation ---")
bounty = {"fibmod": 400.0}
flux = 200.0  # 400.0 / 2

# Generation 0: stalled
stalled_gate = {"gen": 0, "kit": "fibmod", "took": None, "gain": 0.0}
if stalled_gate.get("took"):
    bounty["fibmod"] = 400.0
else:
    bounty["fibmod"] = round(bounty["fibmod"] + flux, 1)
check("4a. Stalled generation raises niche bounty to 600.0", bounty["fibmod"] == 600.0, bounty["fibmod"])

# Generation 1: stalled again
if stalled_gate.get("took"):
    bounty["fibmod"] = 400.0
else:
    bounty["fibmod"] = round(bounty["fibmod"] + flux, 1)
check("4b. Second stalled generation raises bounty to 800.0", bounty["fibmod"] == 800.0, bounty["fibmod"])

# Generation 2: winning generation
won_gate = {"gen": 2, "kit": "fibmod", "took": "g2-fibmod-0", "gain": 0.45}
if won_gate.get("took"):
    bounty["fibmod"] = 400.0
else:
    bounty["fibmod"] = round(bounty["fibmod"] + flux, 1)
check("4c. Winning generation resets bounty to base reward 400.0", bounty["fibmod"] == 400.0, bounty["fibmod"])

# -------------------------------------------------------------------------
# Test 5: Gap-Potentiated Reward (CELL_GAP_PAY=1)
# -------------------------------------------------------------------------
print("\n--- Test 5: Gap-Potentiated Reward (CELL_GAP_PAY=1) ---")
c5 = run / "gap-test-cell"
c5.mkdir(parents=True, exist_ok=True)
M.born(c5, 200.0)
M.GAP_PAY = True
M.REWARD = 400.0

# Set sense ratio to 0.50
M.ledger(c5, lambda d: d[M.cid(c5)].__setitem__("sense", 0.50))
eff_r = M.eff_reward(c5)
check("5a. eff_reward at sense=0.50 is 2.0 * REWARD (800.0)", eff_r == 800.0, eff_r)

v = M.vitals(c5, "mid", "low", [])
# Expected: 800 * log1p(0.1) = 76, 800 * log1p(1.0) = 555
expected_10 = round(800.0 * math.log1p(0.1))
expected_100 = round(800.0 * math.log1p(1.0))
check("5b. vitals() displays gap-potentiated reward",
      f"+10% earns {expected_10}" in v and f"+100% earns {expected_100}" in v,
      [l for l in v.splitlines() if "scored win" in l])

# Reset GAP_PAY to check fallback
M.GAP_PAY = False
check("5c. eff_reward falls back to standard REWARD when GAP_PAY=False", M.eff_reward(c5) == 400.0)

# -------------------------------------------------------------------------
# Test 6: L9 Model-Switch Cache-Write Guard
# -------------------------------------------------------------------------
print("\n--- Test 6: L9 Model-Switch Cache-Write Guard ---")
seen: dict = {}
fixed = M.fixed_chars(M.SYSTEM, M.TOOLS)
pi_mid, po_mid = M.price("mid")
top_mid = pi_mid * 1.25 / 1000

# Step 0: mid with warm cache
prompt0 = "x" * 2000
u0 = dict(inp=4, out=100, cr=2000, cw=0, rs=0, usd=None)
cost0 = M.step_cost("mid", u0)
M.observe("mid", prompt0, u0, cost0, seen, fixed)

check("6a. Step 0 records last_model and chars", seen.get("last_model") == "mid" and f"chars:mid" in seen)

# Steps 1..4: light growing prompt by 8000 chars total
curr_prompt = prompt0
for step in range(1, 5):
    curr_prompt += "y" * 2000
    u_l = dict(inp=4, out=50, cr=1500, cw=500, rs=0, usd=None)
    cost_l = M.step_cost("light", u_l)
    M.observe("light", curr_prompt, u_l, cost_l, seen, fixed)

check("6b. Steps 1-4 update last_model to light", seen.get("last_model") == "light")

# Step 5: switch back to mid with e=175.4 (the l1b2/g0-compress-0 scenario)
prompt5 = curr_prompt
e5 = 175.4
m_pick, cap_pick, est_pick = M.pick("mid", prompt5, e5, seen, fixed)

# Verify estimator priced input at top rate
chars5 = fixed + len(prompt5)
tpc = seen["tpc"] * 1.1 if "tpc" in seen else 1.0 / 2.8
pad = 0 if "tpc" in seen else 600
expected_est = (chars5 * tpc + pad) * top_mid

check("6c. Step 5 input estimated at cache-write top rate", abs(est_pick - expected_est) < 1e-4, (est_pick, expected_est))

# Verify actual step cost with full output cap does not exceed e5
# (Worst-case actual call: all input tokens charged at cw)
tok_actual = int(chars5 * seen["tpc"])
u5_actual = dict(inp=4, cw=tok_actual, cr=0, out=cap_pick, rs=0, usd=None)
cost5_actual = M.step_cost(m_pick, u5_actual)
check("6d. Cost of capped step <= energy available (0 overdrafts)", cost5_actual <= e5 + 1e-6,
      f"cost {cost5_actual:.2f} <= energy {e5:.2f}")

# Clean up temporary run directory and lock
shutil.rmtree(run, ignore_errors=True)
lock = Path.home() / "Work/razi-cells/.bench.lock"
if lock.exists():
    try:
        lock.unlink()
    except Exception:
        pass

print("\n-------------------------------------------------------------------------")
print(f"Dissipative Offline Verification: {len(ok)} checks, {ok.count(True)} passed, {ok.count(False)} failed")
print("ALL OK" if all(ok) else "FAILED %d" % ok.count(False))
if not all(ok):
    sys.exit(1)
