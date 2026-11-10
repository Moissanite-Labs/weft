"""tk_smoke.py: can we do the five primitives an adapter-genome pilot needs? create, train step, eval, save, fork.
Tiny on purpose (a few thousand tokens). Key is read in memory by tinker_key and never printed."""
import os, re, sys, time, json
sys.path.insert(0, os.path.expanduser("~/Work/razi-tools"))
import tinker_key
os.environ["TINKER_API_KEY"] = tinker_key.get()
import warnings; warnings.simplefilter("ignore")
import tinker
from tinker import types

MODEL = sys.argv[1] if len(sys.argv) > 1 else "thinkingmachines/Inkling-2-Small"
def safe(s): return re.sub(r"tml-[A-Za-z0-9_\-\.]+", "tml-[REDACTED]", str(s))[:500]
T0 = time.time()
def lap(msg): print(f"[{time.time()-T0:6.1f}s] {msg}", flush=True)

try:
    sc = tinker.ServiceClient()
    tc = sc.create_lora_training_client(base_model=MODEL, rank=8, seed=0)
    lap(f"training client ok: {MODEL} rank 8")
    if MODEL.startswith("thinkingmachines/"):
        # Thinking Machines models have no HF tokenizer; the renderer package carries it.
        from tml_renderers import renderers
        rk = renderers.Inkling2().tokenizer
        rk = rk() if callable(rk) else rk
        enc = lambda s, special=False: list(rk.encode_ordinary(s))
    else:
        hk = tc.get_tokenizer()
        enc = lambda s, special=False: hk.encode(s, add_special_tokens=special)
    lap("tokenizer ok")

    def datum(p, c):
        pt = enc(p, True); ct = enc(c)
        t = pt + ct; w = [0] * len(pt) + [1] * len(ct)
        return types.Datum(model_input=types.ModelInput.from_ints(tokens=t[:-1]),
                           loss_fn_inputs=dict(weights=w[1:], target_tokens=t[1:]))
    # a made-up rule the base model cannot know: word -> word reversed then doubled last letter
    words = ["lamp", "river", "stone", "cloud", "table", "green", "mouse", "paper"]
    rule = lambda w: w[::-1] + w[0]
    train = [datum(f"zorb({w}) =", " " + rule(w)) for w in words[:6]]
    held = [datum(f"zorb({w}) =", " " + rule(w)) for w in words[6:]]
    ntok = sum(d.model_input.length for d in train)
    lap(f"data ok: {len(train)} train datums, {ntok} tokens per pass")

    def loss(out, data):
        import numpy as np
        lp = np.concatenate([o["logprobs"].tolist() for o in out.loss_fn_outputs])
        w = np.concatenate([d.loss_fn_inputs["weights"].tolist() for d in data])
        return float(-(lp * w).sum() / w.sum())
    e0 = loss(tc.forward(held, "cross_entropy").result(), held); lap(f"held-out loss before: {e0:.4f}")
    for i in range(4):
        fb = tc.forward_backward(train, "cross_entropy"); op = tc.optim_step(types.AdamParams(learning_rate=1e-3))
        l = loss(fb.result(), train); op.result(); lap(f"step {i} train loss {l:.4f}")
    e1 = loss(tc.forward(held, "cross_entropy").result(), held); lap(f"held-out loss after 4 steps: {e1:.4f}")
    st = tc.save_state(name="smoke-parent", ttl_seconds=3600).result(); lap(f"save_state ok: path type {type(st.path).__name__}, scheme {str(st.path).split(':')[0]}")
    kids = [sc.create_training_client_from_state(st.path) for _ in range(2)]
    ek = [loss(k.forward(held, "cross_entropy").result(), held) for k in kids]
    lap(f"fork ok: two daughters from one state, held-out loss {ek[0]:.4f} / {ek[1]:.4f} (parent {e1:.4f})")
    fb = kids[0].forward_backward(train, "cross_entropy"); kids[0].optim_step(types.AdamParams(learning_rate=1e-3)).result(); fb.result()
    ea = loss(kids[0].forward(held, "cross_entropy").result(), held); eb = loss(kids[1].forward(held, "cross_entropy").result(), held)
    lap(f"daughters diverge: trained {ea:.4f}, untouched {eb:.4f}")
    print(json.dumps({"model": MODEL, "ok": True, "tokens_per_pass": ntok, "wall_s": round(time.time() - T0, 1)}))
except Exception as e:
    lap(f"ERR {type(e).__name__}: {safe(e)}")
