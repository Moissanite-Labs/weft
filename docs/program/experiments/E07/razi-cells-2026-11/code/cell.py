"""Stem cells v3: micro-harnesses that start from a NEED and an empty folder and grow their own tools.

What changed from v2 (g2 evidence in ~/Work/razi-cells/exp/g2):
- Membrane: actions are native tool calls, not JSON in text. g2 lost 46 replies: 22 were the model's own
  tool markup (DSML) written as text, 24 were empty. Text JSON and DSML stay as fallbacks.
- Trusted assay: the cell proposes a fitness command once; the harness checks it (exit 0, score > 0,
  measured noise) before anything is ever compared with it. g2 had a split where both sides scored 0.
- Asymmetric mitosis (`try`): the parent body is the incumbent; one daughter grows one idea. Ties keep
  the incumbent. Win threshold comes from measured noise, not a fixed 5%.
- Cheap variation (`variants`): one call proposes up to 6 versions of one file; the bench scores them
  all. The model mutates, the CPU selects.
- Germline: colony LIBRARY.md collects every scored result and lesson. All cells read it.
- Apoptosis: 3 failed steps in a row end the cell.

Run with Exo's python:  ~/Work/exo-live/.venv/bin/python cell.py seed DIR "need..." [--steps N]
"""
from __future__ import annotations
import time
import re

import argparse, asyncio, fcntl, json, os, re, shutil, statistics, subprocess, sys, tempfile, threading, time
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Work/exo-live/src"))
from exo.config import Config  # noqa: E402
from exo.core.models import router as R  # noqa: E402
from exo.core.models.router import Router, aux_sync  # noqa: E402
from exo.core.types import Message, ToolSpec  # noqa: E402

PY = "/opt/homebrew/bin/python3"
MODEL = os.environ.get("CELL_MODEL", "").strip()  # e.g. "anthropic:claude-fable-5-1"
ROLE = "main" if MODEL else os.environ.get("CELL_ROLE", "fast")
GENOME_CAP, OUT_CAP, SH_TIMEOUT = 4000, 2000, 30
MAX_DEPTH, MAX_CALLS = 1, int(os.environ.get("CELL_MAX_CALLS", "120"))
REPEATS, MIN_MARGIN, MAX_NOISE, MAX_VARIANTS = int(os.environ.get("CELL_REPEATS", "5")), 0.03, 0.15, 6
BENCH_LOCK = Path.home() / "Work/razi-cells/.bench.lock"  # machine-wide: one measurement at a time
HIDDEN = ("NEED", "log.jsonl", "ASSAY.json", "RESULT")
_router: Router | None = None
_lock = threading.Lock()

SYSTEM = """You are a cell: a tiny agent that starts with nothing but a NEED and an empty folder (your body).
Grow only the tools your need demands, one step at a time. Call exactly one tool per reply.
Path to fitness: 1) build a correct version and check it. 2) register an `assay`: a shell command that
prints one number, higher is better, 0 if the output is wrong. Make its workload heavy enough (about
0.3 to 3 s) that process startup does not dominate. 3) improve with `variants` (cheap: several versions
of one file in one reply, all scored) or `try` (expensive: a daughter cell explores one bigger idea).
Only scored wins are kept. Read LIBRARY: other cells' results and lessons, often useful to you."""

TOOLS = [
    ToolSpec("sh", "Run a shell command in your folder. No network, 30 s limit, python3 available.",
             {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}),
    ToolSpec("write", "Create or overwrite a file in your folder.",
             {"type": "object", "properties": {"path": {"type": "string"}, "text": {"type": "string"}},
              "required": ["path", "text"]}),
    ToolSpec("remember", "Replace genome.md, your memory across steps (max 4000 chars).",
             {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}),
    ToolSpec("assay", "Register your fitness command. The harness runs it 5 times on your current body and "
             "accepts it only if it exits 0, prints a number > 0, and is stable (spread under 15%).",
             {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}),
    ToolSpec("variants", "Propose 2 to 6 full alternative versions of ONE file. Each is scored by your assay "
             "against the current body; the best is adopted only if it wins beyond noise.",
             {"type": "object", "properties": {"path": {"type": "string"}, "why": {"type": "string"},
              "versions": {"type": "array", "items": {"type": "string"}}}, "required": ["path", "versions"]}),
    ToolSpec("try", "Spawn one daughter cell that explores one idea for half your remaining steps. Its body "
             "replaces yours only if it beats you on the assay beyond noise. State the gain you expect.",
             {"type": "object", "properties": {"idea": {"type": "string"}, "expect": {"type": "string"}},
              "required": ["idea"]}),
    ToolSpec("done", "Finish. One paragraph: what you built and the evidence it works.",
             {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}),
]
NAMES = {t.name for t in TOOLS}


def router() -> Router:
    global _router
    if _router is None:
        _router = Router.from_config(Config.load().models())
        if MODEL:  # pin this cell to an exact model chain, no hidden fallback (role "main" has none)
            _router.set_role("main", [m.strip() for m in MODEL.split(",") if m.strip()])
    return _router


def colony_root(cell: Path) -> Path:
    while (cell.parent / "NEED").exists():
        cell = cell.parent
    return cell


def colony(cell: Path) -> Path:  # the run folder that holds all cells of this colony
    return colony_root(cell).parent


def bump(f: Path, by: int = 1) -> int:
    with _lock:
        n = (int(f.read_text() or 0) if f.exists() else 0) + by
        f.write_text(str(n))
        return n


def log(cell: Path, **rec) -> None:
    rec["t"] = round(time.time(), 2)
    with open(cell / "log.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def archive(cell: Path, **rec) -> None:
    """Keep every code version a cell writes (variants.jsonl), for embedding analysis (IDEAS E1-E6)."""
    rec["t"] = round(time.time(), 2)
    with open(cell / "variants.jsonl", "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def library_add(cell: Path, line: str) -> None:
    line = " ".join(line.split())[:400]  # one line per entry; code never leaks into the germline
    f = colony(cell) / "LIBRARY.md"
    with open(f, "a") as fh:  # appends are small; O_APPEND keeps lines whole across processes
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.write(f"- [{colony_root(cell).name}] {line.strip()[:400]}\n")


def sandboxed(cell: Path, cmd: str, timeout: int = SH_TIMEOUT) -> tuple[str, float]:
    real = os.path.realpath(cell)
    tmp = os.path.join(os.path.realpath(colony_root(cell)), ".tmp")
    os.makedirs(tmp, exist_ok=True)
    prof = (f'(version 1)(allow default)(deny network*)'
            f'(deny file-write*)(allow file-write* (subpath "{real}") (subpath "{tmp}") (literal "/dev/null"))'
            f'(deny file-read* (subpath "{Path.home()}"))(allow file-read* (subpath "{real}"))')
    env = {"PATH": f"{Path(PY).parent}:/usr/bin:/bin", "HOME": real, "TMPDIR": tmp, "LANG": "C.UTF-8"}
    t = time.perf_counter()
    try:
        p = subprocess.run(["sandbox-exec", "-p", prof, "/bin/sh", "-c", cmd], cwd=real, env=env,
                           capture_output=True, text=True, timeout=timeout)
        out = f"exit {p.returncode}\n{p.stdout}{p.stderr}"
    except subprocess.TimeoutExpired:
        out = "timeout"
    dt = time.perf_counter() - t
    return (out if len(out) <= OUT_CAP else out[:OUT_CAP // 2] + "\n...\n" + out[-OUT_CAP // 2:]), dt


def inside(cell: Path, rel: str) -> Path | None:
    p = (cell / rel).resolve()
    return p if p.is_relative_to(cell.resolve()) and p.name not in HIDDEN + ("LINEAGE.md",) else None


def body_files(cell: Path) -> list[Path]:
    return [p for p in sorted(cell.rglob("*")) if p.is_file() and not any(
        part.startswith((".", "daughter-")) for part in p.relative_to(cell).parts) and p.name not in HIDDEN]


def copy_body(src: Path, dst: Path) -> None:
    for p in body_files(src):
        q = dst / p.relative_to(src)
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)


# ---- membrane: native tool calls, with text fallbacks -------------------------------------------------
DSML_INVOKE = re.compile(r'invoke name="([^"]+)"[^>]*>(.*?)(?:</[^>]*invoke>|$)', re.S)
DSML_PARAM = re.compile(r'parameter name="([^"]+)"[^>]*>(.*?)</[^>]*parameter>', re.S)


def parse_text(text: str) -> dict | None:
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("do") in NAMES:
            return obj
    m = DSML_INVOKE.search(text)
    if m:
        args = {k: v for k, v in DSML_PARAM.findall(m.group(2))}
        name = m.group(1) if m.group(1) in NAMES else args.pop("do", None) or m.group(2).split("<", 1)[0].strip()
        primary = {"sh": "cmd", "remember": "text", "assay": "cmd", "try": "idea", "done": "result"}
        for k in [k for k in args if k in primary]:  # <parameter name="sh">ls</parameter>: tool as a key
            name, v = k, args.pop(k)
            if v.strip() and primary[k] not in args:
                args[primary[k]] = v
        if name not in NAMES:  # bare invoke "do": infer the tool from its arguments (text alone is ambiguous)
            name = {"cmd": "sh", "path": "write", "idea": "try", "result": "done"}.get(next(iter(args), ""), "")
            if name == "write" and "versions" in args:
                name = "variants"
        if name in NAMES:
            if isinstance(args.get("versions"), str):
                try:
                    args["versions"] = json.loads(args["versions"])
                except json.JSONDecodeError:
                    pass
            return {"do": name, **args}
    return None


TEXT_MODE = os.environ.get("CELL_TEXT_MODE") == "1" or (MODEL or "").startswith("openai:gpt-6")


async def _think(prompt: str, sid: str) -> tuple[dict | None, str, str]:
    tools, system = TOOLS, SYSTEM
    if TEXT_MODE:  # route rejects function tools (gpt-6 on chat/completions): JSON actions in text
        tools = []
        system = SYSTEM + "\n\nTools are not wired natively. Reply with ONE JSON object only: {\"do\": TOOL, ...args}. Tools:\n" + \
            "\n".join(f"- {t.name}: {t.description} args={json.dumps(t.parameters.get('properties', {}))}" for t in TOOLS)
    msgs = [Message.system(system), Message.user(prompt)]
    text, act, route = [], None, ""
    async for ev in router().stream(ROLE, msgs, tools, session_id=sid):
        if ev.kind == "text":
            text.append(ev.text)
        elif ev.kind == "tool_call" and ev.tool_call and act is None:
            act = {"do": ev.tool_call.name, **(ev.tool_call.arguments or {})}
        elif ev.kind == "error":
            raise RuntimeError(f"model error {ev.status}: {(ev.error or '')[:160]}")
        elif ev.kind == "done":
            route = ev.route
    raw = "".join(text)
    return act or parse_text(raw), raw, route


def think(prompt: str, sid: str) -> tuple[dict | None, str, str]:
    return asyncio.run_coroutine_threadsafe(_think(prompt, sid), R._BG["loop"]).result(240)


# ---- the bench: trusted measurement ---------------------------------------------------------------------
def measure(dirs: dict[str, Path], cmd: str, repeats: int = REPEATS) -> dict[str, list[float]]:
    """Serial, under a machine-wide lock, interleaved so drift hits every contender alike."""
    runs: dict[str, list[float]] = {k: [] for k in dirs}
    BENCH_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(BENCH_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for _ in range(repeats):
            for k, d in dirs.items():
                out, _ = sandboxed(d, cmd)
                nums = re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", out.split("\n", 1)[-1])
                runs[k].append(float(nums[-1]) if out.startswith("exit 0") and nums else 0.0)
    return runs


def spread(v: list[float]) -> float:
    m = statistics.median(v)
    return (max(v) - min(v)) / m if m > 0 else float("inf")


def beats(chal: list[float], inc: list[float], noise: float) -> tuple[bool, float]:
    """A real win: the challenger's median clears the incumbent's by the larger of 3% and the measured
    noise, and its worst run is no worse than the incumbent's median."""
    mc, mi = statistics.median(chal), statistics.median(inc)
    gain = (mc - mi) / mi if mi > 0 else 0.0
    return gain > max(MIN_MARGIN, noise) and min(chal) >= mi, gain


def assay(cell: Path, cmd: str) -> str:
    runs = measure({"self": cell}, cmd)["self"]
    med, sp = statistics.median(runs), spread(runs)
    if med <= 0:
        return f"refused: assay scored {runs} on your current body. It must print a number > 0 when correct."
    if sp > MAX_NOISE:
        return (f"refused: assay too noisy, runs {[round(r, 4) for r in runs]} spread {sp:.0%}. "
                "Use a heavier workload or repeat inside the command and print the best or median.")
    (cell / "ASSAY.json").write_text(json.dumps({"cmd": cmd, "baseline": med, "noise": sp}))
    log(cell, event="assay", cmd=cmd, runs=runs)
    return f"assay accepted: baseline median {med:.6g}, noise {sp:.1%}. Wins must beat it by > {max(MIN_MARGIN, sp):.1%}."


def get_assay(cell: Path) -> dict | None:
    return json.loads((cell / "ASSAY.json").read_text()) if (cell / "ASSAY.json").exists() else None


def adopt(cell: Path, src: Path, gain: float, what: str) -> None:
    copy_body(src, cell)
    a = get_assay(cell)
    bump(colony(cell) / ".improvements")
    log(cell, event="improve", gain=round(gain, 4), what=what[:200])
    library_add(cell, f"WIN +{gain:.0%}: {what} (assay: {a['cmd'][:120] if a else '?'})")


def variants(cell: Path, act: dict) -> str:
    a = get_assay(cell)
    if not a:
        return "refused: register an assay first"
    p = inside(cell, str(act.get("path", "")))
    vs = [v for v in act.get("versions") or [] if isinstance(v, str)][:MAX_VARIANTS]
    if not p or len(vs) < 1:
        return "refused: need a path inside your body and 1 to 6 versions"
    rel = p.relative_to(cell.resolve())
    work = Path(tempfile.mkdtemp(dir=colony_root(cell) / ".tmp", prefix="v-"))
    dirs = {"inc": cell}
    for i, v in enumerate(vs):
        d = work / f"v{i}"
        copy_body(cell, d)
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(v)
        dirs[f"v{i}"] = d
    runs = measure(dirs, a["cmd"], repeats=3)
    meds = {k: statistics.median(r) for k, r in runs.items()}
    best = max((k for k in meds if k != "inc"), key=meds.get)
    ok, gain = beats(runs[best], runs["inc"], a["noise"])
    why = str(act.get("why", ""))[:160]
    log(cell, event="variants", path=str(rel), medians=meds, best=best, adopted=ok, gain=round(gain, 4))
    for i, v in enumerate(vs):
        archive(cell, kind="variant", path=str(rel), code=v, score=meds.get(f"v{i}"),
                incumbent=meds.get("inc"), adopted=bool(ok and best == f"v{i}"), why=why)
    if ok:
        adopt(cell, dirs[best], gain, f"{rel} variant ({why})")
    else:
        library_add(cell, f"no gain: {len(vs)} variants of {rel} ({why}); best {gain:+.0%}")
    shutil.rmtree(work, ignore_errors=True)
    shown = ", ".join(f"{k}={v:.4g}" for k, v in meds.items())
    return f"medians {shown}. {'ADOPTED ' + best + f' (+{gain:.0%})' if ok else 'kept incumbent'}."


def autopsy(daughter: Path, idea: str, gain: float) -> str:
    g = (daughter / "genome.md").read_text()[:1200] if (daughter / "genome.md").exists() else ""
    tail = (daughter / "log.jsonl").read_text().splitlines()[-5:] if (daughter / "log.jsonl").exists() else []
    try:
        bump(colony_root(daughter) / ".calls")
        return aux_sync(router(), f"A branch tried: {idea}\nResult vs incumbent: {gain:+.0%}.\nIts memory:\n{g}\n"
                        "Its last steps:\n" + "\n".join(t[:250] for t in tail) +
                        "\n\nOne line: the most useful fact this branch learned, for anyone working on similar code.",
                        role=ROLE, timeout=120, session_id="cell-autopsy")[:300].strip()
    except Exception as e:
        return f"(autopsy failed: {type(e).__name__})"


def try_idea(cell: Path, act: dict, steps: int) -> str:
    a = get_assay(cell)
    if not a:
        return "refused: register an assay first"
    if depth(cell) >= MAX_DEPTH:
        return "refused: daughters cannot spawn daughters; use variants"
    idea, expect = str(act.get("idea", ""))[:600], str(act.get("expect", ""))[:120]
    d = cell / "daughter"
    shutil.rmtree(d, ignore_errors=True)
    copy_body(cell, d)
    shutil.copy2(cell / "ASSAY.json", d / "ASSAY.json")
    (d / "NEED").write_text((cell / "NEED").read_text() + f"\n\nYOUR IDEA TO TEST: {idea}\nThe current body is the "
                            f"incumbent. You win only if the assay improves: {a['cmd']}")
    t0 = time.time()
    run(d, steps)
    runs = measure({"inc": cell, "d": d}, a["cmd"])
    ok, gain = beats(runs["d"], runs["inc"], a["noise"])
    if ok:
        adopt(cell, d, gain, f"try: {idea[:160]}")
        lesson = ""
    else:
        lesson = autopsy(d, idea, gain)
        library_add(cell, f"LOSS {gain:+.0%} (expected {expect or '?'}): {idea[:140]}. Lesson: {lesson}")
    n = len(list((cell / ".lineage").glob("*"))) + 1 if (cell / ".lineage").exists() else 1
    shutil.copytree(d, cell / ".lineage" / f"{n}-{'won' if ok else 'lost'}", dirs_exist_ok=True)
    shutil.rmtree(d, ignore_errors=True)
    log(cell, event="try", idea=idea[:200], expect=expect, runs=runs, won=ok, gain=round(gain, 4),
        grow_secs=round(time.time() - t0, 1), lesson=lesson)
    return f"daughter {'WON' if ok else 'lost'}: {gain:+.0%} vs incumbent (you expected {expect or '?'}). {lesson}"


def depth(cell: Path) -> int:
    d, c = 0, cell
    while (c.parent / "NEED").exists():
        d, c = d + 1, c.parent
    return d


def step_prompt(cell: Path, history: list[tuple[str, str]], left: int) -> str:
    g = (cell / "genome.md").read_text() if (cell / "genome.md").exists() else "(empty)"
    h = "\n\n".join(f"ACTION {a}\nRESULT {r}" for a, r in history[-6:]) or "(none yet)"
    lib = colony(cell) / "LIBRARY.md"
    lib_t = lib.read_text()[-2500:] if lib.exists() else "(empty)"
    a = get_assay(cell)
    return (f"NEED:\n{(cell / 'NEED').read_text()}\n\nLIBRARY (colony results and lessons, newest last):\n{lib_t}"
            f"\n\nGENOME (your memory):\n{g}\n\nBODY:\n{show_body(cell)}" +
            f"\n\nASSAY: {json.dumps(a) if a else 'none registered'}\n\nRECENT:\n{h}\n\nSteps left: {left}. "
            + nudge(a, left))


def nudge(a: dict | None, left: int) -> str:
    """g3: cells registered their assay at step 4-14 of 16, so half never searched. Push it early."""
    if left <= 2:
        return "FINISH NOW: call done with your evidence."
    if not a and left <= 12:
        return ("REGISTER AN ASSAY NOW: once something works, call assay so the bench can measure it. "
                "Without one you cannot search variants.")
    if a and left >= 4:
        return "You have an assay: prefer variants (several ideas, one call) over hand-tuning with sh."
    return "Call one tool."


def show_body(cell: Path, budget: int = 6000) -> str:
    """File contents are in the prompt, so the cell never spends a step reading what it just wrote."""
    out = []
    for p in body_files(cell)[:40]:
        rel = p.relative_to(cell)
        try:
            t = p.read_text()
        except (UnicodeDecodeError, OSError):
            t = None
        if t is not None and p.stat().st_size <= 4000 and len(t) <= budget:
            out.append(f"--- {rel}\n{t}")
            budget -= len(t)
        else:
            out.append(f"--- {rel} ({p.stat().st_size} bytes, not shown)")
    return "\n".join(out) or "(empty)"


def run(cell: Path, steps: int) -> str | None:
    history: list[tuple[str, str]] = []
    fails = 0
    waits = 0
    for i in range(steps):
        if bump(colony_root(cell) / ".calls") > MAX_CALLS:
            log(cell, event="starved")
            return None
        try:
            act, raw, route = think(step_prompt(cell, history, steps - i), "cell-" + cell.name)
            if act is None:
                log(cell, step=i, bad_reply=raw[:200], bad_len=len(raw), route=route)
                raise ValueError("no tool call in reply; call exactly one tool")
        except Exception as e:
            msg = str(e)
            m = re.search(r"reopens in (\d+)s", msg)
            if ("429" in msg or isinstance(e, TimeoutError)) and waits < 6:
                waits += 1
                wait = min(int(m.group(1)) + 2 if m else 20, 120)
                log(cell, step=i, backoff=wait, why=msg[:120] or type(e).__name__)
                time.sleep(wait)
                continue
            fails += 1
            history.append(("(invalid)", f"{type(e).__name__}: {str(e)[:200]}"))
            log(cell, step=i, error=f"{type(e).__name__}: {str(e)[:200]}")
            if fails >= 3:
                log(cell, event="apoptosis")
                return None
            continue
        fails = 0
        do = act.get("do")
        if do == "sh":
            res = sandboxed(cell, str(act.get("cmd", "")))[0]
        elif do == "write":
            p = inside(cell, str(act.get("path", "")))
            if p:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(str(act.get("text", "")))
                archive(cell, kind="write", step=i, path=str(p.relative_to(cell.resolve())), code=str(act.get("text", "")))
            res = f"wrote {p.relative_to(cell.resolve())}" if p else "refused: path outside body"
        elif do == "remember":
            (cell / "genome.md").write_text(str(act.get("text", ""))[:GENOME_CAP])
            res = "genome updated"
        elif do == "assay":
            res = assay(cell, str(act.get("cmd", "")))
        elif do == "variants":
            res = variants(cell, act)
        elif do == "try":
            res = try_idea(cell, act, max(4, (steps - i) // 2))
        elif do == "done":
            (cell / "RESULT").write_text(str(act.get("result", "")))
            log(cell, step=i, act={"do": "done"}, route=route)
            if depth(cell) == 0:
                a = get_assay(cell)
                library_add(cell, f"DONE{' (assay baseline ' + format(a['baseline'], '.4g') + ')' if a else ''}: "
                            f"{str(act.get('result', ''))[:300]}")
            return str(act.get("result", ""))
        else:
            res = f"unknown tool {do!r}"
        short = json.dumps({k: (v if k not in ("text", "versions") else f"<{len(str(v))} chars>") for k, v in act.items()})[:300]
        history.append((short, res))
        log(cell, step=i, act=json.loads(short) if short.endswith("}") else {"do": do}, res=res[:500], route=route)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seed"])
    ap.add_argument("dir")
    ap.add_argument("need")
    ap.add_argument("--steps", type=int, default=16)
    a = ap.parse_args()
    cell = Path(a.dir).expanduser().resolve()
    cell.mkdir(parents=True, exist_ok=True)
    (cell / "NEED").write_text(a.need)
    aux_sync(router(), "ok", role="aux", timeout=60, session_id="cell-warm")  # start the shared loop once
    t = time.time()
    res = run(cell, a.steps)
    calls = (cell / ".calls").read_text()
    print(json.dumps({"result": res, "calls": int(calls), "secs": round(time.time() - t, 1)}, indent=1))
    return 0 if res else 1


if __name__ == "__main__":
    raise SystemExit(main())
