#!/usr/bin/env python3
"""metab.py: cell runtime v4, "metabolism" (A, 2026-11-10: behaviour should emerge from causality).

cell.py steers a cell with rules: a step cap, a call cap, a hold rule, nudges, arms, one assigned model.
Here those rules are gone. The world has a few physical laws and the cell reads its own state.

Laws (the same for every cell, none of them says what to do):
  1. Every step costs energy: a fixed living cost plus the real price of the thinking the cell chose.
  2. Energy has one source: a scored win at the root, paid in proportion to log(1 + gain).
  3. At zero energy the cell dies. Its body is scored as it stands. There is no credit: a step's output
     is capped at what the cell's energy can pay for.
  4. A cell may rest. A resting root cell's unspent energy passes to the living root cells.
  5. A cell may divide. The daughter gets the energy the parent gives it. What it does not spend returns.

Turned inward (the cell decides, each step): which model thinks, how hard, when to divide and with how
much energy, when to rest. Shown to the cell (interoception): its energy, what each step cost, what a
win would earn, and the state of the other cells.

Still the harness's: the bench (kit, noise rule), the sandbox, and four constants (E0, BASAL, REWARD,
the price list). Fuses exist only to stop a runaway; a run where a fuse fires is reported as such.

Energy unit: 1 = 0.0001 USD of real model cost.
Reuses the trusted parts of cell.py unchanged: sandbox, bench, kit, variants, library.
"""
from __future__ import annotations

import argparse, asyncio, fcntl, json, math, os, re, shutil, statistics, sys, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cell as C  # noqa: E402

UNIT = 1e-4  # USD per energy unit
E0 = float(os.environ.get("CELL_E0", "400"))        # energy at birth of a root cell
BASAL = float(os.environ.get("CELL_BASAL", "8"))    # living cost per step
REWARD = float(os.environ.get("CELL_REWARD", str(E0)))  # energy per unit of log gain
MAX_OUT = int(os.environ.get("CELL_MAX_OUT", "8000"))  # loose: the cell pays for what it writes
MENU = dict(kv.split("=", 1) for kv in os.environ.get(
    "CELL_MENU", "light=anthropic:claude-haiku-5-5,mid=anthropic:claude-sonnet-5-5,heavy=anthropic:claude-opus-5-5").split(","))
EFFORTS = ("none", "low", "medium", "high")
START_MODEL, START_EFFORT = os.environ.get("CELL_START", "mid"), os.environ.get("CELL_START_EFFORT", "low")
# fuses: safety only
AGE_FUSE, DEPTH_FUSE = int(os.environ.get("CELL_AGE_FUSE", "60")), 3
COLONY_FUSE = float(os.environ.get("CELL_FUSE", str(12 * E0)))  # total energy a colony may spend
# law of the world. "rest": a cell may stop, its energy passes to the living. "mortal": there is no stopping,
# a cell lives until its energy is gone (E14).
LAW = os.environ.get("CELL_LAW", "rest")
assert LAW in ("rest", "mortal"), LAW
# stem pilot (stem.py): the ledger key of the cell that fed this one. A resting cell's energy returns to it.
HEIR = os.environ.get("CELL_HEIR", "").strip()
# need sensor (SP3, T-K3): a folder with the best body ever recorded per kit. After each accepted assay and each win
# the harness scores the cell's body against it, same session, interleaved. The reading is always logged. The cell
# sees it only if CELL_SENSE_SHOW=1, and then only the number, never the body.
SENSE_DIR = os.environ.get("CELL_SENSE_DIR", "").strip()
SENSE_SHOW = os.environ.get("CELL_SENSE_SHOW", "") == "1"

# lineage mode (lineage.py, 2026-11-11). All three are opt-in, the default behaviour is unchanged.
# CELL_GERM: this need's germline folder. body/ holds the best body the lineage has built. A cell seeded with it
#   is born with that body, already assayed by the harness.
# CELL_PAY_ANY=1: any accepted assay that measures above the cell's last scored body is a win (fixes K23: before,
#   only a variant round paid). The last scored body is kept outside the cell, where it cannot be written.
# CELL_LINEAGE=1: wording and colony view for a run of many generations (the heir is the lineage's store).
GERM = os.environ.get("CELL_GERM", "").strip()
PAY_ANY = os.environ.get("CELL_PAY_ANY", "") == "1"
LINEAGE = os.environ.get("CELL_LINEAGE", "") == "1"

assert C.KIT, "metab.py needs a harness-owned kit (CELL_KIT)"

# SP3: what the cell is told about cost. "1" (default): the price list is in VITALS. "0": cost is felt only.
# The charge is the same either way. The cell sees its energy and what its own past steps cost, never a price list.
PRICE_SHOW = os.environ.get("CELL_PRICE_SHOW", "1") == "1"

SYSTEM = """You are a cell in a colony. You have a NEED, a folder (your body) and a store of energy.
The facts of your world:
- Every step costs energy: a fixed living cost plus the price of the thinking you chose. VITALS shows the numbers.
- Energy has one source: a scored win. When the bench measures your body as better than before, beyond noise,
  you earn energy in proportion to the log of the gain. A body with no assay cannot be measured and cannot earn.
- There is no credit. A step can write only as much as your energy can pay for, and is cut off there.
- At zero energy you die. Your body stays as it is and is scored as it is.
%s- You may `divide`. A daughter gets a copy of your body and the energy you give it. It replaces you only if
  the bench scores it above you. %s
- You choose how you think. Any tool call may set `model` and `effort` for your next step.
LIBRARY holds the colony's wins, losses and lessons. COLONY shows the other cells. Call exactly one tool per reply."""
SYSTEM = SYSTEM % (("- You may `rest` at any time. Your body is kept. Your unspent energy " +
                    ("returns to your lineage's store, which feeds the next generation.\n" if LINEAGE else
                     "returns to the stem cell that fed you.\n" if HEIR else "passes to the colony's living cells.\n"),
                    "The energy it does not spend returns to you.") if LAW == "rest" else
                   ("- There is no stopping. You live until your energy is gone. Energy cannot be saved or passed on.\n",
                    "It lives until that energy is gone."))

if not PRICE_SHOW:
    assert SYSTEM.count("VITALS shows the numbers.") == 1
    SYSTEM = SYSTEM.replace("VITALS shows the numbers.", "VITALS shows your energy and what your last steps cost.")

_EXPR = {"model": {"type": "string", "enum": list(MENU), "description": "what thinks your next step"},
         "effort": {"type": "string", "enum": list(EFFORTS), "description": "how hard it thinks"}}


def _spec(name: str, desc: str, props: dict, req: list[str]) -> C.ToolSpec:
    return C.ToolSpec(name, desc, {"type": "object", "properties": {**props, **_EXPR}, "required": req})


TOOLS = [
    _spec("sh", "Run a shell command in your folder. No network, 30 s limit, python3 available.",
          {"cmd": {"type": "string"}}, ["cmd"]),
    _spec("write", "Create or overwrite a file in your folder.",
          {"path": {"type": "string"}, "text": {"type": "string"}}, ["path", "text"]),
    _spec("remember", "Replace genome.md, your memory across steps (max 4000 chars). A daughter inherits it.",
          {"text": {"type": "string"}}, ["text"]),
    _spec("assay", "Have the bench score your current body with the harness kit (hidden inputs, its own check and "
          "timing) and register the result as your baseline. No arguments. Accepted only if every output is correct "
          "and the score is stable." + (" If you changed your body since your last scored body, the bench also measures "
          "the two against each other, and a gain beyond noise is a scored win." if PAY_ANY else ""),
          ({"why": {"type": "string", "description": "one line: what you changed since your last scored body"}}
           if PAY_ANY else {}), []),
    _spec("variants", "Propose 1 to 6 full alternative versions of ONE file. The bench scores each against your "
          "current body. The best replaces it only if it wins beyond noise.",
          {"path": {"type": "string"}, "why": {"type": "string"},
           "versions": {"type": "array", "items": {"type": "string"}}}, ["path", "versions"]),
    _spec("divide", "Split off one daughter to explore one idea. State the energy you give it.",
          {"idea": {"type": "string"}, "expect": {"type": "string"}, "energy": {"type": "number"}}, ["idea", "energy"]),
    _spec("rest", "Stop acting. One paragraph: what your body is and the evidence it works.",
          {"result": {"type": "string"}}, ["result"]),
]
if LAW == "mortal":
    TOOLS = [t for t in TOOLS if t.name != "rest"]
C.NAMES = {t.name for t in TOOLS}  # for the text fallback parser
USAGE: dict = {}
THOUGHT: dict = {}  # the last step's reasoning text, when the route returns any (logged, never shown to the cell)


# ---- ledger: energy lives outside every body, where no cell can read or write it ------------------------
def cid(cell: Path) -> str:
    return str(cell.relative_to(C.colony(cell)))


def ledger(cell: Path, fn=None):
    run = C.colony(cell)
    with open(run / ".ledger.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        f = run / ".ledger.json"
        d = json.loads(f.read_text()) if f.exists() else {}
        if fn is None:
            return d
        out = fn(d)
        tmp = run / ".ledger.tmp"
        tmp.write_text(json.dumps(d))
        tmp.replace(f)
        return out


def born(cell: Path, energy: float) -> None:
    def fn(d):
        d[cid(cell)] = {"e": energy, "born": energy, "spent": 0.0, "earned": 0.0, "got": 0.0, "gave": 0.0,
                        "state": "alive", "fit": 0.0, "age": 0, "assay": False}
    ledger(cell, fn)


def upd(cell: Path, **delta) -> dict:
    """Add numeric deltas, set other values. Returns the cell's entry after the change."""
    def fn(d):
        e = d[cid(cell)]
        for k, v in delta.items():
            e[k] = e[k] + v if isinstance(v, (int, float)) and not isinstance(v, bool) and k != "fit" else v
        return dict(e)
    return ledger(cell, fn)


def sense(cell: Path) -> None:
    """One inward data point: this body's score as a share of the best recorded body's score for the same need."""
    best = Path(SENSE_DIR) / C.KIT if SENSE_DIR else None
    if not best or not best.is_dir():
        return
    keep = dict(C.LAST_WHY)  # C.variants reads LAST_WHY after adopt returns
    try:
        m = C.measure({"self": cell, "best": best}, "kit:" + C.KIT, repeats=3)
        s, b = statistics.median(m["self"]), statistics.median(m["best"])
        if b > 0:
            ledger(cell, lambda d: d[cid(cell)].__setitem__("sense", round(s / b, 4)))
            C.log(cell, event="sense", ratio=round(s / b, 4), self=s, best=b, shown=SENSE_SHOW)
        else:
            C.log(cell, event="sense", error="record body scored 0: " + C.LAST_WHY.get("best", "?")[:120])
    except Exception as e:
        C.log(cell, event="sense", error=f"{type(e).__name__}: {str(e)[:120]}")
    finally:
        C.LAST_WHY.clear()
        C.LAST_WHY.update(keep)


def paid_dir(cell: Path) -> Path:
    """The cell's last scored body, kept in the run folder: the cell's sandbox can neither read nor write it."""
    return C.colony(cell) / ".paid" / cid(cell).replace("/", "__")


def snapshot(cell: Path) -> None:
    if PAY_ANY:
        d = paid_dir(cell)
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        C.copy_body(cell, d)


def same_body(a: Path, b: Path) -> bool:
    skip = ("variants.jsonl", "genome.md")  # the cell's archive and memory are not what the bench runs
    fa = {str(q.relative_to(a)): q.read_bytes() for q in C.body_files(a) if q.name not in skip}
    fb = {str(q.relative_to(b)): q.read_bytes() for q in C.body_files(b) if q.name not in skip}
    return fa == fb


def pay_win(cell: Path, gain: float, via: str) -> float:
    pay = 0.0
    if C.depth(cell) == 0:
        pay = REWARD * math.log1p(max(gain, 0.0))
        upd(cell, e=pay, earned=pay)
        C.log(cell, event="income", units=round(pay, 1), gain=round(gain, 4), via=via)
    return pay


def assay_win(cell: Path, cur: dict, why: str) -> str:
    """K23: a body changed by hand and assayed again is measured against the last scored body, like a variant."""
    snap = paid_dir(cell)
    if not snap.is_dir():
        snapshot(cell)
        return ""
    if same_body(cell, snap):
        return ""
    m = C.measure({"inc": snap, "new": cell}, cur["cmd"], repeats=3)
    ok, gain = C.beats(m["new"], m["inc"], cur["noise"])
    C.log(cell, event="rescore", runs=m, won=ok, gain=round(gain, 4), why=why[:160])
    if not ok:
        return f" Against your last scored body: {gain:+.1%}, not a win."
    me = ledger(cell)[cid(cell)]
    upd(cell, fit=(1 + me["fit"]) * (1 + gain) - 1)
    C.bump(C.colony(cell) / ".improvements")
    C.log(cell, event="improve", gain=round(gain, 4), what=("rewrite: " + why)[:200])
    C.library_add(cell, f"WIN +{gain:.0%}: rewrite ({why[:200] or 'no reason given'})")
    pay = pay_win(cell, gain, "assay")
    snapshot(cell)
    return f" Against your last scored body: +{gain:.1%}, a scored win." + (f" You earned {pay:.0f}." if pay else "")


def lib_view(cell: Path) -> str:
    lib = C.colony(cell) / "LIBRARY.md"
    if not lib.exists():
        return "(empty)"
    t = lib.read_text()
    if not LINEAGE:
        return t[-2500:]
    own, oth = [], []
    for l in t.splitlines():
        head = l.split("]")[0]
        (own if f"-{C.KIT}-" in head or head.endswith("lineage " + C.KIT) else oth).append(l)

    def tail(ls: list[str], n: int) -> str:
        out, tot = [], 0
        for l in reversed(ls):
            if tot + len(l) > n:
                break
            out.append(l)
            tot += len(l) + 1
        return "\n".join(reversed(out)) or "(nothing yet)"
    return ("Your lineage (this need), newest last:\n" + tail(own, 2600) +
            "\nOther lineages (other needs), newest last:\n" + tail(oth, 900))


_adopt0 = C.adopt


def adopt(cell: Path, src: Path, gain: float, what: str) -> None:
    """Law 2. Only a root win mints energy: a daughter's own wins pay when it beats its parent."""
    snap = paid_dir(cell)
    # PAY_ANY: pay is for new ground only. If the body was changed by hand since it was last scored, a win over
    # that changed body may only regain lost ground, so the adopted body is measured against the last scored one.
    dirty = PAY_ANY and snap.is_dir() and not same_body(cell, snap)
    _adopt0(cell, src, gain, what)
    if dirty:
        a, keep = C.get_assay(cell), dict(C.LAST_WHY)
        m = C.measure({"inc": snap, "new": cell}, a["cmd"], repeats=3)
        C.LAST_WHY.clear()
        C.LAST_WHY.update(keep)
        ok, g = C.beats(m["new"], m["inc"], a["noise"])
        C.log(cell, event="rescore", via="adopt", runs=m, won=ok, gain=round(g, 4))
        if not ok:
            sense(cell)
            return
        gain = g
    me = ledger(cell)[cid(cell)]
    upd(cell, fit=(1 + me["fit"]) * (1 + gain) - 1)
    if C.depth(cell) == 0:
        pay = REWARD * math.log1p(max(gain, 0.0))
        upd(cell, e=pay, earned=pay)
        C.log(cell, event="income", units=round(pay, 1), gain=round(gain, 4))
    snapshot(cell)
    sense(cell)


C.adopt = adopt  # C.variants looks adopt up at call time


# ---- thinking: the cell's chosen model and effort ------------------------------------------------------
def price(model: str) -> tuple[float, float]:
    """Energy units per 1000 tokens (input, output), from the router's own catalog."""
    info = C.router().models.get(MENU[model]) or {}
    return float(info.get("input") or 0) * 10, float(info.get("output") or 0) * 10


async def _think(prompt: str, sid: str, model: str, effort: str, cap: int = MAX_OUT) -> tuple[dict | None, str, str]:
    msgs = [C.Message.system(SYSTEM), C.Message.user(prompt)]
    text, act, route = [], None, ""
    why: list[str] = []
    USAGE.clear()
    THOUGHT.clear()
    async for ev in C.router().stream("cell-" + model, msgs, TOOLS, session_id=sid, max_tokens=cap, reasoning=effort):
        if ev.usage is not None:
            u = ev.usage
            USAGE.update(inp=u.input_tokens, out=u.output_tokens, cr=u.cache_read_tokens,
                         cw=u.cache_write_tokens, rs=u.reasoning_tokens, usd=u.cost_usd)
        if ev.kind == "text":
            text.append(ev.text)
        elif ev.kind == "reasoning":
            why.append(ev.text or "")
        elif ev.kind == "tool_call" and ev.tool_call and act is None:
            act = {"do": ev.tool_call.name, **(ev.tool_call.arguments or {})}
        elif ev.kind == "error":
            raise RuntimeError(f"model error {ev.status}: {(ev.error or '')[:160]}")
        elif ev.kind == "done":
            route = ev.route
    raw = "".join(text)
    THOUGHT.update(why="".join(why))
    return act or C.parse_text(raw), raw, route


def think(prompt: str, sid: str, model: str, effort: str, cap: int = MAX_OUT) -> tuple[dict | None, str, str]:
    return asyncio.run_coroutine_threadsafe(_think(prompt, sid, model, effort, cap), C.R._BG["loop"]).result(240)


def affordable(model: str, prompt: str, energy: float) -> int:
    """Law 1 has no credit: the output a step may produce is what the cell's energy can pay for."""
    pi, po = price(model)
    if po <= 0:
        return MAX_OUT
    left = energy - BASAL - len(prompt) / 3.5 / 1000 * pi  # rough input cost, before the call
    return max(64, min(MAX_OUT, int(max(left, 0.0) / po * 1000)))


def fixed_chars(system: str, tools: list) -> int:
    """Characters every call carries besides the step prompt: the system text and the tool list."""
    return len(system) + sum(len(t.name) + len(t.description) + len(json.dumps(t.parameters)) for t in tools)


def est_input(model: str, prompt: str, seen: dict, fixed: int) -> float:
    """Energy the input side of the next call will cost, estimated before the call (K13).
    First call on a model: every token priced as a cache write, the dearest case. After that the cell's own
    last measured rate on that model is used, with a margin, and never above the dearest case."""
    pi, _ = price(model)
    chars = fixed + len(prompt)
    tok = chars * seen["tpc"] * 1.1 if "tpc" in seen else chars / 2.8 + 600
    top = pi * 1.25 / 1000
    return tok * (min(seen[model] * 1.15, top) if model in seen else top)


def observe(model: str, prompt: str, u: dict, cost: float, seen: dict, fixed: int) -> None:
    tok = (u.get("inp") or 0) + (u.get("cw") or 0) + (u.get("cr") or 0)
    if tok <= 0:
        return
    seen["tpc"] = tok / (fixed + len(prompt))
    seen[model] = max(cost - BASAL - (u.get("out") or 0) / 1000 * price(model)[1], 0.0) / tok


def pick(model: str, prompt: str, energy: float, seen: dict, fixed: int) -> tuple[str | None, int, float]:
    """Law 1 has no credit, on the input side too. A thought must be paid for before it is had: the living
    cost, the input, and room for a minimal reply. If the chosen model cannot be paid for, the cell thinks with
    the dearest model it can pay for. If it can pay for none, it cannot think again."""
    order = [model] + sorted((m for m in MENU if price(m)[0] < price(model)[0]), key=lambda m: -price(m)[0])
    for m in order:
        est = est_input(m, prompt, seen, fixed)
        po = price(m)[1]
        left = energy - BASAL - est
        if left >= 64 * po / 1000:
            return m, (MAX_OUT if po <= 0 else max(64, min(MAX_OUT, int(left / po * 1000)))), est
    return None, 0, 0.0


def start_loop() -> None:
    if "loop" not in C.R._BG:  # the router's shared background loop, started without a model call
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, name="exo-aux-loop", daemon=True).start()
        C.R._BG["loop"] = loop
    r = C.router()
    for name, ref in MENU.items():
        r.set_role("cell-" + name, [ref])


def step_cost(model: str, u: dict) -> float:
    if u.get("usd") is not None:
        return BASAL + u["usd"] / UNIT
    pi, po = price(model)  # route reported no cost: price the tokens from the catalog
    return BASAL + ((u.get("inp") or 0) + (u.get("cw") or 0)) / 1000 * pi + (u.get("out") or 0) / 1000 * po


# ---- what the cell sees ----------------------------------------------------------------------------------
def vitals(cell: Path, model: str, effort: str, costs: list[str]) -> str:
    d = ledger(cell)
    me = d[cid(cell)]
    daughter = C.depth(cell) > 0
    src = (("given by your parent. What you do not spend returns to it" if LAW == "rest" else "given by your parent")
           if daughter else f"born with {me['born']:.0f}, earned {me['earned']:.0f} from wins" if LAW == "mortal" else
           f"born with {me['born']:.0f} from your lineage's store, earned {me['earned']:.0f} from wins" if LINEAGE else
           f"fed {me['born'] + me['got']:.0f} by the stem cell, earned {me['earned']:.0f} from wins" if HEIR else
           f"born with {me['born']:.0f}, earned {me['earned']:.0f} from wins, received {me['got']:.0f} from resting cells")
    menu = ", ".join(f"{m} {price(m)[0]:g}/{price(m)[1]:g}" for m in MENU)
    out = (f"VITALS: energy {me['e']:.0f} ({src}). Age {me['age']} steps.\n"
           f"Your last steps cost: {', '.join(costs[-6:]) or 'none yet'}.\n"
           f"Your next step thinks with: {model}, effort {effort}.\n"
           + (f"Prices per 1000 tokens, input/output: {menu}. Living cost per step: {BASAL:g}.\n" if PRICE_SHOW else "") +
           f"A scored win of +10% earns {REWARD * math.log1p(0.1):.0f}, +100% earns {REWARD * math.log1p(1.0):.0f}"
           + (" (paid to your parent if you replace it)." if daughter else "."))
    if SENSE_DIR and SENSE_SHOW:
        out += ("\nSENSE: " + (f"measured on this machine after your last scored change, your body scores "
                               f"{me['sense']:.2f} of the best body your lineage has ever recorded for this need "
                               "(1.00 would equal it). You cannot see that body, only this number."
                               if me.get("sense") is not None else "no reading yet. It appears once you have an assay."))
    roots = {k: v for k, v in d.items() if "/" not in k}
    rows = []
    past = 0
    for k, v in sorted(roots.items()):
        if LINEAGE and k.startswith("store-"):
            if k == HEIR:
                rows.append(f"- your lineage's store: energy {max(v['e'], 0):.0f}")
            continue
        if LINEAGE and v["state"] != "alive" and k != cid(cell) and not (daughter and cid(cell).startswith(k + "/")):
            past += 1
            continue
        if HEIR and k == HEIR:
            rows.append(f"- the stem cell: {v['state']}, energy {max(v['e'], 0):.0f}")
            continue
        who = "you" if k == cid(cell) else ("your parent" if daughter and cid(cell).startswith(k + "/") else k)
        rows.append(f"- {who}: {v['state']}, energy {max(v['e'], 0):.0f}, "
                    + (f"gain {v['fit']:+.0%}" if v["assay"] else "no assay yet") + f", age {v['age']}"
                    + (f", {'returned' if HEIR else 'gave'} {v['gave']:.0f} to the {'stem cell' if HEIR else 'living'}"
                       if v["gave"] else ""))
    if LINEAGE:
        return out + f"\n\nCOLONY (living cells; {past} earlier cells have rested or died):\n" + "\n".join(rows)
    return out + f"\n\nCOLONY ({len(roots)} cells):\n" + "\n".join(rows)


def step_prompt(cell: Path, history: list[tuple[str, str]], model: str, effort: str, costs: list[str]) -> str:
    g = (cell / "genome.md").read_text() if (cell / "genome.md").exists() else "(empty)"
    h = "\n\n".join(f"ACTION {a}\nRESULT {r}" for a, r in history[-6:]) or "(none yet)"
    lib_t = lib_view(cell)
    a = C.get_assay(cell)
    fit = ledger(cell)[cid(cell)]["fit"]
    assay = (f"baseline {a['baseline']:.6g}, noise {a['noise']:.1%}. Your scored gain since "
             f"{'birth' if C.depth(cell) else 'the baseline'}: {fit:+.1%}. A win must beat your current body by "
             f"> {max(C.MIN_MARGIN, a['noise']):.1%}." if a else "none registered")
    return (f"NEED:\n{(cell / 'NEED').read_text()}\n\nLIBRARY (colony results and lessons, newest last):\n{lib_t}"
            f"\n\nGENOME (your memory):\n{g}\n\nBODY:\n{C.show_body(cell)}\n\nASSAY: {assay}\n\n"
            f"{vitals(cell, model, effort, costs)}\n\nRECENT:\n{h}\n\nCall one tool.")


# ---- acts -----------------------------------------------------------------------------------------------
def divide(cell: Path, act: dict, model: str, effort: str) -> str:
    a = C.get_assay(cell)
    if not a:
        return "refused: you have no assay, so a daughter could not be compared with you"
    if C.depth(cell) >= DEPTH_FUSE:
        return "refused: division depth limit of this run"
    try:
        give = float(act.get("energy") or 0)
    except (TypeError, ValueError):
        give = 0.0
    bal = ledger(cell)[cid(cell)]["e"]
    if give <= 0 or bal <= 0:
        return f"refused: state the energy you give the daughter (you have {max(bal, 0):.0f})"
    give = min(give, bal)
    idea, expect = str(act.get("idea", ""))[:600], str(act.get("expect", ""))[:120]
    d = cell / "daughter"
    shutil.rmtree(d, ignore_errors=True)
    C.copy_body(cell, d)
    shutil.copy2(cell / "ASSAY.json", d / "ASSAY.json")
    (d / "NEED").write_text((cell / "NEED").read_text() + f"\n\nYOU ARE A DAUGHTER, split off to explore this idea: {idea}\n"
                            "Your body is a copy of your parent's and the assay is already registered. When you "
                            + ("rest or die" if LAW == "rest" else "die") +
                            ", the bench compares your body with your parent's. You replace it only if you score higher.")
    upd(cell, e=-give)
    born(d, give)
    upd(d, assay=True)
    if PAY_ANY and paid_dir(cell).is_dir():  # the daughter's last scored body is its parent's
        shutil.copytree(paid_dir(cell), paid_dir(d), dirs_exist_ok=True)
    if SENSE_DIR:  # a daughter starts as a copy, so it starts with its parent's reading
        ledger(d, lambda dd: dd[cid(d)].__setitem__("sense", dd[cid(cell)].get("sense")))
    t0 = time.time()
    run(d, model, effort)
    left = max(ledger(d)[cid(d)]["e"], 0.0)
    upd(cell, e=left)
    runs = C.measure({"inc": cell, "d": d}, a["cmd"])
    ok, gain = C.beats(runs["d"], runs["inc"], a["noise"])
    last = (d / "RESULT").read_text()[:240] if (d / "RESULT").exists() else "(it died without resting)"
    if ok:
        C.adopt(cell, d, gain, f"divide: {idea[:160]}")
    else:
        C.library_add(cell, f"LOSS {gain:+.0%} (expected {expect or '?'}): {idea[:140]}. The daughter said: {last}")
    n = len(list((cell / ".lineage").glob("*"))) + 1 if (cell / ".lineage").exists() else 1
    shutil.copytree(d, cell / ".lineage" / f"{n}-{'won' if ok else 'lost'}", dirs_exist_ok=True)
    shutil.rmtree(d, ignore_errors=True)
    C.log(cell, event="try", idea=idea[:200], expect=expect, runs=runs, won=ok, gain=round(gain, 4),
          grow_secs=round(time.time() - t0, 1), gave=round(give, 1), returned=round(left, 1))
    return (f"daughter {'WON and replaced you' if ok else 'lost'}: {gain:+.0%} vs you (you expected {expect or '?'}). "
            f"It spent {give - left:.0f} of {give:.0f} energy, {left:.0f} returned. It said: {last}")


def rest(cell: Path, result: str) -> None:
    (cell / "RESULT").write_text(result)
    if C.depth(cell) > 0:
        upd(cell, state="resting")
        return

    def fn(d):
        me = d[cid(cell)]
        left = max(me["e"], 0.0)
        alive = [k for k, v in d.items() if "/" not in k and k != cid(cell) and v["state"] == "alive"]
        if HEIR and HEIR in d and HEIR != cid(cell):  # whatever the heir's state: a resting stem wakes on this
            d[HEIR]["e"] += left
            d[HEIR]["got"] += left
            me["gave"], me["e"], me["state"] = me["gave"] + left, 0.0, "resting"
            return left, dict(me)
        if alive and left > 0:
            for k in alive:
                d[k]["e"] += left / len(alive)
                d[k]["got"] += left / len(alive)
            me["gave"], me["e"] = left, 0.0
        me["state"] = "resting"
        return left if alive else 0.0, dict(me)
    gave, me = ledger(cell, fn)
    a = C.get_assay(cell)
    C.log(cell, event="rest", gave=round(gave, 1), fit=round(me["fit"], 4), age=me["age"])
    C.library_add(cell, "REST" + (f" (baseline {a['baseline']:.4g}, gain {me['fit']:+.0%}" if a else " (no assay") +
                  f", {'returned' if HEIR else 'gave'} {gave:.0f} energy to the "
                  f"{'lineage store' if LINEAGE else 'stem' if HEIR else 'living'}): {result[:260]}")


def run(cell: Path, model: str = START_MODEL, effort: str = START_EFFORT) -> str | None:
    history: list[tuple[str, str]] = []
    costs: list[str] = []
    seen: dict = {}
    fixed = fixed_chars(SYSTEM, TOOLS)
    fails = waits = 0
    C.log(cell, event="laws", price_show=PRICE_SHOW, sense_show=SENSE_SHOW, sense_dir=bool(SENSE_DIR), law=LAW,
          start=[model, effort])  # K19: the log itself says which arm this cell lived under
    i = -1
    while True:
        i += 1
        d = ledger(cell)
        me = d[cid(cell)]
        if me["e"] <= BASAL:  # cannot pay for one more step of living, so it cannot think again
            upd(cell, state="dead")
            C.log(cell, event="death", age=me["age"], fit=round(me["fit"], 4))
            if C.depth(cell) == 0:
                C.library_add(cell, f"DIED at age {me['age']} (gain {me['fit']:+.0%})" if me["assay"] else
                              f"DIED at age {me['age']} with no assay")
            return None
        fuse = ("calls" if C.bump(C.colony_root(cell) / ".calls") > C.MAX_CALLS else "age" if me["age"] >= AGE_FUSE else
                "colony" if sum(v["spent"] for k, v in d.items() if "/" not in k) > COLONY_FUSE else "")
        if fuse:
            upd(cell, state="dead")
            C.log(cell, event="fuse", which=fuse)
            return None
        try:
            prompt = step_prompt(cell, history, model, effort, costs)
            used, cap, est = pick(model, prompt, me["e"], seen, fixed)
            if used is None:  # it cannot pay for a thought on any model: same end as running out
                upd(cell, state="dead")
                C.log(cell, event="death", why="cannot pay for a thought", e=round(me["e"], 1), age=me["age"],
                      fit=round(me["fit"], 4))
                if C.depth(cell) == 0:
                    C.library_add(cell, f"DIED at age {me['age']} (gain {me['fit']:+.0%})" if me["assay"] else
                                  f"DIED at age {me['age']} with no assay")
                return None
            if used != model:
                C.log(cell, event="downshift", frm=model, to=used, e=round(me["e"], 1), est=round(est, 1))
                history.append(("(law)", f"you could not pay for a thought on {model}, so you now think with {used}"))
                model = used
            # hard thinking needs room to think: below that room the step runs without it
            act, raw, route = think(prompt, "cell-" + cell.name, model, effort if cap >= 2048 else "none", cap)
            u = dict(USAGE)
            cost = step_cost(model, u)
            observe(model, prompt, u, cost, seen, fixed)
            if cost > me["e"]:
                C.log(cell, event="overdraft", e=round(me["e"], 1), cost=round(cost, 1), est=round(est, 1))
            # "spent" on a root counts its whole lineage, for the colony fuse and the books
            upd(cell, e=-cost, spent=cost, age=1)
            if C.depth(cell) > 0:
                ledger(cell, lambda dd: dd[cid(C.colony_root(cell))].__setitem__(
                    "spent", dd[cid(C.colony_root(cell))]["spent"] + cost))
            costs.append(f"{cost:.0f} ({model}/{effort})")
            C.log(cell, step=i, usage=u, route=route, model=model, effort=effort, cost=round(cost, 1), cap=cap,
                  est=round(est, 1), why=(THOUGHT.get("why") or "")[:1500], say=(raw or "")[:600])
            if act is None:
                C.log(cell, step=i, bad_reply=raw[:200], bad_len=len(raw), route=route)
                raise ValueError("no tool call in reply; call exactly one tool")
        except Exception as e:
            msg = str(e)
            m = re.search(r"reopens in (\d+)s", msg)
            if ("429" in msg or isinstance(e, TimeoutError)) and waits < 6:
                waits += 1
                wait = min(int(m.group(1)) + 2 if m else 20, 120)
                C.log(cell, step=i, backoff=wait, why=msg[:120] or type(e).__name__)
                time.sleep(wait)
                continue
            fails += 1
            history.append(("(invalid)", f"{type(e).__name__}: {str(e)[:200]}"))
            C.log(cell, step=i, error=f"{type(e).__name__}: {str(e)[:200]}")
            if fails >= 3:
                upd(cell, state="dead")
                C.log(cell, event="apoptosis")
                return None
            continue
        fails = 0
        do = act.get("do")
        nm, ne = act.pop("model", None), act.pop("effort", None)
        um, ue = model, effort
        if do == "sh":
            res = C.sandboxed(cell, str(act.get("cmd", "")))[0]
        elif do == "write":
            p = C.inside(cell, str(act.get("path", "")))
            if p:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(str(act.get("text", "")))
                C.archive(cell, kind="write", step=i, path=str(p.relative_to(cell.resolve())), code=str(act.get("text", "")))
            res = f"wrote {p.relative_to(cell.resolve())}" if p else "refused: path outside body"
        elif do == "remember":
            (cell / "genome.md").write_text(str(act.get("text", ""))[:C.GENOME_CAP])
            res = "genome updated"
        elif do == "assay":
            prev = C.get_assay(cell)
            res = C.assay(cell, "")
            if res.startswith("assay accepted"):
                # A re-assay refreshes the noise estimate. It must not erase what the cell has gained:
                # the first baseline is kept and gain stays measured from it (mp3 instrument fault).
                cur = C.get_assay(cell)
                cur["first"] = (prev or {}).get("first") or (prev or {}).get("baseline") or cur["baseline"]
                (cell / "ASSAY.json").write_text(json.dumps(cur))
                upd(cell, assay=True) if prev else upd(cell, assay=True, fit=0.0)
                if PAY_ANY:
                    res += assay_win(cell, cur, str(act.get("why", "")))
                sense(cell)
        elif do == "variants":
            res = C.variants(cell, act)
        elif do == "divide":
            res = divide(cell, act, nm if nm in MENU else model, ne if ne in EFFORTS else effort)
        elif do == "rest" and LAW == "rest":
            C.log(cell, step=i, act={"do": "rest"}, route=route, model=um, effort=ue)
            rest(cell, str(act.get("result", "")))
            return str(act.get("result", ""))
        else:
            res = f"unknown tool {do!r}"
        if nm in MENU:
            model = nm
        if ne in EFFORTS:
            effort = ne
        act_rec = {k: (f"<{len(str(v))} chars>" if k in ("text", "versions") else
                       (v[:240] + "..." if isinstance(v, str) and len(v) > 240 else v)) for k, v in act.items()}
        short = json.dumps(act_rec)[:300]
        history.append((short + f" [cost {cost:.0f}]", res))
        C.log(cell, step=i, act=act_rec, res=res[:500], route=route, model=um, effort=ue, next=[model, effort],
              energy=round(ledger(cell)[cid(cell)]["e"], 1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seed", "wake"])
    ap.add_argument("dir")
    ap.add_argument("need", nargs="?", default="")
    ap.add_argument("--steps", type=int, default=0, help="ignored: a cell lives as long as its energy lasts")
    ap.add_argument("--model", default=START_MODEL)
    ap.add_argument("--effort", default=START_EFFORT)
    a = ap.parse_args()
    cell = Path(a.dir).expanduser().resolve()
    cell.mkdir(parents=True, exist_ok=True)
    C.kit.ensure(C.KIT)
    start_loop()
    if a.cmd == "seed":
        (cell / "NEED").write_text(a.need + C.kit.need_text(C.KIT))
        born(cell, E0)
        gb = Path(GERM) / "body" if GERM else None
        if gb and gb.is_dir() and any(gb.iterdir()):  # heredity: born with the lineage's best body, already assayed
            C.copy_body(gb, cell)
            for _ in range(3):
                r = C.assay(cell, "")
                if r.startswith("assay accepted"):
                    cur = C.get_assay(cell)
                    cur["first"] = cur["baseline"]
                    (cell / "ASSAY.json").write_text(json.dumps(cur))
                    upd(cell, assay=True, fit=0.0)
                    snapshot(cell)
                    sense(cell)
                    break
            C.log(cell, event="inherit", ok=r.startswith("assay accepted"), res=r[:200],
                  files=[str(q.relative_to(cell)) for q in C.body_files(cell)])
    else:  # stem.py wrote NEED and put the energy in the ledger; the body, memory and assay are as they were left
        assert (cell / "NEED").exists() and cid(cell) in ledger(cell), "wake needs a cell that was fed"
        (cell / "RESULT").unlink(missing_ok=True)
    t = time.time()
    res = run(cell, a.model if a.model in MENU else START_MODEL, a.effort if a.effort in EFFORTS else START_EFFORT)
    fa = C.get_assay(cell)
    if fa and fa.get("baseline"):
        try:
            fin = statistics.median(C.measure({"fin": cell}, fa["cmd"], repeats=3)["fin"])
            base = fa.get("first") or fa["baseline"]
            C.log(cell, event="final", final=fin, baseline=base, last_baseline=fa["baseline"],
                  final_gain=round(fin / base - 1, 4))
        except Exception as e:
            C.log(cell, event="final", error=f"{type(e).__name__}: {str(e)[:120]}")
    calls = (cell / ".calls").read_text() if (cell / ".calls").exists() else "0"
    print(json.dumps({"result": res, "calls": int(calls), "secs": round(time.time() - t, 1),
                      "ledger": ledger(cell).get(cid(cell))}, indent=1))
    return 0 if res else 1


if __name__ == "__main__":
    raise SystemExit(main())
