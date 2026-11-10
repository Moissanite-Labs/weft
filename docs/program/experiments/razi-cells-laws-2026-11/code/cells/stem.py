#!/usr/bin/env python3
"""stem.py: stem pilot (IDEAS T-J1, T-K1, J4a to J4e, K3, K8).

A flat colony (metab.py under colony.py) is born committed: one cell per part, each with its own energy,
and no cell hears from the tissue. Here one uncommitted stem cell holds all the energy and has no body.

What is different from the flat colony, and nothing else:
  - Asymmetric division (J4b, K3). The stem stays uncommitted. A daughter is born committed to one part,
    with the energy, start model, start effort and one line that the stem gives it.
  - Niche signal (J4a). The stem sees every part's state: no cell, working, resting, dead, score, energy.
  - Rest and wake (J4c). A daughter may rest; its unspent energy returns to the stem (metab.py CELL_HEIR).
    The stem may feed a resting or dead part again, and that cell wakes with its body and memory.
  - Quiescence. The stem sleeps while cells work and wakes when one stops.

Daughters are ordinary metab.py cells: same laws, same bench, same kits, same prices, same reward.
The colony is born with the same total energy as the flat colony (parts x E0).

  python stem.py RUN_DIR needs.json     needs.json: [{"name", "kit", "need"}]
Writes RUN_DIR/stem/log.jsonl and RUN_DIR/summary.json.
"""
from __future__ import annotations

import json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("CELL_KIT", "fibmod")  # metab.py needs a kit to import; the stem has no body and never uses it
os.environ["CELL_HEIR"] = "stem"
import metab as M  # noqa: E402
import cell as C  # noqa: E402

STEM_AGE_FUSE = int(os.environ.get("STEM_AGE_FUSE", "40"))   # safety only
WAIT_FUSE = int(os.environ.get("STEM_WAIT_FUSE", "1500"))     # seconds, safety only

SYSTEM = """You are the stem cell of a colony. You have no body and no bench: you build nothing yourself.
You hold the colony's energy and decide where it goes.
The facts of your world:
- The NEED has several parts. A part is worked by one cell committed to it. That cell writes a body for its
  part, the bench scores it, and a scored win beyond noise earns that cell energy in proportion to the log of the gain.
- `feed` gives some of your energy to one part. If the part has no cell, one is born committed to it. A resting
  or dead cell that is fed wakes and works again, with its body and memory as it left them. You choose the model
  and effort it starts with, and you may send one line with it.
- Every step of every cell costs energy: a fixed living cost plus the price of the thinking. The same holds for
  you. There is no credit.
- A cell may rest when it chooses. Its unspent energy returns to you. A cell at zero energy dies. Its body stays
  and is scored as it is.
- `wait` puts you to sleep until a working cell stops. The call costs one step, the sleep costs nothing.
- You may `rest` at any time. Working cells finish with what they hold. Energy you still hold stays unspent.
- You choose how you think. Any tool call may set `model` and `effort` for your own next step.
TISSUE shows every part and its cell. LIBRARY holds the colony's wins, losses and lessons.
Call exactly one tool per reply."""

_EXPR = M._EXPR
_START = {"start_model": {"type": "string", "enum": list(M.MENU), "description": "what the fed cell thinks with at first"},
          "start_effort": {"type": "string", "enum": list(M.EFFORTS), "description": "how hard it thinks at first"}}


def _spec(name: str, desc: str, props: dict, req: list[str]) -> C.ToolSpec:
    return C.ToolSpec(name, desc, {"type": "object", "properties": {**props, **_EXPR}, "required": req})


TOOLS = [
    _spec("feed", "Give energy to one part. Births its cell if it has none, wakes it if it rests or is dead.",
          {"part": {"type": "string"}, "energy": {"type": "number"},
           "note": {"type": "string", "description": "one line the cell reads with its need (max 300 chars)"}, **_START},
          ["part", "energy"]),
    _spec("wait", "Sleep until a working cell stops.", {}, []),
    _spec("rest", "Stop acting. One paragraph: what the colony built and what you chose not to spend on.",
          {"result": {"type": "string"}}, ["result"]),
]
USAGE: dict = {}


async def _think(prompt: str, sid: str, model: str, effort: str, cap: int) -> tuple[dict | None, str, str]:
    msgs = [C.Message.system(SYSTEM), C.Message.user(prompt)]
    text, act, route = [], None, ""
    USAGE.clear()
    async for ev in C.router().stream("cell-" + model, msgs, TOOLS, session_id=sid, max_tokens=cap, reasoning=effort):
        if ev.usage is not None:
            u = ev.usage
            USAGE.update(inp=u.input_tokens, out=u.output_tokens, cr=u.cache_read_tokens,
                         cw=u.cache_write_tokens, rs=u.reasoning_tokens, usd=u.cost_usd)
        if ev.kind == "text":
            text.append(ev.text)
        elif ev.kind == "tool_call" and ev.tool_call and act is None:
            act = {"do": ev.tool_call.name, **(ev.tool_call.arguments or {})}
        elif ev.kind == "error":
            raise RuntimeError(f"model error {ev.status}: {(ev.error or '')[:160]}")
        elif ev.kind == "done":
            route = ev.route
    raw = "".join(text)
    return act or C.parse_text(raw), raw, route


def think(prompt: str, sid: str, model: str, effort: str, cap: int) -> tuple[dict | None, str, str]:
    import asyncio
    return asyncio.run_coroutine_threadsafe(_think(prompt, sid, model, effort, cap), C.R._BG["loop"]).result(240)


class Proc:
    """One waking life of a committed cell: its own process, the unchanged metab.py runtime."""

    def __init__(self, run: Path, part: str, kit_name: str, model: str, effort: str):
        self.fh = open(run / f"{part}.out", "a")
        env = {**os.environ, "CELL_KIT": kit_name, "CELL_HEIR": "stem"}
        self.p = subprocess.Popen([sys.executable, str(HERE / "metab.py"), "wake", str(run / part),
                                   "--model", model, "--effort", effort], stdout=self.fh, stderr=subprocess.STDOUT, env=env)

    def done(self) -> bool:
        return self.p.poll() is not None

    def join(self, timeout: float) -> None:
        try:
            self.p.wait(timeout)
        except subprocess.TimeoutExpired:
            pass
        if self.done():
            self.fh.close()


launch = Proc  # the offline check swaps this for an in-process stand-in


# ---- what the stem sees --------------------------------------------------------------------------------
def part_state(run: Path, part: str, live: dict) -> tuple[str, dict | None]:
    e = M.ledger(run / "stem").get(part)
    if e is None:
        return "no cell yet", None
    return ("working" if part in live and not live[part].done() else
            "working" if e["state"] == "alive" and part in live else e["state"]), e


def tissue(run: Path, parts: dict, live: dict, meta: dict) -> str:
    rows = []
    for name in parts:
        st, e = part_state(run, name, live)
        if e is None:
            rows.append(f"- {name}: no cell yet")
            continue
        a = C.get_assay(run / name)
        score = (f"first score {(a.get('first') or a['baseline']):.4g}, gain since then {e['fit']:+.1%}" if a else "no assay yet")
        last = (run / name / "RESULT").read_text()[:200].replace("\n", " ") if (run / name / "RESULT").exists() else ""
        m = meta.get(name, {})
        rows.append(f"- {name}: {st}, holds {max(e['e'], 0):.0f}. Fed {e['born'] + e['got']:.0f} in {m.get('feeds', 0)} "
                    f"feed(s), spent {e['spent']:.0f}, earned {e['earned']:.0f}, returned {e['gave']:.0f}, age {e['age']} steps. "
                    f"{score}. Last start: {m.get('model', '?')}/{m.get('effort', '?')}."
                    + (f" Its last words: {last}" if last and st != "working" else ""))
    return "\n".join(rows)


def stem_prompt(run: Path, need: str, parts: dict, live: dict, meta: dict, history: list, model: str, effort: str,
                costs: list[str]) -> str:
    me = M.ledger(run / "stem")["stem"]
    lib = run / "LIBRARY.md"
    lib_t = lib.read_text()[-2500:] if lib.exists() else "(empty)"
    menu = ", ".join(f"{m} {M.price(m)[0]:g}/{M.price(m)[1]:g}" for m in M.MENU)
    h = "\n\n".join(f"ACTION {a}\nRESULT {r}" for a, r in history[-6:]) or "(none yet)"
    return (f"NEED:\n{need}\n\nTISSUE:\n{tissue(run, parts, live, meta)}\n\n"
            f"LIBRARY (colony results and lessons, newest last):\n{lib_t}\n\n"
            f"VITALS: you hold {me['e']:.0f} (born with {me['born']:.0f}, {me['got']:.0f} returned by resting cells, "
            f"{me['gave']:.0f} fed out, {me['spent']:.0f} spent on your own steps). Age {me['age']} steps.\n"
            f"Your last steps cost: {', '.join(costs[-6:]) or 'none yet'}.\n"
            f"Your next step thinks with: {model}, effort {effort}.\n"
            f"Prices per 1000 tokens, input/output: {menu}. Living cost per step: {M.BASAL:g}.\n"
            f"A cell's scored win of +10% earns it {M.REWARD * M.math.log1p(0.1):.0f}, +100% earns it "
            f"{M.REWARD * M.math.log1p(1.0):.0f}.\n\nRECENT:\n{h}\n\nCall one tool.")


# ---- acts -----------------------------------------------------------------------------------------------
def describe(run: Path, part: str) -> str:
    e = M.ledger(run / "stem")[part]
    return (f"{part} is {e['state']}" + (f", gain {e['fit']:+.0%}" if e["assay"] else ", no assay")
            + f", returned {e['gave']:.0f} in all, holds {max(e['e'], 0):.0f}")


def reap(run: Path, live: dict) -> list[str]:
    out = []
    for part in [p for p, h in live.items() if h.done()]:
        live.pop(part).join(1)
        e = M.ledger(run / "stem")[part]
        C.log(run / "stem", event="stopped", part=part, state=e["state"], fit=round(e["fit"], 4), e=round(e["e"], 1))
        out.append(describe(run, part))
    return out


def feed(run: Path, parts: dict, live: dict, meta: dict, act: dict) -> str:
    stem = run / "stem"
    part = str(act.get("part", ""))
    if part not in parts:
        return f"refused: no such part. Parts: {', '.join(parts)}"
    try:
        give = float(act.get("energy") or 0)
    except (TypeError, ValueError):
        give = 0.0
    bal = M.ledger(stem)["stem"]["e"]
    if give <= 0 or bal <= 0:
        return f"refused: state the energy you give (you hold {max(bal, 0):.0f})"
    give = min(give, bal)
    cell = run / part
    led = M.ledger(stem)
    if part in live and led.get(part, {}).get("state") != "alive":
        live[part].join(180)  # it has stopped and is being scored one last time
    reap(run, live)
    note = " ".join(str(act.get("note", "")).split())[:300]
    sm = act.get("start_model") if act.get("start_model") in M.MENU else M.START_MODEL
    se = act.get("start_effort") if act.get("start_effort") in M.EFFORTS else M.START_EFFORT
    m = meta.setdefault(part, {"feeds": 0})
    if part in live:  # still working: the energy reaches it, the start settings do not apply
        M.upd(cell, e=give, got=give)
        M.upd(stem, e=-give, gave=give)
        m["feeds"] += 1
        if note:
            with open(cell / "NEED", "a") as fh:
                fh.write(f"\n\nSIGNAL FROM THE STEM CELL (with {give:.0f} more energy): {note}")
        C.log(stem, event="feed", kind="top-up", part=part, gave=round(give, 1), note=note)
        return f"{part} is working and now has {give:.0f} more energy. Start model and effort do not apply to a working cell."
    kind = "birth" if part not in led else "wake"
    if kind == "birth":
        cell.mkdir(parents=True, exist_ok=True)
        C.kit.ensure(parts[part]["kit"])
        (cell / "NEED").write_text(parts[part]["need"] + C.kit.need_text(parts[part]["kit"])
                                   + (f"\n\nFROM THE STEM CELL THAT FED YOU: {note}" if note else ""))
        M.born(cell, give)
    else:
        was = led[part]["state"]
        M.upd(cell, e=give, got=give, state="alive")
        with open(cell / "NEED", "a") as fh:
            fh.write(f"\n\nSIGNAL FROM THE STEM CELL (you were {was}, it fed you {give:.0f} more energy)"
                     + (f": {note}" if note else "."))
    M.upd(stem, e=-give, gave=give)
    m.update(feeds=m["feeds"] + 1, model=sm, effort=se)
    live[part] = launch(run, part, parts[part]["kit"], sm, se)
    C.log(stem, event="feed", kind=kind, part=part, gave=round(give, 1), model=sm, effort=se, note=note)
    return (f"{part}: a cell was born committed to it" if kind == "birth" else f"{part}: its cell woke") + \
        f" with {give:.0f} energy, starting {sm}/{se}."


def wait(run: Path, live: dict) -> str:
    if not live:
        return "refused: no cell is working"
    t0 = time.time()
    while not any(h.done() for h in live.values()):
        if time.time() - t0 > WAIT_FUSE:
            C.log(run / "stem", event="fuse", which="wait")
            return "the cells are still working"
        time.sleep(0.5)
    return "stopped: " + "; ".join(reap(run, live)) + f". Slept {time.time() - t0:.0f} s."


def run_stem(run: Path, needs: list[dict]) -> str | None:
    stem = run / "stem"
    stem.mkdir(parents=True, exist_ok=True)
    parts = {n["name"]: n for n in needs}
    need = (f"The colony's need has {len(parts)} parts. Each part is scored on its own by the bench, as the gain of "
            "its body over that part's first accepted score.\n" + "\n".join(f"- {k}: {v['need']}" for k, v in parts.items()))
    (stem / "NEED").write_text(need)
    M.born(stem, M.E0 * len(parts))
    C.NAMES = {t.name for t in TOOLS}
    live: dict = {}
    meta: dict = {}
    history: list[tuple[str, str]] = []
    costs: list[str] = []
    model, effort = M.START_MODEL, M.START_EFFORT
    fails = waits = 0
    result = None
    seen: dict = {}
    fixed = M.fixed_chars(SYSTEM, TOOLS)
    i = -1
    while True:
        i += 1
        me = M.ledger(stem)["stem"]
        if me["e"] <= M.BASAL and not live:
            M.upd(stem, state="dead")
            C.log(stem, event="death", age=me["age"])
            break
        if me["e"] <= M.BASAL:  # cannot pay for a step: it sleeps until energy returns (or no cell is left)
            C.log(stem, event="starved_sleep")
            wait(run, live)
            continue
        if me["age"] >= STEM_AGE_FUSE:
            M.upd(stem, state="dead")
            C.log(stem, event="fuse", which="age")
            break
        try:
            prompt = stem_prompt(run, need, parts, live, meta, history, model, effort, costs)
            used, cap, est = M.pick(model, prompt, me["e"], seen, fixed)
            if used is None and not live:  # cannot pay for a thought and nothing can return energy
                M.upd(stem, state="dead")
                C.log(stem, event="death", why="cannot pay for a thought", e=round(me["e"], 1), age=me["age"])
                break
            if used is None:  # it sleeps until energy returns
                C.log(stem, event="starved_sleep", e=round(me["e"], 1))
                wait(run, live)
                continue
            if used != model:
                C.log(stem, event="downshift", frm=model, to=used, e=round(me["e"], 1), est=round(est, 1))
                history.append(("(law)", f"you could not pay for a thought on {model}, so you now think with {used}"))
                model = used
            act, raw, route = think(prompt, "cell-stem", model, effort if cap >= 2048 else "none", cap)
            u = dict(USAGE)
            cost = M.step_cost(model, u)
            M.observe(model, prompt, u, cost, seen, fixed)
            if cost > me["e"]:
                C.log(stem, event="overdraft", e=round(me["e"], 1), cost=round(cost, 1), est=round(est, 1))
            M.upd(stem, e=-cost, spent=cost, age=1)
            costs.append(f"{cost:.0f} ({model}/{effort})")
            C.log(stem, step=i, usage=u, route=route, model=model, effort=effort, cost=round(cost, 1), cap=cap,
                  est=round(est, 1))
            if act is None:
                C.log(stem, step=i, bad_reply=raw[:200], bad_len=len(raw), route=route)
                raise ValueError("no tool call in reply; call exactly one tool")
        except Exception as e:
            msg = str(e)
            m = re.search(r"reopens in (\d+)s", msg)
            if ("429" in msg or isinstance(e, TimeoutError)) and waits < 6:
                waits += 1
                w = min(int(m.group(1)) + 2 if m else 20, 120)
                C.log(stem, step=i, backoff=w, why=msg[:120] or type(e).__name__)
                time.sleep(w)
                continue
            fails += 1
            history.append(("(invalid)", f"{type(e).__name__}: {str(e)[:200]}"))
            C.log(stem, step=i, error=f"{type(e).__name__}: {str(e)[:200]}")
            if fails >= 3:
                M.upd(stem, state="dead")
                C.log(stem, event="apoptosis")
                break
            continue
        fails = 0
        do = act.get("do")
        nm, ne = act.pop("model", None), act.pop("effort", None)
        um, ue = model, effort
        if do == "feed":
            res = feed(run, parts, live, meta, act)
        elif do == "wait":
            res = wait(run, live)
        elif do == "rest":
            result = str(act.get("result", ""))
            (stem / "RESULT").write_text(result)
            M.upd(stem, state="resting")
            C.log(stem, step=i, act={"do": "rest"}, route=route, model=um, effort=ue, working=sorted(live))
            break
        else:
            res = f"unknown tool {do!r}"
        if nm in M.MENU:
            model = nm
        if ne in M.EFFORTS:
            effort = ne
        act_rec = {k: (v[:300] if isinstance(v, str) else v) for k, v in act.items()}
        history.append((json.dumps(act_rec)[:400] + f" [cost {cost:.0f}]", res))
        C.log(stem, step=i, act=act_rec, res=res[:600], route=route, model=um, effort=ue, next=[model, effort],
              energy=round(M.ledger(stem)["stem"]["e"], 1))
    t0 = time.time()
    while live and time.time() - t0 < WAIT_FUSE:  # working cells finish with what they hold
        reap(run, live)
        time.sleep(0.5)
    if live:
        C.log(stem, event="fuse", which="join", parts=sorted(live))
    return result


def main() -> int:
    run = Path(sys.argv[1]).expanduser().resolve()
    needs = json.loads(Path(sys.argv[2]).read_text())
    run.mkdir(parents=True, exist_ok=True)
    M.start_loop()
    t = time.time()
    res = run_stem(run, needs)
    led = M.ledger(run / "stem")
    summ = {"arm": "stem", "wall_s": round(time.time() - t, 1), "rested": res is not None,
            "ledger": {k: {x: (round(y, 2) if isinstance(y, float) else y) for x, y in v.items()} for k, v in led.items()}}
    (run / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "ledger"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
