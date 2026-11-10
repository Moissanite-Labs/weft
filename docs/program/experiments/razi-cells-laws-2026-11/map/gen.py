# Builds MAP.html: the open directions of the razi-cells research, as a two-sided mind map. Data only, no claims beyond IDEAS.md / TESTS.md.
import html, json
S = {"now": ("#ff7a1a", "in build now"), "ready": ("#3ddc84", "ready to run, tooling exists"),
     "build": ("#4aa8ff", "needs new tooling first"), "parked": ("#8a8f98", "tested or paused, set aside"),
     "far": ("#b66dff", "out of reach today")}
# (label, status, pick, detail)
T = [
 ("LAWS OF THE CELL", "What a cell feels: energy, price, need", "Known: cells stop at the first passing answer, always pick the cheapest model, never divide (0 of 12+). Colony shape is not the lever (SP2).", [
  ("Need sensor (SP3)", "now", 1, "One inward number: my body's score against the best my lineage ever recorded. Patch written tonight, not yet run. Tests K20: cells stop without knowing what is possible."),
  ("Escalation after a failed try", "ready", 1, "A failed round on one model does not count as 'no headroom' until one round on the next model up has also failed. Won in the toy network (GR4, lowest worst-case regret). Never tried in cells."),
  ("Exchange rate: thought price vs win reward", "ready", 1, "A mid step costs 50 to 100, a +10% win pays 38, so cheap and early is rational (K18). Move the rate and see if reach moves. Possibly the real lever."),
  ("Rest is not free (upkeep)", "ready", 0, "I2a. A resting body keeps paying a small living cost. Today rest is free and safe, which may cost reach (K16)."),
  ("Red Queen kit", "ready", 0, "I2c. The kit gets harder as the colony's best rises, so a body that stands still loses ground."),
  ("Inheritance by fitness", "ready", 0, "I2b. Surplus energy flows in proportion to scored gain, not equally."),
  ("Reproduction as the only store", "ready", 0, "I2d. Energy above a level cannot be held, only spent on a daughter. Gives division a cause."),
  ("Daughters born different", "ready", 0, "K1/K3. A copy gives the gate nothing to judge (seen in networks and cells). Daughter starts with another model, effort, or slice of the need."),
  ("Machine load as price", "build", 0, "K4. Energy cost per step follows real CPU and memory load, so cells feel the machine through the law, not a prompt line. Your sensor-exposure idea."),
 ]),
 ("WHICH MIND", "Model families and mixtures", "Known: the effect of the variants tool flips with the model (F5). hy4 never attempted improvement. Only Sonnet/Haiku have run on the valid instrument.", [
  ("Same laws, second family", "ready", 1, "I2e. Run the energy laws on Mistral Large 4 and Argon. No finding counts until it holds on two families (flag rule)."),
  ("Mixed colony: strong builds, cheap runs", "ready", 0, "Strong model for tool-building steps, cheap for routine. Metric: tokens per improvement, against all-cheap and all-strong."),
  ("hy4 with the hold rule", "ready", 0, "F7. hy4 scored 0 because it never tried, not because it could not. Does a hold lift it?"),
  ("Ask vs rule, same model", "ready", 0, "F3. A nudge did nothing (Argon), a refusal did a lot (Sonnet). Never compared on one model and one kit set."),
  ("Model fingerprints in vector space", "ready", 0, "E5. Do different models' code variants occupy separate regions? Does a mixed colony cover more area?"),
  ("Argon reruns on the Gemini key", "build", 0, "Cells are not yet wired to the Gemini route. Small wiring job, then the held Argon runs."),
 ]),
 ("WHAT IS INHERITED", "Memory, reflexes, lessons from losers", "Known: one error type recurred 15 times in the same cell. The prose library is read but changes little. Losers' code is archived and unused.", [
  ("Dormant reflexes", "ready", 1, "T-J2, your discussion 105 idea. A cell that recovers from an error leaves a trigger and response. Costs nothing until the trigger recurs. Colony inherits it."),
  ("Nearest lessons only", "ready", 0, "E4. Give each cell the top few library entries closest to its current code, not the whole file. None / all / top-k."),
  ("Losers passed on as vectors", "build", 0, "H2b. The direction from losers to winners steers the next attempt (F1 steering, F2 toward/away test)."),
  ("Tool commons", "build", 0, "R5/A1. Cells publish tools to a shared shelf. Watch which spread (cultural evolution)."),
  ("Seeded library", "ready", 0, "Start a colony with the library of an earlier one. Is progress sequential across colonies or reset each time?"),
  ("Structured genomes", "build", 0, "Corpus idea (s-expression genomes): memory as structure the harness can cut and recombine, not prose."),
 ]),
 ("BEYOND TEXT", "Fitness and signals that are not words", "Known: a text-parsed score was once fooled by a warning line (179.0). Bend interaction counts are exactly repeatable on a pinned runtime.", [
  ("Deterministic fitness (Bend/HVM)", "ready", 1, "G1/H2a. Score by interaction count, not wall time. Removes noise gate, repeats and bench lock. First question: can models write valid Bend at all?"),
  ("An evaluator as the need", "build", 0, "G3. The task is a lambda-calculus evaluator, which could later run the next generation. Gains could compound."),
  ("Lean arm vs Bend arm", "build", 0, "G5. Same task, same kit, one colony writing Lean, one Bend."),
  ("Predict before benching", "ready", 0, "E3. Nearest-neighbour guess of a variant's score from past variants. Skips likely losers, cuts the serial bench."),
  ("How wide should a split be", "ready", 0, "E1/E2. Distance between daughters against gain. A novelty floor so every A/B is a real experiment."),
  ("One basin or many", "ready", 0, "E6. Across colonies, do winners for a need collapse to one point or several?"),
 ]),
 ("PROOF", "Selection as mathematics", "Known: Lean 4 and Bend are installed. Nothing proven yet. Lean cannot verify Bend code in our stack, only Lean code or a log.", [
  ("Needs that are theorems", "ready", 1, "R2. Fitness is 'the proof compiles'. No timing noise, no fake wins. First need: the Weft gate invariant (Paper 1, Prop 3)."),
  ("Selection rule as a theorem", "build", 0, "R3/F3. State the keep rule in Lean, prove fitness never falls across generations, generate the check from it."),
  ("Proof-carrying wins", "build", 0, "R1. A win is kept only with a certificate: differential test first, Lean equivalence proof later."),
  ("Anchor to generation zero", "ready", 0, "W2. Every winner must still match the first body's outputs. Measures silent drift (Weft's compounding-bound point)."),
  ("Hash-chained lineage", "ready", 0, "W3. Each cell's history as a replayable committed record, like Weft Paper 2."),
 ]),
 ("GROWING A MODEL", "The same laws one layer down", "Known (toy networks): blind division plus a gate plus gradients sizes a network to its need. A fixed gate cannot tell satisfied from stuck. Tinker works end to end (5 of 5).", [
  ("Adapter genome on Inkling 2 Small", "ready", 1, "T-J3. Cell experience becomes training data for a small adapter. Fork, train two ways, gate keeps the better. Key works, pilot not designed."),
  ("Sensor proposes, escalation confirms", "ready", 0, "GR5. The combined gate law on the toy network. Only if the cell pilots need it."),
  ("When need is far out of reach", "ready", 0, "K9. On the hardest toy task no gate wins and ungated growth does. Restraint costs most where need is highest. Open."),
  ("Weight genomes on local models", "build", 0, "H2c. Small local model, genome is a weight delta, a split branches the delta. Direct bridge to Weft Paper 1."),
  ("Do both layers obey the same laws", "build", 0, "H2d/J1. Compare acceptance rate, bold-win share and gate binding between weights and code on matched budgets. Your central hypothesis."),
  ("Model reshapes its own chip", "far", 0, "The FPGA-like layer from the Weft roadmap. No such hardware here."),
 ]),
 ("COLONY AS ORGANISM", "Structure, agency, scale", "Known: doubling cells halved wins per 100 calls. A stem that feeds parts costs 1.6x tokens and ends level. Width needs a problem that splits with cheap checks.", [
  ("A problem that truly splits", "build", 1, "J2/J7. Width only pays on needs with many unlike parts, each cheaply checkable. We have not yet built such a need. Without it 'swarm vs one agent' is untestable."),
  ("Cells that rewrite the mitosis", "build", 0, "A2/R4. A cell whose body is the runtime itself, scored by the wins of a small child colony. Bench and sandbox stay outside."),
  ("Adversary cells", "build", 0, "R6. One writes code, a sibling writes inputs that break it. The kit grows from the attacker's finds."),
  ("Swarm vs one strong agent", "build", 0, "T-J1 remainder. Colony against a single strong agent at equal tokens."),
  ("Micro-harness swarms, many data types", "build", 0, "J3. Modular harnesses spawning swarms across model families. Needs the splitting need first."),
  ("Stem cell feeding", "parked", 0, "SP1/SP2. Need-directed feeding emerged without a rule, but ended nowhere better at higher cost. Parked, code kept."),
  ("Mortal law (no rest)", "parked", 0, "mp3. More attempts, but half the energy went on idling at end of life. Biology keeps rest and adds a wake signal."),
 ]),
 ("INSTRUMENT", "Things that keep results honest", "Known: three instrument faults found and fixed so far (stderr score, cell-owned inputs, own-baseline gain).", [
  ("Kits with real headroom", "ready", 1, "compress has no headroom and fibmod carries most effects. Results lean on 4 uneven tasks. More kits, each with a known ceiling."),
  ("Benchmark carryover", "ready", 0, "G6. Does one cell's bench leave the machine hot for the next? Unchecked."),
  ("Do cells drift their own test", "ready", 0, "F1. Count post-assay benchmark edits per model on the old cell-owned protocol. A finding about agents, not just a bug."),
  ("E07 record corrections", "parked", 0, "Weft PR 101. Paused at your word. Numbers already recomputed."),
 ]),
]
ROW, FS = 27, 13
left, right = T[4:], T[:4]
def side_h(bs): return sum(len(b[3]) for b in bs) * ROW + (len(bs) - 1) * 34
H = max(side_h(left), side_h(right)) + 150
W = 1640; cx, cy = W / 2, H / 2 + 20
out, det = [], []
def esc(s): return html.escape(s, quote=True)
def node(i, x, y, w, h, fill, stroke, txt, cls, anchor="middle", tx=None, sub=None):
    tx = x + w / 2 if tx is None else tx
    cut = 9
    pts = f"{x+cut},{y} {x+w},{y} {x+w},{y+h-cut} {x+w-cut},{y+h} {x},{y+h} {x},{y+cut}"
    s = f'<g class="n {cls}" data-i="{i}"><polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    s += f'<text x="{tx}" y="{y+h/2+(-3 if sub else 4.5)}" text-anchor="{anchor}" class="{cls}t">{esc(txt)}</text>'
    if sub:
        s += f'<text x="{tx}" y="{y+h/2+13}" text-anchor="{anchor}" class="subt">{esc(sub)}</text>'
    return s + "</g>"
def draw(bs, sgn):
    y = cy - side_h(bs) / 2
    for name, sub, known, leaves in bs:
        bh = len(leaves) * ROW
        by = y + bh / 2
        bw, bx = 236, cx + sgn * 150 - (236 if sgn < 0 else 0)
        det.append({"t": name, "s": sub, "d": known, "k": "branch"})
        bi = len(det) - 1
        x0, x1 = cx + sgn * 96, bx + (bw if sgn < 0 else 0)
        out.append(f'<path d="M{x0},{cy} C{x0+sgn*40},{cy} {x1-sgn*40},{by} {x1},{by}" class="lk b"/>')
        ex = bx + (0 if sgn < 0 else bw)
        for j, (lab, st, pick, d) in enumerate(leaves):
            ly = y + j * ROW + ROW / 2
            lx = ex + sgn * 46
            col = S[st][0]
            det.append({"t": lab, "s": S[st][1] + (" · my pick" if pick else ""), "d": d, "k": st})
            li = len(det) - 1
            out.append(f'<path d="M{ex},{by} C{ex+sgn*26},{by} {lx-sgn*26},{ly} {lx},{ly}" class="lk" stroke="{col}"/>')
            star = "★ " if pick else ""
            a = "start" if sgn > 0 else "end"
            tx = lx + sgn * 16
            out.append(f'<g class="n leaf" data-i="{li}"><rect x="{lx-5 if sgn>0 else lx-5}" y="{ly-5}" width="10" height="10" fill="{col}" transform="rotate(45 {lx} {ly})"/>'
                       f'<rect x="{tx-4 if sgn>0 else tx-330}" y="{ly-ROW/2+1}" width="334" height="{ROW-2}" fill="transparent"/>'
                       f'<text x="{tx}" y="{ly+4.5}" text-anchor="{a}" class="leaft{" pick" if pick else ""}">{esc(star+lab)}</text></g>')
        out.append(node(bi, bx, by - 23, bw, 46, "#14181f", "#e8eaed", name, "br", sub=sub))
        y += bh + 34
draw(right, 1); draw(left, -1)
det.append({"t": "RAZI CELLS", "s": "open directions, 2026-11-10", "k": "branch",
            "d": "Core question: which laws, felt from inside by each cell, make a colony improve, divide and show restraint on its own. Click any node. Stars are my picks for where the next real finding is most likely."})
out.append(node(len(det) - 1, cx - 96, cy - 34, 192, 68, "#ff7a1a", "#ff7a1a", "RAZI CELLS", "ct", sub="what is left to explore"))
leg = "".join(f'<span class="lg"><i style="background:{c}"></i>{esc(t)}</span>' for c, t in S.values()) + '<span class="lg">★ my pick</span>'
page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>razi cells: open directions</title>
<style>
html,body{{margin:0;background:#0b0d11;color:#e8eaed;font:14px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif}}
header{{display:flex;justify-content:space-between;align-items:center;padding:14px 22px;border-bottom:1px solid #222834}}
h1{{font-size:15px;letter-spacing:.14em;margin:0;font-weight:700}}
.lg{{margin-left:18px;font-size:12px;color:#aab0bb;white-space:nowrap}} .lg i{{display:inline-block;width:9px;height:9px;transform:rotate(45deg);margin-right:8px}}
svg{{display:block;width:100%;height:auto}}
.lk{{fill:none;stroke-width:1.2;opacity:.55}} .lk.b{{stroke:#e8eaed;stroke-width:1.6;opacity:.8}}
.brt{{fill:#fff;font-size:13px;font-weight:700;letter-spacing:.08em}} .subt{{fill:#9aa1ad;font-size:10.5px}}
.ctt{{fill:#0b0d11;font-size:16px;font-weight:800;letter-spacing:.12em}} .ct .subt{{fill:#3a1c05}}
.leaft{{fill:#cfd3da;font-size:{FS}px}} .leaft.pick{{fill:#fff;font-weight:650}}
.n{{cursor:pointer}} .n:hover text{{fill:#ff7a1a}} .n.on text{{fill:#ff7a1a}}
#d{{position:sticky;bottom:0;background:#11141a;border-top:2px solid #ff7a1a;padding:14px 22px;min-height:64px}}
#d b{{font-size:15px;letter-spacing:.04em}} #d em{{font-style:normal;color:#9aa1ad;margin-left:12px;font-size:12px}} #d p{{margin:6px 0 0;max-width:1100px;color:#d6dae1}}
</style>
<header><h1>RAZI CELLS · OPEN DIRECTIONS</h1><div>{leg}</div></header>
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(out)}</svg>
<div id="d"></div>
<script>
const D={json.dumps(det)};const d=document.getElementById("d");
function show(i,el){{const x=D[i];d.replaceChildren();const b=document.createElement("b");b.textContent=x.t;const e=document.createElement("em");e.textContent=x.s;const p=document.createElement("p");p.textContent=x.d;d.append(b,e,p);
document.querySelectorAll(".n.on").forEach(n=>n.classList.remove("on"));if(el)el.classList.add("on");}}
document.querySelectorAll(".n").forEach(n=>{{n.addEventListener("click",()=>show(+n.dataset.i,n));n.addEventListener("mouseenter",()=>show(+n.dataset.i,n));}});
show(D.length-1,null);
</script></html>'''
open("MAP.html", "w").write(page)
n = sum(len(b[3]) for b in T)
print("branches", len(T), "leaves", n, "picks", sum(l[2] for b in T for l in b[3]), "bytes", len(page), "H", H)
print({k: sum(1 for b in T for l in b[3] if l[1] == k) for k in S})
import re; print("dashes", len(re.findall("[\u2013\u2014]", page)))
