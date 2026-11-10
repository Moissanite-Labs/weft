"""tj3.py: adapter genome pilot (T-J3). Written 2026-11-10 before any T-J3 training result exists.
Genome = a LoRA adapter on one base model. Experience = cell shell commands and what the sandbox did (tj3_data.py).
Arms, all from one shared start state, all with the same number of optimizer steps (GENS * K):
  gc  one lineage, natural batches, never reloaded (what anyone would do)
  gn  one lineage, natural batches, saved and reloaded every K steps (control for the cost of a fork)
  gb  one lineage, balanced batches (half ok, half fail), saved and reloaded every K steps
  s   division with a gate: each generation two daughters fork from the parent, one trains natural, one balanced,
      K steps each; the better daughter on the gate split replaces the parent only if it beats the parent by MARGIN.
      Same total optimizer steps, so half as many generations.
Usage: python tj3.py DATA.json OUT.json [--arms gc,gn,gb,s] [--gens 12] [--k 2] [--seed 0] [--batch 32]
Key is read in memory by tinker_key and never printed."""
import os, re, sys, time, json, math, random, argparse, collections
sys.path.insert(0, os.path.expanduser("~/Work/razi-tools"))
import tinker_key
os.environ["TINKER_API_KEY"] = tinker_key.get()
import warnings; warnings.simplefilter("ignore")
import tinker
from tinker import types

ap = argparse.ArgumentParser()
ap.add_argument("data"); ap.add_argument("out")
ap.add_argument("--arms", default="gc,gn,gb,s"); ap.add_argument("--gens", type=int, default=12)
ap.add_argument("--k", type=int, default=2); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--batch", type=int, default=32); ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--rank", type=int, default=8); ap.add_argument("--margin", type=float, default=0.02)
ap.add_argument("--model", default="thinkingmachines/Inkling-2-Small"); ap.add_argument("--tag", default="tj3")
A = ap.parse_args()
assert A.gens % 2 == 0, "gens must be even so arm s gets exactly half"
def safe(s): return re.sub(r"tml-[A-Za-z0-9_\-\.]+", "tml-[REDACTED]", str(s))[:400]
T0 = time.time()
def lap(msg): print(f"[{time.time()-T0:7.1f}s] {msg}", flush=True)

D = json.load(open(A.data))
from tml_renderers import renderers
rk = renderers.Inkling2().tokenizer
rk = rk() if callable(rk) else rk
enc = lambda s: list(rk.encode_ordinary(s))
def datum(r):
    pt = enc("cmd: " + r["cmd"] + "\nresult:"); ct = enc(" " + r["label"])
    t = pt + ct; w = [0] * len(pt) + [1] * len(ct)
    return types.Datum(model_input=types.ModelInput.from_ints(tokens=t[:-1]),
                       loss_fn_inputs=dict(weights=w[1:], target_tokens=t[1:]))
SETS = {s: [datum(r) for r in D[s]] for s in ("train", "gate", "test")}
OKI = [i for i, r in enumerate(D["train"]) if r["label"] == "ok"]
BADI = [i for i, r in enumerate(D["train"]) if r["label"] != "ok"]
TOK = collections.Counter()

def batch(way, depth):
    """Fixed by seed, way and position. Single lineages pass their depth. Arm s passes generation * K, so a
    refused generation is followed by fresh batches and not by a repeat of the same draw."""
    rng = random.Random(f"{A.seed}|{way}|{depth}")
    if way == "nat": idx = rng.sample(range(len(D["train"])), A.batch)
    else: idx = rng.sample(OKI, A.batch // 2) + rng.sample(BADI, A.batch - A.batch // 2)
    return [SETS["train"][i] for i in idx]
def rowloss(out, data):
    """Mean over rows of minus the log probability of the whole label (nats per row)."""
    tot = 0.0
    for o, d in zip(out.loss_fn_outputs, data):
        lp = o["logprobs"].tolist(); w = d.loss_fn_inputs["weights"].tolist()
        tot += -sum(a * b for a, b in zip(lp, w))
    return tot / len(data)
def evalset(tc, name, arm):
    data = SETS[name]; tot = 0.0
    for i in range(0, len(data), 64):
        ch = data[i:i + 64]
        tot += rowloss(tc.forward(ch, "cross_entropy").result(), ch) * len(ch)
        TOK[arm + ":fwd"] += sum(d.model_input.length for d in ch)
    return round(tot / len(data), 5)
def train(tc, way, depth, arm):
    last = None
    for j in range(A.k):
        b = batch(way, depth + j)
        fb = tc.forward_backward(b, "cross_entropy"); op = tc.optim_step(types.AdamParams(learning_rate=A.lr))
        last = rowloss(fb.result(), b); op.result()
        TOK[arm + ":train"] += sum(d.model_input.length for d in b)
    return round(last, 5)
def save(tc, name): return tc.save_state(name=name, ttl_seconds=86400, overwrite=True).result().path

# label prior: the loss of a predictor that knows only how often each label occurs in train
pc = collections.Counter(r["label"] for r in D["train"]); n = sum(pc.values())
prior = {s: round(sum(-math.log(max(pc[r["label"]], 0.5) / n) for r in D[s]) / len(D[s]), 5) for s in ("gate", "test")}
R = {"args": vars(A), "prior": prior, "rows": {s: len(v) for s, v in D.items()}, "arms": {}, "ok": False}
def dump():
    R["tokens"] = dict(TOK); R["wall_s"] = round(time.time() - T0, 1)
    json.dump(R, open(A.out, "w"), indent=1)
try:
    sc = tinker.ServiceClient()
    base = sc.create_lora_training_client(base_model=A.model, rank=A.rank, seed=A.seed)
    P0 = save(base, f"{A.tag}-s{A.seed}-p0")
    R["start"] = {"gate": evalset(base, "gate", "start"), "test": evalset(base, "test", "start")}
    lap(f"start state saved. prior {prior} start {R['start']}"); dump()
    for arm in A.arms.split(","):
        log = []; t1 = time.time()
        if arm in ("gc", "gn", "gb"):
            way = "bal" if arm == "gb" else "nat"
            tc = sc.create_training_client_from_state(P0); depth = 0
            for g in range(A.gens):
                tl = train(tc, way, depth, arm); depth += A.k
                gl = evalset(tc, "gate", arm)
                log.append({"gen": g, "depth": depth, "way": way, "train": tl, "gate": gl})
                if arm != "gc" and g < A.gens - 1:
                    tc = sc.create_training_client_from_state(save(tc, f"{A.tag}-s{A.seed}-{arm}-g{g}"))
                lap(f"{arm} gen {g} depth {depth} train {tl} gate {gl}")
            final = tc
        elif arm == "s":
            P, pg, depth, final = P0, R["start"]["gate"], 0, None
            for g in range(A.gens // 2):
                kids = []
                for way in ("nat", "bal"):
                    tc = sc.create_training_client_from_state(P)
                    tl = train(tc, way, g * A.k, arm); gl = evalset(tc, "gate", arm)
                    kids.append({"way": way, "train": tl, "gate": gl, "tc": tc})
                best = min(kids, key=lambda k: k["gate"])
                took = best["gate"] < pg * (1 - A.margin)
                log.append({"gen": g, "depth": depth + (A.k if took else 0), "parent_gate": pg,
                            "kids": [{x: k[x] for x in ("way", "train", "gate")} for k in kids],
                            "took": best["way"] if took else None})
                lap(f"s gen {g} parent {pg} nat {kids[0]['gate']} bal {kids[1]['gate']} took {log[-1]['took']}")
                if took:
                    final, pg, depth = best["tc"], best["gate"], depth + A.k
                    if g < A.gens // 2 - 1: P = save(final, f"{A.tag}-s{A.seed}-s-g{g}")
            if final is None: final = sc.create_training_client_from_state(P)
        else: raise SystemExit("unknown arm " + arm)
        R["arms"][arm] = {"log": log, "gate": evalset(final, "gate", arm), "test": evalset(final, "test", arm),
                          "wall_s": round(time.time() - t1, 1)}
        lap(f"{arm} done gate {R['arms'][arm]['gate']} test {R['arms'][arm]['test']}"); dump()
    R["ok"] = True; dump()
    print(json.dumps({"ok": True, "prior": prior, "start": R["start"],
                      "final": {a: {"gate": v["gate"], "test": v["test"]} for a, v in R["arms"].items()},
                      "tokens": dict(TOK), "wall_s": R["wall_s"]}))
except Exception as e:
    R["error"] = f"{type(e).__name__}: {safe(e)}"; dump(); lap("ERR " + R["error"])
